import json,re,os,shutil
D='deck/project'; OUT=__import__('os').environ.get('OUT_DIR','./web')
os.makedirs(OUT+'/img',exist_ok=True)
blobs={'69437991d53f7b2cd64e09d2b9821710':'skyline.jpg','34e58fb1565555fad2c1e71553be81a2':'aerial.jpg','a93153eec78251b017ef7f982a1b0ea2':'palmsprings.png','2f65fe8ca78b06cceabbad6ea4f40821':'riverside.jpg','cd428642351af1bdc08dd0c167549940':'newspaper.jpg','3da0eaac4f725992f135081b2c4acb35':'night.jpg','d0dd2e4e2db2d5d05f01a9814648d765':'candlestick.png','43d3c817225c6800925fbb9231d7ed79':'palm_cut.png','3e749685d1373fdd50626739300f7714':'aerial_crop.jpg','cd9d1b2bae8833eb533ea17611150bb3':'skyline_crop.jpg','fe38f7919f029fb7ede6c3c9feb10ba4':'night_crop.jpg','51a53875f4a09458d2d7e4b517ae4a5e':'news_crop.jpg','d235ecb2b1986d2a650bc74a1e60bf3b':'river_crop.jpg','4e815f3caddf2f30b44128f67cd87618':'palm_fade.png','0e8dd132b3750405af9e704535c45cdd':'palm_full.jpg'}
d=json.load(open(D+'/deck.json')); secs=[]
used=set()
for i in d['order']:
    s=open(f'{D}/slides/{i}.html',encoding='utf-8').read()
    def rep(m):
        f=blobs[m.group(1)]; used.add(f); return 'img/'+f
    s=re.sub(r'/_blob/([0-9a-f]{32})',rep,s)
    secs.append(s)
for f in used: shutil.copy('assets/'+f,OUT+'/img/'+f)
css=open(D+'/deck.css',encoding='utf-8').read()
icons=open('pv/icons.css',encoding='utf-8').read()
fonts=''.join(f'<link rel="stylesheet" href="{v["href"]}">' for v in d['faces'].values())
base='''* { margin: 0 } html,body{height:100%;background:#0E1A2B;overflow:hidden}
body { font: 32px/1.2 sans-serif }
#stage{position:fixed;left:50%;top:50%;width:1920px;height:1080px;transform-origin:0 0}
#stage > section { position:absolute; left:0; top:0; width: 1920px; height: 1080px; overflow: hidden; box-sizing: border-box; isolation: isolate; display:none }
#stage > section.is-cur { display:flex }
aside, noscript { display: none !important }
h1 { font-size: 96px; font-weight: 600 } h2 { font-size: 64px; font-weight: 600 } h3 { font-size: 44px; font-weight: 600 }
table { width: 100%; border-collapse: separate; border-spacing: 0; border: solid #0003; border-width: 2px 0 0 2px }
th, td { padding: .35em .6em; text-align: left; border: solid #0003; border-width: 0 2px 2px 0 }
x-shape, x-embed { display: block } x-icon{display:block}
.ic x-icon{width:30px;height:30px} .circ x-icon{width:44px;height:44px}
x-shape[kind=arrow-right]{clip-path:polygon(0 30%,60% 30%,60% 0,100% 50%,60% 100%,60% 70%,0 70%)}
#bar{position:fixed;left:0;bottom:0;height:4px;background:#E2B04A;transition:width .4s;z-index:9}
#hud{position:fixed;right:14px;bottom:12px;font:14px/1 sans-serif;color:#C9D4E2;opacity:.7;z-index:9;user-select:none}
#hint{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:rgba(14,26,43,.85);color:#F3F1EC;font:15px/1.4 sans-serif;padding:10px 18px;border-radius:20px;z-index:10;transition:opacity .6s}
#notes{position:fixed;left:0;right:0;bottom:0;max-height:38%;overflow:auto;background:rgba(14,26,43,.95);color:#F3F1EC;font:17px/1.6 sans-serif;padding:16px 24px;white-space:pre-wrap;display:none;z-index:11}
.nav{position:fixed;top:0;bottom:0;width:18%;z-index:8;cursor:pointer}
#prev{left:0} #next{right:0;width:82%}
'''
js='''
const S=[...document.querySelectorAll('#stage>section')];let i=0;
const st=document.getElementById('stage');
function fit(){const k=Math.min(innerWidth/1920,innerHeight/1080);st.style.transform=`scale(${k}) translate(-50%,-50%)`;st.style.transformOrigin='0 0';st.style.left='50%';st.style.top='50%';st.style.transform=`translate(-50%,-50%) scale(${k})`;st.style.transformOrigin='center center'}
addEventListener('resize',fit);fit();
function show(n,back){S.forEach(s=>s.classList.remove('is-cur'));i=Math.max(0,Math.min(S.length-1,n));const s=S[i];
 s.querySelectorAll('.fragment').forEach(f=>f.classList.toggle('visible',!!back));void s.offsetWidth;s.classList.add('is-cur');
 document.getElementById('bar').style.width=((i+1)/S.length*100)+'%';document.getElementById('hud').textContent=(i+1)+' / '+S.length;
 const a=s.querySelector('aside');document.getElementById('notes').textContent=a?a.textContent:'';history.replaceState(null,'','#'+(i+1))}
function next(){const f=S[i].querySelector('.fragment:not(.visible)');if(f){f.classList.add('visible');return}if(i<S.length-1)show(i+1)}
function prev(){const v=[...S[i].querySelectorAll('.fragment.visible')];if(v.length){v[v.length-1].classList.remove('visible');return}if(i>0)show(i-1,true)}
addEventListener('keydown',e=>{if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();next()}
 else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(e.key)){e.preventDefault();prev()}
 else if(e.key==='Home')show(0);else if(e.key==='End')show(S.length-1,true);
 else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
 else if(e.key==='n'||e.key==='N'){const n=document.getElementById('notes');n.style.display=n.style.display==='block'?'none':'block'}});
document.getElementById('next').onclick=next;document.getElementById('prev').onclick=prev;
let tx=null;addEventListener('touchstart',e=>tx=e.touches[0].clientX,{passive:true});
addEventListener('touchend',e=>{if(tx===null)return;const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>50){dx<0?next():prev()}tx=null});
setTimeout(()=>document.getElementById('hint').style.opacity=0,5000);
document.fonts&&document.fonts.ready.then(()=>{});
show((parseInt(location.hash.slice(1))||1)-1);
'''
html=f'''<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SPALI วิเคราะห์งบการเงิน 5 ปี</title>{fonts}
<style>{base}</style><style>{css}</style><style>{icons}</style></head><body>
<div id="stage">
{chr(10).join(secs)}
</div>
<div class="nav" id="prev"></div><div class="nav" id="next"></div>
<div id="bar"></div><div id="hud"></div><div id="notes"></div>
<div id="hint">คลิก / แตะ / ปุ่มลูกศร = ถัดไป · F = เต็มจอ · N = บทพูด</div>
<script>{js}</script></body></html>'''
open(OUT+'/index.html','w',encoding='utf-8').write(html)
print(len(html)//1024,'KB',sorted(used))
