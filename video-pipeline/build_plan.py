"""Build plan.json for render.py from transcript + silences + manual corrections.
Usage: VIDEO_WORK=/path/to/workdir python build_plan.py out_plan.json [--until SRC_SECONDS] [--no-music]
NOTE: CORR, HL, EXCLUDE, STICK, hook and cards below are specific to the example video; edit them for a new clip.
"""
import json, sys, os

# Working directory holding source.mp4, voice_clean.wav, silences.txt, transcript_large.json, music_bed.wav
WORK = os.environ.get("VIDEO_WORK", os.getcwd())
V = G = A = WORK
out = sys.argv[1]
until = float(sys.argv[sys.argv.index("--until") + 1]) if "--until" in sys.argv else 1e9
segs = json.load(open(f"{A}/transcript_large.json"))
dur = 281.02

# Corrected subtitle text per transcript segment. "|" = forced chunk break. None = drop.
CORR = {
    0: "สวัสดีคณะกรรมการ|ทุกท่านครับ",
    1: "ผมนายภัททิยะ ยาตรา",
    2: "ตัวแทนทีม|Solar Finance Marketplace",
    3: "จากมหาวิทยาลัยเทคโนโลยี|ราชมงคลพระนคร",
    8: "ปัจจุบันผู้ประกอบการ SME|ต้องการลดต้นทุนค่าไฟฟ้า",
    9: "และติดตั้งโซลาร์เซลล์",
    10: "แต่ยังมีข้อจำกัดสำคัญ",
    11: "เงินทุนเริ่มต้นที่สูง",
    12: "การคำนวณผลตอบแทนที่ซับซ้อน",
    13: "และขาดข้อมูล|เปรียบเทียบแหล่งเงินทุน",
    14: "ทำให้ตัดสินใจลงทุนได้ยาก",
    15: "ทีมเราจึงเสนอ|Solar Finance Marketplace",
    16: "ต้นแบบแพลตฟอร์ม|ที่รวมการวิเคราะห์ต้นทุน|ผลตอบแทน ทางเลือกเงินทุน",
    17: "และความเสี่ยงไว้ในระบบเดียว",
    18: "จุดเด่นคือเชื่อมการวิเคราะห์|ทางการเงิน|เข้ากับการลงทุนพลังงานสะอาด",
    19: "ช่วยให้ SME ตัดสินใจ|จากข้อมูลที่ตรวจสอบได้",
    20: "แพลตฟอร์มทำงาน|ทั้งหมด 4 ขั้นตอน",
    21: "1. กรอกข้อมูลค่าไฟฟ้า|และต้นทุนติดตั้ง",
    22: "2. คำนวณ NPV, IRR|และระยะเวลาคืนทุน",
    23: "3. เปรียบเทียบแหล่งเงินทุน|และวิเคราะห์ความเสี่ยง",
    24: "4. แสดงผลผ่าน Dashboard|เพื่อประกอบการตัดสินใจ",
    25: "ตัวอย่างความคุ้มค่า|ลงทุนโซลาร์ 250,000 บาท",
    26: "ประหยัดค่าไฟปีละ 40,000 บาท|ค่าบำรุงรักษาปีละ 6,000 บาท",
    27: "กระแสเงินสดสุทธิ|ปีละ 34,000 บาท",
    28: "วิเคราะห์ 20 ปี|NPV เป็นบวก",
    29: "ประมาณ 83,817 บาท",
    30: "IRR 12.25%|คืนทุนประมาณ 7.35 ปี",
    31: "คุ้มค่าการลงทุน|ในกรณีจำลอง",
    32: "ระเบียบวิธีวิจัย",
    33: "ใช้แนวทางวิจัยและพัฒนา",
    34: "เริ่มจากศึกษาความต้องการของ SME",
    35: "ในจังหวัดสมุทรปราการ",
    36: "จำนวน 12–15 ราย",
    37: "พัฒนาต้นแบบ",
    38: "ตรวจสอบความถูกต้อง|ทดลองใช้งาน",
    39: "และประเมินความเป็นไปได้",
    40: "ตรวจสอบผลลัพธ์|สูตรการเงินอย่างน้อย 10 กรณี",
    41: "NPV คลาดเคลื่อนไม่เกิน 1 บาท",
    42: "IRR ไม่เกิน 0.01 จุดร้อยละ",
    43: "ทดลองใช้กับ SME|อย่างน้อย 6 ราย",
    44: "ประเมินประสิทธิภาพ|และความสะดวกในการใช้งาน",
    45: "แผนการดำเนินงาน 3 เดือน",
    46: "มกราคม – มีนาคม 2567",
    47: "เดือนแรก ศึกษาข้อมูล|เดือนที่ 2 พัฒนาต้นแบบ",
    48: "เดือนสุดท้าย|ทดสอบและประเมินผล",
    49: "งบประมาณวิจัย 40,000 บาท",
    50: "เน้นพัฒนาแพลตฟอร์ม|และตรวจสอบความถูกต้อง",
    51: "ประโยชน์และผลกระทบ|3 ด้าน",
    52: "ด้านเศรษฐกิจ|SME วิเคราะห์การลงทุน|ลดต้นทุนพลังงานระยะยาว",
    53: "แผนใช้เงินรางวัล|หากได้รับรางวัล 400,000 บาท",
    54: "ต่อยอดจากต้นแบบวิจัย|สู่แพลตฟอร์มที่พร้อมใช้งาน",
    55: "เน้น 3 ส่วนสำคัญ|1. พัฒนาระบบ|และเครื่องมือวิเคราะห์การเงิน",
    56: "2. ขยายการทดลองใช้กับ SME|และสร้างความร่วมมือ",
    57: "3. ความปลอดภัยของข้อมูล|และความพร้อมด้านกฎหมาย",
    58: "เป้าหมาย: ขยายผล|สู่ผู้ประกอบการทั่วประเทศ",
    59: "Solar Finance Marketplace|ไม่ใช่แค่เครื่องคำนวณผลตอบแทน",
    60: "แต่เชื่อมความรู้การเงิน|เข้ากับพลังงานสะอาด",
    61: "ให้ SME ตัดสินใจลงทุน|อย่างมั่นใจ",
    62: "ขอบคุณคณะกรรมการทุกท่านครับ",
}
HL = ["Solar Finance Marketplace", "SME", "250,000 บาท", "40,000 บาท", "6,000 บาท", "34,000 บาท",
      "83,817 บาท", "NPV เป็นบวก", "IRR 12.25%", "7.35 ปี", "4 ขั้นตอน", "พลังงานสะอาด", "400,000 บาท",
      "12–15 ราย", "10 กรณี", "6 ราย", "3 เดือน", "ซับซ้อน", "สูง", "ราชมงคลพระนคร", "ภัททิยะ ยาตรา"]

# Cut the spoken team roll-call (replaced by an on-screen card) — src 9.75..33.25
EXCLUDE = [(9.75, 33.25)]
# Section 3:24-3:38 (social/environment) is kept as video but has no verified subtitle text.

# speech intervals = complement of silences, padded
sil = [tuple(map(float, l.split())) for l in open(f"{V}/silences.txt") if l.strip()]
speech, t = [], 0.0
for a, b in sil:
    if a > t: speech.append([t, a])
    t = b
if t < dur: speech.append([t, dur])
PAD = 0.09
keep = []
for a, b in speech:
    pieces = [[max(0, a - PAD), min(dur, b + PAD)]]
    for ea, eb in EXCLUDE:  # subtract each excluded range
        nxt = []
        for pa, pb in pieces:
            if pb <= ea or pa >= eb: nxt.append([pa, pb]); continue
            if pa < ea: nxt.append([pa, ea])
            if pb > eb: nxt.append([eb, pb])
        pieces = nxt
    keep += [p for p in pieces if p[1] - p[0] > 0.2]
# merge overlaps / tiny gaps
keep.sort(); merged = []
for a, b in keep:
    if merged and a - merged[-1][1] < 0.12: merged[-1][1] = max(merged[-1][1], b)
    else: merged.append([a, b])
merged = [[a, min(b, until)] for a, b in merged if a < until]
# also switch framing at sentence starts (no time removed) so the shot changes every few seconds
splits = sorted(sg["start"] - 0.05 for sg in segs)
fine = []
for a, b in merged:
    cur = a
    for s in splits:
        if cur + 2.0 < s < b - 2.0:
            fine.append([cur, s]); cur = s
    fine.append([cur, b])
merged = fine
# punch-in zoom alternation; very short pieces keep the previous zoom
zs, z = [], 1.0
for a, b in merged:
    if b - a >= 1.0: z = 1.12 if z == 1.0 else 1.0
    zs.append([round(a, 3), round(b, 3), z])

subs = []
for i, sg in enumerate(segs):
    txt = CORR.get(i)
    if not txt or sg["start"] >= until: continue
    s0, s1 = sg["start"], sg["end"]
    if i == 52: s1 = min(s1, 204.0)  # only the verified economic sentence
    chunks = txt.split("|"); total = sum(len(c) for c in chunks); acc = 0
    for c in chunks:
        cs = s0 + (s1 - s0) * acc / total; acc += len(c); ce = s0 + (s1 - s0) * acc / total
        subs.append({"s": round(cs, 3), "e": round(ce, 3), "text": c, "hl": [h for h in HL if h in c][:2]})

STICK = [(33.6, "😓", 690), (41.3, "💸", 40), (52.8, "💡", 690), (66.6, "🌱", 40),
         (77.0, "⚙️", 690), (98.6, "💰", 690), (113.2, "📈", 40), (134.3, "🔬", 690), (154.6, "✅", 40),
         (173.9, "🗓️", 690), (186.7, "💵", 40), (193.9, "🌍", 690), (220.7, "🏆", 690), (259.8, "⭐", 40),
         (275.4, "🙏", 690)]
os.makedirs(f"{G}/stickers", exist_ok=True)
stickers = []
for k, (t0, em, x) in enumerate(STICK):
    if t0 >= until: continue
    f = f"{G}/stickers/s{k:02d}.mov"
    stickers.append({"t": t0, "dur": 1.8, "file": f, "x": x, "y": 220, "emoji": em})

plan = {
    "source": f"{V}/source.mp4", "voice": f"{V}/voice_clean.wav",
    "music": None if "--no-music" in sys.argv else f"{G}/music_bed.wav",
    "keep": zs, "subs": subs, "stickers": stickers,
    "hook": {"text": "ลงทุนโซลาร์ 250,000\\Nคุ้มไหม?", "dur": 2.6},
    "cards": [{"s": 4.1, "e": 9.7, "text": "ทีม Solar Finance Marketplace\\N"
               "นายภัททิยะ ยาตรา\\Nนางสาวเจนจิราภร สวนสำราณ\\Nนายฉัตรชัย ชูเชิด\\Nนางสาววิยะดา ยุทธ"}],
}
json.dump(plan, open(out, "w"), ensure_ascii=False, indent=1)
total = sum(b - a for a, b, _ in zs)
print(f"segments={len(zs)} kept={total:.1f}s subs={len(subs)} stickers={len(stickers)}")
