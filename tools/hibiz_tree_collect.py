#!/usr/bin/env python3
# HiBiz 실측 모음: 이 창 기록(jsonl)에서 device_list_dir 결과를 거두어 한 장의 나무 목록으로 만든다.
# 쓰는 법: python3 tools/hibiz_tree_collect.py <기록.jsonl> <시작 시각 ISO(UTC)>  → cowork/ctl/hibiz/hibiz_tree.tsv(로컬 전용)
import json,sys,re,os
JS,since=sys.argv[1].split(','),sys.argv[2]
ROOT='C:\\Users\\marty\\Documents\\HiBiz'
use={};res={}
for line in (l for J in JS for l in open(J,encoding='utf-8')):
    try:o=json.loads(line)
    except: continue
    if o.get('timestamp','')<since: continue
    m=o.get('message',{}); c=m.get('content')
    if not isinstance(c,list): continue
    for b in c:
        if b.get('type')=='tool_use' and b.get('name','').endswith('device_list_dir'):
            use[b['id']]=b['input']['path']
        if b.get('type')=='tool_result' and b.get('tool_use_id') in use:
            t=b.get('content'); 
            if isinstance(t,list): t=''.join(x.get('text','') for x in t)
            res[b['tool_use_id']]=t
out={}; bad=[]
for i,p in use.items():
    t=res.get(i,'')
    m=re.search(r'saved to (\S+\.txt)',t)
    if m: t=open(m.group(1),encoding='utf-8').read()
    try:
        d=json.loads(t)
        if isinstance(d,list): d=json.loads(d[0]['text'])
    except Exception as e: bad.append((p,str(e)[:60])); continue
    rel=p[len(ROOT):].strip('\\')
    if not rel: continue          # 전체 한 번에 받은 것은 2000줄에서 잘려 쓰지 않음
    if d.get('truncated'): bad.append((p,'2000줄에서 잘림'))
    if d.get('truncated'): continue
    out[rel]=d['entries']
rows=[]
for top in sorted(out):
    t=top.replace('\\','/')
    if '/' in t: rows.append((t,'dir','',''))
    for e in out[top]:
        rows.append((t+'/'+e['name'].replace('\\','/'),e['type'],str(e.get('size','')),str(e.get('mtimeMs',''))))
rows=sorted(set(rows))
rows.sort()
os.makedirs('cowork/ctl/hibiz',exist_ok=True)
with open('cowork/ctl/hibiz/hibiz_tree.tsv','w',encoding='utf-8') as f:
    f.write('경로\t종류\t크기\t고친 때\n')
    for r in rows: f.write('\t'.join(r)+'\n')
print('1층',len(out),'줄',len(rows),'파일',sum(1 for r in rows if r[1]=='file'),'폴더',sum(1 for r in rows if r[1]=='dir'))
for b in bad: print('문제:',b)
