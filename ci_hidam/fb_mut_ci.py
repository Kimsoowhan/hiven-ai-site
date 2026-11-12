# Fable 따로 돌리는 변이: 엔진 줄을 기계적으로 틀리게 바꿔(연산자·상수 뒤집기) 시나리오가 잡는지 본다. 시뮬레이션.
import os,re,random,os,sys,subprocess,json,shutil,tempfile,ast
E0=os.path.dirname(os.path.abspath(__file__)); src=open(os.path.join(E0,"hidam_app.py"),encoding="utf-8").read().split("\n")
OPS=[(r" == "," != "),(r" != "," == "),(r" >= "," < "),(r" <= "," > "),(r" < "," >= "),(r" > "," <= "),(r" and "," or "),(r" or "," and "),(r"\bTrue\b","False"),(r"\bFalse\b","True"),(r"\bnot ",""),(r" \+ 1\b"," + 2"),(r"0\.5","0.9"),(r"return None","return 0")]
random.seed(20261111); cand=[]
for i,l in enumerate(src):
    s=l.strip()
    if not s or s.startswith(("#",'"""',"'''","import","from","def ","class ")) or "print(" in s: continue
    for a,b in OPS:
        if re.search(a,l): cand.append((i,a,b))
random.shuffle(cand); res=[]; n=0
for i,a,b in cand:
    if n>=60: break
    new=re.sub(a,b,src[i],count=1)
    m=src[:]; m[i]=new; code="\n".join(m)
    try: ast.parse(code)
    except SyntaxError: continue
    d=tempfile.mkdtemp(prefix="fbm_"); open(os.path.join(d,"hidam_app.py"),"w",encoding="utf-8").write(code)
    out=os.path.join(d,"r.json")
    try:
        p=subprocess.run([sys.executable,os.path.join(E0,"sim_hidam_app.py"),out,"--no-mutants"],env=dict(os.environ,HIDAM_ENGINE_DIR=d,PYTHONIOENCODING="utf-8"),capture_output=True,text=True,timeout=120)
        try:
            r=json.load(open(out)); v="잡음(실패 %d)"%(r["total"]-r["passed"]) if r["passed"]<r["total"] else "살아남음"
        except Exception: v="잡음(멈춤)"
    except subprocess.TimeoutExpired: v="잡음(시간 넘김)"
    n+=1; res.append(dict(no=n,line=i+1,before=src[i].strip()[:110],after=new.strip()[:110],verdict=v)); shutil.rmtree(d,ignore_errors=True)
    json.dump(res,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"res_fbmut.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(sum(1 for r in res if r["verdict"].startswith("잡음")),len(res))
