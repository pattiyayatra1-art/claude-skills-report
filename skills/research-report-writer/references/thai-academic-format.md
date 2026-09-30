# Thai academic report format — defaults

These are the common defaults across Thai universities. They are **defaults only**: if
the user supplies a university template, style guide, or sample, it overrides everything
here. When in doubt about an institution-specific rule, ask.

## Page setup

| Setting | Default | docx-js value |
|---|---|---|
| Paper | A4 | docx-js default (no override needed) |
| Margin top | 1.5" | `top: 2160` (DXA) |
| Margin left | 1.5" | `left: 2160` |
| Margin bottom | 1" | `bottom: 1440` |
| Margin right | 1" | `right: 1440` |
| Line spacing | Single | `spacing: { line: 240 }` |

## Fonts

| Element | Font | Size | docx-js `size` (half-points) |
|---|---|---|---|
| Body text | TH Sarabun New (fallback: Sarabun) | 16 pt | 32 |
| Chapter / main section title | same | 20 pt bold, centred | 40 |
| Heading level 2 | same | 18 pt bold | 36 |
| Heading level 3 | same | 16 pt bold | 32 |
| Table text | same | 14-16 pt | 28-32 |
| Captions | same | 16 pt; label (ตารางที่ 1) bold | 32 |

Set the font on the document default style and on every heading style, including the
East Asian / complex-script font slots, otherwise Word may fall back to a Latin font for
Thai runs. In docx-js set `font: { ascii, hAnsi, cs, eastAsia }` all to the Thai font
name and use `sizeComplexScript` alongside `size`.

TH Sarabun New renders small; never drop body text below 16 pt.

## Paragraphs

- Indent the first line of body paragraphs 0.5" (`indent: { firstLine: 720 }`).
- Thai has no spaces between words, so full justification can stretch lines badly.
  Use `AlignmentType.THAI_DISTRIBUTE` if the renderer supports it; otherwise left
  alignment is safer than `JUSTIFIED`. Check the render.
- Don't insert spaces to force Thai line breaks.

## Heading numbering

Two conventions are common — pick one and apply it throughout:

- **Decimal:** 1, 1.1, 1.1.1 (common in science/engineering)
- **Chapter layout (thesis):** บทที่ 1 … then 1.1, 1.2 inside each chapter

Keep heading text on `HeadingLevel.HEADING_1/2/3` so the TOC picks it up.

## Front matter (include what the report type needs)

Order: ปก (cover) → บทคัดย่อ → Abstract (if required) → กิตติกรรมประกาศ (thesis only)
→ สารบัญ → สารบัญตาราง → สารบัญภาพ → body.

- Cover: title, author name(s) and ID(s), course/program, instructor, institution,
  semester/academic year (ปีการศึกษา, Buddhist era). Leave unknown fields as clearly
  marked blanks for the user — never invent names or IDs.
- Front-matter pages use Thai letters (ก, ข, ค …) as page numbers; the body restarts
  at 1. Use separate sections with `pageNumbers: { start: 1, formatType: ... }`.
- Page numbers commonly sit top-right or bottom-centre; follow the template.

## Tables and figures

- Caption **above** tables: **ตารางที่ 1** ชื่อตาราง
- Caption **below** figures: **ภาพที่ 1** ชื่อภาพ
- Number consecutively through the document (or per chapter: ตารางที่ 4.1 in thesis
  layout).
- Add a source line under borrowed tables/figures: ที่มา: (ผู้แต่ง, ปี)
- Refer to every table/figure in the text before it appears.

## Numbers and years

- Arabic numerals are the default; use Thai numerals only if the template demands it.
- Thai sources use the Buddhist-era year (พ.ศ.) as published; English sources use the
  Common Era. Do not convert a source's year. Convert only when writing prose dates if
  the user asks (พ.ศ. = ค.ศ. + 543).
