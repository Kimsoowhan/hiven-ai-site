#!/usr/bin/env python3
# 261113 Fable(이력 1113): 법인 설립 전 무료 운영 정책 검사 — 외부 저장소(Durable Object)를 부르는 주기 호출이 60초보다 짧으면 실패.
# 정본: HiBiz\91_Claude_소통(COM)\91_02_지시문\91_02_02_워크지시(Fable)\Fable_지시문_법인설립전_무료운영정책-261113_1023.md
import re,os,sys,glob
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
roots=[R]+[p for p in (os.path.join(os.path.dirname(R),n) for n in ('hiven-ic','hs')) if os.path.isdir(p) and os.path.realpath(p)!=os.path.realpath(R)]
CALL=re.compile(r"ic\.hiven\.ai\.kr/__|['\"]/__(?:cmd|apr|sec|dev|id|quota|cs)|CMDAPI\+|APR\+|DAPI\+|IC\+'/__")
bad=[];rows=[]
for root in roots:
    for f in sorted(glob.glob(root+'/*.js')+glob.glob(root+'/*.html')+glob.glob(root+'/test/*.html')):
        if os.path.basename(f)=='worker.js': continue
        s=open(f,encoding='utf-8',errors='ignore').read()
        fn={m.group(1):s[m.end():m.end()+900] for m in re.finditer(r'function\s+([A-Za-z_$][\w$]*)\s*\(',s)}
        for m in re.finditer(r'setInterval\(\s*(function\s*\([^)]*\)\s*\{.{0,400}?\}|[A-Za-z_$][\w$]*)\s*,\s*(\d+)\s*\)',s,re.S):
            body,ms=m.group(1),int(m.group(2))
            names=[body] if body in fn else re.findall(r'([A-Za-z_$][\w$]*)\s*\(',body)
            text=body+''.join(fn.get(n,'')[:900] for n in names)
            hit=bool(CALL.search(text)) and 'clearInterval' not in body  # 횟수가 정해진 1회성 대기(스스로 멈춤)는 주기 호출이 아님
            if hit:
                rel=os.path.relpath(f,os.path.dirname(R)); ln=s[:m.start()].count('\n')+1
                rows.append((rel,ln,ms,'적합' if ms>=60000 else '위반'))
                if ms<60000: bad.append('%s:%d 주기 %dms(60000ms 미만)로 외부 저장소 호출'%(rel,ln,ms))
        for m in re.finditer(r"(CMDAPI|APR)\+'list'",s): bad.append('%s 목록 호출에 v=2 없음(옛 방식)'%os.path.relpath(f,os.path.dirname(R)))
for root in roots:
    w=os.path.join(root,'worker.js')
    if os.path.exists(w):
        t=open(w,encoding='utf-8').read()
        for need,why in (('async tick(u)','누적 집계'),('listc(env','목록 재사용·옛 코드 차단'),("'/__quota'",'누적 조회 주소')):
            if need not in t: bad.append('worker.js에 %s 없음'%why)
if '--table' in sys.argv:
    for r in rows: print('\t'.join(map(str,r)))
for b in bad: print('실패:',b)
print('호출 정책 검사: 주기 호출 %d곳 · 위반 %d건'%(len(rows),len(bad)))
sys.exit(1 if bad else 0)
