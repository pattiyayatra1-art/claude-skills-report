# Tagged input format (`build_research_docx.ps1`)

The input is UTF-8 text with one item per line. A paragraph is exactly one line, with no embedded newlines. Blank lines and lines starting with `#` are ignored. Any unknown tag stops the build with an error that names the offending line.

Inside `[P]`, `[PN]`, `[LI*]`, `[REF]`, `[NOTE]`, `[KW]` and `[C/L/R]` text you can use inline `**bold**` and `*italic*`. Use italic for APA titles of books and journals and for statistical symbols (*t*, *F*, *p*, *r*).

## Layout and sections
| Tag | Effect |
|---|---|
| `[SECTION:front]` | Section break (new page). Front matter starts here and is numbered ก ข ค, restarting at ก. Everything before it is the cover and has no page number. |
| `[SECTION:body]` | Section break (new page). Numbering switches to 1 2 3, restarting at 1. Put it right before `[CH]บทที่ 1|บทนำ`. |
| `[PAGEBREAK]` | Page break within a section, e.g. between the outer and inner cover |
| `[BLANK]` / `[BLANK:n]` | n empty lines, used for vertical spacing on the cover or approval page |
| `[C:size:b]text` | Centred line; the size (pt) and `b` (bold) are optional, e.g. `[C:20:b]`, `[C:18]`, `[C]` |
| `[L:…]` / `[R:…]` | Same, left- or right-aligned. Use `[R]` for the signature under กิตติกรรมประกาศ and `[R:16:b]หน้า` above the contents lists. |

## Headings (all feed the table of contents)
| Tag | Effect |
|---|---|
| `[FH]text` | Front-matter heading such as บทคัดย่อ, ABSTRACT, กิตติกรรมประกาศ, สารบัญ, สารบัญตาราง or สารบัญภาพ: new page, centred, 20 pt bold, TOC level 1 |
| `[CH]บทที่ 1\|บทนำ` | Chapter title: new page, two centred lines, 20 pt bold. The TOC shows it as "บทที่ 1 บทนำ". |
| `[BACK]text` | Back-matter heading such as บรรณานุกรม or ประวัติผู้วิจัย: new page, centred, TOC level 1 |
| `[APPX]ภาคผนวก ก\|แบบสอบถาม` | Appendix title page, formatted like `[CH]` |
| `[H2]1.1 text` | Section heading: bold, flush left, TOC level 2. Type the number yourself. |
| `[H3]1.1.1 text` | Sub-section heading: bold, indented 0.5″. It is not in the TOC unless you pass `-TocLevels 3`. |

## Body
| Tag | Effect |
|---|---|
| `[P]text` | Body paragraph with a 0.5″ first-line indent and Thai distributed justification |
| `[PN]text` | Body paragraph with no indent |
| `[LI]text` `[LI2]` `[LI3]` | List item at level 1, 2 or 3 with a hanging indent. Type the marker yourself, e.g. `1)`, `1.1)`, `-`. |
| `[KW]คำสำคัญ: a, b, c` | Keywords line; the label before the colon is bold. Works for `Keywords:` too. |
| `[REF]entry` | Bibliography entry: 0.5″ hanging indent, left-aligned |

## Tables and figures
```
[TCAP]ตารางที่ 4.1 จำนวนและร้อยละของผู้ตอบแบบสอบถาม จำแนกตามเพศ
[TABLE:apa]
[TR]เพศ | จำนวน (คน) | ร้อยละ
[TR]ชาย | 180 | 45.00
[TR]หญิง | 220 | 55.00
[TR]รวม | 400 | 100.00
[/TABLE]
[NOTE]ที่มา: จากการสำรวจของผู้วิจัย (2568)
```
- The `[TCAP]` caption goes **above** the table. Its label ("ตารางที่ 4.1") is bolded automatically and it feeds สารบัญตาราง.
- `[TABLE:apa]` draws a three-line APA table. `[TABLE]` or `[TABLE:grid]` draws a full grid. The first row is a bold header that repeats when the table breaks across pages. Column 1 is left-aligned and the other columns are centred.
- Cells are separated by `|`. Keep a literal `|` out of the cell text.
- `[NOTE]` goes under a table, one line each, for **ที่มา:** or **หมายเหตุ:**. It is set 2 pt smaller and the label is bold.

```
[IMG]figures/framework.png|14
[FCAP]ภาพที่ 2.1 กรอบแนวคิดในการวิจัย
```
- `[IMG]path|widthCm` inserts a centred picture. A relative path is resolved from the input file's folder, and the default width is 14 cm.
- `[FCAP]` is the caption **below** the figure. It is centred, its label is bold, and it feeds สารบัญภาพ.
- For appendix figures use the label `ภาพภาคผนวก ก1`, and for appendix tables `ตารางภาคผนวก ก1`.

## Auto contents lists
| Tag | Inserts |
|---|---|
| `[TOC]` | สารบัญ: headings level 1 to `-TocLevels` (default 2) plus every `[FH]` |
| `[LOT]` | สารบัญตาราง: every `[TCAP]` |
| `[LOF]` | สารบัญภาพ: every `[FCAP]` |

Put each of these right after its `[FH]` heading and a `[R:16:b]หน้า` line. They are Word fields that the script updates before saving. If the user edits the document later, right-click → Update Field refreshes them.

## Column widths (Node builder)

`build_research_docx.js` sizes columns from the longest cell in each column. A column
whose longest cell is at most 24 characters gets a fixed width (`0.24 cm × length + 0.6 cm`,
capped at 4.5 cm). Longer columns share what is left in proportion to their length. Two
long columns next to a medium one leave the medium column only about 2.5 cm wide, and
Thai text then breaks every few characters. Write tables with a short first column
(`ระดับ`, `ประเด็น`) and balanced text columns, or merge into three columns. Always look
at the rendered table.

## Contents page numbers

`[TOC]`, `[LOT]` and `[LOF]` produce entries without page numbers. After building, run
`scripts/fill_toc_pages.py` (see `model-build-pipeline.md`) so the delivered file shows
real page numbers.
