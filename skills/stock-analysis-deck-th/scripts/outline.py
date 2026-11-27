import html,base64,glob,io
from PIL import Image
B='นายภัททิยะ'; K='นายกฤตนัย'
S=[
(1,'ปก',B,'0:30',['แนะนำตัว: ภัททิยะ และกฤตนัย','คำถามเดียว: บริษัทดีอย่างศุภาลัย หุ้นน่าซื้อหรือไม่','เล่า 3 ช่วง: รู้จักบริษัท → วิเคราะห์งบ 5 ปี → สรุปและมูลค่า']),
(2,'ประวัติบริษัท',B,'0:25',['ก่อตั้ง 1989 · เข้าตลาด 1993 · ไปออสเตรเลีย 2014','ปัจจุบัน 414 โครงการ ใน 29 จังหวัด','แบรนด์ 36 ปี แข็งแรง']),
(3,'ธุรกิจและรายได้',B,'0:25',['รายได้ 95.7% มาจากขายบ้านและคอนโด','ยอดขายใหม่ 26,249 ล้านบาท ทรงตัว','กำไรผูกกับ "การโอนบ้าน"']),
(4,'วงจรเงิน',B,'0:35',['จ่ายเงินก่อน (16,936) → กลายเป็นสต็อก (77,448) → ขาย → โอน = รับรู้รายได้','3 อย่างที่ต้องจับตา: สต็อก · หนี้ · เงินสด']),
(5,'การเติบโต',B,'0:30',['ปี 2025 รายได้ −22.5% กำไร −35.1% ต่ำสุดใน 5 ปี (สูงสุดปี 2022)','ยอดขายใหม่ไม่ลด แต่ยอดโอนลด']),
(6,'อัตรากำไร',B,'0:25',['GPM 40 → 34% · OPM 29.7 → 20.6% · NPM 23.8 → 16.2%','ค่าใช้จ่ายไม่ลดตามรายได้ จึงกำไรลดเร็วกว่ารายได้']),
(7,'ROE / ROA',B,'0:50',['ROE 17.6% → 7.5% (ROA 10.2 → 4.0%)','สาเหตุหลัก: สินทรัพย์หมุนช้าลง (0.44 → 0.25 เท่า) [คลิก] ดูปี 2025','ROE ต่ำกว่าต้นทุนทุน 10% จึงทำให้ P/BV ต่ำ (0.52 เท่า)']),
(8,'สต็อก + กำไร 9M26',B,'0:50',['สต็อก 77,448 = 78% ของสินทรัพย์ ต้องขาย 3.27 ปี (เดิมราว 2 ปี)','[คลิก] กำไร 9M26 +7.6% แต่มาจาก JV +382 และภาษี +321 ส่วนธุรกิจหลัก −488','ส่งต่อให้กฤตนัย']),
(9,'สภาพคล่อง',K,'0:30',['Current ratio 2.66 ดูดี แต่ Quick ratio แค่ 0.16 (สต็อก = 94% ของสินทรัพย์หมุนเวียน)','หนี้ระยะสั้น 100 บาท มีเงินสดเพียง 15 บาท']),
(10,'หนี้สิน',K,'0:35',['D/E 0.81 ยังไม่น่ากลัว','หนี้มีดอกเบี้ย +91% แต่ EBITDA −40%','ND/EBITDA 2.04 → 6.42 เท่า = สัญญาณเตือนที่ชัดที่สุด']),
(11,'กระแสเงินสด',K,'0:40',['CFO ต่ำกว่ากำไรทุกปี (CFO/กำไร 0.57 → 0.21)','5 ปี ได้เงินสด 7,265 แต่จ่ายคืนผู้ถือหุ้น 13,901 → ส่วนต่าง 6,636 มาจากเงินกู้','Payout เพิ่ม 34% → 60%']),
(12,'เทียบคู่แข่ง',K,'0:35',['เทียบ AP · LH · QH · SIRI (งบปี 2025)','ดี: กำไรสุทธิอันดับ 2 · หนี้ต่อทุนอันดับ 2','แย่: รายได้ลดแรงที่สุด (อันดับ 5/5)','สรุป: ปัญหาคือยอดโอน ไม่ใช่ความสามารถทำกำไร']),
(13,'สุขภาพการเงิน',K,'0:40',['Dashboard: เกือบทุกตัวแย่ลง ยกเว้น Current ratio','[คลิก 5 ครั้ง] ประเมิน 5 ด้าน: Vulnerable 3 ด้าน · Stable/Mixed 2 ด้าน','สรุป: ยังไม่มีปัญหา แต่ผลตอบแทนลดและพึ่งหนี้มากขึ้น']),
(14,'Red flags + AI Audit',K,'0:55',['Red flag 4 ข้อ: สต็อก 3.27 ปี · ND/EBITDA 6.42 · CFO ต่ำ · กำไรพึ่ง JV+ภาษี','[คลิก 4 ครั้ง] AI บอกว่า สภาพคล่องดี / กำไรฟื้น / หนี้ต่ำ = ชวนเข้าใจผิด · ปันผลปลอดภัย = ผิด','บทเรียน: AI ตัวเลขถูกแต่ขาดบริบท เราจึงตรวจกับงบต้นฉบับทุกตัว','คำถามปิด: ต้องการข้อมูลเพิ่ม → อัตราปฏิเสธสินเชื่อ · อายุสต็อก · ตารางหุ้นกู้ 2027']),
(15,'มูลค่า',K,'0:50',['ราคา 15.40 · P/E 6.9 · P/BV 0.52 · ปันผล 8% ดูถูก','มูลค่ากลาง 14.89 (ช่วง 11.35–18.45) → ราคาสูงกว่าเล็กน้อย','[คลิก] เผื่อความปลอดภัย 20% → ควรซื้อ ≤ 11.91','ดูถูกเพราะ ROE ต่ำ ไม่ใช่ตลาดประเมินผิด']),
(16,'ตอบ 3 คำถาม',K,'0:35',['ธุรกิจดีไหม → ดี','การเงินแข็งแรงไหม → พอใช้ แนวโน้มอ่อนลง','ราคาน่าซื้อไหม → ยังไม่ใช่ รอ ≤ 11.91','ปิด: "บริษัทดี ≠ หุ้นน่าซื้อ"']),
(17,'ขอบคุณที่รับฟัง',K,'0:10',['ขอบคุณอาจารย์กรรณิการ์และเพื่อน ๆ']),
]
tot=sum(int(t[:1])*60+int(t[2:]) for _,_,_,t,_ in S);p1=sum(int(t[:1])*60+int(t[2:]) for n,_,_,t,_ in S if n<=8)
assert tot==600,tot
imgs=sorted(glob.glob('../jpg/*.jpg'))
def b64(p):
    im=Image.open(p).convert('RGB').resize((720,405));b=io.BytesIO();im.save(b,'JPEG',quality=82);return base64.b64encode(b.getvalue()).decode()
rows=''
for n,t,w,tm,bl in S:
    li=''.join('<li>'+html.escape(x).replace('[คลิก 5 ครั้ง]','<span class="clk">คลิก 5 ครั้ง</span>').replace('[คลิก 4 ครั้ง]','<span class="clk">คลิก 4 ครั้ง</span>').replace('[คลิก]','<span class="clk">คลิก</span>')+'</li>' for x in bl)
    rows+=f'<section class="s"><img src="data:image/jpeg;base64,{b64(imgs[n-1])}"><div class="tx"><div class="hd"><span class="no">{n}</span><span class="tt">{t}</span><span class="who {"b" if w==B else "k"}">{w.replace("นาย","")}</span><span class="tm">⏱ {tm}</span></div><ul>{li}</ul></div></section>\n'
    if n==8: rows+='<div class="hand">ส่งต่อผู้พูด: นายภัททิยะ → นายกฤตนัย (ครึ่งแรก 4:30 นาที)</div>'
doc=f'''<!doctype html><html lang="th"><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Kanit:wght@500;600&family=Anuphan:wght@400;600&display=swap">
<style>@page{{size:A4;margin:11mm 14mm 11mm}}*{{box-sizing:border-box;margin:0}}body{{font-family:'Anuphan',sans-serif;color:#14233A;font-size:12.5pt;line-height:1.55}}
.top{{background:#1E3A5F;color:#F3F1EC;border-radius:4mm;padding:4.5mm 7mm;margin-bottom:3.5mm}}.top h1{{font-family:'Kanit';font-size:24pt;line-height:1.2}}.top p{{font-size:11.5pt;color:#C9D4E2;margin-top:1.5mm}}
.nums{{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin-bottom:4mm}}.nums div{{border:1px solid #DDE3EB;border-radius:3mm;padding:2.5mm 3.5mm;background:#F5F7FA}}.nums b{{display:block;font-family:'Kanit';font-size:15pt;color:#9C6A10}}.nums span{{font-size:10pt;color:#4A5B70}}
.h{{font-family:'Kanit';font-weight:600;font-size:12pt;margin:2mm 0 1mm}}
.s{{display:flex;gap:5mm;padding:3.2mm 0;border-bottom:1px solid #E3E8EF;break-inside:avoid}}.s img{{width:46mm;height:25.9mm;flex:none;border:1px solid #DDE3EB;border-radius:2mm}}
.hd{{display:flex;gap:2.5mm;align-items:center;margin-bottom:1mm}}.no{{background:#1E3A5F;color:#fff;font-family:'Kanit';min-width:7.5mm;height:7.5mm;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11pt}}
.tt{{font-family:'Kanit';font-weight:600;font-size:13pt}}.who{{font-size:9.5pt;padding:0.3mm 2.5mm;border-radius:4mm;font-weight:600}}.who.b{{background:#DCE7F4;color:#1E3A5F}}.who.k{{background:#FBEFD2;color:#7A5208}}.tm{{font-size:10pt;color:#5E6E82;margin-left:auto;font-weight:600}}
ul{{padding-left:5mm}}li{{font-size:11.5pt;margin-bottom:0.6mm}}.clk{{background:#E2B04A;color:#14233A;font-weight:600;font-size:9pt;padding:0.2mm 1.8mm;border-radius:2mm}}
.hand{{text-align:center;background:#1E3A5F;color:#F3F1EC;border-radius:3mm;padding:1.8mm;margin:2.5mm 0;font-weight:600;font-size:10.5pt}}</style></head><body>
<div class="top"><h1>SPALI · หัวข้อพูดนำเสนอ (10 นาที)</h1><p>นายภัททิยะ ยาตรา (สไลด์ 1–8 · 4:30 นาที) · นายกฤตนัย เพ็ญไพรัตน์กุล (สไลด์ 9–17 · 5:30 นาที) · เสนอ อาจารย์กรรณิการ์ กลิ่นสุคนธ์</p></div>
<div class="h">ตัวเลขที่ต้องจำ 6 ตัว</div>
<div class="nums"><div><b>−22.5%</b><span>รายได้ปี 2025</span></div><div><b>17.6% → 7.5%</b><span>ROE</span></div><div><b>3.27 ปี</b><span>สต็อกขายหมด</span></div><div><b>6.42 เท่า</b><span>ND/EBITDA</span></div><div><b>0.21</b><span>CFO ÷ กำไร</span></div><div><b>14.89 / ≤ 11.91</b><span>มูลค่ากลาง / ราคาที่ควรซื้อ</span></div></div>
<div class="h">ข้อความหลัก: "บริษัทดี แต่ผลตอบแทนลด พึ่งหนี้มากขึ้น และราคายังไม่ถูกพอ"  <span class="clk">คลิก</span> = กดเพื่อแสดงส่วนถัดไปบนสไลด์</div>
{rows}</body></html>'''
open('outline.html','w',encoding='utf-8').write(doc)
md='# SPALI · หัวข้อพูดนำเสนอ (10 นาที)\n\nนายภัททิยะ ยาตรา สไลด์ 1–8 (4:30 นาที) · นายกฤตนัย เพ็ญไพรัตน์กุล สไลด์ 9–17 (5:30 นาที)\n\n**ตัวเลขที่ต้องจำ:** รายได้ 2025 −22.5% · ROE 17.6% → 7.5% · สต็อกขายหมด 3.27 ปี · ND/EBITDA 6.42 เท่า · CFO ÷ กำไร 0.21 · มูลค่ากลาง 14.89 / ซื้อได้ ≤ 11.91\n\n'
for n,t,w,tm,bl in S:
    md+=f'## สไลด์ {n} · {t} · {w} · {tm} นาที\n'+''.join(f'- {x}\n' for x in bl)+'\n'
    if n==8: md+='> ส่งต่อผู้พูด: นายภัททิยะ → นายกฤตนัย\n\n'
open(__import__('os').path.join(__import__('os').environ.get('OUT_DIR','.'),'Speaker_Outline_10min.md'),'w',encoding='utf-8').write(md)
print('ok',tot,p1)
