# Citation styles

Use one style for the whole report. Default is APA 7th. Every example below shows the
pattern only — never copy example names, titles, or DOIs into a real report.

## APA 7th (default)

### Author rules — Thai vs. English

| | Thai author | English author |
|---|---|---|
| Name form | Full given name + surname, not inverted, no initials | Surname, Initials |
| Year | Buddhist era as published (e.g. 2566) | Common era (e.g. 2023) |
| 2 authors (in-text) | ชื่อ สกุล และชื่อ สกุล | Surname & Surname |
| 3+ authors (in-text) | ชื่อ สกุล และคณะ | Surname et al. |

Thai titles such as ดร., ศ., รศ., ผศ. are omitted from citations.

### In-text

| Form | Thai | English |
|---|---|---|
| Parenthetical | (ชื่อ สกุล, 2566) | (Surname, 2023) |
| Narrative | ชื่อ สกุล (2566) | Surname (2023) |
| Two authors | (ชื่อ สกุล และชื่อ สกุล, 2566) | (Surname & Surname, 2023) |
| Three or more | (ชื่อ สกุล และคณะ, 2566) | (Surname et al., 2023) |
| Organisation | (สำนักงานสถิติแห่งชาติ, 2566) | (World Health Organization, 2023) |
| Direct quote | add page: (ชื่อ สกุล, 2566, น. 12) | (Surname, 2023, p. 12) |

### Reference list

Journal article:

```
ชื่อ สกุล, และชื่อ สกุล. (ปี พ.ศ.). ชื่อบทความ. *ชื่อวารสาร*, *ปีที่*(ฉบับที่), หน้าแรก–หน้าสุดท้าย. https://doi.org/xxxx
Surname, A. B., & Surname, C. D. (Year). Title of article. *Journal Name*, *Volume*(Issue), pages. https://doi.org/xxxx
```

Book:

```
ชื่อ สกุล. (ปี). *ชื่อหนังสือ* (พิมพ์ครั้งที่ x). สำนักพิมพ์.
Surname, A. B. (Year). *Title of book* (xth ed.). Publisher.
```

Thesis:

```
ชื่อ สกุล. (ปี). *ชื่อวิทยานิพนธ์* [วิทยานิพนธ์ปริญญามหาบัณฑิต, ชื่อมหาวิทยาลัย]. ชื่อคลัง. URL
Surname, A. B. (Year). *Title* [Master's thesis, University]. Repository. URL
```

Report / web document from an organisation:

```
ชื่อหน่วยงาน. (ปี). *ชื่อรายงาน*. URL
Organization Name. (Year). *Title of report*. URL
```

Formatting:
- Hanging indent 0.5" (`indent: { left: 720, hanging: 720 }`).
- Italics as marked with `*…*` above (use `italics: true` runs in docx-js).
- DOI as `https://doi.org/...` when one exists; otherwise a stable URL. No
  "Retrieved from" in APA 7.
- **Ordering:** common Thai university practice lists Thai-language references first
  (ordered by Thai alphabet), then English references (A–Z). Follow the template if it
  says otherwise.

## IEEE (engineering / computer science)

- In-text: bracketed numbers in order of first appearance: `[1]`, `[2], [5]`, `[3]–[6]`.
- Reuse the same number for a repeat citation.
- Reference list ordered by number, not alphabet:

```
[1] A. B. Surname, C. D. Surname, and E. Surname, "Title of article," *Journal Abbrev.*, vol. x, no. x, pp. xx–xx, Mon. Year, doi: xxxx.
[2] ชื่อ สกุล, "ชื่อบทความ," *ชื่อวารสาร*, ปีที่ x, ฉบับที่ x, น. xx–xx, ปี.
```

## Vancouver (medicine / health sciences)

- In-text: numbers in order of first appearance, in parentheses `(1)` or superscript —
  pick one.
- Reference list ordered by number; up to 6 authors listed, then "et al." / "และคณะ".

```
1. Surname AB, Surname CD. Title of article. Journal Abbrev. Year;Vol(Issue):pages. doi:xxxx
2. ชื่อ สกุล, ชื่อ สกุล. ชื่อบทความ. ชื่อวารสาร. ปี;ปีที่(ฉบับที่):หน้า.
```

## Cross-check procedure (Step 7)

1. Extract text: `pandoc -t plain report.docx -o report.txt`.
2. List every in-text citation (author + year, or number).
3. List every reference entry.
4. Confirm a one-to-one match: spelling of names, year, and "และคณะ/et al." usage
   consistent with the author count.
5. For numbered styles, confirm numbers appear in order of first use and none are
   skipped.
