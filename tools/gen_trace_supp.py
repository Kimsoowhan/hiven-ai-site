"""W19-07(Opus 11/05): 지시추적매트릭스 보충표(S01~, 11/04 18:27 이후)를 cowork/ctl/trace_v.tsv 뒤에 합친다.
매트릭스 2.0(18:26까지) 행은 그대로 두고, 순번이 S로 시작하는 행만 지우고 다시 붙인다(여러 번 돌려도 같은 결과).
사용: python tools/gen_trace_supp.py <보충표 xlsx 경로>"""
import sys,csv,openpyxl,os
G=os.path.join(os.path.dirname(__file__),'..','cowork','ctl','trace_v.tsv')
rows=list(csv.reader(open(G,encoding='utf-8'),delimiter='\t'))
head,body=rows[0],[r for r in rows[1:] if not r[0].startswith('S')]
ws=openpyxl.load_workbook(sys.argv[1],data_only=True).worksheets[0]
add=[]
for r in list(ws.iter_rows(values_only=True))[1:]:
    if not r or not r[0]:continue
    s=lambda i:'' if i>=len(r) or r[i] is None else str(r[i]).replace('\t',' ').replace('\n',' ')
    st=s(8);judge='일치' if ('완료' in st or '승인' in st) else ('결과 미확정(조치 진행 중)' if st else '해당 없음')
    add.append([s(0),s(1),s(2),s(3),s(4),s(5),s(6),s(7),st,s(9),'반영' if judge=='일치' else '진행',s(10),judge])
w=csv.writer(open(G,'w',encoding='utf-8',newline=''),delimiter='\t',lineterminator='\n')
w.writerow(head);[w.writerow(x) for x in body+add]
print('매트릭스 %d행 + 보충 %d행 = %d행'%(len(body),len(add),len(body)+len(add)))
