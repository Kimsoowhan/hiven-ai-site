#!/usr/bin/env python3
# 화면 × 문서 × 폴더 × 분류 연결표(SC-15): 화면 코드(views*.js·data.js·sec*.js)에서 화면마다 읽는 게시 원천을 뽑아
# 실제 파일·만드는 도구·마지막 갱신과 대조한다. 손으로 적는 것은 구조표(sc_structure.tsv)뿐이다.
import re,os,glob,subprocess,sys
C='cowork/ctl/'
js=sorted(glob.glob('views*.js'))+['sec.js','sec2.js','app.js','schedule.js']
order=[];html=open('index.html',encoding='utf-8').read()
for m in re.finditer(r'src="/?([a-z0-9\-]+\.js)',html): order.append(m.group(1))
body={}
for f in [x for x in order if os.path.exists(x)]:
    s=open(f,encoding='utf-8').read()
    ms=list(re.finditer(r"V\['(SC-\d\d)'\]\s*=",s))
    for i,m in enumerate(ms):
        e=ms[i+1].start() if i+1<len(ms) else len(s)
        m2=re.search(r"\n(?:function |var |/\*|\(function|window\.|document\.)",s[m.end():e])   # 화면 정의가 끝나고 다른 코드가 시작하는 자리
        if m2: e=m.end()+m2.start()
        b=s[m.start():e]
        if re.search(r"[A-Za-z0-9_]{3,}\.(?:tsv|json)(?!\()",b) or m.group(1) not in body: body[m.group(1)]=(f,b)   # 원천을 읽는 정의를 씀(덧씌우는 껍데기는 건너뜀)
tools={}
for t in sorted(glob.glob('tools/*.py')):
    s=open(t,encoding='utf-8',errors='ignore').read()
    for m in set(re.findall(r"[A-Za-z0-9_]+\.(?:tsv|json)",s)): tools.setdefault(m,[]).append(t)
def gl(p):
    try: return subprocess.run(['git','log','-1','--format=%cd','--date=format:%Y-%m-%d %H:%M','--',p],capture_output=True,text=True).stdout.strip()
    except Exception: return ''
st=[l.split('\t') for l in open(C+'sc_structure.tsv',encoding='utf-8').read().split('\n')[1:] if l]
import json
M=json.load(open(C+'sc_fetch_measured.json',encoding='utf-8')) if os.path.exists(C+'sc_fetch_measured.json') else {'화면':{},'잰때':''}
ms_={k:set(os.path.basename(x) for x in v['읽은것']) for k,v in M['화면'].items()}
common=set.intersection(*ms_.values()) if ms_ else set()
SHARED=('SC-00','SC-01','SC-17')            # views9.js의 함께 불러오는 묶음(결재·고객 지원·말 명령)을 쓰는 화면
def find(x):
    for q in (C+x,x,'cowork/'+x,'cowork/reports/'+x):
        if os.path.exists(q): return q
    return ''
rows=[];bad=0
for r in st:
    sc=r[0];f,b=body.get(sc,('',''))
    stat=set(re.findall(r"([A-Za-z0-9_]{3,}\.(?:tsv|json))(?!\()",b))
    dyn=(ms_.get(sc,set())-common)|(common if sc in SHARED else set())
    src=sorted(stat|dyn)
    if not f: rows.append([sc,r[1],r[2],'화면 정의 없음','-','없음','','-','','-',r[5],r[6],r[7],'어긋남']);bad+=1;continue
    if not src: rows.append([sc,r[1],r[2],f,'원천 파일을 읽지 않음(화면 코드 안의 값)','-','','-','','실측',r[5],r[6],r[7],'원천에 안 이어짐']);bad+=1;continue
    for x in src:
        p=find(x);n=''
        if p and x.endswith('.tsv'): n=str(max(0,open(p,'rb').read().count(b'\n')-1))
        tl=[t for t in tools.get(x,[]) if 'gen_sc_map' not in t and 'precheck' not in t]
        ok='맞음' if p and tl else ('원천 없음' if not p else '손으로 쓰는 원천')
        if not p: bad+=1
        rows.append([sc,r[1],r[2],f,x,'있음' if p else '없음',n,' · '.join(t.replace('tools/','') for t in tl[:3])+(' 밖 %d'%(len(tl)-3) if len(tl)>3 else '') or '-',gl(p) if p else '','실측' if x in dyn else '코드',r[5],r[6],r[7],ok])
with open(C+'aics_scmap.tsv','w',encoding='utf-8') as o:
    o.write('\t'.join(['화면','이름','흐름 자리','화면 코드','게시 원천(데이터 문서)','존재','행 수','만드는 도구(코드)','마지막 갱신','근거','HiBiz 원천 폴더','HiDAM 분류','문서 규칙','대조'])+'\n')
    for r in rows: o.write('\t'.join(r)+'\n')
import collections
c=collections.Counter(r[-1] for r in rows)
# 폴더 × 화면 덮임표: HiBiz 1층 폴더마다 어느 화면의 원천인지(구조표의 「HiBiz 원천 폴더」 칸에서 폴더 번호를 읽음). 실측이 있을 때만.
TR=C+'hibiz/hibiz_tree.tsv'
if os.path.exists(TR):
    tops=sorted({l.split('\t')[0].split('/')[0] for l in open(TR,encoding='utf-8').read().split('\n')[1:] if l})
    fc=collections.Counter(l.split('\t')[0].split('/')[0] for l in open(TR,encoding='utf-8').read().split('\n')[1:] if l and l.split('\t')[1]=='file')
    use=collections.defaultdict(list)
    for r in st:
        nums=set(re.findall(r'(?<![0-9_])(\d\d)_(?:HIVE|Claude)',r[5]))
        if re.search(r'11~17',r[5]): nums|={'11','12','13','14','15','16','17'}
        if 'NN_' in r[5] and '폴더마다' not in r[5]: nums|={'11','12','13','14','15','16','17'}
        if '폴더마다' in r[5]: nums|={t[:2] for t in tops}
        for t in tops:
            if t[:2] in nums and (t[:2]!='94' or t in r[5] or '폴더마다' in r[5]): use[t].append(r[0])
    cov=[]
    for t in tops:
        own=[x for x in use[t] if x!='SC-15']
        cov.append([t,fc[t],' · '.join(own) or '-','SC-15' if 'SC-15' in use[t] else '-','이어짐' if own else '화면에 안 이어짐(SC-15 실측만)'])
    miss=[r[0]+' '+r[1] for r in st if re.search(r'\d\d_(?:HIVE|Claude)',r[5]) and not any(t.split('_')[0]+'_' in r[5] and t in r[5] or t[:2]+'_' in r[5] for t in tops)]
    with open(C+'aics_cover.tsv','w',encoding='utf-8') as o:
        o.write('HiBiz 1층 폴더\t파일 수\t이 폴더를 원천으로 쓰는 화면\t문서 실측\t덮임\n')
        for r in cov: o.write('\t'.join(str(x) for x in r)+'\n')
    print('덮임',collections.Counter(r[4] for r in cov)); print('안 이어진 폴더:',[r[0] for r in cov if r[4]!='이어짐'])

print('화면',len(st),'줄',len(rows),dict(c))
