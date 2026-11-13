#!/usr/bin/env python3
# 대표 지시 장 ↔ PC 91_02_01_대표지시 맞춤(이력 1180). SC-17 말 명령의 자료는 그 폴더에 반드시 있어야 한다.
#  python3 tools/ceo_pc_sync.py pending   → 올려야 할 장 목록(올릴 사본은 /mnt/user-data/outputs/ceo_up/ 에 놓음)
#  python3 tools/ceo_pc_sync.py verify    → PC에서 다시 받은 사본(/mnt/user-data/uploads/…/91_02_01_대표지시/)과 md5를 맞대어 같은 장만 ceo_orders_pc.tsv 에 적음
import os,sys,hashlib,shutil
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/cowork/ctl/';PC=R+'ceo_orders_pc.tsv'
UP='/mnt/user-data/uploads/91_Claude_소통(COM)/91_02_지시문/91_02_01_대표지시/';O='/mnt/user-data/outputs/ceo_up/'
md=lambda f:hashlib.md5(open(f,'rb').read()).hexdigest()
def load():
    d={}
    if os.path.exists(PC):
        for l in open(PC,encoding='utf-8'):
            c=l.rstrip('\n').split('\t')
            if len(c)>1: d[c[0]]=c[1]
    return d
def pend():
    pc=load();out=[]
    for d in ('ceo_orders','ceo_turns'):
        for f in sorted(os.listdir(R+d)):
            if pc.get(f)!=md(R+d+'/'+f): out.append((d,f))
    return out
a=sys.argv[1] if len(sys.argv)>1 else 'pending';P=pend()
if a=='pending':
    shutil.rmtree(O,ignore_errors=True);os.makedirs(O)
    for d,f in P: shutil.copy(R+d+'/'+f,O+f)
    print('올려야 할 장 %d'%len(P));[print(f) for d,f in P[:60]]
else:
    pc=load();ok=0;bad=[]
    for d,f in P:
        if os.path.exists(UP+f) and md(UP+f)==md(R+d+'/'+f): pc[f]=md(R+d+'/'+f);ok+=1
        else: bad.append(f)
    open(PC,'w',encoding='utf-8').write('\n'.join(k+'\t'+v for k,v in sorted(pc.items()))+'\n')
    print('PC 재수신 대조 일치 %d · 불일치 또는 못 받음 %d'%(ok,len(bad)));[print(' -',f) for f in bad]
    sys.exit(1 if bad else 0)
