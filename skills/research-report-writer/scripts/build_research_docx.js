#!/usr/bin/env node
/*
 * Build the user's approved RMUTP model report as a .docx WITHOUT Microsoft Word.
 *
 * Reads the same tagged UTF-8 text as build_research_docx.ps1 (see
 * ../references/word-tag-format.md) and reproduces the layout that
 * build_research_docx.ps1 + modelfmt.ps1 produce in Word:
 *   - cover with no page number, front matter numbered ก ข ค, body numbered 1 2 3,
 *     page numbers top-right
 *   - TH Sarabun New 16 pt, headings 20 pt, Thai distributed justification
 *   - สารบัญ / สารบัญตาราง / สารบัญภาพ as real Word TOC fields (marked dirty so Word
 *     refreshes the page numbers when the file is opened)
 *   - tables: full grid, navy header (#1F3864) with white bold text, light-blue
 *     banded rows (#DCE6F2), bold caption label above, ที่มา below
 *   - สารบัญตาราง and สารบัญภาพ on one page, Heading 3 flush left, black headings
 *
 * Pure Node.js (no npm packages), so it runs in the Claude API code-execution
 * container as well as on Windows.
 *
 * Usage:  node build_research_docx.js <input.txt> <output.docx> [--toc-levels 2]
 * Prints  PARAGRAPHS=<n>, TABLES=<n>, IMAGES=<n>, SAVED=<path>; warnings go to stderr.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

// ---------------------------------------------------------------- arguments
const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node build_research_docx.js <input.txt> <output.docx> [--toc-levels 2]');
  process.exit(2);
}
const inputPath = path.resolve(args[0]);
const outputPath = path.resolve(args[1]);
let tocLevels = 2;
const tl = args.indexOf('--toc-levels');
if (tl >= 0 && args[tl + 1]) tocLevels = parseInt(args[tl + 1], 10);
const baseDir = path.dirname(inputPath);

// ---------------------------------------------------------------- layout constants
const FONT = 'TH Sarabun New';
const BODY_HP = 32;            // 16 pt in half-points
const HEAD_HP = 40;            // 20 pt
const TW_IN = 1440;            // twips per inch
const TW_CM = 567;             // twips per cm (approx.)
const PAGE_W = 11906, PAGE_H = 16838;                 // A4
const MARGIN = { top: 2160, left: 2160, right: 1440, bottom: 1440, header: 1152, footer: 720 };
const TEXT_W = PAGE_W - MARGIN.left - MARGIN.right;   // 8306 twips
const NAVY = '1F3864', BAND = 'DCE6F2';
const EMU_CM = 360000;

// ---------------------------------------------------------------- helpers
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function runProps({ bold = false, italic = false, size = null, color = null } = {}) {
  let p = '';
  if (bold) p += '<w:b/><w:bCs/>';
  if (italic) p += '<w:i/><w:iCs/>';
  if (color) p += `<w:color w:val="${color}"/>`;
  if (size) p += `<w:sz w:val="${size}"/><w:szCs w:val="${size}"/>`;
  return p ? `<w:rPr>${p}</w:rPr>` : '';
}
// Thai text must sit in runs flagged <w:cs/> (complex script), as Word itself writes
// it; otherwise Word does not apply Thai word breaking and thaiDistribute stretches
// the letters of whole lines apart. Split each run into Thai / non-Thai segments.
const THAI_SPLIT = /([฀-๿][฀-๿\s]*)/;
function run(text, opts = {}) {
  let out = '';
  for (const seg of text.split(THAI_SPLIT)) {
    if (!seg) continue;
    const thai = /^[฀-๿]/.test(seg);
    let rpr = runProps(opts);
    if (thai) rpr = rpr ? rpr.replace('<w:rPr>', '<w:rPr><w:cs/>') : '<w:rPr><w:cs/></w:rPr>';
    out += `<w:r>${rpr}<w:t xml:space="preserve">${esc(seg)}</w:t></w:r>`;
  }
  return out;
}
// **bold** and *italic* markdown -> real runs (Latin + Thai properties).
function mdRuns(text, base = {}) {
  let out = '';
  for (const part of text.split(/(\*\*.+?\*\*|\*.+?\*)/)) {
    if (!part) continue;
    let m;
    if ((m = part.match(/^\*\*(.+)\*\*$/))) out += run(m[1], { ...base, bold: true });
    else if ((m = part.match(/^\*(.+)\*$/))) out += run(m[1], { ...base, italic: true });
    else out += run(part, base);
  }
  return out;
}
function para(style, inner, extraPPr = '') {
  const ps = style ? `<w:pStyle w:val="${style}"/>` : '';
  const ppr = ps || extraPPr ? `<w:pPr>${ps}${extraPPr}</w:pPr>` : '';
  return `<w:p>${ppr}${inner}</w:p>`;
}
// Bold the label before the first colon ("ที่มา:", "คำสำคัญ:"), rest as markdown.
function labelled(text, base = {}) {
  const m = text.match(/^([^:：]+[:：])(.*)$/);
  if (!m) return mdRuns(text, base);
  return run(m[1], { ...base, bold: true }) + mdRuns(m[2], base);
}
// Bold the "ตารางที่ 4.1" / "ภาพที่ 2.1" label (first two words), title normal.
function captionRuns(text, sep) {
  const m = text.match(/^(\S+\s*\S+)\s+(.*)$/);
  if (!m) return run(text);
  const sepXml = sep === '\t' ? '<w:r><w:tab/></w:r>' : run(sep);
  return run(m[1], { bold: true }) + sepXml + mdRuns(m[2]);
}

// ---------------------------------------------------------------- read input
const lines = fs.readFileSync(inputPath, 'utf8').replace(/^﻿/, '').split(/\r?\n/).map((l) => l.replace(/\s+$/, ''));

// Pre-pass: collect TOC / LOT / LOF entries and find the last front heading.
const tocEntries = [], lotEntries = [], lofEntries = [];
let lastFrontIdx = -1, frontCount = 0;
lines.forEach((line, i) => {
  let m;
  if ((m = line.match(/^\[FH\](.*)$/))) { tocEntries.push({ lvl: 1, text: m[1] }); lastFrontIdx = i; frontCount++; }
  else if ((m = line.match(/^\[(CH|APPX)\](.*)$/))) tocEntries.push({ lvl: 1, text: m[2].split('|').map((s) => s.trim()).join(' ') });
  else if ((m = line.match(/^\[BACK\](.*)$/))) tocEntries.push({ lvl: 1, text: m[1] });
  else if ((m = line.match(/^\[H2\](.*)$/)) && tocLevels >= 2) tocEntries.push({ lvl: 2, text: m[1] });
  else if ((m = line.match(/^\[H3\](.*)$/)) && tocLevels >= 3) tocEntries.push({ lvl: 3, text: m[1] });
  else if ((m = line.match(/^\[TCAP\](.*)$/))) lotEntries.push({ lvl: 1, text: m[1] });
  else if ((m = line.match(/^\[FCAP\](.*)$/))) lofEntries.push({ lvl: 1, text: m[1] });
});
// modelfmt.ps1: สารบัญตาราง and สารบัญภาพ share a page -> last front heading does not break the page.
if (frontCount < 2) lastFrontIdx = -1;
const hasSections = lines.some((l) => /^\[SECTION:(front|body)\]$/.test(l));

// ---------------------------------------------------------------- body build
const body = [];
const images = [];      // {rid, name, data, ext}
const headers = {};     // section kind -> header part name
let current = hasSections ? 'cover' : 'body';
let tableRows = null, nTables = 0, nParas = 0, drawingId = 1;

function headerFor(kind) {
  if (kind === 'cover') return null;
  if (!headers[kind]) headers[kind] = { name: `header_${kind}.xml`, rid: `rIdHdr${kind}` };
  return headers[kind];
}
function sectPr(kind) {
  const h = headerFor(kind);
  const hdrRef = h ? `<w:headerReference w:type="default" r:id="${h.rid}"/>` : '';
  const pg = kind === 'front' ? '<w:pgNumType w:fmt="thaiLetters" w:start="1"/>'
    : kind === 'body' ? '<w:pgNumType w:fmt="decimal" w:start="1"/>' : '';
  return `<w:sectPr>${hdrRef}<w:type w:val="nextPage"/><w:pgSz w:w="${PAGE_W}" w:h="${PAGE_H}"/>`
    + `<w:pgMar w:top="${MARGIN.top}" w:right="${MARGIN.right}" w:bottom="${MARGIN.bottom}" w:left="${MARGIN.left}" w:header="${MARGIN.header}" w:footer="${MARGIN.footer}" w:gutter="0"/>`
    + `${pg}<w:cols w:space="720"/></w:sectPr>`;
}

// Word TOC field. The cached result already lists the entries (without page numbers)
// so viewers that never update fields still show the contents; dirty="true" makes
// Word recompute the real page numbers on open.
function tocField(instr, entries, styleFor) {
  const begin = `<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r><w:r><w:instrText xml:space="preserve"> ${esc(instr)} </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>`;
  const end = '<w:r><w:fldChar w:fldCharType="end"/></w:r>';
  if (entries.length === 0) return para('THPlain', begin + end);
  return entries.map((e, i) => {
    const pre = i === 0 ? begin : '';
    const post = i === entries.length - 1 ? end : '';
    return para(styleFor(e), pre + run(e.text.replace(/\*\*?/g, '')) + '<w:r><w:tab/></w:r>' + post);
  }).join('');
}

function imageSize(buf) {
  if (buf.slice(1, 4).toString() === 'PNG') return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20), ext: 'png' };
  if (buf[0] === 0xff && buf[1] === 0xd8) {
    let i = 2;
    while (i < buf.length) {
      if (buf[i] !== 0xff) { i++; continue; }
      const marker = buf[i + 1];
      const len = buf.readUInt16BE(i + 2);
      if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
        return { h: buf.readUInt16BE(i + 5), w: buf.readUInt16BE(i + 7), ext: 'jpeg' };
      }
      i += 2 + len;
    }
  }
  return null;
}
function imageXml(file, widthCm) {
  const buf = fs.readFileSync(file);
  const sz = imageSize(buf);
  if (!sz) throw new Error(`Unsupported image (use PNG or JPEG): ${file}`);
  const n = images.length + 1;
  const rid = `rIdImg${n}`;
  images.push({ rid, name: `image${n}.${sz.ext}`, data: buf, ext: sz.ext });
  const cx = Math.round(widthCm * EMU_CM);
  const cy = Math.round(cx * sz.h / sz.w);
  const id = drawingId++;
  return `<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="${cx}" cy="${cy}"/>`
    + `<wp:docPr id="${id}" name="Picture ${id}"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>`
    + `<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>`
    + `<pic:nvPicPr><pic:cNvPr id="${id}" name="${esc(path.basename(file))}"/><pic:cNvPicPr/></pic:nvPicPr>`
    + `<pic:blipFill><a:blip r:embed="${rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>`
    + `<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="${cx}" cy="${cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>`
    + `</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>`;
}

// Column widths as in build_research_docx.ps1: short columns get what their longest
// cell needs; "text" columns (longest cell > 24 chars) share the rest in proportion.
function columnWidths(rows, ncol) {
  const maxLen = new Array(ncol).fill(0);
  for (const r of rows) for (let c = 0; c < ncol; c++) {
    const len = (r[c] || '').replace(/\s+/g, ' ').trim().length;
    if (len > maxLen[c]) maxLen[c] = len;
  }
  const wide = [];
  for (let c = 0; c < ncol; c++) if (maxLen[c] > 24) wide.push(c);
  const widths = new Array(ncol).fill(0);
  let narrowSum = 0;
  for (let c = 0; c < ncol; c++) if (!wide.includes(c)) {
    widths[c] = Math.min(4.5, Math.max(1.0, 0.24 * maxLen[c] + 0.6)) * TW_CM;
    narrowSum += widths[c];
  }
  if (wide.length === 0) {
    if (narrowSum > TEXT_W) for (let c = 0; c < ncol; c++) widths[c] *= TEXT_W / narrowSum;
  } else {
    const minWide = 0.35 * TEXT_W;
    if (TEXT_W - narrowSum < minWide) {
      const scale = (TEXT_W - minWide) / narrowSum;
      for (let c = 0; c < ncol; c++) if (!wide.includes(c)) widths[c] *= scale;
      narrowSum = TEXT_W - minWide;
    }
    const wideTotal = wide.reduce((s, c) => s + maxLen[c], 0);
    for (const c of wide) widths[c] = (TEXT_W - narrowSum) * maxLen[c] / wideTotal;
  }
  return { widths: widths.map((w) => Math.round(w)), wide };
}

function flushTable(rows) {
  if (!rows.length) return;
  const ncol = Math.max(...rows.map((r) => r.length));
  const { widths, wide } = columnWidths(rows, ncol);
  const b = (side) => `<w:${side} w:val="single" w:sz="4" w:space="0" w:color="000000"/>`;
  let x = `<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="${widths.reduce((a, c) => a + c, 0)}" w:type="dxa"/><w:jc w:val="center"/>`
    + `<w:tblBorders>${b('top')}${b('left')}${b('bottom')}${b('right')}${b('insideH')}${b('insideV')}</w:tblBorders>`
    + `<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr>`
    + `<w:tblGrid>${widths.map((w) => `<w:gridCol w:w="${w}"/>`).join('')}</w:tblGrid>`;
  rows.forEach((r, ri) => {
    const header = ri === 0;
    // modelfmt.ps1: header navy; Word rows 3,5,7... (1-based) light blue.
    const fill = header ? NAVY : ((ri + 1) % 2 === 1 ? BAND : null);
    x += `<w:tr><w:trPr><w:cantSplit/>${header ? '<w:tblHeader/>' : ''}</w:trPr>`;
    for (let c = 0; c < ncol; c++) {
      const align = header ? 'center' : (c === 0 || wide.includes(c) ? 'left' : 'center');
      const shd = fill ? `<w:shd w:val="clear" w:color="auto" w:fill="${fill}"/>` : '';
      const txt = (r[c] || '').trim();
      const runs = header ? run(txt, { bold: true, color: 'FFFFFF' }) : mdRuns(txt);
      x += `<w:tc><w:tcPr><w:tcW w:w="${widths[c]}" w:type="dxa"/>${shd}</w:tcPr>`
        + para('THTableText', runs, `<w:jc w:val="${align}"/>`) + '</w:tc>';
    }
    x += '</w:tr>';
  });
  x += '</w:tbl>';
  body.push(x);
  nTables++;
}

lines.forEach((line, idx) => {
  let m;
  if (tableRows) {
    if ((m = line.match(/^\[TR\](.*)$/))) { tableRows.push(m[1].split(/\s*\|\s*/)); return; }
    if (line === '[/TABLE]') { flushTable(tableRows); tableRows = null; return; }
    if (line === '') return;
    throw new Error(`Unexpected line inside [TABLE] block: ${line}`);
  }
  if (line === '' || line.startsWith('#')) return;
  nParas++;

  if ((m = line.match(/^\[SECTION:(front|body)\]$/))) {
    body.push(`<w:p><w:pPr>${sectPr(current)}</w:pPr></w:p>`);
    current = m[1];
    return;
  }
  if (line === '[PAGEBREAK]') { body.push('<w:p><w:r><w:br w:type="page"/></w:r></w:p>'); return; }
  if ((m = line.match(/^\[BLANK(?::(\d+))?\]$/))) {
    const n = m[1] ? parseInt(m[1], 10) : 1;
    for (let k = 0; k < n; k++) body.push(para('THPlain', ''));
    return;
  }
  if ((m = line.match(/^\[(C|L|R)(?::(\d+))?(?::(b))?\](.*)$/))) {
    const jc = { C: 'center', L: 'left', R: 'right' }[m[1]];
    const size = m[2] ? parseInt(m[2], 10) * 2 : null;
    body.push(para('THPlain', mdRuns(m[4], { bold: !!m[3], size }), `<w:jc w:val="${jc}"/>`));
    return;
  }
  if ((m = line.match(/^\[FH\](.*)$/))) {
    const extra = idx === lastFrontIdx ? '<w:pageBreakBefore w:val="0"/><w:spacing w:before="480"/>' : '';
    body.push(para('THFrontHeading', run(m[1]), extra));
    return;
  }
  if ((m = line.match(/^\[(CH|APPX)\](.*)$/))) {
    const parts = m[2].split('|');
    let inner = run(parts[0].trim());
    if (parts.length > 1) inner += '<w:r><w:br/></w:r>' + run(parts.slice(1).join('|').trim());
    body.push(para('Heading1', inner));
    return;
  }
  if ((m = line.match(/^\[BACK\](.*)$/))) { body.push(para('Heading1', run(m[1]))); return; }
  if ((m = line.match(/^\[H2\](.*)$/))) { body.push(para('Heading2', mdRuns(m[1]))); return; }
  if ((m = line.match(/^\[H3\](.*)$/))) { body.push(para('Heading3', mdRuns(m[1]))); return; }
  if ((m = line.match(/^\[P\](.*)$/))) { body.push(para('THBody', mdRuns(m[1]))); return; }
  if ((m = line.match(/^\[PN\](.*)$/))) { body.push(para('THBodyNoIndent', mdRuns(m[1]))); return; }
  if ((m = line.match(/^\[LI(2|3)?\](.*)$/))) { body.push(para(`THList${m[1] || 1}`, mdRuns(m[2]))); return; }
  if ((m = line.match(/^\[KW\](.*)$/))) { body.push(para('THKeywords', labelled(m[1]))); return; }
  if ((m = line.match(/^\[TCAP\](.*)$/))) { body.push(para('THTableCaption', captionRuns(m[1], '\t'))); return; }
  if ((m = line.match(/^\[FCAP\](.*)$/))) { body.push(para('THFigureCaption', captionRuns(m[1], ' '))); return; }
  if ((m = line.match(/^\[TABLE(?::(apa|grid))?\]$/))) { tableRows = []; return; }
  if ((m = line.match(/^\[NOTE\](.*)$/))) { body.push(para('THNote', labelled(m[1]))); return; }
  if ((m = line.match(/^\[IMG\]([^|]+)(?:\|([\d.]+))?$/))) {
    let p = m[1].trim();
    if (!path.isAbsolute(p)) p = path.join(baseDir, p);
    if (!fs.existsSync(p)) {
      // The cover seal is downloaded separately and may be unavailable offline:
      // warn and continue rather than lose the whole report.
      console.error(`WARNING: image not found, skipped: ${p}`);
      return;
    }
    body.push(para('THFigure', imageXml(p, m[2] ? parseFloat(m[2]) : 14)));
    return;
  }
  if (line === '[TOC]') {
    body.push(tocField(`TOC \\o "1-${tocLevels}" \\h \\z \\t "TH Front Heading,1"`, tocEntries, (e) => `TOC${e.lvl}`));
    return;
  }
  if (line === '[LOT]') { body.push(tocField('TOC \\h \\z \\t "TH Table Caption,1"', lotEntries, () => 'TOC1')); return; }
  if (line === '[LOF]') { body.push(tocField('TOC \\h \\z \\t "TH Figure Caption,1"', lofEntries, () => 'TOC1')); return; }
  if ((m = line.match(/^\[REF\](.*)$/))) { body.push(para('THReference', mdRuns(m[1]))); return; }
  throw new Error(`Unknown tag on line ${idx + 1}: ${line}`);
});
if (tableRows) throw new Error('[TABLE] block not closed with [/TABLE]');
headerFor(current);

// ---------------------------------------------------------------- package parts
const NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
  + 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
  + 'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
  + 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
  + 'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"';
const XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n';

const documentXml = `${XML}<w:document ${NS}><w:body>${body.join('')}${sectPr(current)}</w:body></w:document>`;

const fonts = `<w:rFonts w:ascii="${FONT}" w:hAnsi="${FONT}" w:eastAsia="${FONT}" w:cs="${FONT}"/>`;
function style(id, name, { type = 'paragraph', basedOn = 'Normal', ppr = '', rpr = '', outline = null, extra = '' } = {}) {
  const ol = outline === null ? '' : `<w:outlineLvl w:val="${outline}"/>`;
  return `<w:style w:type="${type}"${id === 'Normal' ? ' w:default="1"' : ''} w:customStyle="${/^(Normal|Heading\d|TOC\d|TableGrid|Header)$/.test(id) ? 0 : 1}" w:styleId="${id}">`
    + `<w:name w:val="${name}"/>${basedOn ? `<w:basedOn w:val="${basedOn}"/>` : ''}${extra}<w:qFormat/>`
    + `<w:pPr>${ppr}${ol}</w:pPr><w:rPr>${fonts}<w:color w:val="000000"/>${rpr}</w:rPr></w:style>`;
}
const bold = '<w:b/><w:bCs/>';
const sz = (hp) => `<w:sz w:val="${hp}"/><w:szCs w:val="${hp}"/>`;
const ind = (left, opt = '') => `<w:ind w:left="${left}" ${opt}/>`;
const tocTab = `<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="${TEXT_W}"/></w:tabs>`;
const stylesXml = `${XML}<w:styles ${NS}>`
  + `<w:docDefaults><w:rPrDefault><w:rPr>${fonts}${sz(BODY_HP)}<w:lang w:val="en-US" w:eastAsia="en-US" w:bidi="th-TH"/></w:rPr></w:rPrDefault>`
  + `<w:pPrDefault><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>`
  + style('Normal', 'Normal', { basedOn: null, ppr: '<w:jc w:val="thaiDistribute"/>', rpr: sz(BODY_HP) })
  + style('Heading1', 'heading 1', { ppr: '<w:keepNext/><w:pageBreakBefore/><w:spacing w:before="0" w:after="360"/><w:ind w:left="0" w:firstLine="0"/><w:jc w:val="center"/>', rpr: bold + sz(HEAD_HP), outline: 0, extra: '<w:next w:val="THBody"/>' })
  + style('Heading2', 'heading 2', { ppr: '<w:keepNext/><w:spacing w:before="240" w:after="0"/><w:ind w:left="0" w:firstLine="0"/><w:jc w:val="left"/>', rpr: bold + sz(BODY_HP), outline: 1, extra: '<w:next w:val="THBody"/>' })
  + style('Heading3', 'heading 3', { ppr: '<w:keepNext/><w:spacing w:before="120" w:after="0"/><w:ind w:left="0" w:firstLine="0"/><w:jc w:val="left"/>', rpr: bold + sz(BODY_HP), outline: 2, extra: '<w:next w:val="THBody"/>' })
  + style('THFrontHeading', 'TH Front Heading', { ppr: '<w:keepNext/><w:pageBreakBefore/><w:spacing w:after="360"/><w:jc w:val="center"/>', rpr: bold + sz(HEAD_HP) })
  + style('THTableCaption', 'TH Table Caption', { ppr: `<w:keepNext/><w:spacing w:before="240" w:after="120"/><w:ind w:left="${2 * TW_CM}" w:hanging="${2 * TW_CM}"/><w:jc w:val="left"/>` })
  + style('THFigureCaption', 'TH Figure Caption', { ppr: '<w:spacing w:before="120" w:after="240"/><w:jc w:val="center"/>' })
  + style('THBody', 'TH Body', { ppr: `<w:ind w:firstLine="${TW_IN / 2}"/><w:jc w:val="thaiDistribute"/>` })
  + style('THBodyNoIndent', 'TH Body NoIndent', { ppr: '<w:jc w:val="thaiDistribute"/>' })
  + [1, 2, 3].map((l) => style(`THList${l}`, `TH List ${l}`, { ppr: ind(Math.round((0.5 * l + 0.3) * TW_IN), `w:hanging="${Math.round(0.3 * TW_IN)}"`) + '<w:jc w:val="thaiDistribute"/>' })).join('')
  + style('THKeywords', 'TH Keywords', { ppr: '<w:spacing w:before="240"/><w:jc w:val="thaiDistribute"/>' })
  + style('THReference', 'TH Reference', { ppr: `<w:spacing w:after="120"/>${ind(TW_IN / 2, `w:hanging="${TW_IN / 2}"`)}<w:jc w:val="left"/>` })
  + style('THNote', 'TH Note', { ppr: '<w:spacing w:before="60" w:after="120"/><w:jc w:val="left"/>', rpr: sz(BODY_HP - 4) })
  + style('THFigure', 'TH Figure', { ppr: '<w:keepNext/><w:jc w:val="center"/>' })
  + style('THPlain', 'TH Plain', { ppr: '<w:jc w:val="left"/>' })
  + style('THTableText', 'TH Table Text', { ppr: '<w:jc w:val="center"/>' })
  + [1, 2, 3].map((l) => style(`TOC${l}`, `toc ${l}`, { ppr: `${tocTab}<w:ind w:left="${Math.round([0, 0.4, 0.8][l - 1] * TW_IN)}"/><w:jc w:val="left"/>` })).join('')
  + style('Header', 'header', { ppr: '<w:jc w:val="right"/>' })
  + `<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders>`
  + ['top', 'left', 'bottom', 'right', 'insideH', 'insideV'].map((s) => `<w:${s} w:val="single" w:sz="4" w:space="0" w:color="000000"/>`).join('')
  + `</w:tblBorders></w:tblPr></w:style>`
  + `</w:styles>`;

const headerXml = `${XML}<w:hdr ${NS}><w:p><w:pPr><w:pStyle w:val="Header"/><w:jc w:val="right"/></w:pPr>`
  + `<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>`
  + `<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:hdr>`;

const settingsXml = `${XML}<w:settings ${NS}><w:updateFields w:val="true"/><w:defaultTabStop w:val="720"/>`
  + `<w:themeFontLang w:val="en-US" w:bidi="th-TH"/>`
  // applyBreakingRules = Word's Thai line-breaking rules. Without it Word breaks Thai
  // lines at the wrong places and thaiDistribute then stretches the letters apart.
  + `<w:compat><w:applyBreakingRules/>`
  + ['compatibilityMode:15', 'overrideTableStyleFontSizeAndJustification:1', 'enableOpenTypeFeatures:1', 'doNotFlipMirrorIndents:1', 'differentiateMultirowTableHeaders:1']
    .map((kv) => { const [k, v] = kv.split(':'); return `<w:compatSetting w:name="${k}" w:uri="http://schemas.microsoft.com/office/word" w:val="${v}"/>`; }).join('')
  + `</w:compat></w:settings>`;

const docRels = `${XML}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">`
  + `<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>`
  + `<Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>`
  + Object.values(headers).map((h) => `<Relationship Id="${h.rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="${h.name}"/>`).join('')
  + images.map((im) => `<Relationship Id="${im.rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/${im.name}"/>`).join('')
  + `</Relationships>`;

const contentTypes = `${XML}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">`
  + `<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>`
  + `<Default Extension="xml" ContentType="application/xml"/>`
  + `<Default Extension="png" ContentType="image/png"/><Default Extension="jpeg" ContentType="image/jpeg"/>`
  + `<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>`
  + `<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>`
  + `<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>`
  + Object.values(headers).map((h) => `<Override PartName="/word/${h.name}" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>`).join('')
  + `</Types>`;

const rootRels = `${XML}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">`
  + `<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>`;

const parts = [
  ['[Content_Types].xml', contentTypes],
  ['_rels/.rels', rootRels],
  ['word/document.xml', documentXml],
  ['word/styles.xml', stylesXml],
  ['word/settings.xml', settingsXml],
  ['word/_rels/document.xml.rels', docRels],
  ...Object.values(headers).map((h) => [`word/${h.name}`, headerXml]),
  ...images.map((im) => [`word/media/${im.name}`, im.data]),
];

// ---------------------------------------------------------------- minimal zip writer
const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
  return t;
})();
function crc32(buf) { let c = 0xffffffff; for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; }
function zip(entries) {
  const locals = [], centrals = [];
  let offset = 0;
  for (const [name, content] of entries) {
    const data = Buffer.isBuffer(content) ? content : Buffer.from(content, 'utf8');
    const comp = zlib.deflateRawSync(data);
    const nameBuf = Buffer.from(name, 'utf8');
    const crc = crc32(data);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0); local.writeUInt16LE(20, 4); local.writeUInt16LE(0x0800, 6); local.writeUInt16LE(8, 8);
    local.writeUInt32LE(0, 10); local.writeUInt32LE(crc, 14); local.writeUInt32LE(comp.length, 18); local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(nameBuf.length, 26); local.writeUInt16LE(0, 28);
    locals.push(local, nameBuf, comp);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0); central.writeUInt16LE(20, 4); central.writeUInt16LE(20, 6); central.writeUInt16LE(0x0800, 8); central.writeUInt16LE(8, 10);
    central.writeUInt32LE(0, 12); central.writeUInt32LE(crc, 16); central.writeUInt32LE(comp.length, 20); central.writeUInt32LE(data.length, 24);
    central.writeUInt16LE(nameBuf.length, 28); central.writeUInt32LE(offset, 42);
    centrals.push(central, nameBuf);
    offset += 30 + nameBuf.length + comp.length;
  }
  const cdSize = centrals.reduce((s, b) => s + b.length, 0);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0); end.writeUInt16LE(entries.length, 8); end.writeUInt16LE(entries.length, 10);
  end.writeUInt32LE(cdSize, 12); end.writeUInt32LE(offset, 16);
  return Buffer.concat([...locals, ...centrals, end]);
}

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, zip(parts));
console.log(`PARAGRAPHS=${nParas}`);
console.log(`TABLES=${nTables}`);
console.log(`IMAGES=${images.length}`);
console.log(`SAVED=${outputPath}`);
