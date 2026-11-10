# 게시 원천 동기화·메타 산출(W19-3 T-W19-31·35, AICS 재설계안 2.0 3장) — 모델이 직접 실행하는 산출 스크립트(자동 실행 장치 아님, 금지 4조항·처리정책 4장 준수)
# 입력: 노트북에서 받은 최신본(진행상황판·일일보고 폴더) + 게시본 cowork/
# 출력: cowork/progress.json(상황판과 같은 상태·점수) · cowork/reports/(일일보고 사본·index.json) · cowork/publish_meta.json(파일별 원천·갱신·건수)
import json,re,os,glob,shutil,csv,hashlib,datetime,sys,subprocess
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 261111: 박힌 경로 대신 저장소 기준
U='/mnt/user-data/uploads/HiBiz/01_클로_소통(COM)/';G=ROOT+'/cowork/'
# 사용: python3 tools/gen_meta.py [실행자]            → 상황판·일일보고(노트북 받은 사본) 동기화 + 메타
#       python3 tools/gen_meta.py --meta-only [실행자] → 저장소 안 파일만으로 메타(publish_meta.json)만 다시 냄. 노트북 원천을 지금 값으로 확인하지 못했을 때 이것만 쓴다
ARGS=[a for a in sys.argv[1:] if not a.startswith('--')];META_ONLY='--meta-only' in sys.argv
KST=lambda:(datetime.datetime.now(datetime.UTC)+datetime.timedelta(hours=9))
BY=ARGS[0] if ARGS else '모델'
def score(st,fb,ap):
    s=st+' '+fb+' '+ap
    if '승인·반영(100)' in st or re.search(r'\d{2}:\d{2} 승인\(대표님\)',ap) or st.startswith('완료·승인'):return 100
    if '통과(G2)' in fb or 'Fable 통과' in st:return 90
    if '완료·검수 대기' in st:return 70
    if '보류' in st or '제외' in st:return 0
    if '진행' in st or '초판' in st or '작성' in st:return 30
    return 0
def sync_progress():
    b=open(U+'CoWork_진행상황판-261104.md',encoding='utf-8').read()
    p=json.load(open(G+'progress.json',encoding='utf-8'));items={i['id']:i for i in p['items']}
    n=0
    for l in b.split('\n'):
        if not re.match(r'^\| W\d+ \|',l):continue
        c=[x.strip() for x in l.split('|')]
        wid,title,own,due,st,out,sc,fb,ap=c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8],c[9]
        sco=score(st,fb,ap)
        if wid=='W19':  # W19-1·2·3 평균(하위 단계 3개)
            sub=[100 if 'W19-1 승인' in st or 'W19-1' in ap else 0, 100 if ('W19-2' in ap or 'W19-2 승인' in st) else 70 if 'W19-2 완료' in st else 0, 100 if ('W19-3 승인' in st or '압축판 T-W19-04~06 승인' in st) else 70 if ('W19-3 완료' in st or 'W19-3 게시 완료' in st) else 30 if 'W19-3 진행' in st else 0]  # W19-3 = 게시 완료(압축판 승인 전) 70
            sco=round(sum(sub)/3)
        it=items.get(wid) or {'id':wid,'title':re.sub(r'\*','',title),'difficulty':'','owner':own,'due':due,'tasks':[]}
        it.update(status=st,score=sco,output=out,self_check=sc or '-',fable=fb or '-',approved=ap or '-',due=due)
        items[wid]=it;n+=1
    p['items']=sorted(items.values(),key=lambda x:int(x['id'][1:]))
    act=[i for i in p['items'] if '제외' not in i['status'] and '보류' not in i['status']]
    p['week']=round(sum(i['score'] for i in act)/len(act));p['week_all']=round(sum(i['score'] for i in p['items'])/len(p['items']))
    for m in ('Opus','Sonnet'):
        mine=[i for i in act if m in i.get('owner','')]
        if mine:p['models'][m]=round(sum(i['score'] for i in mine)/len(mine))
    p['updated']=KST().strftime('%Y-%m-%dT%H:%M:00+09:00')
    json.dump(p,open(G+'progress.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    shutil.copy(U+'CoWork_진행상황판-261104.md',G+'board.md')
    return n
def sync_reports():
    idx=[]
    for f in sorted(glob.glob(U+'일일보고/일일보고_*.txt')):
        nm=os.path.basename(f)
        if '템플릿' in nm:continue
        if re.search(r'Haiku_261104(_1\.[0-3]_작업)?\.txt$',nm):continue  # Haiku 최종본(1.4)만
        shutil.copy(f,G+'reports/'+nm)
        mdl=nm.split('_')[1];w=re.search(r'워크(\d{4})',nm)
        idx.append({'file':nm,'model':mdl,'date':'2026-11-04' if '261104' in nm else '워크 '+w.group(1),'title':nm[:-4]})
    idx.sort(key=lambda x:(x['date'],x['model']),reverse=True)
    json.dump(idx,open(G+'reports/index.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    return len(idx)
def rows(p):
    try:return sum(1 for _ in open(p,encoding='utf-8'))-1
    except FileNotFoundError:return None
def ftime(rel):
    # 게시 파일 시각: 커밋된 그대로면 마지막 커밋 시각(받은 사본의 파일 시각은 받은 때라 사실과 다름), 고친 뒤 아직 커밋 전이면 파일 시각
    g=['git','-c','safe.directory=*']
    try:
        dirty=subprocess.run(g+['status','--porcelain','--','cowork/'+rel],cwd=ROOT,capture_output=True,text=True).stdout.strip()
        if not dirty:
            o=subprocess.run(g+['log','-1','--format=%cd','--date=format-local:%Y-%m-%d %H:%M','--','cowork/'+rel],cwd=ROOT,capture_output=True,text=True,env=dict(os.environ,TZ='Asia/Seoul')).stdout.strip()
            if o:return o
    except Exception as e: print('경고: git 시각 읽기 실패 '+rel+' '+str(e)[:80],file=sys.stderr)
    return datetime.datetime.fromtimestamp(os.path.getmtime(G+rel),datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')
def meta():
    t=KST().strftime('%Y-%m-%d %H:%M')
    F=[('progress.json','COM\\CoWork_진행상황판-261104.md','SC-09',None),('board.md','COM\\CoWork_진행상황판-261104.md','SC-09',None),('log.tsv','—(게시 전용 append)','SC-09','log.tsv'),('reports/index.json','COM\\일일보고\\','SC-09',None),
       ('ctl/model_control_history.tsv','COM\\모델통제(CTL)\\모델통제_통합이력.tsv','SC-01·SC-15','ctl/model_control_history.tsv'),('ctl/model_control_status.tsv','COM\\모델통제(CTL)\\모델통제_현황.tsv','SC-15','ctl/model_control_status.tsv'),
       ('ctl/action_lifecycle.tsv','tools/gen_lifecycle.py 산출','SC-01','ctl/action_lifecycle.tsv'),('ctl/trace_sum.json','지시추적매트릭스(91_Fable)','SC-01·SC-16',None),('ctl/trace_v.tsv','지시추적매트릭스 종단','SC-16','ctl/trace_v.tsv'),
       ('ctl/qa_checks.tsv','승인전재검 xlsx(91_Fable)','SC-01·SC-12','ctl/qa_checks.tsv'),('ctl/bg_lifecycle.tsv','사업부 설정안 6장(AICS 접점)','SC-04','ctl/bg_lifecycle.tsv')]
    out=[]
    for f,src,sc,cnt in F:
        p=G+f
        if not os.path.exists(p):continue
        out.append({'file':f,'source':src,'screen':sc,'rows':rows(G+cnt) if cnt else None,'sha16':hashlib.sha256(open(p,'rb').read()).hexdigest()[:16],'mtime':ftime(f)})
    h=rows(G+'ctl/model_control_history.tsv');l=rows(G+'ctl/action_lifecycle.tsv')
    m={'published':t,'by':BY,'history_rows':h,'lifecycle_rows':l,'consistent':h==l,'files':out}
    json.dump(m,open(G+'publish_meta.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    return m
if __name__=='__main__':
    a,b=('건너뜀','건너뜀') if META_ONLY else (sync_progress(),sync_reports());m=meta();print('progress',a,'reports',b,'history',m['history_rows'],'lifecycle',m['lifecycle_rows'],'consistent',m['consistent'])
