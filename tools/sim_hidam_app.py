# -*- coding: utf-8 -*-
"""HiDAM.app 기준 구현 시뮬레이션 — 시나리오 TS-01~28. 만든 파일로 돌린 것이며 실측이 아니다."""
import os, sys, json, shutil, tempfile, hashlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hidam_app import HiDAMApp, Medium, classify, sha, POLICY

R, T = [], tempfile.mkdtemp(prefix="hidam_")
def w(root, rel, data, mtime=None):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(data if isinstance(data, bytes) else data.encode("utf-8"))
    if mtime: os.utime(p, (mtime, mtime))
def rd(root, rel): return open(os.path.join(root, rel), "rb").read()
def mk(name): p = os.path.join(T, name); os.makedirs(p, exist_ok=True); return p
def ok(no, title, rule, cond, seen): R.append(dict(no=no, title=title, rule=rule, result="통과" if cond else "실패", seen=str(seen)[:160]))
def snap(root):
    out = {}
    for d, _, fs in os.walk(root):
        if "_HiDAM" in d: continue
        for f in fs: out[os.path.relpath(os.path.join(d, f), root)] = sha(open(os.path.join(d, f), "rb").read())
    return out
JPG_SHOT = b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00" + b"photo" * 40
JPG_PLAIN = b"\xff\xd8\xff\xe0" + b"plain" * 40
PNG = b"\x89PNG\r\n" + b"cap" * 40
ORGS = (("가나건설", "03.01"),)

# --- 분류(CLS·SEC) ---
c1 = classify("문서/2024_이력서_최종.docx", b"x"); c2 = classify("D:/다른경로/문서/2024_이력서_최종.docx".split(":/")[1].split("/", 1)[1], b"x")
ok("TS-01", "같은 파일을 두 기기에서 판정", "CP-06", c1 == c2 and c1[0] == "02.01", (c1, c2))
pc = mk("pc"); w(pc, "사진/IMG_0001.jpg", JPG_SHOT); w(pc, "사진/Screenshot_20260101.png", PNG); w(pc, "사진/무제.jpg", JPG_PLAIN)
w(pc, "NPKI/signCert.der", b"cert"); w(pc, "DCIM/Camera/a.jpg", JPG_SHOT); w(pc, "가나건설/현장/b.jpg", JPG_SHOT); w(pc, "메모.txt", "a\nb\n")
free = HiDAMApp(pc, tier="무료", orgs=ORGS); sub = HiDAMApp(pc, tier="구독", orgs=ORGS)
pf, _ = free.preview(); ps, st = sub.preview()
ok("TS-02", "무료 미리 보기와 구독 판정", "CP-10", {k: v["code"] for k, v in pf.items()} == {k: v["code"] for k, v in ps.items()}, st)
ok("TS-03", "인증서 파일", "JR-1", ps["NPKI/signCert.der"]["code"] == "00.04" and os.path.exists(os.path.join(pc, "NPKI/signCert.der")), ps["NPKI/signCert.der"])
ok("TS-04", "휴대폰 백업 폴더", "JR-2", ps["DCIM/Camera/a.jpg"]["code"] == "97.01", ps["DCIM/Camera/a.jpg"])
ok("TS-05", "찍은 사진과 화면 캡처", "PV-01·02", ps["사진/IMG_0001.jpg"]["code"] == "06.01" and ps["사진/Screenshot_20260101.png"]["code"] == "06.10", "06.01 / 06.10")
ok("TS-06", "찍은 정보가 없는 사진", "PV-09", ps["사진/무제.jpg"]["code"] == "99.01" and ps["사진/무제.jpg"]["conf"] == "낮음", ps["사진/무제.jpg"])
ok("TS-07", "묶음 안의 사진", "JR-9 · PV-04", ps["가나건설/현장/b.jpg"]["code"] == "03.01", ps["가나건설/현장/b.jpg"])
sub.user_rules["무제.jpg"] = "06.08"; p2, _ = sub.preview()
ok("TS-08", "사용자가 자리를 고침", "CP-08", p2["사진/무제.jpg"]["code"] == "06.08", p2["사진/무제.jpg"])

# --- 보호·자가 통제(AAD·SCT)·연결(LNK) ---
app = HiDAMApp(mk("pc2"), orgs=ORGS, auto=False); bad = mk("usb_bad"); w(bad, "보고서.pdf.exe", b"MZ" + b"x" * 20); w(bad, "정상.txt", "hello\n")
r = app.plug(Medium("USB-BAD", bad))
ok("TS-09", "위협이 든 매체를 꽂음", "AP-02 · A-05", r == "이중 확장자" and not os.path.exists(os.path.join(bad, "보고서.pdf.exe")) and app.mirror("USB-BAD")["stopped"], r)
r = app.plug(Medium("USB-NEW", mk("usb_new"), registered=False))
ok("TS-10", "미등록 매체", "AP-03 · M3", r == "미등록 매체" and app.led.rows[-1]["grade"] == "M3", r)
app = HiDAMApp(mk("pc3"), auto=False); rs = [app.plug(Medium("M%d" % i, mk("m%d" % i))) for i in range(1, 10)]
ok("TS-11", "1 대 다: 매체 여덟 자리, 아홉째", "SY-01 · TP-03", rs[:8] == ["정상"] * 8 and rs[8] == "자리 없음", rs)
ok("TS-25", "한 기기에 세션 둘", "NC-01", app.open_session("A") and not app.open_session("B") and app.led.rows[-1]["act"] == "세션 거절", "둘째 거절")

# --- 최적화(OPT)·정합(SYN) ---
pcx = mk("pcx"); A, B, C, D, E_ = (mk(x) for x in ("mA", "mB", "mC", "mD", "mE"))
base = "제목\n1장 처음\n2장 처음\n3장 처음\n4장 처음\n5장 처음\n"
now = time.time()
w(A, "계획서.txt", base, now - 300); w(B, "계획서 - 복사본.txt", base + "6장 추가\n", now - 200); w(C, "계획서_최종.txt", base + "6장 추가\n7장 추가\n", now - 900)   # C가 최신인데 날짜는 가장 옛날
w(A, "보고.md", "머리\n가\n나\n다\n라\n마\n"); w(B, "보고(1).md", "머리\n가 고침\n나\n다\n라\n마\n"); w(C, "보고_v2.md", "머리\n가\n나\n다\n라\n마 고침\n")
w(A, "회의.txt", "x\n안건\ny\n"); w(B, "회의_수정.txt", "x\n안건 갑\ny\n"); w(C, "회의_최종.txt", "x\n안건 을\ny\n")
w(A, "그림.png", PNG + b"1"); w(B, "그림(1).png", PNG + b"2")
w(A, "같은것.bin", b"same" * 100); w(B, "사본/같은것.bin", b"same" * 100); w(C, "같은것.bin", b"same" * 100)
before = {x: snap(x) for x in (A, B, C)}
app = HiDAMApp(pcx, auto=False)
for i, x in zip("ABC", (A, B, C)): app.plug(Medium("M-" + i, x))
opt, dup, vers = app.dup_map()
ok("TS-12", "매체 사이 완전 중복 지도", "DUP-A · OZ-01", opt["dup_groups"] == 1 and opt["reclaim_bytes"] == 800, opt)
rec = {r["stem"]: r for r in app.reconcile()}
ok("TS-13", "한 줄로 이어진 판(세 매체)", "SY-04·06", rec["계획서"]["judge"] == "SY-최신" and rd(pcx, "기준자리/계획서.txt").decode().endswith("7장 추가"), rec["계획서"]["why"])
ok("TS-16", "날짜가 속임(가장 옛 날짜가 최신 내용)", "SY-03", rec["계획서"]["final_from"] == ["M-C"], rec["계획서"]["final_from"])
m = rd(pcx, "기준자리/보고.md").decode()
ok("TS-14", "갈라짐: 겹치지 않게 고침", "SY-07", rec["보고"]["how"] == "자동 합침" and "가 고침" in m and "마 고침" in m, m.replace("\n", "/"))
ok("TS-15", "갈라짐: 같은 대목을 다르게 고침", "SY-07·08", rec["회의"]["how"] == "사용자가 고름" and not os.path.exists(os.path.join(pcx, "기준자리/회의.txt")), rec["회의"]["why"])
ok("TS-17", "글자 문서가 아닌 것의 갈라짐", "SY-07", rec["그림"]["how"] == "사용자가 고름", rec["그림"]["why"])
ok("TS-28", "정합 뒤 매체의 원래 판", "SY-09 · P-01", all(snap(x) == before[x] for x in (A, B, C)), "세 매체 해시 그대로")

# --- 미러링·자동(SYN) ---
app.plug(Medium("M-D", D)); r = app.mirror("M-D")
ok("TS-18", "거울: 최종본만, 해시 대조", "MR-03 · SY-10", r["done"] == 2 and r["mismatch"] == 0 and sha(rd(D, "_HiDAM_거울/기준자리/계획서.txt")) == app.finals["기준자리/계획서.txt"], r)
w(C, "계획서_최종.txt", base + "6장 추가\n7장 추가\n8장 추가\n"); app.media["M-C"].scan(); app.auto = True; la = app.auto_run("바뀌면")
ok("TS-19", "바뀌면 자동: 최신 판 → 최종본 → 거울", "MR-12 · AP-07·08", rd(D, "_HiDAM_거울/기준자리/계획서.txt").decode().endswith("8장 추가") and la["result"] == "정상", la)
os.remove(os.path.join(pcx, "기준자리/보고.md")); r = app.mirror("M-D")
ok("TS-20", "원본에서 지움", "MR-04 · CON-09", r["held"] == 1 and os.path.exists(os.path.join(D, "_HiDAM_보류함/기준자리/보고.md")), r)
for i in range(6): w(pcx, "기준자리/n%d.txt" % i, "n%d\n" % i); app.finals["기준자리/n%d.txt" % i] = sha(("n%d\n" % i).encode())
r = app.mirror("M-D", auto=True)
ok("TS-21", "대량 변경", "MR-16 · AP-08", r["stopped"] and app.led.rows[-1]["grade"] == "M3", r["stopped"])
app.unplug("M-A"); d = app.dashboard()
ok("TS-26", "매체를 뽑음", "UD-05", [x for x in d["1_내기기"]["media"] if x["dev"] == "M-A"][0]["state"].startswith("뽑힘"), "뽑힘(마지막 본 값)")
ok("TS-29", "자동 실행 표시", "UD-07 · MR-14", d["4_거울상태"]["last_auto"]["trigger"] == "바뀌면", d["4_거울상태"]["last_auto"])

# --- 다 대 다 ---
pcy = mk("pcy"); app2 = HiDAMApp(pcy, device_id="DEV-PC-02", auto=False)
peer = Medium("DEV-PC-01", os.path.join(pcx, "기준자리"), kind="기기"); app2.plug(peer); w(E_, "계획서.txt", base); app2.plug(Medium("M-E", E_))
r2 = {r["stem"]: r for r in app2.reconcile()}
ok("TS-27", "다 대 다: 다른 기기의 최종본이 최신", "TP-01·02 · MR-07", r2["계획서"]["final_from"] == ["DEV-PC-01"] and sha(rd(pcy, "기준자리/계획서.txt")) == sha(rd(pcx, "기준자리/계획서.txt")), r2["계획서"]["why"])

# --- 복구·원장·Cloud ---
f = HiDAMApp(mk("pcf"), tier="무료"); w(f.dev.root, "a.txt", "1\n"); f._keep_version("a.txt"); w(f.dev.root, "a.txt", "2\n")
r1 = f.recover("a.txt", 1); r2_ = f.recover("a.txt", 1); r3 = f.recover("a.txt", 1)
ok("TS-22", "무료 복구(되돌리기) 두 번 뒤 세 번째", "RT · 정-1", r1["ok"] and r2_["ok"] and not r3["ok"] and r1["note"].startswith("※") and r1["name"] == "복구(되돌리기)", (r1["left"], r2_["left"], r3["guide"]))
s = HiDAMApp(mk("pcs")); w(s.dev.root, "a.txt", "1\n"); s._keep_version("a.txt"); n = [s.recover("a.txt", 1)["ok"] for _ in range(5)]
ok("TS-23", "구독 복구(원복) 다섯 번", "RS", all(n) and s.recover("a.txt", 1)["name"] == "복구(원복)", n)
s.led.rows[1]["act"] = "고침"
try: s.led.add("X", "x"); stop = False
except RuntimeError: stop = True
ok("TS-24", "원장 위변조", "K-02", stop, "그 뒤 동작 중지")
pl = sub.cloud_payload(); raw = json.dumps(pl, ensure_ascii=False)
ok("TS-30", "Cloud로 올리는 내용", "UD-08·09", "name" not in pl["assets"][0] and "IMG_0001" not in raw and "photo" not in raw and free.cloud_payload() is None, "항목: " + ",".join(pl["assets"][0].keys()))
ok("TS-31", "원장 사슬", "P-03", app.led.verify() and len(app.led.rows) > 20, "%d줄" % len(app.led.rows))

out = dict(title="HiDAM.app 기준 구현 시뮬레이션", note="만든 파일로 돌린 시뮬레이션이며 실측이 아니다", policy=POLICY,
           code_sha256=sha(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hidam_app.py"), "rb").read()),
           total=len(R), passed=sum(1 for r in R if r["result"] == "통과"), cases=sorted(R, key=lambda r: int(r["no"][3:])),
           dashboard_sample=d, ledger_tail=app.led.rows[-5:])
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "sim_hidam_app_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in out["cases"]: print(r["no"], r["result"], r["title"], "|", r["seen"][:70])
print("합계", out["passed"], "/", out["total"])
shutil.rmtree(T)
