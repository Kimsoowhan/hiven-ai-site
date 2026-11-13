#!/usr/bin/env python3
# 에이전트 점검(수행 체계 10절). 구동한 모델이 돌린다. 에이전트에게 묻지 않고 실행 기록으로 잰다.
#  한 번 재기:  python3 tools/agent_watch.py once
#  지켜보기:    python3 tools/agent_watch.py watch [최대분=15] [점검간격분=5] [멈춤기준분=10]
#   → 간격마다 한 줄, 「멈춤」(기준 분 동안 기록이 늘지 않음)이거나 최대 분이 되면 끝난다(끝나면 구동한 모델이 다시 불린다)
import sys,os,glob,json,time,subprocess,datetime
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def files():
    out=[]
    for f in glob.glob('/tmp/claude-*/**/tasks/*.output',recursive=True):
        try:
            if time.time()-os.path.getmtime(f)>30*60: continue  # 30분 넘게 조용한 기록은 끝난 것으로 봄
            with open(f,'rb') as h:
                if not isinstance(json.loads(h.readline().decode('utf-8','ignore')),dict): continue
            out.append(f)
        except Exception: pass
    return out
def last(f):
    try:
        with open(f,'rb') as h:
            h.seek(max(0,os.path.getsize(f)-400000)); L=h.read().decode('utf-8','ignore').split('\n')
    except Exception: return ('','')
    ts='';what=''
    for l in reversed(L):
        try: o=json.loads(l)
        except Exception: continue
        if not isinstance(o,dict): continue
        c=(o.get('message') or {}).get('content') if isinstance(o.get('message'),dict) else None
        if isinstance(c,list):
            for b in c:
                if b.get('type')=='tool_use':
                    i=b.get('input') or {}
                    what=b['name'].split('__')[-1]+' '+str(i.get('description') or i.get('command') or i.get('path') or '')[:60].replace('\n',' ')
                    t=o.get('timestamp','')
                    try: ts=(datetime.datetime.strptime(t[:19],'%Y-%m-%dT%H:%M:%S')+datetime.timedelta(hours=9)).strftime('%H:%M:%S')
                    except Exception: ts=t[11:19]
                    return (ts,what)
    return (ts,what)
def queue():
    try:
        L=open(R+'/cowork/ctl/work_queue.tsv',encoding='utf-8-sig').read().split('\n')[1:]
        s=[l.split('\t')[4] for l in L if l.strip()]
        m=datetime.datetime.fromtimestamp(os.path.getmtime(R+'/cowork/ctl/work_queue.tsv')+0).strftime('%H:%M')
        return '큐 끝 %d·대기 %d·막힘 %d(고침 %s)'%(s.count('끝'),len([x for x in s if x not in('끝','막힘')]),s.count('막힘'),m)
    except Exception: return '큐 없음'
def measure(prev):
    now=time.time();rows=[]
    for f in files():
        sz=os.path.getsize(f);mt=os.path.getmtime(f);idle=int((now-mt)/60)
        ts,what=last(f)
        rows.append((os.path.basename(f)[:8],sz,sz-prev.get(f,sz),idle,ts,what));prev[f]=sz
    return rows
def line(rows):
    t=time.strftime('%H:%M:%S',time.localtime(time.time()+0))
    if not rows: return t+' 에이전트 실행 기록 없음 · '+queue()
    return ' | '.join('%s 에이전트 %s: 기록 %d바이트(+%d) · 마지막 실행 %s · 조용한 지 %d분 · %s'%(t,r[0],r[1],r[2],r[4],r[3],r[5]) for r in rows)+' · '+queue()
if __name__=='__main__':
    os.environ['TZ']='Asia/Seoul';time.tzset()
    mode=sys.argv[1] if len(sys.argv)>1 else 'once';prev={}
    if mode=='once':
        measure(prev);time.sleep(20);print(line(measure(prev)));sys.exit(0)
    mx=int(sys.argv[2]) if len(sys.argv)>2 else 15; iv=int(sys.argv[3]) if len(sys.argv)>3 else 5; st=int(sys.argv[4]) if len(sys.argv)>4 else 10
    t0=time.time();measure(prev)
    while True:
        time.sleep(iv*60);rows=measure(prev);print(line(rows),flush=True)
        act=[r for r in rows if r[3]<st]
        if not act: print('판정: 멈춤 또는 끝 — %d분 동안 기록이 늘지 않음. 구동한 모델이 지금 재촉하거나 결과를 받는다(점-4)'%st,flush=True);sys.exit(2)
        if time.time()-t0>=mx*60: print('판정: 진행 중 — 대표님께 수치 한 줄을 알리고 다시 지켜본다(점-5)',flush=True);sys.exit(0)
