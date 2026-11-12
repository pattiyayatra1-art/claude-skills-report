const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, HeadingLevel, ShadingType, BorderStyle, Header, PageNumber,
  VerticalAlign, TableLayoutType,
} = require("docx");
const Q = require("./questions");

const FONT = "TH SarabunPSK";
const NAVY = "1F3864";
const LIGHT = "EAF0F8";
const ANS_BG = "F2F6FB";
const TABLE_W = 11906 - 1701 - 1418; // A4 minus margins (3 cm left, 2.5 cm right)
const LETTERS = ["ก", "ข", "ค", "ง"];

const members = [
  ["นายทินภัทร ต้นวาตะ", "076750306019-0"],
  ["นายภัททิยะ ยาตรา", "076750306033-1"],
  ["นายกิชติธเนศ ต่วนกล่ำ", "076750306045-5"],
  ["นายปองภพ สองห้องนอก", "076750306056-2"],
  ["นายกฤตนัย เพ็ญไพรัตน์กุล", "076750306016-6"],
];
const subtopics = [
  ["6.1", "แนวความคิดเกี่ยวกับ Tokenization, Open Banking และ Fintech"],
  ["6.2", "การใช้นวัตกรรมทางการเงินในการลงทุน เช่น High-Frequency Trading (HFT) และ Generative AI"],
  ["6.3", "กระบวนการจัดการสินเชื่อโดยใช้นวัตกรรม ได้แก่ P2P Lending"],
  ["6.4", "นวัตกรรมพร้อมเพย์ (PromptPay) กับระบบการชำระเงิน"],
  ["6.5", "การวิเคราะห์การลงทุนแบบยั่งยืน (ESG Investing)"],
];
const parts = [
  { key: "basic", title: "ตอนที่ 1 ระดับพื้นฐาน", short: "พื้นฐาน" },
  { key: "analysis", title: "ตอนที่ 2 ระดับวิเคราะห์", short: "วิเคราะห์" },
  { key: "apply", title: "ตอนที่ 3 ระดับการประยุกต์ใช้", short: "ประยุกต์ใช้" },
];

// ── sanity checks against the brief ──
const want = { basic: 10, analysis: 10, apply: 5 };
for (const k of Object.keys(want)) {
  const n = Q.filter((q) => q.level === k).length;
  if (n !== want[k]) throw new Error(`${k}: ${n} != ${want[k]}`);
}
Q.forEach((q, i) => {
  if (q.opts.length !== 4) throw new Error(`ข้อ ${i + 1} ตัวเลือกไม่ครบ 4`);
  if (!(q.ans >= 0 && q.ans < 4) || !q.exp) throw new Error(`ข้อ ${i + 1} เฉลย/คำอธิบาย`);
});
Q.forEach((q, i) => (q.no = i + 1));

// ── helpers ──
const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 32, bold: o.bold, color: o.color, italics: o.italics });
const para = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [run(children, o)], ...o.p });
const center = (text, size, bold, after = 0) =>
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after }, children: [run(text, { size, bold })] });
const range = (nums) => {
  if (!nums.length) return "-";
  const out = []; let s = nums[0], p = nums[0];
  for (const n of nums.slice(1).concat([null])) {
    if (n === p + 1) { p = n; continue; }
    out.push(s === p ? `${s}` : `${s}–${p}`); s = p = n;
  }
  return out.join(", ");
};
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: none, bottom: none, left: none, right: none };
const thin = { style: BorderStyle.SINGLE, size: 4, color: "8EA9C8" };
const grid = { top: thin, bottom: thin, left: thin, right: thin };

function cell(text, w, o = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    borders: o.borders || grid,
    verticalAlign: VerticalAlign.CENTER,
    shading: o.fill ? { type: ShadingType.CLEAR, color: "auto", fill: o.fill } : undefined,
    margins: { top: 40, bottom: 40, left: 100, right: 100 },
    children: [new Paragraph({
      keepNext: !!o.keepNext,
      alignment: o.align || AlignmentType.CENTER,
      children: [run(text, { size: o.size || 30, bold: o.bold, color: o.color })],
    })],
  });
}
function table(widths, header, rows, o = {}) {
  const hdr = new TableRow({
    tableHeader: true, cantSplit: true,
    children: header.map((h, i) => cell(h, widths[i], { fill: NAVY, color: "FFFFFF", bold: true, keepNext: true })),
  });
  const body = rows.map((r, ri) => new TableRow({
    cantSplit: true,
    children: r.map((c, i) => cell(c, widths[i], {
      fill: (o.boldLast && ri === rows.length - 1) ? "D9E2F0" : (ri % 2 ? LIGHT : undefined),
      align: (o.leftCols || []).includes(i) ? AlignmentType.LEFT : AlignmentType.CENTER,
      bold: o.boldLast && ri === rows.length - 1,
      keepNext: o.keepTogether && ri < rows.length - 1,
    })),
  }));
  return new Table({ width: { size: TABLE_W, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows: [hdr, ...body] });
}
const caption = (label, text) => new Paragraph({
  spacing: { before: 200, after: 80 }, keepNext: true,
  children: [run(label + " ", { bold: true }), run(text)],
});

// ── cover ──
const cover = [
  new Paragraph({ spacing: { before: 1400 }, children: [] }),
  center("ข้อสอบปรนัย", 40, true, 120),
  center("หัวข้อที่ 6", 36, true, 120),
  center("นวัตกรรมทางการเงินและการลงทุน", 40, true, 60),
  center("(Innovation for Finance and Investment)", 36, true, 600),
  center("จำนวน 25 ข้อ", 32, true, 60),
  center("ระดับพื้นฐาน 10 ข้อ  ระดับวิเคราะห์ 10 ข้อ  ระดับการประยุกต์ใช้ 5 ข้อ", 32, false, 1200),
  center("จัดทำโดย", 36, true, 200),
  new Table({
    width: { size: 8787, type: WidthType.DXA }, columnWidths: [3700, 1900, 3187], alignment: AlignmentType.CENTER,
    layout: TableLayoutType.FIXED,
    borders: { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none },
    rows: members.map(([n, id]) => new TableRow({ children: [
      cell(n, 3700, { borders: noBorders, align: AlignmentType.LEFT, size: 32 }),
      cell("รหัสนักศึกษา", 1900, { borders: noBorders, align: AlignmentType.LEFT, size: 32 }),
      cell(id, 3187, { borders: noBorders, align: AlignmentType.LEFT, size: 32 }),
    ] })),
  }),
];

// ── instructions + blueprint ──
const intro = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [run("คำชี้แจง", { size: 40, bold: true })] }),
  para([run("1. ข้อสอบชุดนี้เป็นข้อสอบปรนัยแบบเลือกตอบ 4 ตัวเลือก จำนวน 25 ข้อ ครอบคลุมหัวข้อที่ 6 นวัตกรรมทางการเงินและการลงทุน (Innovation for Finance and Investment)")], { p: { indent: { left: 360, hanging: 360 }, spacing: { after: 60 } } }),
  para([run("2. แบ่งตามระดับความยาก 3 ตอน ได้แก่ ระดับพื้นฐาน 10 ข้อ (ข้อ 1–10) ระดับวิเคราะห์ 10 ข้อ (ข้อ 11–20) และระดับการประยุกต์ใช้ 5 ข้อ (ข้อ 21–25)")], { p: { indent: { left: 360, hanging: 360 }, spacing: { after: 60 } } }),
  para([run("3. ทุกข้อมีคำถาม ตัวเลือก ก ข ค ง เฉลย และคำอธิบายคำตอบ พร้อมตารางสรุปเฉลยท้ายเล่ม")], { p: { indent: { left: 360, hanging: 360 }, spacing: { after: 200 } } }),
  new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run("ขอบเขตเนื้อหา", { size: 36, bold: true })] }),
  ...subtopics.map(([n, t]) => para([run(`${n}  `, { bold: true }), run(t)], { p: { indent: { left: 720, hanging: 540 }, spacing: { after: 40 } } })),
  caption("ตารางที่ 1", "การกระจายข้อสอบตามหัวข้อย่อยและระดับความยาก (ตัวเลขในวงเล็บคือเลขข้อ)"),
  (() => {
    const w = [1500, 2000, 2000, 2000, 1287];
    const rows = subtopics.map(([s]) => {
      const cells = parts.map((p) => {
        const nums = Q.filter((q) => q.sub === s && q.level === p.key).map((q) => q.no);
        return nums.length ? `${nums.length} (${range(nums)})` : "-";
      });
      return [`หัวข้อ ${s}`, ...cells, `${Q.filter((q) => q.sub === s).length}`];
    });
    rows.push(["รวม", ...parts.map((p) => `${Q.filter((q) => q.level === p.key).length}`), `${Q.length}`]);
    return table(w, ["หัวข้อย่อย", "พื้นฐาน", "วิเคราะห์", "ประยุกต์ใช้", "รวม"], rows, { boldLast: true, keepTogether: true });
  })(),
];

// ── questions ──
function questionBlock(q) {
  const keep = { keepNext: true, keepLines: true };
  const out = [];
  out.push(new Paragraph({
    ...keep, spacing: { before: 280, after: 80 }, indent: { left: 567, hanging: 567 },
    children: [run(`${q.no}.`, { bold: true }), run("\t"), run(q.q, { bold: true })],
    tabStops: [{ type: "left", position: 567 }],
  }));
  out.push(new Paragraph({ ...keep, spacing: { after: 60 }, indent: { left: 567 }, children: [run(`[หัวข้อ ${q.sub} ${q.tag}]`, { size: 26, color: "6B7A90", italics: true })] }));
  q.opts.forEach((o, i) => out.push(new Paragraph({
    ...keep, indent: { left: 1134, hanging: 567 }, spacing: { after: 20 },
    tabStops: [{ type: "left", position: 1134 }],
    children: [run(`${LETTERS[i]}.`), run("\t"), run(o)],
  })));
  const box = { style: BorderStyle.SINGLE, size: 6, color: "B4C6E0", space: 4 };
  const shade = { type: ShadingType.CLEAR, color: "auto", fill: ANS_BG };
  out.push(new Paragraph({
    ...keep, spacing: { before: 100 }, indent: { left: 567, right: 113 }, shading: shade,
    border: { top: box, left: box, right: box },
    children: [run("เฉลย ", { bold: true, color: NAVY }), run(`${LETTERS[q.ans]}.`, { bold: true, color: NAVY })],
  }));
  out.push(new Paragraph({
    keepLines: true, spacing: { after: 120 }, indent: { left: 567, right: 113 }, shading: shade,
    alignment: AlignmentType.THAI_DISTRIBUTE,
    border: { bottom: box, left: box, right: box },
    children: [run("คำอธิบาย: ", { bold: true }), run(q.exp)],
  }));
  return out;
}
const body = [];
for (const p of parts) {
  const qs = Q.filter((q) => q.level === p.key);
  body.push(new Paragraph({
    heading: HeadingLevel.HEADING_1, pageBreakBefore: true,
    children: [run(`${p.title} (ข้อ ${qs[0].no}–${qs[qs.length - 1].no} จำนวน ${qs.length} ข้อ)`, { size: 40, bold: true })],
  }));
  qs.forEach((q) => body.push(...questionBlock(q)));
}

// ── answer key ──
const key = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [run("สรุปเฉลยข้อสอบ", { size: 40, bold: true })] }),
  caption("ตารางที่ 2", "เฉลยข้อสอบทั้ง 25 ข้อ จำแนกตามระดับความยากและหัวข้อย่อย"),
  table([1100, 1500, 1000, 5187],
    ["ข้อ", "ระดับ", "เฉลย", "หัวข้อย่อย"],
    Q.map((q) => [`${q.no}`, parts.find((p) => p.key === q.level).short, LETTERS[q.ans], `${q.sub} ${q.tag}`]),
    { leftCols: [3] }),
  (() => {
    const c = LETTERS.map((l, i) => `${l} ${Q.filter((q) => q.ans === i).length} ข้อ`).join("  ");
    return new Paragraph({ spacing: { before: 120 }, children: [run("หมายเหตุ: ", { bold: true, size: 28 }), run(`จำนวนข้อที่เฉลยแต่ละตัวเลือก ${c}`, { size: 28 })] });
  })(),
];

const doc = new Document({
  creator: "กลุ่มผู้จัดทำ",
  title: "ข้อสอบหัวข้อที่ 6 นวัตกรรมทางการเงินและการลงทุน",
  styles: {
    default: { document: { run: { font: { ascii: FONT, hAnsi: FONT, cs: FONT, eastAsia: FONT }, size: 32, sizeComplexScript: 32 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 40, bold: true, color: "000000" },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 240 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 36, bold: true, color: "000000" },
        paragraph: { spacing: { before: 120, after: 80 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: {
      titlePage: true,
      page: { margin: { top: 1418, bottom: 1418, left: 1701, right: 1418, header: 708 } },
    },
    headers: {
      first: new Header({ children: [new Paragraph({ children: [] })] }),
      default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 32 })] })] }),
    },
    children: [...cover, ...intro, ...body, ...key],
  }],
});

const out = path.join(__dirname, "ข้อสอบ_หัวข้อที่6_นวัตกรรมทางการเงินและการลงทุน.docx");
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(out, b); console.log("wrote", out); });
