#!/usr/bin/env python3
# HiDAM 자산원장 2차(이력 1329 감리): 1차 원장에 없는 HiBiz 실측 줄을 덧붙이는 원장.
# 입력: cowork/ctl/hibiz/hibiz_tree.tsv(실측) · 1차 원장 사본. sha256은 저장소가 원본을 가진 파일만 잼(그 밖은 「재지 않음(목록 실측)」).
#  python3 tools/gen_asset_ledger2.py "<실측 시각>"
import csv,hashlib,sys,os,re,unicodedata,datetime
T=sys.argv[1] if len(sys.argv)>1 else ''
A='/mnt/user-data/uploads/HiBiz/14_HIVEN_HiDAM/14_10_관리/14_10_11_자산원장/HiBiz_자산원장_1차-261112_1.0_작업.tsv'
r1=list(csv.reader(open(A,encoding='utf-8'),delimiter='\t'));H=r1[0]
have={unicodedata.normalize('NFC',x[2]) for x in r1[1:]}
tree=list(csv.reader(open('cowork/ctl/hibiz/hibiz_tree.tsv',encoding='utf-8'),delimiter='\t'))[1:]
# 저장소·내보낸 자리에서 이름과 크기가 같은 원본을 찾아 해시를 잰다
loc={}
for d in ('/mnt/user-data/outputs/audit','/mnt/user-data/outputs/handover','/mnt/user-data/outputs/hibiz_up','cowork/ctl','dl'):
    for b,_,fs in os.walk(d):
        for f in fs:
            p=os.path.join(b,f)
            try: loc.setdefault((unicodedata.normalize('NFC',f),os.path.getsize(p)),p)
            except OSError: pass
out=[H];nh=0
for p,k,sz,mt in tree:
    full='HiBiz\\'+p.replace('/','\\');full=unicodedata.normalize('NFC',full)
    if full in have: continue
    name=full.rsplit('\\',1)[-1];rel=full.split('\\',1)[1]
    aid='HB-'+hashlib.sha1(rel.encode('utf-8')).hexdigest()[:12].upper()
    seg=rel.split('\\');ss='해당없음(최상위)' if len(seg)==1 else (re.match(r'\d\d_(\d\d)',seg[1]).group(1) if re.match(r'\d\d_(\d\d)',seg[1]) else '미부여')
    if k=='dir':
        out.append([aid,'폴더',full,name,'해당없음','현행']+['해당없음(폴더)']*3+['미부여',ss]+['미부여']*4+['해당없음(폴더)','Fable 5.2',T,'해당없음(폴더)','2차: 1차 뒤에 생긴 폴더(목록 실측)'])
    else:
        m=re.search(r'-\d{6}_(\d+(?:\.\d+)+)',name);ver=m.group(1) if m else '판 없음'
        mts=datetime.datetime.fromtimestamp(int(mt)/1000,datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S') if mt else '확인 안 됨'
        lp=loc.get((name,int(sz) if sz else -1))
        if lp: h=hashlib.sha256(open(lp,'rb').read()).hexdigest();hm='sha256(저장소 원본, 이름·크기 같음)';nh+=1
        else: h='재지 않음(목록 실측)';hm='재지 않음'
        out.append([aid,'파일',full,name,ver,'현행' if '_작업' not in name else '작업',h,sz,mts,'미부여',ss]+['미부여']*4+['미판정','Fable 5.2',T,hm,'2차: 1차 원장에 없던 줄'])
o='/mnt/user-data/outputs/audit/HiBiz_자산원장_2차-261113_1.0_작업.tsv'
csv.writer(open(o,'w',encoding='utf-8',newline=''),delimiter='\t',lineterminator='\n').writerows(out)
print('1차 %d줄 · 실측 %d줄 · 2차에 올린 줄 %d(해시 잰 것 %d) → %s'%(len(r1)-1,len(tree),len(out)-1,nh,o))
