import os,sys,tempfile,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from hidam_app import *
T=tempfile.mkdtemp(); q=os.path.join(T,"q"); os.makedirs(q); open(os.path.join(q,"a.txt"),"w").write("x\n")
Q=HiDAMApp(q,auto=False); Q.preview(); lk=os.path.join(q,"_HiDAM","00.02_원장.jsonl"); raw=open(lk,encoding="utf-8").read()
print("rows",len(Q.led.rows),"count 엔진",raw.count('"엔진"'),"fsize",Q.led.fsize,os.path.getsize(lk),"fmt",str(getattr(Q.led,"fmt",None))[:12], sha(open(lk,"rb").read())[:12])
open(lk,"w",encoding="utf-8",newline="\n").write(raw.replace('"엔진"','"지원"',1))
print("after",os.path.getsize(lk),sha(open(lk,"rb").read())[:12])
Q.led.follow(); print("state",Q.led.state)
os.makedirs(os.path.join(T,"z")); print("plug",Q.plug(Medium("Z",os.path.join(T,"z"))), Q.led.state)
