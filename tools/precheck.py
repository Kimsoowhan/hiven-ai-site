#!/usr/bin/env python3
"""수정 뒤 검사(대표님 21:42 질타 재발 방지): 통과하지 못하면 종료 코드 1, 이 경우 커밋·푸시·보고를 하지 않는다.
검사: ① tools/*.py 문법 ② 사이트 js 문법(node --check) ③ cowork/ctl json 형식 ④ 이력 tsv 11칸 ⑤ 색인 생성기 실행 종료 코드 0·산출물 갱신·생명주기 공백 0 ⑥ 무결성 목록
      ⑦ 화면별 자료 신선도(알림) ⑧ 화면 사이 건수 일치(이력 ↔ 생명주기는 실패, 그 밖은 알림) ⑨ 두 저장소 공통 4종 sha256 일치(261112 OJ-3)
261111 H-3: 색인 생성기는 저장소 안 tools/index_build.py 하나만 돌린다(저장소 밖 생성기 의존 없앰). 저장소만 받은 곳에서도 같은 검사가 된다.
사용: python3 tools/precheck.py [--strict] [--gap 시간] [--peer 짝저장소경로]
  --strict  알림도 실패로 본다        --gap N  신선도 간격(시간, 기본 24)
알아 둘 것: ⑤는 색인 생성기를 실제로 돌리므로 cowork/ctl/model_control_index.json의 시각 칸이 바뀐다."""
import sys,os,glob,json,subprocess,py_compile,time,re,csv,datetime
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A=sys.argv[1:];STRICT='--strict' in A;GAP=float(A[A.index('--gap')+1]) if '--gap' in A else 24.0
bad=[];note=[]
def fail(m): bad.append(m); print('실패:',m)
def warn(m): note.append(m); print('알림:',m)
for f in glob.glob(R+'/tools/*.py'):
    try: py_compile.compile(f,doraise=True)
    except Exception as e: fail('문법 '+os.path.basename(f)+' '+str(e)[:120])
for f in glob.glob(R+'/*.js'):
    if subprocess.run(['node','--check',f],capture_output=True).returncode: fail('js 문법 '+os.path.basename(f))
for f in glob.glob(R+'/cowork/ctl/*.json')+[R+'/cowork/publish_meta.json',R+'/cowork/progress.json']:
    try: json.load(open(f,encoding='utf-8'))
    except Exception as e: fail('json '+os.path.basename(f))
C=R+'/cowork/ctl/';H=C+'model_control_history.tsv'
HL=open(H,encoding='utf-8').read().rstrip('\n').split('\n')[1:]
for i,l in enumerate(HL,2):
    if l.count('\t')!=10: fail('이력 %d행 칸 수 %d'%(i,l.count('\t')+1)); break
idx=C+'model_control_index.json'; t0=time.time()
p=subprocess.run([sys.executable,R+'/tools/index_build.py'],cwd=R,capture_output=True,text=True)
if p.returncode: fail('색인 생성기 종료 코드 %d %s'%(p.returncode,(p.stderr or p.stdout)[-160:]))
elif os.path.getmtime(idx)<t0-1: fail('색인 산출물이 갱신되지 않음')
else:
    g=json.load(open(idx,encoding='utf-8'))['lifecycle_gap']
    if g['count']: fail('생명주기 공백 %d건'%g['count'])
g2=subprocess.run([sys.executable,R+'/tools/gen_integrity.py','--check'],capture_output=True,text=True)
if g2.returncode: fail(g2.stdout.strip()+' — tools/gen_integrity.py 실행 필요')

# ── ⑦ 화면별 자료 신선도: 자료 파일 안에 적힌 마지막 시각이 이력의 마지막 시각보다 GAP시간 넘게 뒤처지면 알림(실패 아님)
def T(s):
    s=re.sub(r'(\d{2}:\d)x',r'\g<1>0',str(s or '').strip())  # 「07:5x」처럼 적힌 시각은 그 10분대의 처음으로 읽음
    m=re.search(r'(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})',s)
    if m: return datetime.datetime(*map(int,m.groups()))
    m=re.search(r'(\d{1,2})/(\d{1,2}) (\d{2}):(\d{2})',s)
    if m: return datetime.datetime(2026,*map(int,m.groups()))
    return None
def tsv(f):
    try: return list(csv.reader(open(C+f,encoding='utf-8'),delimiter='\t'))[1:]
    except FileNotFoundError: return None
def J(f):
    try: return json.load(open(f,encoding='utf-8'))
    except Exception: return None
def col(f,i,pre=None):
    r=tsv(f)
    if not r: return None
    v=[T((x[pre]+' ' if pre is not None else '')+x[i]) for x in r if len(x)>i]
    v=[x for x in v if x]; return max(v) if v else None
hist=[T(l.split('\t')[1]+' '+l.split('\t')[3].split(' ')[-1]) for l in HL if l.count('\t')>=3]
hist=[x for x in hist if x]; HT=max(hist) if hist else None
pm=J(R+'/cowork/publish_meta.json') or {}; lcj=J(C+'action_lifecycle.json') or {}; ts=J(C+'trace_sum.json') or {}; ix=J(idx) or {}; pg=J(R+'/cowork/progress.json') or {}; ph=J(C+'phrase_scan.json') or {}
FRESH=[  # (화면, 자료, 자료 안의 마지막 시각)
 ('SC-02·SC-11','publish_meta.json 「published」',T(pm.get('published'))),
 ('SC-02','action_lifecycle.json 「산출」',T(lcj.get('산출'))),
 ('SC-02·SC-16','trace_sum.json 「산출」',T(ts.get('산출'))),
 ('SC-10','progress.json 「updated」',T(pg.get('updated'))),
 ('SC-12','aics_changes.tsv 시각 칸',col('aics_changes.tsv',1)),
 ('SC-13','aics_qa.tsv 결함 줄의 마지막 시각',max([T(x[2]) for x in (tsv('aics_qa.tsv') or []) if x and x[0]=='결함' and T(x[2])] or [None],key=lambda v:v or datetime.datetime.min)),
 ('SC-15','aics_docgen.tsv 마지막 갱신 칸',col('aics_docgen.tsv',5)),
 ('SC-16','model_control_status.tsv 갱신 칸',col('model_control_status.tsv',5)),
 ('SC-17','trace_v.tsv 날짜·시각 칸',col('trace_v.tsv',2,1)),
 ('SC-09','deploy_beta1_events.tsv 시각 칸',col('deploy_beta1_events.tsv',2,1)),
]
print('— 신선도(이력 마지막 시각 %s, 간격 %g시간)'%(HT,GAP))
for sc,nm,t in FRESH:
    if t is None: warn('신선도 %s %s — 시각을 읽지 못함(확인 안 됨)'%(sc,nm)); continue
    if HT and (HT-t).total_seconds()>GAP*3600: warn('신선도 %s %s = %s — 이력보다 %d시간 뒤처짐'%(sc,nm,t.strftime('%m-%d %H:%M'),(HT-t).total_seconds()//3600))

# ── ⑧ 화면 사이 건수 일치: 이력 건수를 쓰는 화면들의 값이 같은가
N=len(HL)
lc=tsv('action_lifecycle.tsv') or []
if len(lc)!=N: fail('건수 SC-02 생명주기 %d줄 ≠ 이력 %d건 — tools/gen_lifecycle.py 실행 필요'%(len(lc),N))
s3=sum((lcj.get('3분류') or {}).values())
if s3!=N: fail('건수 action_lifecycle.json 3분류 합 %d ≠ 이력 %d건'%(s3,N))
CNT=[('SC-02·SC-16 색인 history_rows',ix.get('history_rows')),('SC-11 publish_meta history_rows',pm.get('history_rows')),('SC-11 publish_meta lifecycle_rows',pm.get('lifecycle_rows')),
     ('SC-11 publish_meta 파일표의 이력 건수',next((f.get('rows') for f in pm.get('files',[]) if f.get('file')=='ctl/model_control_history.tsv'),None)),
     ('SC-15 aics_docgen의 생명주기 행 수',next((int(x[4]) for x in (tsv('aics_docgen.tsv') or []) if x[0]=='ctl/action_lifecycle.tsv' and x[4].isdigit()),None)),
     ('SC-02 trace_sum 기준의 이력 건수',(lambda m:int(m.group(1)) if m else None)(re.search(r'이력\s*(\d+)건',ts.get('기준','')))) ]
for nm,v in CNT:
    if v!=N: warn('건수 %s = %s ≠ 이력 %d건'%(nm,v,N))
DF=('지적(자가 발견)','위반','지적','장애')
nd=sum(1 for l in HL if l.split('\t')[5] in DF); qd=sum(1 for x in (tsv('aics_qa.tsv') or []) if x and x[0]=='결함')
if nd!=qd: warn('건수 SC-13 결함 대장 %d건 ≠ 이력의 위반·지적·자가 발견·장애 %d건 — tools/gen_aics_src.py qa 실행 필요'%(qd,nd))
# 화면 쪽 완료 대응표와 산출 쪽 완료 대응표가 같은가(H-2)
try:
    js=re.search(r"HV_ST_DONE=\[([^\]]*)\]",open(R+'/data.js',encoding='utf-8').read()).group(1); py=re.search(r"^DONE=(.*)$",open(R+'/tools/gen_lifecycle.py',encoding='utf-8').read(),re.M).group(1)
    if sorted(re.findall(r"'([^']*)'",js))!=sorted(re.findall(r"'([^']*)'",py)): fail('완료 대응표가 화면(data.js)과 산출(gen_lifecycle.py)에서 다름')
except Exception as e: fail('완료 대응표 읽기 실패 '+str(e)[:80])
# ── ⑨ 두 저장소 공통 4종 정합(Fable 지시문 261112_1940 마-1 OJ-2 · 마-3): 데이터 파일은 「변조」가 아니라 「정합」으로 감시한다.
#    짝 저장소(hiven-ai-site ↔ hiven-ic)의 approval_line · model_control_history · alerts · trace_v sha256이 같아야 통과. 짝을 찾지 못해도 실패(확인 안 됨으로 넘기지 않음).
#    짝 자리: --peer 경로 > 환경 변수 HV_PEER > 이 저장소 옆 폴더(hiven-ic · hs · hiven-ai-site) 중 자기 아닌 것.
import hashlib
COMMON4=('approval_line.tsv','model_control_history.tsv','alerts.tsv','trace_v.tsv')
def _peer():
    if '--peer' in A: return [A[A.index('--peer')+1]]
    if os.environ.get('HV_PEER'): return [os.environ['HV_PEER']]
    up=os.path.dirname(R); return [os.path.join(up,n) for n in ('hiven-ic','hs','hiven-ai-site')]
PEER=next((p for p in _peer() if os.path.isdir(os.path.join(p,'cowork','ctl')) and os.path.realpath(p)!=os.path.realpath(R)),None)
if not PEER: fail('공통 4종 정합: 짝 저장소를 찾지 못함(--peer 경로 또는 HV_PEER 지정)')
else:
    def _h(p):
        try: return hashlib.sha256(open(p,'rb').read()).hexdigest()
        except FileNotFoundError: return None
    diff4=[(n,(_h(C+n) or '없음')[:12],(_h(os.path.join(PEER,'cowork','ctl',n)) or '없음')[:12]) for n in COMMON4 if _h(C+n) is None or _h(C+n)!=_h(os.path.join(PEER,'cowork','ctl',n))]
    if diff4: fail('공통 4종 정합: %d종 다름 %s (짝 %s)'%(len(diff4),'; '.join('%s 이쪽 %s · 짝 %s'%d for d in diff4),PEER))
    else: print('공통 4종 정합: 4/4 같음 (짝 %s)'%PEER)
if STRICT and note: bad+=note
# ── ⑩ 증적 적용 점검(261113 이력 1048): 새 시험·시뮬레이션·에뮬레이터 파일이 증적 등록부에 없으면 실패
_e=subprocess.run([sys.executable,R+'/tools/ev_run.py','check'],capture_output=True,text=True)
_pl=0
for _l in _e.stdout.splitlines():
    if _l.startswith('실패:'): fail('증적 '+_l[3:].strip())
    elif _l.startswith('알림:'): _pl+=1
if _e.returncode not in (0,1): fail('ev_run check 실행 오류 '+(_e.stderr or '')[-120:])
if _pl: warn('증적 등록부 알림 %d건(계획 상태·실행 기록 없음, python3 tools/ev_run.py check)'%_pl)
# ── ⑪ 호출 정책 검사(261113 이력 1113, 법인 설립 전 무료 운영 정책): 외부 저장소를 부르는 60초 미만 주기 호출·옛 목록 호출·누적 집계 누락이면 실패
_c=subprocess.run([sys.executable,R+'/tools/call_policy_check.py'],capture_output=True,text=True)
for _l in _c.stdout.splitlines():
    if _l.startswith('실패:'): fail('호출 정책 '+_l[3:].strip())
    elif _l.startswith('호출 정책 검사'): print(_l)
if _c.returncode not in (0,1): fail('call_policy_check 실행 오류 '+(_c.stderr or '')[-120:])
# ── ⑫ 각서 재서명 점검(261113 이력 1114): 정책·지시문이 바뀌었는데 재서명 요구가 없으면 실패, 서명 대기는 알림
_p=subprocess.run([sys.executable,R+'/tools/pledge_resign.py','check'],capture_output=True,text=True)
for _l in _p.stdout.splitlines():
    if _l.startswith('실패:'): fail('각서 '+_l[3:].strip())
    elif _l.startswith('알림:'): warn(_l[3:].strip())
    elif _l.startswith('각서'): print(_l)
if _p.returncode not in (0,1): fail('pledge_resign 실행 오류 '+(_p.stderr or '')[-120:])
print(('검사 통과' if not bad else '검사 실패 %d건 — 커밋·푸시 금지'%len(bad))+(' · 알림 %d건'%len(note) if note else ''))
sys.exit(1 if bad else 0)
