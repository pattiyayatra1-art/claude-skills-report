# Thai Academic Skills สำหรับ Claude Code

สกิลสำหรับเขียนรายงานวิจัยและรายงานเชิงวิชาการภาษาไทยเป็นไฟล์ Word (.docx)

## สกิลในชุดนี้

| สกิล | หน้าที่ |
|---|---|
| `research-report-writer` (v2.1) | เขียนรายงานวิชาการ / รายงานวิจัย / บทที่ 1-5 เป็นภาษาไทย อ้างอิงแหล่งจริงที่ตรวจสอบแล้ว และสร้างไฟล์ตามรูปแบบต้นแบบที่ผู้ใช้ยืนยันแล้ว |

## รูปแบบรายงานต้นแบบ (v2.1)

สร้างด้วย Microsoft Word ได้หน้าตาแบบนี้:

- ปกมีตรามหาวิทยาลัย → คำนำ → บทคัดย่อ + คำสำคัญ → สารบัญ → สารบัญตาราง/ภาพ (เลขหน้า ก ข ค)
- เนื้อหาหัวข้อ 1. / 1.1 เลขหน้ามุมขวาบน
- ตารางหัวสีกรมท่า แถวสลับสีฟ้าอ่อน มีที่มาใต้ตาราง
- เอกสารอ้างอิงแยกภาษาไทย / ภาษาอังกฤษ

ต้องมี Windows + Microsoft Word + ฟอนต์ TH Sarabun New ถ้าไม่มี Word สกิลจะสร้างด้วย docx-js แทน (รูปแบบจะต่างไป)

## ติดตั้งบนเครื่องใหม่

ใน Claude Code พิมพ์:

```
/plugin marketplace add pattiyayatra1-art/claude-skills-report
/plugin install thai-academic-skills@pattiyayatra-skills
```

อัปเดตเป็นเวอร์ชันล่าสุด:

```
/plugin marketplace update pattiyayatra-skills
```

repo นี้เป็น private ต้องล็อกอิน GitHub ในเครื่องนั้นก่อน (เช่น `gh auth login`)

## สกิลที่ทำงานร่วมกัน

`research-report-writer` เรียกใช้สกิลเหล่านี้เมื่อจำเป็น (มากับบัญชี claude.ai):

- `docx` — สร้างไฟล์ Word เมื่อไม่มี Microsoft Word
- `pdf` — อ่านไฟล์ PDF งานวิจัยที่ผู้ใช้ให้มา
- `xlsx` — วิเคราะห์ข้อมูลแบบสอบถาม
- `dataviz` — ทำกราฟ
- `design:research-synthesis` — วิเคราะห์ข้อมูลสัมภาษณ์
- `design:user-research` — ออกแบบการวิจัย

## ปลั๊กอินตัดต่อวิดีโอ (ฟรี)

ปลั๊กอิน `video-editing` ติดตั้ง MCP [Kinocut](https://github.com/KyaniteLabs/kinocut) ซึ่งเป็นโอเพนซอร์ส (Apache-2.0) ทำงานบนเครื่องด้วย FFmpeg ไม่ต้องสมัครบัญชีหรือใช้ API key ใช้ตัด รวมคลิป ใส่ซับไตเติล และปรับเสียง/สี

ต้องมีในเครื่อง: [uv](https://docs.astral.sh/uv/) และ FFmpeg (รวม ffprobe)

```
/plugin marketplace update pattiyayatra-skills
/plugin install video-editing@pattiyayatra-skills
```

ตรวจความพร้อมด้วย `uvx kinocut==1.16.5 doctor` (เปิดครั้งแรกจะดาวน์โหลดแพ็กเกจจาก PyPI)

ใช้ได้ใน Claude Code และ Claude Desktop เท่านั้น เพราะเป็น MCP ที่รันบนเครื่อง จึงใช้ในหน้าเว็บ claude.ai ไม่ได้

### ใช้ในเซสชันคลาวด์ (claude.ai/code)

ไฟล์ `.mcp.json` ที่ root ของ repo ประกาศ Kinocut เป็น MCP ของโปรเจกต์ เซสชันใหม่ที่เปิด repo นี้จะเห็น `kinocut` ใน `/mcp` และต้องกดอนุมัติเซิร์ฟเวอร์ครั้งแรก

ให้ติดตั้งล่วงหน้าใน setup script ของ environment (เมนู environment บนแถบชื่อเซสชัน → Edit) เพื่อไม่ให้เปิดช้าหรือ timeout:

```bash
uvx kinocut==1.16.5 --version
```

หมายเหตุ: ปลั๊กอิน `thai-academic-skills` ใช้ root ของ repo เป็นโฟลเดอร์ปลั๊กอิน จึงโหลด `.mcp.json` นี้ไปด้วย ผู้ที่ติดตั้งปลั๊กอินนั้นจะได้ Kinocut มาด้วย

## โครงสร้าง

```
.claude-plugin/
  plugin.json
  marketplace.json
skills/research-report-writer/
  SKILL.md
  references/
    user-academic-writing-style.md  สำนวนและการจัดเรียงตามรายงานต้นแบบของผู้ใช้
    model-build-pipeline.md         ขั้นตอนสร้างไฟล์ตามต้นแบบด้วย Word
    word-tag-format.md              แท็กที่สคริปต์ build ใช้
    thai-academic-format.md         รูปแบบหน้า ฟอนต์ หัวข้อ ตาม ม.ไทย
    citation-styles.md              APA 7 / IEEE / Vancouver + กฎผู้แต่งไทย
    methods-and-data.md             แปลงข้อมูลเป็นบทวิธีวิจัยและผลการวิจัย
    qa-checklist.md                 รายการตรวจก่อนส่งมอบ
  scripts/
    build_research_docx.ps1         สร้าง .docx ผ่าน Word (ปก, ก ข ค, สารบัญอัตโนมัติ)
    modelfmt.ps1                    จัดตาราง/คำบรรยาย/สารบัญตามต้นแบบ + ส่งออก PDF
  assets/
    template_model.txt              แม่แบบแท็กของรายงานต้นแบบ
  examples/
    digital_economy_report_tagged.txt  ตัวอย่างรายงานจริงที่ผ่านการยืนยัน
    fig_boxes_example.py               ตัวอย่างภาพแผนภาพกล่อง
```
