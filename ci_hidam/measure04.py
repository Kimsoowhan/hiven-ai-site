# -*- coding: utf-8 -*-
"""OP-2 끝난 기준 ③ · ④의 잣대: 흔한 쓰임 둘에서 묻는 비율, 모든 걸음 뒤 원본 매체의 폴더 전체 해시.
만든 파일로 돌린 시뮬레이션이며 실측이 아니다. 대상 폴더는 임시 폴더뿐이다."""
import os, sys, json, random, tempfile, shutil, time, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("HIDAM_ENGINE_DIR") or HERE)
from hidam_app import HiDAMApp, Medium, sha, APP_VER
T = tempfile.mkdtemp(prefix="m04_")
def mk(n):
    p = os.path.join(T, n); os.makedirs(p, exist_ok=True); return p
def w(root, rel, data):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(data if isinstance(data, bytes) else data.encode("utf-8"))
def tree(root):
    """폴더 전체 해시: 모든 파일의 (자리, 내용 해시)를 차례대로 묶은 해시. 엔진이 거울 매체에 쓰는 _HiDAM_* 자리는 거울 매체에서만 뺀다."""
    out = []
    for d, ds, fs in os.walk(root):
        ds.sort()
        for f in sorted(fs):
            p = os.path.join(d, f)
            out.append((os.path.relpath(p, root).replace("\\", "/"), sha(open(p, "rb").read())))
    return sha(json.dumps(out, ensure_ascii=False).encode()), len(out)

res = dict(engine=APP_VER, engine_sha256=sha(open(os.path.join(os.environ.get("HIDAM_ENGINE_DIR") or HERE, "hidam_app.py"), "rb").read()),
           env="Python %s · %s" % (sys.version.split()[0], sys.platform), ran_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

# ① USB 둘을 번갈아 20번 고침(검수 K t2_usage U1과 같은 입력, random.seed(7))
random.seed(7); app = HiDAMApp(mk("U1"), auto=True); A, B = mk("U1a"), mk("U1b"); docs = ["보고서.txt", "회의록.md", "예산.csv", "일정.txt", "메모.md"]
body = {d: ["%s %d줄" % (d, i) for i in range(12)] for d in docs}
for d in docs:
    for x in (A, B): w(x, "업무/" + d, "\n".join(body[d]) + "\n")
app.plug(Medium("A", A)); app.plug(Medium("B", B)); cur = {(m, d): list(body[d]) for m in "AB" for d in docs}
asked, same_after, steps, seen_p = 0, 0, [], set(app.pkeys)
for st in range(20):
    m = "AB"[st % 2]; d = docs[st % 5]; L = cur[(m, d)]; L[random.randrange(len(L))] += " 고침%d" % st; L.append("더함%d" % st)
    w(A if m == "A" else B, "업무/" + d, "\n".join(L) + "\n")
    before = (tree(A), tree(B))                      # 사용자가 고친 뒤의 값이 「처음」이다
    la = app.auto_run("바뀌면")
    after = (tree(A), tree(B))
    newp = [k for k in app.pkeys if k not in seen_p and k.startswith(("판|", "판확인|"))]; seen_p |= set(app.pkeys)
    q = bool(newp or la["waiting"]); asked += q; same_after += before == after
    steps.append(dict(step=st, medium=m, doc=d, result=la["result"], asked=q, media_same=before == after))
fin = {d: open(os.path.join(app.dev.root, "기준자리/업무", d), encoding="utf-8").read() for d in docs}
kept = all(("고침%d" % s) in fin[docs[s % 5]] and ("더함%d" % s) in fin[docs[s % 5]] for s in range(20))
res["U1_번갈아_20번"] = dict(runs=20, asked=asked, ratio=asked / 20, media_same_steps=same_after, all_edits_in_final=kept,
                         dashboard=app.dashboard()["3_보호상태"]["state"], steps=steps)

# ② 첫날 매체 넷(검수 K t2_usage U2와 같은 입력)
JPG = lambda i: b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00" + (b"photo%05d" % i) * 30
app = HiDAMApp(mk("U2"), auto=True); M = [mk("U2m%d" % i) for i in range(4)]; pc = app.dev.root
base = ["사업계획서", "1. 개요", "2. 시장", "3. 제품", "4. 일정", "5. 예산", "6. 맺음"]
for i in range(10):
    nm = "문서/계획%02d.txt" % i; b0 = [x + " %d" % i for x in base]
    w(pc, nm, "\n".join(b0) + "\n"); w(M[0], nm, "\n".join(b0 + ["7. 더함"]) + "\n")
    w(M[1], nm.replace(".txt", "_최종.txt"), "\n".join(b0[:3] + ["3-1. 끼움"] + b0[3:]) + "\n" if i % 2 else "\n".join(b0 + ["7. 더함", "8. 또 더함"]) + "\n")
for i in range(1, 101): w(M[2], "DCIM/100CANON/IMG_%04d.JPG" % i, JPG(i)); w(M[3], "DCIM/100CANON/IMG_%04d.JPG" % i, JPG(1000 + i))
for i, m in enumerate(M):
    w(m, "desktop.ini", "[.ShellClassInfo]\nIconIndex=%d\n" % i); w(m, "Thumbs.db", b"\xd0\xcf\x11\xe0" + bytes([i]) * 50); w(m, ".DS_Store", b"\x00\x00\x00\x01Bud1" + bytes([i]) * 40)
    w(m, "메모.txt", "매체 %d에 적어 둔 서로 다른 메모\n내용 %d\n" % (i, i)); w(m, "사진/증명사진.jpg", JPG(5000 + i))
    w(m, "받은 파일/주민센터 안내문.pdf", b"%PDF-1.4 " + bytes([65 + i]) * 30); w(m, "여행/졸업여행 단체.jpg", JPG(7000 + i))
t0 = [tree(m) for m in M]
for i, m in enumerate(M): app.plug(Medium("M%d" % i, m))
rows = app.reconcile(); ask = sum(1 for r in rows if r["how"] in ("확인 필요", "사용자가 고름", "자동에서 뺌"))
D = mk("U2d"); app.plug(Medium("MIR", D, role="거울")); pr = [p for p in app.proposals() if p["kind"] in ("첫 미러링", "매체 역할")]
app.confirm_first("MIR"); mr = app.mirror("MIR"); t1 = [tree(m) for m in M]; dash = app.dashboard()
res["U2_첫날_매체넷"] = dict(groups=len(rows), asked=ask, ratio=ask / max(len(rows), 1), how={h: sum(1 for r in rows if r["how"] == h) for h in sorted({r["how"] for r in rows})},
                         media_files=sum(n for _, n in t0), media_same=t0 == t1, mirrored=mr["done"], vault=mr.get("vault"),
                         protected_waiting=dash["4_거울상태"]["protected_waiting"], state=dash["3_보호상태"]["state"])
res["끝난기준3"] = dict(U1=res["U1_번갈아_20번"]["ratio"] < 0.10, U2=res["U2_첫날_매체넷"]["ratio"] < 0.10)
res["끝난기준4"] = dict(U1_steps_same=same_after == 20, U2_same=t0 == t1)
json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "measure04_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("① 번갈아 20번: 물음 %d / 20 = %.0f%% · 고침 모두 최종본에 %s · 걸음 뒤 매체 같음 %d / 20" % (asked, 100 * asked / 20, kept, same_after))
print("② 첫날 매체 넷: 판 묶음 %d · 물음 %d = %.0f%% · 매체 파일 %d · 매체 같음 %s · 금고 %s" % (len(rows), ask, 100 * ask / max(len(rows), 1), sum(n for _, n in t0), t0 == t1, mr.get("vault")))
shutil.rmtree(T, ignore_errors=True)
