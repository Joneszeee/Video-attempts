const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.cwd()+'/make.html');
for(const [fn,out] of [['profile','profile.png'],['banner','banner.png']]){await p.evaluate(f=>window[f](),fn);
const d=await p.evaluate(()=>document.getElementById('c').toDataURL('image/png'));require('fs').writeFileSync(out,Buffer.from(d.split(',')[1],'base64'));}
await b.close();})();
