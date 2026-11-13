/* 대표 일정 공통(이력 1240~1242·1249, Opus 5.5): schedule.html 과 통합관제 첫 화면이 함께 쓴다.
   공개 키 방식(이력 1249): 열쇠 → PBKDF2-SHA256(120000회, 소금 hiven-sched-ec-261113, 48바이트) → P-256 개인 값
   (FIPS 186-4 부록 B.4.1 「여분 비트」 방식: d = c mod (n-1) + 1). 공개 값(압축 33바이트, base64url 44자)을 「잠그는 값」이라 부른다.
   묶음(sched.enc.json, v2)은 ECIES: 임시 키 짝 + ECDH(P-256) + HKDF-SHA256 + AES-256-GCM. 묶는 쪽(tools/gen_ceo_schedule.py)은
   잠그는 값(sched.pub.json)만 있으면 되고 열쇠는 모른다. 푸는 쪽은 이 파일이 열쇠에서 개인 값을 다시 뽑아 Web Crypto ECDH 로 푼다.
   공개 값 계산(d·G)만 아래 BigInt 곱으로 하고(Web Crypto 가 개인 값만으로는 들여오기를 받지 않음), ECDH·HKDF·AES-GCM 은 Web Crypto 가 한다.
   열쇠는 통합관제(IC)와 같은 열쇠다(11-13 17:08 대표님 확정, 일정 전용 열쇠 없음). 열쇠가 맞는지는 묶음이 풀리는지로 보고,
   묶음이 없거나 다른 잠그는 값으로 만든 묶음일 때만 통합관제 열쇠 확인 값(KEYH)으로 맞는지 본 뒤 잠그는 값을 보인다.
   뽑은 개인 값은 이 창(탭)의 sessionStorage hv_sk2 에만 두고 「나오기」·창 닫기에 사라진다. */
var HVSCH=(function(){
function hk(v){var M={'ㅂ':'q','ㅈ':'w','ㄷ':'e','ㄱ':'r','ㅅ':'t','ㅛ':'y','ㅕ':'u','ㅑ':'i','ㅐ':'o','ㅔ':'p','ㅁ':'a','ㄴ':'s','ㅇ':'d','ㄹ':'f','ㅎ':'g','ㅗ':'h','ㅓ':'j','ㅏ':'k','ㅣ':'l','ㅋ':'z','ㅌ':'x','ㅊ':'c','ㅍ':'v','ㅠ':'b','ㅜ':'n','ㅡ':'m','ㅃ':'q','ㅉ':'w','ㄸ':'e','ㄲ':'r','ㅆ':'t','ㅒ':'o','ㅖ':'p'},C=['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'],V=['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'],T=['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'],X={'ㅘ':'ㅗㅏ','ㅙ':'ㅗㅐ','ㅚ':'ㅗㅣ','ㅝ':'ㅜㅓ','ㅞ':'ㅜㅔ','ㅟ':'ㅜㅣ','ㅢ':'ㅡㅣ','ㄳ':'ㄱㅅ','ㄵ':'ㄴㅈ','ㄶ':'ㄴㅎ','ㄺ':'ㄹㄱ','ㄻ':'ㄹㅁ','ㄼ':'ㄹㅂ','ㄽ':'ㄹㅅ','ㄾ':'ㄹㅌ','ㄿ':'ㄹㅍ','ㅀ':'ㄹㅎ','ㅄ':'ㅂㅅ'},o='';for(var i=0;i<v.length;i++){var c=v.charCodeAt(i),j=[];if(c>=44032&&c<=55203){var n=c-44032;j=[C[Math.floor(n/588)],V[Math.floor(n%588/28)],T[n%28]];}else j=[v.charAt(i)];for(var k=0;k<j.length;k++){var u=X[j[k]]||j[k];for(var m=0;m<u.length;m++){var h=u.charAt(m);o+=(M[h]||h);}}}return o;}
 var SALT='hiven-sched-ec-261113',IT=120000,SK='hv_sk2',SK0='hv_sk',INFO='hiven-sched-ecies-v2',AAD='hiven-sched-v2';
 /* 열쇠 확인 값: 통합관제 data.js 의 KEYH 와 같은 값(이미 공개된 값, 열쇠 자체는 아님). data.js 가 있는 화면(통합관제)에서는 그쪽 값을 쓴다.
    gen_ceo_schedule.py 가 묶음을 만들 때 data.js 와 같은지 대조한다. */
 var CHK={h:'35bb76b137d27780cddcccbf47e093ba24f5a90d91bf9e54f0a0725f936e79ad',s:'hiven-intro-261113',i:120000,n:6};
 var te=new TextEncoder();
 function norm(v){return hk(String(v||'').trim()).toLowerCase()}
 function hex(b){return Array.prototype.map.call(new Uint8Array(b),function(c){return ('0'+c.toString(16)).slice(-2)}).join('')}
 function unhex(h){var a=new Uint8Array(h.length/2);for(var i=0;i<a.length;i++)a[i]=parseInt(h.substr(i*2,2),16);return a}
 function b64(s){s=String(s).replace(/-/g,'+').replace(/_/g,'/');while(s.length%4)s+='=';var b=atob(s),a=new Uint8Array(b.length);for(var i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return a}
 function b64u(a){var s='';for(var i=0;i<a.length;i++)s+=String.fromCharCode(a[i]);return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
 function cat(a,b){var c=new Uint8Array(a.length+b.length);c.set(a,0);c.set(b,a.length);return c}
 function pb(v,salt,it,bits){return crypto.subtle.importKey('raw',te.encode(v),'PBKDF2',false,['deriveBits']).then(function(km){return crypto.subtle.deriveBits({name:'PBKDF2',hash:'SHA-256',salt:te.encode(salt),iterations:it},km,bits)})}

 /* ── P-256 공개 값 계산(SEC 2 / FIPS 186-4 곡선 상수, 야코비 좌표 더하기·두 배) ── */
 var EC=null;
 function ec(){if(EC)return EC;var B=BigInt;
  EC={p:B('0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff'),n:B('0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551'),
   b:B('0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b'),
   gx:B('0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296'),gy:B('0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5')};return EC}
 function md(a){var p=EC.p;a%=p;return a<0n?a+p:a}
 function pw(a,e){var r=1n;a=md(a);while(e>0n){if(e&1n)r=r*a%EC.p;a=a*a%EC.p;e>>=1n}return r}
 function dbl(P){if(!P||P[1]===0n)return null;var X=P[0],Y=P[1],Z=P[2],dl=md(Z*Z),gm=md(Y*Y),bt=md(X*gm),al=md(3n*(X-dl)*(X+dl)),X3=md(al*al-8n*bt),Z3=md((Y+Z)*(Y+Z)-gm-dl),Y3=md(al*(4n*bt-X3)-8n*gm*gm);return [X3,Y3,Z3]}
 function add(P,Q){if(!P)return Q;if(!Q)return P;var Z1=md(P[2]*P[2]),Z2=md(Q[2]*Q[2]),U1=md(P[0]*Z2),U2=md(Q[0]*Z1),S1=md(P[1]*Q[2]*Z2),S2=md(Q[1]*P[2]*Z1),H=md(U2-U1),r=md(S2-S1);
  if(H===0n)return r===0n?dbl(P):null;var I=md(4n*H*H),J=md(H*I),rr=md(2n*r),Vv=md(U1*I),X3=md(rr*rr-J-2n*Vv),Y3=md(rr*(Vv-X3)-2n*S1*J),Z3=md(((P[2]+Q[2])*(P[2]+Q[2])-Z1-Z2)*H);return [X3,Y3,Z3]}
 function mul(k){ec();var R=null,Pt=[EC.gx,EC.gy,1n],s=k.toString(2);for(var i=0;i<s.length;i++){R=dbl(R);if(s.charAt(i)==='1')R=add(R,Pt)}
  if(!R)return null;var zi=pw(R[2],EC.p-2n),z2=zi*zi%EC.p,x=R[0]*z2%EC.p,y=R[1]*z2%EC.p*zi%EC.p;
  if(md(y*y-(x*x*x-3n*x+EC.b))!==0n)return null;/* 곡선 위에 있는지 스스로 확인 */return [x,y]}
 function be(x){var h=x.toString(16);while(h.length<64)h='0'+h;return unhex(h)}
 /* 개인 값(16진 64자) → {d,x,y 바이트, 잠그는 값} — 한 페이지 안에서 한 번만 계산 */
 var KP={};
 function pair(dh){if(KP[dh])return KP[dh];if(typeof BigInt!=='function')return null;var d=BigInt('0x'+dh),Q=mul(d);if(!Q)return null;
  var x=be(Q[0]),y=be(Q[1]),c=cat(new Uint8Array([Q[1]&1n?3:2]),x);return KP[dh]={d:unhex(dh),x:x,y:y,pub:b64u(c),pubRaw:c}}
 /* 열쇠 → 개인 값(16진 64자). FIPS 186-4 B.4.1: 48바이트 c, d = c mod (n-1) + 1 */
 function derive(v){v=norm(v);if(!v||!(window.crypto&&crypto.subtle)||typeof BigInt!=='function')return Promise.resolve(null);
  return pb(v,SALT,IT,384).then(function(b){ec();var c=BigInt('0x'+hex(b)),d=c%(EC.n-1n)+1n,h=d.toString(16);while(h.length<64)h='0'+h;return h}).catch(function(){return null})}
 function pubOf(dh){var k=dh&&pair(dh);return k?k.pub:''}
 /* 열쇠가 통합관제 열쇠인지(묶음이 없거나 풀리지 않을 때만 씀) */
 function check(v){v=norm(v);var C=(typeof KEYH==='string')?{h:KEYH,s:KEYS,i:KEYI,n:KEYN}:CHK;if(v.length!==C.n||!(window.crypto&&crypto.subtle))return Promise.resolve(false);return pb(v,C.s,C.i,256).then(function(b){return hex(b)===C.h}).catch(function(){return false})}
 function getK(){try{return sessionStorage.getItem(SK)||''}catch(e){return ''}}
 function setK(h){try{sessionStorage.removeItem(SK0);h?sessionStorage.setItem(SK,h):sessionStorage.removeItem(SK)}catch(e){}}
 /* 묶음은 페이지마다 한 번만 읽는다(없을 때도 다시 읽지 않음, 이력 1243). 없음·옛 꼴(v1)은 null */
 var boxP=null;
 function box(){if(!boxP)boxP=fetch('/sched.enc.json?t='+Date.now(),{cache:'no-store',credentials:'same-origin'}).then(function(r){return r.ok?r.json():null}).then(function(b){return b&&b.v===2&&b.epk&&b.ct?b:null}).catch(function(){return null});return boxP}
 /* 풀기: 성공하면 자료, 열쇠가 틀리면(또는 다른 잠그는 값으로 만든 묶음이면) false, 묶음이 없으면 null */
 function open(dh){return box().then(function(bx){if(!bx)return null;var k=dh&&pair(dh);if(!k)return false;var S=crypto.subtle,E={name:'ECDH',namedCurve:'P-256'},epk=b64(bx.epk);
  return Promise.all([S.importKey('jwk',{kty:'EC',crv:'P-256',d:b64u(k.d),x:b64u(k.x),y:b64u(k.y),ext:false},E,false,['deriveBits']),S.importKey('raw',epk,E,false,[])])
   .then(function(a){return S.deriveBits({name:'ECDH',public:a[1]},a[0],256)})
   .then(function(z){return S.importKey('raw',z,'HKDF',false,['deriveBits'])})
   .then(function(hk){return S.deriveBits({name:'HKDF',hash:'SHA-256',salt:cat(epk,k.pubRaw),info:te.encode(INFO)},hk,256)})
   .then(function(kb){return S.importKey('raw',kb,{name:'AES-GCM'},false,['decrypt'])})
   .then(function(ak){return S.decrypt({name:'AES-GCM',iv:b64(bx.iv),additionalData:te.encode(AAD)},ak,b64(bx.ct))})
   .then(function(p){return JSON.parse(new TextDecoder().decode(p))}).catch(function(){return false})})}
 /* 묶음이 있으면 그 묶음의 잠그는 값(없으면 '') — 화면 안내용 */
 function boxPub(){return box().then(function(b){return b&&b.rk||''})}
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
 return {norm:norm,derive:derive,pubOf:pubOf,check:check,box:box,getK:getK,setK:setK,open:open,boxPub:boxPub,today:today,dnum:dnum,dday:dday,dtxt:dtxt,cancelled:cancelled,finished:finished,level:level,LV:LV,LC:LC,alerts:alerts,next:next,esc:esc};
})();
