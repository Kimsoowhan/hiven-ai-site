#!/usr/bin/env python3
# 규칙 강제 검사(이력 1220·1221, 대표님 11-13 15:38·15:41): 규칙을 적어만 두지 않고 어기면 올리지 못하게 막는다.
#  ① 보-8·보-9: 오늘 이후 지시문·설계안·큐에 대표님 선행 작업을 전제로 한 글이 있으면 실패
#  ② 선-2: 「[개발]」 일감이 「진행 중」인데 지시문 칸에 기준 문서(정의서·설계안·판정)가 없으면 실패
#  ③ 선-6: 큐 줄의 일감에 「선행 큐-NN」이 적혀 있는데 그 줄이 「끝」이 아니면서 이 줄이 「진행 중」이면 실패
#  ④ 수행 체계 지시문에 선-1~6·보-8·보-9·점-9 줄이 남아 있는지(지워지면 실패)
import os,re,sys,glob,csv
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); bad=[]
BAN=['대표님 결정 뒤','대표님 결정 대기','대표님이 정해 주시면','대표님 결정이 필요','대표님 검사 필수','대표님 확인 필수','결정 4건 답하고']
ALLOW=('보-8','보-9','금지','쓰지 않는다','같은 글','없다','않는다','취소','기록','질타','위반','고침','고쳐')
docs=[f for f in glob.glob(R+'/cowork/ctl/work_docs/*.md')+glob.glob(R+'/cowork/ctl/design/*.md') if re.search(r'-2611(1[3-9]|[2-3]\d)',os.path.basename(f))]
for f in docs+[R+'/cowork/ctl/work_queue.tsv']:
    for n,l in enumerate(open(f,encoding='utf-8-sig',errors='replace'),1):
        for b in BAN:
            if b in l and not any(a in l for a in ALLOW): bad.append('보-8 %s:%d 「%s」'%(os.path.basename(f),n,b))
rows=list(csv.reader(open(R+'/cowork/ctl/work_queue.tsv',encoding='utf-8-sig'),delimiter='\t',quoting=csv.QUOTE_NONE))
st={r[0]:(r[4] if len(r)>4 else '') for r in rows[1:] if r}
for r in rows[1:]:
    if len(r)<5: continue
    m=re.match(r'큐-(\d+)',r[0]); num=int(m.group(1)) if m else 0
    if num>=34 and '[개발' in r[1] and r[4]=='진행 중' and not re.search('정의서|설계안|판정|지시문',r[2]): bad.append('선-2 %s 개발 일감에 기준 문서 없음'%r[0])
    for p in re.findall(r'선행 (큐-\d+)',r[1]):
        if r[4]=='진행 중' and st.get(p)!='끝': bad.append('선-6 %s 선행 %s 상태 「%s」'%(r[0],p,st.get(p)))
pol=''.join(open(f,encoding='utf-8').read() for f in glob.glob(R+'/cowork/ctl/policy_docs/Fable_지시문_수행체계*.md'))
for k in ['선-1','선-2','선-3','선-4','선-5','선-6','보-8','보-9','점-9']:
    if k not in pol: bad.append('수행 체계 지시문에 %s 줄 없음'%k)
for b in bad: print('규칙 강제 실패:',b)
print('규칙 강제 검사(보-8·9 · 선-2·6 · 규칙 줄): '+('통과' if not bad else '실패 %d건'%len(bad)))
sys.exit(1 if bad else 0)
