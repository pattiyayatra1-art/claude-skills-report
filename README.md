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
