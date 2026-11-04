# video-pipeline — ตัดต่อคลิปแนวตั้งสำหรับ TikTok แบบอัตโนมัติ

สคริปต์ที่ใช้ตัดคลิปพูดหน้ากล้องให้กระชับ ใส่ซับภาษาไทย กล่องฮุก อีโมจิเด้ง และเพลงคลอ

## สิ่งที่ต้องมี
- ffmpeg (มี libass สำหรับซับ)
- Python 3.12 + `pip install faster-whisper==1.1.1 requests av==12.3.0 pillow numpy`
- ฟอนต์อีโมจิ Noto Color Emoji (`/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf`)
- ฟอนต์ Kanit อยู่ใน `assets/fonts/` แล้ว (OFL)
- เครือข่ายที่เข้า `huggingface.co` ได้ ตอนโหลดโมเดลถอดเสียงครั้งแรก (~3 GB)

## ลำดับการใช้งาน
กำหนดโฟลเดอร์ทำงาน `WORK` ที่มี `source.mp4` แล้ว:

1. **เตรียมเสียง** (ลดเสียงรบกวน ปรับความดัง -16 LUFS)
   ```
   ffmpeg -i source.mp4 -vn -af "highpass=f=80,afftdn=nr=10:nf=-40,acompressor=threshold=-24dB:ratio=3:attack=10:release=200,loudnorm=I=-14:TP=-1.5:LRA=9" -ar 48000 voice_clean.wav
   ffmpeg -i source.mp4 -vn -ac 1 -ar 16000 asr16k.wav
   ```
2. **หาช่วงเงียบ**
   ```
   ffmpeg -i asr16k.wav -af silencedetect=noise=-42dB:d=0.25 -f null - 2>&1 | grep -oE "silence_(start|end): [0-9.]+" | awk '{print $2}' | paste - - > silences.txt
   ```
3. **ถอดเสียงภาษาไทย** (ราว 17 นาทีต่อคลิป 4:41 บน 4 CPU)
   `python transcribe.py asr16k.wav transcript_large.json Systran/faster-whisper-large-v3`
4. **ตรวจและแก้คำผิดในบทพูดด้วยตนเอง** แล้วแก้ `CORR`, `HL`, `EXCLUDE`, `STICK`, `hook`, `cards` ใน `build_plan.py` ให้ตรงกับคลิปใหม่ (ค่าที่มีอยู่เป็นของคลิปตัวอย่าง)
5. **สร้างเพลงคลอ** `python music.py music_bed.wav 285` (ความยาววินาที)
6. **สร้างแผน** `VIDEO_WORK=$WORK python build_plan.py plan.json` (ใส่ `--until 56` เพื่อทำตัวอย่างสั้น หรือ `--no-music` เพื่อไม่ใส่เพลง) แล้วสร้างไฟล์อีโมจิตามที่ระบุใน `plan.json` ด้วย `python sticker.py "😂" stickers/s00.mov 1.8 200`
7. **render** `python render.py plan.json out.mp4` ใช้เวลาประมาณ 15–20 นาทีต่อคลิปเต็ม ใช้ `--preview 30` เพื่อทดสอบสั้น ๆ

## ข้อควรรู้
- ผลถอดเสียงภาษาไทยของ Whisper มีคำผิดเสมอ โดยเฉพาะชื่อคนและศัพท์เฉพาะ ต้องตรวจก่อนทำซับ
- ช่วงที่พูดเร็วมากอาจถอดไม่ได้ ลอง `vad_filter=False` เฉพาะช่วงนั้น
- เพลงที่สร้างขึ้นเองเป็นเพลงบรรเลงง่าย ๆ ไม่ติดลิขสิทธิ์ แต่ต้องฟังเองก่อนใช้
- ต้องเปิดดูและฟังคลิปที่ได้ก่อนโพสต์ทุกครั้ง
