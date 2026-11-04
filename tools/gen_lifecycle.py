# 조치 생명주기 산출(대표님 11/04 17:40·17:42) — 모델이 실행하는 산출 스크립트(자동 실행 장치 아님, 금지 4조항 준수)
# 입력: 모델통제 이력(게시본), 보고서 3종(일일보고 Opus·Sonnet, Fable 검수대기열, 별도지시대장 — 노트북에서 받은 최신본)
# 출력: cowork/ctl/action_lifecycle.tsv — 번호별 7단계(감지·경고·착수·조치 중·해제·보고서 이관·통제 확인)와 3분류(미조치·조치 중·조치 완료)
import csv,re,datetime,json,sys
C='/home/claude/hiven-ai-site/cowork/ctl/model_control_history.tsv'
U='/mnt/user-data/uploads/HiBiz/01_클로_소통(COM)/'
R={'일일보고 Opus':U+'일일보고/일일보고_Opus_261104.txt','일일보고 Sonnet':U+'일일보고/일일보고_Sonnet_261104.txt','Fable 검수대기열':U+'Fable_검수대기열.md','별도지시대장':U+'대표님_별도지시대장.md'}
ref={}
def nums(txt):
  out=set()
  for m in re.finditer(r'이력\s*([0-9][0-9·~,\s번]*)',txt):
    seg=re.sub(r'번','',m.group(1))
    for a in re.finditer(r'(\d+)\s*~\s*(\d+)|(\d+)',seg):
      if a.group(1): out|=set(range(int(a.group(1)),int(a.group(2))+1))
      else: out.add(int(a.group(3)))
  return out
for k,f in R.items():
  try: t=open(f,encoding='utf-8').read()
  except FileNotFoundError: continue
  for n in nums(t): ref.setdefault(n,[]).append(k)
rows=list(csv.reader(open(C,encoding='utf-8'),delimiter='\t'))[1:]
out=[];cnt={}
for c in rows:
  n=int(c[0]);act=(c[8] or '').strip();st=c[9];fb=c[10] if len(c)>10 else ''
  started=bool(act) and st!='미조치'
  cls='조치 완료' if st=='조치 완료' else ('미조치' if not started else '조치 중')
  rp='; '.join(ref.get(n,[]))
  stage=('7 통제 확인' if fb not in ('','대기') else '6 보고서 이관' if (cls=='조치 완료' and rp) else '5 해제' if cls=='조치 완료' else '4 조치 중' if started else '2 경고·알람')
  out.append([c[0],c[1],c[3],c[4],c[5],cls,'예','예','예' if started else '아니오','예' if cls!='미조치' else '아니오','예' if cls=='조치 완료' else '아니오',rp or '아니오',fb or '대기',stage])
  cnt[cls]=cnt.get(cls,0)+1
w=csv.writer(open('/home/claude/hiven-ai-site/cowork/ctl/action_lifecycle.tsv','w',encoding='utf-8',newline=''),delimiter='\t',lineterminator='\n')
w.writerow(['번호','날짜','시각','모델','구분','3분류','1 감지','2 경고·알람','3 조치 착수','4 조치 중','5 해제','6 보고서 이관','7 통제 확인','현재 단계'])
w.writerows(out)
src={k:(datetime.datetime.fromtimestamp(__import__('os').path.getmtime(f),datetime.UTC)+datetime.timedelta(hours=9)).strftime('%m-%d %H:%M') for k,f in R.items()}
json.dump({'산출':(datetime.datetime.now(datetime.UTC)+datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M'),'3분류':cnt,'보고서 기준':src},open('/home/claude/hiven-ai-site/cowork/ctl/action_lifecycle.json','w',encoding='utf-8'),ensure_ascii=False)
print(cnt, sum(1 for o in out if o[11]!='아니오'))
