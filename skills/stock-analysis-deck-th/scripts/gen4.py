import os; D=os.path.join(os.environ.get('DECK_WORK','.'),'deck/project')
S=D+'/slides'
YRS=['2021','2022','2023','2024','2025']
NAVY='#1E3A5F'; GOLD='#E2B04A'; BLUE='#5B86BA'; RED='#B4504B'; LB='#6F95C4'
IMG={'aerial':'3e749685d1373fdd50626739300f7714','palm':'0e8dd132b3750405af9e704535c45cdd','river':'d235ecb2b1986d2a650bc74a1e60bf3b','night':'fe38f7919f029fb7ede6c3c9feb10ba4','skyline':'cd9d1b2bae8833eb533ea17611150bb3'}
SPK1='ผู้พูด: นายภัททิยะ ยาตรา\n\n'; SPK2='ผู้พูด: นายกฤตนัย เพ็ญไพรัตน์กุล\n\n'
def fmt(v,f): return ('−' if v<0 else '')+f.format(abs(v))
def head(tag,title,sub,tc='tag ev'):
    return f'<div class="hd">\n<p class="{tc}">{tag}</p>\n<h2 class="title">{title}</h2>\n<p class="sub">{sub}</p>\n</div>\n'
def foot(src,n,notes):
    return f'<p class="src">{src}</p>\n<p class="pg">SPALI · {n}</p>\n<div class="corner"></div>\n<aside>{notes}</aside>\n</section>\n'
def sec(i): return f'<section id="{i}" data-transition="fade">\n'
def legend(items):
    return '<div class="legend">'+''.join(f'<p class="pill" style="background:{c}; color:{"#14233A" if c in (GOLD,LB) else "#F3F1EC"}">{n}</p>' for n,c in items)+'</div>'
def ic(name,cls=''): return f'<div class="ic {cls}"><x-icon name="{name}"></x-icon></div>'
def circ(name,extra=''): return f'<div class="circ pop" style="{extra}"><x-icon name="{name}"></x-icon></div>'
def bars(series,hw,ph,extra=None,f='{:,.0f}',hi=None,top=34):
    vals=[v for _,vs in series for v in vs]; vmax=max(0,max(vals)); vmin=min(0,min(vals)); neg=vmin<0
    sc=ph/(vmax-vmin); zero=top+vmax*sc
    k=len(series); bw=min(60,(hw-40-(k-1)*6)//k); tot=k*bw+(k-1)*6; x0=(hw-tot)/2
    bottom=top+ph+(30 if neg else 0)
    H=bottom+44+((64 if extra and '<br>' in extra[0] else 34) if extra else 0)
    out='<div style="display:flex">\n'
    for i,y in enumerate(YRS):
        out+=f'<div class="host" style="width:{hw}px; height:{int(H)}px">\n<div style="position:absolute; left:0px; top:{int(zero)}px; width:{hw}px; height:2px; background:#C9D2DD"></div>\n'
        for j,(c,vs) in enumerate(series):
            v=vs[i]; x=int(x0+j*(bw+6)); h=max(3,abs(v)*sc)
            col=RED if v<0 else (hi if (hi and i==4 and j==0) else c)
            t=zero-h if v>=0 else zero+2
            g='gu' if v>=0 else 'gd'; rad='8px 8px 0 0' if v>=0 else '0 0 8px 8px'
            d=0.15+i*0.1+j*0.05
            out+=f'<div class="bar {g}" style="left:{x}px; top:{int(t)}px; width:{bw}px; height:{int(h)}px; background:{col}; border-radius:{rad}; animation-delay:{d:.2f}s"></div>\n'
            lt=t-30 if v>=0 else zero+h+6
            fw='; font-weight:600' if i==4 else ''
            out+=f'<p class="{"sv r" if v<0 else "sv"} fd" style="left:{x-15}px; top:{int(lt)}px; width:{bw+30}px{fw}">{fmt(v,f)}</p>\n'
        fw='; font-weight:600' if i==4 else ''
        out+=f'<p class="sy" style="left:0px; top:{int(bottom+10)}px; width:{hw}px{fw}">{y}</p>\n'
        if extra: out+=f'<p class="sy" style="left:0px; top:{int(bottom+42)}px; width:{hw}px{fw}">{extra[i]}</p>\n'
        out+='</div>\n'
    return out+'</div>\n'
def chart(title,leg,inner,w,cap=''):
    c=f'<p class="cap">{cap}</p>' if cap else ''
    return f'<div class="chart a1" style="width:{w}px; padding:20px 28px; gap:8px; box-sizing:border-box">\n<div style="display:flex; justify-content:space-between; align-items:center"><p class="lbl w" style="font-weight:600">{title}</p>{legend(leg) if leg else ""}</div>\n{inner}{c}</div>\n'
def take(t,k='ข้อสรุป'): return f'<div class="take a3"><p class="tk">{k}</p><p class="tt">{t}</p></div>\n'
def kcard(label,val,sub,col='nv',icon=None,icc='',delay=0.3,deep=False):
    i=ic(icon,icc) if icon else ''
    if deep: return f'<div class="card deep pop" style="flex:1; justify-content:center; gap:4px; padding:18px 26px; animation-delay:{delay}s"><div class="thead">{i}<p class="lbl onm">{label}</p></div><p class="kpi {col}">{val}</p><p class="lbl onm">{sub}</p></div>\n'
    return f'<div class="card pop" style="flex:1; justify-content:center; gap:4px; padding:18px 26px; animation-delay:{delay}s"><div class="thead">{i}<p class="lbl">{label}</p></div><p class="kpi {col}">{val}</p><p class="lbl">{sub}</p></div>\n'
def donut(pct,size,color,inner,thick=46,track='#E3E8EF'):
    r=(size-thick)/2; c=2*3.14159265*r; on=c*pct/100
    svg=f'<svg aria-label="วงกลมสัดส่วน {pct}%" width="{size}" height="{size}" viewBox="0 0 {size} {size}"><circle cx="{size/2}" cy="{size/2}" r="{r:.1f}" fill="none" stroke="{track}" stroke-width="{thick}"/><circle cx="{size/2}" cy="{size/2}" r="{r:.1f}" fill="none" stroke="{color}" stroke-width="{thick}" stroke-dasharray="{on:.1f} {c:.1f}" transform="rotate(-90 {size/2} {size/2})"/></svg>'
    return f'<div class="donut ring" style="width:{size}px; height:{size}px">{svg}<div class="hole" style="left:{thick}px; top:{thick}px; width:{size-2*thick}px; height:{size-2*thick}px">{inner}</div></div>'
def spark(vals,col):
    mx=max(abs(v) for v in vals); o='<div style="display:flex; align-items:flex-end; gap:5px; height:44px">'
    for i,v in enumerate(vals):
        hh=max(4,int(abs(v)/mx*44)); c=RED if v<0 else (col if i==4 else '#C9D2DD')
        o+=f'<div class="bar gu" style="position:relative; width:16px; height:{hh}px; background:{c}; border-radius:3px; animation-delay:{0.2+i*0.08:.2f}s"></div>'
    return o+'</div>'
P={}
def metric(i,n,tag,title,sub,ch,right,tk,src,notes,spk):
    h=sec(i)+head(tag,title,sub)
    h+='<div style="display:flex; gap:28px; align-items:stretch">\n'+ch+'<div class="a2" style="flex:1; display:flex; flex-direction:column; gap:16px">\n'+right+'</div>\n</div>\n'+take(tk)
    return h+foot(src,n,spk+notes)

# ---------- 2 history
tl=[('Lightbulb','1989','ก่อตั้ง ทุน 100 ล้าน'),('Trust','1992','เป็นบริษัทมหาชน'),('Chart','1993','เข้าตลาด SET'),('Globe','2014','ไปออสเตรเลีย'),('CheckCircle','2024','414 โครงการ')]
h=sec('history')+head('COMPANY · ประวัติ','36 ปี จากทุน 100 ล้านบาท สู่ 414 โครงการใน 29 จังหวัด','"ศุภาลัย" = ที่อยู่อาศัยอันเป็นมงคล','tag')
h+='<div style="position:relative; display:flex; gap:20px">\n<div class="hb" style="position:absolute; left:160px; top:42px; width:1344px; height:6px; background:#E2B04A; border-radius:3px"></div>\n'
for k,(icn,y,t) in enumerate(tl):
    last=k==4
    h+=f'<div class="pop" style="flex:1; display:flex; flex-direction:column; align-items:center; gap:10px; animation-delay:{0.3+k*0.15:.2f}s"><div class="circ" style="position:relative{"; background:#E2B04A" if last else ""}"><x-icon name="{icn}"{" style=\"color:#14233A\"" if last else ""}></x-icon></div><p class="num {"g" if last else "nv"}">{y}</p><p class="txt w" style="font-weight:600">{t}</p></div>\n'
h+='</div>\n<div class="a2" style="display:flex; gap:20px; align-items:stretch">\n'
h+=f'<img src="/_blob/{IMG["aerial"]}" alt="ภาพมุมสูงหมู่บ้านจัดสรร" style="width:720px; height:280px; object-fit:cover; border-radius:24px; box-shadow:0 10px 30px rgba(20,35,58,.12)">\n'
h+='<div style="flex:1; display:grid; grid-template-columns:1fr 1fr; gap:16px">\n'
for k,(icn,t,v,s) in enumerate([('Database','ทุนชำระแล้ว','1,953','ล้านบาท'),('Users','Free float','54.5%','ของหุ้นทั้งหมด'),('Globe','ต่างชาติถือ','13.0%','ของหุ้นทั้งหมด'),('Chart','รายได้ 2025','24,772','ล้านบาท')]):
    h+=f'<div class="card pop" style="flex-direction:row; align-items:center; gap:16px; padding:8px 22px; animation-delay:{0.6+k*0.1:.2f}s">{ic(icn,"goldt")}<div><p class="lbl">{t}</p><p class="num nv">{v}</p><p class="lbl">{s}</p></div></div>\n'
h+='</div>\n</div>\n'
h+=foot('ที่มา: แบบ 56-1 One Report · SET (ข้อมูลผู้ถือหุ้น: Free float 54.51%, ต่างชาติ 12.99%) · FS FY2025',2,SPK1+'บทพูด: ศุภาลัยก่อตั้งเมื่อ 26 มิถุนายน 1989 ด้วยทุน 100 ล้านบาท เป็นบริษัทมหาชนในปี 1992 และเข้าจดทะเบียนในตลาดหลักทรัพย์ฯ วันที่ 17 พฤศจิกายน 1993 ปี 2014 เริ่มลงทุนในออสเตรเลียผ่านการร่วมทุน ปัจจุบัน 24 โครงการใน 4 รัฐ และถึงมีนาคม 2024 พัฒนาสะสม 414 โครงการใน 29 จังหวัด\n\nตัวเลข: ทุนชำระแล้ว 1,953.05 ล้านบาท (FS FY2025) · Free float 54.51% · ต่างชาติ 12.99% (SET) · รายได้รวม 2025 24,772.2 ล้านบาท')
P['history']=h

# ---------- 3 biz
h=sec('biz')+head('COMPANY · ธุรกิจ','รายได้ 95.7% มาจากการขายบ้านและคอนโด','ลูกค้ารายได้ปานกลางถึงสูง · ปี 2025 · ล้านบาท','tag')
h+='<div style="display:flex; gap:24px; align-items:stretch">\n'
h+=f'<img class="a1" src="/_blob/{IMG["palm"]}" alt="โครงการ Supalai Palm Springs" style="width:480px; height:500px; object-fit:cover; border-radius:24px; box-shadow:0 10px 30px rgba(20,35,58,.12)">\n'
inner='<p class="kpi nv" style="font-size:58px">95.7%</p><p class="lbl">ขายอสังหาฯ</p>'
h+=f'<div class="card a1" style="width:440px; align-items:center; justify-content:center; gap:16px; padding:24px">{donut(95.7,280,NAVY,inner,48,GOLD)}<p class="txt w" style="font-weight:600">รายได้รวม 24,772</p><p class="lbl">ทอง 4.3% = ค่าเช่าอาคาร และโรงแรม</p></div>\n'
h+='<div class="a2" style="flex:1; display:flex; flex-direction:column; gap:16px">\n<div style="display:grid; grid-template-columns:1fr 1fr; gap:12px">'
for t in ['บ้านเดี่ยว','บ้านแฝด','ทาวน์โฮม','คอนโด']:
    h+=f'<div class="card" style="padding:12px 18px; align-items:center; background:#EEF2F7; box-shadow:none"><p class="txt nv" style="font-weight:600">{t}</p></div>'
h+='</div>\n<div class="card" style="flex:1; gap:8px; padding:16px 24px; justify-content:center"><p class="lbl w" style="font-weight:600">ยอดขายใหม่ (Presales) 2025</p><p class="kpi nv" style="font-size:68px">26,249</p>'
h+='<div class="hb" style="display:flex; height:44px; border-radius:12px; overflow:hidden"><div style="width:65.1%; background:#2E5B92; display:flex; align-items:center; padding-left:16px"><p class="lbl on" style="font-weight:600">แนวราบ 65%</p></div><div style="flex:1; background:#E2B04A; display:flex; align-items:center; padding-left:14px"><p class="lbl w" style="font-weight:600">คอนโด 35%</p></div></div>'
h+='<p class="lbl">ทรงตัวจากปี 2024 (26,743 · −1.8%)</p></div>\n</div>\n</div>\n'
h+=take('กำไรผูกกับการโอนบ้านเกือบทั้งหมด → กำลังซื้อลด รายได้ลดทันที')
h+=foot('ที่มา: FS FY2025 (รายได้ตามประเภท) · 56-1 One Report 2025 · MD&amp;A 2025 · ภาพโครงการ © ศุภาลัย ใช้เพื่อการศึกษา',3,SPK1+'บทพูด: สินค้าหลักคือบ้านเดี่ยว บ้านแฝด ทาวน์โฮม และคอนโด สำหรับลูกค้ารายได้ปานกลางถึงสูง วงกลมแสดงว่ารายได้ปี 2025 มาจากการขายอสังหาฯ 95.7% ยอดขายใหม่ 26,249 ล้านบาท แนวราบประมาณสองในสาม ใกล้เคียงปีก่อน\n\nตัวเลข: รายได้ขายอสังหาฯ 23,713.6 ÷ รายได้รวม 24,772.2 = 95.7% · Presales แนวราบ 17,087 + คอนโด 9,162 = 26,249 (แนวราบ 65.1%) · 2024 26,743')
P['biz']=h

# ---------- 4 cycle
steps=[('Settings','ซื้อที่ดิน + ก่อสร้าง','16,936','จ่ายในปี 2025'),('Database','สต็อกโครงการ','77,448','คงเหลือสิ้นปี 2025'),('Users','ขายล่วงหน้า','26,249','Presales 2025'),('CheckCircle','โอน = รายได้','24,772','รายได้รวม 2025')]
h=sec('cycle')+head('COMPANY · วงจรเงิน','จ่ายเงินก่อน แต่รับรู้รายได้ตอนโอนบ้าน','ล้านบาท · แต่ละขั้นต่างช่วงเวลา ใช้ดูลำดับ ไม่ได้บวกลบกัน','tag')
h+='<div style="display:flex; gap:10px; align-items:stretch">\n'
for k,(icn,t,v,s) in enumerate(steps):
    if k: h+=f'<div class="nudge" style="align-self:center"><x-shape kind="arrow-right" style="background:#E2B04A; width:44px; height:28px"></x-shape></div>\n'
    dp=k==3
    h+=f'<div class="card{" deep" if dp else ""} pop" style="flex:1; align-items:center; text-align:center; gap:8px; padding:26px 20px; animation-delay:{0.2+k*0.2:.1f}s"><div class="circ"{" style=\"background:#E2B04A\"" if dp else ""}><x-icon name="{icn}"{" style=\"color:#14233A\"" if dp else ""}></x-icon></div><p class="txt {"on" if dp else "w"}" style="font-weight:600">{t}</p><p class="kpi {"gl" if dp else "nv"}" style="font-size:72px">{v}</p><p class="lbl{" onm" if dp else ""}">{s}</p></div>\n'
h+='</div>\n<div class="a3" style="display:flex; gap:16px">\n'
for icn,cls,t in [('Clock','goldt','รายได้ตามหลังยอดขาย 1–3 ปี'),('Warning','red','สต็อกทำให้ Current ratio สูงเกินจริง'),('Activity','blue','ค่าที่ดินอยู่ใน CFO → CFO ผันผวน')]:
    h+=f'<div class="card" style="flex:1; flex-direction:row; align-items:center; gap:14px; padding:14px 20px">{ic(icn,cls)}<p class="txt w" style="font-weight:600">{t}</p></div>\n'
h+='</div>\n'
h+=take('ปี 2025 เปิดใหม่ 22 โครงการ (29,470) · Backlog 15,264 (ก.ย. 26) → จับตา สต็อก · หนี้ · CFO','จับตา')
h+=foot('ที่มา: FS FY2025 (Note 24, ต้นทุนโครงการ) · MD&amp;A 2025 และ 3Q26 (Presales, Backlog, โครงการใหม่)',4,SPK1+'บทพูด: ธุรกิจนี้จ่ายเงินก่อน ปี 2025 จ่ายค่าที่ดินและก่อสร้าง 16,936 ล้านบาท เงินไปพักเป็นสต็อก 77,448 ล้านบาท ขายล่วงหน้าแล้วจึงรับรู้รายได้เมื่อโอน ผลต่อการอ่านงบมีสามข้อ คือ รายได้ตามหลังยอดขาย Current ratio ดูสูงเพราะนับสต็อก และ CFO ผันผวนเพราะค่าที่ดินอยู่ในกิจกรรมดำเนินงาน\n\nตัวเลข: Note 24 FS FY2025 Purchase of land and payment of construction 16,936 (2024: 27,308) · Property development costs 77,447.6 · Presales 2025 26,249 · โครงการใหม่ 22 โครงการ 29,470 · Backlog 15,264 ณ 30 ก.ย. 2026 (MD&amp;A 3Q26)')
P['cycle']=h

# ---------- 5 frame
dims=[('Chart','เติบโต + ทำกำไร','6–8','Growth · Margin · ROE · DuPont'),('Search','คุณภาพกำไร + สต็อก','9','MD&amp;A bridge · ปีขายหมด'),('Trust','สภาพคล่อง + หนี้','10–11','Quick · ND/EBITDA · ICR'),('Activity','กระแสเงินสด','12','CFO/NP · FCF · Payout')]
h=sec('frame')+head('METHOD · กรอบการวิเคราะห์','วิเคราะห์ 4 มิติ จากงบที่ตรวจแล้ว และตรวจทุกตัวเลขที่ AI ให้มา','งบการเงินรวม 2021–2025 · กำไร = ส่วนของบริษัทใหญ่ · อัตราส่วนใช้ยอดปลายปี','tag')
h+='<div style="display:flex; gap:18px">\n'
for k,(icn,t,sl,m) in enumerate(dims):
    h+=f'<div class="card pop" style="flex:1; align-items:center; text-align:center; gap:10px; padding:26px 20px; animation-delay:{0.2+k*0.15:.2f}s"><div class="circ"><x-icon name="{icn}"></x-icon></div><p class="h3 nv">{t}</p><p class="lbl">{m}</p><p class="pill gold" style="align-self:center">สไลด์ {sl}</p></div>\n'
h+='</div>\n<div class="a3" style="display:flex; gap:18px; align-items:stretch">\n<div class="card" style="flex:2.2; gap:12px; padding:18px 24px"><p class="lbl w" style="font-weight:600">ลำดับความน่าเชื่อถือของข้อมูล</p><div style="display:flex; gap:8px; align-items:center">'
for k,(t,c,tc) in enumerate([('งบที่ผู้สอบบัญชีตรวจ',NAVY,'on'),('56-1 · MD&amp;A','#2E5B92','on'),('SET',LB,'w'),('โบรกเกอร์ (รอง)','#C9D2DD','w')]):
    if k: h+='<x-shape kind="arrow-right" style="background:#E2B04A; width:26px; height:18px"></x-shape>'
    h+=f'<div style="flex:1; background:{c}; border-radius:12px; padding:10px 12px; text-align:center"><p class="lbl {tc}" style="font-weight:600">{t}</p></div>'
h+='</div></div>\n<div class="card focus" style="flex:1; flex-direction:row; align-items:center; gap:14px; padding:18px 22px">'+ic('Verified','light')+'<div><p class="txt w" style="font-weight:600">AI ช่วยดึง + คำนวณ</p><p class="lbl">คนตรวจกับต้นฉบับ → สไลด์ 14</p></div></div>\n</div>\n'
h+=foot('ที่มา: กรอบ 4 มิติ · Data source hierarchy · 6-step process (Workshop 2: Stock in Focus) ปรับใช้กับ SPALI',5,SPK1+'บทพูด: เราวิเคราะห์ตามสี่มิติของ Workshop การ์ดแต่ละใบบอกตัวชี้วัดและสไลด์ที่จะนำเสนอ ข้อมูลใช้งบที่ผู้สอบบัญชีตรวจแล้วเป็นหลัก ตามด้วย 56-1 และ MD&amp;A SET และบทวิเคราะห์โบรกเกอร์เป็นความเห็นรอง AI ใช้ช่วยดึงข้อมูลและคำนวณ ทุกตัวเลขตรวจกับต้นฉบับก่อนใช้\n\nข้อจำกัด: อัตราส่วนคิดจากยอดปลายปี · ROE ใช้ส่วนของผู้ถือหุ้นบริษัทใหญ่ (ไม่รวมส่วนได้เสียที่ไม่มีอำนาจควบคุม) ให้ตรงกับกำไรส่วนของบริษัทใหญ่ · D/E และ Net gearing ใช้ส่วนของผู้ถือหุ้นรวม')
P['frame']=h

# ---------- 6 grow
rev=[29647,35501,31818,31985,24772]; npf=[7070,8173,5989,6190,4015]
gr=['+41.4%<br><span class="g">+66.3%</span>','+19.7%<br><span class="g">+15.6%</span>','<span class="r">−10.4%<br>−26.7%</span>','+0.5%<br><span class="g">+3.3%</span>','<span class="r">−22.5%<br>−35.1%</span>']
ch=chart('รายได้รวม และกำไรสุทธิ (ล้านบาท) · แถวล่าง: % เติบโต',[('รายได้',NAVY),('กำไร',GOLD)],bars([(NAVY,rev),(GOLD,npf)],210,200,extra=gr),1110,'สูตร: เติบโต = ปีนี้ ÷ ปีก่อน − 1 · CAGR = (2025 ÷ 2021)^(1/4) − 1')
rt=kcard('CAGR รายได้ 2021–25','−4.4%','ต่อปี','r','Activity','red',0.5)
rt+=kcard('CAGR กำไร 2021–25','−13.2%','ต่อปี','r','Warning','red',0.7)
P['grow']=metric('grow',6,'ANALYSIS · การเติบโต','ปี 2025 รายได้ลด 22.5% กำไรลด 35.1% ต่ำสุดในรอบ 5 ปี','งบกำไรขาดทุนรวม · จุดสูงสุดปี 2022',ch,rt,'Presales ทรงตัว แต่การโอนลด (รายได้ขายอสังหาฯ −23%) และกำไรลดเร็วกว่ารายได้','ที่มา: งบกำไรขาดทุนรวม FY2021–FY2025 (EY) · กำไร = ส่วนของบริษัทใหญ่ · CAGR คำนวณโดยผู้จัดทำ','บทพูด: รายได้และกำไรสูงสุดในปี 2022 แล้วลดลงแรงในปี 2025 รายได้ลด 22.5% กำไรลด 35.1% ห้าปีเฉลี่ยรายได้ติดลบ 4.4% ต่อปี กำไรติดลบ 13.2% ต่อปี ยอดขายใหม่ใกล้เคียงเดิม แต่การโอนลดลง และกำไรลดเร็วกว่ารายได้\n\nตัวเลข (ล้านบาท): รายได้รวม 29,647.5 / 35,500.7 / 31,818.1 / 31,984.7 / 24,772.2 · กำไรส่วนบริษัทใหญ่ 7,070.3 / 8,173.3 / 5,989.4 / 6,189.5 / 4,015.0 · รายได้ขายอสังหาฯ 30,816.6 → 23,713.6 = −23.0%',SPK1)

# ---------- 7 margin
ch=chart('อัตรากำไร 3 ระดับ (%)',[('GPM',NAVY),('OPM',BLUE),('NPM',GOLD)],bars([(NAVY,[40,39,36,38,34]),(BLUE,[29.7,29.3,24.8,25.8,20.6]),(GOLD,[23.8,23.0,18.8,19.4,16.2])],210,235,f='{:g}'),1110,'สูตร: GPM = กำไรขั้นต้น ÷ รายได้ขาย · OPM = กำไรจากการดำเนินงาน ÷ รายได้รวม · NPM = กำไรสุทธิ ÷ รายได้รวม')
rt=''
for k,(a,b,c) in enumerate([('GPM','−6.0','40 → 34%'),('OPM','−9.1','29.7 → 20.6%'),('NPM','−7.6','23.8 → 16.2%')]):
    rt+=f'<div class="card pop" style="flex:1; flex-direction:row; align-items:center; justify-content:space-between; padding:14px 24px; animation-delay:{0.5+k*0.15:.2f}s"><div><p class="h3 nv">{a}</p><p class="lbl">{c}</p></div><p class="kpi r" style="font-size:64px">{b}<span class="lbl r"> จุด</span></p></div>\n'
P['margin']=metric('margin',7,'ANALYSIS · ความสามารถทำกำไร','อัตรากำไรลดทุกระดับ: OPM จาก 29.7% เหลือ 20.6%','งบกำไรขาดทุนรวม · % ของรายได้',ch,rt,'OPM ลดมากกว่า GPM → ค่าใช้จ่ายขายและบริหารไม่ลดตามรายได้ · 9M26 OPM ลดต่อเหลือ 17.2%','ที่มา: งบกำไรขาดทุนรวม FY2021–FY2025 · 9M26 · กำไรจากการดำเนินงาน = กำไรก่อนภาษี + ต้นทุนการเงิน − ส่วนแบ่งกำไร JV','บทพูด: อัตรากำไรลดทั้งสามระดับ GPM ลด 6 จุด แปลว่าขายบ้านได้กำไรต่อหลังน้อยลง OPM ลด 9.1 จุด มากกว่า GPM เพราะค่าใช้จ่ายขายและบริหารไม่ลดตามรายได้ และเก้าเดือนแรกของปี 2026 OPM ลดต่อเหลือ 17.2%\n\nตัวเลข: กำไรจากการดำเนินงาน 8,808.6 / 10,401.8 / 7,890.3 / 8,251.8 / 5,114.9 ÷ รายได้รวม · GPM ปัดเป็นจำนวนเต็ม · 9M26 OPM = (3,485.0 + 460.3 − 1,112.1) ÷ 16,501.8 = 17.2%',SPK1)

# ---------- 8 roe (owners' equity)
ROE=[16.8,17.6,11.9,11.6,7.5]; ROA=[9.9,10.2,7.0,6.4,4.0]
ch=chart('ROE และ ROA (%)',[('ROE',NAVY),('ROA',GOLD)],bars([(NAVY,ROE),(GOLD,ROA)],150,250,f='{:.1f}'),810,'ROE = กำไรสุทธิ ÷ ส่วนผู้ถือหุ้นบริษัทใหญ่ · ROA = กำไรสุทธิ ÷ สินทรัพย์รวม')
def eqrow(lbl,vals,hl):
    o=f'<div style="display:flex; align-items:center; gap:8px"><p class="lbl w" style="width:64px; font-weight:600">{lbl}</p>'
    names=['NPM','รอบหมุน','หนี้ (EM)']
    for k,v in enumerate(vals[:3]):
        bg='#FBEFD2' if hl and k==1 else ('#FFFFFF')
        o+=f'<div class="card" style="flex:1; padding:8px 10px; gap:0; align-items:center; background:{bg}; box-shadow:none"><p class="cap">{names[k]}</p><p class="h3 {"r" if hl and k==1 else "nv"}">{v}</p></div><p class="h3 g">{"×" if k<2 else "="}</p>'
    o+=f'<div class="card {"deep" if hl else ""}" style="flex:1; padding:8px 10px; gap:0; align-items:center"><p class="cap{" onm" if hl else ""}">ROE</p><p class="h3 {"gl" if hl else "nv"}">{vals[3]}</p></div></div>'
    return o
rt='<div class="card pop" style="gap:12px; padding:18px 20px; animation-delay:.4s"><p class="lbl w" style="font-weight:600">DuPont: ROE = NPM × รอบหมุนสินทรัพย์ × ตัวคูณส่วนทุน</p>'+eqrow('2022',['23.0%','0.44','1.72','17.6%'],False)+eqrow('2025',['16.2%','0.25','1.85','7.5%'],True)+'</div>\n'
rt+='<div class="card pop" style="gap:10px; padding:16px 20px; animation-delay:.7s"><p class="lbl w" style="font-weight:600">ROE 2024 → 2025 ลด 4.2 จุด มาจาก</p><div class="hb" style="display:flex; height:44px; border-radius:10px; overflow:hidden"><div style="width:62%; background:#B4504B; display:flex; align-items:center; padding-left:12px"><p class="lbl on" style="font-weight:600">รอบหมุนช้าลง 65%</p></div><div style="flex:1; background:#E2B04A; display:flex; align-items:center; padding-left:12px"><p class="lbl w" style="font-weight:600">อัตรากำไร 40%</p></div></div><p class="cap">หนี้ที่เพิ่มช่วยดันกลับ 5%</p></div>\n'
P['roe']=metric('roe',8,'ANALYSIS · ROE / ROA','ROE ลดจาก 17.6% เหลือ 7.5% เพราะสินทรัพย์หมุนช้าลง','คำนวณจากงบรวม · ยอดปลายปี · แยกสาเหตุด้วย DuPont',ch,rt,'ROE 7.5% ต่ำกว่าต้นทุนส่วนของผู้ถือหุ้นที่ใช้ประเมิน (10%) → สอดคล้องกับ P/BV ต่ำกว่า 1 เท่า','ที่มา: คำนวณจากงบรวม FY2021–FY2025 · ส่วนผู้ถือหุ้นบริษัทใหญ่ 42,070 / 46,514 / 50,475 / 53,176 / 53,728 ล้านบาท','บทพูด: ROE ลดจาก 17.6% ในปี 2022 เหลือ 7.5% ในปี 2025 ROA จาก 10.2% เหลือ 4.0% สมการ DuPont ชี้ว่าตัวที่เปลี่ยนมากที่สุดคือรอบหมุนสินทรัพย์ จาก 0.44 เหลือ 0.25 เท่า สินทรัพย์เพิ่มขึ้นแต่สร้างรายได้น้อยลง หนี้ที่เพิ่มขึ้นกลับช่วยพยุง ROE ไว้เล็กน้อย ROE ต่ำกว่าต้นทุนส่วนของผู้ถือหุ้น 10% ตลาดจึงให้ราคาต่ำกว่ามูลค่าตามบัญชี\n\nแก้ไขจากฉบับก่อน: ใช้ส่วนของผู้ถือหุ้นบริษัทใหญ่ (ไม่รวม NCI) ให้ตรงกับกำไรส่วนบริษัทใหญ่ ROE จึงเป็น 16.8 / 17.6 / 11.9 / 11.6 / 7.5% · EM = สินทรัพย์รวม ÷ ส่วนผู้ถือหุ้นบริษัทใหญ่ 1.70 / 1.72 / 1.71 / 1.81 / 1.85 · การแยกส่วน 2024 → 2025 (log): NPM −0.177 (40%) · Asset turnover −0.287 (65%) · EM +0.021 (−5%) · รวม −0.443',SPK1)

# ---------- 9 stock
inv=[62104,65675,71125,74641,77448]
ch=chart('สต็อกโครงการ (ล้านบาท) · แถวล่าง: ปีที่ใช้ขายหมด',None,bars([(NAVY,inv)],140,240,extra=['2.15 ปี','1.92 ปี','2.31 ปี','2.42 ปี','<span class="r" style="font-weight:600">3.27 ปี</span>'],hi=GOLD),740,'ปีที่ขายหมด = สต็อก ÷ รายได้ขายอสังหาฯ ต่อปี')
def y(v): return 40+(3100-v)/900*240
wf=[('กำไร<br>9M25',2200,2677.1,BLUE,'2,677.1',''),('ส่วนแบ่ง<br>JV',2677.1,3058.8,GOLD,'+381.7','g'),('ธุรกิจหลัก<br>ก่อนภาษี',2570.8,3058.8,RED,'−488.0','r'),('ภาษี<br>ลดลง',2570.8,2891.9,GOLD,'+321.1','g'),('อื่น ๆ',2881.5,2891.9,RED,'−10.4','r'),('กำไร<br>9M26',2200,2881.5,NAVY,'2,881.5','')]
w='<div class="host" style="width:800px; height:350px">\n'
for k,(lb,lo,hi_,c,vl,vc) in enumerate(wf):
    x=10+k*132; t=y(hi_); hh=max(4,y(lo)-t)
    w+=f'<div class="bar gu" style="left:{x}px; top:{int(t)}px; width:100px; height:{int(hh)}px; background:{c}; border-radius:6px; animation-delay:{0.3+k*0.18:.2f}s"></div>\n'
    lt=t+hh+6 if vc=='r' else t-30
    w+=f'<p class="vl {vc} fd" style="left:{x-20}px; top:{int(lt)}px; width:140px; font-weight:600">{vl}</p>\n'
    w+=f'<p class="cl" style="left:{x-20}px; top:290px; width:140px">{lb}</p>\n'
w+='<div style="position:absolute; left:0px; top:280px; width:800px; height:2px; background:#C9D2DD"></div>\n</div>\n'
rt=f'<div class="chart" style="padding:20px 26px; gap:6px"><p class="lbl w" style="font-weight:600">กำไรสุทธิ 9M25 → 9M26 (ล้านบาท) · แกนเริ่ม 2,200</p>\n{w}<p class="cap">EBIT ไม่รวม JV <span class="r">−17.1%</span> · อัตราภาษี 16.1% เทียบ 24.6%</p></div>\n'
P['stock']=metric('stock',9,'ANALYSIS · สต็อกและคุณภาพกำไร (MD&amp;A)','สต็อกต้องขาย 3.27 ปี และกำไร 9M26 โตจากรายการพิเศษ','สต็อก = ต้นทุนโครงการระหว่างพัฒนา = 78% ของสินทรัพย์รวม',ch,rt,'สต็อกเพิ่ม 25% ใน 5 ปี · กำไร 9M26 +7.6% มาจาก JV และภาษี ขณะธุรกิจหลักลดลง','ที่มา: งบฐานะการเงินรวม FY2021–FY2025 · งบไตรมาส 9M26 · MD&amp;A 3Q26 · การกระทบยอดคำนวณโดยผู้จัดทำ','บทพูด: สต็อกเพิ่มจาก 62,104 เป็น 77,448 ล้านบาท ถ้าขายในอัตราปี 2025 ต้องใช้ 3.27 ปี จากเดิมราวสองปี ด้านขวาคือการอ่าน MD&amp;A กำไรเก้าเดือนเพิ่ม 204 ล้านบาท แต่มาจากส่วนแบ่งกำไรร่วมทุน 382 และภาษีที่ลดลง 321 ขณะธุรกิจหลักก่อนภาษีลดลง 488 ล้านบาท\n\nปีที่ขายหมด: 62,104 ÷ 28,937.9 = 2.15 · 65,675 ÷ 34,221.8 = 1.92 · 71,125 ÷ 30,836.4 = 2.31 · 74,641 ÷ 30,816.6 = 2.42 · 77,448 ÷ 23,713.6 = 3.27 · การกระทบยอด 9M: กำไรก่อนภาษี 3,485.0 เทียบ 3,591.3 · JV 1,112.1 เทียบ 730.4 · ภาษี 561.1 เทียบ 882.2 · อื่น ๆ −10.4 · EBIT ไม่รวม JV 2,833 เทียบ 3,419',SPK2)

# ---------- 10 liq
ch=chart('Current ratio และ Quick ratio (เท่า)',[('Current',NAVY),('Quick',GOLD)],bars([(NAVY,[2.74,2.49,2.86,2.44,2.66]),(GOLD,[0.13,0.12,0.24,0.20,0.16])],210,270,f='{:.2f}'),1110,'Current = สินทรัพย์หมุนเวียน ÷ หนี้สินหมุนเวียน · Quick = (สินทรัพย์หมุนเวียน − สต็อก) ÷ หนี้สินหมุนเวียน')
sq=''.join(f'<div class="sq{" on" if k<3 else ""} pop" style="animation-delay:{0.4+k*0.04:.2f}s"></div>' for k in range(20))
rt=f'<div class="card" style="flex:1; gap:12px; padding:22px 26px; justify-content:center"><p class="lbl w" style="font-weight:600">หนี้ระยะสั้น 100 บาท มีเงินสดเพียง</p><p class="kpi g">15 บาท</p><div style="display:grid; grid-template-columns:repeat(10, 34px); gap:8px">{sq}</div><p class="lbl">ปี 2025: เงินสด 3,788 · หนี้ถึงกำหนดใน 1 ปี 25,246</p></div>\n'
P['liq']=metric('liq',10,'ANALYSIS · สภาพคล่อง','Current ratio 2.66 ดูดี แต่ไม่นับสต็อก Quick ratio เหลือ 0.16','งบฐานะการเงินรวม · เท่า · สต็อก = 94% ของสินทรัพย์หมุนเวียน',ch,rt,'สภาพคล่องจริงขึ้นกับการขายสต็อก และการกู้ใหม่หรือออกหุ้นกู้ใหม่มาชำระหนี้เดิม','ที่มา: งบฐานะการเงินรวม FY2021–FY2025 · หนี้ระยะสั้น 2025 = ตั๋วแลกเงิน 6,163 + เงินกู้และหุ้นกู้ที่ถึงกำหนดใน 1 ปี 19,083','บทพูด: Current ratio อยู่ราว 2.5 ถึง 2.9 เท่าทุกปี แต่ 94% ของสินทรัพย์หมุนเวียนคือสต็อก ตัดออกแล้ว Quick ratio เหลือ 0.12 ถึง 0.24 เท่า ภาพขวาบอกว่าหนี้ที่ถึงกำหนดในหนึ่งปีทุก 100 บาท บริษัทมีเงินสดรองรับเพียง 15 บาท\n\nตัวเลข 2025: สินทรัพย์หมุนเวียน 82,369.9 ÷ หนี้สินหมุนเวียน 31,007 = 2.66 · (82,369.9 − 77,447.6) ÷ 31,007 = 0.16 · หนี้ระยะสั้น = ตั๋วแลกเงิน 6,163.0 + เงินกู้ธนาคารส่วนที่ถึงกำหนด 9,961.0 + หุ้นกู้ส่วนที่ถึงกำหนด 9,121.9 = 25,246 · เงินสด 3,788.2 ÷ 25,246 = 15.0% · เงินสด ÷ หนี้ระยะสั้น 5 ปี 10.2 / 6.4 / 23.0 / 19.5 / 15.0%',SPK2)

# ---------- 11 debt
ibd=[19890,24536,27164,34187,37988]
ch=chart('หนี้ที่มีดอกเบี้ย (ล้านบาท) · แถวล่าง: ND/EBITDA (เท่า)',None,bars([(NAVY,ibd)],150,210,extra=['2.04','2.21','2.80','3.44','<span class="r" style="font-weight:600">6.42</span>'],hi=RED),810,'ND/EBITDA = (หนี้มีดอกเบี้ย − เงินสด) ÷ (กำไรจากการดำเนินงาน + ค่าเสื่อมราคา)')
rt='<div style="display:flex; gap:14px">'+kcard('หนี้มีดอกเบี้ย 5 ปี','+91%','19,890 → 37,988','r','Warning','red',0.4)+kcard('EBITDA 5 ปี','−40%','8,931 → 5,328','r','Activity','red',0.6)+'</div>\n'
rt+='<table class="tb pop" style="font-size:24px; animation-delay:.8s">\n<tr class="th"><th style="width:30%">อัตราส่วน (เท่า)</th>'+''.join(f'<th class="n">{y_}</th>' for y_ in YRS)+'</tr>\n'
for r,row in enumerate([['D/E','0.66','0.68','0.67','0.77','0.81'],['Net gearing','0.43','0.49','0.44','0.54','0.62'],['ICR','36.1','39.0','17.4','12.2','8.1']]):
    rt+=f'<tr{" class=\"z\"" if r%2 else ""}><td>{row[0]}</td>'+''.join(f'<td class="n">{c}</td>' for c in row[1:])+'</tr>\n'
rt+='</table>\n'
P['debt']=metric('debt',11,'ANALYSIS · หนี้สิน','หนี้มีดอกเบี้ย +91% ใน 5 ปี ดัน ND/EBITDA เป็น 6.42 เท่า','D/E = หนี้สินรวม ÷ ส่วนผู้ถือหุ้นรวม · ICR = (กำไรก่อนภาษี + ต้นทุนการเงิน) ÷ ต้นทุนการเงิน',ch,rt,'D/E 0.81 ยังไม่อันตราย แต่หนี้เทียบความสามารถหาเงินเพิ่มกว่า 3 เท่า → สัญญาณเตือนที่ชัดที่สุด','ที่มา: งบรวม FY2021–FY2025 · หมายเหตุเงินกู้และหุ้นกู้ · ค่าเสื่อมราคาจากงบกระแสเงินสด · คำนวณโดยผู้จัดทำ','บทพูด: ถ้าดูแค่ D/E หนี้ยังต่ำกว่าหนึ่งเท่า แต่หนี้ที่มีดอกเบี้ยเพิ่ม 91% ขณะที่ EBITDA ลด 40% ND/EBITDA จึงเพิ่มจาก 2.04 เป็น 6.42 เท่า ความสามารถจ่ายดอกเบี้ยลดจาก 36 เท่าเหลือ 8 เท่า ยังจ่ายได้ แต่แนวโน้มชัดว่าพึ่งหนี้มากขึ้น\n\nEBITDA = กำไรจากการดำเนินงาน + ค่าเสื่อมราคา: 2021 8,808.6 + 122.7 = 8,931.3 · 2025 5,114.9 + 213.3 = 5,328.2 (−40.3%) · ND 2025 = 37,988 − 3,788 = 34,200 · ICR 2025 = (5,120.7 + 724.6) ÷ 724.6 = 8.1 (นับรวมส่วนแบ่ง JV) · แก้ไขจากฉบับก่อน: สูตร ICR เดิมเขียนว่าใช้กำไรจากการดำเนินงาน ซึ่งจะได้ 7.1 เท่า ตัวเลข 8.1 คำนวณจากกำไรก่อนภาษี + ต้นทุนการเงิน',SPK2)

# ---------- 12 cash
ch=chart('กำไรสุทธิ เทียบ CFO (ล้านบาท) · แถวล่าง: FCF',[('กำไร',NAVY),('CFO',GOLD)],bars([(NAVY,npf),(GOLD,[4009,3270,-180,-687,853])],210,200,extra=['3,925','3,145','<span class="r">−259</span>','<span class="r">−930</span>','712']),1110,'CFO/NP = เงินสดจากการดำเนินงาน ÷ กำไรสุทธิ · FCF = CFO − รายจ่ายลงทุน · Payout = DPS ÷ EPS')
rt='<div class="card" style="flex:1; gap:10px; padding:20px 24px; justify-content:center"><p class="lbl w" style="font-weight:600">รวม 5 ปี (ล้านบาท)</p>'
rt+='<div class="hb" style="width:52%; height:44px; background:#E2B04A; border-radius:10px; display:flex; align-items:center; padding-left:14px; box-sizing:border-box"><p class="lbl w" style="font-weight:600">CFO 7,265</p></div>'
rt+='<div class="hb" style="width:100%; height:44px; background:#1E3A5F; border-radius:10px; display:flex; align-items:center; padding-left:14px; box-sizing:border-box; animation-delay:.6s"><p class="lbl on" style="font-weight:600">ปันผล + ซื้อหุ้นคืน 13,901</p></div>'
rt+='<p class="lbl">ส่วนต่าง <span class="r" style="font-weight:600">6,636</span> มาจากเงินกู้ (1.9 เท่าของ CFO)</p></div>\n'
inner='<p class="h3 nv">60%</p><p class="cap">Payout 2025</p>'
rt+=f'<div class="card pop" style="flex-direction:row; align-items:center; gap:20px; padding:14px 24px; animation-delay:.8s">{donut(60,150,GOLD,inner,22)}<div><p class="txt w" style="font-weight:600">Payout ratio เพิ่มขึ้น</p><p class="lbl">34% → 35% → 47% → 46% → 60%</p></div></div>\n'
P['cash']=metric('cash',12,'ANALYSIS · กระแสเงินสด','CFO ต่ำกว่ากำไรทุกปี แต่จ่ายคืนผู้ถือหุ้น 1.9 เท่าของ CFO','งบกระแสเงินสดรวม · ล้านบาท · CFO/NP 0.57 → 0.21',ch,rt,'เงินสดถูกใช้ซื้อที่ดินและก่อสร้าง ปันผลส่วนหนึ่งจ่ายด้วยเงินกู้ → ไม่ยั่งยืนถ้าสต็อกยังขายไม่ออก','ที่มา: งบกระแสเงินสดรวม FY2021–FY2025 · DPS/EPS จากงบการเงินและหมายเหตุเงินปันผล · คำนวณโดยผู้จัดทำ','บทพูด: แท่งทองคือเงินสดจากการดำเนินงาน ต่ำกว่ากำไรทุกปี และติดลบในปี 2023 ถึง 2024 ห้าปีรวม CFO ได้ 7,265 ล้านบาท แต่จ่ายปันผลและซื้อหุ้นคืน 13,901 ล้านบาท ส่วนต่าง 6,636 ล้านบาทจึงมาจากเงินกู้ และสัดส่วนการจ่ายปันผลเพิ่มจาก 34% เป็น 60%\n\nตัวเลขจากงบกระแสเงินสด: เงินปันผลจ่าย 1,947.7 / 2,828.1 / 2,830.5 / 2,635.9 / 2,700.8 (รวม 12,943.0) · ซื้อหุ้นคืน 957.8 (ปี 2025) · รวม 13,900.8 · ส่วนต่าง 13,900.8 − 7,265 = 6,635.8 · แก้ไขจากฉบับก่อน: ฉบับก่อนนับซื้อหุ้นคืน 3,000 เป็นปี 2021 แต่งบ FY2021 แสดงว่าจ่ายในปี 2020 (นอกช่วง 5 ปี) ยอดจ่ายคืนจึงเป็น 13,901 ไม่ใช่ 16,901 · ปี 2022 มีเงินรับจากขายหุ้นซื้อคืน 102.4 (ไม่ได้หักออก) · CFO 4,009 / 3,270 / −180 / −687 / 853 · FCF 3,925 / 3,145 / −259 / −930 / 712 · Payout = DPS ÷ EPS 1.25/3.63 · 1.45/4.19 · 1.45/3.07 · 1.45/3.17 · 1.25/2.09',SPK2)

# ---------- 13 health
k=[('Revenue growth',[41.4,19.7,-10.4,0.5,-22.5],'+41.4%','−22.5%',1),('OPM',[29.7,29.3,24.8,25.8,20.6],'29.7%','20.6%',1),('NPM',[23.8,23.0,18.8,19.4,16.2],'23.8%','16.2%',1),('ROE',ROE,'16.8%','7.5%',1),('ROA',ROA,'9.9%','4.0%',1),('Current ratio',[2.74,2.49,2.86,2.44,2.66],'2.74','2.66',0),('D/E',[0.66,0.68,0.67,0.77,0.81],'0.66','0.81',1),('ND/EBITDA',[2.04,2.21,2.80,3.44,6.42],'2.04','6.42',1),('CFO/NP',[0.57,0.40,-0.03,-0.11,0.21],'0.57','0.21',1),('FCF',[3925,3145,-259,-930,712],'3,925','712',1)]
h=sec('health')+head('SUMMARY · FINANCIAL HEALTH','สุขภาพการเงิน: ยังไม่มีปัญหา แต่เกือบทุกตัวแย่ลง','Dashboard 2021 → 2025 · แท่งเล็ก = แนวโน้ม 5 ปี · กดเพื่อดูผลประเมิน 5 ด้าน')
h+='<div class="a1" style="display:grid; grid-template-columns:repeat(5, 1fr); gap:12px">\n'
for n_,vals,a,b,bad in k:
    col=RED if bad else BLUE
    h+=f'<div class="card" style="flex-direction:row; align-items:flex-end; justify-content:space-between; gap:8px; padding:12px 16px"><div><p class="lbl">{n_}</p><p class="txt w" style="font-weight:600">{a} → <span class="{"r" if bad else "b"}">{b}</span></p></div>{spark(vals,col)}</div>\n'
h+='</div>\n<div style="display:flex; gap:12px; align-items:stretch">\n'
for a,v,r,icn in [('ผลการดำเนินงาน','Vulnerable','รายได้ −22.5% · ROE 7.5%','Chart'),('ฐานะการเงิน','Stable/Mixed','D/E 0.81 แต่สต็อก 78%','Database'),('กระแสเงินสด','Vulnerable','CFO/NP 0.21 · ปันผลใช้เงินกู้','Activity'),('ความเสี่ยงหลัก','Vulnerable','ND/EBITDA 6.42','Warning'),('แนวโน้ม','Stable/Mixed','Presales ทรงตัว · JV ช่วย','Clock')]:
    vul=v=='Vulnerable'; band=RED if vul else GOLD
    h+=f'<div class="card fragment" style="flex:1; gap:8px; padding:0 0 16px 0; overflow:hidden"><div style="height:10px; background:{band}"></div><div style="display:flex; flex-direction:column; gap:8px; padding:4px 18px 0 18px">{ic(icn,"red" if vul else "goldt")}<p class="txt w" style="font-weight:600">{a}</p><p class="stamp {"r" if vul else "g"}">{v}</p><p class="lbl">{r}</p></div></div>\n'
h+='</div>\n'
h+=foot('ที่มา: สไลด์ 6–12 (งบรวม FY2021–FY2025, 9M26) · กรอบ Health Assessment จาก Workshop 2 · ผลประเมินเป็นความเห็นของผู้จัดทำ',13,SPK2+'บทพูด: แถวบนคือ Dashboard ตามที่โจทย์กำหนด แต่ละช่องมีกราฟแท่งเล็กแสดงแนวโน้มห้าปี ตัวสีแดงคือแย่ลง มีเพียง Current ratio ที่ทรงตัว ซึ่งเห็นแล้วว่าเพราะสต็อก แถวล่างคือการประเมินห้าด้าน (กดทีละใบ) ผลการดำเนินงาน กระแสเงินสด และความเสี่ยงหลักอยู่ในระดับ Vulnerable ฐานะการเงินและแนวโน้มอยู่ในระดับ Stable/Mixed สรุปคือยังไม่ใช่บริษัทที่มีปัญหา แต่ผลตอบแทนต่อเงินทุนลดลงและพึ่งหนี้มากขึ้น\n\nเกณฑ์ (ผู้จัดทำกำหนด): Vulnerable = แย่ลงชัดเจนและต่ำกว่าเกณฑ์ (ROE &lt; COE 10%, CFO/NP &lt; 0.5, ND/EBITDA &gt; 4) · Stable/Mixed = มีทั้งจุดแข็งและจุดอ่อน · Improving = ดีขึ้นต่อเนื่อง ไม่มีด้านใดเข้าเกณฑ์นี้')
P['health']=h

# ---------- 14 audit
h=sec('audit')+head('SUMMARY · RED FLAGS · AI AUDIT','Red flag 4 ข้อ · AI สรุปชวนเข้าใจผิด 3 ข้อ ผิด 1 ข้อ','ถาม AI ให้สรุปสุขภาพการเงิน SPALI แล้วตรวจกับงบจริง · กดเพื่อดูทีละข้อ')
h+='<div class="a1" style="display:flex; gap:12px">\n'
for k,(v,t) in enumerate([('3.27 ปี','สต็อกขายหมด (เดิม 2.15)'),('6.42×','ND/EBITDA'),('0.21','CFO ÷ กำไร'),('+7.6%','กำไร 9M26 จาก JV + ภาษี')]):
    h+=f'<div class="card pop" style="flex:1; flex-direction:row; align-items:center; gap:14px; padding:8px 18px; animation-delay:{0.2+k*0.12:.2f}s">{ic("Warning","red")}<div><p class="h3 r">{v}</p><p class="lbl">{t}</p></div></div>\n'
h+='</div>\n<div style="display:flex; flex-direction:column; gap:8px">\n'
G='grid-template-columns:1fr 1.25fr 220px 1.25fr'
h+=f'<div style="display:grid; {G}; gap:14px; background:#1E3A5F; border-radius:14px; padding:8px 20px">'+''.join(f'<p class="lbl on" style="font-weight:600">{x}</p>' for x in ['AI กล่าวว่า','หลักฐานจากงบ','ผลตรวจ','ข้อสรุปที่ถูกต้อง'])+'</div>\n'
for a,e,v,c in [('"สภาพคล่องดี Current ratio 2.66"','Quick 0.16 · เงินสด/หนี้ระยะสั้น 15%','MISLEADING','พึ่งการขายสต็อกและการกู้ใหม่'),('"กำไร 9M26 ฟื้นตัว +7.6%"','ธุรกิจหลัก −488 · JV +382 · ภาษี +321','MISLEADING','ธุรกิจหลักยังลดลง'),('"หนี้ต่ำ D/E 0.81"','ND/EBITDA 2.04 → 6.42','MISLEADING','หนี้เทียบความสามารถหาเงินสูงขึ้นมาก'),('"ปันผล 8% ปลอดภัย"','CFO 5 ปี 7,265 vs จ่ายคืน 13,901','INCORRECT','ปันผลส่วนหนึ่งมาจากเงินกู้ อาจถูกลด')]:
    h+=f'<div class="card fragment" style="display:grid; {G}; gap:14px; align-items:center; padding:6px 20px"><p class="ct m">{a}</p><p class="ct">{e}</p><p class="stamp {"r" if v=="INCORRECT" else "g"}">{v}</p><p class="ct w" style="font-weight:600">{c}</p></div>\n'
h+='</div>\n'
h+=take('ต้องการข้อมูลอะไรเพิ่มก่อนลงทุน? อัตราการปฏิเสธสินเชื่อ · อายุสต็อกบ้านสร้างเสร็จ · ตารางครบกำหนดหุ้นกู้ 2027','คำถามปิด')
h+=foot('ที่มา: งบรวม FY2021–FY2025 · 9M26 · MD&amp;A 3Q26 · ข้อความ "AI กล่าวว่า" มาจากการทดสอบของผู้จัดทำ',14,SPK2+'บทพูด: แถวบนคือ Red flag สี่ข้อ ด้านล่างคือ AI Audit (กดทีละแถว) สามข้อ AI ใช้ตัวเลขถูกแต่สรุปชวนเข้าใจผิด เพราะดูตัวชี้วัดเดียวโดยไม่ดูบริบทของธุรกิจอสังหาฯ อีกข้อผิด คือบอกว่าปันผลปลอดภัย ทั้งที่ห้าปี CFO ได้ 7,265 แต่จ่ายคืนผู้ถือหุ้น 13,901 ล้านบาท ปิดด้วยคำถามของโจทย์ ข้อมูลที่ต้องการเพิ่มคือ อัตราการปฏิเสธสินเชื่อ อายุสต็อกบ้านสร้างเสร็จ และตารางครบกำหนดหุ้นกู้\n\nหมายเหตุสำหรับผู้นำเสนอ: ตรวจว่าข้อความในคอลัมน์ AI กล่าวว่า ตรงกับคำตอบจริงที่ได้จาก AI ที่ทดสอบ และเก็บภาพหน้าจอเป็นหลักฐาน')
P['audit']=h

# ---------- 15 value (corrected BVPS 27.51)
h=sec('value')+head('VALUATION · MARGIN OF SAFETY','ราคา 15.40 เกินมูลค่ากลาง 14.89 → ยังไม่มีส่วนเผื่อ','มูลค่า = เฉลี่ย P/E, P/BV, DDM · COE 10% · สมมติฐานของผู้จัดทำ · ราคา 17 พ.ย. 2026')
h+='<div class="a1" style="display:grid; grid-template-columns:repeat(5, 1fr); gap:14px">\n'
for k,(a,b) in enumerate([('ราคาปิด','15.40'),('P/E (SET)','6.94 เท่า'),('P/BV (SET)','0.52 เท่า'),('อัตราปันผล','8.12%'),('ช่วง 52 สัปดาห์','14.80–19.00')]):
    h+=f'<div class="card pop" style="gap:0px; padding:12px 20px; animation-delay:{0.1+k*0.08:.2f}s"><p class="lbl">{a}</p><p class="h3 nv">{b}</p></div>\n'
h+='</div>\n'
def X(v): return int(60+(v-10)*150)
sc='<div class="host" style="width:1600px; height:250px">\n'
sc+=f'<div class="hb" style="position:absolute; left:{X(11.35)}px; top:96px; width:{X(18.45)-X(11.35)}px; height:52px; background:#DCE7F4; border-radius:26px"></div>\n'
sc+=f'<div style="position:absolute; left:{X(10)}px; top:121px; width:{X(20)-X(10)}px; height:2px; background:#C9D2DD"></div>\n'
for t in range(10,21,2):
    sc+=f'<p class="cap" style="position:absolute; left:{X(t)-30}px; top:226px; width:60px; text-align:center">{t}</p>\n'
for v,l,c,p,cl in [(11.35,'Bear 11.35',BLUE,'up',''),(11.91,'ซื้อได้ ≤ 11.91','#9C6A10','dn',''),(14.89,'Base 14.89',NAVY,'up',''),(15.40,'ราคา 15.40',RED,'dn','pulse'),(16.80,'Finansia 16.80',LB,'up2',''),(17.50,'KKPS 17.50',LB,'up',''),(18.45,'Bull 18.45',BLUE,'dn',''),(19.00,'InnovestX 19.00',LB,'up2','')]:
    x=X(v)
    if cl=='pulse':
        sc+=f'<div class="pulse" style="position:absolute; left:{x-14}px; top:108px; width:28px; height:28px; border-radius:50%; background:{c}"></div>\n'
    else:
        sc+=f'<div style="position:absolute; left:{x-4}px; top:84px; width:8px; height:76px; background:{c}; border-radius:4px"></div>\n'
    top={'up':44,'up2':6,'dn':166}[p]
    sc+=f'<p class="vl fd" style="left:{x-110}px; top:{top}px; width:220px; font-weight:600; color:{c}">{l}</p>\n'
sc+='</div>\n'
h+=f'<div class="chart a2" style="padding:14px 28px; gap:2px"><p class="lbl w" style="font-weight:600">ช่วงมูลค่า Bear–Bull (แถบฟ้า) · ราคาเป้าหมายนักวิเคราะห์ (ความเห็นรอง) · บาทต่อหุ้น</p>\n{sc}</div>\n'
h+=take('Margin of Safety 20% → ราคาที่ควรซื้อ ≤ 11.91 บาท · หุ้นดูถูกเพราะ ROE ต่ำกว่า COE ไม่ใช่เพราะตลาดประเมินผิด','มูลค่า')
h+=foot('ที่มา: SET (ราคา P/E P/BV อัตราปันผล 17 พ.ย. 2026) · InnovestX · KKPS · Finansia Syrus · รายละเอียดในสไลด์สำรอง B2',15,SPK2+'บทพูด: ราคาปิด 15.40 บาท P/E 6.94 เท่า P/BV 0.52 เท่า ปันผล 8.12% ดูถูกในเชิงตัวเลข เราประเมินมูลค่าสามวิธีแล้วเฉลี่ยได้ 14.89 บาทในกรณีฐาน ช่วงขาลงถึงขาขึ้น 11.35 ถึง 18.45 บาท ราคาตลาดจึงสูงกว่ามูลค่ากลางเล็กน้อย ถ้าต้องการส่วนเผื่อความปลอดภัย 20% ราคาที่ควรซื้อคือไม่เกิน 11.91 บาท ราคาเป้าหมายโบรกเกอร์ 16.80 ถึง 19.00 บาท ใช้เป็นความเห็นรอง\n\nแก้ไขจากฉบับก่อน: BVPS เดิม 29.41 คำนวณจากส่วนของผู้ถือหุ้น 57,440 ซึ่งไม่ตรงกับงบ งบ FY2025 แสดงส่วนผู้ถือหุ้นบริษัทใหญ่ 53,728.3 → BVPS 27.51 (บน 1,953.05 ล้านหุ้น) · P/BV value 12.38 / 15.13 / 17.88 · เฉลี่ย Bear (11.67 + 12.38 + 10.00) ÷ 3 = 11.35 · Base (16.64 + 15.13 + 12.91) ÷ 3 = 14.89 · Bull (21.52 + 17.88 + 15.94) ÷ 3 = 18.45 · MoS 14.89 × 0.8 = 11.91 · P/BV 0.52 เท่าเป็นค่าที่ SET รายงาน (ฐานข้อมูลต่างจากการคำนวณของผู้จัดทำ) · ไม่ใช่คำแนะนำซื้อขาย')
P['value']=h

# ---------- 16 answer
h=sec('answer')+head('CONCLUSION · ตอบ 3 คำถาม','บริษัทดี แต่การเงินอ่อนลง และราคายังไม่ถูกพอ','สรุปจากงบ 5 ปี และมูลค่า · เพื่อการศึกษา ไม่ใช่คำแนะนำซื้อขาย')
h+='<div style="display:flex; gap:20px; align-items:stretch">\n'
for k,(icn,q,a,e,c,cls) in enumerate([('Trust','ธุรกิจดีไหม?','ดี','แบรนด์ 36 ปี · 414 โครงการ · NPM 16.2% · JV ออสเตรเลีย','b','blue'),('Activity','การเงินแข็งแรงไหม?','พอใช้ อ่อนลง','ROE 17.6% → 7.5% · สต็อก 3.27 ปี · ND/EBITDA 6.42','g','goldt'),('Search','ราคาน่าซื้อไหม?','ยังไม่ใช่','ราคา 15.40 > มูลค่า 14.89 · รอ ≤ 11.91 หรือรอให้สต็อกลด','r','red')]):
    h+=f'<div class="card pop" style="flex:1; gap:16px; padding:40px 32px; animation-delay:{0.2+k*0.2:.1f}s"><div class="thead">{ic(icn,cls)}<p class="txt m" style="font-weight:600">{k+1} · {q}</p></div><p class="kpi {c}" style="font-size:80px">{a}</p><p class="txt">{e}</p></div>\n'
h+='</div>\n<div class="a3" style="display:flex; gap:20px; align-items:stretch">\n'
h+=f'<div class="card deep" style="flex:1.4; flex-direction:row; align-items:center; gap:24px; padding:18px 30px"><p class="ans gl">บริษัทดี ≠ หุ้นน่าซื้อ</p><p class="lbl onm">ติดตาม: Presales · สต็อก · CFO · หุ้นกู้ครบกำหนด</p></div>\n'
h+='<div class="card focus pulse" style="flex:0.6; align-items:center; justify-content:center; padding:18px"><p class="h3 nv">ถาม–ตอบ</p><p class="lbl">ขอบคุณครับ</p></div>\n</div>\n'
h+=foot('ที่มา: สไลด์ 2–15 · ผลประเมินเป็นความเห็นของผู้จัดทำ · เพื่อการศึกษา ไม่ใช่คำแนะนำซื้อขาย',16,SPK2+'บทพูด: ตอบสามคำถามหลัก ข้อแรก ธุรกิจดี แบรนด์ 36 ปี ยังทำกำไรได้ และมีรายได้จากออสเตรเลียช่วย ข้อสอง การเงินพอใช้แต่อ่อนลง ROE ลดจาก 17.6% เหลือ 7.5% สต็อกต้องใช้กว่าสามปีจึงขายหมด และหนี้เทียบ EBITDA สูงขึ้นเป็น 6.42 เท่า ข้อสาม ราคายังไม่น่าซื้อ ราคาตลาดสูงกว่ามูลค่ากลาง 14.89 บาทเล็กน้อย เราจะรอที่ไม่เกิน 11.91 บาท หรือรอให้สต็อกลดลงและ CFO ฟื้น บริษัทดีไม่ได้แปลว่าหุ้นน่าซื้อ ขอบคุณครับ ยินดีรับคำถาม')
P['answer']=h

# ---------- B1
L=[('Revenue growth','ปีนี้ ÷ ปีก่อน − 1','24,772 ÷ 31,985 = −22.5%'),('GPM','กำไรขั้นต้น ÷ รายได้ขาย','34%'),('OPM','EBIT ไม่รวม JV ÷ รายได้รวม','5,115 ÷ 24,772 = 20.6%'),('NPM','กำไรสุทธิ ÷ รายได้รวม','4,015 ÷ 24,772 = 16.2%'),('ROE','กำไรสุทธิ ÷ ส่วนทุนบริษัทใหญ่','4,015 ÷ 53,728 = 7.5%'),('ROA','กำไรสุทธิ ÷ สินทรัพย์รวม','4,015 ÷ 99,285 = 4.0%'),('Asset turnover','รายได้รวม ÷ สินทรัพย์รวม','24,772 ÷ 99,285 = 0.25'),('Equity multiplier','สินทรัพย์ ÷ ส่วนทุนบริษัทใหญ่','99,285 ÷ 53,728 = 1.85'),('ปีที่ขายสต็อกหมด','สต็อก ÷ รายได้ขายอสังหาฯ','77,448 ÷ 23,714 = 3.27')]
R_=[('Current ratio','สินทรัพย์ ÷ หนี้สิน หมุนเวียน','82,370 ÷ 31,007 = 2.66'),('Quick ratio','(สินทรัพย์หมุนเวียน − สต็อก) ÷ หนี้สินหมุนเวียน','4,922 ÷ 31,007 = 0.16'),('เงินสด/หนี้ระยะสั้น','เงินสด ÷ หนี้ถึงกำหนดใน 1 ปี','3,788 ÷ 25,246 = 15.0%'),('D/E','หนี้สินรวม ÷ ส่วนผู้ถือหุ้นรวม','44,499 ÷ 54,786 = 0.81'),('Net gearing','(หนี้มีดอกเบี้ย − เงินสด) ÷ ส่วนผู้ถือหุ้นรวม','34,200 ÷ 54,786 = 0.62'),('ND/EBITDA','หนี้สุทธิ ÷ (EBIT ไม่รวม JV + ค่าเสื่อม)','34,200 ÷ 5,328.2 = 6.42'),('ICR','(EBT + ต้นทุนการเงิน) ÷ ต้นทุนการเงิน','5,845 ÷ 725 = 8.1'),('FCF','CFO − รายจ่ายลงทุน','853 − 141 = 712'),('Payout ratio','DPS ÷ EPS','1.25 ÷ 2.09 = 60%')]
def ft(rows):
    o='<table class="tb" style="font-size:24px; flex:1">\n<tr class="th"><th style="width:26%">ตัวชี้วัด</th><th>สูตร</th><th style="width:36%">ปี 2025</th></tr>\n'
    for r,(a,b,c) in enumerate(rows): o+=f'<tr{" class=\"z\"" if r%2 else ""}><td style="font-weight:600; padding:6px 12px">{a}</td><td style="padding:6px 12px">{b}</td><td style="padding:6px 12px">{c}</td></tr>\n'
    return o+'</table>\n'
h=sec('b1')+head('BACKUP B1 · สำหรับตอบคำถาม','สูตรและตัวอย่างการคำนวณปี 2025 ของทุกตัวชี้วัด','งบการเงินรวม · ล้านบาท · ยอดปลายปี','tag bk')
h+='<div class="a1" style="display:flex; gap:24px; align-items:flex-start">\n'+ft(L)+ft(R_)+'</div>\n'
h+=foot('ที่มา: FS FY2024–FY2025 งบรวม (EY) · ส่วนผู้ถือหุ้นบริษัทใหญ่ 53,728.3 + NCI 1,057.5 = ส่วนผู้ถือหุ้นรวม 54,785.8','B1','สไลด์สำรอง ใช้ตอบเมื่อถูกถามว่าตัวเลขคำนวณอย่างไร · ROE และ EM ใช้ส่วนผู้ถือหุ้นบริษัทใหญ่ ให้สอดคล้องกับกำไรส่วนบริษัทใหญ่ · D/E และ Net gearing ใช้ส่วนผู้ถือหุ้นรวม · ICR: กำไรก่อนภาษี 5,120.7 + ต้นทุนการเงิน 724.6 = 5,845.3 · รายจ่ายลงทุน 2025 = 63.3 + 34.3 + 43.7 = 141.3 · EBITDA 2025 = 5,114.9 + 213.3 = 5,328.2')
P['b1']=h

# ---------- B2 corrected
h=sec('b2')+'<div class="corner"></div>\n'+head('BACKUP B2 · สำหรับตอบคำถาม','รายละเอียดการประเมินมูลค่า 3 วิธี × 3 กรณี','บาทต่อหุ้น · EPS และ BVPS บน 1,953.05 ล้านหุ้น · BVPS 27.51 · COE 10% · สมมติฐานของผู้จัดทำ','tag bk')
rows=[('กำไร FY26E (ล้านบาท)','3,800','4,220','4,333',''),('EPS FY26E','1.95','2.16','2.22','z'),('P/E (ตัวคูณ)','11.67 (6.0 เท่า)','16.64 (7.7 เท่า)','21.52 (9.7 เท่า)',''),('P/BV (ตัวคูณ)','12.38 (0.45 เท่า)','15.13 (0.55 เท่า)','17.88 (0.65 เท่า)','z'),('DDM (DPS, g)','10.00 (1.00, 0%)','12.91 (1.15, 1%)','15.94 (1.25, 2%)',''),('ค่าเฉลี่ย 3 วิธี','11.35','14.89','18.45','hi'),('เทียบราคา 15.40','<span class="r">−26.3%</span>','<span class="r">−3.3%</span>','<span class="b">+19.8%</span>','')]
t='<table class="tb a1">\n<tr class="th"><th style="width:26%">วิธี / สมมติฐาน</th><th class="n">Bear</th><th class="n">Base</th><th class="n">Bull</th></tr>\n'
for a,b,c,d,z in rows: t+=f'<tr{f" class=\"{z}\"" if z else ""}><td>{a}</td><td class="n">{b}</td><td class="n">{c}</td><td class="n">{d}</td></tr>\n'
h+=t+'</table>\n'
h+=foot('P/E 7.7 = เฉลี่ยกลุ่ม · 9.7 = เฉลี่ยระยะยาว · DDM = DPS × (1 + g) ÷ (10% − g) · BVPS = ส่วนผู้ถือหุ้นบริษัทใหญ่ 53,728 ÷ 1,953.05 ล้านหุ้น','B2','สไลด์สำรอง ใช้ตอบเมื่อถูกถามว่ามูลค่า 14.89 บาทมาจากไหน ตัวคูณและอัตราเติบโตเป็นสมมติฐานของผู้วิเคราะห์ ค่าเฉลี่ย P/E 2025A ของกลุ่ม = (5.9 + 11.3 + 8.4 + 5.5 + 7.6) ÷ 5 = 7.74 (AP, LH, QH, SIRI, SPALI ตาม InnovestX 10 พ.ย. 2026) · แก้ไขจากฉบับก่อน: BVPS เดิม 29.41 ใช้ส่วนผู้ถือหุ้น 57,440 ซึ่งไม่ตรงกับงบ งบ FY2025 แสดงส่วนผู้ถือหุ้นบริษัทใหญ่ 53,728.3 (รวม NCI = 54,785.8) จึงใช้ BVPS 27.51 · P/E ของ SET 6.94 ใช้ 1,902.05 ล้านหุ้น การประเมินใช้ 1,953.05 ล้านหุ้นซึ่งรวมหุ้นซื้อคืน 51 ล้านหุ้น (ประมาณการแบบระมัดระวัง) · เป้านักวิเคราะห์: InnovestX 19.00 · KKPS 17.50 · Finansia Syrus 16.80 · กำไร Bull = ประมาณการ InnovestX · ไม่ใช่คำแนะนำซื้อขาย')
P['b2']=h

# ---------- B3
h=sec('b3')+head('BACKUP B3 · งบย่อ 5 ปี','ตัวเลขหลักจากงบการเงินรวม 2021–2025','ล้านบาท ยกเว้นระบุ · กำไร = ส่วนของบริษัทใหญ่','tag bk')
rows=[['รายได้รวม','29,647','35,501','31,818','31,985','24,772'],['กำไรสุทธิ','7,070','8,173','5,989','6,190','4,015'],['สินทรัพย์รวม','71,432','79,924','86,126','96,231','99,285'],['สต็อกโครงการ','62,104','65,675','71,125','74,641','77,448'],['หนี้สินรวม','28,506','32,461','34,661','42,011','44,499'],['หนี้ที่มีดอกเบี้ย','19,890','24,536','27,164','34,187','37,988'],['ส่วนผู้ถือหุ้นบริษัทใหญ่','42,070','46,514','50,475','53,176','53,728'],['ส่วนผู้ถือหุ้นรวม (รวม NCI)','42,926','47,463','51,465','54,220','54,786'],['CFO','4,009','3,270','−180','−687','853'],['ปันผลจ่าย (งบกระแสเงินสด)','1,948','2,828','2,831','2,636','2,701'],['EPS / DPS (บาท)','3.63 / 1.25','4.19 / 1.45','3.07 / 1.45','3.17 / 1.45','2.09 / 1.25']]
t='<table class="tb a1" style="font-size:24px">\n<tr class="th"><th style="width:28%">รายการ</th>'+''.join(f'<th class="n">{y_}</th>' for y_ in YRS)+'</tr>\n'
for r,row in enumerate(rows): t+=f'<tr{" class=\"z\"" if r%2 else ""}><td style="padding:5px 12px">{row[0]}</td>'+''.join(f'<td class="n" style="padding:5px 12px">{c}</td>' for c in row[1:])+'</tr>\n'
h+=t+'</table>\n'
h+=foot('ที่มา: งบการเงินรวม FY2021–FY2025 (EY) · ปี 2022 จากตัวเลขเปรียบเทียบใน FS FY2023 · ซื้อหุ้นคืน 957.8 ในปี 2025','B3','สไลด์สำรอง ใช้ตอบเมื่อถูกถามตัวเลขดิบ · A = L + E ตรงทุกปี เช่น 2025: 44,499 + 54,786 = 99,285 · ส่วนผู้ถือหุ้นบริษัทใหญ่จากงบแสดงฐานะการเงิน: 42,069.6 (2021) · 46,514.3 (2022) · 50,475.1 (2023) · 53,175.6 (2024) · 53,728.3 (2025) · ซื้อหุ้นคืน 3,000 ล้านบาทเกิดในปี 2020 (นอกช่วงวิเคราะห์) · ปี 2022 ขายหุ้นซื้อคืนได้ 102.4')
P['b3']=h



# ---------- peers (FY2025, company filings)
PEERS={'SPALI':(-22.5,16.2,7.5,0.81),'AP':(1.0,11.6,9.4,0.86),'LH':(-17.6,16.0,7.2,1.68),'QH':(-9.4,21.9,5.7,0.39),'SIRI':(-12.3,13.1,9.1,1.90)}
def pchart(title,idx,fmtf,asc,rank,good,delay):
    rows=sorted(PEERS.items(),key=lambda kv:kv[1][idx],reverse=not asc)
    mx=max(abs(v[idx]) for v in PEERS.values())
    o=f'<div class="card pop" style="flex:1; gap:10px; padding:20px 22px; animation-delay:{delay}s"><p class="lbl w" style="font-weight:600">{title}</p>'
    for k,(n,v) in enumerate(rows):
        val=v[idx]; sp=n=='SPALI'
        col=GOLD if sp else ('#E7B9B6' if val<0 else '#A9BBD1')
        w=max(4,int(abs(val)/mx*100))
        o+=f'<div style="display:flex; align-items:center; gap:10px"><p class="lbl {"g" if sp else "m"}" style="width:70px; font-weight:{600 if sp else 400}">{n}</p><div style="flex:1; height:30px"><div class="hb" style="width:{w}%; height:30px; background:{col}; border-radius:8px; animation-delay:{delay+0.2+k*0.12:.2f}s"></div></div><p class="lbl {"r" if val<0 else "w"}" style="width:100px; text-align:right; white-space:nowrap; font-weight:{600 if sp else 400}">{fmtf(val)}</p></div>'
    o+=f'<p class="pill {"gold" if good else "red"}" style="align-self:flex-start">SPALI อันดับ {rank}/5</p></div>\n'
    return o
h=sec('peers')+head('ANALYSIS · เทียบคู่แข่ง','กำไรต่อยอดขายและหนี้ดีกว่ากลุ่ม แต่รายได้หดตัวแรงที่สุด','งบการเงินรวมปี 2025 ของผู้พัฒนาอสังหาฯ รายใหญ่ 5 ราย · แถบทอง = SPALI')
h+='<div style="display:flex; gap:16px; align-items:stretch">\n'
h+=pchart('รายได้เติบโต 2025',0,lambda v:fmt(v,'{:.1f}%') if v<0 else f'+{v:.1f}%',False,5,False,0.2)
h+=pchart('อัตรากำไรสุทธิ (NPM)',1,lambda v:f'{v:.1f}%',False,2,True,0.4)
h+=pchart('ROE (ส่วนทุนบริษัทใหญ่)',2,lambda v:f'{v:.1f}%',False,3,True,0.6)
h+=pchart('D/E (ต่ำ = ดี)',3,lambda v:f'{v:.2f}',True,2,True,0.8)
h+='</div>\n<div class="card a3" style="flex-direction:row; align-items:center; gap:14px; padding:12px 24px">'+ic('Chart','goldt')+'<p class="lbl w" style="font-weight:600">P/E 2025A (InnovestX):</p><p class="lbl">AP 5.9 · LH 11.3 · QH 8.4 · SIRI 5.5 · <span class="g" style="font-weight:600">SPALI 7.6</span> · เฉลี่ยกลุ่ม 7.7 เท่า</p></div>\n'
h+=take('ปัญหาของ SPALI ไม่ใช่ความสามารถทำกำไร แต่เป็นยอดโอนที่หดตัวแรงกว่าคู่แข่ง')
h+=foot('ที่มา: งบการเงินรวมและ 56-1 ปี 2025 ของทั้ง 5 บริษัท · D/E = หนี้สินรวม ÷ ส่วนทุนรวม · คำนวณโดยผู้จัดทำ',12,'(ล้านบาท, ปี 2025): SPALI รายได้ 24,772 (−22.5%) กำไร 4,015 ส่วนทุนบริษัทใหญ่ 53,728 หนี้สิน 44,499 ส่วนทุนรวม 54,786 · AP รายได้รวม 37,345 (+1.0%) กำไร 4,316.7 ส่วนทุน 46,093.6 หนี้สิน 39,583.6 สินทรัพย์ 85,661.3 (AP IR, SET snapshot) · LH รายได้รวม 23,200 (2024: 28,151 → −17.6%) กำไร 3,716.2 ส่วนทุนบริษัทใหญ่ 51,881.8 หนี้สิน 88,372.7 ส่วนทุนรวม 52,629.5 (LH 56-1 2025) · QH รายได้รวม 7,882 (2024: 8,695 → −9.4%) กำไร 1,728 ส่วนทุน 30,238 หนี้สิน 11,841 (QH 56-1 2025) · SIRI รายได้รวม 34,395 (−12.3%) กำไร 4,513.3 ส่วนทุนบริษัทใหญ่ 49,465.0 หนี้สิน 95,343.1 สินทรัพย์ 145,404.9 (SIRI MD&amp;A, SET snapshot) · NPM = กำไร ÷ รายได้รวมที่บริษัทรายงาน นิยามรายได้รวมของแต่ละบริษัทอาจต่างกันเล็กน้อย · P/E 2025A จาก InnovestX (10 พ.ย. 2026) เป็นความเห็นรอง')
P['peers']=h
open(f'{S}/peers.html','w',encoding='utf-8').write(h)
for i in ['history','biz','cycle','grow','margin','roe','stock','liq','debt','cash','health','audit','value','answer']:
    open(f'{S}/{i}.html','w',encoding='utf-8').write(P[i])
print('peers ok')
