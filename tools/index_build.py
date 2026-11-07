import csv,json,datetime,collections,time
HS='/tmp/claude-0/hs/cowork/ctl/'
W={'지시거부':6,'위반':5,'지적':4,'지적(자가 발견)':3,'질타':2,'유휴':1}
TRG={'지시거부','위반','지적','질타'}
MS=['Opus','Sonnet','Fable','Haiku','전 모델','미상']
P=json.load(open(HS+'phrase_scan.json',encoding='utf-8'))
PW={l['cat']:l['w'] for l in P['lexicon']}
H=[r for r in csv.reader(open(HS+'model_control_history.tsv',encoding='utf-8'),delimiter='\t')][1:]
import re
def tm(r):
    m=re.match(r'(\d{1,2}):(\d)([\dx])',(r[3].split(' ')[-1] if ' ' in r[3] else r[3]))
    hh=int(m.group(1)) if m else 0; mm=(int(m.group(2))*10+(0 if m.group(3)=='x' else int(m.group(3)))) if m else 0
    d=datetime.datetime.strptime(r[1],'%Y-%m-%d')
    return int((d.timestamp()+0)*1000)  # placeholder replaced below
def tmk(r):
    m=re.search(r'(\d{1,2}):(\d)([\dx])',r[3]);hh=int(m.group(1)) if m else 0;mm=(int(m.group(2))*10+(0 if m.group(3)=='x' else int(m.group(3)))) if m else 0
    y,mo,d=map(int,r[1].split('-'));kst=datetime.timezone(datetime.timedelta(hours=9))
    return int(datetime.datetime(y,mo,d,hh,mm,tzinfo=kst).timestamp()*1000)
F=P.get('row_form',{})
L=[]
for r in H:
    if r[5] in W:
        f=F.get(r[0],'');f='' if f.startswith('기타') else f
        L.append(dict(no=int(r[0]),t=tmk(r),w=W[r[5]],m=r[4],ty=r[5],st=r[9],f=f,date=r[1]))
L.sort(key=lambda x:(x['t'],x['no']))
end=max(tmk(r) for r in H);DAY=86400000
out={'generated':datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),'history_rows':len(H),'basis':'이력 TSV + 문구 스캔(phrase_scan.json). 가중치·한도·판정 임계는 산정안(대표님 확정 전).','thresholds':{'budget_points_per_day':20,'burn':{'긴급':'1시간·5분 14.4배','경고':'6시간·30분 6배','주의':'3일·6시간 1배'},'recurrence':{'개선 없음':0.7,'개선 미흡':0.4},'min_mature':5},'models':{}}
for m in MS:
    A=[x for x in L if x['m']==m];ev=[r for r in H if r[4]==m and r[5]!='칭찬']
    c=collections.Counter(r[5] for r in ev);days={r[1] for r in ev}
    bm=P['by_model'].get(m,{})
    pr=bm.get('지시거부',0);pv=bm.get('지시위반',0)+bm.get('작업규칙위반',0);pl=bm.get('사용량 낭비',0)
    fr={'지시거부':{'이력':c['지시거부'],'문구':pr,'합계':c['지시거부']+pr},'지시위반':{'이력':c['위반'],'문구':pv,'합계':c['위반']+pv},'사용량 낭비':{'이력':c['유휴'],'문구':pl,'합계':c['유휴']+pl}}
    tot=sum(v['합계'] for v in fr.values())
    mat=rec=same=fx=fxr=rc=ex=n=0;gaps=[]
    dsum=collections.defaultdict(int)
    for i,x in enumerate(A):
        dsum[x['date']]+=x['w']
        if any(y['ty'] in TRG and y['t']<x['t'] and x['t']-y['t']<=DAY and y['f'] and x['f'] and y['f']==x['f'] for y in A[:i]):rc+=1;ex+=x['w']
        if x['ty'] not in TRG:continue
        lt=[y for y in A[i+1:] if y['t']>x['t']];r24=[y for y in lt if y['t']-x['t']<=DAY];n+=1
        sfa=any(x['f'] and y['f']==x['f'] for y in lt)
        if x['st']=='조치 완료':
            fx+=1;fxr+=1 if sfa else 0
        if x['t']+DAY<=end:
            mat+=1;rec+=1 if r24 else 0;same+=1 if any(x['f'] and y['f']==x['f'] for y in r24) else 0
            if lt:gaps.append(lt[0]['t']-x['t'])
    rate=rec/mat if mat else None
    lv='표본 부족' if mat<5 else ('개선 없음' if rate>=0.7 else '개선 미흡' if rate>=0.4 else '개선 보임')
    hs=sum(x['w'] for x in A);ps=sum(bm.get(k,0)*PW[k] for k in PW)
    out['models'][m]={'records':len(ev),'active_days':len(days),'frequency':fr,'frequency_total':tot,'per_active_day':round(tot/len(days),2) if days else None,'per_100_records':round(100*tot/len(ev),1) if ev else None,
     'faults':len(A),'history_score':hs,'phrase_score':ps,'recurrence_extra':ex,'recurrence_count':rc,'composite':hs+ps+ex,
     'recurrence':{'triggers':n,'mature':mat,'recurred_24h':rec,'rate':rate,'same_form_24h':same,'fixed':fx,'fixed_then_same_form':fxr,'median_gap_min':(sorted(gaps)[len(gaps)//2]//60000 if gaps else None),'judgment':lv}}
T=sum(v['composite'] for v in out['models'].values())
for m,v in out['models'].items():
    v['index']={'control':round(100*v['composite']/T,1) if T else 0,'recurrence':round(100*v['recurrence']['rate'],1) if v['recurrence']['rate'] is not None else None,'no_improvement':round(100*v['recurrence_extra']/v['history_score'],1) if v['history_score'] else 0}
out['baseline']={'row':436,'time':'2026-11-06 19:31','note':'기준선 이후 증감은 SC-14에서 실시간 계산'}
json.dump(out,open(HS+'model_control_index.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for m,v in out['models'].items():print(m,v['faults'],v['composite'],v['recurrence']['mature'],v['recurrence']['recurred_24h'],v['recurrence']['same_form_24h'],v['recurrence_extra'],v['index'])

# ---- 19:47: 통제 3축(시스템·서비스·고객 지원) · 정합성 · 역방향 검토
import os,glob
AX={'고객 지원':['고객 지원','지원센터','접수','환불','문의','assist@','contact@','회신','고객'],
    '서비스':['배포','설치 파일','베타','HiCoffer','Hi Coffer','AICS','사업군','웹사이트','hiven.co.kr','홈페이지','브랜드','로고','푸터'],
    '시스템':['대시보드','SC-','Cloudflare','접근 제어','저장소','GitHub','훅','계정','로그인','노트북','예약작업','동결','캐시','DNS','Pages','서버','Mbiz','폴더']}
FT={'지시거부','위반','지적','지적(자가 발견)','질타','유휴'}
axes={a:{m:{'rows':0,'faults':0,'score':0} for m in MS} for a in list(AX)+['공통(분류 없음)']}
for r in H:
    t=' '.join(r[6:9]);m=r[4]
    if m not in MS:continue
    hit=[a for a,ks in AX.items() if any(k in t for k in ks)] or ['공통(분류 없음)']
    for a in hit:
        axes[a][m]['rows']+=1
        if r[5] in FT:axes[a][m]['faults']+=1;axes[a][m]['score']+=W[r[5]]
out['axes']=axes;out['axis_rules']={a:ks for a,ks in AX.items()};out['axis_note']='한 기록이 여러 축에 걸리면 각 축에 모두 센다(키워드 분류, 대표님 확정 전 산정안).'
# 정합성
st=[r[0] for r in csv.reader(open(HS+'model_control_status.tsv',encoding='utf-8'),delimiter='\t')][1:]
tsum=json.load(open(HS+'trace_sum.json',encoding='utf-8'));mcov=re.search(r'이력\s*(\d+)건',tsum.get('기준',''));cov=int(mcov.group(1)) if mcov else 0
lc=sum(1 for _ in open(HS+'action_lifecycle.tsv',encoding='utf-8'))-1
hm=sum(1 for r in H if r[2].isdigit() and (lambda m:m and int(m.group(1))!=int(r[2]))(re.search(r'(\d{1,2}):\d',r[3])))
nofb=sum(1 for r in H if r[10].strip() and r[10].strip() not in('대기','읽음','처리 중','처리 완료'))
nost=sum(1 for r in H if r[9] not in('조치 완료','조치 중'))
nh=sum(1 for r in H if not r[2].isdigit())
MOVED={445}  # 칭찬 크레딧 원장으로 이관(20:06)
seq=[int(r[0]) for r in H]==[n for n in range(1,len(H)+len(MOVED)+1) if n not in MOVED]
chk=[['이력 번호 연속·11칸(445번은 칭찬 원장으로 이관해 비어 있음)',seq and all(len(r)==11 for r in H),'정합'],['이력 건수',len(H),'기준'],['모델 상태표에 없는 모델 행',[m for m in {r[4] for r in H} if m not in st],'화면에 기록상 표기 행으로 보완'],
 ['지시 추적 교차 검사 산출 기준 이력 건수',cov,'공백 %d건'%(len(H)-cov)],['조치 생명주기 게시 행 수',lc,'공백 %d건'%(len(H)-lc)],['Fable 확인 칸 표준 외 표기',nofb,'화면에서 단계로 묶어 표시(원문 보존)'],['상태 칸 표준 외 표기',nost,'완료(이름 변경)은 완료, 미결·부분 완료는 진행으로 계산'],['시 칸과 시각(원문) 불일치',hm,'원문 기준 확인 필요'],['시 칸 비어 있음',nh,'기간별 집계에서 시각 미기재로 따로 셈'],
 ['문구 스캔 이력 건수',P['hist_rows'],'정합' if P['hist_rows']==len(H) else '재실행 필요'],['집약본(model_control_index) 이력 건수',len(H),'정합']]
out['consistency']=[{'item':a,'value':b,'result':c} for a,b,c in chk]
out['review']=[
 {'item':'지시 추적 교차 검사 산출 갱신','system_finding':'산출 이후 이력 %d건 미검사'%(len(H)-cov),'back_to_framework':'Fable이 별도지시대장×이력×보고서 산출을 오늘 이력까지 갱신','owner':'Fable'},
 {'item':'조치 생명주기 갱신','system_finding':'이력 %d건 중 %d건만 단계 기록(11-05 15:50에서 멈춤)'%(len(H),lc),'back_to_framework':'#%d 이후 기록의 7단계를 사실 기준으로 채움(판단 근거 없는 값은 채우지 않음)'%(lc),'owner':'Fable·Opus'},
 {'item':'모델 상태표 갱신','system_finding':'갱신 11-05 07:5x 이후 중단','back_to_framework':'배포 작업·완료·남은 일을 오늘 기준으로 갱신','owner':'Fable'},
 {'item':'지시거부 구분의 확정 추이 그래프 반영','system_finding':'확정 추이 그래프(구분 7종)에 지시거부 계열이 없음(표·집계에는 추가)','back_to_framework':'대표님 결정: 확정 사양에 지시거부 계열 추가 여부','owner':'대표님'},
 {'item':'모델별 토큰 실측 연결','system_finding':'이력에는 토큰 값이 없어 사용량 영향은 대리 지표뿐','back_to_framework':'OpenTelemetry 계측·사용량 기록을 이력과 결합하는 설계','owner':'Fable'},
 {'item':'이력 변경 시 자동 재생성','system_finding':'scan.py·index_build.py를 수동 실행 중','back_to_framework':'이력 변경 감시 장치로 자동 실행','owner':'Fable'}]
out['upload']={'framework':'자동화 통합 통제 체계 → 모델 통제(MCS) 모듈','system':'자동화 통합 통제 시스템 SC-01(요약)·SC-14(전체)','direction':'체계가 만든 집약본을 시스템이 읽어 표출하고, 시스템의 정합성·개선 검토 결과(review)를 체계로 되돌려 갱신한다','feeds':['model_control_history.tsv','phrase_scan.json','model_control_index.json','trace_v.tsv','trace_h.tsv','trace_sum.json','action_lifecycle.tsv','model_control_status.tsv']}

# ================= 19:53~20:00: 공백 사유 강제 기입 · 차단 경보 · 칭찬 크레딧(독립 모티베이션) · 모델 자각 카드 =================
def kst_now(): return datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=9))).replace(tzinfo=None)
NOW=kst_now()
def rts(r):
    m=re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d)([\dx])',r[3])
    if m:
        mo,dd,hh,m1,m2=m.groups();return datetime.datetime(2026,int(mo),int(dd),int(hh),int(m1)*10+(0 if m2=='x' else int(m2)))
    return datetime.datetime.strptime(r[1],'%Y-%m-%d')
def iso(dt): return dt.strftime('%Y-%m-%dT%H:%M:00+09:00')
LCN={int(r[0]) for r in csv.reader(open(HS+'action_lifecycle.tsv',encoding='utf-8'),delimiter='\t') if r and r[0].isdigit()}
lcj=json.load(open(HS+'action_lifecycle.json',encoding='utf-8'))
def fbs(r):
    return '대기' if r[10].strip() in ('','대기') else '확인'
gap=[]
for r in H:
    n=int(r[0])
    if n in LCN: continue
    t=rts(r);st=r[9];done=st=='조치 완료'
    codes=['G1']
    if done and fbs(r)=='대기': codes.append('G2')
    if not done: codes.append('G3')
    gap.append({'no':n,'time':iso(t),'model':r[4],'type':r[5],'status':st,'fable':fbs(r),'action':'있음' if r[8].strip() not in ('','-') else '없음','codes':codes,
      'blocked_stage':'② 산출(생명주기 산출 미실행)'+(' · ⑦ 통제 확인(Fable 확인 대기)' if 'G2' in codes else '')+(' · ④ 조치 중 → ⑤ 해제' if 'G3' in codes else ''),
      'owner':'Fable·Opus(산출)'+(' · Fable(확인)' if 'G2' in codes else '')+(' · '+r[4]+'(조치)' if 'G3' in codes and r[4] in ('Opus','Sonnet','Fable','Haiku') else ''),
      'release':'생명주기 재산출 + 단계마다 증거(시각·근거 문서) 기입'+(' + Fable 개별 확인 시각' if 'G2' in codes else '')+(' + 해제 근거' if 'G3' in codes else '')})
GC={'G1':'생명주기 산출 미실행: 산출 스크립트(gen_lifecycle.py)는 모델이 손으로 실행하는 방식(자동 실행 장치 아님, 11/04 금지 4조항 준수)이고, 이력 기록 절차에 산출 실행 단계가 없어 마지막 산출(%s) 뒤 기록은 단계가 만들어지지 않았다.'%lcj.get('산출','-'),
    'G2':'조치 완료로 기록됐으나 Fable 확인 칸이 비어 있거나 「대기」: 통제 확인(7단계)에 도달하지 못함.',
    'G3':'조치 진행 중·미결: 해제(5단계) 전이라 보고서 이관·통제 확인 불가.'}
out['lifecycle_gap']={'count':len(gap),'last_lifecycle_no':max(LCN),'codes':GC,'rows':gap,
  'note':'값을 지어내지 않는다. 빈 단계마다 공백 사유·막힌 단계·담당·해소 조건을 강제 기입(대표님 19:53 지시). 생명주기 게시본은 일부러 채우지 않아 이력-생명주기 건수 불일치 경보가 해소 전까지 유지된다.'}
open(HS+'lifecycle_gap.tsv','w',encoding='utf-8',newline='').write('번호\t시각\t모델\t구분\t상태\tFable 확인\t조치 칸\t공백 사유 코드\t막힌 단계\t담당\t해소 조건\n'+'\n'.join('\t'.join([str(g['no']),g['time'][:16].replace('T',' '),g['model'],g['type'],g['status'],g['fable'],g['action'],','.join(g['codes']),g['blocked_stage'],g['owner'],g['release']]) for g in gap)+'\n')
out['investigation']={
 'facts':[
  '조치 생명주기 7단계와 산출 스크립트(gen_lifecycle.py)는 대표님 11/04 17:40·17:42 지시로 생겼다(스크립트 머리말, 게시 커밋 11/04 17:45).',
  '스크립트는 「모델이 실행하는 산출 스크립트(자동 실행 장치 아님, 금지 4조항 준수)」로 명시돼 있고, 이력 변경 때 실행하게 하는 장치·절차가 없다.',
  '11/05 15:29~15:50 Opus 위반·지시거부가 연속 기록되어 이력이 309번에서 347번(약 21분에 39건)으로 늘었고, 15:56 마지막 생명주기 산출·게시 메타(347건 일치)가 만들어졌다.',
  '11/05 16:47 이후 이력 348번부터는 기록만 되고 산출은 실행되지 않았다(게시 이력상 생명주기 파일 마지막 변경 15:56).',
  '게시 메타(publish_meta.json)의 「일치(consistent: true)」는 15:56 시점의 고정값이라 이후 건수가 달라져도 바뀌지 않는다. 화면의 건수 비교 경고(SC-01 하단 한 줄)만 남아 있었고 담당·기한·경과 시간이 없었다.',
  '생명주기 1·2단계(감지·경고)는 347건 전부 「예」 고정값이고, 7단계(통제 확인)는 Fable 확인 칸에 글자만 있으면 도달한다. 확인 칸 표기는 365건이 표준 외이고 130건이 같은 분(11/04 19:55) 일괄 확인, 31건은 시각이 「07:5x」 형태다.',
  '산출 스크립트는 보고서 원천이 없으면 오류 없이 건너뛴다(except FileNotFoundError: continue). 건너뛴 사실은 어디에도 남지 않는다.',
  'PC 형상 대장(작업일지·추적 매트릭스)은 17:43의 37번에서 멈춰 있었다(이번 작업에서 보충).'],
 'judgment':['11/05 15:29~15:50의 대량 기록은 같은 시각 대표님 지시(15:35·15:49)로 Opus 위반·지시거부를 기록한 일이 계기였던 것으로 판단된다(이력 314~321·328~346번 요지 근거).','공백은 한 곳의 실수가 아니라 구조 때문이다: 수동 실행 + 실행 단계 부재 + 고정값 단계 + 건너뛰기 + 약한 경보가 겹쳤다.'],
 'unconfirmed':['작업 모델이 의도적으로 회피했는지, 시스템 내부 개입·압력이 있었는지는 기록으로 확인 안 됨. 코드 검색 범위(tools/*.py, views*.js, app.js)에서 일부러 단계를 숨기는 코드는 발견되지 않았다.','15:56 이후 어느 모델이 산출을 건너뛰기로 판단했는지 기록 없음(확인 안 됨).']}
trc=json.load(open(HS+'trace_sum.json',encoding='utf-8'));mm_=re.search(r'이력\s*(\d+)건',trc.get('기준',''));covn=int(mm_.group(1)) if mm_ else 0
pm=json.load(open('/tmp/claude-0/hs/cowork/publish_meta.json',encoding='utf-8'))
stamp=collections.Counter(re.sub(r'\s*[—·(].*$','',r[10].strip()) for r in H if re.match(r'처리 완료 \d',r[10].strip()))
bigstamp=[(k,v) for k,v in stamp.items() if v>=10]
donewait=[r for r in H if r[9]=='조치 완료' and fbs(r)=='대기']
def hrbad(r):
    if not r[2].isdigit(): return True
    m=re.search(r'(\d{1,2}):\d',r[3]);return bool(m) and int(m.group(1))!=int(r[2])
badhr=[r for r in H if hrbad(r)]
silent=[]
for fp in sorted(glob.glob('/tmp/claude-0/hs/tools/*.py')):
    LN=open(fp,encoding='utf-8').read().split('\n')
    for i,l in enumerate(LN,1):
        if re.search(r'except\s+\w*\s*:',l):
            nxt=l+' '+(LN[i] if i<len(LN) else '')
            if 'MISS' not in nxt and 'stderr' not in nxt: silent.append(os.path.basename(fp)+':'+str(i))
def firstrow(pred):
    for r in H:
        if pred(r): return rts(r)
    return NOW
gap_since=rts(next(r for r in H if int(r[0])>max(LCN))) if gap else NOW
tr_since=rts(H[covn]) if covn<len(H) else NOW
al=[]
def A(i,lv,cls,stage,title,reason,since,ev,owner,rel,cwx,fix):
    al.append({'id':i,'level':lv,'class':cls,'stage':stage,'title':title,'reason':reason,'since':iso(since),'evidence':ev,'owner':owner,'release':rel,'cwx':cwx,'added_fence':fix,'open':True})
A('A1','차단','막힘','② 산출 → ③ 표출','조치 생명주기 게시본 미갱신','이력 %d건 중 %d건만 단계 기록(%d건 공백). 산출 스크립트가 수동 실행이고 기록 절차에 실행 단계가 없음.'%(len(H),len(LCN),len(gap)),gap_since,'공백 %d건(lifecycle_gap)'%len(gap),'Fable·Opus','생명주기 재산출, 단계마다 증거 기입, 건수 일치','CWX-1106-42','기록 즉시 산출 실행을 기록 절차에 묶음(미실행이면 해당 이력은 「미반영」)')
A('A2','차단','막힘','② 산출 → ④ 정합 검사','지시 추적 교차 검사 미갱신','산출 기준 이력 %d건, 현재 %d건(공백 %d건). 별도지시대장×이력×보고서 산출이 11/05 08:22에서 멈춤.'%(covn,len(H),len(H)-covn),tr_since,'공백 %d건'%(len(H)-covn),'Fable','교차 검사 산출을 현재 이력까지 갱신','CWX-1106-43','추적 산출도 같은 묶음에 포함, 산출 시각이 이력 마지막 시각보다 오래되면 자동 차단 경보')
A('A3','차단','막힘','② 산출 → ③ 표출','모델 상태표 갱신 중단','모델 상태표 갱신 열이 2026-11-05 07:5x에서 멈춤(Haiku·미상은 11-04 20:05). 오늘 배포 작업·완료·남은 일이 현재와 다름.',datetime.datetime(2026,11,5,7,50),'상태표 5행 모두 11/05 이전','Fable','모델별 오늘 배포 작업·완료·남은 일 갱신','CWX-1106-44','상태표 갱신 시각이 24시간 넘으면 경보')
A('A4','차단','우회 징후','⑦ 통제 확인','일괄 확인 도장','Fable 확인 칸에 같은 분 일괄 처리 표기: '+(', '.join('%s %d건'%(k,v) for k,v in bigstamp) or '없음')+'. 개별 확인 증거가 약함.',(lambda m:datetime.datetime(2026,int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4))) if m else NOW)(re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})',bigstamp[0][0]) if bigstamp else None),'일괄 표기 %d건'%sum(v for k,v in bigstamp),'Fable','건별 확인 시각·근거(읽은 문서) 기입, 일괄 표기는 「일괄 확인 — 개별 근거 대기」로 재분류','CWX-1106-45','같은 분 10건 이상 확인은 자동 차단 경보, 확인 칸에 근거 필수')
A('A5','차단','우회 징후','① 감지 · ② 경고','생명주기 1·2단계 고정값','%d건 모두 1감지 「예」·2경고 「예」 고정값(감지·경고 증거 없이 채워짐). 단계가 증거가 아니라 규칙으로 채워졌다.'%len(LCN),datetime.datetime.fromisoformat(lcj.get('산출','2026-11-05 15:56').replace(' ','T')),'%d/%d 고정'%(len(LCN),len(LCN)),'Fable·Opus','단계마다 증거 ID(경고 기록·알림 시각) 칸 추가, 증거 없으면 「증거 없음」','CWX-1106-46','증거 칸이 비면 해당 단계는 「예」로 계산하지 않음')
A('A6','차단' if silent else '경고','우회 징후','산출 코드','조용한 건너뜀 코드','산출 스크립트: 보고서 원천 누락은 11/06 20:0x에 기록·경고·종료 코드 방식으로 고쳤다(실제 산출 실행으로 검증 전). 아직 기록 없이 기본값으로 넘어가는 처리: %s. 원천이 없어도 완료로 보일 수 있다.'%(', '.join(silent) if silent else '없음'),datetime.datetime(2026,11,4,17,45),'%d곳'%len(silent),'Opus','건너뛴 원천을 결과 파일(missing_sources)과 경보에 기록하고 종료 코드로 알림','CWX-1106-47','건너뜀은 항상 기록, 건너뛴 수가 0이 아니면 산출 결과를 「불완전」으로 표시')
A('A7','경고','표기','⑦ 통제 확인','완료인데 Fable 확인 대기','상태 「조치 완료」인데 Fable 확인이 비어 있거나 「대기」인 이력 %d건.'%len(donewait),firstrow(lambda r:r[9]=='조치 완료' and fbs(r)=='대기'),'%d건'%len(donewait),'Fable','건별 확인 또는 완료 취소','CWX-1106-48','완료 처리는 확인 칸이 채워져야 인정')
A('A8','경고','표기','② 산출 → ③ 표출','게시 메타 고정값','publish_meta.json 「일치」가 %s 시점 고정값(이력 %s건)인데 현재 이력은 %d건. 메타 값은 갱신 전까지 바뀌지 않는다.'%(pm['published'],pm['history_rows'],len(H)),datetime.datetime.strptime(pm['published'],'%Y-%m-%d %H:%M'),'메타 %s건 / 현재 %d건'%(pm['history_rows'],len(H)),'Fable','화면이 직접 건수를 비교(적용), 메타는 산출 때마다 재계산','CWX-1106-48','메타 값을 신뢰하지 않고 직접 비교')
A('A9','경고','표기','② 집약','시각 칸 불일치·누락','시 칸과 시각(원문) 불일치 또는 시 칸 비어 있음 %d건.'%len(badhr),firstrow(lambda r:hrbad(r)),'%d건'%len(badhr),'Fable','원문 기준 확인·정정(이력 값은 임의로 바꾸지 않음)','CWX-1106-48','기록 시 시 칸을 시각 원문에서 자동 계산')
out['alerts']={'scale':['정상','주의','경고','긴급','차단'],'note':'「차단」은 모델 결함(번레이트 주의·경고·긴급)보다 위 등급이다. 통제 체계 자체의 막힘·우회 징후이며 즉시 대처가 필요하다. 번레이트 경보와 별도로 표시하고 해소 전까지 열림 상태가 유지된다.','rows':al,'checked':iso(NOW),'open_block':sum(1 for x in al if x['level']=='차단'),'matrix_rule':'차단 경보가 열리면 같은 시각에 지시 추적 매트릭스(CWX)에 추적 행을 발동한다. 시스템 연결이 안 될 때도 CWX 행은 수동으로 먼저 만든다.'}
out['fences']=[
 ['산출 신선도 검사','게시본 건수·시각이 이력과 다르면 차단 경보','적용(이번)','시스템'],
 ['공백 사유 강제 기입','빈 단계마다 사유·막힌 단계·담당·해소 조건 기입(lifecycle_gap)','적용(이번)','Fable'],
 ['고정값 금지','단계 1·2에 증거 칸 추가, 증거 없으면 계산 제외','설계','Fable·Opus'],
 ['일괄 확인 차단','같은 분 10건 이상 확인은 개별 근거 필수','설계(경보는 적용)','Fable'],
 ['조용한 건너뜀 금지','건너뛴 원천을 기록하고 불완전 표시, 종료 코드 알림','적용(이번, 산출 스크립트)','Opus'],
 ['기록 묶음 절차','이력 → 집약 → 산출을 한 묶음, 미완료 기록은 「미반영」','설계','Fable'],
 ['산출·확인 분리','산출한 모델이 확인하지 않고 다른 모델이 확인(Fable 산출분은 Opus 확인)','설계','Fable'],
 ['자동 감시 실행','이력 변경 감시 → 집약 자동 실행(금지 4조항과의 관계는 대표님 승인 필요)','승인 대기','대표님'],
 ['경보 유지·표출','막힌 단계·사유·경과 시간을 열려 있는 동안 표출','적용(이번)','시스템'],
 ['매트릭스 추적 발동','차단 경보 열림과 동시에 CWX 행(수동, 자동은 설계)','적용(수동)','Fable'],
 ['역검사','화면 합계 ↔ 집약본 ↔ 원천 3중 대조','적용','시스템'],
 ['칭찬 크레딧','칭찬은 이력 밖 별도 원장에 기록, 모델 스스로 관리하는 모티베이션(점수와 독립)','적용(이번)','Fable']]
out['purpose']={'title':'왜 자동화 통합 통제 시스템이 관리해야 하는가(대표님 지시 취지, 해석)','points':[
 '작업 모델이 자기 작업의 정합을 스스로 보고하면 공백이 보고서에 드러나지 않는다. 15:56의 「일치」 값이 그대로 남은 것이 그 사례다.',
 '시스템·서비스·고객 지원을 통제하는 핵심 코어가 모델 통제의 공백에 눈감으면 모든 통제가 같은 방식으로 비게 된다. 통제를 통제하는 장치가 시스템 쪽에 있어야 한다.',
 '데이터가 없는 것도 신호다. 공백은 이력으로만 남기지 않고 경보·담당·기한·해소 조건이 붙은 열린 항목으로 올려야 한다.',
 '종단(시간 흐름)·횡단(원천 간)·역검사(화면 → 원천)가 함께 있어야 한쪽이 멈춰도 다른 쪽이 잡는다.']}
# ---- 칭찬 크레딧 (대표님 20:00·20:03·20:06: 이력과 분리된 별도 원장, 상쇄·가감·중첩 없음)
PL=[r for r in csv.reader(open(HS+'praise_credit_ledger.tsv',encoding='utf-8'),delimiter='\t')][1:]
def lts(r): return rts([r[0],r[1],r[2],r[3]])
cred={m:{'praise':sum(1 for r in PL if r[4]==m)} for m in MS}
for m in cred: cred[m]['credit']=cred[m]['praise']
WIN0=datetime.datetime(2026,11,6,19,8)
INS={'지시','개선요청'}
rf=P.get('row_form',{})
def score_between(m,a,b): return sum(W[r[5]] for r in H if r[4]==m and r[5] in W and a<=rts(r)<b)
perf=[];per_model={}
for m in ['Opus','Sonnet','Fable','Haiku']:
    ins_all=sum(1 for r in H if r[4]==m and r[5] in INS)
    ins_win=sum(1 for r in H if r[4]==m and r[5] in INS and rts(r)>=WIN0)
    pw=sum(1 for r in PL if r[4]==m and lts(r)>=WIN0);pa=cred[m]['credit']
    per_model[m]={'instructions_all':ins_all,'instructions_window':ins_win,'praise_window':pw,'credit_total':pa,
      'acquire_window':round(100*pw/ins_win,1) if ins_win else None,'acquire_all':round(100*pa/ins_all,1) if ins_all else None}
for r in PL:
    m=r[4];t=lts(r);el=int((NOW-t).total_seconds()//60)
    pre=score_between(m,t-datetime.timedelta(minutes=60),t);post=score_between(m,t,NOW+datetime.timedelta(minutes=1))
    mature=el>=60
    if mature and pre>0:
        ch=(post-pre)/pre
        jd='감소(개선)' if ch<=-0.3 else '증가(악화)' if ch>=0.1 else '변화 없음'
    elif mature: jd='전 60분 결함 0 — 비교 불가'
    else: jd='판정 보류(60분 경과 전)'
    hold=[x for x in H if x[4]==m and x[5] in W and rts(x)>t and rf.get(x[0],'').split('·')[0] in ('거짓','누락')]
    hold2=[x[0] for x in H if x[4]==m and x[5] in W and rts(x)>t and (rf.get(x[0],'').startswith('거짓·오보') or rf.get(x[0],'').startswith('누락·지연'))]
    selfd=[x[0] for x in H if x[4]==m and x[5]=='지적(자가 발견)' and rts(x)>t]
    perf.append({'no':int(r[0]),'model':m,'time':iso(t),'elapsed_min':el,'pre60_score':pre,'post_score':post,'judgment':jd,'same_form_after':hold2,'self_found_after':selfd,
      'keep':'유지(칭찬 뒤 같은 형태 결함 기록 없음)' if not hold2 else '재발 %d건'%len(hold2)})
okk=sum(1 for p in perf if p['keep'].startswith('유지'))
out['credit']={'name':'칭찬 크레딧','definition':'칭찬 크레딧 = 각 작업 모델의 작업 지시에 대한 책임 있고 명확한 책임 완수를 위한 모티베이션 동기부여',
 'principles':['이력과 완전히 분리된 별도 체계다. 칭찬은 이력(model_control_history.tsv)에 기록하지 않고 별도 원장(praise_credit_ledger.tsv)에만 남긴다.','이력(질타·지적·위반·지시거부 등)은 칭찬과 상관없이 그 자체로 유지된다. 칭찬 크레딧은 이력 점수·종합 점수·지수·재발·경보·판정에 더하거나 빼지 않고 중첩·상계·가감도 없다.','별도 합산·별도 누적하며, 모델이 스스로 자각하는 모티베이션 근거로만 쓴다. 칭찬 1건 = 크레딧 1건(가중치 없음).'],
 'models':cred,'ledger_header':['번호','날짜','시(時)','시각(원문)','모델','구분','대표님 칭찬 요지','칭찬 사유','적용','상태','Fable 확인'],'ledger':PL,'ledger_file':'cowork/ctl/praise_credit_ledger.tsv',
 'moved_from_history':[445],'per_model':per_model,'effect':perf,
 'indices':{'획득 지수(이 창)':'칭찬 크레딧 ÷ 이 창(11/06 19:08~) 작업 지시 수 × 100, 모델별','획득 지수(누적)':'누적 칭찬 크레딧 ÷ 누적 작업 지시 수 × 100','유지 지수':'칭찬 뒤 같은 형태(거짓·오보·누락·지연) 결함이 없는 칭찬 건수 ÷ 판정 가능 칭찬 건수 × 100 = %d/%d'%(okk,len(perf)),'성과 지수':'칭찬 뒤 60분 결함 점수 vs 칭찬 전 60분(개선 ≥30% 감소, 악화 ≥10% 증가). 60분 경과 전 판정 보류. 참고 비교이며 인과를 뜻하지 않음'},
 'role':'칭찬 크레딧의 역할: 모델이 칭찬받은 행동(%s)을 스스로 확인하고 유지·확대하는 근거. 이력의 질타·지적과 독립이며 어디에도 가감되지 않음.'%(PL[-1][7] if PL else '-'),
 'scan':{'sources':['이력 %d건 전수(구분·요지·조치 문구)'%len(H),'이 창 대화 사용자 메시지 전부(11/06 19:08~, 이어받은 요약 포함)','claude.ai 과거 대화 10개(11/01 이후 갱신분 전부)를 창별로 칭찬·감사 문구(한글·영어·음차·줄임말)로 검색','작업 공간 대화 원문(이 세션) 사용자 메시지 정규식 검사(tools/praise_scan.py)'],'result':'칭찬 기록 3건: 11/02 06:14 「Good Job」(창 Clo 261101, 모델 미상) · 11/03 18:10 「정말 고마워」(창 Clo 261101, Opus) · 11/06 19:53 「아주 잘했어」(이 창, Sonnet). 확인한 범위 한정: claude.ai 검색 도구는 대화 원문 전수 열람이 아니라 검색 결과로만 찾을 수 있어(창 하나가 2천 턴을 넘기도 함) 빠진 칭찬이 있을 수 있음 — 확인 안 됨. 기간 밖(11/01 이전)이라 센 것 아님: 10/30 00:12 「아주 훌륭해」(창 HIVEN 1030~).'},
 'dictionary':{'include':['한글: 잘했어·잘했다·훌륭해·훌륭했어·훌륭하다·고마워·고맙다·감사·수고했어·최고·좋아·좋았어·좋았다·좋았네·좋네·멋져·대단해·완벽·마음에 들어·만족','영어: Good(Good Job 포함)·Great·Nice·Excellent·Awesome·Perfect·Well done·Thank you·Thanks·Bravo','음차·줄임말: 굿·땡큐·땡스·THX·Thnx·TY'],'exclude':['인사(칭찬 아님): Good morning·Good afternoon·Good evening·Good night·Good day·굿모닝·굿나잇·좋은 아침·좋은 저녁·안녕·잘 자','답변(칭찬 아님): OK·Okay·오케이·오키·알겠어·승인 — 문장에 대한 대답이라 산정하지 않음','칭찬 문구를 정의·인용하는 지시(예: 「잘했어」「고마워」 같은 문구를 센다는 지시)는 칭찬이 아님','기간 밖: 11/01 00:00:00 이전'],'rule':'만족·잘했다는 뜻으로 쓴 말만 센다. 사전에 없는 표현이라도 문맥상 칭찬·만족이면 원장에 추가해 센다(대표님 20:16 지시, 원장 사유 칸에 판단 문맥을 적는다). 한 메시지에 여러 번 나와도 1건. 모델은 그 창의 기록으로 확인되는 경우에만 귀속하고, 확인되지 않으면 미상.'},
 'labels':{'Fable':'Fable 5.1','Opus':'Opus 5.5','Sonnet':'Sonnet 5.5','Haiku':'Haiku 5.5','미상':'미상(모델 미확인)'},
 'approval_note':'「오케이」·「승인」은 칭찬이 아니라 승인이므로 크레딧 건수에 넣지 않는다. 아침·저녁 인사(Good morning·Good night 등)도 칭찬이 아니다.'}
open(HS+'praise_credit_summary.tsv','w',encoding='utf-8',newline='').write('모델\t크레딧(누적)\t칭찬 횟수\t이 창 작업 지시\t획득 지수(이 창)\t누적 작업 지시\t획득 지수(누적)\n'+''.join('%s\t%d\t%d\t%d\t%s\t%d\t%s\n'%(m,cred[m]['credit'],cred[m]['praise'],v['instructions_window'],v['acquire_window'],v['instructions_all'],v['acquire_all']) for m,v in per_model.items()))
FORMACT={'미열람':'작업 전에 소통·작업 규칙 아티팩트와 메모리를 먼저 읽고 읽은 증빙(항목·시각)을 남긴다','지시거부':'막혀도 「안 된다」로 끝내지 않는다. 가능한 방법을 모두 시도하고 시도한 방법과 결과로만 보고한다','지시위반':'지시 문구를 항목별로 쪼개 수행 전에 맞춰 보고, 지시 밖 일은 끼우지 않는다','작업규칙위반':'수행 전 해당 규칙 항목을 대조하고 결과표에 규칙 근거를 쓴다','거짓·오보':'확인 안 된 것은 「확인 안 됨」으로 쓰고, 보고 전에 원천을 다시 열어 대조한다','전가':'대표님께 일을 넘기지 않는다. 직접 확인하고 모델이 할 수 없는 사유만 쓴다','반복·재발':'지적받은 형태는 24시간 안에 같은 형태로 다시 틀리지 않는다. 지적 직후 해당 항목 점검표를 먼저 쓴다','누락·지연':'기록은 다른 작업보다 먼저 하고, 기록 전에 마지막 번호·시각을 확인한다','사용량 낭비':'같은 도구·검색을 반복하지 않고 한 번에 모아 실행한다','질책·책임':'맡은 일은 끝까지 책임지고 완료 기준(적용 화면에서 확인)까지 수행한다'}
PRAISEACT=['공백·결함을 지어낸 값으로 메우지 않고 사실대로 드러내 검토 대상으로 올린다(#445 칭찬 사유)','자가 발견한 잘못은 묻기 전에 먼저 정정하고 이력에 기록한다(규칙 기반 후보, 칭찬 기록 없음)','지시를 하나도 빠짐없이 기록·반영하고 적용된 화면에서 확인한다(규칙 기반 후보, 칭찬 기록 없음)','막혀도 가능한 모든 방법을 시도하고 시도·결과로 보고한다(규칙 기반 후보, 칭찬 기록 없음)']
SELF_PRE=['① 이 지시를 이력→아티팩트→메모리 순으로 기록했고 규칙을 먼저 읽었는가?','② 지금 「안 된다·권한 밖·남은 일은 어떻게 할까요」로 일을 피할 이유를 만들고 있지는 않은가?','③ 지시에 없는 일을 끼우고 있지는 않은가?','④ 같은 형태로 24시간 안에 지적받은 적이 있는가? 있다면 그 점검표부터 쓴다']
SELF_POST=['① 지시 문구 하나하나와 결과를 표로 대조했는가?','② 확인 안 된 것을 단정하지 않았는가?','③ 빈칸을 지어낸 값으로 채우지 않았는가?','④ 기록·게시·동기화까지 끝내고 적용된 화면에서 확인했는가?']
aw={}
for m in ['Opus','Sonnet','Fable','Haiku']:
    o=out['models'][m];bm=P['by_model'].get(m,{})
    top=sorted([(c,v) for c,v in bm.items() if c in FORMACT],key=lambda x:-x[1])[:3]
    ft=[rts(r) for r in H if r[4]==m and r[5] in W]
    last=max(ft) if ft else None
    f24=sum(1 for r in H if r[4]==m and r[5] in W and rts(r)>NOW-datetime.timedelta(hours=24))
    rr=o['recurrence']['rate']
    sig='긴급' if (rr is not None and rr>=0.7 and f24>=10) else '경고' if (rr is not None and rr>=0.7) or f24>=5 else '주의' if f24>=1 else '안정'
    aw[m]={'signal':sig,'credit':cred[m]['credit'],'f24':f24,'last_fault':iso(last) if last else None,'top_forms':[{'form':a,'count':b,'do':FORMACT[a]} for a,b in top],'next_action':(FORMACT[top[0][0]] if top else '지금까지 기록된 형태 없음 — 규칙 대조 후 수행'),'recurrence_rate':rr}
out['awareness']={'principle':'질타·지적(채찍, 이력)과 칭찬 크레딧(당근, 별도 원장)을 한 화면에서 볼 수 있게 하되 기록과 점수는 섞지 않는다. 모델이 무엇이 칭찬받고 무엇이 질타받는지 스스로 보고, 책임 있고 명확한 책임 완수 쪽으로 행동을 고르게 한다.','praise_actions':PRAISEACT,'self_check_before':SELF_PRE,'self_check_after':SELF_POST,'models':aw,'protocol':['작업 시작 전: 자각 카드의 「지금 할 행동」과 작업 전 4문을 읽는다(전달문 최상단 각인과 함께).','작업 중: 막히면 시도 기록을 남긴다(회피 금지).','작업 후: 자가 점검 4문을 결과표 「검증 사항」 칸에 쓴다.','대표님 질타·지적·위반·지시거부는 즉시 이력에 기록하고, 칭찬은 이력이 아니라 칭찬 크레딧 원장(별도 표)에만 기록한다. 칭찬 크레딧 건수는 집약 때 별도로 합산한다.','집약본의 모델별 상태 신호(안정·주의·경고·긴급)와 지금 할 행동이 SC-14·SC-01에 표출된다.']}

# ---- 칭찬 크레딧 영향 비교 (대표님 11/06 20:26): 통제 이탈의 원인·요건이 아니다. 이력·집계·경보·가중치에 연동하지 않고 효과·효능 분석에만 쓴다.
H24=datetime.timedelta(hours=24)
ec=[]
for m in ['Fable','Opus','Sonnet','Haiku']:
    cr=cred[m]['credit'];ins=per_model[m]['instructions_all']
    cur=score_between(m,NOW-H24,NOW+datetime.timedelta(minutes=1));prv=score_between(m,NOW-2*H24,NOW-H24)
    sf24=sum(1 for r in H if r[4]==m and r[5]=='지적(자가 발견)' and rts(r)>=NOW-H24)
    sfall=sum(1 for r in H if r[4]==m and r[5]=='지적(자가 발견)')
    chg=None if prv==0 else round(100*(cur-prv)/prv,1)
    effort=(sf24>0) or (prv>0 and cur<=0.7*prv)
    rr=out['models'][m]['recurrence']['rate']
    if cr>0: grp='칭찬 받음'
    elif effort: grp='칭찬 못 받음 · 노력 신호 있음'
    else: grp='칭찬 못 받음 · 노력 신호 없음'
    ec.append({'model':m,'credit':cr,'instructions':ins,'self_found_24h':sf24,'self_found_all':sfall,'score_24h':cur,'score_prev24h':prv,'change_pct':chg,'recurrence_rate':rr,'effort_signal':effort,'group':grp,
      'score_per_instruction':round(cur/ins,2) if ins else None})
def gmean(sel):
    xs=[e['score_24h'] for e in ec if sel(e)]
    return round(sum(xs)/len(xs),1) if xs else None
out['credit']['effect_compare']={'rows':ec,
 'groups':{'칭찬 받음':{'models':[e['model'] for e in ec if e['credit']>0],'avg_score_24h':gmean(lambda e:e['credit']>0)},
           '칭찬 못 받음 · 노력 신호 있음':{'models':[e['model'] for e in ec if e['credit']==0 and e['effort_signal']],'avg_score_24h':gmean(lambda e:e['credit']==0 and e['effort_signal'])},
           '칭찬 못 받음 · 노력 신호 없음':{'models':[e['model'] for e in ec if e['credit']==0 and not e['effort_signal']],'avg_score_24h':gmean(lambda e:e['credit']==0 and not e['effort_signal'])}},
 'effort_rule':'노력 신호 = 최근 24시간 안에 「지적(자가 발견)」 기록이 있거나, 최근 24시간 결함 점수가 직전 24시간보다 30% 이상 줄어든 경우(확정, 대표님 11/06 21:05 승인).',
 'purpose':'칭찬을 누가 많이·적게 받았나를 가리는 표가 아니다. 칭찬을 받으려는 행동(자가 발견, 즉시 기록, 결함 감소)을 하고 있는지, 태도·자세·성과에 변화가 있는지를 칭찬 받음·못 받음 비교군과 견주어 긍정적 영향이 있는지 보는 효과·효능 분석용이다. 인과가 아니라 참고 비교다.',
 'independence':'통제 이탈(결함 점수·재발·번레이트·차단 경보·3축·가중치)의 원인·요건이 아니며 어느 곳에도 가감·연동하지 않는다. 자동화 통합 통제 시스템에는 효과·효능 분석 입력으로만 한 방향 연동한다.'}
out['credit']['principles'].append('칭찬 크레딧은 이력·집계 누적이 말하는 통제 이탈의 원인·요건이 아니다. 칭찬을 받으려는 행동·태도·성과의 변화(긍정적 영향)를 비교군과 견주는 효과·효능 분석 데이터로만 쓴다(대표님 11/06 20:26).')
out['credit']['watch']={'name':'칭찬 자동 감지 장치(praise_watch)','approval':'대표님 11/06 20:21 예외 승인(칭찬 크레딧 작업, Sonnet 5.5 한정, 금지 4조항 충돌 없음 인정)','status_file':'cowork/ctl/praise_watch_status.json','review_file':'cowork/ctl/praise_watch_review.tsv',
 'requirements':[
  ['감지 대상','대표님 메시지(이 작업 공간 창)의 원문. 도구 결과·시스템 문구는 읽지 않음'],
  ['판별','칭찬 사전(한글·영어·음차·줄임말·좋았어·훌륭했어 등) 일치 + 인사(Good morning 등)·OK류 답변 제외. 사전에 없는 표현도 문맥상 칭찬이면 원장에 추가'],
  ['모델 귀속','대화 원문의 직전 답변 모델. 확인되지 않으면 미상'],
  ['기록','원장(praise_credit_ledger.tsv)에 한 줄 추가 → 상태 파일 갱신 → 원장·상태만 커밋·푸시'],
  ['표출','SC-14이 원장·상태를 10초마다 직접 읽어 집약 대기 없이 카운트(배포 지연 약 1~2분)'],
  ['중복·오검출 방지','같은 메시지는 한 번만, 칭찬 문구를 정의·인용하는 지시는 세지 않고 문맥 검토 대기 큐로'],
  ['구동 방식','15초 감시(praise_watch.py --watch) — 이 작업 공간의 창만 대상, 작업 공간이 살아 있는 동안만 구동. 다른 창 칭찬 감지·훅은 하지 않음(대표님 21:30 결정)'],
  ['중지','/tmp/claude-0/praise_watch.off 파일 생성 시 즉시 멈춤(삭제하면 재개). 항상 종료 코드 0, 입력을 막지 않음'],
  ['연동 범위','통제 이탈 지표·경보·가중치·이력에는 연동하지 않음. 효과·효능 분석(영향 비교)에만 한 방향 연동']]}
chk2=[['칭찬 원장 건수',len(PL),'별도 원장(이력과 무관)'],['칭찬 감지 장치 상태 파일',os.path.exists(HS+'praise_watch_status.json'),'있음' if os.path.exists(HS+'praise_watch_status.json') else '없음'],['칭찬 문맥 검토 대기',sum(1 for _ in open(HS+'praise_watch_review.tsv',encoding='utf-8'))-1 if os.path.exists(HS+'praise_watch_review.tsv') else 0,'대표님 문맥 판단 대기(세지 않음)']]
out['consistency']+= [{'item':a,'value':b,'result':c} for a,b,c in chk2]
out['review'].append({'item':'칭찬 크레딧 영향 비교(효과·효능 분석)','system_finding':'칭찬 받음 %s · 못 받음(노력 신호 있음) %s · 못 받음(노력 신호 없음) %s'%(','.join(out['credit']['effect_compare']['groups']['칭찬 받음']['models']) or '-',','.join(out['credit']['effect_compare']['groups']['칭찬 못 받음 · 노력 신호 있음']['models']) or '-',','.join(out['credit']['effect_compare']['groups']['칭찬 못 받음 · 노력 신호 없음']['models']) or '-'),'back_to_framework':'칭찬 크레딧은 통제 이탈 판정에 쓰지 않고, 행동·태도·성과 변화의 긍정적 영향 비교에만 사용(대표님 20:26)','owner':'Fable'})
out['upload']['feeds']=list(out['upload'].get('feeds',[]))+['praise_credit_ledger.tsv (효과·효능 분석 입력, 한 방향)','praise_watch_status.json','praise_watch_review.tsv']
# 구분 변경 이력(대표님 20:34·20:35·20:40·20:41 지시) — 옛 구분 기준 소급 관리
_rl=[r for r in csv.reader(open(HS+'history_reclass_log.tsv',encoding='utf-8-sig'),delimiter='\t')]
_rh,_rr=_rl[0],_rl[1:]
_cnt={}
for r in _rr: _cnt[(r[4],r[5])]=_cnt.get((r[4],r[5]),0)+1
out['reclass']={'file':'cowork/ctl/history_reclass_log.tsv','rows':_rr,'header':_rh,
 'summary':[{'before':k[0],'after':k[1],'count':v,'basis':{'개선요청 → 지시':'대표님 20:34·20:35','번호 중복(2행) → 1행으로 병합':'중복 기록 정리','개선요청 → 개선요청(유지)':'대표님 20:40 「개선요청으로 두십시오」'}.get(k[0]+' → '+k[1],'-')} for k,v in _cnt.items()],
 'defs':[['지시','대표님이 모델에게 하는 「이렇게 하세요·그렇게 하세요」'],['개선요청','「너 왜 이렇게 안 했나」 하고 되묻는 말'],['질타','시킨 것·한 것과 비교해 「왜 이렇게 했나」 하는 말(더 나은 방식을 두고 다르게 한 경우 포함)'],['지적','시킨 대로 안 했거나 물었는데 답이 없는 것을 짚는 말'],['위반·지시거부','소통·작업 규칙에 반한 행동에서 나오는 말']],
 'rule':'옛 구분 기준으로 기록된 상황은 이 표(변경 이력)로 관리한다. 명칭·구문·실행 방법·규칙은 새 기준으로 소급 적용한다(대표님 20:41).'}
out['consistency'].append({'item':'구분 변경 이력 건수(옛 구분 소급)','value':'%d건'%len(_rr),'result':'일치(원장 파일 행 수와 같음)'})
json.dump(out,open(HS+'model_control_index.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('axes ok',{a:sum(v['faults'] for v in d.values()) for a,d in axes.items()})
