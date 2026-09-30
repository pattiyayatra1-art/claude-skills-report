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
- If Word is missing, fall back to the docx-js route in SKILL.md Step 6 and tell the user the layout will differ.

## Steps

1. **Seal** — download the official RMUTP seal next to the tagged file (skip if the user gives another logo):
   ```powershell
   Invoke-WebRequest -Uri "https://www.rmutp.ac.th/web2561/wp-content/uploads/2018/07/PRANAKORN-color-transparency1.png" -OutFile rmutp_seal.png -UseBasicParsing
   ```
   Source page: https://www.rmutp.ac.th/สัญลักษณ์ (ตราประจำมหาวิทยาลัย).
2. **Tagged text** — copy `assets/template_model.txt`, fill every `{…}`. Tag reference:
   `word-tag-format.md`. One paragraph per line. A worked example is
   `examples/digital_economy_report_tagged.txt`.
   - Cover defaults for this user (verify against each assignment; see the memory/profile
     in the session if available): นายภัททิยะ ยาตรา, รหัสนักศึกษา 076750306033-1,
     สาขานวัตกรรมทางการเงินและการลงทุน, มหาวิทยาลัยเทคโนโลยีราชมงคลพระนคร.
     Course, instructor, semester change per assignment — ask if unknown.
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

## Known gotchas

- `thai-academic-report-docx`'s `build_docx.ps1` sets only `Bold`/`Italic` (Latin), so
  Thai text does not turn bold — this pipeline uses `build_research_docx.ps1`, which sets
  `BoldBi`/`ItalicBi` too.
- The research script's Heading 3 is indented 0.5″; the model has it flush left
  (`modelfmt.ps1` fixes it).
- YouTube sources: pull Thai auto-captions with `yt-dlp --write-auto-subs --sub-langs th`
  and check every claim about the video against the transcript before citing it.
