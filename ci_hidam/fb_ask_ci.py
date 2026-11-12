# Fable이 따로 돌리는 묻는 비율(시뮬레이션): Opus와 다른 입력 셋
import os,sys,json,random,tempfile,hashlib
sys.dont_write_bytecode=True; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from hidam_app import HiDAMApp, Medium, sha
T=tempfile.mkdtemp(prefix="fba_")
def mk(n):
    p=os.path.join(T,n); os.makedirs(p,exist_ok=True); return p
def w(root,rel,data):
    p=os.path.join(root,rel); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,"w",encoding="utf-8").write(data)
def tree(root):
    out=[]
    for d,ds,fs in os.walk(root):
        ds.sort()
        for f in sorted(fs):
            p=os.path.join(d,f); out.append((os.path.relpath(p,root),sha(open(p,"rb").read())))
    return sha(json.dumps(out).encode())
def run(tag,seed,nmed,docs,steps,pick,mid_insert=False):
    random.seed(seed); app=HiDAMApp(mk(tag),auto=True); R=[mk("%s_%d"%(tag,i)) for i in range(nmed)]
    body={d:["%s %d줄"%(d,i) for i in range(12)] for d in docs}
    for d in docs:
        for x in R: w(x,"업무/"+d,"\n".join(body[d])+"\n")
    for i,x in enumerate(R): app.plug(Medium("M%d"%i,x))
    cur={(i,d):list(body[d]) for i in range(nmed) for d in docs}; asked=same=0; seen=set(app.pkeys); marks=[]
    for st in range(steps):
        m,d=pick(st,nmed,docs); L=cur[(m,d)]; L[random.randrange(len(L))]+=" 고침%d"%st
        if mid_insert and st%3==0: L.insert(random.randrange(1,len(L)),"끼움%d"%st)
        else: L.append("더함%d"%st)
        w(R[m],"업무/"+d,"\n".join(L)+"\n"); marks.append((d,"고침%d"%st))
        b=[tree(x) for x in R]; la=app.auto_run("바뀌면"); a=[tree(x) for x in R]
        newp=[k for k in app.pkeys if k not in seen and k.startswith(("판|","판확인|"))]; seen|=set(app.pkeys)
        asked+=bool(newp or la["waiting"]); same+=(a==b)
    fin={d:(open(os.path.join(app.dev.root,"기준자리/업무",d),encoding="utf-8").read() if os.path.exists(os.path.join(app.dev.root,"기준자리/업무",d)) else "") for d in docs}; edited={d for d,_ in marks}; miss=[d for d in edited if not fin[d]]
    kept=sum(1 for d,mk_ in marks if mk_ in fin[d])
    return dict(tag=tag,seed=seed,steps=steps,asked=asked,ratio=round(asked/steps,3),media_same=same,edits_in_final="%d/%d"%(kept,len(marks)),final_missing=miss)
D5=["보고서.txt","회의록.md","예산.csv","일정.txt","메모.md"]; out=[]
for s in range(1,11): out.append(run("F1s%d"%s,s,2,D5,20,lambda st,n,docs:(st%2,docs[st%5])))
for s in (11,12,13): out.append(run("F2s%d"%s,s,3,D5+["계획.txt"],30,lambda st,n,docs:(random.randrange(n),random.choice(docs)),mid_insert=True))
for s in (21,22,23): out.append(run("F3s%d"%s,s,2,["보고서.txt"],20,lambda st,n,docs:(st%2,docs[0])))
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"res_fbask.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
for o in out: print(o)
