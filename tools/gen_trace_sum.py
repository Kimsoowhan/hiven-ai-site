# 지시 추적 교차 검사 재산출(W19-3 T-W19-32, M-05) — 모델이 직접 실행하는 산출 스크립트(자동 실행 장치 아님)
# 종단: 별도지시대장 행(지시) → 상태 칸으로 결과 판정 / 횡단: 모델통제 이력 행 → 보고서(일일보고·검수대기열·대장) 기재 여부
import re,json,csv,datetime
import os
U='/mnt/user-data/uploads/91_Claude_소통(COM)/91_10_관리/';G=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/cowork/ctl/'  # 11-12 이력 870: 옛 자리 01_클로_소통 → 91_10_관리, 저장소 기준 경로
d=open(U+'대표님_별도지시대장.md',encoding='utf-8').read()
rows=[l for l in d.split('\n') if re.match(r'^\| \d+ \|',l)]
# 11-12: 새 지시대장(command_ledger.tsv, 91_02_01_대표지시)도 종단에 더한다
CL=[r for r in csv.reader(open(G+'command_ledger.tsv',encoding='utf-8'),delimiter='\t') if r and r[0].isdigit()]
V={}
for r in CL:
    st=r[4] if len(r)>4 else ''
    k='일치' if re.search(r'완료|처리됨',st) else '결과 미확정(조치 진행 중)'
    V[k]=V.get(k,0)+1
for l in rows:
    st=l.split('|')[7].strip() if len(l.split('|'))>8 else ''
    k='지시만(기록 없음)' if st in('','—') else '결과 미확정(조치 진행 중)' if re.search(r'진행 중|대기|보류',st) and not re.search(r'완료|처리됨|승인',st) else '일치'
    V[k]=V.get(k,0)+1
lc=list(csv.reader(open(G+'action_lifecycle.tsv',encoding='utf-8'),delimiter='\t'))[1:]
H={'일치':sum(1 for r in lc if r[11]!='아니오'),'보고서 미기재(해제 전 포함)':sum(1 for r in lc if r[11]=='아니오'),'기록만(지시 연결 없음)':0}
now=(datetime.datetime.now(datetime.UTC)+datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
json.dump({'기준':('별도지시대장 %d건 + 지시대장(91_02_01) '+str(len(CL))+'건 × 모델통제 이력 %d건 × 보고서(일일보고 전 워크·검수대기열·대장)')%(len(rows),len(lc)),'종단':V,'횡단':H,'산출':now},open(G+'trace_sum.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(rows),V,H)
