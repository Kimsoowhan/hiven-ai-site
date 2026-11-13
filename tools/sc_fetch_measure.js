// 화면마다 실제로 읽는 게시 원천을 실측한다(브라우저로 화면을 열어 요청을 받아 적음). 내는 것: cowork/ctl/sc_fetch_measured.json
// 쓰는 법: node tools/sc_fetch_measure.js  (저장소 맨 위에서)
const {chromium}=require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const root=process.cwd();const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);if(p.endsWith('/'))p+='index.html';fs.readFile(path.join(root,p),(e,b)=>{if(e){r.writeHead(404);r.end()}else{r.writeHead(200);r.end(b)}})}).listen(0,async()=>{
 const port=srv.address().port,b=await chromium.launch(),out={},errs={};
 const ids=['SC-00','SC-01','SC-02','SC-03','SC-04','SC-05','SC-06','SC-07','SC-08','SC-09','SC-10','SC-11','SC-12','SC-13','SC-14','SC-15','SC-16','SC-17'];
 for(const id of ids){const pg=await b.newPage({viewport:{width:1280,height:900}});let on=false;const got=new Set(),er=[];
  pg.on('pageerror',e=>er.push(e.message.slice(0,80)));
  await pg.route('**/*',r=>{const u=r.request().url();if(!u.startsWith('http://localhost'))return r.abort();if(on){const p=decodeURIComponent(u.split('?')[0].replace(/^http:\/\/localhost:\d+\//,''));if(/\.(tsv|json)$/.test(p))got.add(p.replace(/^(\.\.\/)+/,''))}r.continue()});
  await pg.goto('http://localhost:'+port+'/test/index.html');await pg.waitForTimeout(1200);on=true;
  const has=await pg.evaluate(id=>{if(typeof V==='undefined'||!V[id])return false;try{if(typeof cur!=='undefined')cur=id}catch(e){}const d=document.createElement('div');document.body.appendChild(d);d.innerHTML=V[id]();return true},id);
  await pg.waitForTimeout(2500);out[id]={정의:has,읽은것:[...got].sort()};if(er.length)errs[id]=er;await pg.close()}
 await b.close();srv.close();
 fs.writeFileSync('cowork/ctl/sc_fetch_measured.json',JSON.stringify({잰때:new Date().toISOString(),화면:out,오류:errs},null,1));
 for(const k of ids)console.log(k,out[k].정의?out[k].읽은것.length:'정의 없음',(errs[k]||[]).length?'오류 '+errs[k][0]:'')});
