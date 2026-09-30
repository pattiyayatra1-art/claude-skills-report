---
name: research-report-writer
description: >
  Write full academic research reports in Thai (.docx) — covering any discipline, not
  just business/finance — with proper structure (abstract, introduction, literature
  review, methodology, results, discussion, conclusion, references) formatted as a
  polished Word document. Always searches for and cites real, verified international
  and Thai published research — never fabricated or placeholder sources. Also handles
  the inputs a report is built from: survey/Excel data, interview transcripts, and PDF
  papers the user supplies. Use whenever the user asks for a "งานวิจัย", "รายงานวิจัย",
  "รายงานวิชาการ", "research paper", "research report", a thesis/project chapter
  (บทที่ 1-5), or an academic write-up in Thai, even if they only give a topic. Trigger
  on partial requests like "ช่วยเขียนงานวิจัยเรื่อง...", "ทำรายงานวิจัยให้หน่อย",
  "เขียนบทที่ 2 ให้หน่อย", or "สรุปงานวิจัยเป็น Word". Word-document skill only — for a
  matching presentation deck, point the user to a slide-focused skill instead.
---

# Research Report Writer (v2)

Produces a full academic research report as a `.docx` file, in Thai, structured to the
convention Thai universities expect. It layers research content, method, and citation
rules on top of the base Word skill, and pulls in the related skills below when the
report needs them.

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
| Author names, student IDs, course, instructor | Optional | Leave the cover page fields for the user rather than inventing them |

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

## Step 4 — Structure

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

Read `references/citation-styles.md` before writing citations.

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

Load the `docx` skill and follow it end to end (docx-js build, gotchas, page setup,
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
4. No leftover placeholders (`lorem`, `TODO`, `xxx`, `[insert`, `...`).

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
