const {chromium}=require('/opt/node-tools/node_modules/playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.route('**/*',r=>{const u=new URL(r.request().url());if(u.host.endsWith('googleapis.com')||u.host.endsWith('gstatic.com'))return r.continue();if(u.protocol==='file:'||u.protocol==='data:')return r.continue();return r.abort()});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(1500);
console.log(await p.evaluate(()=>[...document.fonts].map(f=>f.family+':'+f.status).join(',')));
await p.pdf({path:process.argv[3],format:'A4',printBackground:true,preferCSSPageSize:true});await b.close();})();
