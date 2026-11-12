# Thai Academic Skills สำหรับ Claude Code

สกิลสำหรับเขียนรายงานวิจัยและรายงานเชิงวิชาการภาษาไทยเป็นไฟล์ Word (.docx)

## สกิลในชุดนี้

| สกิล | หน้าที่ |
|---|---|
| `research-report-writer` (v2.2) | เขียนรายงานวิชาการ / รายงานวิจัย / บทที่ 1-5 เป็นภาษาไทย อ้างอิงแหล่งจริงที่ตรวจสอบแล้ว และสร้างไฟล์ตามรูปแบบต้นแบบที่ผู้ใช้ยืนยันแล้ว |

## รูปแบบรายงานต้นแบบ (v2.1)

สร้างด้วย Microsoft Word ได้หน้าตาแบบนี้:

- ปกมีตรามหาวิทยาลัย → คำนำ → บทคัดย่อ + คำสำคัญ → สารบัญ → สารบัญตาราง/ภาพ (เลขหน้า ก ข ค)
- เนื้อหาหัวข้อ 1. / 1.1 เลขหน้ามุมขวาบน
- ตารางหัวสีกรมท่า แถวสลับสีฟ้าอ่อน มีที่มาใต้ตาราง
- เอกสารอ้างอิงแยกภาษาไทย / ภาษาอังกฤษ

ต้องมี Windows + Microsoft Word + ฟอนต์ TH Sarabun New ถ้าไม่มี Word สกิลจะสร้างด้วย Node.js (`build_research_docx.js`) ให้ได้รูปแบบเดียวกัน แล้วเติมเลขหน้าสารบัญด้วย `fill_toc_pages.py`

## มีอะไรใหม่ใน v2.2

- **ถามข้อมูลก่อนเริ่มงาน:** ก่อนค้นคว้า สกิลจะถามข้อมูลหน้าปกที่ยังไม่รู้ในครั้งเดียว ได้แก่ ชื่อ รหัส รายวิชา อาจารย์ ภาคเรียน ปีการศึกษา สาขา และไฟล์ตรามหาวิทยาลัย ไม่เดาและไม่ปล่อยช่องจุดไว้บนปก
- **เลขหน้าสารบัญครบ:** สคริปต์ `fill_toc_pages.py` เติมเลขหน้าในสารบัญ สารบัญตาราง และสารบัญภาพ โดยคำนวณจากฟอนต์ TH Sarabun New ตัวจริง (ติดตั้งจาก npm `@apw-pdf/fonts`)
- **สำนวนไม่แข็ง:** เพิ่มกติกา 7 ข้อ ตัวอย่างก่อน–หลัง และตัวชี้วัดที่นับได้ ใน `references/user-academic-writing-style.md`
- **ตาราง:** เพิ่มคำอธิบายการคำนวณความกว้างคอลัมน์ และวิธีเลี่ยงคอลัมน์แคบจนตัดคำ

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

| ปลั๊กอิน | มาจาก | ได้อะไร |
|---|---|---|
| `kinocut@pattiyayatra-skills` | [Kinocut](https://github.com/KyaniteLabs/kinocut) (Apache-2.0) ปลั๊กอินทางการ | MCP ตัดต่อด้วย FFmpeg (ตัด รวม ใส่ข้อความ/ซับ เปลี่ยนขนาด ปรับเสียง ตรวจคุณภาพ ทำคลิปสั้น) + สกิล `kinocut`, `kinocut-repurpose` |
| `hyperframes@hyperframes` | [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache-2.0) marketplace ทางการของ HeyGen | สกิลสร้างวิดีโอจาก HTML/CSS/แอนิเมชัน แล้ว render เป็น MP4 (motion graphics, caption, overlay, transition) |

ไม่ต้องสมัครบัญชีหรือใช้ API key

ต้องมีในเครื่อง: [uv](https://docs.astral.sh/uv/), FFmpeg (รวม ffprobe) และ Node.js 22+ (สำหรับ HyperFrames)

### เปิดโปรเจกต์นี้ใน Claude Code

`.claude/settings.json` ประกาศทั้งสองปลั๊กอินไว้แล้ว เปิดโฟลเดอร์นี้ใน Claude Code (Desktop หรือ terminal) แล้วยอมรับการติดตั้งที่ขึ้นมา

### ติดตั้งให้ใช้ได้ทุกโปรเจกต์ (ในเครื่อง)

ใน terminal:

```
claude plugin marketplace add pattiyayatra1-art/claude-skills-report
claude plugin install kinocut@pattiyayatra-skills
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

ตรวจความพร้อม: `uvx kinocut==1.16.5 doctor` (ครั้งแรกจะดาวน์โหลดแพ็กเกจจาก PyPI)

### เซสชันคลาวด์ (claude.ai/code)

ใส่บรรทัดนี้ใน setup script ของ environment (เมนู environment บนแถบชื่อเซสชัน → Edit) เพื่อโหลด Kinocut ไว้ก่อน ไม่ให้เปิดช้าจน timeout:

```bash
uvx kinocut==1.16.5 --version
```

## โครงสร้าง

```
.claude-plugin/
  plugin.json
  marketplace.json      thai-academic-skills + kinocut (ดึงจาก repo ของ Kinocut)
.claude/settings.json   เปิดใช้ kinocut และ hyperframes เมื่อเปิดโปรเจกต์นี้
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
