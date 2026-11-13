#!/usr/bin/env python3
# 261113 Fable(이력 1114): 정책·정의·규칙·지시문이 바뀔 때마다 모든 작업 모델에게 각서 서명을 다시 받는 틀.
#  issue : 바뀐 문서를 등록하고 모델마다 「서명 대기」 줄을 만든다(문서 해시 포함)
#  sign  : 모델이 스스로 서명한다(인지한 내용 · 옛 코드·옛 명령 점검 결과를 적어야 함)
#  check : 등록 안 된 변경(실패)과 서명 대기(알림)를 알려 준다 — 검사 스크립트(precheck) ⑫가 부른다
import sys,os,glob,hashlib,subprocess,argparse
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); C=R+'/cowork/ctl/'; L=C+'pledge_resign.tsv'
MODELS=['Fable 5.2','Opus 5.5','Sonnet 5.5']
HEAD=['번호','발행 시각','문서','문서 해시','왜 바뀌었나','변경 사항','지시 사항','모델','서명 상태','서명 시각','서명 문구(인지한 내용 · 옛 코드·옛 명령 점검 결과)']
def now(): return subprocess.check_output(['date','+%Y-%m-%d %H:%M']).decode().strip()
def h(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()[:12]
def tracked(): return sorted(glob.glob(C+'policy_docs/*'))+[C+'free_tier_policy.tsv']
def rel(p): return os.path.relpath(p,R)
def rows():
    if not os.path.exists(L): return []
    return [l.rstrip('\n').split('\t') for l in open(L,encoding='utf-8')][1:]
def save(rs): open(L,'w',encoding='utf-8').write('\n'.join('\t'.join(r) for r in [HEAD]+rs)+'\n')
def clean(s): return ' '.join(str(s).split())
a=argparse.ArgumentParser(); a.add_argument('cmd',choices=['issue','sign','check']); a.add_argument('--doc'); a.add_argument('--why'); a.add_argument('--change'); a.add_argument('--order'); a.add_argument('--id'); a.add_argument('--model'); a.add_argument('--text')
A=a.parse_args(); rs=rows()
if A.cmd=='issue':
    p=A.doc if os.path.isabs(A.doc) else os.path.join(R,A.doc)
    if not (A.why and A.change and A.order): sys.exit('왜·변경 사항·지시 사항을 모두 적어야 발행됩니다')
    n=max([int(r[0][3:]) for r in rs] or [0])+1; t=now()
    for m in MODELS: rs.append(['PR-%03d'%n,t,rel(p),h(p),clean(A.why),clean(A.change),clean(A.order),m,'서명 대기','',''])
    save(rs); print('발행 PR-%03d · %s · 대상 %d모델'%(n,rel(p),len(MODELS)))
elif A.cmd=='sign':
    if A.model not in MODELS: sys.exit('모델 이름은 %s 중 하나'%' · '.join(MODELS))
    tx=clean(A.text or '')
    if len(tx)<30 or '옛' not in tx: sys.exit('서명 문구에 인지한 내용과 옛 코드·옛 명령 점검 결과를 적어야 합니다(30자 이상, 「옛」 점검 포함)')
    ok=0
    for r in rs:
        if r[0]==A.id and r[7]==A.model and r[8]=='서명 대기': r[8]='서명'; r[9]=now(); r[10]=tx; ok+=1
    if not ok: sys.exit('서명 대기 줄이 없습니다: %s %s'%(A.id,A.model))
    save(rs); print('서명 %s · %s'%(A.id,A.model))
else:
    bad=0; last={}
    for r in rs: last[r[2]]=r[3]
    for p in tracked():
        if not os.path.exists(p): continue
        if last.get(rel(p))!=h(p): print('실패: 정책·지시문이 바뀌었는데 재서명 요구 미발행 — %s (python3 tools/pledge_resign.py issue --doc … --why … --change … --order …)'%rel(p)); bad+=1
    pend={}
    for r in rs:
        if r[8]=='서명 대기': pend.setdefault(r[7],[]).append(r[0])
    for m,v in pend.items(): print('알림: 각서 재서명 대기 — %s %d건(%s). 이 모델은 작업 전에 문서를 읽고 서명부터 합니다'%(m,len(v),' · '.join(sorted(set(v)))))
    print('각서 재서명 점검: 발행 %d건 · 서명 대기 %d줄 · 미발행 변경 %d건'%(len({r[0] for r in rs}),sum(len(v) for v in pend.values()),bad))
    sys.exit(1 if bad else 0)
