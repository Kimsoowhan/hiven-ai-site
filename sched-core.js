/* 대표 일정 공통(이력 1240~1242, Opus 5.5): schedule.html 과 통합관제 첫 화면이 함께 쓴다.
   일정 자료는 sched.enc.json(AES-256-GCM) 하나로만 싣는다. 암호 열쇠 = PBKDF2-SHA256(120000회, 소금 hiven-sched-261113)으로 통합관제 열쇠에서 뽑는다.
   열쇠 확인 값(data.js KEYH)과 소금이 달라 확인 값으로는 풀리지 않는다. 뽑은 열쇠는 이 창(탭)의 sessionStorage hv_sk 에만 두고 「나오기」·창 닫기에 사라진다. */
var HVSCH=(function(){
function hk(v){var M={'ㅂ':'q','ㅈ':'w','ㄷ':'e','ㄱ':'r','ㅅ':'t','ㅛ':'y','ㅕ':'u','ㅑ':'i','ㅐ':'o','ㅔ':'p','ㅁ':'a','ㄴ':'s','ㅇ':'d','ㄹ':'f','ㅎ':'g','ㅗ':'h','ㅓ':'j','ㅏ':'k','ㅣ':'l','ㅋ':'z','ㅌ':'x','ㅊ':'c','ㅍ':'v','ㅠ':'b','ㅜ':'n','ㅡ':'m','ㅃ':'q','ㅉ':'w','ㄸ':'e','ㄲ':'r','ㅆ':'t','ㅒ':'o','ㅖ':'p'},C=['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'],V=['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'],T=['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'],X={'ㅘ':'ㅗㅏ','ㅙ':'ㅗㅐ','ㅚ':'ㅗㅣ','ㅝ':'ㅜㅓ','ㅞ':'ㅜㅔ','ㅟ':'ㅜㅣ','ㅢ':'ㅡㅣ','ㄳ':'ㄱㅅ','ㄵ':'ㄴㅈ','ㄶ':'ㄴㅎ','ㄺ':'ㄹㄱ','ㄻ':'ㄹㅁ','ㄼ':'ㄹㅂ','ㄽ':'ㄹㅅ','ㄾ':'ㄹㅌ','ㄿ':'ㄹㅍ','ㅀ':'ㄹㅎ','ㅄ':'ㅂㅅ'},o='';for(var i=0;i<v.length;i++){var c=v.charCodeAt(i),j=[];if(c>=44032&&c<=55203){var n=c-44032;j=[C[Math.floor(n/588)],V[Math.floor(n%588/28)],T[n%28]];}else j=[v.charAt(i)];for(var k=0;k<j.length;k++){var u=X[j[k]]||j[k];for(var m=0;m<u.length;m++){var h=u.charAt(m);o+=(M[h]||h);}}}return o;}
 var SALT='hiven-sched-261113',IT=120000,SK='hv_sk';
 function norm(v){return hk(String(v||'').trim()).toLowerCase()}
 function hex(b){return Array.prototype.map.call(new Uint8Array(b),function(c){return ('0'+c.toString(16)).slice(-2)}).join('')}
 function unhex(h){var a=new Uint8Array(h.length/2);for(var i=0;i<a.length;i++)a[i]=parseInt(h.substr(i*2,2),16);return a}
 function b64(s){var b=atob(s),a=new Uint8Array(b.length);for(var i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return a}
 function derive(v){var te=new TextEncoder();v=norm(v);if(!v||!(window.crypto&&crypto.subtle))return Promise.resolve(null);return crypto.subtle.importKey('raw',te.encode(v),'PBKDF2',false,['deriveBits']).then(function(km){return crypto.subtle.deriveBits({name:'PBKDF2',hash:'SHA-256',salt:te.encode(SALT),iterations:IT},km,256)}).then(hex).catch(function(){return null})}
 function getK(){try{return sessionStorage.getItem(SK)||''}catch(e){return ''}}
 function setK(h){try{h?sessionStorage.setItem(SK,h):sessionStorage.removeItem(SK)}catch(e){}}
 var boxP=null;
 function box(){if(!boxP)boxP=fetch('/sched.enc.json?t='+Date.now(),{cache:'no-store',credentials:'same-origin'}).then(function(r){if(!r.ok)throw new Error('묶음 없음 '+r.status);return r.json()});return boxP}
 /* 풀기: 성공하면 자료, 열쇠가 틀리면 false, 묶음이 없으면 null */
 function open(h){return box().then(function(bx){if(!h)return false;return crypto.subtle.importKey('raw',unhex(h),{name:'AES-GCM'},false,['decrypt']).then(function(k){return crypto.subtle.decrypt({name:'AES-GCM',iv:b64(bx.iv)},k,b64(bx.ct))}).then(function(p){return JSON.parse(new TextDecoder().decode(p))}).catch(function(){return false})},function(){boxP=null;return null})}
 /* 서울 날짜: 한국은 일광 절약 시간이 없어 UTC+9 고정 */
 function today(){var d=new Date(Date.now()+9*3600000);return d.toISOString().slice(0,10)}
 function dnum(s){var m=/^(\d{4})-(\d\d)-(\d\d)$/.exec(s||'');return m?Date.UTC(+m[1],+m[2]-1,+m[3])/86400000:null}
 function dday(s,t){var a=dnum(s),b=dnum(t||today());return a==null||b==null?null:a-b}
 function dtxt(d){return d==null?'':d===0?'D-DAY':d>0?'D-'+d:'D+'+(-d)}
 function cancelled(r){return /취소/.test(r[4]||'')}
 function finished(r){return /끝남|완료|마침/.test(r[4]||'')}
 /* 얼럿 단계: 지남(기한 넘김, 끝나지 않음) · 1일 안(D-DAY·D-1) · 3일 안(D-2·D-3) · 7일 안(D-4~D-7) */
 function level(d){return d==null?null:d<0?'past':d<=1?'d1':d<=3?'d3':d<=7?'d7':null}
 var LV={past:'기한 지남',d1:'1일 안',d3:'3일 안',d7:'7일 안'},LC={past:'#b71c1c',d1:'#d64545',d3:'#ef6c00',d7:'#d4a800'};
 function alerts(ceo,t){return (ceo||[]).filter(function(r){return !cancelled(r)&&!finished(r)}).map(function(r){var d=dday(r[1],t);return {r:r,d:d,lv:level(d)}}).filter(function(x){return x.lv}).sort(function(a,b){return a.d-b.d})}
 function next(ceo,t){return (ceo||[]).filter(function(r){return !cancelled(r)&&!finished(r)}).map(function(r){return {r:r,d:dday(r[1],t)}}).filter(function(x){return x.d!=null&&x.d>=0}).sort(function(a,b){return a.d-b.d})[0]||null}
 function esc(v){return String(v==null?'':v).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
 return {norm:norm,derive:derive,getK:getK,setK:setK,open:open,today:today,dnum:dnum,dday:dday,dtxt:dtxt,cancelled:cancelled,finished:finished,level:level,LV:LV,LC:LC,alerts:alerts,next:next,esc:esc};
})();
