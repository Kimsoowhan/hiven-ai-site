#!/usr/bin/env python3
# 대화 기록 읽기 도구의 결과(부속 기록에 그대로 남음)에서 사람 턴 원문을 꺼내 /home/claude/turns/N.txt 로 쓴다(모델이 다시 받아 적지 않음).
import json,glob,re,os,html,sys
out='/home/claude/turns/';os.makedirs(out,exist_ok=True);T={};A=set()
for f in glob.glob('/root/.claude/projects/-home-claude/*/subagents/*.jsonl')+glob.glob('/root/.claude/projects/-home-claude/*.jsonl'):
    if os.path.getmtime(f)<float(sys.argv[1]) if len(sys.argv)>1 else False: continue
    for l in open(f,errors='ignore'):
        if 'turn n=' not in l: continue
        try:o=json.loads(l)
        except Exception: continue
        c=(o.get('message') or {}).get('content')
        if not isinstance(c,list): continue
        for x in c:
            if not(isinstance(x,dict) and x.get('type')=='tool_result'): continue
            y=x.get('content');s=y if isinstance(y,str) else '\n'.join(z.get('text','') for z in (y or []) if isinstance(z,dict))
            for m in re.finditer(r'<turn n="(\d+)">(Human|Assistant): (.*?)</turn>',s,flags=re.S):
                n=int(m.group(1));A.add(n)
                if m.group(2)=='Human' and m.group(3).strip(): T[n]=html.unescape(m.group(3))
for n,t in T.items(): open(out+'%d.txt'%n,'w',encoding='utf-8').write(t)
A=sorted(A);gaps=[];p=None
for n in A:
    if p is not None and n!=p+1: gaps.append((p+1,n-1))
    p=n
print('읽힌 턴',len(A),'사람 턴',len(T),'글자',sum(len(t) for t in T.values()));print('빈 구간',gaps[:40],'끝',A[-1] if A else None)
