---
name: "stock-analysis-deck-th"
description: "Build a Thai stock-analysis presentation (งบ 5 ปี, ROE/DuPont, หนี้, เงินสด, เทียบคู่แข่ง, มูลค่า, AI Audit) as Claude Slides + web HTML + PPTX + speaker-script PDF, from verified financial statements. Example: SPALI."
---

# Stock Analysis Deck (ไทย) · v1.0

ทำชุดนำเสนอวิเคราะห์หุ้นรายตัวหน้าห้อง จากงบการเงินที่ตรวจแล้ว 5 ปี ตัวอย่างต้นแบบคือ SPALI (17 สไลด์ ~10–16 นาที)
สร้างได้ 4 ผลลัพธ์: Slides ใน Claude (Artifact) · เว็บ HTML ส่งลิงก์ · PPTX (ภาพทั้งหน้า) · PDF บทพูด

## ใช้เมื่อ
ผู้ใช้ขอ "วิเคราะห์หุ้น X ทำสไลด์ / storyboard / บทพูด" ตามโจทย์ Workshop (Dashboard · Health 5 ด้าน · AI Audit · Margin of Safety · 3 คำถาม)

## ลำดับงาน
1. **ถามก่อน (ถามครั้งเดียว):** ชื่อหุ้น · ผู้นำเสนอ/อาจารย์/วิชา · ผู้ฟังรู้การเงินหรือไม่ · เวลา (10/16 นาที) · มีภาพบริษัทไหม
2. **ดึงข้อมูล 5 ปี** (อ่าน `references/data-and-verification.md` ก่อน) แล้วกระทบยอด A = L + E ทุกปี
3. **ร่าง storyboard** ตาม `references/example-storyboard-spali.md` แล้วให้ผู้ใช้ยืนยันก่อนสร้างสไลด์
4. **สร้างสไลด์:** ตั้งโฟลเดอร์งาน (ดู "โครงโฟลเดอร์") แก้ตัวเลขใน `scripts/gen4.py` → รัน `gen4.py` → `post.py`
5. **พรีวิวตรวจล้น:** `node scripts/pvx.js <work>/deck <out>` ดูภาพทุกหน้า (ต้องไม่มี BAD ยกเว้นรูปเต็มหน้า)
6. **เผยแพร่ Artifact** (ชนิด Slides) ด้วย `root` = `<work>/deck` แล้วส่งไฟล์ `project/deck.css`, `project/slides/*.html`
7. **ส่งออกอื่น (เมื่อขอ):** เว็บ `mkweb.py` · PPTX `mkpptx.js` · PDF บทพูด `outline2.py` + `mk.js`
8. **ตรวจท้ายก่อนส่ง:** เลขหน้า, ที่มาทุกสไลด์, ตัวเลขตรงกับ storyboard, บทพูดตรงสไลด์, "AI กล่าวว่า…" ต้องมาจากคำตอบ AI จริงที่ผู้ใช้ทดสอบ

## โครงโฟลเดอร์งาน (`DECK_WORK`, ค่าเริ่มต้น = โฟลเดอร์ปัจจุบัน)
```
deck/project/{deck.json, deck.css, slides/}   ← เริ่มจาก templates/
assets/            รูปภาพ (ชื่อไฟล์ตรงกับ map ใน pvx.js / mkweb.py)
pv/                pvx.js, icons.css (รัน mkicons.js), icons.woff2 ไม่จำเป็นแล้ว
jpg/               ภาพสไลด์ 16:9 สำหรับ PPTX / PDF (ได้จาก pvx.js, DSF=2)
```
ตัวแปร: `DECK_WORK` (โฟลเดอร์งาน), `OUT_DIR` (ที่เก็บผลลัพธ์), `ASSETS` (โฟลเดอร์รูป สำหรับ pvx.js)
`mkicons.js`/`mkpptx.js` ต้องมี `react react-dom react-icons pptxgenjs` (ติดตั้งในโฟลเดอร์ชั่วคราวนอก repo)

## สคริปต์ (`scripts/`)
| ไฟล์ | หน้าที่ |
|---|---|
| `gen4.py` | สร้าง HTML ของสไลด์ 2–16 (ยกเว้นปก/ขอบคุณ) · **ข้อมูลหุ้นอยู่ในไฟล์นี้** (ตัวแปร rev, npf, ROE, inv, ibd, PEERS, ข้อความ, หมายเหตุ) |
| `post.py` | ใส่แถบช่วง (tracker), กดทีละส่วน (fragment), เลขหน้า, **บทพูด `SCRIPT`**, ลำดับ `order`, สร้าง deck.json และ Speaker_Script.md |
| `pvx.js` | พรีวิว Playwright (ปิด JS) + รายงานล้น/เกินขีดจำกัด · `DSF=2` สำหรับภาพคมชัด |
| `mkicons.js` | สร้าง `icons.css` (ไอคอน SVG mask ใช้แทนฟอนต์ไอคอนของระบบ ซึ่งดึงออกมาไม่ได้) |
| `mkweb.py` | รวมสไลด์เป็นเว็บ HTML เดียว มีแอนิเมชัน กดทีละส่วน ปัดมือถือ ปุ่ม F/N |
| `mkpptx.js` | PPTX = ภาพทั้งหน้า + บทพูดใน Notes (แก้ข้อความไม่ได้) |
| `outline.py`, `outline2.py`, `mk.js` | PDF หัวข้อ + บทพูดสั้น (10 นาที) · `mk.js` = HTML→PDF (ฟอนต์ Kanit/Anuphan จาก Google Fonts) |
| `templates/` | deck.css, deck.json, cover.html, thanks.html (ปก/ขอบคุณเขียนมือ ต้องแก้ชื่อ รูป ข้อมูล) |

## สร้างหุ้นตัวใหม่ — ต้องแก้อะไร
1. `gen4.py`: ตัวเลขทุกชุด, ข้อความหัวเรื่อง/ข้อสรุป, ค่า PEERS, ลำดับอันดับ (rank) ในสไลด์เทียบคู่แข่ง, ฉลาก 2021–2025
2. `post.py`: `SCRIPT` (บทพูด), ชื่อผู้พูด P1/P2, เวลา, `SEC`
3. `templates/cover.html`, `thanks.html`: ชื่อบริษัท ผู้จัดทำ อาจารย์ รูป
4. `outline.py`/`outline2.py`: ข้อความ S และ T ใน PDF บทพูด 10 นาที
5. blob id ของรูป (ใน `pvx.js`, `mkweb.py`) ให้ตรงกับรูปที่อัปโหลดเข้า Artifact ใหม่

## ข้อจำกัดของ Artifact ชนิด Slides (ผ่านมาแล้ว ห้ามพลาดซ้ำ)
- ไม่ใช้: `conic-gradient`, `background-size/position`, `::after`, `z-index`, `clip-path`, `transform:scale()` นอก keyframes → กราฟวงกลมใช้ `<svg>` (stroke-dasharray)
- `position:absolute` ไม่เกิน 24 ต่อ `<div>` · ไม่เกิน 200 กล่องต่อสไลด์ · ฟอนต์ ≥ 24px · ตารางไม่เกินความกว้าง
- ไอคอนใช้ `<x-icon name>` เฉพาะชื่อที่ระบบรองรับ · ลูกศรใช้ `<x-shape kind="arrow-right">` (วางใน `<div>` ถ้าต้องขยับ)
- ลำดับ publish: ต้องอ่านไฟล์ที่ผู้ใช้แก้ในตัวแก้ไขก่อน ไม่งั้นถูกปฏิเสธ → อ่าน, ผสาน, publish ใหม่
- ตัวพรีวิวในเครื่อง "แสดงส่วนที่ต้องกดไว้ครบ" และไม่เล่นแอนิเมชัน ให้บอกผู้ใช้ว่าต้องเปิดดูจริง

## กฎคุณภาพ
- ตัวเลขทุกตัวมีที่มา · ไม่แต่ง · ข้อมูลไม่มีให้เขียน "ไม่มีข้อมูล"
- ROE ใช้ส่วนทุนของบริษัทใหญ่ (ไม่รวม NCI) ให้ตรงกับกำไรส่วนบริษัทใหญ่ · D/E ใช้ส่วนทุนรวม
- แยก ข้อเท็จจริง / ความเห็น · ราคาเป้าโบรกเกอร์เป็นความเห็นรอง · ไม่ใช่คำแนะนำซื้อขาย
- ห้ามสร้าง PR / push นอก branch ที่ระบบกำหนด · ภาพบริษัทใช้เพื่อการศึกษาและระบุเครดิต

รายละเอียดข้อมูลและบทเรียน: `references/data-and-verification.md`
