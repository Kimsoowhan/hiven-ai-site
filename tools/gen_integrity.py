#!/usr/bin/env python3
"""무결성 목록 생성(HTML은 Cloudflare가 전송 중 코드를 끼워 넣어 제외): 화면 핵심 파일의 SHA-256을 cowork/ctl/integrity.json에 기록(침입 경보 3·6단계 '변조 의심' 판정 기준). 파일을 바꾼 뒤 반드시 실행."""
import hashlib,json,glob,os,sys
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F=sorted([os.path.basename(p) for p in glob.glob(R+'/*.js')]+['style.css'])
d={f:hashlib.sha256(open(R+'/'+f,'rb').read()).hexdigest() for f in F}
out=json.dumps({'algo':'sha256','files':d},ensure_ascii=False,indent=1)
p=R+'/cowork/ctl/integrity.json'
if len(sys.argv)>1 and sys.argv[1]=='--check':
    cur=json.load(open(p,encoding='utf-8'))['files'] if os.path.exists(p) else {}
    bad=[f for f in d if cur.get(f)!=d[f]]
    print('무결성 목록 일치' if not bad else '무결성 목록 낡음: '+','.join(bad)); sys.exit(1 if bad else 0)
open(p,'w',encoding='utf-8').write(out+'\n'); print('무결성 목록',len(d),'개')
