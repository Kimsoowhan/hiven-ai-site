# T-W31-01 AICS 원천 연결 1차(M-13~M-16 + SC-08) — 모델이 직접 실행하는 산출 스크립트(자동 실행 장치 아님, 금지 4조항 준수)
# 입력: 게시본 cowork/ctl/*.tsv · cowork/log.tsv · cowork/reports/index.json · 저장소 git 기록 · 노트북 HV_STD 목록(모델이 device_list_dir로 받은 값, 인자 JSON)
# 출력: cowork/ctl/aics_docgen.tsv(SC-15) · aics_deploy.tsv(SC-08) · aics_cs_cases.tsv(SC-14) · aics_qa.tsv(SC-13) · aics_changes.tsv(SC-12)
import csv,json,os,re,subprocess,sys,hashlib,datetime
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/';C=R+'cowork/ctl/'  # 261111: 박힌 경로 대신 저장소 기준
GIT=['git','-c','safe.directory=*'];ENV=dict(os.environ,TZ='Asia/Seoul')
# 사용(261111): python3 tools/gen_aics_src.py [갈래 …] [HV_STD 목록.json]
#   갈래 = docgen · cs · qa · changes  (안 적으면 넷 모두). HV_STD 목록(json)을 주면 deploy도 낸다. 목록이 없으면 deploy(SC-08)는 건드리지 않는다(노트북 원천을 지금 값으로 모르면 다시 내지 않음).
#   changes = aics_changes.tsv의 내용(손으로 적은 설명)은 그대로 두고 시각 칸만 커밋 시각으로 맞춘다(D-5). 저장소에 없는 해시는 적힌 시각을 그대로 둔다.
A=sys.argv[1:];LST=[a for a in A if a.endswith('.json')];SEL=[a for a in A if not a.endswith('.json')] or ['docgen','cs','qa','changes']
def rows(p):
    with open(p,encoding='utf-8') as f: return list(csv.reader(f,delimiter='\t'))
def w(p,head,data):
    with open(C+p,'w',encoding='utf-8',newline='') as f:
        x=csv.writer(f,delimiter='\t',lineterminator='\n');x.writerow(head);x.writerows(data)
def gitlast(path):
    o=subprocess.run(GIT+['log','-1','--format=%cd|%h','--date=format-local:%Y-%m-%d %H:%M','--',path],cwd=R,capture_output=True,text=True,env=ENV).stdout.strip()
    return o.split('|') if o else ['확인 안 됨','']
# SC-15 문서 자동 생성: 산출 스크립트가 만든 게시 문서(실제 파일) — 행 수·갱신 커밋
gen=[('ctl/action_lifecycle.tsv','tools/gen_lifecycle.py','SC-02·SC-16'),('ctl/action_lifecycle.json','tools/gen_lifecycle.py','SC-02'),
     ('ctl/trace_sum.json','tools/gen_trace_sum.py','SC-02'),('ctl/trace_v.tsv','tools/gen_trace_supp.py','SC-16'),('ctl/trace_h.tsv','tools/gen_trace_supp.py','SC-16'),
     ('ctl/bg_contact.tsv','tools/gen_contact.py','SC-05'),('progress.json','tools/gen_meta.py','SC-10'),('reports/index.json','tools/gen_meta.py','SC-10'),('publish_meta.json','tools/gen_meta.py','SC-10'),
     ('ctl/aics_doccheck.tsv','tools/hibiz_doc_check.py','SC-15'),('ctl/aics_docfolder.tsv','tools/hibiz_doc_check.py','SC-15'),('ctl/aics_docsync.tsv','tools/hibiz_doc_check.py','SC-15'),('ctl/aics_scmap.tsv','tools/gen_sc_map.py','SC-15'),('ctl/sc_fetch_measured.json','tools/sc_fetch_measure.js','SC-15'),('ctl/aics_testgate.tsv','tools/hibiz_doc_check.py','SC-15')]
d=[]
if 'docgen' in SEL:
 for f,tool,sc in gen:
     p=R+'cowork/'+f
     if not os.path.exists(p): d.append([f,tool,sc,'없음','','',''] );continue
     b=open(p,'rb').read();n=b.count(b'\n')-1 if f.endswith('.tsv') else ''
     t,h=gitlast('cowork/'+f)
     d.append([f,tool,sc,'있음',n,t,h])
 w('aics_docgen.tsv',['게시 문서','생성 도구','표출 화면','존재','행 수','마지막 갱신','커밋'],d)
# SC-08 체계 배포: 노트북 HV_STD 분류·규칙 문서 최종본·작업본 판
dd=[]
if LST:
 L=json.load(open(LST[0],encoding='utf-8'))
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
else: print('알림: HV_STD 목록이 없어 aics_deploy.tsv(SC-08)는 다시 내지 않음',file=sys.stderr)
# SC-14 고객 지원 사례 원장(DR-07~15 열) — 베타1 배포 전이라 접수 0건(실측), 행은 접수 시 추가
# 261111 H-4: 열 더함 — 회원 번호(MBR) · 갈래(가·나·다) · 종결 방식(챗봇·사람·통제) · 자동 접수(예·아니오) · 문구 번호(MSG). 이름·경로·내용 칸은 두지 않는다(UM-06·UD-15). 사례 번호 형식 CASE-서비스-주제-번호
CSH=['사례 번호','서비스','채널','접수 시각','첫 응답 시각','종결 시각','응답 기한','진행 단계','상태','회원 번호','갈래','종결 방식','자동 접수','문구 번호']
if 'cs' in SEL:
 old=rows(C+'aics_cs_cases.tsv')[1:] if os.path.exists(C+'aics_cs_cases.tsv') else []
 w('aics_cs_cases.tsv',CSH,[r+['']*(len(CSH)-len(r)) for r in old])  # 있던 줄은 지우지 않고 빈 칸만 채움
# SC-13 검수·품질: qa_checks(자동 검수) + 결함 대장 = 모델통제 이력의 지적(자가 발견)·위반 행
q=[];dfx=[]
if 'qa' in SEL:
 H=rows(C+'model_control_history.tsv')[1:]
 q=[[r[0],r[1],r[2],'자동 검수 기록'] for r in rows(C+'qa_checks.tsv')[1:]]
 dfx=[[r[0],r[3],r[4],r[5],r[6][:80],r[9]] for r in H if len(r)>9 and r[5] in ('지적(자가 발견)','위반','지적','장애')]
 w('aics_qa.tsv',['구분','번호·검사','시각·마지막 실행','모델·결과','내용','상태'],[['자동 검수',x[0],x[1],x[2],'',''] for x in q]+[['결함',x[0],x[1],x[2]+' · '+x[3],x[4],x[5]] for x in dfx])
# SC-12 형상·변경: 게시 저장소 커밋 기록(최근 30)
ch=[]
if 'changes' in SEL:
 cur=rows(C+'aics_changes.tsv');fix=[]
 for r in cur[1:]:
  o=subprocess.run(GIT+['show','-s','--format=%cd','--date=format-local:%Y-%m-%d %H:%M',r[0]],cwd=R,capture_output=True,text=True,env=ENV)
  t=o.stdout.strip() if o.returncode==0 else ''
  if t and t!=r[1]: fix.append([r[0],r[1],t]);r[1]=t
  ch.append(r)
 w('aics_changes.tsv',cur[0],ch)
 if fix:
  fp='aics_changes_timefix.tsv';old=rows(C+fp)[1:] if os.path.exists(C+fp) else []
  w(fp,['커밋','적혀 있던 시각','커밋 시각(맞춘 값)'],old+fix)  # 바꾸기 전 값 대조표(쌓임)
 print('changes 시각 맞춤',len(fix),'건 / 전체',len(ch),file=sys.stderr)
print('docgen',len(d),'deploy',len(dd),'cs',0,'qa',len(q),'+',len(dfx),'changes',len(ch))
