#!/usr/bin/env python3
# 큐 대조(수행 체계 11절). 에이전트를 구동한 모델이 돌린다. 에이전트가 「끝」이라 적은 줄을 그대로 믿지 않는다.
#  목록:  python3 tools/queue_verify.py list            → 「끝」 줄마다 끝 증거에 적힌 저장소·컨테이너 경로가 실제로 있는지, 대조 대장에 올랐는지
#  기록:  python3 tools/queue_verify.py mark 큐-07 일치|불일치 "대조한 모델" "잰 방법과 값"
#  검사:  python3 tools/queue_verify.py check           → 대조 안 된 「끝」 줄이나 불일치가 있으면 종료 코드 1
import sys,os,re,csv,time
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q=R+'/cowork/ctl/work_queue.tsv';V=R+'/cowork/ctl/work_queue_verify.tsv'
H='번호\t대조한 때\t대조한 모델\t결과\t잰 방법과 값\t그때의 끝 증거\n'
def q(): return list(csv.DictReader(open(Q,encoding='utf-8-sig'),delimiter='\t'))
def v():
    if not os.path.exists(V): open(V,'w',encoding='utf-8').write(H)
    d={}
    for r in csv.DictReader(open(V,encoding='utf-8-sig'),delimiter='\t'): d[r['번호']]=r
    return d
def paths(t):
    out=[]
    for m in re.findall(r'(/(?:mnt|home)/[^\s,·()「」]+|(?:cowork|tools)/[^\s,·()「」]+)',t):
        p=m.rstrip('.,;') ; out.append((m,os.path.exists(p if p.startswith('/') else R+'/'+p)))
    return out
os.environ['TZ']='Asia/Seoul';time.tzset()
a=sys.argv[1] if len(sys.argv)>1 else 'list'
if a=='mark':
    n,res,model,how=sys.argv[2:6];v()
    ev=next((r['끝 증거'] for r in q() if r['번호']==n),'')
    L=[l for l in open(V,encoding='utf-8-sig').read().split('\n') if l and not l.startswith(n+'\t')]
    L.append('\t'.join([n,time.strftime('%m-%d %H:%M'),model,res,how.replace('\t',' '),ev.replace('\t',' ')]))
    open(V,'w',encoding='utf-8').write('\n'.join(L)+'\n');print('대조 기록',n,res);sys.exit(0)
d=v();bad=0
for r in q():
    if r['상태'].strip()!='끝': continue
    w=d.get(r['번호']);ps=paths(r['끝 증거'])
    miss=[p for p,ok in ps if not ok]
    if not w: st='대조 대기';bad+=1
    elif w['결과']!='일치': st='불일치 — 상태를 「대기」로 되돌리고 에이전트에게 돌려보냄';bad+=1
    elif w['그때의 끝 증거'].strip()!=r['끝 증거'].replace('\t',' ').strip(): st='끝 증거가 대조 뒤에 바뀜 — 다시 대조';bad+=1
    else: st='일치('+w['대조한 모델']+' '+w['대조한 때']+')'
    if a=='list' or st[:2]!='일치': print('%s %s | 적힌 경로 %d개 중 없는 것 %d개%s | %s'%(r['번호'],r['일감'][:28],len(ps),len(miss),(' '+', '.join(miss))[:120] if miss else '',st))
print('큐 대조: 「끝」 줄 중 대조 대기·불일치 %d줄'%bad)
if a=='check' and bad: sys.exit(1)
