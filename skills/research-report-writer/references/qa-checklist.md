# Pre-delivery QA checklist

Run all of it before telling the user the report is done. Report anything that fails
and wasn't fixed.

## 1. Render and look

- [ ] Converted to PDF and to page images (docx skill: `soffice.py` + `pdftoppm`).
- [ ] Every page viewed, not just the first few.
- [ ] Thai text renders correctly: no boxes (tofu), no floating or stacked tone marks
      and vowels, no Latin fallback font in Thai runs.
- [ ] Headings are consistent in size and numbering; the TOC lists them with correct
      page numbers (update fields if needed).
- [ ] Tables fit inside the margins, no overflowing columns, header row distinct.
- [ ] Charts are legible at print size, Thai labels render, numbered captions present.
- [ ] Page numbers present and correct (front matter vs. body).

- [ ] Every สารบัญ / สารบัญตาราง / สารบัญภาพ entry shows a page number, and the
      numbers match the rendered pages (`fill_toc_pages.py` printed `MISSING []`).
- [ ] No table column is so narrow that Thai text breaks every few characters.
- [ ] Cover is complete: seal, author, ID, course, instructor, semester, year (or
      blanks the user chose to leave, listed in the hand-off).

## 2. Content completeness

- [ ] Every section from Step 4 present (or deliberately merged/omitted, and the user
      told why).
- [ ] Abstract is 150-250 words and includes problem, method, finding, implication.
- [ ] Each research objective is answered in Results and discussed in Discussion.
- [ ] Limitations stated honestly.
- [ ] Word count of main body is within the requested length.

- [ ] Readability pass ("สำนวนที่ไม่แข็ง" in `user-academic-writing-style.md`): each
      content chapter has a concrete scenario/example; few paragraphs open with an
      author name; group-author names abbreviated after first use; bullets ≤ half the
      paragraph count.

## 3. Integrity

- [ ] Every source in the reference list was fetched and verified in Step 3.
- [ ] One-to-one match between in-text citations and reference entries
      (see `citation-styles.md` cross-check procedure).
- [ ] No invented DOIs, page numbers, quotes, statistics, sample sizes, or approvals.
- [ ] Every number in Results matches the computed data.
- [ ] Direct quotes: ≤1 per source, <15 words, with page number.
- [ ] Participants are anonymised.

## 4. Leftovers

Search the extracted text for placeholders:

```
pandoc -t plain report.docx | grep -niE "lorem|todo|xxx|\[insert|tbd|placeholder|\.\.\.\]"
```

On Windows PowerShell:

```
pandoc -t plain report.docx | Select-String -Pattern 'lorem|todo|xxx|\[insert|tbd|placeholder' -CaseSensitive:$false
```

- [ ] Only intentional markers remain (e.g. `[ต้องการแหล่งอ้างอิงเพิ่มเติม]`, cover-page
      blanks) — and they're listed for the user.

## 5. Hand-off message

Tell the user:
- Where the file is saved.
- Number of verified sources (Thai / international).
- What they still need to fill in or check (cover page, sections needing sources,
  pending data, university template differences).
