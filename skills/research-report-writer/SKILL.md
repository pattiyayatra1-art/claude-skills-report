---
name: "research-report-writer"
description: "Write full academic research reports in Thai (.docx) with verified real citations; for general academic reports (รายงานวิชาการ) use the separate non-research structure."
---

# Research Report Writer (v2.3)

Produces a full academic research report as a `.docx` file, in Thai, structured to the
convention Thai universities expect. It layers research content, method, and citation
rules on top of the base Word skill, and pulls in the related skills below when the
report needs them.

## Routing rule: รายงานวิชาการ ≠ รายงานวิจัย (check FIRST)

Decide the report type before anything else. Never mix the two structures.

| User says | Type | Structure |
|---|---|---|
| "รายงานวิชาการ", "รายงานเชิงวิชาการ", term paper, ภาคนิพนธ์ทั่วไป | **General academic report** | Use the structure below. Do NOT use Steps 4's research skeleton. |
| "งานวิจัย", "รายงานวิจัย", บทที่ 1-5, thesis chapter, has/needs data collection | **Research report** | Steps 1-7 as written |

If the request is ambiguous, ask one short question. If the user only says "รายงานเชิงวิชาการ", it is the general academic report.

**General academic report structure** (source: Siam University and Suan Sunandha guides; full notes in the project doc `claude/academic-report-guide.md` when the session is attached to the นักเขียนรายงาน project):

1. Front: ปกนอก, คำนำ, สารบัญ, สารบัญตาราง/ภาพ (if any). คำนำ = general lead-in to the topic and report, not บทนำ; no apologising or excuses.
2. บทที่ 1 บทนำ: ความเป็นมาและความสำคัญ (broad to specific) / วัตถุประสงค์ (start with "เพื่อ" + verb, declarative, numbered; count matches the knowledge chapters) / ขอบเขต / วิธีดำเนินการศึกษา (search, analyse, conclude; not a research methodology) / ประโยชน์ที่คาดว่าจะได้รับ / ข้อตกลงเบื้องต้น (terms).
3. Middle chapters split by topic, one per objective. In each: knowledge or theory, then the author's analysis, then evidence. Separate what sources found from the author's own view.
4. Final chapter บทสรุป: สรุปผลตามวัตถุประสงค์, อภิปรายผล, ข้อเสนอแนะเพื่อนำไปใช้, ข้อเสนอแนะเพื่อการศึกษาต่อ. Recommendations must follow from the content.
5. บรรณานุกรม (Thai before English), ภาคผนวก if needed.

**Do NOT include in a general academic report** (research-only parts): บทคัดย่อ/Abstract, ระเบียบวิธีวิจัย (population, sample, instruments), ผลการวิจัย, สมมติฐาน, กรอบแนวคิดการวิจัย, ช่องว่างงานวิจัย (research gap), ข้อจำกัดของการวิจัย. Add one only if the user explicitly asks.

Still apply to both types: Step 1a cover-details question round (before anything else), Step 3 real-source search and verification, Step 5 citation rules, Step 6 build, Step 7 QA. Build with the same tagged file; just use the structure above.

This skill does **not** produce slides. If the user also wants a presentation of the
same research, finish the report, then hand off to a slide skill.

## Skills this one depends on

Load the base skill before building anything; load the others only when their input or
output is actually part of the job. Invoke each with the Skill tool (the name may carry
a prefix such as `anthropic-skills:` depending on the install).

| When | Skill | What it contributes |
|---|---|---|
| **Always**, before Step 6 | `docx` | docx-js build, gotchas, render-to-image QA, helper scripts |
| User supplies PDF papers or a PDF assignment brief | `pdf` | Extract text/tables (pdfplumber), OCR scanned pages |
| User supplies survey/experiment data (.xlsx/.csv) | `xlsx` | Read and clean data, compute statistics with formulas |
| Results need a chart | `dataviz` | Chart form, palette, labelling — read before any chart code |
| User has interview/open-ended data to analyse | `design:research-synthesis` | Theme extraction, frequency ("X of Y"), quotes, insight tables |
| User needs to *design* the study (instruments, sampling) | `design:user-research` | Method choice, sample sizes, interview guide structure |

If a dependency skill isn't installed, say which one is missing and continue with the
closest built-in approach rather than stopping.

Reference files in this skill (read when the step says so):
- `references/user-academic-writing-style.md` — the user's preferred academic writing
  and formatting model, learned from their MIDTERM Word/PDF example. Read before
  outlining or drafting reports for this user; scale its structure to the assignment.
- `references/model-build-pipeline.md` — **how to build** that approved layout with
  Microsoft Word (scripts, template, QA). Use it in Step 6 for this user.
- `references/word-tag-format.md` — tag reference for `scripts/build_research_docx.ps1`
- `references/thai-academic-format.md` — page setup, fonts, heading levels, Thai
  numbering conventions, front matter
- `references/citation-styles.md` — APA 7 / IEEE / Vancouver patterns, Thai vs.
  English author rules, Buddhist-era years
- `references/methods-and-data.md` — how each data type flows into Methodology/Results
- `references/qa-checklist.md` — the pre-delivery checklist for Step 7

## Step 1 — Gather the essentials

Pull from everything already in the conversation and any files the user attached (prior
interview scripts, data, related coursework, an assignment brief) before asking the
user to repeat themselves. Ask only for what is genuinely missing, in one message:

| Item | Required? | Default if not given |
|---|---|---|
| Topic / research question | Required | — |
| Discipline | Should have | Infer from the topic; never default to business/finance framing |
| Data available (survey, interviews, financials, experiment) or literature-based | Should have | Ask — this decides Methodology/Results |
| Output type: full report, or specific chapters (บทที่ 1-5) | Should have | Full report |
| Citation style | Optional | APA 7th · IEEE for engineering/CS · Vancouver for medicine/health |
| Length | Optional | Course report ~2,000-4,000 words of main body; more for thesis chapters |
| University template / cover format | Optional | Ask for a sample; never guess institutional requirements |

### Step 1a — Ask for the cover and front-matter details BEFORE any research (required)

The user asked for this explicitly: never start searching, outlining or building while
cover details are unknown, and never ship a cover full of `......` blanks. Before Step 2,
check every item below against the conversation, attached files and the memory/profile.
Ask for **all** missing items in **one** question round. Use the `AskUserQuestion` tool when it
is available (one question per item group, with the profile value as the first option
marked "(ตามข้อมูลเดิม)" so the user can confirm with one click). Otherwise ask in one
short Thai message and wait for the answer.

| Item | Ask even if a profile default exists? | Notes |
|---|---|---|
| ชื่อ–นามสกุลผู้จัดทำ (และสมาชิกกลุ่ม ถ้าเป็นงานกลุ่ม) | Confirm | Group work changes the cover and คำนำ signature |
| รหัสนักศึกษา | Confirm | |
| รายวิชา (ชื่อ และรหัสวิชา ถ้ามี) | Ask | Changes every assignment |
| ชื่ออาจารย์ผู้สอน (พร้อมคำนำหน้า/ตำแหน่ง) | Ask | Never invent titles such as ดร. or ผศ. |
| ภาคเรียน และปีการศึกษา | Ask | Do not infer from today's date |
| สาขา / คณะ | Confirm | |
| มหาวิทยาลัย และตรามหาวิทยาลัย | Confirm university; **find the seal yourself, then confirm** | Do not ask the user to supply the seal (user instruction, 12 Nov 2026). Download the official seal from the university's own site (RMUTP: see `model-build-pipeline.md`). If the sandbox proxy blocks the host, request that exact host through the environment tools (`update_environment`/`create_environment`), then retry. Send the downloaded image to the user and ask "ใช่ตรานี้ไหม" **before** inserting it. Never draw, trace or generate a seal |
| รูปแบบปก/แม่แบบของผู้สอน | Ask once | If the instructor gave a template, it overrides the model layout. If there is no course (e.g. a test or self-study report), drop the รายวิชา/เสนอ lines instead of leaving dotted blanks |
| การอ้างอิงในเนื้อหา | Ask | Two options: (a) APA in-text citations (ผู้แต่ง, ปี) plus บรรณานุกรม (standard academic practice), or (b) **no in-text citations**: บรรณานุกรม at the end only, with the "ที่มา:" lines under tables and figures kept. This user chose (b) on 12 Nov 2026. Mention once that many courses require (a) |
| ความยาว และรูปแบบการอ้างอิง | Ask only if the brief is silent | Defaults in the table above |

**No in-text citation mode (option b).** Write facts as plain statements. Where a
sentence's subject was a researcher ("Wang et al. (2024) พบว่า…"), describe the work instead
("งานสำรวจที่สังเคราะห์งานวิจัยด้าน … พบว่า…", "การศึกษาภาคสนามกับพนักงาน 5,172 คน…"),
or refer back to the section that introduced it ("ตามที่อธิบายไว้ในหัวข้อ 3.3").
Organisations whose framework *is* the topic (NIST, OWASP, สพธอ., สคส.) may still be named
as subjects. Every bibliography entry must still be used somewhere in the content. Keep the
source log from Step 3 so the user can switch back to option (a).

Only items the user explicitly says to leave blank (e.g. "ยังไม่รู้ชื่ออาจารย์ ใส่ทีหลัง")
may stay as blanks; list them again in the hand-off message. Write the answers into
the session memory/profile only if the user agrees, so the next report can offer them as
defaults.

**Thesis-chapter mode.** Thai theses often use the five-chapter layout. If the user
asks for "บทที่ 1-5" or a single chapter, map it as:
บทที่ 1 บทนำ · บทที่ 2 เอกสารและงานวิจัยที่เกี่ยวข้อง · บทที่ 3 วิธีดำเนินการวิจัย ·
บทที่ 4 ผลการวิจัย · บทที่ 5 สรุป อภิปรายผล และข้อเสนอแนะ.
Write only the chapters asked for, but keep numbering and cross-references consistent
with the full layout.

## Step 2 — Prepare the user's own inputs (when any exist)

Do this before the literature search so the search can target what the data shows.
Details per data type are in `references/methods-and-data.md`.

- **PDF papers / brief** → `pdf` skill: extract text, record full citation details of
  each paper (they count toward Step 3's verified sources only if the bibliographic
  details are confirmed).
- **Survey / quantitative data** → `xlsx` skill: clean, then compute the descriptive
  statistics the report will cite (n, %, mean, SD; inferential tests only if the design
  supports them). Every number in Results must trace to this computation. Never invent
  or round-to-look-nice.
- **Interviews / open-ended answers** → `design:research-synthesis`: themes with
  frequency ("7 จาก 12 คน"), representative quotes, and separate what was observed from
  interpretation.
- **No data yet but the user must design the study** → `design:user-research` for the
  method, sample size, and instrument (questionnaire / interview guide), which then
  becomes the Methodology section.

## Step 3 — Search for real reference research (required, every time)

Before writing the literature review, **always search the web** for real published
research relevant to the topic. Do not rely on memory alone, and never invent a source.
Aim for a mix of:

- **International**: peer-reviewed articles (ScienceDirect, SpringerLink, IEEE Xplore,
  JSTOR, SSRN, PubMed, the journal's own site) or major international organisation
  reports (UN, World Bank, IMF, WHO, OECD — by field).
- **Thai / national**: ThaiJO journals, TDC (Thai Digital Collection) theses,
  university repositories, ministry reports, Bank of Thailand, NESDC (สศช.), NSTDA
  (สวทช.), NSO (สำนักงานสถิติแห่งชาติ) — by field.

For each candidate, fetch it and verify it is a real, complete, published work (not a
stub, blog summary, or broken link): identifiable authors, venue, year, and ideally a
DOI or stable URL. Minimum 4-8 verified sources for a course report; 15+ for a thesis
literature chapter. Prefer the last 5-10 years unless the source is foundational.

If a genuinely relevant source cannot be found after a reasonable search, tell the user
rather than citing something tangential to fill a slot.

Keep a source log as you go (authors, year, title, venue, volume/issue/pages,
DOI/URL, and one line on what it contributes). Steps 5 and 7 are built from this log.

## Step 4 — Structure (research reports only)

> Applies only when the routing rule above says **research report**. For a general academic report use that section's structure instead.

Standard skeleton — adapt names and order to the discipline and to what the user
already has, but keep this backbone:

1. **บทคัดย่อ (Abstract)** — 150-250 words: problem, method, key finding, implication.
   Add 3-5 คำสำคัญ (keywords). Add an English abstract only if the user or template
   requires one.
2. **บทนำ (Introduction)** — background, problem statement, research questions /
   objectives (numbered), scope, expected benefits (ประโยชน์ที่คาดว่าจะได้รับ), and
   definitions of key terms (นิยามศัพท์เฉพาะ) when the field expects them.
3. **ทบทวนวรรณกรรม (Literature Review)** — organise by theme or concept, not
   source-by-source; end with the research gap and, for empirical work, a conceptual
   framework (กรอบแนวคิดการวิจัย) and hypotheses if any.
4. **วิธีวิจัย (Methodology)** — design, population and sample (with how size was
   decided), instruments, instrument quality checks (e.g. IOC, reliability) only if
   actually done, data collection, analysis, and research ethics where relevant.
5. **ผลการวิจัย (Results)** — findings ordered by objective; tables and charts where
   they clarify data; report numbers, don't interpret here.
6. **อภิปรายผล (Discussion)** — interpret results against the literature and each
   objective; say where findings agree or disagree with prior work.
7. **สรุปและข้อเสนอแนะ (Conclusion & Recommendations)** — summary, limitations,
   practical recommendations, future research.
8. **เอกสารอ้างอิง (References)**
9. **ภาคผนวก (Appendices)** — instrument, extra tables — only when material exists.

Conceptual or literature-based topics: merge 4-5 into a synthesis section
(การสังเคราะห์) instead of inventing a methodology the paper doesn't have.

Never fabricate data, sample sizes, statistical results, reliability coefficients, or
ethics approvals. If the user wants a proposal-stage report (no data yet), write
Methodology in the future tense as a plan and omit Results, or mark those sections as
pending data. Say which you did.

## Step 5 — Citations

Read `references/citation-styles.md` before writing citations. If the user chose the
no in-text citation mode in Step 1a, the rules below still apply to the source log,
the บรรณานุกรม and the "ที่มา:" notes. Only the in-text (ผู้แต่ง, ปี) markers are dropped.

- Every citation must trace to a source verified in Step 3. Never invent sources, page
  numbers, DOIs, or quotes. If a claim can't be backed, soften it, ask the user for a
  source, or mark it `[ต้องการแหล่งอ้างอิงเพิ่มเติม]` — a fabricated citation in an
  academic submission is far worse than an honest gap.
- Paraphrase web-sourced material in your own words. At most one direct quote per
  source, under 15 words, and only when truly needed.
- In-text and reference-list style must match the style chosen in Step 1, and every
  in-text citation must have exactly one matching reference entry and vice versa.
- Thai and English sources follow different author rules (Thai: full given name +
  surname, no inversion). Follow the reference file.

## Step 6 — Build the `.docx`

**Default for this user (Windows with Microsoft Word):** follow
`references/model-build-pipeline.md` — fill `assets/template_model.txt`, run
`scripts/build_research_docx.ps1` then `scripts/modelfmt.ps1`. This reproduces the
user-approved model layout (RMUTP seal cover, ก ข ค front matter, navy-header tables,
Thai/English reference groups).

**No Word (Linux, the Claude API / code-execution container, macOS, phone):** build the
same model layout from the same tagged file with Node.js — no Word, no npm packages:

```bash
node scripts/build_research_docx.js report.txt "รายงาน_<หัวข้อสั้น>.docx"
```

- Write the tagged file exactly as for the Word route (`assets/template_model.txt`,
  `references/word-tag-format.md`). The script reproduces both Word scripts: cover
  without page number, ก ข ค front matter, 1 2 3 body, numbers top-right, TH Sarabun New
  16/20 pt, Thai distributed justify, navy-header banded grid tables, bold caption
  labels, สารบัญตาราง + สารบัญภาพ on one page.
- สารบัญ / สารบัญตาราง / สารบัญภาพ come out **without page numbers** (Word fields that
  Word may or may not refresh on open). A user received a report with an empty สารบัญ
  this way, so always fill the numbers before delivery:
  1. Install the real TH Sarabun New (SIPA v1.35) so the page layout matches Word. See
     "Fonts without Word" in `references/model-build-pipeline.md`. Do **not** use the
     `font-th-sarabun-new` npm package: its webfont files are scaled wrong (about 1.5× wider),
     so the page numbers come out wrong.
  2. Run `python3 scripts/fill_toc_pages.py report.docx report_final.docx`. It renders
     the file with LibreOffice, finds the page of every heading, table and figure caption,
     and writes the numbers into the contents lists. It also removes the "update fields?"
     prompt. The fields stay, so the user can still refresh them after editing.
  3. Check that the run prints `MISSING []`. Any entry listed there needs a manual look.
     Then read the contents pages of the rendered PDF.
- A missing image (e.g. the RMUTP seal when there is no network) is skipped with a
  WARNING on stderr instead of failing. Try the seal download from
  `model-build-pipeline.md` first; if it fails, say the seal is missing.
- Check the run printed `SAVED=`. Render-to-image QA (Step 7) works the same way.

Use the generic docx-js route below only if Node.js is unavailable, and tell the user
the layout will differ from the model.

**Last resort (no Word, no Node.js):** load the `docx` skill and follow it end to end (docx-js build, gotchas, page setup,
verification-by-render). Read `references/thai-academic-format.md` for the page and
font defaults. On top of the base skill:

- `HeadingLevel.*` for every section heading so the table of contents (สารบัญ) works;
  include a TOC for anything longer than a short course report.
- Tables for structured results, with numbered captions above the table
  (ตารางที่ 1 ...) and figure captions below the figure (ภาพที่ 1 ...). Follow the
  base skill's dual-width table rule and `ShadingType.CLEAR`.
- Charts: read `dataviz` first. Render to PNG at print resolution (≥200 dpi) with Thai
  labels in a Thai-capable font, embed with `ImageRun` (`type: "png"`), and keep the
  underlying numbers in a table or appendix so the reader can check them.
- Page numbers in the footer; front matter and body numbering per the format file.
- Save the output in the user's working directory (or where they ask), with a
  descriptive filename, e.g. `รายงานวิจัย_<หัวข้อสั้น>.docx`.

## Step 7 — QA and deliver

Run the checklist in `references/qa-checklist.md`. At minimum:

1. Render the `.docx` to images (docx skill's soffice + pdftoppm steps) and look at
   every page: missing sections, broken tables, Thai glyphs rendering (no boxes or
   floating vowels/tone marks), captions, page numbers.
2. Citation cross-check: every in-text citation resolves to a reference entry, every
   reference entry is cited, author/year match exactly.
3. Every number in Results matches the computed data from Step 2.
4. No leftover placeholders (`lorem`, `TODO`, `xxx`, `[insert`, `...`), and no dotted
   blanks on the cover unless the user chose to leave that field blank (Step 1a).
5. Every สารบัญ / สารบัญตาราง / สารบัญภาพ entry has a page number (Step 6).
6. Readability pass from `references/user-academic-writing-style.md` → "สำนวนที่ไม่แข็ง":
   the report must not read stiff (user feedback, 12 Nov 2026).

Then tell the user where the file is, how many verified sources were used, and anything
left for them: cover-page details, sections marked as needing a source, or data still
pending.

## Notes

- Default language is Thai unless the user asks for English (e.g. an international
  journal or conference).
- Discipline-agnostic: don't assume finance/business framing because past projects were
  business-oriented; the user's topic drives the literature and method.
- Font caveat: if no Thai font (TH Sarabun New / Sarabun) is installed where the file is
  rendered, say so explicitly rather than shipping a file whose preview can't be
  trusted for Thai glyphs.
- If the request is outside this skill's scope (e.g. a business plan deck, a non-academic
  memo), ask before forcing it into this structure.