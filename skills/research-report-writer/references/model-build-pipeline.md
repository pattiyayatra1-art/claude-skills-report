# Building the user's approved model layout (Word pipeline)

The user approved this pipeline as "ถูกต้อง 100%" on 2026-09-30 (digital-economics video
report). Use it for this user's Thai reports instead of the docx-js build in Step 6,
whenever Microsoft Word is installed (Windows). The layout itself is described in
`user-academic-writing-style.md`; this file is the *how*.

## What it produces

| Part | Result |
|---|---|
| Cover | RMUTP seal on top, รายงาน / รายวิชา / เรื่อง / จัดทำโดย / เสนอ, course-program-semester-university block at the bottom, no page number |
| Front matter | คำนำ (signed right), บทคัดย่อ + **คำสำคัญ:**, สารบัญ with "หน้า" column and dot leaders, สารบัญตาราง + สารบัญภาพ on one page, numbered ก ข ค top-right |
| Body | centred chapter title, bold black 1. / 1.1 headings, TH Sarabun New 16 pt, Thai distributed justify, numbered 1 2 3 top-right |
| Tables | bold caption above, full grid, navy header (#1F3864) white bold text, light-blue banded rows, "ที่มา:" below |
| Figures | centred picture, bold caption below, "ที่มา:" line |
| References | เอกสารอ้างอิง with **ภาษาไทย** then **ภาษาอังกฤษ**, hanging indent, no border box |
| TOC | Word fields updated twice before saving (no "Error! Bookmark not defined.") |

## Requirements

- Windows + Microsoft Word (COM). Check: `Get-ItemProperty 'Registry::HKEY_CLASSES_ROOT\Word.Application\CurVer'`
- Font TH Sarabun New installed
- Python + Pillow/matplotlib for figures and contact sheets; Poppler (`pdftoppm`) for page images
- If Word is missing, build the same layout with `node scripts/build_research_docx.js report.txt out.docx`
  (pure Node.js, same tagged file; see SKILL.md Step 6). Only if Node.js is missing too,
  fall back to the generic docx-js route and tell the user the layout will differ.

## Steps

1. **Seal**: use the logo file the user attached in SKILL.md Step 1a. If none was attached, download the official RMUTP seal next to the tagged file:
   ```powershell
   Invoke-WebRequest -Uri "https://www.rmutp.ac.th/web2561/wp-content/uploads/2018/07/PRANAKORN-color-transparency1.png" -OutFile rmutp_seal.png -UseBasicParsing
   ```
   Source page: https://www.rmutp.ac.th/สัญลักษณ์ (ตราประจำมหาวิทยาลัย).
   In a sandbox the download is often blocked (proxy 403). If it fails, ask the user to
   attach the seal **before** building. Never deliver a cover that is silently missing it.
2. **Tagged text** — copy `assets/template_model.txt`, fill every `{…}`. Tag reference:
   `word-tag-format.md`. One paragraph per line. A worked example is
   `examples/digital_economy_report_tagged.txt`.
   - Cover fields come from the SKILL.md Step 1a question round, never from guesses.
     The profile defaults (นายภัททิยะ ยาตรา, รหัสนักศึกษา 076750306033-1,
     สาขานวัตกรรมทางการเงินและการลงทุน, มหาวิทยาลัยเทคโนโลยีราชมงคลพระนคร) are offered for
     the user to confirm. Course, instructor, semester and year are asked every time.
   - Bullet-like items: `[LI]- **หัวข้อ:** คำอธิบาย` (bold lead-in).
3. **Figures** (optional) — box diagrams in the model's style: adapt
   `examples/fig_boxes_example.py` (TH Sarabun New, light-blue boxes, navy result box,
   220 dpi). Charts: follow the `dataviz` skill.
4. **Build**
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "<skill>\scripts\build_research_docx.ps1" -InputPath report.txt -OutputPath "<out>.docx"
   powershell -NoProfile -ExecutionPolicy Bypass -File "<skill>\scripts\modelfmt.ps1" -Docx "<out>.docx" -Pdf "<out>.pdf"
   ```
   `modelfmt.ps1` applies the navy table header + banding, bold captions, H3 flush left,
   black headings, merges สารบัญตาราง/สารบัญภาพ onto one page, refreshes TOC fields and
   exports the PDF with Word itself.
   - Run each script **only once per build**: rebuild from the tagged file rather than
     re-running `modelfmt.ps1` on its own output.
   - Windows PowerShell 5 reads BOM-less UTF-8 scripts as ANSI — keep Thai text out of
     `.ps1` files (match styles by ASCII names/outline levels instead).
5. **QA** — `pdftoppm -jpeg -r 60 <out>.pdf page`, view every page (contact sheet is
   fine), then zoom into tables and references. Check: cover fits one page, สารบัญ page
   numbers are real, no heading stranded at a page bottom, Thai bold/italic render, every
   in-text citation matches a reference entry (see `qa-checklist.md`).

## Fonts without Word (Linux sandbox) and the สารบัญ page numbers

`build_research_docx.js` leaves the contents lists without page numbers. To fill them
with numbers that match Word, render with the real TH Sarabun New:

```bash
# SIPA TH Sarabun New v1.35 (1000 upm). npm is reachable from the sandbox; GitHub/Google Fonts may not be
npm pack @apw-pdf/fonts && mkdir -p apw && tar xzf apw-pdf-fonts-*.tgz -C apw
mkdir -p ~/.fonts && cp apw/package/files/THSarabunNew-*.ttf ~/.fonts/ && fc-cache -f
fc-match "TH Sarabun New"          # must print THSarabunNew-Regular.ttf
python3 scripts/fill_toc_pages.py report.docx report_final.docx   # prints MISSING []
```

- Do **not** use the npm package `font-th-sarabun-new`. Its `*-webfont.ttf` files are
  rescaled (2048 upm, about 1.5× wider glyphs), so a 30-page report renders as 53 pages and
  every page number is wrong.
- For figures (matplotlib) the same TTFs work. If only Sarabun is needed, the
  `@fontsource/sarabun` npm package ships WOFF files: convert the `thai` and `latin`
  subsets to TTF with fontTools and merge them (`fontTools.merge.Merger`).
- On Windows with Word, `modelfmt.ps1` already refreshes the fields, so this step is
  not needed there.

## Known gotchas

- Table column widths (`build_research_docx.js`): a column whose longest cell is at most
  24 characters gets a fixed width of up to 4.5 cm. Longer columns share the rest of the
  width in proportion to their longest cell. A table with two long columns plus a medium
  third one squeezes that third column to about 2.5 cm, so Thai text breaks every few
  characters. Keep the first column short, keep cells balanced, or use 3 columns.

- `thai-academic-report-docx`'s `build_docx.ps1` sets only `Bold`/`Italic` (Latin), so
  Thai text does not turn bold — this pipeline uses `build_research_docx.ps1`, which sets
  `BoldBi`/`ItalicBi` too.
- The research script's Heading 3 is indented 0.5″; the model has it flush left
  (`modelfmt.ps1` fixes it).
- YouTube sources: pull Thai auto-captions with `yt-dlp --write-auto-subs --sub-langs th`
  and check every claim about the video against the transcript before citing it.
