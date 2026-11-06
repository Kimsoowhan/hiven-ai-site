#!/usr/bin/env python3
"""수정 뒤 검사(대표님 21:42 질타 재발 방지): 통과하지 못하면 종료 코드 1, 이 경우 커밋·푸시·보고를 하지 않는다.
검사: ① tools/*.py 문법 ② 사이트 js 문법(node --check) ③ cowork/ctl json 형식 ④ 이력 tsv 11칸 ⑤ 색인 생성기 실행 종료 코드 0·산출물 갱신·생명주기 공백 0.
사용: python3 tools/precheck.py [색인 생성기 폴더, 기본 /tmp/claude-0/mcs]"""
import sys,os,glob,json,subprocess,py_compile,time
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M=sys.argv[1] if len(sys.argv)>1 else '/tmp/claude-0/mcs'
bad=[]
def fail(m): bad.append(m); print('실패:',m)
for f in glob.glob(R+'/tools/*.py')+[M+'/index_build.py',M+'/gen_lc_run.py']:
    if not os.path.exists(f): continue
    try: py_compile.compile(f,doraise=True)
    except Exception as e: fail('문법 '+os.path.basename(f)+' '+str(e)[:120])
for f in glob.glob(R+'/*.js'):
    if subprocess.run(['node','--check',f],capture_output=True).returncode: fail('js 문법 '+os.path.basename(f))
for f in glob.glob(R+'/cowork/ctl/*.json'):
    try: json.load(open(f,encoding='utf-8'))
    except Exception as e: fail('json '+os.path.basename(f))
H=R+'/cowork/ctl/model_control_history.tsv'
for i,l in enumerate(open(H,encoding='utf-8').read().rstrip('\n').split('\n')[1:],2):
    if l.count('\t')!=10: fail('이력 %d행 칸 수 %d'%(i,l.count('\t')+1)); break
idx=R+'/cowork/ctl/model_control_index.json'; t0=time.time()
p=subprocess.run(['python3','index_build.py'],cwd=M,capture_output=True,text=True)
if p.returncode: fail('색인 생성기 종료 코드 %d %s'%(p.returncode,(p.stderr or p.stdout)[-160:]))
elif os.path.getmtime(idx)<t0-1: fail('색인 산출물이 갱신되지 않음')
else:
    g=json.load(open(idx,encoding='utf-8'))['lifecycle_gap']
    if g['count']: fail('생명주기 공백 %d건'%g['count'])
print('검사 통과' if not bad else '검사 실패 %d건 — 커밋·푸시 금지'%len(bad))
sys.exit(1 if bad else 0)
