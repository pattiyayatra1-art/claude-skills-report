const {chromium}=require('/opt/node-tools/node_modules/playwright');
const fs=require('fs'),path=require('path');
const [,,root,out,...only]=process.argv;
const deck=JSON.parse(fs.readFileSync(root+'/project/deck.json'));
const blobs={'69437991d53f7b2cd64e09d2b9821710':'skyline.jpg','34e58fb1565555fad2c1e71553be81a2':'aerial.jpg','a93153eec78251b017ef7f982a1b0ea2':'palmsprings.png','2f65fe8ca78b06cceabbad6ea4f40821':'riverside.jpg','cd428642351af1bdc08dd0c167549940':'newspaper.jpg','3da0eaac4f725992f135081b2c4acb35':'night.jpg','d0dd2e4e2db2d5d05f01a9814648d765':'candlestick.png','43d3c817225c6800925fbb9231d7ed79':'palm_cut.png','3e749685d1373fdd50626739300f7714':'aerial_crop.jpg','cd9d1b2bae8833eb533ea17611150bb3':'skyline_crop.jpg','fe38f7919f029fb7ede6c3c9feb10ba4':'night_crop.jpg','51a53875f4a09458d2d7e4b517ae4a5e':'news_crop.jpg','d235ecb2b1986d2a650bc74a1e60bf3b':'river_crop.jpg','4e815f3caddf2f30b44128f67cd87618':'palm_fade.png','0e8dd132b3750405af9e704535c45cdd':'palm_full.jpg'};
const ids=deck.order.filter(i=>fs.existsSync(`${root}/project/slides/${i}.html`)&&(!only.length||only.includes(i)));
const css=`* { margin: 0 } body { font: 32px/1.2 sans-serif }
body > section { width: 1920px !important; height: 1080px !important; overflow: hidden !important; box-sizing: border-box !important; position: relative; isolation: isolate }
section[hidden], aside, noscript { display: none !important }
h1 { font-size: 96px; font-weight: 600 } h2 { font-size: 64px; font-weight: 600 } h3 { font-size: 44px; font-weight: 600 }
p, li, h1, h2, h3, td, th { overflow-wrap: break-word; text-wrap: pretty }
table { width: 100%; border-collapse: separate; border-spacing: 0; border: solid #0003; border-width: 2px 0 0 2px }
th, td { padding: .35em .6em; text-align: left; border: solid #0003; border-width: 0 2px 2px 0 }
x-shape, x-icon, x-embed { display: block } x-shape{background:#888} .fragment{opacity:1 !important; transform:none !important} x-shape[kind=arrow-right]{clip-path:polygon(0 30%,60% 30%,60% 0,100% 50%,60% 100%,60% 70%,0 70%)} x-icon{display:block !important} .ic x-icon{width:30px;height:30px} .circ x-icon{width:44px;height:44px} ${require('fs').readFileSync(__dirname+'/icons.css','utf8')}`;
const links=Object.values(deck.faces).map(f=>`<link rel="stylesheet" href="${f.href}">`).join('');
const html=`<!doctype html><html><head><meta charset="utf-8">${links}<style>${css}</style><link rel="stylesheet" href="/project/deck.css"></head><body>${ids.map(i=>fs.readFileSync(`${root}/project/slides/${i}.html`,'utf8')).join('\n')}</body></html>`;
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:+(process.env.DSF||1),javaScriptEnabled:false});const p=await ctx.newPage();
await p.route('**/*',r=>{const u=new URL(r.request().url());
 if(u.host==='deck.local'&&u.pathname==='/') return r.fulfill({body:html,contentType:'text/html'});
 if(u.host==='deck.local'&&u.pathname==='/project/deck.css') return r.fulfill({body:fs.readFileSync(root+'/project/deck.css'),contentType:'text/css'});
 if(u.host==='deck.local'&&u.pathname==='/icons.woff2') return r.fulfill({body:fs.readFileSync(__dirname+'/icons.woff2'),contentType:'font/woff2'});
 if(u.host==='deck.local'&&u.pathname.startsWith('/_blob/')) return r.fulfill({body:fs.readFileSync(path.join(process.env.ASSETS,blobs[u.pathname.slice(7)])),contentType:'image/jpeg'});
 if(u.host.endsWith('googleapis.com')||u.host.endsWith('gstatic.com')) return r.continue();
 return r.abort('aborted');});
await p.goto('http://deck.local/');await p.waitForTimeout(2500);
const secs=await p.$$('body > section');
for(let k=0;k<secs.length;k++){await secs[k].scrollIntoViewIfNeeded();await p.waitForTimeout(150);await secs[k].screenshot({path:`${out}/${String(deck.order.indexOf(ids[k])+1).padStart(2,'0')}-${ids[k]}.png`,animations:'disabled'});}
const rep=await p.evaluate(()=>[...document.querySelectorAll('body>section')].map(s=>{const sr=s.getBoundingClientRect();const bad=[];const skip=['bleed','half-photo','cut','cut-line','pg','src'];s.querySelectorAll('*').forEach(e=>{if(e.closest('aside')||e.closest('.pg'))return;if(skip.some(c=>e.classList.contains(c)))return;const r=e.getBoundingClientRect();if(r.width===0)return;if(r.bottom>sr.top+921||r.right>sr.left+1793)bad.push(e.tagName+'.'+e.className+':'+Math.round(r.right-sr.left)+','+Math.round(r.bottom-sr.top));if(['P','H1','H2','TD','TH'].includes(e.tagName)&&e.scrollWidth>e.clientWidth+2)bad.push('hscroll '+e.tagName+' '+e.textContent.slice(0,30));});const all=[...s.querySelectorAll('*')].filter(e=>!e.closest('aside')&&!e.closest('svg')||e.tagName==='svg');let maxAbs=0,maxDepth=0;all.forEach(e=>{const n=[...e.children].filter(c=>getComputedStyle(c).position==='absolute').length;if(n>maxAbs)maxAbs=n;let d=0,p=e;while(p&&p!==s){if(p.tagName==='DIV')d++;p=p.parentElement}if(d>maxDepth)maxDepth=d;});const sAbs=[...s.children].filter(c=>getComputedStyle(c).position==='absolute').length;return s.id+': boxes='+all.length+' maxAbs='+Math.max(maxAbs,sAbs)+' depth='+maxDepth+' svg='+s.querySelectorAll('svg').length+(bad.length?' BAD '+bad.slice(0,4).join(' | '):'')}));
console.log(rep.join('\n'));await b.close();})();
