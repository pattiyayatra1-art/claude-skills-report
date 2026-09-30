# From data to Methodology and Results

How each kind of input becomes report content, and which companion skill handles it.
The rule throughout: **every number, theme count, and quote in the report must come
from the user's actual data or a verified source.** If the data doesn't support a
statement, don't make it.

## Quantitative data (questionnaire, experiment, financial data)

Companion skills: `xlsx` to read/clean, `dataviz` for charts.

1. Read the file with the xlsx skill (pandas for analysis). Report to the user: number
   of rows, missing values, obviously invalid responses. Ask before dropping anything.
2. Compute what the design supports:
   - Demographics: frequency and percentage.
   - Likert scales: mean and SD per item and per construct, with the interpretation
     bands stated in Methodology (e.g. 4.21-5.00 = มากที่สุด for a 5-point scale —
     state the band you use).
   - Inferential tests (t-test, ANOVA, correlation, regression) only when the research
     questions call for them and the sample allows it. Report the test, statistic,
     df, p-value, and effect size where standard.
3. Keep the computation reproducible (a script or a workbook with formulas) and tell the
   user where it is.
4. Results: one table per objective or construct, numbered captions, then a short
   paragraph stating what the table shows — no interpretation (that goes in
   Discussion).

Methodology should state: population, sample size and how it was determined (e.g.
Krejcie & Morgan table, Yamane formula, G*Power) — **only the method the user actually
used**, the sampling technique, the instrument, and the analysis methods.

Instrument quality (IOC, Cronbach's alpha, pilot test): report only if the user did it
and gives the values. Otherwise, omit or list it as a limitation.

## Qualitative data (interviews, focus groups, open-ended answers)

Companion skill: `design:research-synthesis`.

1. Code the transcripts into themes. For each theme record: frequency (X จาก Y คน),
   a one-line summary, and 1-2 short verbatim quotes with a participant code (ผู้ให้
   ข้อมูลคนที่ 3).
2. Separate observation from interpretation: Results reports what participants said;
   Discussion interprets it against the literature.
3. Anonymise: no real names, workplaces, or identifying details unless the user
   confirms consent to use them.

Methodology should state: key informants and selection criteria (purposive,
snowball …), number of participants, interview format and length, and analysis approach
(e.g. thematic analysis / content analysis).

## Mixed methods

Present quantitative and qualitative results separately under each objective, then
integrate them in Discussion (where they converge, where they diverge).

## Designing the study (no data yet)

Companion skill: `design:user-research`.

Use it to choose the method and sample size and to draft the instrument (questionnaire
items tied to each construct in the conceptual framework, or an interview guide). Put
the instrument in ภาคผนวก. Write Methodology as a plan, and leave Results as pending —
never simulate responses.

## Literature-based / conceptual papers

No Methodology/Results split. Replace with a synthesis section: describe how sources
were selected (databases, keywords, years, inclusion criteria), then synthesise by
theme, with a comparison table of key studies (author/year, context, method, finding).

## Source material in PDF

Companion skill: `pdf`.

- Extract text with pdfplumber; OCR scanned pages with pytesseract (Thai needs the
  `tha` language pack — say so if it's missing).
- Confirm bibliographic details (authors, year, venue, DOI) from the PDF's own front
  matter or the publisher page before citing.
- An assignment brief PDF defines requirements (length, sections, style) — those
  override this skill's defaults.
