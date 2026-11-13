// 화면마다 실제로 읽는 게시 원천을 실측한다(브라우저로 본판을 열어 요청을 받아 적음). 내는 것: cowork/ctl/sc_fetch_measured.json
// 쓰는 법: node tools/sc_fetch_measure.js [페이지(기본 index.html)]  (저장소 맨 위에서)
// 261113 고침(Fable 지시 · Opus 5.5): 시험 페이지(test/index.html)가 아니라 본판 index.html을 연다 — 본판만 읽는 sec.js · sec2.js의 값도 잡힌다.
//  열쇠 화면은 통과하지 않는다(열쇠를 넣지 않음). 화면 함수는 페이지가 다 읽힌 뒤 hvgo(화면)로 그린다(인트로를 가리는 것은 이 측정 브라우저 안에서만).
//  ① 공통: 화면을 부르기 전(페이지를 열 때 + 4초 쉬는 동안)에 페이지 전체가 미리 읽은 원천. 쉬는 동안 다시 읽은 것은 「주기」.
//  ② 화면: 화면을 부른 뒤 4초 동안 새로 읽은 원천 가운데 공통에 없는 것(「읽은것」). 공통 원천을 화면이 다시 읽은 것은 「공통과겹침」.
//  화면 함수가 공통으로 미리 읽어 둔 변수(views9.js P.* · views0.js hvMeta.*)를 쓰는 것은 요청으로 잡히지 않는다 → tools/gen_sc_confirmed.py(코드에서 뽑음)가 cowork/ctl/sc_source_confirmed.tsv로 낸다.
//  바깥 호출(ic.hiven.ai.kr · 글꼴 등)은 모두 막고, 막은 주소만 「서버호출」로 적는다(실제로 부르지 않음).
const {chromium}=require('playwright');const http=require('http'),fs=require('fs'),path=require('path');
const root=process.cwd(),PAGE=process.argv[2]||'index.html',WAIT=4000;
const MIME={'.js':'application/javascript','.html':'text/html; charset=utf-8','.css':'text/css','.json':'application/json','.tsv':'text/tab-separated-values; charset=utf-8','.svg':'image/svg+xml'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);if(p.endsWith('/'))p+='index.html';fs.readFile(path.join(root,p),(e,b)=>{if(e){r.writeHead(404);r.end()}else{const t=MIME[path.extname(p)];r.writeHead(200,t?{'Content-Type':t}:{});r.end(b)}})}).listen(0,async()=>{
 const port=srv.address().port,b=await chromium.launch(),out={},errs={};
 const norm=u=>decodeURIComponent(u.split('?')[0].replace(/^http:\/\/localhost:\d+\//,'')).replace(/^(\.\.\/)+/,'').replace(/^\/+/,'');
 const ext=u=>{const m=u.match(/^https?:\/\/([^\/?#]+)([^?#]*)/);return m?m[1]+m[2]:u};
 async function open(){const pg=await b.newPage({viewport:{width:1280,height:900}}),st={ph:'load',load:new Set(),idle:new Set(),cnt:{},scr:new Set(),srvPre:new Set(),srvScr:new Set(),er:[]};
  pg.on('pageerror',e=>st.er.push(e.message.slice(0,100)));
  await pg.route('**/*',r=>{const u=r.request().url();if(!u.startsWith('http://localhost')){(st.ph==='scr'?st.srvScr:st.srvPre).add(ext(u));return r.abort()}
   const p=norm(u);if(/\.(tsv|json)$/.test(p)){st.cnt[p]=(st.cnt[p]||0)+1;(st.ph==='load'?st.load:st.ph==='idle'?st.idle:st.scr).add(p)}r.continue()});
  await pg.goto('http://localhost:'+port+'/'+PAGE,{waitUntil:'load'});await pg.waitForTimeout(1500);st.ph='idle';await pg.waitForTimeout(WAIT);return {pg,st}}
 const first=await open();
 const ids=await first.pg.evaluate(()=>{var a=(typeof S!=='undefined'?S.map(function(s){return s[0]}):[]);Object.keys(V||{}).forEach(function(k){if(/^SC-\d\d$/.test(k)&&a.indexOf(k)<0)a.push(k)});return a.sort()});
 const common=new Set([...first.st.load,...first.st.idle]),periodic=[...first.st.idle].sort(),pre=[...first.st.srvPre].sort();await first.pg.close();
 for(const id of ids){const {pg,st}=await open();const base=new Set([...st.load,...st.idle]);st.ph='scr';
  const has=await pg.evaluate(id=>{if(typeof V==='undefined'||!V[id])return false;var i=document.getElementById('intro'),a=document.getElementById('app');if(i)i.classList.add('hide');if(a)a.classList.remove('hide');if(typeof hvgo==='function')hvgo(id);else{cur=id;document.getElementById('main').innerHTML=V[id]()}return true},id);
  await pg.waitForTimeout(WAIT);
  const got=[...st.scr];out[id]={정의:has,읽은것:got.filter(p=>!base.has(p)&&!common.has(p)).sort(),공통과겹침:got.filter(p=>base.has(p)||common.has(p)).sort(),서버호출:[...st.srvScr].sort()};
  if(st.er.length)errs[id]=st.er;await pg.close()}
 await b.close();srv.close();
 fs.writeFileSync('cowork/ctl/sc_fetch_measured.json',JSON.stringify({잰때:new Date().toISOString(),페이지:PAGE,방법:'본판을 열쇠 없이 열어 화면을 부르기 전(공통)과 부른 뒤 '+WAIT/1000+'초(화면) 요청을 갈라 적음. 바깥 호출은 막고 주소만 적음. 미리 읽은 변수를 쓰는 화면 원천은 sc_source_confirmed.tsv(코드에서 뽑음)',
  공통:{읽은것:[...common].sort(),주기:periodic,서버호출:pre},화면:out,오류:errs},null,1)+'\n');
 console.log('공통',common.size,'(주기 '+periodic.length+') 서버호출',pre.length);
 for(const k of ids)console.log(k,out[k].정의?'화면 '+out[k].읽은것.length+' · 겹침 '+out[k].공통과겹침.length+' · 서버 '+out[k].서버호출.length:'정의 없음',(errs[k]||[]).length?'오류 '+errs[k][0]:'')});
