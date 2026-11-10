# -*- coding: utf-8 -*-
"""HiDAM.app 기준 구현 0.2 시뮬레이션. 만든 파일로 돌린 것이며 실측이 아니다.
0.1의 시나리오에 병행 검수 A가 낸 반례(되풀이 시험)와 모드·매체 역할을 더했다."""
import os, sys, json, shutil, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hidam_app import HiDAMApp, Medium, classify, sec_grade, aad_check, sha, POLICY, APP_VER

R, T = [], tempfile.mkdtemp(prefix="hidam_")
def w(root, rel, data, mtime=None):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(data if isinstance(data, bytes) else data.encode("utf-8"))
    if mtime: os.utime(p, (mtime, mtime))
def rd(root, rel): return open(os.path.join(root, rel), "rb").read()
def ex(root, rel): return os.path.exists(os.path.join(root, rel))
def mk(name): p = os.path.join(T, name); os.makedirs(p, exist_ok=True); return p
def ok(no, grp, title, rule, cond, seen): R.append(dict(no=no, group=grp, title=title, rule=rule, result="통과" if cond else "실패", seen=str(seen)[:170]))
def snap(root):
    out = {}
    for d, _, fs in os.walk(root):
        if "_HiDAM" in os.path.relpath(d, root): continue
        for f in fs: out[os.path.relpath(os.path.join(d, f), root)] = sha(open(os.path.join(d, f), "rb").read())
    return out
JPG_SHOT = b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00" + b"photo" * 40
JPG_PLAIN = b"\xff\xd8\xff\xe0" + b"plain" * 40
PNG = b"\x89PNG\r\n" + b"cap" * 40
ORGS, PROJ = (("가나건설", "03.01"),), (("HiCoffer베타2", "P001"),)
G1, G2, G3, G4, G5, G6, G7 = "가 분류·보안 분류", "나 보호·자가 통제·연결", "다 최적화·정합", "라 미러링·자동", "마 다 대 다", "바 복구·원장·Cloud", "사 모드·매체 역할"

# ===== 가 =====
pc, pcb = mk("pc"), mk("other_device")
for root in (pc, pcb): w(root, "문서/2024_이력서_최종.docx", b"resume")
w(pc, "사진/IMG_0001.jpg", JPG_SHOT); w(pc, "사진/Screenshot_20260101.png", PNG); w(pc, "사진/무제.jpg", JPG_PLAIN)
w(pc, "NPKI/signCert.der", b"cert"); w(pc, "DCIM/Camera/a.jpg", JPG_SHOT); w(pc, "가나건설/현장/b.jpg", JPG_SHOT); w(pc, "메모.txt", "a\nb\n")
w(pc, "개인/여권사본.pdf", b"%PDF-1.4 passport")
free = HiDAMApp(pc, tier="무료", orgs=ORGS); sub = HiDAMApp(pc, tier="구독", orgs=ORGS); other = HiDAMApp(pcb, device_id="DEV-PC-09", orgs=ORGS)
pf, _ = free.preview(); ps, st = sub.preview(); po, _ = other.preview()
a, b = ps["문서/2024_이력서_최종.docx"], po["문서/2024_이력서_최종.docx"]
ok("TS-01", G1, "같은 파일을 두 기기에서 판정", "CP-06", a["code"] == b["code"] == "02.01" and sub.dev.index["문서/2024_이력서_최종.docx"]["asset"] == other.dev.index["문서/2024_이력서_최종.docx"]["asset"], (a["code"], b["code"], "ASSET_ID 같음"))
ok("TS-02", G1, "무료 미리 보기와 구독 판정", "CP-10", {k: v["code"] for k, v in pf.items()} == {k: v["code"] for k, v in ps.items()}, st)
ok("TS-03", G1, "인증서 파일", "JR-1", ps["NPKI/signCert.der"]["code"] == "00.04" and ps["NPKI/signCert.der"]["grade"] == "D3" and ex(pc, "NPKI/signCert.der"), ps["NPKI/signCert.der"]["code"] + " D3, 옮김 0")
ok("TS-04", G1, "휴대폰 백업 폴더", "JR-2", ps["DCIM/Camera/a.jpg"]["code"] == "97.01", ps["DCIM/Camera/a.jpg"]["code"])
ok("TS-05", G1, "찍은 사진과 화면 캡처", "PV-01·02", ps["사진/IMG_0001.jpg"]["code"] == "06.01" and ps["사진/Screenshot_20260101.png"]["code"] == "06.10", "06.01 / 06.10")
ok("TS-06", G1, "찍은 정보가 없는 사진", "PV-09", ps["사진/무제.jpg"]["code"] == "99.01" and ps["사진/무제.jpg"]["conf"] == "낮음", "99.01 낮음")
ok("TS-07", G1, "묶음 안의 사진", "JR-9 · PV-04", ps["가나건설/현장/b.jpg"]["code"] == "03.01", ps["가나건설/현장/b.jpg"]["code"])
sub.user_rules["무제.jpg"] = "06.08"; sub.user_rules["signcert.der"] = "08.01"; p2, _ = sub.preview()
ok("TS-08", G1, "사용자가 자리를 고침", "CP-08", p2["사진/무제.jpg"]["code"] == "06.08", p2["사진/무제.jpg"]["code"])
ok("TS-32", G1, "사용자 규칙으로 인증서 자리를 바꾸려 함", "CP-08 · JR-1", p2["NPKI/signCert.der"]["code"] == "00.04" and p2["NPKI/signCert.der"]["grade"] == "D3", "보호가 앞섬, D3 유지")
ok("TS-33", G1, "여권 사본의 등급", "SV-01·02", ps["개인/여권사본.pdf"]["grade"] == "D3", ps["개인/여권사본.pdf"]["code"] + " " + ps["개인/여권사본.pdf"]["grade"])

import unicodedata
nfc, nfd = unicodedata.normalize("NFC", "문서/이력서.docx"), unicodedata.normalize("NFD", "문서/이력서.docx")
ok("TS-60", G1, "같은 이름을 운영체제가 다르게 적은 경우(NFC·NFD)", "TP-07 · CP-06", nfc != nfd and classify(nfc, b"x")["code"] == classify(nfd, b"x")["code"] == "02.01", "둘 다 02.01")

# ===== 나 =====
app = HiDAMApp(mk("pc2"), auto=False); bad = mk("usb_bad"); w(bad, "보고서.pdf.exe", b"MZ" + b"x" * 80); w(bad, "정상.txt", "hello\n")
r = app.plug(Medium("USB-BAD", bad, role="거울"))
ok("TS-09", G2, "위협이 든 매체를 꽂음", "AP-02 · A-05", r.startswith("위험") and ex(bad, "보고서.pdf.exe") and app.mirror("USB-BAD")["stopped"] == "매체 사용 불가", r + " · 파일은 그 자리에 둠")
t1 = aad_check("일기.txt", b"MZ is my initials. " * 10); t2 = aad_check("a.pdf", b"\n%PDF-1.4 x"); t3 = aad_check("그림.png", JPG_PLAIN)
ok("TS-34", G2, "위협이 아닌 것을 막지 않음", "AP-02", t1 is None and t2 is None and t3 and t3[0] == "주의", (t1, t2, t3))
r = app.plug(Medium("USB-NEW", mk("usb_new"), registered=False))
ok("TS-10", G2, "미등록 매체", "AP-03 · M3", r == "미등록 매체" and app.led.rows[-1]["code"] == "SCT-E01", r + " " + app.led.rows[-1]["code"])
app = HiDAMApp(mk("pc3"), auto=False); rs = [app.plug(Medium("M%d" % i, mk("m%d" % i))) for i in range(1, 10)]
ok("TS-11", G2, "1 대 다: 매체 여덟 자리, 아홉째", "SY-01 · TP-03", rs[:8] == ["정상"] * 8 and rs[8] == "자리 없음", rs[7:])
ok("TS-25", G2, "한 기기에 세션 둘", "NC-01", app.open_session("A") and not app.open_session("B") and app.led.rows[-1]["code"] == "SCT-E02", "둘째 거절 SCT-E02")

# ===== 다 =====
pcx = mk("pcx"); A, B, C, D, E_ = (mk(x) for x in ("mA", "mB", "mC", "mD", "mE"))
base = "제목\n1장\n2장\n3장\n4장\n5장\n"; now = time.time()
w(A, "계획서.txt", base); w(B, "계획서 - 복사본.txt", base + "6장\n"); w(C, "계획서_최종.txt", base + "6장\n7장\n")
for x in (A, B, C): w(x, "보고.md", "머리\n가\n나\n다\n라\n마\n"); w(x, "회의.txt", "x\n안건\ny\n"); w(x, "사슬.txt", "x\ny\nm\nz\n"); w(x, "지움.txt", "a\nb\nc\n")
w(A, "그림.png", PNG + b"1"); w(B, "그림.png", PNG + b"2")
w(A, "같은것.bin", b"same" * 100); w(B, "사본/같은것.bin", b"same" * 100); w(C, "같은것.bin", b"same" * 100)
w(A, "사진/IMG_20240101.jpg", JPG_SHOT + b"1"); w(A, "사진/IMG_20240102.jpg", JPG_SHOT + b"2"); w(A, "가/README.md", "하나\n둘\n셋\n"); w(B, "나/README.md", "전혀\n다른\n글\n"); w(A, "빈.txt", ""); w(B, "빈.txt", "")
w(A, "옛글.txt", "한글 부호\n둘째 줄\n".encode("cp949")); w(B, "옛글.txt", "한글 부호\n둘째 줄\n셋째 줄\n".encode("cp949"))
app = HiDAMApp(pcx, auto=False)
for i, x in zip("ABC", (A, B, C)): app.plug(Medium("M-" + i, x))
opt, dup = app.dup_map()
ok("TS-12", G3, "매체 사이 완전 중복 지도", "DUP-A · OZ-01", opt["dup_groups"] >= 1 and any(len(v) == 3 and v[0][2] == 400 for v in dup.values()), opt)
try: rec = {r["stem"]: r for r in app.reconcile()}; crash = False
except Exception as e_: rec, crash = {}, repr(e_)
ok("TS-40", G3, "옛 부호(cp949) 글자 문서가 섞여 있음", "SY-07", not crash and "옛글" in rec, rec.get("옛글", {}).get("judge", crash))
ok("TS-35", G3, "처음 만난 판들(계보 없음), 한 판이 다른 판의 줄을 다 담음", "SY-03·08", rec["계획서"]["judge"] == "SY-제안" and rec["계획서"]["final"] is None, rec["계획서"]["why"][:60])
ok("TS-38", G3, "날짜 이름 사진·다른 폴더의 같은 이름·빈 파일", "SY-03 · IX-06", not any(k.startswith("img") or k in ("readme", "빈") for k in rec), sorted(rec))
fin = app.choose("계획서", "txt", "M-C")
ok("TS-13", G3, "사용자가 고른 판이 최종본", "SY-06·09", sha(rd(pcx, fin)) == sha(rd(C, "계획서_최종.txt")), "최종본 바이트 = 고른 판 바이트")
before = {x: snap(x) for x in (A, B, C)}
w(B, "보고.md", "머리\n가 고침\n나\n다\n라\n마\n"); w(C, "보고.md", "머리\n가\n나\n다\n라\n마 고침\n")           # 바탕에서 두 갈래, 겹치지 않음
w(B, "회의.txt", "x\n안건 갑\ny\n"); w(C, "회의.txt", "x\n안건 을\ny\n")                                           # 같은 대목을 다르게
w(B, "사슬.txt", "x\nY\nm\nz\n"); w(C, "사슬.txt", "x\nY\nm\nZ\n")                                               # 차례로 바꿔 쓴 것(C는 B를 보고 고침)
w(C, "지움.txt", "a\nc\n", now - 9000)                                                                            # 줄을 지운 것이 마지막 고침, 날짜는 가장 옛날
rec = {r["stem"]: r for r in app.reconcile()}
m = rd(pcx, "기준자리/보고.md").decode() if ex(pcx, "기준자리/보고.md") else ""
ok("TS-14", G3, "갈라짐: 바탕이 확인되고 겹치지 않게 고침", "SY-07", rec["보고"]["how"] == "자동 합침" and "가 고침" in m and "마 고침" in m, m.replace("\n", "/"))
ok("TS-15", G3, "갈라짐: 같은 대목을 다르게 고침", "SY-07·08", rec["회의"]["how"] == "사용자가 고름" and not ex(pcx, "기준자리/회의.txt"), rec["회의"]["why"])
ok("TS-37", G3, "차례로 바꿔 쓴 사슬을 틀리게 합치지 않음", "SY-07·08", rec["사슬"]["how"] == "사용자가 고름" and not ex(pcx, "기준자리/사슬.txt"), rec["사슬"]["why"])
ok("TS-36", G3, "줄을 지운 것이 마지막 고침", "SY-03·15", rec["지움"]["judge"] == "SY-최신" and rd(pcx, "기준자리/지움.txt") == b"a\nc\n", rec["지움"]["why"])
ok("TS-16", G3, "날짜가 속임(가장 옛 날짜가 최신 내용)", "SY-03", rec["지움"]["final_from"] == ["M-C"], rec["지움"]["final_from"])
ok("TS-17", G3, "글자 문서가 아닌 것의 갈라짐", "SY-07", rec["그림"]["how"] == "사용자가 고름", rec["그림"]["why"])
w(pcx, "기준자리/지움.txt", "a\nc\nd\n"); rec = {r["stem"]: r for r in app.reconcile()}
ok("TS-41", G3, "기기에서 최종본을 직접 고침", "SY-12 · AP-03", rd(pcx, "기준자리/지움.txt") == b"a\nc\nd\n" and rec["지움"]["judge"] == "SY-최신", "덮어쓰지 않음: " + rec["지움"]["why"][:40])
n1 = len(os.listdir(app.vers)); app.reconcile(); app.reconcile()
ok("TS-42", G3, "같은 정합을 되풀이", "SY-09", len(os.listdir(app.vers)) == n1 and sum(len(os.listdir(os.path.join(app.vers, d))) for d in os.listdir(app.vers)) <= 3, "판이 쌓이지 않음")
expect = dict(before["M-B"] if "M-B" in before else before[B]); 
ok("TS-28", G3, "정합 뒤 매체의 파일", "SY-09 · P-01", snap(A) == before[A] and all(not any("_HiDAM" in p for p in os.listdir(x)) for x in (A, B, C)), "엔진이 작업 매체에 쓴 것 0")

# ===== 라 =====
w(pcx, "일반/메모.txt", "보통 파일\n"); w(pcx, "개인/여권사본.pdf", b"%PDF-1.4 pp")
app.plug(Medium("M-D", D, role="거울")); r0 = app.mirror("M-D"); rA = app.mirror("M-A")
ok("TS-18", G4, "거울: 역할을 준 매체에만, 첫 실행은 확인 뒤", "MR-08·15", r0["stopped"].startswith("첫 미러링") and rA["stopped"] == "거울 역할이 아닌 매체" and not ex(D, "_HiDAM_거울"), (r0["stopped"], rA["stopped"]))
app.confirm_first("M-D"); r = app.mirror("M-D")
ok("TS-43", G4, "엇갈림이 없는 보통 파일도 거울로", "MR-03", r["mismatch"] == 0 and ex(D, "_HiDAM_거울/일반/메모.txt") and sha(rd(D, "_HiDAM_거울/기준자리/지움.txt")) == sha(rd(pcx, "기준자리/지움.txt")), r)
ok("TS-44", G4, "보호 등급 자산은 자동 거울에서 빠짐", "SV-03 · IX-14", not ex(D, "_HiDAM_거울/개인/여권사본.pdf") and any("보호 등급" in s[1] for s in app.skipped), [s for s in app.skipped if "보호" in s[1]][:1])
ok("TS-45", G4, "엇갈림이 안 풀린 것은 거울로 가지 않음", "SY-10", not ex(D, "_HiDAM_거울/기준자리/회의.txt"), "회의·사슬·그림 빠짐")
for x in (B, C): w(x, "보고.md", rd(pcx, "기준자리/보고.md"))            # 사용자가 매체의 옛 판을 최종본으로 바꿈(SY-10)
app.reconcile(); w(C, "보고.md", rd(pcx, "기준자리/보고.md").decode() + "바 더함\n"); app.auto = True; la = app.auto_run("바뀌면")
ok("TS-19", G4, "바뀌면 자동: 최신 판 → 최종본 → 거울", "MR-12 · AP-07·08", rd(D, "_HiDAM_거울/기준자리/보고.md").decode().endswith("바 더함\n") and "확인 대기" in la["result"], la["result"])
ok("TS-29", G4, "자동 실행과 기다리는 것이 화면에 보임", "UD-07 · MR-14", app.dashboard()["4_거울상태"]["last_auto"]["waiting"] != [] and app.dashboard()["3_보호상태"]["state"] == "살핌 필요", la["waiting"])
os.remove(os.path.join(pcx, "일반/메모.txt")); r = app.mirror("M-D")
ok("TS-20", G4, "원본에서 지움", "MR-04 · CON-09", r["held"] == 1 and ex(D, "_HiDAM_보류함/일반/메모.txt"), r)
for i in range(12): w(pcx, "대량/n%d.txt" % i, "n%d\n" % i)
rn_ = app.mirror("M-D", auto=True)                                   # 새로 생긴 것은 대량 변경이 아니다
for i in range(10): w(pcx, "대량/n%d.txt" % i, "바뀜 %d\n" % i)       # 이미 거울에 있는 것이 한꺼번에 바뀜
r = app.mirror("M-D", auto=True)
ok("TS-21", G4, "대량 변경", "MR-16 · AP-08", rn_["stopped"] is None and rn_["done"] == 12 and r["stopped"] == "대량 변경 — 확인 필요" and app.led.rows[-1]["code"] == "SYN-E05", "새 파일 12건은 비춤 · 10건이 한꺼번에 바뀌자 멈춤")
app.unplug("M-A"); d = app.dashboard()
ok("TS-26", G4, "매체를 뽑음", "UD-05", [x for x in d["1_내기기"]["media"] if x["dev"] == "M-A"][0]["state"].startswith("뽑힘"), "뽑힘(마지막 본 값)")
F = mk("mF"); app.plug(Medium("M-F", F, role="거울", scope="08")); app.confirm_first("M-F"); app.mirror("M-F")
got = snap(os.path.join(F, "_HiDAM_거울")) if ex(F, "_HiDAM_거울") else {}
ok("TS-46", G4, "범위를 준 거울 매체(자료실 08만)", "ST-02 · MR-08", got and all(app.judge(app.dev, k.replace(os.sep, "/"))["code"].startswith("08") for k in got), "%d건 모두 08" % len(got))

# ===== 마 =====
pcy = mk("pcy"); app2 = HiDAMApp(pcy, device_id="DEV-PC-02", auto=False)
w(E_, "지움.txt", "a\nb\nc\n"); app2.plug(Medium("M-E", E_)); app2.plug(Medium("DEV-PC-01", os.path.join(pcx, "기준자리"), kind="기기"))
r2 = {r["stem"]: r for r in app2.reconcile()}; first = r2["지움"]["judge"]
app2.import_lineage(app); r2 = {r["stem"]: r for r in app2.reconcile()}
ok("TS-27", G5, "다 대 다: 다른 기기의 최신 내용을 기준으로 맞춤", "SY-15·16·19", first != "SY-최신" and r2["지움"]["judge"] == "SY-최신" and rd(pcy, "기준자리/지움.txt") == rd(pcx, "기준자리/지움.txt"), "계보 없이는 %s → 계보를 받은 뒤 %s" % (first, r2["지움"]["judge"]))
n = len(app2.led.rows); app2.reconcile()
ok("TS-47", G5, "이미 받은 판을 다시 받지 않음", "SY-17", not any(r["code"] == "SYN-E02" for r in app2.led.rows[n:]), "최종본 사건 0")

# ===== 바 =====
f = HiDAMApp(mk("pcf"), tier="무료"); w(f.dev.root, "a.txt", "1\n"); f._keep_version("a.txt"); w(f.dev.root, "a.txt", "2\n")
r1 = f.recover("a.txt", 1); r2_ = f.recover("a.txt", 1); r3 = f.recover("a.txt", 1)
ok("TS-22", G6, "무료 복구(되돌리기) 두 번 뒤 세 번째", "RT · 정-1", r1["ok"] and r2_["ok"] and not r3["ok"] and r1["note"].startswith("※") and r1["name"] == "복구(되돌리기)", (r1["left"], r2_["left"], r3["guide"]))
fb = HiDAMApp(mk("pcfb"), tier="무료"); fb.beta = True; w(fb.dev.root, "a.txt", "1\n"); fb._keep_version("a.txt"); w(fb.dev.root, "a.txt", "2\n")
rb = [fb.recover("a.txt", 1) for _ in range(7)]
ok("TS-58", G6, "베타: 다섯 번을 넘어도 계속, 다섯 번째부터 안내", "RT · 정-1", all(x["ok"] for x in rb) and rb[3]["guide"] is None and rb[4]["guide"] and rb[6]["guide"], "7번 모두 됨, 5번째부터 안내")
fr = f.reconcile(); fm_ = HiDAMApp(mk("pcf2"), tier="무료"); mm = Medium("X", mk("mx"), role="거울"); fm_.plug(mm)
ok("TS-48", G6, "무료 층에서 정합·거울", "MR-01 · SY-14", "unsettled" in fr and fm_.mirror("X")["stopped"] == "미러링은 구독 기능입니다", "건수만 · 거절")
s = HiDAMApp(mk("pcs")); w(s.dev.root, "기준자리/a.txt", "1\n"); s._keep_version("기준자리/a.txt"); w(s.dev.root, "기준자리/a.txt", "2\n")
n = [s.recover("기준자리/a.txt", 1)["ok"] for _ in range(5)]
ok("TS-23", G6, "구독 복구(원복) 다섯 번", "RS", all(n) and s.recover("기준자리/a.txt", 1)["name"] == "복구(원복)", n)
ms = mk("ms"); w(ms, "a.txt", "2\n"); s.plug(Medium("M-S", ms)); s.auto_run("때 되면")
ok("TS-49", G6, "복구한 것을 자동 실행이 되돌리지 않음", "SY-11 · RS", rd(s.dev.root, "기준자리/a.txt") == b"1\n", "복구한 내용 그대로")
w(s.dev.root, "x/a.txt", "X1\n"); s._keep_version("x/a.txt"); w(s.dev.root, "x_a.txt", "Y1\n"); s._keep_version("x_a.txt"); w(s.dev.root, "x/a.txt", "X2\n"); s.recover("x/a.txt", 1)
ok("TS-50", G6, "이름이 닮은 두 자리의 판이 섞이지 않음", "CON-01", rd(s.dev.root, "x/a.txt") == b"X1\n", "x/a.txt ← 자기 판")
os.remove(os.path.join(s.dev.root, "x/a.txt")); rr = s.recover("x/a.txt", 1); rn = s.recover("x/a.txt", 99)
ok("TS-51", G6, "지워진 파일의 복구, 없는 판 고르기", "RS · K-01", rr["ok"] and rd(s.dev.root, "x/a.txt") == b"X1\n" and not rn["ok"] and s.led.rows[-1]["code"] == "LED-E04", "되살림 · 실패는 LED-E04로 남음")
s.led.rows[1]["act"] = "고침"
try: s.led.add("X", "x"); stop = False
except RuntimeError: stop = True
ok("TS-24", G6, "원장 위변조", "K-02", stop, "그 뒤 동작 중지")
pl = sub.cloud_payload(); raw = json.dumps(pl, ensure_ascii=False)
ok("TS-30", G6, "Cloud로 올리는 내용", "UD-08·09", "name" not in pl["assets"][0] and "IMG_0001" not in raw and "photo" not in raw and free.cloud_payload() is None, "항목: " + ",".join(pl["assets"][0].keys()))
ok("TS-31", G6, "원장 사슬과 사건 코드", "P-03 · HDA-R2", app.led.verify() and all(r["code"][-3:] != "E00" for r in app.led.rows), "%d줄, 코드 없는 사건 0" % len(app.led.rows))

# ===== 사 =====
pm = mk("pcm"); w(pm, "HiCoffer베타2/07_품질검수/검수조서.pdf", b"%PDF-1.4 q"); w(pm, "HiCoffer베타2/04_설계안/설계서.docx", b"d"); w(pm, "아무데나/노래.mp3", b"ID3")
am = HiDAMApp(pm, projects=PROJ, mode="일반"); v1, _ = am.preview(); am.set_mode("시스템"); v2, _ = am.preview(); am.set_mode("프로젝트"); v3, _ = am.preview()
k = "HiCoffer베타2/07_품질검수/검수조서.pdf"
ok("TS-52", G7, "모드 셋: 같은 자산, 다른 자리", "MO-01~04", (v1[k]["place"], v2[k]["place"], v3[k]["place"]) == ("HiCoffer베타2/07_품질검수", "08.01", "P001-07") and v1[k]["code"] == v3[k]["code"] and v1[k]["project"] == "P001-07", (v1[k]["place"], v2[k]["place"], v3[k]["place"]))
ok("TS-53", G7, "프로젝트 모드에서 프로젝트 밖의 파일", "MO-05", v3["아무데나/노래.mp3"]["place"] == "08.05", "표준 자리로 내려감: 08.05")
ok("TS-54", G7, "프로젝트 단계 읽기", "PJ-03", v3["HiCoffer베타2/04_설계안/설계서.docx"]["project"] == "P001-04", "P001-04")
P = mk("mP"); am.plug(Medium("M-P", P, role="거울", scope="P001")); am.confirm_first("M-P"); am.mirror("M-P"); gp = snap(os.path.join(P, "_HiDAM_거울"))
ok("TS-55", G7, "매체에 프로젝트 역할: 그 프로젝트만 비춤", "RL-03", len(gp) == 2 and all("HiCoffer" in x for x in gp), sorted(gp))
am.set_role("M-P", "보관", "08"); 
ok("TS-56", G7, "매체 역할을 바꾸면 다시 확인받음", "RL-05 · ST-04", am.media["M-P"].first_ok is False and am.led.rows[-1]["code"] == "SCT-E04" and am.mirror("M-P")["stopped"] == "거울 역할이 아닌 매체", "역할 바꿈 SCT-E04")
n0 = len(am.led.rows); dd = am.dashboard(); am.cloud_payload()
ok("TS-59", G7, "화면 보기·올릴 내용 만들기는 원장에 쓰지 않음", "UD-01", len(am.led.rows) == n0 and os.path.exists(am.led.path) and all(r.get("at") and r.get("actor") for r in am.led.rows), "원장 줄 그대로, 줄마다 시각·행위자")
ok("TS-57", G7, "대시보드에 모드와 매체 역할", "UD-05 · MO-06", dd["1_내기기"]["mode"] == "프로젝트" and dd["1_내기기"]["media"][0]["role"] == "보관" and "P001-07" in dd["2_내디지털자산"]["by_place"], dd["2_내디지털자산"]["by_place"])

here = os.path.dirname(os.path.abspath(__file__))
out = dict(title="HiDAM.app 기준 구현 시뮬레이션", note="만든 파일로 돌린 시뮬레이션이며 실측이 아니다", policy=POLICY, app=APP_VER,
           code_sha256=sha(open(os.path.join(here, "hidam_app.py"), "rb").read()), scenario_sha256=sha(open(os.path.abspath(__file__), "rb").read()),
           ran_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), env="Python %s · %s" % (sys.version.split()[0], sys.platform), total=len(R), passed=sum(1 for r in R if r["result"] == "통과"),
           groups=[G1, G2, G3, G4, G5, G6, G7], cases=R, dashboard_sample=d, ledger_tail=app.led.rows[-5:])
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "sim_hidam_app_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in R:
    if r["result"] != "통과" or "-v" in sys.argv: print(r["no"], r["result"], r["title"], "|", r["seen"][:90])
print("합계", out["passed"], "/", out["total"])
shutil.rmtree(T)
