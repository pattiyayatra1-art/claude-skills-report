# Thai Academic Skills สำหรับ Claude Code

สกิลสำหรับเขียนรายงานวิจัยเชิงวิชาการภาษาไทยเป็นไฟล์ Word (.docx)

## สกิลในชุดนี้

| สกิล | หน้าที่ |
|---|---|
| `research-report-writer` (v2) | เขียนรายงานวิจัย / บทที่ 1-5 ของวิทยานิพนธ์ เป็นภาษาไทย อ้างอิงแหล่งจริงที่ตรวจสอบแล้ว |

## ติดตั้งบนเครื่องใหม่

ใน Claude Code พิมพ์:

```
/plugin marketplace add pattiyayatra1-art/claude-skills-report
/plugin install thai-academic-skills@pattiyayatra-skills
```

ถ้าเป็น repo แบบ private ต้องล็อกอิน GitHub ในเครื่องนั้นก่อน (เช่น `gh auth login`)

## สกิลที่ทำงานร่วมกัน

`research-report-writer` เรียกใช้สกิลเหล่านี้เมื่อจำเป็น ต้องมีติดตั้งอยู่ในเครื่อง (มากับบัญชี claude.ai):

- `docx` — สร้างไฟล์ Word (จำเป็นเสมอ)
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
    thai-academic-format.md   รูปแบบหน้า ฟอนต์ หัวข้อ ตาม ม.ไทย
    citation-styles.md        APA 7 / IEEE / Vancouver + กฎผู้แต่งไทย
    methods-and-data.md       แปลงข้อมูลเป็นบทวิธีวิจัยและผลการวิจัย
    qa-checklist.md           รายการตรวจก่อนส่งมอบ
```
