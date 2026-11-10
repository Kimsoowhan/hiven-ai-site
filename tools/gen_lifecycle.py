# 조치 생명주기 산출(대표님 11/04 17:40·17:42) — 모델이 실행하는 산출 스크립트(자동 실행 장치 아님, 금지 4조항 준수)
# 입력: 모델통제 이력(게시본), 보고서 3종(일일보고 Opus·Sonnet, Fable 검수대기열, 별도지시대장 — 노트북에서 받은 최신본)
# 출력: cowork/ctl/action_lifecycle.tsv — 번호별 7단계(감지·경고·착수·조치 중·해제·보고서 이관·통제 확인)와 3분류(미조치·조치 중·조치 완료)
import csv,re,datetime,json,sys
C='/home/claude/hiven-ai-site/cowork/ctl/model_control_history.tsv'  # 실행 전 노트북 원천과 같은지 확인(같은 커밋 규칙)
U='/mnt/user-data/uploads/HiBiz/01_클로_소통(COM)/'
import glob
R={('일일보고 '+f.split('일일보고_')[-1][:-4]):f for f in sorted(glob.glob(U+'일일보고/일일보고_*.txt')) if '템플릿' not in f}  # W19-3 T-W19-32: 워크별 일일보고 전부(M-04)
R.update({'Fable 검수대기열':U+'Fable_검수대기열.md','별도지시대장':U+'대표님_별도지시대장.md'})
ref={}
def nums(txt):
  out=set()
  for m in re.finditer(r'이력\s*([0-9][0-9·~,\s번]*)',txt):
    seg=re.sub(r'번','',m.group(1))
    for a in re.finditer(r'(\d+)\s*~\s*(\d+)|(\d+)',seg):
      if a.group(1): out|=set(range(int(a.group(1)),int(a.group(2))+1))
      else: out.add(int(a.group(3)))
  return out
MISS=[]  # 조용한 건너뜀 금지(대표님 11/06 19:53): 원천이 없으면 건너뛰되 반드시 기록·경고
for k,f in R.items():
  try: t=open(f,encoding='utf-8').read()
  except FileNotFoundError:
    MISS.append(k); continue
  for n in nums(t): ref.setdefault(n,[]).append(k)
rows=list(csv.reader(open(C,encoding='utf-8'),delimiter='\t'))[1:]
out=[];cnt={}
for c in rows:
  n=int(c[0]);act=(c[8] or '').strip();st=c[9];fb=c[10] if len(c)>10 else ''
  started=bool(act) and st!='미조치'
  cls='조치 완료' if st in ('조치 완료','완료','처리됨','완료(이름 변경)') else ('미조치' if not started else '조치 중')
  rp='; '.join(ref.get(n,[]))
  stage=('7 통제 확인' if fb not in ('','대기') else '6 보고서 이관' if (cls=='조치 완료' and rp) else '5 해제' if cls=='조치 완료' else '4 조치 중' if started else '2 경고·알람')
  out.append([c[0],c[1],c[3],c[4],c[5],cls,'예','예','예' if started else '아니오','예' if cls!='미조치' else '아니오','예' if cls=='조치 완료' else '아니오',rp or '아니오',fb or '대기',stage])
  cnt[cls]=cnt.get(cls,0)+1
w=csv.writer(open('/home/claude/hiven-ai-site/cowork/ctl/action_lifecycle.tsv','w',encoding='utf-8',newline=''),delimiter='\t',lineterminator='\n')
w.writerow(['번호','날짜','시각','모델','구분','3분류','1 감지','2 경고·알람','3 조치 착수','4 조치 중','5 해제','6 보고서 이관','7 통제 확인','현재 단계'])
w.writerows(out)
import os
try: DM=json.load(open(U+'_device_mtime.json',encoding='utf-8'))  # 노트북 파일 목록의 실제 수정 시각(받은 사본 시각이 아님)
except FileNotFoundError: DM={}
src={k:(datetime.datetime.fromtimestamp(DM[os.path.basename(f)]/1000 if os.path.basename(f) in DM else os.path.getmtime(f),datetime.UTC)+datetime.timedelta(hours=9)).strftime('%m-%d %H:%M') for k,f in R.items()}
if MISS: print('경고: 보고서 원천 누락 %d건(산출 불완전) — %s'%(len(MISS),', '.join(MISS)),file=sys.stderr)
json.dump({'불완전':bool(MISS),'누락 원천':MISS,'산출':(datetime.datetime.now(datetime.UTC)+datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M'),'3분류':cnt,'보고서 기준':src},open('/home/claude/hiven-ai-site/cowork/ctl/action_lifecycle.json','w',encoding='utf-8'),ensure_ascii=False)
print(cnt, sum(1 for o in out if o[11]!='아니오'))
if MISS: sys.exit(2)  # 종료 코드로 알림: 불완전 산출은 통과로 보지 않는다
