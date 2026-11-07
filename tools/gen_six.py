# SC-09 6단 막대(T·TT·W·WW·M·MM) 값 산출(Opus 워크 0006, 계층규칙 2.0 4장) — 모델이 직접 실행(자동 실행 장치 아님)
# T = 전 W# 태스크 완료 비율 · TT = 현재 워크 TT 행 완료 비율(91_Fable\TT) · W = W# 평균(progress.week) · WW·M·MM = progress의 Fable 집계값
import json,re,glob
G='/home/claude/hiven-ai-site/cowork/progress.json';U='/mnt/user-data/uploads/HiBiz/91_Fable/TT/'
p=json.load(open(G,encoding='utf-8'))
tk=[t for i in p['items'] for t in i.get('tasks',[])];td=sum(1 for t in tk if re.search('완료|검수|통과',t.get('status','')))
import sys
wk=sys.argv[1] if len(sys.argv)>1 else '0006'  # 현재 워크(Fable 시작 체크 기준) — 실행 때 지정
s=open(U+'타임테이블_워크%s_전체.md'%wk,encoding='utf-8').read();rows=[l for l in s.split('\n') if l.startswith('| TT-')]
tt=(sum(1 for l in rows if l.rstrip(' |').split('|')[-1].strip().startswith('완료')),len(rows))
pc=lambda a,b:round(a*100/b) if b else 0
p['six']=[{'k':'T','v':pc(td,len(tk)),'s':'태스크 %d/%d 완료'%(td,len(tk))},
 {'k':'TT','v':pc(*tt),'s':'워크 %s TT %d/%d 완료'%(wk,tt[0],tt[1])},
 {'k':'W','v':p.get('week',0),'s':'W# %d건 평균'%len(p['items'])},
 {'k':'WW','v':p['ww']['percent'],'s':p['ww']['id']+' · '+p['ww']['range']},
 {'k':'M','v':p['month']['percent'],'s':p['month']['id']+' · '+p['month']['range']},
 {'k':'MM','v':p['mm']['percent'],'s':p['mm']['id']+' · '+p['mm']['range']}]
json.dump(p,open(G,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(p['six'])
