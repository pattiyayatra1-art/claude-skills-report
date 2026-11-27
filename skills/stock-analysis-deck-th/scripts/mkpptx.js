const pptxgen=require('pptxgenjs');const fs=require('fs');
const notes=JSON.parse(fs.readFileSync('notes.json','utf8'));const imgs=fs.readdirSync('jpg').sort();
const pres=new pptxgen();pres.layout='LAYOUT_WIDE';pres.title='SPALI วิเคราะห์งบการเงิน 5 ปี';pres.author='ภัททิยะ ยาตรา, กฤตนัย เพ็ญไพรัตน์กุล';
imgs.forEach((f,i)=>{const s=pres.addSlide();s.addImage({path:'jpg/'+f,x:0,y:0,w:13.333,h:7.5,altText:'สไลด์ '+(i+1)});s.addNotes(notes[i]);});
pres.writeFile({fileName:(process.env.OUT_DIR||'.')+'/Presentation.pptx'}).then(f=>console.log('ok',f));
