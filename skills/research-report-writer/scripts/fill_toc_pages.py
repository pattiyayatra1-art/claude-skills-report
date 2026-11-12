"""Fill page numbers into the pre-built TOC / LOT / LOF entries of a docx made by
build_research_docx.js.  Page numbers are read from a PDF rendered by LibreOffice
with the real TH Sarabun New font, so they match Word's layout closely.

usage: python3 fill_toc_pages.py in.docx out.docx

Install the SIPA TH Sarabun New first (see references/model-build-pipeline.md,
"Fonts without Word"); with a substitute font the page numbers will not match Word.
"""
import re, subprocess, sys, zipfile, tempfile, os, shutil, html

if len(sys.argv) != 3:
    sys.exit(__doc__)
src, dst = sys.argv[1], sys.argv[2]
fm = subprocess.run(["fc-match", "TH Sarabun New"], capture_output=True, text=True).stdout
if "THSarabunNew-Regular" not in fm:
    print("WARNING: TH Sarabun New (SIPA) not installed; fc-match gives: " + fm.strip(), file=sys.stderr)
tmp = tempfile.mkdtemp()
shutil.copy(src, os.path.join(tmp, "in.docx"))
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp,
                os.path.join(tmp, "in.docx")], check=True, capture_output=True, timeout=300)
pdf = os.path.join(tmp, "in.pdf")
n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))

norm = lambda t: re.sub(r"\s+", "", t)
pages = []  # (label, [normalized lines])
for p in range(1, n + 1):
    txt = subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), pdf, "-"],
                         capture_output=True, text=True).stdout
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    label = lines[0] if lines and re.fullmatch(r"[0-9ก-ฮ]{1,3}", lines[0]) else ""
    pages.append((label, [norm(l) for l in lines]))

z = zipfile.ZipFile(src)
doc = z.read("word/document.xml").decode("utf-8")

def entry_text(par):
    return html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", par)))

# where the contents lists end: first body page (label "1")
first_body = next(i for i, (lab, _) in enumerate(pages) if lab == "1")

def find_page(text):
    key = norm(text)
    is_chapter = key.startswith("บทที่")
    is_front = key in ("คำนำ", "สารบัญ", "สารบัญตาราง", "สารบัญภาพ")
    rng = range(len(pages)) if is_front else range(first_body, len(pages))
    for i in rng:
        lines = pages[i][1]
        joined = "".join(lines[1:])
        if is_front or key == "บรรณานุกรม":
            if key in lines[1:]:
                return pages[i][0]
        elif is_chapter:
            m = re.match(r"(บทที่\d+)(.*)", key)
            if m and m.group(1) in lines[1:3] and joined.startswith(m.group(1) + m.group(2)[:8]):
                return pages[i][0]
        else:
            probe = key[:30]
            if probe in joined:
                return pages[i][0]
    return None

missing = []
def fill(m):
    par = m.group(0)
    if "<w:tab/>" not in par:
        return par
    text = entry_text(par)
    pg = find_page(text)
    if pg is None:
        missing.append(text)
        return par
    run = f'<w:r><w:t xml:space="preserve">{pg}</w:t></w:r>'
    i = par.rfind("<w:r><w:tab/></w:r>")
    return par[:i] + "<w:r><w:tab/></w:r>" + run + par[i + len("<w:r><w:tab/></w:r>"):]

doc = re.sub(r'<w:p><w:pPr><w:pStyle w:val="(?:TOC[12]|TableofFigures|TOCFigure|TOCTable)"/>.*?</w:p>',
             fill, doc, flags=re.S)
doc = doc.replace(' w:dirty="true"', "")  # numbers are filled; Word can still refresh on demand

out = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for item in z.infolist():
    data = doc.encode("utf-8") if item.filename == "word/document.xml" else z.read(item.filename)
    out.writestr(item, data)
out.close()
print("PAGES", n, "first_body_index", first_body)
print("MISSING", missing)
