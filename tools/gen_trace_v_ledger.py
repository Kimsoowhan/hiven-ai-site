"""11-12 이력 870(Opus): 새 지시대장(command_ledger.tsv, 91_02_01_대표지시)의 대표님 지시를 추적 매트릭스 종단(trace_v.tsv)에 이어 붙인다.
옛 S122(11-05) 뒤로 멈춰 있던 종단을 지시대장 번호 = 이력 번호로 잇는다. 다시 돌려도 같은 번호는 한 번만 들어간다."""
import csv,os,re
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','cowork','ctl')
V=os.path.join(R,'trace_v.tsv');L=os.path.join(R,'command_ledger.tsv');H=os.path.join(R,'model_control_history.tsv')
rows=[l.rstrip('\n').split('\t') for l in open(V,encoding='utf-8') if l.strip()]
have=set(m for r in rows for m in re.findall(r'#(\d+)',r[6] if len(r)>6 else ''))
hist={r[0]:r for r in (l.rstrip('\n').split('\t') for l in open(H,encoding='utf-8')) if r and r[0].isdigit()}
last=max([int(r[0][1:]) for r in rows if re.match(r'^S\d+$',r[0])] or [0])
add=0
for r in (l.rstrip('\n').split('\t') for l in open(L,encoding='utf-8')):
    if not r or not r[0].isdigit() or r[0] in have: continue
    h=hist.get(r[0],[]);last+=1;add+=1
    st=h[9] if len(h)>9 else r[4]
    rows.append(['S%d'%last,h[1] if len(h)>1 else '2026-11-12',(r[1].split(' ')[-1] if r[1] else ''),'대표님 「'+re.sub(r'^대표님\s*','',r[2]).strip('「」 ')+'」',h[5] if len(h)>5 else '지시','지시대장 #'+r[0],'#'+r[0],h[4] if len(h)>4 else '',st,(h[8][:120] if len(h)>8 else ''),'반영' if re.search('완료|처리됨',st) else '진행 중','이력·지시대장 번호 대조','일치' if h else '이력 없음'])
open(V,'w',encoding='utf-8').write('\n'.join('\t'.join(x) for x in rows)+'\n')
print('추가',add,'전체',len(rows)-1)
