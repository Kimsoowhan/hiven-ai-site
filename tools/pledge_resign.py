#!/usr/bin/env python3
# 261113 Fable(이력 1114·1115): 각서와 서명을 구분해 매번 다시 받고, 대표님 결재선(approval_line.tsv → SC-00 결재함)에 잇는 틀.
#  각서 = 전체 정책·규칙에 대해 「나는 이렇게 일하겠다」는 다짐(작업 순서·규칙·이행·방식·태도·답변). 정책·규칙이 바뀔 때마다 다시.
#  서명 = 지시문 한 건마다 「이번 작업을 이렇게 하겠다」는 것. 서명 → 시행 → 시행 보고(done) → 결재.
#  issue/sign/done/check. check는 검사 스크립트(precheck) ⑫가 부른다.
import sys,os,glob,hashlib,subprocess,argparse
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); C=R+'/cowork/ctl/'; L=C+'pledge_resign.tsv'; AL=C+'approval_line.tsv'; TR=C+'pledge_trace.tsv'
MODELS=['Fable 5.2','Opus 5.5','Sonnet 5.5']
HEAD=['번호','갈래','발행 시각','문서','문서 해시','왜 바뀌었나','변경 사항','지시 사항','모델','서명 상태','서명 시각','서명 문구(인지한 내용 · 옛 코드·옛 명령 점검 결과)','시행 상태','시행 시각','결재 번호','근거(이력·말 명령)']
def now(): return subprocess.check_output(['date','+%Y-%m-%d %H:%M']).decode().strip()
def h(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()[:12]
def tracked(): return sorted(glob.glob(C+'policy_docs/*'))+sorted(glob.glob(C+'work_docs/*'))+[C+'free_tier_policy.tsv']  # 정책 지시(각서) · 워크·월·연·긴급 지시(서명)
def rel(p): return os.path.relpath(p,R)
def clean(s): return ' '.join(str(s).split())
def rd(f): return [l.rstrip('\n').split('\t') for l in open(f,encoding='utf-8-sig')] if os.path.exists(f) else []
def wr(f,rs,bom=False): open(f,'w',encoding='utf-8-sig' if bom else 'utf-8').write('\n'.join('\t'.join(r) for r in rs)+'\n')
def rows(): return rd(L)[1:]
def save(rs): wr(L,[HEAD]+rs)
def al_bom(): return open(AL,'rb').read(3)==b'\xef\xbb\xbf'
def al_state(rs,pid):
    # 261113 이력 1117: 각서·서명 결재는 승인이 아니라 상황 확인용. 발행 즉시 「확인 대기」로 오르고 진행 정도를 함께 보인다. 작업은 결재를 기다리지 않는다.
    g=[r for r in rs if r[0]==pid]; kind=g[0][1]; n=len(g); s=sum(r[9]=='서명' for r in g); d=sum(r[12]=='시행함' for r in g)
    return '확인 대기 · %s %d/%d'%(kind,s,n)+(' · 시행 보고 %d/%d'%(d,n) if kind=='서명' else '')+' · 작업은 진행 중(결재를 기다리지 않음)'
def al_sync(rs):
    a=rd(AL); bom=al_bom(); ch=0
    for pid in sorted({r[0] for r in rs}):
        g=[r for r in rs if r[0]==pid]; an=g[0][14]; st=al_state(rs,pid)
        for x in a:
            if x[0]==an and not any(k in x[7] for k in ('허가','승인','되돌림','파기','대체됨','확인함')) and x[7]!=st: x[7]=st; ch+=1
    if ch: wr(AL,a,bom)
a=argparse.ArgumentParser(); a.add_argument('cmd',choices=['issue','sign','done','check','sync','retire'])
for k in ('doc','why','change','order','id','model','text','kind','basis','by'): a.add_argument('--'+k)
A=a.parse_args(); rs=rows()
if A.cmd=='issue':
    p=A.doc if os.path.isabs(A.doc) else os.path.join(R,A.doc)
    if A.kind not in ('각서','서명'): sys.exit('--kind 는 각서(정책·규칙 전체 다짐) 또는 서명(지시문 한 건)')
    if not (A.why and A.change and A.order): sys.exit('왜·변경 사항·지시 사항을 모두 적어야 발행됩니다')
    n=max([int(r[0][3:]) for r in rs] or [0])+1; pid='PR-%03d'%n; t=now()
    al=rd(AL); an='A-%03d'%(max(int(x[0][2:]) for x in al if x[0].startswith('A-'))+1); doc=os.path.basename(p)
    for m in MODELS: rs.append([pid,A.kind,t,rel(p),h(p),clean(A.why),clean(A.change),clean(A.order),m,'서명 대기','','','시행 전' if A.kind=='서명' else '해당 없음','',an,clean(A.basis or '')])
    what=('작업 모델 3개가 바뀐 정책·규칙을 읽고 각서(작업 순서·규칙·이행·방식·태도·답변의 다짐)에 다시 서명했는지 상황 확인(승인 용도 아님, 작업은 결재를 기다리지 않음)' if A.kind=='각서' else '작업 모델 3개가 이 지시문에 서명하고 시행하고 있는지 상황 확인(승인 용도 아님, 작업은 결재를 기다리지 않음)')
    al.append([an,t,'Fable 5.2','확인','[%s] %s — %s'%(A.kind,doc,clean(A.change)),what,'%s · 문서 해시 %s · cowork/ctl/pledge_resign.tsv%s'%(pid,h(p),(' · '+clean(A.basis)) if A.basis else ''),al_state(rs,pid),'',''])
    wr(AL,al,al_bom()); save(rs)
    tr=rd(TR); tr.append([pid,t[5:].replace('-','/'),'[%s] %s'%(A.kind,doc),clean(A.order),'%s → 결재 %s'%(rel(p),an),'서명 수집 중']); wr(TR,tr)
    print('발행 %s(%s) · 결재 %s · %s'%(pid,A.kind,an,rel(p)))
elif A.cmd in ('sign','done'):
    if A.model not in MODELS: sys.exit('모델 이름은 %s 중 하나'%' · '.join(MODELS))
    tx=clean(A.text or ''); ok=0
    if A.cmd=='sign' and (len(tx)<30 or '옛' not in tx): sys.exit('서명 문구에 인지한 내용과 옛 코드·옛 명령 점검 결과를 적어야 합니다(30자 이상, 「옛」 점검 포함)')
    if A.cmd=='done' and len(tx)<15: sys.exit('시행 보고에는 무엇을 어디에 했는지 적어야 합니다(15자 이상)')
    for r in rs:
        if r[0]==A.id and r[8]==A.model:
            if A.cmd=='sign' and r[9]=='서명 대기': r[9]='서명'; r[10]=now(); r[11]=tx; ok+=1
            if A.cmd=='done' and r[1]=='서명' and r[9]=='서명' and r[12]=='시행 전': r[12]='시행함'; r[13]=now(); r[11]+=' ∥ 시행 보고: '+tx; ok+=1
    if not ok: sys.exit('해당 줄이 없습니다(서명 대기 또는 서명 뒤 시행 전인지 확인): %s %s'%(A.id,A.model))
    save(rs); al_sync(rs)
    tr=rd(TR)
    for x in tr:
        if x[0]==A.id: x[5]=al_state(rs,A.id)
    wr(TR,tr); print('%s %s · %s → %s'%('서명' if A.cmd=='sign' else '시행 보고',A.id,A.model,al_state(rs,A.id)))
elif A.cmd=='retire':
    # 261113 이력 1119: 새 요구로 대체된 요구는 「파기된 지시문」으로 표시하고 기록으로만 보존(지우지 않음). 서명 대기는 닫힌다.
    if not A.by: sys.exit('--by 에 대체한 새 요구 번호(PR-…)를 적습니다')
    t=now(); an=None; n=0
    for r in rs:
        if r[0]==A.id:
            an=r[14]
            if r[9]=='서명 대기': r[9]='파기된 지시문(기록 보존) · %s로 대체 %s'%(A.by,t); n+=1
            if r[12]=='시행 전': r[12]='파기(시행 대상 아님)'
    if an is None: sys.exit('없는 번호: '+A.id)
    al=rd(AL)
    for x in al:
        if x[0]==an: x[7]='파기(기록 보존) · 파기된 지시문 — %s로 대체'%A.by
    wr(AL,al,al_bom()); save(rs); tr=rd(TR)
    for x in tr:
        if x[0]==A.id: x[5]='파기된 지시문(기록 보존) · %s로 대체'%A.by
    wr(TR,tr); print('파기 처리 %s → %s (서명 대기 %d줄 닫음)'%(A.id,A.by,n))
elif A.cmd=='sync': al_sync(rs); print('결재선 맞춤')
else:
    bad=0; last={}
    for r in rs: last[r[3]]=r[4]
    for p in tracked():
        if os.path.exists(p) and last.get(rel(p))!=h(p): print('실패: 정책·지시문이 바뀌었는데 각서·서명 요구 미발행 — %s (python3 tools/pledge_resign.py issue --kind 각서|서명 --doc … --why … --change … --order …)'%rel(p)); bad+=1
    al={x[0] for x in rd(AL)}
    for pid in sorted({r[0] for r in rs}):
        an=[r for r in rs if r[0]==pid][0][14]
        if an not in al: print('실패: %s의 결재 줄 %s가 결재선에 없음'%(pid,an)); bad+=1
    pend={};todo={}
    for r in rs:
        if r[9]=='서명 대기': pend.setdefault(r[8],[]).append(r[0])
        elif r[12]=='시행 전': todo.setdefault(r[8],[]).append(r[0])
    for m,v in pend.items(): print('알림: 각서·서명 대기 — %s %d건(%s). 이 모델은 작업 전에 문서를 읽고 서명부터 합니다'%(m,len(v),' · '.join(sorted(set(v)))))
    for m,v in todo.items(): print('알림: 서명 뒤 시행 보고 대기 — %s %d건(%s)'%(m,len(v),' · '.join(sorted(set(v)))))
    print('각서·서명 점검: 발행 %d건(각서 %d · 서명 %d) · 서명 대기 %d줄 · 시행 보고 대기 %d줄 · 미발행 변경 %d건'%(len({r[0] for r in rs}),len({r[0] for r in rs if r[1]=='각서'}),len({r[0] for r in rs if r[1]=='서명'}),sum(map(len,pend.values())),sum(map(len,todo.values())),bad))
    sys.exit(1 if bad else 0)
