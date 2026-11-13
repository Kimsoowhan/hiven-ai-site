#!/usr/bin/env python3
# SC-15 문서 자동 생성·검사: HiBiz 실측(cowork/ctl/hibiz/hibiz_tree.tsv, 로컬 전용)과 문서 규칙표(cowork/ctl/doc_rules.tsv)를 대조한다.
# 내는 것: ① 전체 펼침표(로컬·비공개, 파일마다 한 줄) ② SC-15 게시 원천 aics_doccheck.tsv(폴더×검사 건수), aics_docalert.tsv(얼럿)
#          ③ 폴더별 00 색인 자동 생성본(/mnt/user-data/outputs/hibiz_idx/) ④ 옮길 것 목록
# 쓰는 법: python3 tools/hibiz_doc_check.py [실측 날짜시각 "2026-11-13 18:08"]
import re,sys,os,collections,datetime
C='cowork/ctl/';H=C+'hibiz/';OUT='/mnt/user-data/outputs/hibiz_idx/'
when=sys.argv[1] if len(sys.argv)>1 else ''
YMD=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%y%m%d')
rows=[l.split('\t') for l in open(H+'hibiz_tree.tsv',encoding='utf-8').read().split('\n')[1:] if l]
files=[(p,int(s or 0),m) for p,t,s,m in rows if t=='file'];dirs=[p for p,t,s,m in rows if t=='dir']
tops=sorted({p.split('/')[0] for p,_,_,_ in rows})
NAME=re.compile(r'^(?P<t>.+)-(?P<d>\d{6})(?:_(?P<v>\d+(?:\.\d+)*))?(?P<w>_작업)?(?P<x>[^.]*)\.(?P<e>[A-Za-z0-9]+)$')
# 이름 규칙 예외(DR-14 증적·실측 원본, 코드, 바깥에서 받은 원본)
EXC_DIR=re.compile(r'(시범테스트|실측|증적|증빙|_도구|/도구|개발_코드|기억장치|Mbiz_down|자동_검수_결과|자동화_통제|기준구현|ClaudeHiCoffer|홈페이지|작업대기열|일일보고|태스크|대표지시|워크지시|Fable_전달|삭제전검증|모델통제|outputs|Claude_Fable|Claude_작업|복원지점|실행_도구)')
CODE=('py','js','json','html','css','ps1','cmd','bat','cs','xaml','csproj','sln','log','lnk','ico','key','gz','iss','yml','yaml','toml','lock','map','svg','ttf','otf','woff','woff2','resx','config','manifest','xml','sh','ts','tsx','sha256','sig','exe','dll','msi','0')
STAGE={'00':'색인','01':'기준원칙','02':'사례·벤치마킹','03':'설정안','04':'설계안','05':'수행안','06':'수행결과','07':'품질검수','08':'시범테스트','09':'감리','10':'관리','11':'매뉴얼','12':'자료'}
KW=[('01',r'정책|원칙|규정|지침|표준_|_체계'),('02',r'사례|벤치마킹'),('03',r'설정안|요구사항|정의서'),('04',r'설계안|설계서|시안|보기판|구조도'),('07',r'검수|전수검사|대조표|점검표|검사표'),('08',r'시험_계획|시험_묶음|시험_결과|테스트_결과'),('11',r'매뉴얼|설명서')]
BIZ=('11','12','13','14','15','16','17')
DOCX=('md','txt','tsv','pdf','docx','xlsx','pptx','hwp','csv','html')
ORIG=re.compile(r'(원본|캡처|이용기록|inDownload|PersonInfo|Brand_Assets|Identity_STD|_12_자료|/12_자료|참고자료|career\.html|Work진행현황|외부의견|아이덴티티·이미지)')
def kind(p):
    d,fn=p.rsplit('/',1) if '/' in p else ('',p);e=fn.rsplit('.',1)[-1].lower() if '.' in fn else ''
    if re.search(r'\.A-\d+$',fn) or EXC_DIR.search(d): return '기록·증적'
    if e in CODE: return '코드·실행'
    if e not in DOCX: return '자산 원본'
    if ORIG.search(d): return '바깥·대표 원본'
    return '관리 문서'
find=collections.defaultdict(list)   # 검사 번호 → [(경로, 내용, 처리)]
def add(k,p,why,act): find[k].append((p,why,act))
topdirs=collections.defaultdict(set)
for d in dirs:
    s=d.split('/')
    if len(s)==2: topdirs[s[0]].add(s[1])
byd=collections.defaultdict(list)
for p,sz,m in files: byd[p.rsplit('/',1)[0]].append((p.rsplit('/',1)[1],sz,m))
for t in tops:
    nn=t[:2];idx=[d for d in topdirs[t] if re.match(r'^%s_00_'%nn,d)]
    if not idx: add('K01',t,'색인 폴더(%s_00_색인) 없음'%nn,'색인 폴더를 만들고 자동 색인을 넣음'); continue
    inside=[f for f,_,_ in byd.get(t+'/'+idx[0],[])]
    guide=sorted(f for f in inside if f.startswith('폴더안내'))
    if not guide: add('K02',t+'/'+idx[0],'폴더안내 없음','폴더안내-%s.txt를 넣음'%YMD)
    for g in guide[:-1]: add('K08',t+'/'+idx[0]+'/'+g,'옛 폴더안내가 맨 위에 남음(가장 새 것: %s)'%guide[-1],'이전판 폴더로 옮김')
    if not any(('색인' in f or '하위목록' in f) and not f.startswith('폴더안내') for f in inside): add('K03',t+'/'+idx[0],'색인 문서 없음','자동 색인을 넣음')
for p,sz,m in files:
    s=p.split('/');top=s[0];nn=top[:2];fn=s[-1];d='/'.join(s[:-1])
    if len(s)==2: add('K04',p,'1층 폴더 바로 아래에 파일','맞는 단계 폴더로 옮김')
    ext=fn.rsplit('.',1)[-1].lower() if '.' in fn else ''
    exc=bool(EXC_DIR.search(d)) or ext in CODE or fn.startswith(('_폴더생성','폴더안내'))
    mm=NAME.match(fn)
    if not mm and not exc and kind(p)=='관리 문서': add('K05',p,'이름이 「제목-yymmdd_판」 틀이 아님','이름을 틀에 맞춤(원래 이름은 대조표에 남김)')
    if fn.startswith('_폴더생성') and len(byd[d])==1 and not any(x.startswith(d+'/') for x in dirs): add('K06',d,'표식 파일만 있는 빈 폴더','넣을 산출물이 없으면 폴더를 없앰')
    if nn in BIZ and len(s)==3 and mm and not exc:
        st=s[1][3:5]
        if st in ('12','03','06','10'):
            for k,rx in KW:
                if k!=st and re.search(rx,mm.group('t')) and not (st=='03' and k in('04','01')) :
                    add('K11',p,'제목 열쇳말은 %s_%s 쪽인데 %s에 있음'%(k,STAGE[k],s[1]),'Fable이 보고 맞는 단계 폴더로 옮김'); break
for d in dirs:
    s=d.split('/')
    if len(s)==2 and not re.match(r'^%s_\d\d_'%s[0][:2],s[1]): add('K09',d,'2층 폴더 이름이 NN_dd_이름 틀이 아님','이름을 틀에 맞춤')
    if s[-1].endswith('이전판') and not re.search(r'_02_이전판$',s[-1]): add('K10',d,'이전판 폴더 번호가 02가 아님','NN_dd_02_이전판으로 맞춤')
# K07 같은 제목의 판 여러 개(맨 위에 최종본 하나·작업본 하나만)
def vkey(v): return tuple(int(x) for x in v.split('.')) if v else (0,)
for d,fl in byd.items():
    if '이전판' in d or EXC_DIR.search(d): continue
    g=collections.defaultdict(list)
    for f,sz,m in fl:
        mm=NAME.match(f)
        if mm and mm.group('e').lower() not in CODE: g[(mm.group('t'),mm.group('e').lower())].append((mm.group('d'),vkey(mm.group('v')),bool(mm.group('w')),mm.group('x'),f))
    for (t,e),L in g.items():
        fin=sorted([x for x in L if not x[2] and not x[3]]);wrk=sorted([x for x in L if x[2] and not x[3]])
        keep=set()
        if fin: keep.add(fin[-1][4])
        if wrk and (not fin or wrk[-1][:2]>fin[-1][:2]): keep.add(wrk[-1][4])
        newest=max(L)[4]
        for x in fin+wrk:
            if x[4] not in keep: add('K07',d+'/'+x[4],'새 판(%s)이 있는데 옛 판이 맨 위에 남음'%newest,'이전판 폴더로 옮김')
# K12 겹침(같은 이름·같은 크기가 두 곳 이상, 1KB 넘는 문서만)
dup=collections.defaultdict(list)
for p,sz,m in files:
    fn=p.rsplit('/',1)[1]
    if sz>1024 and NAME.match(fn) and not fn.startswith('폴더안내') and fn.rsplit('.',1)[-1].lower() not in CODE and not EXC_DIR.search(p): dup[(fn,sz)].append(p)
for (fn,sz),L in dup.items():
    if len(L)>1:
        for p in L: add('K12',p,'같은 이름·같은 크기 파일이 %d곳에 있음'%len(L),'해시로 대조한 뒤 원천 한 곳만 남기고 나머지는 경로로 바꿈')
# K13·K14 GS 인증 폴더·설명서
GS='14_HIVEN_HiDAM/14_13_GS인증'
need=[('14_13_00_색인','색인','GS 인증 색인'),('14_13_01_기준원칙','조건_전부','GS 인증 조건표'),('14_13_04_설계안','준비_계획','GS 인증 준비 계획'),('14_13_07_품질검수','자가_점검','GS 자가 점검표'),('14_13_11_인증용_설명서','제품설명서','GS 인증용 제품설명서'),('14_13_11_인증용_설명서','사용자취급설명서','GS 인증용 사용자취급설명서')]
for sub,kw,nm in need:
    if not any(kw in f for f,_,_ in byd.get(GS+'/'+sub,[])): add('K13',GS+'/'+sub,nm+' 없음','만들어 넣음(GS 조건표 GC 번호에 맞춤)')
man=[f for f,_,_ in byd.get('12_HIVEN_HiCoffer/12_11_매뉴얼',[])]
for kw,nm in [('전체_사용자','전체 사용자 매뉴얼'),('고객_지원','고객 지원 대처 매뉴얼'),('기술_관리','기술 관리 매뉴얼'),('기술자','기술자 매뉴얼'),('원천_정리','매뉴얼 원천 정리'),('자가_복구','오프라인 자가 복구 매뉴얼')]:
    if not any(kw in f for f in man): add('K14','12_HIVEN_HiCoffer/12_11_매뉴얼',nm+' 없음','만들어 넣음')
if not any('0.1.27' in f or '사용_설명서' in f for f in man): add('K14','12_HIVEN_HiCoffer/12_11_매뉴얼','0.1.27판 사용 설명서가 원천 자리에 없음','검수 뒤 넣음')
# K15 말 명령 문서 한 줄기(DR-15): 이력 ↔ 지시 대장 ↔ 대표 지시 장 ↔ 아티팩트·메모리 반영 표식(order_sync.tsv)
hist=[l.split('\t') for l in open(C+'model_control_history.tsv',encoding='utf-8').read().split('\n')[1:] if l]
led={l.split('\t')[0] for l in open(C+'command_ledger.tsv',encoding='utf-8').read().split('\n')[1:] if l}
oi={l.split('\t')[0] for l in open(C+'ceo_orders_index.tsv',encoding='utf-8').read().split('\n')[1:] if l}
osy={r[0]:int(r[1]) for r in (l.split('\t') for l in open(C+'order_sync.tsv',encoding='utf-8').read().split('\n')[1:] if l)} if os.path.exists(C+'order_sync.tsv') else {}
last=max(int(r[0]) for r in hist if r[0].isdigit())
for r in hist:
    if not r[0].isdigit() or int(r[0])<1223: continue          # 대장·지시 장을 한 줄기로 묶기 시작한 11-13 15:48 뒤부터 봄
    if r[5] in('지시','질타','개선요청','지적','위반') and '대표님' in r[6]:
        if r[0] not in led: add('K15','이력 '+r[0],'지시 대장에 없음','대장에 올림')
        if r[0] not in oi: add('K15','이력 '+r[0],'대표 지시 장(91_02_01)이 없음','tools/ceo_order_file.py gen 뒤 PC에 올림')
for k,v in osy.items():
    if v<last: add('K15',k,'이력 %d~%d이 아직 반영되지 않음'%(v+1,last),'반영하고 표식을 올림')
# K16 시험 문서(DR-16): 사업군 시험 폴더마다 계획·실행·결과가 있는지, 지금 시험할 판(HiCoffer 0.1.27)의 세 가지가 원천 자리에 있는지
TV='0.1.27';T8='12_HIVEN_HiCoffer/12_08_시범테스트'
t8=[p for p,_,_ in files if p.startswith(T8+'/')]
for kw,nm in [('시험_계획','시험 계획'),('시험_묶음','시험 묶음(실행)')]:   # 시험 결과는 시험이 끝난 뒤에 생기므로 시작 전 판정에서는 보지 않음(끝난 뒤 L4에서 봄)
    if not any(TV in p and (kw in p or kw.replace('시험_','재시험_') in p) for p in t8): add('K16',T8,'%s판 %s 문서가 원천 자리에 없음'%(TV,nm),'만들어 넣음(판·배포 단계 표시, 자산원장에 올림)')
if not any(re.search(r'베타[123]|상용',p) for p in t8): add('K16',T8,'배포 단계(베타1·2·3·상용) 표시가 있는 시험 폴더·문서가 없음','시험 폴더 이름에 판과 배포 단계를 적음')
led14=' '.join(f for f,_,_ in byd.get('14_HIVEN_HiDAM/14_10_관리/14_10_11_자산원장',[]))
if '증적' not in led14: add('K16','14_HIVEN_HiDAM/14_10_관리/14_10_11_자산원장','증적 자산원장이 없음','증적 자산원장을 만듦')
# K17 화면 원천(DR-17): 연결표(aics_scmap.tsv)에서 원천에 안 이어진 화면·없는 원천
if os.path.exists(C+'aics_scmap.tsv'):
    for l in open(C+'aics_scmap.tsv',encoding='utf-8').read().split('\n')[1:]:
        c=l.split('\t')
        if len(c)>13 and c[13] in('원천에 안 이어짐','원천 없음','어긋남'): add('K17',c[0]+' '+c[1],c[13]+': '+c[4],'원천 파일과 만드는 도구에 이음')
# K18 바깥 관계 폴더(DR-18): SC-18·19·20의 원천 폴더와 색인·폴더안내·목록(대장)
for top,kw,nm in [('41_HIVEN_Stakeholder(STK)','Stakeholder_목록','Stakeholder 목록'),('41_HIVEN_Stakeholder(STK)','받은_얼럿','받은 얼럿 기록'),('42_HIVEN_이해관계자_협력사(PTN)','협력사_목록','이해관계자·협력사 목록'),('42_HIVEN_이해관계자_협력사(PTN)','SLA_MOU','협의·SLA·MOU 대장'),('43_HIVEN_계약(CTR)','계약_대장','계약 대장'),('44_HIVEN_이용약관_정책(PCY)','이용약관_정책_목록','이용약관·정책 목록'),('44_HIVEN_이용약관_정책(PCY)','개인정보_처리_대장','개인정보 처리 대장'),('44_HIVEN_이용약관_정책(PCY)','회원_관리_대장','회원 관리 대장'),('44_HIVEN_이용약관_정책(PCY)','베타_설치_대장','베타 설치 대장')]:
    if top not in tops: add('K18',top,'폴더 없음(실측에 없음)','폴더를 만들고 색인·폴더안내·'+nm+'을 넣음')
    elif not any(kw in p for p,_,_ in files if p.startswith(top+'/')): add('K18',top,nm+' 없음','만들어 넣음')
# K19 덮임(대표님 11-13 18:35·18:36): HiBiz 1층 폴더가 어느 화면에도 원천으로 이어지지 않음(범위 = 하이븐 통합사업 전체)
if os.path.exists(C+'aics_cover.tsv'):
    for l in open(C+'aics_cover.tsv',encoding='utf-8').read().split('\n')[1:]:
        c=l.split('\t')
        if len(c)>4 and c[4]!='이어짐': add('K19',c[0],'어느 화면(SC-00~SC-20)에도 원천으로 이어지지 않음','이을 화면을 정해 구조표에 넣음')
# K20 개인정보 처리(DR-19): 처리 대장에서 보유 기간·파기 방법·근거 조항이 정해지지 않은 줄
PIL=C+'pip_ledger.tsv'
if os.path.exists(PIL):
    for l in open(PIL,encoding='utf-8').read().split('\n')[1:]:
        c=l.split('\t')
        if len(c)>8 and any(x.startswith('확인 안 됨') or not x for x in (c[6],c[7],c[8])): add('K20',c[0]+' '+c[1],'보유 기간·파기 방법·근거 조항이 정해지지 않음','처리방침·처리 체계와 대조해 채움')
else: add('K20','개인정보 처리 대장','대장 없음','만듦')
if os.path.exists(C+'policy_list.tsv'):
    for l in open(C+'policy_list.tsv',encoding='utf-8').read().split('\n')[1:]:
        c=l.split('\t')
        if len(c)>6 and (c[6].startswith('확인 안 됨') or c[3].startswith('확인 안 됨')): add('K20',c[0]+' '+c[2],'판 또는 시행 여부가 정해지지 않음','문서를 읽어 판·시행 여부를 채움')
KN={'K01':'색인 폴더 없음','K02':'폴더안내 없음','K03':'색인 문서 없음','K04':'맨 위에 나온 파일','K05':'이름 틀 어긋남','K06':'빈 폴더(표식만)','K07':'옛 판이 맨 위에 남음','K08':'옛 폴더안내 남음','K09':'2층 폴더 이름 어긋남','K10':'이전판 폴더 번호 어긋남','K11':'단계 폴더 어긋남(열쇳말)','K12':'겹친 사본','K13':'GS 인증 자료 빠짐','K14':'설명서 빠짐','K15':'말 명령 문서 빠짐','K16':'시험 문서 빠짐','K17':'화면이 원천에 안 이어짐','K18':'바깥 관계 폴더 빠짐','K19':'화면에 안 이어진 폴더','K20':'약관·정책·개인정보 기준 빠짐'}
KR={'K01':'DR-01','K02':'DR-02','K03':'DR-03','K04':'DR-04','K05':'DR-07','K06':'DR-06','K07':'DR-08','K08':'DR-02','K09':'DR-05','K10':'DR-09','K11':'DR-10','K12':'DR-11','K13':'DR-12','K14':'DR-13','K15':'DR-15','K16':'DR-16','K17':'DR-17','K18':'DR-18','K19':'DR-17','K20':'DR-19'}
GRD={'K06':'의심','K10':'의심','K11':'의심','K12':'의심'}   # 그 밖은 확정(기계로 참·거짓이 갈림)
SEV={'K20':'얼럿','K19':'얼럿','K18':'얼럿','K16':'얼럿','K17':'얼럿','K15':'얼럿','K04':'얼럿','K07':'얼럿','K08':'얼럿','K13':'얼럿','K14':'얼럿','K01':'얼럿','K02':'주의','K03':'주의','K05':'주의','K12':'주의','K11':'확인','K06':'확인','K09':'확인','K10':'확인'}
def W(path,head,body):
    with open(path,'w',encoding='utf-8') as f:
        f.write('\t'.join(head)+'\n')
        for r in body: f.write('\t'.join(str(x).replace('\t',' ').replace('\n',' ') for x in r)+'\n')
# ① 전체 펼침표(비공개)
flag=collections.defaultdict(list)
for k,L in find.items():
    for p,why,act in L: flag[p].append((k,why,act))
mv={}
mp=C+'std/HiBiz_사업군_옮김_대응표-261113_0.1_작업.tsv'
if os.path.exists(mp):
    for l in open(mp,encoding='utf-8').read().split('\n')[1:]:
        c=l.split('\t')
        if len(c)>3: mv[c[1].replace('\\','/')]=(c[2].replace('\\','/'),c[3])
pan=[]
for p,sz,m in files:
    s=p.split('/');fn=s[-1];mm=NAME.match(fn)
    st=STAGE.get(s[1][3:5],'내용 폴더') if len(s)>2 and re.match(r'^\d\d_\d\d_',s[1]) else ('맨 위' if len(s)==2 else '틀 밖')
    fl=flag.get(p,[])
    to,why=mv.get(p,('',''))
    pan.append([s[0],s[1] if len(s)>2 else '',st,kind(p),p,fn,mm.group('d') if mm else '',mm.group('v') or '' if mm else '','작업본' if mm and mm.group('w') else ('최종본' if mm else ''),sz,' · '.join(k+' '+w for k,w,a in fl) or '맞음',' · '.join(dict.fromkeys(a for k,w,a in fl)) or ('옮김(대응표)' if to else '그대로'),to,why])
W(H+'HiBiz_전체_펼침표-%s_0.1_작업.tsv'%YMD,['1층 폴더','2층 폴더','단계','대상 구분','지금 자리(경로)','파일','날짜','판','본 구분','크기','규칙 검사(SC-15)','처리','옮길 자리(대응표)','옮기는 까닭'],pan)
# ② SC-15 게시 원천(건수만, 파일 이름은 싣지 않음)
chk=[]
for k in sorted(KN):
    L=find.get(k,[]);c=collections.Counter((p.split('/')[0][:2] if k not in('K15','K17','K20') else ('91' if k=='K15' else ('SC' if k=='K17' else '44'))) for p,_,_ in L)
    chk.append([k,KN[k],KR[k],('얼럿' if GRD.get(k,'확정')=='확정' and SEV[k]=='얼럿' else ('확정' if GRD.get(k,'확정')=='확정' else '의심(판정 필요)')),len(L),' '.join('%s:%d'%(a,b) for a,b in sorted(c.items())) or '-',L[0][2] if L else '-',when])
W(C+'aics_doccheck.tsv',['검사','무엇을 보는가','규칙','등급','어긋난 건수','폴더별(번호:건수)','처리','실측 시각'],chk)
fc=collections.Counter(p.split('/')[0] for p,_,_ in files);dc=collections.Counter(d.split('/')[0] for d in dirs)
bad=collections.Counter();al=collections.Counter()
for k,L in find.items():
    for p,_,_ in L:
        if k=='K15': p='91_Claude_소통(COM)'
        if k=='K17': continue
        if k=='K20': p='44_HIVEN_이용약관_정책(PCY)'
        bad[p.split('/')[0]]+=1
        if SEV[k]=='얼럿': al[p.split('/')[0]]+=1
W(C+'aics_docfolder.tsv',['1층 폴더','폴더 수','파일 수','어긋난 건수','얼럿 건수','색인 자동 생성','실측 시각'],[[t,dc[t],fc[t],bad[t],al[t],'%s_00_색인_자동-%s'%(t[:2],YMD),when] for t in tops])
W(H+'HiBiz_정리할_것-%s_0.1_작업.tsv'%YMD,['검사','규칙','등급','자리(경로)','무엇이 어긋나는가','처리'],[[k,KR[k],SEV[k],p,w,a] for k in sorted(find) for p,w,a in sorted(find[k])])
# ③ 폴더별 00 색인 자동 생성본
os.makedirs(OUT,exist_ok=True)
for t in tops:
    nn=t[:2];L=['# %s 색인 (자동 생성)'%t,'','- 만든 도구: tools/hibiz_doc_check.py (SC-15 문서 자동 생성) · 실측 %s · 손으로 고치지 않습니다. 다시 실측하면 새 판이 나옵니다.'%when,'- 원천 경로: C:\\Users\\marty\\Documents\\HiBiz\\%s'%t,'- 폴더 %d개 · 파일 %d개 · 규칙에 어긋난 것 %d건(얼럿 %d건)'%(dc[t],fc[t],bad[t],al[t]),'','## 1. 폴더 목록','','| 폴더 | 바로 아래 파일 | 아래 전체 파일 | 가장 새 파일 |','|---|---|---|---|']
    sub=sorted(d for d in dirs if d.startswith(t+'/'))
    for d in sub:
        s=d.split('/')
        if len(s)>3: continue
        own=byd.get(d,[]);allf=[(p,m) for p,_,m in files if p.startswith(d+'/')]
        nw=max(allf,key=lambda x:x[1])[0].rsplit('/',1)[1] if allf else '-'
        L.append('| %s%s | %d | %d | %s |'%('　'*(len(s)-2),s[-1],len(own),len(allf),nw))
    L+=['','## 2. 문서 목록 (단계 폴더 바로 아래, 폴더마다 60개까지)','']
    for d in sub:
        s=d.split('/');own=sorted(byd.get(d,[]))
        if len(s)>3 or not own: continue
        L.append('### %s (%d개)'%('\\'.join(s[1:]),len(own)))
        for f,sz,m in own[:60]:
            fl=flag.get(d+'/'+f,[]);L.append('- %s%s'%(f,'  ← '+' · '.join(k+' '+KN[k] for k,_,_ in fl) if fl else ''))
        if len(own)>60: L.append('- … 그 밖 %d개(전체는 전체 펼침표에 있음)'%(len(own)-60))
        L.append('')
    mine=[(k,p,w,a) for k in sorted(find) for p,w,a in find[k] if p.split('/')[0]==t]
    L+=['## 3. 정리할 것 (%d건)'%len(mine),'']
    if mine:
        L+=['| 검사 | 자리 | 무엇이 어긋나는가 | 처리 |','|---|---|---|---|']
        for k,p,w,a in mine[:80]: L.append('| %s %s | %s | %s | %s |'%(k,KN[k],p[len(t)+1:] or '(1층)',w,a))
        if len(mine)>80: L.append('| … | 그 밖 %d건 | 전체는 「HiBiz_정리할_것」 표에 있음 | |'%(len(mine)-80))
    else: L.append('없음')
    L+=['','## 4. 잇는 곳','','- 규칙: 07_HIVEN_명명분류(STD)\\07_01_기준원칙\\HiBiz_문서_규칙표 (DR-01~14) · 문서 생애 절차(L1~L7)','- 화면: 하이븐 자동화 통합 통제 시스템 SC-15 문서 자동 생성','- HiDAM: 14_HIVEN_HiDAM\\14_10_관리\\14_10_11_자산원장 · 분류 모드 HB-BIZ','- GS 인증: 14_HIVEN_HiDAM\\14_13_GS인증\\14_13_00_색인','']
    open(OUT+'%s_00_색인_자동-%s_0.1_작업.md'%(nn if t!='94_Claude_Fable' else '94F',YMD),'w',encoding='utf-8').write('\n'.join(L))
# ⑤ 싱크 대조: 실측 목록 지문과 앞 실측과의 차이(SC-15 목록 = Dell XPS 15 HiBiz 실측)
import hashlib,shutil
cur={p:(sz,m) for p,sz,m in files}
fp=hashlib.sha256('\n'.join('%s|%d|%s'%(p,cur[p][0],cur[p][1]) for p in sorted(cur)).encode()).hexdigest()
prevp=H+'hibiz_tree_prev.tsv';log=C+'aics_docsync.tsv'
old=[l.split('\t') for l in open(log,encoding='utf-8').read().split('\n')[1:] if l] if os.path.exists(log) else []
if not old or old[-1][2]!=fp:
    if os.path.exists(prevp):
        pv={r[0]:(int(r[2] or 0),r[3]) for r in (l.split('\t') for l in open(prevp,encoding='utf-8').read().split('\n')[1:] if l) if r[1]=='file'}
        new=[p for p in cur if p not in pv];gone=[p for p in pv if p not in cur];chg=[p for p in cur if p in pv and pv[p]!=cur[p]]
        nb=sum(1 for p in new if p in flag)
        W(H+'HiBiz_실측_차이-%s_작업.tsv'%YMD,['갈래','경로','규칙 검사'],[['새로 생김',p,' · '.join(k for k,_,_ in flag.get(p,[])) or '맞음'] for p in sorted(new)]+[['없어짐',p,''] for p in sorted(gone)]+[['바뀜',p,''] for p in sorted(chg)])
        d=[len(new),len(gone),len(chg),nb]
    else: d=['첫 실측','첫 실측','첫 실측',0]
    old.append([when,'Dell XPS 15',fp,len(files),len(dirs)]+d+[sum(len(v) for v in find.values())])
    W(log,['실측 시각','기기','목록 지문(SHA256)','파일 수','폴더 수','새로 생김','없어짐','바뀜','새로 생긴 것 중 규칙 밖','어긋난 건수'],old)
    shutil.copy(H+'hibiz_tree.tsv',prevp)
import collections as _c
kc=_c.Counter(kind(p) for p,_,_ in files)
W(C+'aics_dockind.tsv',['대상 구분','파일 수','거는 규칙','실측 시각'],[[k,kc[k],{'관리 문서':'이름 틀(DR-07) · 판·이전판(DR-08) · 자리(DR-10) · 생애 절차 L1~L7','기록·증적':'이름·내용 불변(DR-14) · 해시 목록 · 보유 기간(DR-19)','자산 원본':'이름 불변 · 자산 대장(HiDAM) · 겹침만 봄','코드·실행':'형상 관리(커밋) · 이름 틀 밖','바깥·대표 원본':'이름 불변 · 받은 그대로 보존'}[k],when] for k in ('관리 문서','기록·증적','자산 원본','코드·실행','바깥·대표 원본')])
fx=sum(len(v) for k,v in find.items() if GRD.get(k,'확정')=='확정');sx=sum(len(v) for k,v in find.items() if GRD.get(k)=='의심')
print('파일',len(files),'폴더',len(dirs),'확정',fx,'의심',sx,dict(kc))
# ⑥ 시험 시작 판정(대표님 11-13 18:33): 얼럿 등급 검사가 모두 0이고 화면 연결표가 모두 맞아야 「시작 가능」
al_n={k:len(find.get(k,[])) for k in KN if GRD.get(k,'확정')=='확정'}
why=[KN[k]+' %d건'%n for k,n in sorted(al_n.items()) if n]
sm_bad=0
if os.path.exists(C+'aics_scmap.tsv'):
    sm_bad=sum(1 for l in open(C+'aics_scmap.tsv',encoding='utf-8').read().split('\n')[1:] if l and l.split('\t')[13]!='맞음')
if sm_bad: why.append('화면 연결표에서 맞지 않는 줄 %d건'%sm_bad)
W(C+'aics_testgate.tsv',['판정','실측 시각','얼럿 건수','까닭','판정 기준'],[['시작 가능' if not why else '시작 불가',when,sum(al_n.values()),' · '.join(why) or '없음','확정 검사(기계로 참·거짓이 갈리는 것) 0건 + 화면 연결표 전부 맞음 + 실측 싱크에서 규칙 밖 새 파일 0. 의심(판정 필요)은 Fable 판정 뒤 확정으로 올리거나 지움']])
sys.stdout.write(''.join('%s %s %s %d\n'%(k,KN[k],SEV[k],len(find.get(k,[]))) for k in sorted(KN)))
