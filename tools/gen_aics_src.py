# T-W31-01 AICS 원천 연결 1차(M-13~M-16 + SC-06) — 모델이 직접 실행하는 산출 스크립트(자동 실행 장치 아님, 금지 4조항 준수)
# 입력: 게시본 cowork/ctl/*.tsv · cowork/log.tsv · cowork/reports/index.json · 저장소 git 기록 · 노트북 HV_STD 목록(모델이 device_list_dir로 받은 값, 인자 JSON)
# 출력: cowork/ctl/aics_docgen.tsv(SC-13) · aics_deploy.tsv(SC-06) · aics_cs_cases.tsv(SC-12) · aics_qa.tsv(SC-11) · aics_changes.tsv(SC-10)
import csv,json,os,re,subprocess,sys,hashlib,datetime
R='/home/claude/hiven-ai-site/';C=R+'cowork/ctl/'
def rows(p):
    with open(p,encoding='utf-8') as f: return list(csv.reader(f,delimiter='\t'))
def w(p,head,data):
    with open(C+p,'w',encoding='utf-8',newline='') as f:
        x=csv.writer(f,delimiter='\t',lineterminator='\n');x.writerow(head);x.writerows(data)
def gitlast(path):
    o=subprocess.run(['git','log','-1','--format=%cd|%h','--date=format:%Y-%m-%d %H:%M','--',path],cwd=R,capture_output=True,text=True).stdout.strip()
    return o.split('|') if o else ['확인 안 됨','']
# SC-13 문서 자동 생성: 산출 스크립트가 만든 게시 문서(실제 파일) — 행 수·갱신 커밋
gen=[('ctl/action_lifecycle.tsv','tools/gen_lifecycle.py','SC-01·SC-14'),('ctl/action_lifecycle.json','tools/gen_lifecycle.py','SC-01'),
     ('ctl/trace_sum.json','tools/gen_trace_sum.py','SC-01'),('ctl/trace_v.tsv','tools/gen_trace_supp.py','SC-14'),('ctl/trace_h.tsv','tools/gen_trace_supp.py','SC-14'),
     ('ctl/bg_contact.tsv','tools/gen_contact.py','SC-04'),('progress.json','tools/gen_meta.py','SC-08'),('reports/index.json','tools/gen_meta.py','SC-08'),('publish_meta.json','tools/gen_meta.py','SC-08')]
d=[]
for f,tool,sc in gen:
    p=R+'cowork/'+f
    if not os.path.exists(p): d.append([f,tool,sc,'없음','','',''] );continue
    b=open(p,'rb').read();n=b.count(b'\n')-1 if f.endswith('.tsv') else ''
    t,h=gitlast('cowork/'+f)
    d.append([f,tool,sc,'있음',n,t,h])
w('aics_docgen.tsv',['게시 문서','생성 도구','표출 화면','존재','행 수','마지막 갱신','커밋'],d)
# SC-06 체계 배포: 노트북 HV_STD 분류·규칙 문서 최종본·작업본 판
L=json.load(open(sys.argv[1],encoding='utf-8'))
fam={}
for e in L:
    m=re.match(r'(HIVEN_(?:[^-]*분류[^-]*|자체_분류_체계_인증시험_조건\(기준\)|전사적_서비스_용어집|사업구조_확정서))-(\d{6})_(\d+\.\d+)(_작업)?\.(md|pdf)$',e['name'])
    if not m: continue
    k=m.group(1);v=m.group(3);wk=bool(m.group(4));ts=datetime.datetime.fromtimestamp(e['mtimeMs']/1000,datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')
    f=fam.setdefault(k,{'fin':'','work':'','t':''})
    key='work' if wk else 'fin'
    if tuple(map(int,v.split('.')))>tuple(map(int,(f[key] or '0.0').split('.'))): f[key]=v
    f['t']=max(f['t'],ts)
dd=[[k.replace('HIVEN_','').replace('_',' '),v['fin'] or '—',v['work'] or '—','작업본 승인 대기' if v['work'] else '최종본만',v['t']] for k,v in sorted(fam.items())]
w('aics_deploy.tsv',['문서','최종본 판','작업본 판','상태','마지막 수정(노트북)'],dd)
# SC-12 고객 지원 사례 원장(DR-07~15 열) — 베타1 배포 전이라 접수 0건(실측), 행은 접수 시 추가
w('aics_cs_cases.tsv',['사례 번호','서비스','채널','접수 시각','첫 응답 시각','종결 시각','응답 기한','진행 단계','상태'],[])
# SC-11 검수·품질: qa_checks(자동 검수) + 결함 대장 = 모델통제 이력의 지적(자가 발견)·위반 행
H=rows(C+'model_control_history.tsv')[1:]
q=[[r[0],r[1],r[2],'자동 검수 기록'] for r in rows(C+'qa_checks.tsv')[1:]]
dfx=[[r[0],r[3],r[4],r[5],r[6][:80],r[9]] for r in H if len(r)>9 and r[5] in ('지적(자가 발견)','위반','지적','장애')]
w('aics_qa.tsv',['구분','번호·검사','시각·마지막 실행','모델·결과','내용','상태'],[['자동 검수',x[0],x[1],x[2],'',''] for x in q]+[['결함',x[0],x[1],x[2]+' · '+x[3],x[4],x[5]] for x in dfx])
# SC-10 형상·변경: 게시 저장소 커밋 기록(최근 30)
o=subprocess.run(['git','log','-30','--date=format:%Y-%m-%d %H:%M','--format=%h\t%cd\t%s','--shortstat'],cwd=R,capture_output=True,text=True).stdout
ch=[];cur=None
for l in o.split('\n'):
    if '\t' in l: cur=l.split('\t');cur[2]=cur[2][:90];cur.append('');ch.append(cur)
    elif 'changed' in l and cur: cur[3]=re.sub(r' files? changed','개 파일',l.split(',')[0].strip())
w('aics_changes.tsv',['커밋','시각','내용','바뀐 파일'],ch)
print('docgen',len(d),'deploy',len(dd),'cs',0,'qa',len(q),'+',len(dfx),'changes',len(ch))
