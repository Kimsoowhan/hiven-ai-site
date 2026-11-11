# -*- coding: utf-8 -*-
"""HiDAM.app 기준 구현 0.4 시뮬레이션(0.3의 시나리오 위에 OP-2의 넷과 변이 사본을 더함). 만든 파일로 돌린 것이며 실측이 아니다.
0.2의 시나리오 59건(TS-01~60)은 통과 조건을 바꾸지 않고 그대로 두었고, 0.3에서 넣은 것의 시나리오(TS-61~)와
「통과 조건이 늘 참이 아닌지」를 엔진의 한 줄을 일부러 틀리게 바꾼 사본으로 돌려 보는 확인(--no-mutants를 주면 건너뜀)을 더했다."""
import os, re, sys, json, shutil, tempfile, time, subprocess
ENGINE_DIR = os.environ.get("HIDAM_ENGINE_DIR") or os.path.dirname(os.path.abspath(__file__))   # 「늘 참」 확인 때는 틀리게 바꾼 엔진의 폴더
sys.path.insert(0, ENGINE_DIR)
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
ok("TS-35", G3, "처음 만난 판들(계보 없음), 한 판이 다른 판의 줄을 다 담고 가장 나중에 고쳐짐 → 스스로 맞춤(0.4에서 바꿈: 앞 판은 판 보관·매체 그대로, 지운 쪽이 더 나중이면 묻는 것은 TS-101)", "SY-03·08 · 기-1",
   rec["계획서"]["judge"] == "SY-최신" and rec["계획서"]["how"] == "자동" and rd(pcx, rec["계획서"]["final"]) == rd(C, "계획서_최종.txt") and snap(A) and rd(A, "계획서.txt") == base.encode(), rec["계획서"]["why"][:60])
ok("TS-38", G3, "날짜 이름 사진·다른 폴더의 같은 이름·빈 파일", "SY-03 · IX-06", not any(k.startswith("img") or k in ("readme", "빈") for k in rec), sorted(rec))
fin = app.choose("계획서", "txt", "M-C")
ok("TS-13", G3, "사용자가 고른 판이 최종본", "SY-06·09", sha(rd(pcx, fin)) == sha(rd(C, "계획서_최종.txt")), "최종본 바이트 = 고른 판 바이트")
before = {x: snap(x) for x in (A, B, C)}
w(B, "보고.md", "머리\n가 고침\n나\n다\n라\n마\n"); w(C, "보고.md", "머리\n가\n나\n다\n라\n마 고침\n")           # 바탕에서 두 갈래, 겹치지 않음
w(B, "회의.txt", "x\n의제\ny\n"); w(C, "회의.txt", "x\n논의\ny\n")                                           # 같은 대목을 다르게
w(B, "사슬.txt", "x\nY\nm\nz\n"); w(C, "사슬.txt", "x\nY\nm\nZ\n")                                               # 차례로 바꿔 쓴 것(C는 B를 보고 고침)
w(C, "지움.txt", "a\nc\n", now - 9000)                                                                            # 줄을 지운 것이 마지막 고침, 날짜는 가장 옛날
import collections as _co
rec = _co.defaultdict(lambda: dict(how=None, judge=None, why="", final_from=None, final=None), {r["stem"]: r for r in app.reconcile()})
m = rd(pcx, "기준자리/보고.md").decode() if ex(pcx, "기준자리/보고.md") else ""
ok("TS-14", G3, "갈라짐: 바탕이 확인되고 겹치지 않게 고침", "SY-07", rec["보고"]["how"] == "자동 합침" and "가 고침" in m and "마 고침" in m, m.replace("\n", "/"))
ok("TS-15", G3, "갈라짐: 같은 대목을 다르게 고침", "SY-07·08", rec["회의"]["how"] == "사용자가 고름" and not ex(pcx, "기준자리/회의.txt"), rec["회의"]["why"])
ok("TS-37", G3, "차례로 바꿔 쓴 사슬을 틀리게 합치지 않음", "SY-07·08", (rec["사슬"]["how"] == "사용자가 고름" and not ex(pcx, "기준자리/사슬.txt")) or (ex(pcx, "기준자리/사슬.txt") and rd(pcx, "기준자리/사슬.txt") == rd(C, "사슬.txt")), rec["사슬"]["why"])
ok("TS-36", G3, "줄을 지운 것이 마지막 고침", "SY-03·15", rec["지움"]["judge"] == "SY-최신" and rd(pcx, "기준자리/지움.txt") == b"a\nc\n", rec["지움"]["why"])
ok("TS-16", G3, "날짜가 속임(가장 옛 날짜가 최신 내용)", "SY-03", rec["지움"]["final_from"] == ["M-C"], rec["지움"]["final_from"])
ok("TS-17", G3, "글자 문서가 아닌 것: 처음 만난 같은 이름의 다른 그림은 판으로 묶지 않음(0.4에서 바꿈, K-16 · K-09 — 같은 자산의 갈라짐은 TS-111)", "SY-07 · K-16", "그림" not in rec, sorted(rec))
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
vt = [f for f in (os.listdir(os.path.join(D, "_HiDAM_금고")) if ex(D, "_HiDAM_금고") else [])]
ok("TS-44", G4, "보호 등급 자산은 그대로 비추지 않고 금고 거울로(잠가서, 이름도 숨김) · 열면 원본과 같음", "SV-03 · IX-14 · TG-04 · K-10",
   not ex(D, "_HiDAM_거울/개인/여권사본.pdf") and len(vt) >= 1 and not any("여권" in f for f in vt) and app.vault_restore("M-D", "개인/여권사본.pdf") == rd(pcx, "개인/여권사본.pdf")
   and all(b"passport" not in rd(os.path.join(D, "_HiDAM_금고"), f) and b"pp" not in rd(os.path.join(D, "_HiDAM_금고"), f)[-40:-32] for f in vt), "금고 %d칸, 바깥 이름은 해시" % len(vt))
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
r2 = {r["stem"]: r for r in app2.reconcile()}; first = r2.get("지움", {}).get("judge")
app2.import_lineage(app); r2 = _co.defaultdict(lambda: dict(how=None, judge=None, why="", final_from=None, final=None), {r["stem"]: r for r in app2.reconcile()})
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

# ======================================================================
# 0.3에서 더한 시나리오(TS-61~). 0.2의 59건은 위에 그대로 있고 통과 조건을 바꾸지 않았다.
# ======================================================================
G8, G9, G10, G11, G12, G13, G14 = "아 재시작·식별자", "자 자리·이름", "차 프로젝트", "카 묶음·갈래", "타 제시·스스로 돌기", "파 형식·중복·원장", "하 재검수 K의 높음"
def codes(a, frm=0): return [r["code"] for r in a.led.rows[frm:]]
def mv(root, a, b):
    os.makedirs(os.path.dirname(os.path.join(root, b)), exist_ok=True); os.rename(os.path.join(root, a), os.path.join(root, b))
def bag(root): return sorted(snap(root).values())
ALL_APPS = [free, sub, other, app, app2, f, fb, fm_, am, s]
def new(*a, **k):
    x = HiDAMApp(*a, **k); ALL_APPS.append(x); return x

# ===== 아 재시작·식별자 =====
r1, u1 = mk("r1"), mk("u1"); w(r1, "문서/노트.txt", "하나\n둘\n셋\n"); w(u1, "노트.txt", "하나\n둘\n셋\n")
e1 = new(r1, auto=False); e1.plug(Medium("U1", u1)); e1.reconcile(); n_before = len(e1.led.rows); head1 = e1.led.head; del e1
w(u1, "노트.txt", "하나\n셋\n넷\n")                               # 엔진이 꺼져 있는 동안 매체에서 고침(줄을 지우고 더함)
e2 = new(r1, auto=False); e2.plug(Medium("U1", u1)); rr2 = {r["stem"]: r for r in e2.reconcile()}
c1, cu = mk("c1"), mk("cu"); w(c1, "문서/노트.txt", "하나\n둘\n셋\n"); w(cu, "노트.txt", "하나\n셋\n넷\n")
ctl = new(c1, auto=False); ctl.plug(Medium("U1", cu)); rc_ = {r["stem"]: r for r in ctl.reconcile()}     # 견줌: 앞 색인이 없는 엔진은 같은 파일을 최신으로 정하지 못한다
ok("TS-61", G8, "엔진을 껐다 켠 뒤 계보가 이어짐", "항목 1 · SY-03 · DUP-11",
   rr2["노트"]["judge"] == "SY-최신" and rr2["노트"]["how"] == "자동" and rd(r1, rr2["노트"]["final"]) == "하나\n셋\n넷\n".encode()
   and rc_["노트"]["judge"] != "SY-최신" and e2.led.rows[n_before - 1]["h"] == head1 and e2.led.rows[n_before]["prev"] == head1 and "LED-E05" in codes(e2) and e2.led.verify(),
   "껐다 켠 엔진 %s(%s) · 앞 색인 없는 엔진 %s · 원장 %d줄 뒤에 이어 씀" % (rr2["노트"]["judge"], rr2["노트"]["how"], rc_["노트"]["judge"], n_before))
r2 = mk("r2"); w(r2, "a.txt", "1\n"); f1 = new(r2, tier="무료"); f1._keep_version("a.txt"); w(r2, "a.txt", "2\n"); x1 = f1.recover("a.txt", 1); x2 = f1.recover("a.txt", 1); f1._save(); del f1
f2 = new(r2, tier="무료"); x3 = f2.recover("a.txt", 1)
r3, u3 = mk("r3"), mk("u3"); g1 = new(r3, auto=False, mode="프로젝트"); g1.plug(Medium("U3", u3)); g1.set_role("U3", "거울", "08"); g1.confirm_first("U3"); g1.set_rename_policy("모드 규칙"); g1.user_rules["x.txt"] = "05.04"; g1._save(); del g1
g2 = new(r3, auto=False); m3 = g2.media["U3"]
ok("TS-62", G8, "껐다 켠 뒤 복구 횟수·모드·매체 역할·이름 규칙·사용자 규칙이 남음", "항목 1 · RT · MO · RL",
   x1["ok"] and x2["ok"] and not x3["ok"] and x3.get("left") == 0 and g2.mode == "프로젝트" and (m3.role, m3.scope, m3.first_ok, m3.plugged) == ("거울", "08", True, False)
   and g2.rename_policy == "모드 규칙" and g2.user_rules == {"x.txt": "05.04"},
   "무료 복구 2회 뒤 다시 켜도 3회째 거절 · 모드 %s · 매체 %s/%s 첫확인 %s, 다시 꽂기 전 뽑힘" % (g2.mode, m3.role, m3.scope, m3.first_ok))
r4 = mk("r4"); w(r4, "문서/메모.txt", "가\n"); h1 = new(r4, auto=False); h1.preview(); del h1
open(os.path.join(r4, "_HiDAM", "00.02_색인.json"), "wb").write(b"\x00\xff{{{ not json")
try: h2 = new(r4, auto=False); pv, _ = h2.preview(); died = False
except Exception as e_: died = repr(e_)
kept = [x for x in os.listdir(os.path.join(r4, "_HiDAM")) if "망가짐" in x]
lp = os.path.join(r4, "_HiDAM", "00.02_원장.jsonl"); open(lp, "ab").write(b'{"seq": 999, "eid": "DEV')      # 쓰다 끊긴 마지막 줄
try: h3 = new(r4, auto=False); h3.preview(); torn_ok = "LED-E07" in codes(h3) and h3.led.verify()
except Exception as e_: torn_ok = repr(e_)
lines = open(lp, encoding="utf-8").read().split("\n"); lines[1] = lines[1].replace('"엔진"', '"사용자"', 1); open(lp, "w", encoding="utf-8").write("\n".join(lines))   # 가운데 줄을 고침
try: h4 = new(r4, auto=False); alive = True
except Exception as e_: alive = repr(e_)
try: _r4 = h4.preview(); stopped = isinstance(_r4, dict) and "원장 사슬 끊김" in str(_r4.get("stopped"))
except RuntimeError: stopped = True
dz = h4.dashboard(); pz = [p for p in h4.proposals() if p["kind"] == "원장 새 사슬"]
az = h4.accept(pz[0]["no"]) if pz else {}; h4.preview(); keptl = [x for x in os.listdir(os.path.join(r4, "_HiDAM")) if "끊김" in x]; new_ok = h4.led.verify() and h4.led.rows[0]["code"] == "LED-E08" and h4.led.rows[0]["seq"] > 1; del h4
lines = open(lp, encoding="utf-8").read().split("\n"); open(lp, "w", encoding="utf-8").write("\n".join(lines[:-3]) + "\n")       # 뒤의 두 줄을 잘라 냄(남은 사슬은 맞음)
h5 = new(r4, auto=False)
ok("TS-63", G8, "색인 파일·원장 파일이 망가졌을 때 죽지 않음", "항목 1 · K-02",
   died is False and "문서/메모.txt" in pv and kept and "LED-E06" in codes(h2) and torn_ok is True and alive is True and stopped and dz["3_보호상태"]["state"] == "위험"
   and len(pz) == 1 and az.get("ok") and new_ok and keptl and h5.led.state == "끊김" and h5.boot[0] == ("원장", "끊김"),
   "색인 망가짐 → 다시 만듦(LED-E06), 망가진 파일 보존 %d · 끝줄 고침 %s · 가운데 줄 고침 → 적는 걸음 멈춤, 「새 사슬」 한 번 받아들임 뒤 이어짐 · 뒤의 줄을 잘라 낸 원장도 알아봄(장치카드의 마지막 줄 해시와 다름)" % (len(kept), torn_ok))
r5 = mk("r5"); w(r5, "문서/글월.txt", "첫 판\n"); w(r5, "사본/글월 - 복사본.txt", "첫 판\n"); k5 = new(r5, auto=False); k5.preview()
a0, v0 = k5.asset_of("문서/글월.txt"), k5.dev.index["문서/글월.txt"]["ver"]; same2 = k5.asset_of("사본/글월 - 복사본.txt") == a0; cp = [c for c in k5.copies(a0)]
w(r5, "문서/글월.txt", "첫 판\n고친 판\n"); k5.preview(); a1_, v1_ = k5.asset_of("문서/글월.txt"), k5.dev.index["문서/글월.txt"]["ver"]
ok("TS-64", G8, "내용을 고쳐도 자산 식별자는 그대로, 같은 내용 두 자리는 자산 하나의 사본 둘", "ID-11·13 · T-103·105",
   a0 == a1_ and v0 != v1_ and same2 and len(cp) == 2 and len(k5.assets[a0]["vers"]) == 2 and a0 == v0,
   "자산 %s 그대로 · 판 %s → %s · 사본 %d" % (a0, v0, v1_, len(cp)))
w(r5, "양식/양식.txt", "제목:\n내용:\n"); w(r5, "보고/3월보고.txt", "제목:\n내용:\n"); k5.preview(); ay = k5.asset_of("양식/양식.txt"); one = k5.asset_of("보고/3월보고.txt") == ay
w(r5, "보고/3월보고.txt", "제목: 3월\n내용: 매출\n"); k5.preview(); still = k5.asset_of("보고/3월보고.txt") == ay
ps_ = [p for p in k5.proposals() if p["kind"] == "자산 가르기"]; k5.accept(ps_[0]["no"]) if ps_ else None; an = k5.asset_of("보고/3월보고.txt")
ok("TS-65", G8, "양식을 베껴 따로 고침 → 가르기를 제시, 받아들이면 새 자산 식별자", "ID-13 · T-104",
   one and still and len(ps_) == 1 and ps_[0]["who"] == "한 번" and an == ay + "~1" and k5.asset_of("양식/양식.txt") == ay and "CLS-E09" in codes(k5),
   "받아들이기 전 같은 자산 %s · 뒤 %s" % (ay, an))
r6 = mk("r6")
for i in range(10): w(r6, "빈것/e%d.txt" % i, "")
import hidam_app as H
H.FP_LEN = 1; pair, seen_ = None, {}
for i in range(200):                                               # 지문 앞자리(한 글자로 줄여 봄)와 크기가 같고 전체 해시가 다른 두 내용
    b = ("%03d" % i).encode(); k = sha(b)[0]
    if k in seen_: pair = (seen_[k], b); break
    seen_[k] = b
w(r6, "겹침/x.bin", pair[0]); w(r6, "겹침/y.bin", pair[1]); k6 = new(r6, auto=False); k6.preview()
ax, ay_ = k6.asset_of("겹침/x.bin"), k6.asset_of("겹침/y.bin"); vx, vy = k6.dev.index["겹침/x.bin"]["ver"], k6.dev.index["겹침/y.bin"]["ver"]; H.FP_LEN = 16
o6, d6 = k6.dup_map()
ok("TS-66", G8, "빈 파일 열 개는 자산이 아님 · 지문 앞자리가 겹쳐도 전체 해시로 가름", "ID-14·15 · T-102",
   len(k6.empties) == 10 and all(k6.dev.index[r]["asset"] is None for r in k6.empties) and len(k6.assets) == 2 and vx == vy and ax != ay_ and ay_ == ax + "+2" and o6["dup_groups"] == 0,
   "빈 파일 %d(목록에만) · 자산 %d · 판 지문 같음(%s) → 자산 %s / %s" % (len(k6.empties), len(k6.assets), vx, ax, ay_))
r7 = mk("r7"); w(r7, "a.txt", "1\n"); f7 = new(r7, tier="무료"); f7._keep_version("a.txt"); w(r7, "a.txt", "2\n"); y1 = f7.recover("a.txt", 1); y2 = f7.recover("a.txt", 1)
mv(r7, "a.txt", "새이름.txt"); f7.preview(); y3 = f7.recover("새이름.txt", 1)
ok("TS-67", G8, "복구 횟수는 자산으로 셈(이름을 바꿔도 다시 생기지 않음)", "RT · A-19 · ID-11", y1["ok"] and y2["ok"] and not y3["ok"] and y3.get("guide") == "구독 안내" and codes(f7)[-1] == "LED-E03",
   "이름을 바꾼 뒤 3회째: %s" % ("거절(구독 안내)" if not y3["ok"] else "됨"))

# ===== 자 자리·이름 =====
def fill(root):
    w(root, "사진/IMG_1.jpg", JPG_SHOT + b"1"); w(root, "사진/IMG_2.jpg", JPG_SHOT + b"2"); w(root, "받은것/Screenshot_20260101.png", PNG + b"s")
    w(root, "프로그램/설치.exe", b"MZ" + b"\x00" * 70 + b"PE\x00\x00"); w(root, "NPKI/signCert.der", b"cert"); w(root, "개인/여권사본.pdf", b"%PDF-1.4 pp")
    w(root, "문서/계획.docx", b"plan"); w(root, "문서/모름.xyz", b"?"); w(root, "DCIM/Camera/c.jpg", JPG_SHOT + b"c")
    w(root, "서류/졸업_증명원.pdf", b"%PDF-1.4 gr")                   # 확신 높음(두 신호가 같은 영역)이면서 보호 등급 D3: 확인 없이 옮기면 안 되는 것
s1 = mk("s1"); fill(s1); fr = new(s1, tier="무료"); b0 = snap(s1); pl0 = fr.plan_places(); sm = fr.set_mode("시스템"); ap0 = fr.apply_places()
ok("TS-68", G9, "무료 층: 미리 보기는 되고 실제 배정·시스템 모드는 닫혀 있음", "CP-10 · FN-03 · FN-17", len(pl0) == 10 and all(p["code"] and p["std_name"] for p in pl0) and sm is False and not ap0["ok"]
   and snap(s1) == b0 and codes(fr)[-2:] == ["SCT-E09", "CLS-E11"] and fr.led.rows[-1]["res"] == "거절", "미리 보기 %d건 · 모드 바꿈 거절 · 배정 거절(%s) · 파일 그대로" % (len(pl0), ap0["why"]))
s2 = mk("s2"); fill(s2); on = new(s2, tier="무료", once=True); on.set_mode("시스템"); pl1 = [p for p in on.plan_places() if p["how"] == "자동" and p["moves"]]; b1 = bag(s2); ap1 = on.apply_places(); ap1b = on.apply_places()
ok("TS-69", G9, "기능 별도의 「한 번 적용」: 미리 보기 그대로 한 번만 배정", "FN-03 · CP-10", ap1["ok"] and sorted(a for a, _ in ap1["pairs"]) == sorted(p["rel"] for p in pl1) and ap1["moved"] == 4
   and all(nw.startswith(p["to"] + "/") for p in pl1 for o_, nw in ap1["pairs"] if o_ == p["rel"]) and bag(s2) == b1 and not ap1b["ok"], "미리 보기 자동 %d건 = 옮긴 %d건 · 내용 해시 묶음 같음 · 두 번째는 거절(%s)" % (len(pl1), ap1["moved"], ap1b.get("why")))
s3 = mk("s3"); fill(s3); sy = new(s3, mode="시스템", auto=False); b3, s3snap = bag(s3), snap(s3); ap3 = sy.apply_places(); moved3 = dict(ap3["pairs"])
keep3 = all(ex(s3, x) for x in ("NPKI/signCert.der", "개인/여권사본.pdf", "문서/계획.docx", "문서/모름.xyz", "DCIM/Camera/c.jpg", "서류/졸업_증명원.pdf"))
hi_d3 = [(p["conf"], p["grade"], p["how"]) for p in sy.plan_places() if p["rel"] == "서류/졸업_증명원.pdf"]
ok("TS-70", G9, "구독·시스템 모드의 실제 배정: 높음만, 보호 자산·보호 등급·꾸러미·중간·판정 대기는 그대로", "FN-03 · AP-05 · SV-03 · JR-1·2",
   ap3["ok"] and len(moved3) == 4 and moved3.get("사진/IMG_1.jpg", "").startswith("06_개인_가족/06_01_사진_영상/") and moved3.get("받은것/Screenshot_20260101.png") == "06_개인_가족/06_10_화면_캡처_녹화/Screenshot_20260101.png"
   and moved3.get("프로그램/설치.exe") == "09_설치_소프트웨어/09_02_업무_오피스/설치.exe" and keep3 and hi_d3 == [("높음", "D3", "확인 뒤")] and bag(s3) == b3 and codes(sy).count("CLS-E03") == 4 and codes(sy).count("LED-E09") == 4
   and all(r.get("old") and r.get("new") and r.get("undo") for r in sy.led.rows if r["code"] == "CLS-E03"), "옮김 4 · 그대로 6(확신 높음이어도 D3인 것 포함) · 내용 해시 묶음 같음 · 원장에 옛 자리·새 자리 4줄")
nw_ = moved3.get("사진/IMG_1.jpg", "없음"); vs = [v for v in sy.versions(nw_) if v["kind"] == "자리"]; rv = sy.recover(nw_, vs[0]["ver"]) if vs else dict(ok=False)
ok("TS-71", G9, "복구로 자리·이름까지 되돌아감", "LED · RS · 바꾸면 안 되는 원칙", rv["ok"] and ex(s3, "사진/IMG_1.jpg") and not ex(s3, nw_) and sha(rd(s3, "사진/IMG_1.jpg") if ex(s3, "사진/IMG_1.jpg") else b"") == s3snap[os.path.join("사진", "IMG_1.jpg")]
   and sy.led.rows[-1]["code"] == "LED-E02" and sy.led.rows[-1].get("what") == "자리·이름", "%s → 사진/IMG_1.jpg, 해시 같음" % nw_)
def newfile_case(tag, mode, policy):
    root = mk("nf_" + tag); w(root, "문서/있던것.txt", "x\n"); a = new(root, mode=mode, rename_policy=policy); a.preview()
    w(root, "바탕화면/여행~사진.jpg", JPG_SHOT + b"n"); w(root, "바탕화면/새 파일 (2).jpg", JPG_SHOT + b"m"); a.auto_run("바뀌면")
    return root, a, sorted(k.replace(os.sep, "/") for k in snap(root) if "있던것" not in k and "기준자리" not in k)
ra, aa, la_ = newfile_case("a", "시스템", None); rb, ab, lb = newfile_case("b", "시스템", "모드 규칙"); rc2, ac, lc = newfile_case("c", "일반", "모드 규칙")
day, ym = time.strftime("%Y%m%d"), time.strftime("%Y%m")
ok("TS-72", G9, "rename_policy 「보이기만」(기본): 새 파일에 자리는 붙고 이름은 그대로, 표준 이름은 옆에 보임", "NM-06·07 · GO-3 · T-118",
   aa.rename_policy == "보이기만" and la_ == ["06_개인_가족/06_01_사진_영상/%s_바탕화면/새 파일 (2).jpg" % ym, "06_개인_가족/06_01_사진_영상/%s_바탕화면/여행~사진.jpg" % ym] and len(aa.bundles) == 1 and "CLS-E04" not in codes(aa) and codes(aa).count("CLS-E03") == 2
   and aa.suggest["바탕화면/여행~사진.jpg"]["std_name"] == "여행_사진.jpg" and [(p["kind"], p["data"]["rels"]) for p in aa.props.values()] == [("자리 묶음", ["문서/있던것.txt"])], "이름 그대로 %s · 옆에 보인 이름 %s · 새 파일 때문에 물은 건수 0(이미 있던 파일의 묶음 제안 1건뿐)" % (la_, aa.suggest["바탕화면/여행~사진.jpg"]["std_name"]))
rn_rows = [r for r in ab.led.rows if r["code"] == "CLS-E04"]
ok("TS-73", G9, "rename_policy 「모드 규칙」: 새 파일에 표준 이름과 자리가 붙고 옛 이름이 원장에 남음", "NM-01~06 · T-118",
   lb == ["06_개인_가족/06_01_사진_영상/%s_바탕화면/%s_바탕화면.jpg" % (ym, day), "06_개인_가족/06_01_사진_영상/%s_바탕화면/여행_사진.jpg" % ym] and sorted(r["old_name"] for r in rn_rows) == ["새 파일 (2).jpg", "여행~사진.jpg"]
   and all(r["undo"] for r in rn_rows), "새 이름 %s · 옛 이름 원장 %d줄" % ([x.split("/")[-1] for x in lb], len(rn_rows)))
ok("TS-74", G9, "일반 모드: 새 파일을 옮기지도 이름을 바꾸지도 않고 표준 이름·자리를 옆에 보이기만", "NM-06 · MO-01",
   lc == ["바탕화면/새 파일 (2).jpg", "바탕화면/여행~사진.jpg"] and ac.suggest["바탕화면/여행~사진.jpg"] == dict(std_name="여행_사진.jpg", code="06.01", to=None) and "CLS-E03" not in codes(ac),
   "그대로 %s · 옆에 %s" % (lc, ac.suggest["바탕화면/여행~사진.jpg"]))
s4 = mk("s4"); w(s4, "있던것.txt", "x\n"); cl = new(s4, mode="시스템"); cl.preview(); w(s4, "가/IMG_7.jpg", JPG_SHOT + b"7a"); w(s4, "나/img_7.JPG", JPG_SHOT + b"7b"); w(s4, "다/IMG_8.jpg", JPG_SHOT + b"8")
cl.busy.add("다/IMG_8.jpg"); cl.auto_run("바뀌면"); l4 = sorted(k.replace(os.sep, "/") for k in snap(s4) if k.lower().endswith("jpg"))
ok("TS-75", G9, "이름이 겹치면 순번(대소문자만 다른 이름도 같은 이름) · 열려 있는 파일은 건너뛰고 보류로 적음", "NM-02·04 · M-03",
   l4 == ["06_개인_가족/06_01_사진_영상/IMG_7.jpg", "06_개인_가족/06_01_사진_영상/img_7_2.JPG", "다/IMG_8.jpg"] and cl.held == [("다/IMG_8.jpg", "RC-12")]
   and [r["rc"] for r in cl.led.rows if r["code"] == "CLS-E05"] == ["RC-12"], l4)
t0 = time.mktime((2026, 11, 5, 12, 0, 0, 0, 0, -1))
nm = [H.std_name(x, t0)[0] for x in ("HiDAM 표준 정립서 v1.1.docx", "보고서_20261103_v2.hwp", "HiDAM_표준_정립서-261111_1.0_작업.md", "회의록.docx", "CON.txt", "가·나:다*.txt", " 앞뒤 .txt", "IMG_0001.jpg", "제목 없음.txt")]
ok("TS-76", G9, "이름의 꼴: 판이 있는 문서 · 판이 없는 것 · 쓰지 않는 글자", "NM-01·02·04",
   nm == ["HiDAM_표준_정립서-261105_1.1.docx", "보고서-261103_2.0.hwp", "HiDAM_표준_정립서-261111_1.0_작업.md", "회의록.docx", "CON_.txt", "가_나_다_.txt", "앞뒤.txt", "IMG_0001.jpg", "20261105_파일.txt"], nm)
s5 = mk("s5"); w(s5, "가나건설/현장/도면.pdf", b"%PDF-1.4 d"); w(s5, "사진/무제.jpg", JPG_PLAIN + b"u"); pm_ = new(s5, orgs=ORGS, auto=False); q0, _ = pm_.preview()
mv(s5, "가나건설/현장/도면.pdf", "기타/도면.pdf"); q1, _ = pm_.preview(); np1 = len([p for p in pm_.proposals() if p["kind"] == "자리 바꿈"])
mv(s5, "기타/도면.pdf", "DCIM/도면.pdf"); q2, _ = pm_.preview(); pp = [p for p in pm_.proposals() if p["kind"] == "자리 바꿈"]; pm_.accept(pp[0]["no"]) if pp else None; q3, _ = pm_.preview()
n5 = len(pm_.led.rows); pm_.set_place("사진/무제.jpg", "06.08"); got5 = [r for r in pm_.led.rows[n5:] if r["code"] == "CLS-E02"]
ok("TS-77", G9, "자리 기억: 폴더를 옮겨도 스스로 바꾸지 않고, 더 앞선 순위의 새 신호일 때만 「자리를 바꿀까요」", "PL-11·12 · T-109 · A-20",
   q0["가나건설/현장/도면.pdf"]["code"] == "03.01" and q1["기타/도면.pdf"]["code"] == "03.01" and q1["기타/도면.pdf"].get("kept") == "자리 기억" and np1 == 0
   and q2["DCIM/도면.pdf"]["code"] == "03.01" and len(pp) == 1 and pp[0]["answer"] == "97.01" and q3["DCIM/도면.pdf"]["code"] == "97.01"
   and len(got5) == 1 and (got5[0]["old"], got5[0]["new"]) == ("99.01", "06.08"), "옮김 뒤 03.01 그대로(제안 0) → 꾸러미 폴더로 옮기자 제안 1건 → 받아들임 97.01 · 판정 대기 99.01 → 06.08 사건")
s6 = mk("s6"); w(s6, "받은것/도면.pdf", b"%PDF-1.4 d"); w(s6, "사진/무제.jpg", JPG_PLAIN + b"u"); pb = new(s6, device_id="DEV-PC-07", auto=False); pb.import_lineage(pm_); q6, _ = pb.preview()
s7 = mk("s7"); w(s7, "받은것/도면.pdf", b"%PDF-1.4 d"); pc_ = new(s7, device_id="DEV-PC-08", auto=False); q7, _ = pc_.preview(); pc_.import_lineage(pm_); q7b, _ = pc_.preview()
pq = [p for p in pc_.proposals() if p["kind"] == "자리 바꿈"]
ok("TS-78", G9, "사용자 규칙과 자리 기억을 다른 기기로 넘김", "PL-12 · SY-19", q6["받은것/도면.pdf"]["code"] == "97.01" and q6["사진/무제.jpg"]["code"] == "06.08"
   and q7["받은것/도면.pdf"]["code"] == "08.01" and q7b["받은것/도면.pdf"]["code"] == "08.01" and len(pq) == 1 and pq[0]["answer"] == "97.01" and "LNK-E04" in codes(pb),
   "새 기기: 받은 기억대로 97.01 · 사용자 규칙 06.08 / 이미 08.01로 기억한 기기: 스스로 바꾸지 않고 제안 1건")

# ===== 카 묶음·갈래 =====
gt = [H.gal_of(x) for x in ("04_설계안", "12_04_설계안", "품질검수", "07 품질검수 자료", "사례금영수증", "관리비", "감리교회", "06_통합사업", "설계안초안모음", "11_기타")]
cg = classify("내프로젝트/사례금영수증/a.pdf", b"%PDF", projects=(("내프로젝트", "P9"),))["project"]
ok("TS-79", G11, "갈래 읽기: 마디 번호이거나 온전한 낱말일 때만", "PL-07 · 항목 5", gt == ["04", "04", "07", "07", None, None, None, "06", None, None] and cg == "P9-xx", "%s · 사례금영수증 폴더 → %s" % (gt, cg))
b1r = mk("b1"); [w(b1r, "여행/2025 제주/IMG_%d.jpg" % i, JPG_SHOT + bytes([i])) for i in range(3)]; w(b1r, "여행/2025 제주/메모.txt", "m\n")
bx = new(b1r, auto=False); qb, _ = bx.preview(); bb = [b for b in bx.bundles.values()]
ok("TS-80", G11, "묶음의 자동 발급: 범주 안 일련번호와 사람이 읽는 이름", "PL-04·06 · CP-01", len(bb) == 1 and bb[0]["id"] == "06.01-B0001" and bb[0]["name"] == "2025_여행_제주" and bb[0]["btype"] == "00"
   and qb["여행/2025 제주/IMG_1.jpg"]["place_code"] == "KR-P / 06.01-B0001" and qb["여행/2025 제주/메모.txt"]["bundle"] is None and "CLS-E07" in codes(bx), "%s 「%s」 · 자리 %s" % (bb[0]["id"], bb[0]["name"], qb["여행/2025 제주/IMG_1.jpg"]["place_code"]))
[w(b1r, "여행/2025 제주/%s/P_%d.jpg" % (d_, i), JPG_SHOT + d_.encode() + bytes([i])) for d_ in ("첫째날", "둘째날") for i in range(2)]; bx.preview()
ids0 = sorted(b["id"] for b in bx.bundles.values() if b["state"] == "씀"); sp = bx.split_bundle("06.01-B0001", ["여행/2025 제주/첫째날", "여행/2025 제주/둘째날"])
mg_ = bx.merge_bundles(sp, "여행/2025 제주"); [w(b1r, "다른/부산/Q_%d.jpg" % i, JPG_SHOT + b"q" + bytes([i])) for i in range(2)]; bx.preview()
live_ = sorted(b["id"] for b in bx.bundles.values() if b["state"] == "씀"); olds = sorted(b["id"] for b in bx.bundles.values() if b["state"] == "옛 번호")
ok("TS-81", G11, "묶음을 가름·합침: 새 번호, 옛 번호는 다시 쓰지 않음, 대응표", "PL-05 · T-107", len(set(ids0 + sp + [mg_])) == len(ids0) + 3 and "06.01-B0001" in olds and all(x in olds for x in sp)
   and len(live_) == len(set(live_)) and not set(live_) & set(olds) and [m_["why"] for m_ in bx.bmap if m_["old"] in ["06.01-B0001"] + sp] == ["가름", "합침", "합침"] and codes(bx).count("CLS-E08") >= 3,
   "가름 %s → 합침 %s · 쓰는 번호 %s · 옛 번호 %s" % (sp, mg_, live_, olds))
dx, dy = mk("dx"), mk("dy")
[w(dx, "사진/제주/J_%d.jpg" % i, JPG_SHOT + b"j" + bytes([i])) for i in range(2)]; X = new(dx, device_id="DEV-PC-X", auto=False); X.preview()
[w(dy, "사진/부산/B_%d.jpg" % i, JPG_SHOT + b"b" + bytes([i])) for i in range(2)]; Y = new(dy, device_id="DEV-PC-Y", auto=False); Y.preview()
[w(dy, "사진/제주/J_%d.jpg" % i, JPG_SHOT + b"j" + bytes([i])) for i in range(2)]; Y.preview()
bid = lambda a, f_: next(b["id"] for b in a.bundles.values() if b["state"] == "씀" and b["folder"].endswith(f_))
pre = (bid(X, "제주"), bid(Y, "부산"), bid(Y, "제주")); mvd = X.sync_bundles(Y); post = (bid(X, "제주"), bid(Y, "부산"), bid(Y, "제주"))
ok("TS-82", G11, "두 기기에서 따로 발급된 묶음 번호가 겹침 → 뒤에 등록된 쪽을 옮기고 대응표", "PL-04 · T-108", pre == ("06.01-B0001", "06.01-B0001", "06.01-B0002") and post[0] == post[2] and post[1] != post[0]
   and len(Y.bmap) >= 1 and X.bseq["06.01"] == Y.bseq["06.01"] and len({post[0], post[1]}) == 2, "앞 %s → 뒤 %s · 옮긴 것 %s" % (pre, post, mvd))

# ===== 차 프로젝트 =====
pj = mk("pj")
w(pj, "HiCoffer_PC_베타2/01_기준원칙/과업내용-261020_1.0.pdf", b"%PDF-1.4 a"); w(pj, "HiCoffer_PC_베타2/03_설정안/요구정의서-261101_1.0.docx", b"req1")
w(pj, "HiCoffer_PC_베타2/04_설계안/설계서-261105_0.9_작업.docx", b"design-0.9"); w(pj, "HiCoffer_PC_베타2/06_수행결과/결과보고-261110_1.0.docx", b"result-1.0")
w(pj, "이사_2026/01_계약/계약서.pdf", b"%PDF-1.4 c"); w(pj, "이사_2026/02_견적/견적서.pdf", b"%PDF-1.4 e"); w(pj, "이사_2026/06_한일/이사완료.jpg", JPG_SHOT + b"mv")
w(pj, "급한일/03_설정안/요구.docx", b"rq"); w(pj, "급한일/06_수행결과/결과.docx", b"rs"); w(pj, "관리비/1월.pdf", b"%PDF-1.4 f"); w(pj, "사례금/영수증.pdf", b"%PDF-1.4 g")
P = new(pj, auto=False); v0_, _ = P.preview(); k4 = "HiCoffer_PC_베타2/04_설계안/설계서-261105_0.9_작업.docx"
cand = {p["what"]: p for p in P.proposals()}; mo = [p for p in P.proposals() if p["kind"] == "모드"][0]; pjs = [p for p in P.proposals() if p["kind"] == "프로젝트 묶기"]
before_ok = v0_[k4]["project"] is None and P.mode == "일반"
for p in pjs: P.accept(p["no"])
P.accept(mo["no"]); v1p, _ = P.preview(); B = {b["shown"]: b for b in P.bundles.values() if b["kind"] == "프로젝트"}; hb, mvb, ub = B["HiCoffer_PC_베타2"], B["이사_2026"], B["급한일"]
ok("TS-83", G10, "이름을 등록하지 않아도 프로젝트 후보를 뽑아 한 번 제시, 받아들이면 갈래·유형·국면이 선다", "MO-06·07 · PJ-06 · T-113",
   before_ok and len(pjs) == 3 and mo["answer"] == "프로젝트" and mo["who"] == "제시" and all(p["who"] == "한 번" for p in pjs) and P.mode == "프로젝트"
   and v1p[k4]["project"] == hb["id"] + "-04" and v1p[k4]["place_code"] == "KR-P / %s-04" % hb["id"] and (hb["btype"], hb["phase"], mvb["btype"], mvb["pack"]) == ("10", 3, "50", "생활")
   and hb["outs"][P.asset_of(k4)]["no"] == "04.01" and [x["no"] for x in hb["bl"]] == ["BL01"] and not any("관리비" in p["what"] or "사례금" in p["what"] for p in P.proposals(True)),
   "후보 3건(관리비·사례금 폴더는 후보 아님) · 모드 권함 %s · %s 유형 %s 국면 PH%d · 산출물 %s-04.01 · %s" % (mo["answer"], hb["id"], hb["btype"], hb["phase"], hb["id"], hb["bl"][0]["no"]))
ch = {b["shown"]: P.project_checks(b["id"]) for b in (hb, mvb, ub)}; kinds = lambda x: sorted({c["check"] for c in x})
ok("TS-84", G10, "빠진 산출물(확장판의 목록이 있을 때만): 기본 확장판과 생활 확장판", "8장 검사 ① · MO-08 · T-114",
   [c["target"] for c in ch["HiCoffer_PC_베타2"] if c["check"] == "빠진 산출물"] == ["05"] and [c["detail"][:4] for c in ch["이사_2026"] if c["check"] == "빠진 산출물"] == ["할 일 "]
   and ub["pack"] == "기본" and P.dashboard()["다_프로젝트"][0]["missing"] == ["05"], "기본: 05 수행안 빠짐 · 생활: 「할 일」 빠짐(화면 말은 확장판의 말)")
ok("TS-85", G10, "국면을 건너뜀 · 최종본 없이 다음 국면으로 감", "8장 검사 ②·③ · STG-03",
   [c["target"] for c in ch["급한일"] if c["check"] == "국면 건너뜀"] == ["PH2"] and "국면 건너뜀" not in kinds(ch["HiCoffer_PC_베타2"])
   and [c["target"] for c in ch["HiCoffer_PC_베타2"] if c["check"] == "최종본 없이 다음 국면"] == ["04.01"], "급한일: PH2 없이 PH3 · HiCoffer: 04.01이 0.9(작업본)인 채 PH3")
w(pj, "HiCoffer_PC_베타2/07_품질검수/검수조서-261111_1.0.pdf", b"%PDF-1.4 ac"); P.preview(); ac1 = hb["ac"][0]; okc = kinds(P.project_checks(hb["id"]))
aid4 = P.asset_of(k4); w(pj, k4, b"design-0.95 changed"); P.preview(); c2 = P.project_checks(hb["id"])
ok("TS-86", G10, "검수 조서를 낸 뒤 산출물을 고침 → 검수가 가리킨 판과 다름 · 기준선과 지금 판이 다름", "PJ-04 · 8장 검사 ④·⑦ · T-115",
   ac1["no"] == "AC01" and ac1["points"]["04.01"] == sha(b"design-0.9") and "검수 뒤 바뀜" not in okc and hb["phase"] == 4 and [x["no"] for x in hb["bl"]] == ["BL01", "BL02"] and [e["no"] for e in hb["ep"]] == ["EP01"]
   and P.asset_of(k4) == aid4 and [c["target"] for c in c2 if c["check"] == "검수 뒤 바뀜"] == ["04.01"] and [c["target"] for c in c2 if c["check"] == "기준선과 다름"] == ["04.01"],
   "AC01이 가리킨 판 ≠ 지금 판(자산·산출물 번호는 그대로) · BL02와 다름 · 증적 묶음 EP01")
w(pj, "HiCoffer_PC_베타2/09_감리/감리보고서.pdf", b"%PDF-1.4 au"); P.preview(); fno = P.add_finding(hb["id"], "AU01", "04.01"); c3 = [c["target"] for c in P.project_checks(hb["id"]) if c["check"] == "지적 미조치"]
w(pj, k4, b"design-0.97 fixed"); P.preview(); st1 = hb["finds"][0]["state"]; w(pj, "HiCoffer_PC_베타2/09_감리/AU01-001_조치결과.pdf", b"%PDF-1.4 fx"); P.preview(); st2 = hb["finds"][0]["state"]
ok("TS-87", G10, "감리 지적에 조치가 없음 → 미조치, 산출물 판이 오르면 조치 중, 조치 문서가 놓이면 조치 완료(제시)", "8장 검사 ⑤ · T-116",
   [a["no"] for a in hb["au"]] == ["AU01"] and fno == "AU01-001" and c3 == ["AU01-001"] and (st1, st2) == ("조치 중", "조치 완료") and "지적 미조치" not in kinds(P.project_checks(hb["id"])), "%s: 미조치 → %s → %s" % (fno, st1, st2))
rq = P.add_requirement(hb["id"]); c4 = P.project_checks(hb["id"]); P.link(hb["id"], rq, "04.01"); P.link(hb["id"], "04.01", "08.01"); c5 = P.project_checks(hb["id"])
P.set_external(hb["id"], "04.01", "고객산출물:D-03"); P.set_external(hb["id"], "06.01", "고객산출물:D-03"); c6 = P.project_checks(hb["id"])
ok("TS-88", G10, "추적 줄 끊김 · 증적에 든 판이 사라짐 · 바깥 번호 겹침", "8장 검사 ⑥·⑧·⑨ · CON-07 · PJ-05",
   [c["target"] for c in c4 if c["check"] == "추적 줄 끊김"] == [rq] and [c["target"] for c in c5 if c["check"] == "추적 줄 끊김"] == ["04.01→08.01"]
   and "EP01/04.01" in [c["target"] for c in c5 if c["check"] == "증적 판 사라짐"] and "EP01/06.01" not in [c["target"] for c in c5 if c["check"] == "증적 판 사라짐"]
   and len([c for c in c6 if c["check"] == "바깥 번호 겹침"]) == 1 and len(set(kinds(ch["HiCoffer_PC_베타2"]) + kinds(ch["급한일"]) + kinds(c2) + kinds(c5) + kinds(c6) + ["지적 미조치"])) == 9,
   "요구 %s 줄 없음 → 이음 · 없는 산출물로 이은 줄 끊김 · 고쳐서 사라진 판을 가리키는 증적 · 같은 바깥 번호 두 곳 · 검사 아홉 가지가 모두 한 번 이상 잡힘" % rq)

# ===== 타 제시·스스로 돌기 =====
t1 = mk("t1"); w(t1, "문서/보고.txt", "가\n나\n"); w(t1, "사진/IMG_1.jpg", JPG_SHOT + b"1"); w(t1, "사진/IMG_2.jpg", JPG_SHOT + b"2"); w(t1, "문서/계획서.docx", b"plan")
N1, N2, N3, N4 = mk("n1"), mk("n2"), mk("n3"), mk("n4")
w(N1, "보고.txt", "가\n나\n"); w(N1, "자료/참고.pdf", b"%PDF-1.4 r")
[w(N2, "DCIM/100CANON/IMG_900%d.jpg" % i, JPG_SHOT + b"c" + bytes([i])) for i in range(3)]
w(N4, "Backup_2025/a.doc", b"a"); w(N4, "Backup_2025/b.doc", b"b"); w(N4, "백업/c.hwp", b"c")
Z = new(t1); steps, exp = [], {x: snap(x) for x in (N1, N2, N4)}
def step(name, fn):
    r_ = fn(); same = all(snap(x) == exp[x] for x in (N1, N2, N4)) and not any(os.path.exists(os.path.join(x, d_)) for x in (N1, N2, N4) for d_ in ("_HiDAM", "_HiDAM_거울", "_HiDAM_보류함"))
    steps.append((name, same, len(Z.props))); return r_
roles0 = {}
for nm_, root_ in (("N1", N1), ("N2", N2), ("N3", N3), ("N4", N4)): step("꽂음 " + nm_, lambda: Z.plug(Medium(nm_, root_))); roles0[nm_] = Z.media[nm_].role
w(t1, "문서/새 메모.txt", "새로 만든 글\n"); step("기기에 새 파일", lambda: Z.auto_run("바뀌면"))
w(N1, "보고.txt", "가\n나\n다\n"); exp[N1] = snap(N1); step("작업 매체에서 고침", lambda: Z.auto_run("바뀌면"))
w(t1, "문서/새 메모.txt", "새로 만든 글\n고침\n"); la9 = step("기기에서 고침", lambda: Z.auto_run("때 되면"))
pz_ = Z.proposals(); ms0 = Z.measures(); role_ans = {p["what"].split("(")[1].split(")")[0]: p["answer"] for p in pz_ if p["kind"] == "매체 역할"}
ok("TS-89", G12, "처음 꽂은 매체의 역할을 권함, 받아들이기 전에는 작업", "RL-04 · T-111 · FW-5", role_ans == {"N2": "보관", "N3": "거울", "N4": "원천"} and set(roles0.values()) == {"작업"}
   and all(m.role == "작업" for m in Z.media.values()) and Z.mirror("N3")["stopped"] == "거울 역할이 아닌 매체" and not os.listdir(N3), "권한 역할 %s · 작업 모양의 N1은 묻지 않음 · 지금 역할은 모두 작업" % role_ans)
fz = new(mk("t1f"), tier="무료"); w(fz.dev.root, "a/04_설계안/x.txt", "x"); fz.preview()
ok("TS-90", G12, "모드를 권함(구독), 무료는 일반만이라 묻지 않음", "MO-06", [p["answer"] for p in pz_ if p["kind"] == "모드"] == ["시스템"] and Z.mode == "일반" and not [p for p in fz.proposals() if p["kind"] == "모드"],
   "구독: 「시스템」을 권함, 받아들이기 전 일반 · 무료: 모드 제안 0")
auto_done = dict(final=rd(t1, "기준자리/보고.txt") == "가\n나\n다\n".encode(), judged=len(Z.preview(log=False)[0]), bundles=len(Z.bundles), mirrored=sum(r.get("done", 0) for r in Z.led.rows if r["code"] == "SYN-E03"))
ok("TS-91", G12, "사용자가 아무것도 정하지 않고 매체 넷을 꽂고 파일을 만들고 고침: 기본값으로 어디까지 스스로 도는가, 몇 번 물었는가", "0장 · GO-1 · T-120",
   ms0["user_touches"] == 0 and ms0["asked"] == 4 and ms0["asked_once"] == 3 and ms0["asked_offer"] == 1 and auto_done["final"] and auto_done["mirrored"] == 0 and la9["result"] == "정상" and auto_done["judged"] == 6,
   "물은 건수 %d(한 번 %d · 제시 %d), 손댄 횟수 %d · 스스로: 판정 %d건, 묶음 %d, 계보로 최종본 맞춤 · 거울 0건(거울 역할을 받아들이기 전)" % (ms0["asked"], ms0["asked_once"], ms0["asked_offer"], ms0["user_touches"], auto_done["judged"], auto_done["bundles"]))
ok("TS-92", G12, "모든 걸음 뒤에 작업·보관·원천 매체의 폴더 전체 해시가 처음(사용자가 고친 뒤의 값)과 같음", "RL-06 · P-01 · A-34", len(steps) == 7 and all(s_[1] for s_ in steps), [(s_[0], "같음" if s_[1] else "다름") for s_ in steps])
for p in pz_: step("받아들임 " + p["kind"], lambda: Z.accept(p["no"]))
p2_ = Z.proposals(); [step("받아들임 " + p["kind"], lambda: Z.accept(p["no"])) for p in p2_]
w(t1, "바탕화면/Screenshot_20261111_101010.png", PNG + b"new"); asked_b = len(Z.props); step("새 화면 캡처", lambda: Z.auto_run("바뀌면")); asked_c = len(Z.props)
w(t1, "바탕화면/회의록.docx", b"minutes"); step("새 문서(확신 중간)", lambda: Z.auto_run("바뀌면")); ms1 = Z.measures(); gm = snap(os.path.join(N3, "_HiDAM_거울"))
ok("TS-93", G12, "권한 답을 그대로 받아들인 뒤: 모드·역할·거울·표준 자리가 서고, 새 파일에는 묻지 않고 자리가 붙음", "GO-3·4 · FW-3·4·5",
   Z.mode == "시스템" and (Z.media["N2"].role, Z.media["N2"].scope, Z.media["N3"].role, Z.media["N4"].role) == ("보관", "06.01", "거울", "원천") and len(pz_) == 4 and [p["kind"] for p in p2_] == ["자리 묶음"]
   and ex(t1, "06_개인_가족/06_10_화면_캡처_녹화/Screenshot_20261111_101010.png") and asked_c == asked_b and len(gm) >= 5 and ex(t1, "08_자료실/08_01_문서/%s_문서/계획서.docx" % ym)
   and all(s_[1] for s_ in steps) and ms1["user_touches"] == 5 and not ex(t1, "바탕화면/회의록.docx") and any(x.endswith("회의록.docx") for x in snap(os.path.join(t1, "08_자료실"))) and ms1["asked"] == 5 and "CLS-E13" in codes(Z),
   "받아들임 5번(모드 1 · 매체 3 · 자리 묶음 1) · 거울 %d건 · 새 화면 캡처는 물음 없이 자리 붙음 · 새 문서(중간)도 받아들인 범주라 물음 없이 자리 붙음(0.4에서 바꿈) → 물은 건수 모두 %d" % (len(gm), ms1["asked"]))

# ===== 파 형식·중복·원장 =====
fg = {n_: classify(n_, d_)["code"] for n_, d_ in (("a.zip", b"PK\x03\x04z"), ("a.iso", b"i"), ("a.dwg", b"d"), ("a.psd", b"p"), ("a.py", b"x=1"), ("a.sql", b"s"), ("a.log", b"l"), ("a.sqlite", b"q"),
                                               ("a.xyz", b"?"), ("README", b"r"), ("a.ttf", b"f"), ("a.exe", b"MZ"), ("a.svg", b"<svg"), ("a.mp3", b"ID3"), ("a.hwp", b"h"), ("가짜.pdf", JPG_SHOT))}
ok("TS-94", G13, "형식군 열둘 전부의 판정", "데이터 분류 체계 1장 · A-22", fg == {"a.zip": "97.06", "a.iso": "97.06", "a.dwg": "09.05", "a.psd": "09.05", "a.py": "05.04", "a.sql": "05.04", "a.log": "99.01", "a.sqlite": "99.01",
   "a.xyz": "99.02", "README": "99.02", "a.ttf": "09.05", "a.exe": "09.02", "a.svg": "99.01", "a.mp3": "08.05", "a.hwp": "08.01", "가짜.pdf": "06.01"} and H.fgroup("zip") == "압축·디스크 이미지" and H.fgroup("") == "확장자 없음" and H.fgroup("xyz") == "기타", fg)
wd = {n_: classify(n_, b"x")["code"] for n_ in ("졸업여행.jpg", "전세금_계약.pdf", "감성적인_글.txt", "무경력자_채용.pdf", "자동차보험.pdf", "최신고화질.mp4", "성적표.pdf", "2024_이력서_최종.docx", "경력기술서.docx", "여권사본.pdf", "세금 신고서.pdf", "졸업_증명서.pdf")}
ok("TS-95", G13, "낱말을 낱말 경계로 봄(우연히 든 낱말을 잡지 않음)", "JR-4·5 · A-22", wd == {"졸업여행.jpg": "99.01", "전세금_계약.pdf": "08.01", "감성적인_글.txt": "08.01", "무경력자_채용.pdf": "08.01", "자동차보험.pdf": "08.01",
   "최신고화질.mp4": "99.01", "성적표.pdf": "01.02", "2024_이력서_최종.docx": "02.01", "경력기술서.docx": "02.01", "여권사본.pdf": "01.01", "세금 신고서.pdf": "07.01", "졸업_증명서.pdf": "01.02"}, wd)
o1 = mk("o1"); w(o1, "글/가.txt", "제목  하나\r\n둘째 줄\r\n\r\n"); w(o1, "글/나.txt", "제목 하나\n둘째 줄\n"); w(o1, "글/다.txt", "제목 하나\n둘째 줄\n셋째\n")
[w(o1, "여행/p%d.bin" % i, b"trip%d" % i) for i in range(4)]; oa, ob, oc = mk("oa"), mk("ob"), mk("oc")
[w(oa, "복사/여행/p%d.bin" % i, b"trip%d" % i) for i in range(4)]; [w(ob, "일부/p%d.bin" % i, b"trip%d" % i) for i in range(2)]; [w(oc, "섞임/p%d.bin" % i, b"trip%d" % i) for i in (0, 1, 2)]; w(oc, "섞임/q.bin", b"other1"); w(oc, "섞임/r.bin", b"other2")
import zipfile
os.makedirs(os.path.join(o1, "압축"), exist_ok=True)
with zipfile.ZipFile(os.path.join(o1, "압축", "여행.zip"), "w") as z_:
    for i in range(4): z_.writestr("p%d.bin" % i, b"trip%d" % i)
w(o1, "압축/깨진.zip", b"PK\x03\x04 not a real zip")
O = new(o1, auto=False); [O.plug(Medium(n_, r_)) for n_, r_ in (("OA", oa), ("OB", ob), ("OC", oc))]; oo, od = O.dup_map(); deep = O.dup_deep()
ok("TS-96", G13, "내용 중복: 공백·줄바꿈만 다른 글자 문서", "DUP-B · IX-04", oo["content_groups"] == 1 and sorted(x[1] for x in deep["content"][0]["where"]) == ["글/가.txt", "글/나.txt"] and not any("가.txt" in v_[1] for g_ in od.values() for v_ in g_),
   "DUP-B 1무리(가·나), 다는 아님 · 완전 중복 목록에는 없음")
sk = {(x["a"][1], x["b"][1]): x["kind"] for x in deep["sets"]}; sk.update({(b_, a_): k_ for (a_, b_), k_ in list(sk.items())})
ok("TS-97", G13, "폴더째 겹침: 완전히 같음 · 한쪽이 다 들어 있음 · 몇 퍼센트 겹침", "SET · IX-12", sk.get(("여행", "복사/여행")) == "완전히 같음" and sk.get(("여행", "일부")) == "한쪽이 다 들어 있음" and sk.get(("여행", "섞임")) == "50% 겹침"
   and ("복사", "여행") in sk and oo["set_dups"] == len(deep["sets"]), sorted(set(sk.values())))
dv = [d_ for d_ in deep["derived"] if d_["zip"][1] == "압축/여행.zip"]
ok("TS-98", G13, "압축 ↔ 푼 폴더(파생), 깨진 압축 파일에도 죽지 않음", "DRV · 11장", {d_["folder"][1] for d_ in dv if d_["exact"]} >= {"여행", "복사/여행"} and not any(d_["zip"][1] == "압축/깨진.zip" for d_ in deep["derived"]) and dv[0]["entries"] == 4,
   "여행.zip ↔ %s" % sorted({d_["folder"][1] for d_ in dv if d_["exact"]}))
Z.bump_policy("HiDAM-STD-1.0(작업)+시험")
rows_all = [(a_.dev.dev_id, r) for a_ in ALL_APPS for r in a_.led.rows]
bad_rows = [r["code"] for _, r in rows_all if r["cause"] not in H.CAUSES or r["res"] not in H.RESULTS or (r["res"] in ("거절", "멈춤", "실패") and r["rc"] not in H.RC) or r["code"] not in H.EV.values()
            or not r["app"] or not r["policy"] or not r["eid"].endswith("#%d" % r["seq"])]
cs = {c_ for _, r in rows_all for c_ in [r["cause"]]}; rs_ = {r["res"] for _, r in rows_all}
ex_, ey_ = {r["eid"] for r in X.led.rows}, {r["eid"] for r in Y.led.rows}
ok("TS-99", G13, "원장 줄의 꼴: 원인·결과·까닭 코드 칸, 사건 코드가 없는 사건 0, 기기 둘의 사건 식별자가 겹치지 않음", "코드 분류 체계 6장 · CD-02 · T-119",
   not bad_rows and len(rows_all) > 400 and len(set(H.EV.values())) == len(H.EV) and all(re.match(r"^[A-Z]{3}-E\d\d$", c_) for c_ in H.EV.values()) and cs == set(H.CAUSES) and rs_ == set(H.RESULTS)
   and not ex_ & ey_ and any(r["policy"].endswith("+시험") for r in Z.led.rows) and [r for r in Z.led.rows if r["code"] == "SCT-E08"][0]["cause"] == "정책 판 올림"
   and {r["actor"] for _, r in rows_all} == {"엔진", "사용자", "자동 실행"}, "%d줄 모두 꼴에 맞음 · 본 원인 %d가지 · 결과 %s · 사건 코드 %d개" % (len(rows_all), len(cs), sorted(rs_), len(H.EV)))
n0z = len(Z.led.rows); dz_ = Z.dashboard(); cz = Z.cloud_payload(); rawz = json.dumps(cz, ensure_ascii=False); today = [r for r in Z.led.rows if r["at"][:10] == dz_["나_HiDAM이_해놓은_일"]["day"]]
dn = dz_["나_HiDAM이_해놓은_일"]
ok("TS-100", G13, "대시보드·올릴 내용의 새 칸: 제안 건수, 해 놓은 일(원장에서 셈), 프로젝트 국면, 잣대. 보기는 원장에 쓰지 않고 이름은 올리지 않음", "UD-01·08·09 · GO-4 · 항목 11",
   len(Z.led.rows) == n0z and dz_["가_한번만_봐주세요"]["count"] == len(Z.proposals()) == 0 and dn["placed"] == sum(1 for r in today if r["code"] == "CLS-E03") >= 4 and dn["finals"] >= 1 and dn["mirrored"] >= 5
   and dz_["라_잣대"]["asked"] == 5 and cz["measures"]["asked"] == 5 and cz["proposals"]["open"] == 0 and "회의록" not in rawz and "Screenshot" not in rawz and "보고" not in rawz and "N3" in rawz
   and P.cloud_payload()["projects"][0]["phase"] == "PH4" and "HiCoffer" not in json.dumps(P.cloud_payload(), ensure_ascii=False) and all(set(e_) == {"seq", "eid", "code", "cause", "res", "rc"} for e_ in cz["events"]),
   "한 번만 봐 주세요 %d건 · 오늘 자리 붙임 %d · 맞춘 판 %d · 비춘 거울 %d · 줄일 수 있는 용량 %d바이트 · 물은 건수 %d · 손댄 횟수 %d" % (dz_["가_한번만_봐주세요"]["count"], dn["placed"], dn["finals"], dn["mirrored"], dn["reclaim_bytes"], dz_["라_잣대"]["asked"], dz_["라_잣대"]["user_touches"]))
v1r, va, vb, vd = mk("v1"), mk("va"), mk("vb"), mk("vd"); w(va, "계획서.txt", "1장\n2장\n"); w(vb, "계획서.txt", "1장\n2장\n3장\n", time.time() - 9000)
V = new(v1r, auto=False); V.plug(Medium("VA", va)); V.plug(Medium("VB", vb)); V.reconcile(); pv1 = [p for p in V.proposals() if p["kind"] == "판 고르기"]; a1v = V.accept(pv1[0]["no"]) if pv1 else {}
V.plug(Medium("VD", vd, role="거울")); V.mirror("VD"); pv2 = [p for p in V.proposals() if p["kind"] == "첫 미러링"]; a2v = V.accept(pv2[0]["no"]) if pv2 else {}
for i in range(12): w(v1r, "많음/n%d.txt" % i, "n%d\n" % i)
V.mirror("VD")
for i in range(12): w(v1r, "많음/n%d.txt" % i, "바뀜 %d\n" % i)
mst = V.mirror("VD", auto=True); pv3 = [p for p in V.proposals() if p["kind"] == "대량 변경"]; a3v = V.accept(pv3[0]["no"]) if pv3 else {}
rest = [p["kind"] for p in V.proposals()]
ok("TS-101", G12, "묻는 것은 제안 한 곳으로: 계보 없는 판 고르기(권하는 답 먼저) · 첫 미러링 · 대량 변경을 받아들임 한 번씩으로", "GO-1 · SY-08 · MR-15·16 · 항목 6",
   len(pv1) == 1 and pv1[0]["answer"] == "VB" and a1v.get("ok") and rd(v1r, "기준자리/계획서.txt") == rd(vb, "계획서.txt") and len(pv2) == 1 and a2v.get("ok") and a2v["out"]["done"] >= 1
   and mst["stopped"] == "대량 변경 — 확인 필요" and len(pv3) == 1 and a3v.get("ok") and a3v["out"]["done"] == 12 and V.measures()["user_touches"] == 3 and rest == ["모드"]
   and all(set(p) == {"no", "kind", "what", "answer", "why", "if_not", "who", "state"} for p in V.proposals(True)), "권한 답 %s → 최종본 · 첫 미러링 %d건 · 대량 변경 12건 확인 뒤 비춤 · 손댄 횟수 3 · 남은 제안 %s" % (pv1[0]["answer"] if pv1 else None, a2v.get("out", {}).get("done", 0), rest))
# ===== 하 재검수 K의 높음(K-02~K-15. K-01은 TS-61·62) =====
import hidam_app as H2
def rdx(root, rel): return rd(root, rel) if ex(root, rel) else b""
lg = H2.Ledger("x", os.path.join(pc, "_HiDAM", "00.02_원장.jsonl")); st_pc = lg.load(); eids = [r["eid"] for r in lg.rows]
k2 = mk("k2"); w(k2, "a.txt", "x\n"); E1 = new(k2, auto=False); E1.preview(); E1.preview(); ok_before = E1.dashboard()["6_기록"]["chain_ok"]
lk = os.path.join(k2, "_HiDAM", "00.02_원장.jsonl"); raw_ = open(lk, encoding="utf-8").read(); open(lk, "w", encoding="utf-8", newline="\n").write(raw_.replace('"엔진"', '"지원"', 1)); dk = E1.dashboard()
try: _r2 = E1.preview(); st2 = isinstance(_r2, dict) and "원장 사슬 끊김" in str(_r2.get("stopped"))
except RuntimeError: st2 = True
ok("TS-102", G14, "같은 기기 폴더에 엔진 둘(TS-01·02가 그렇다)이어도 원장은 한 사슬 · 돌고 있는 동안 원장 파일을 손으로 고치면 알아봄", "K-02 · K-02(P-03)",
   st_pc == "이음" and lg.verify() and len(eids) == len(set(eids)) and {r["actor"] for r in lg.rows} and len(lg.rows) == len(sub.led.rows) and ok_before
   and dk["6_기록"]["chain_ok"] is False and dk["3_보호상태"]["state"] == "위험" and st2, "무료·구독 엔진이 함께 쓴 원장 %d줄: 사슬 맞음, 겹친 사건 식별자 0 · 파일을 고치자 화면에 「위험」, 적는 걸음 멈춤" % len(lg.rows))
def roll(order):
    root, ma, mb = mk("k3_" + order), mk("k3a_" + order), mk("k3b_" + order); v1, v2 = "1\n2\n3\n", "1\n2\n3\n4\n"
    w(ma, "문서.txt", v1); w(mb, "문서.txt", v1); a = new(root, auto=False); a.plug(Medium("KA", ma)); a.plug(Medium("KB", mb))
    w(ma, "문서.txt", v2); w(mb, "문서.txt", v2); a.reconcile(); a.unplug("KA"); a.unplug("KB"); w(mb, "문서.txt", v1)                 # 한쪽만 옛 판으로 되돌림(옛 백업으로 덮어씀)
    for d_ in order: a.plug(Medium("K" + d_, ma if d_ == "A" else mb))
    r_ = {x["stem"]: x for x in a.reconcile()}["문서"]; return r_["judge"], rdx(root, "기준자리/문서.txt").decode(), "SYN-E08" in codes(a)
ra_, rb_ = roll("AB"), roll("BA")
k3 = mk("k3c"); mc_, md_ = mk("k3m"), mk("k3n"); w(mc_, "메모.txt", "장보기\n우유\n달걀\n빵\n"); w(md_, "메모.txt", "장보기\n우유\n달걀\n빵\n"); K3 = new(k3, auto=False); K3.plug(Medium("KC", mc_)); K3.plug(Medium("KD", md_))
a_old = K3.asset_of("메모.txt", K3.media["KC"]); os.remove(os.path.join(mc_, "메모.txt")); w(mc_, "메모.txt", "회의 안건\n예산\n일정\n담당\n"); r3_ = {x["stem"]: x for x in K3.reconcile()}
ok("TS-103", G14, "옛 판으로 덮어쓴 것을 「뒤 판」으로 잇지 않음(꽂는 순서와 무관) · 같은 이름으로 다시 만든 다른 글은 다른 자산", "K-03 · K-04 · SY-03",
   ra_ == rb_ == ("SY-최신", "1\n2\n3\n4\n", True) and "메모" not in r3_ and not ex(k3, "기준자리/메모.txt") and K3.asset_of("메모.txt", K3.media["KC"]) != a_old and "SYN-E08" in codes(K3),
   "두 순서 모두 최종본은 넷째 줄이 있는 판 그대로 · 다시 만든 메모는 판으로 묶이지 않고 새 자산")
k5a, k5b, k5m = mk("k5a"), mk("k5b"), mk("k5m"); w(k5m, "글.txt", "가\n나\n다\n"); A5 = new(k5a, device_id="DEV-K5A", auto=False); A5.plug(Medium("K5M", k5m)); w(k5m, "글.txt", "가\n나\n다\n라\n"); A5.reconcile()
B5 = new(k5b, device_id="DEV-K5B", auto=False); h_old, h_new = sha("가\n나\n다\n".encode()), sha("가\n나\n다\n라\n".encode()); B5.anc[h_old] = {h_new}       # 틀린 계보: 옛 판이 새 판의 뒤라고 적힘
n5a = len(A5.led.rows); ok5 = A5.import_lineage(B5); still5 = A5._desc(h_new, h_old) and not A5._desc(h_old, h_new)
F5 = new(mk("k5f"), tier="무료"); mf = mk("k5fm"); w(F5.dev.root, "계획.txt", "1\n2\n"); w(mf, "계획.txt", "1\n2\n3\n"); F5.plug(Medium("FM", mf)); F5.preview(); n5f = len(F5.led.rows)
fr5 = (F5.choose("계획", "txt", "FM"), F5.set_role("FM", "보관", "08"), F5.set_mode("프로젝트"), F5.import_lineage(A5)); fc5 = codes(F5, n5f)
ok("TS-104", G14, "이 기기의 계보와 거꾸로인 계보는 받지 않고 받은 사실을 원장에 남김 · 무료 층에서 판 고르기·매체 역할·모드·계보 받기가 닫혀 있음", "K-05 · K-11 · FN-06·17",
   ok5 and still5 and [r["rc"] for r in A5.led.rows[n5a:] if r["code"] == "LNK-E05"] == ["RC-25"] and "LNK-E04" in codes(A5, n5a)
   and fr5 == (None, False, False, False) and fc5 == ["SYN-E06", "SCT-E11", "SCT-E09", "LNK-E05"] and not ex(F5.dev.root, "기준자리") and F5.media["FM"].role == "작업" and F5.mode == "일반",
   "거꾸로인 줄 1건 거절(RC-25), 받음 사건 남음 · 무료: 넷 다 거절 %s, 최종본 안 만듦" % fc5)
k6, k6a, k6b = mk("k6"), mk("k6a"), mk("k6b"); w(k6a, "메모.txt", "장보기\n우유\n달걀\n빵\n"); w(k6b, "메모.txt", "회의 안건\n예산\n일정\n담당\n"); w(k6a, "가/목록.txt", "ㄱ\nㄴ\nㄷ\nㄹ\nㅁ\n"); w(k6b, "가/목록.txt", "ㄱ\nㄴ\nㄷ\nㄹ\nㅁ\n")
w(k6a, "나/목록.txt", "하나\n둘\n셋\n넷\n다섯\n"); w(k6b, "나/목록.txt", "하나\n둘\n셋\n넷\n다섯\n"); w(k6, "기준자리/보고.txt", "사용자가 여기에 둔 다른 글\n둘째 줄\n셋째 줄\n"); w(k6a, "보고.txt", "보고 1\n보고 2\n보고 3\n")
k6c, k6d = mk("k6c"), mk("k6d"); w(k6c, "메모.txt", "장보기\n우유\n달걀\n빵\n"); w(k6d, "메모.txt", "회의 안건\n예산\n일정\n담당\n"); w(k6c, "나/목록.txt", "하나\n둘\n셋\n넷\n다섯\n"); w(k6c, "보고.txt", "보고 1\n보고 2\n보고 3\n")     # 옛 판이 남아 있는 다른 매체 둘
K6 = new(k6, auto=False); [K6.plug(Medium(n_, r_)) for n_, r_ in (("K6A", k6a), ("K6B", k6b), ("K6C", k6c), ("K6D", k6d))]; K6.reconcile()
w(k6a, "메모.txt", "장보기\n우유\n달걀\n빵\n과자\n"); w(k6b, "메모.txt", "회의 안건\n예산\n일정\n담당\n장소\n"); w(k6a, "보고.txt", "보고 1\n보고 2\n보고 3\n보고 4\n")
w(k6a, "나/목록.txt", "하나 고침\n둘\n셋\n넷\n다섯\n"); w(k6b, "나/목록.txt", "하나\n둘\n셋\n넷\n다섯 고침\n"); w(k6a, "가/목록.txt", "ㄱ\nㄴ\nㄷ\nㄹ\nㅁ\nㅂ\n"); r6 = K6.reconcile(); r6b = K6.reconcile()
memo = sorted(rdx(k6, x).decode().split("\n")[0] for x in ("기준자리/메모.txt", "기준자리/메모_2.txt") if ex(k6, x))
ok("TS-105", G14, "이름만 같은 다른 것의 최종본을 덮지 않음(순번 자리) · 합친 것은 자기 무리의 자리에 · 사용자가 기준 자리에 둔 다른 글을 덮지 않음", "K-06 · K-07 · K-19 · SY-09",
   memo == ["장보기", "회의 안건"] and rdx(k6, "기준자리/가/목록.txt").decode().endswith("ㅂ\n") and rdx(k6, "기준자리/나/목록.txt").decode() == "하나 고침\n둘\n셋\n넷\n다섯 고침\n"
   and rdx(k6, "기준자리/보고.txt").decode().startswith("사용자가 여기에") and rdx(k6, "기준자리/보고_2.txt").decode().endswith("보고 4\n") and [x["final"] for x in r6] == [x["final"] for x in r6b]
   and K6.asset_of("기준자리/메모.txt") != K6.asset_of("기준자리/메모_2.txt"), "메모 둘의 최종본이 따로(%s) · 가/목록과 나/목록이 제자리 · 사용자의 글은 그대로, 엔진의 최종본은 보고_2.txt · 되풀이해도 같은 자리" % memo)
k8, k8a, k8b = mk("k8"), mk("k8a"), mk("k8b"); c3, c4, c5 = "1장\n2장\n3장\n", "1장\n2장\n3장\n4장\n", "1장\n2장\n3장\n4장\n5장\n"
w(k8, "책.txt", c3); w(k8a, "책.txt", c3); w(k8b, "책.txt", c3); K8 = new(k8); K8.plug(Medium("K8A", k8a)); K8.plug(Medium("K8B", k8b)); w(k8a, "책.txt", c4); K8.auto_run("바뀌면"); w(k8b, "책.txt", c4); K8.auto_run("바뀌면"); w(k8b, "책.txt", c5); K8.auto_run("바뀌면")
f5_ = rdx(k8, "기준자리/책.txt").decode(); v4 = [v["ver"] for v in K8.versions("기준자리/책.txt") if v["hash"] == sha(c4.encode())]; rv8 = K8.recover("기준자리/책.txt", v4[0]) if v4 else dict(ok=False); l8 = K8.auto_run("때 되면"); l8b = K8.auto_run("때 되면")
ok("TS-106", G14, "복구한 것을 자동 실행이 되돌리지 않음(다른 판이 여럿 있어도) · 복구 사건의 행위자는 사용자", "K-08 · K-26 · SY-11", f5_ == c5 and rv8["ok"] and rdx(k8, "기준자리/책.txt").decode() == c4
   and [r["actor"] for r in K8.led.rows if r["code"] == "LED-E02"] == ["사용자"], "기기 3장 · 매체 4장·5장 → 5장으로 맞춘 뒤 4장 판으로 복구 → 자동 실행 두 번 뒤에도 4장 그대로(%s)" % l8b["result"])
k12, k12m, k12t = mk("k12"), mk("k12m"), mk("k12t"); w(k12, "문서/a.txt", "a\n"); w(k12, "문서/b.txt", "b\n"); w(k12, "c.txt", "c\n"); os.makedirs(os.path.join(k12m, "_HiDAM_거울")); w(k12m, "_HiDAM_거울/문서", "폴더가 있어야 할 자리에 놓인 파일")
K12 = new(k12, auto=False); K12.plug(Medium("K12M", k12m, role="거울")); K12.confirm_first("K12M")
try: m1 = K12.mirror("K12M"); crash12 = None
except Exception as e_: m1, crash12 = {}, repr(e_)
os.remove(os.path.join(k12m, "_HiDAM_거울", "문서")); w(k12m, "_HiDAM_거울/남은.hidam_tmp", "쓰다 만 것"); m2 = K12.mirror("K12M")
w(k12t, "정상.txt", "ok\n"); w(k12t, "보고서.pdf.exe", b"MZ" + b"x" * 80); w(k12t, "_HiDAM_x/숨긴.pdf.exe", b"MZ" + b"y" * 80)
try: os.symlink(os.path.join(k12t, "없는곳"), os.path.join(k12t, "깨진바로가기.txt")); linked = True
except (OSError, NotImplementedError, AttributeError): linked = False
try: p12 = K12.plug(Medium("K12T", k12t)); crash13 = None
except Exception as e_: p12, crash13 = None, repr(e_)
pt = [p for p in K12.proposals() if p["kind"] == "위험 매체"]; at = K12.accept(pt[0]["no"]) if pt else {}; T12 = K12.media["K12T"]; w(k12t, "뒤에생김.pdf.exe", b"MZ" + b"z" * 80); K12.reconcile()
ok("TS-107", G14, "거울 매체에 쓰지 못해도 죽지 않고 멈춤 · 읽지 못하는 파일은 그 파일만 「보지 못함」 · 위험 표시 매체를 한 번의 결정으로 풀 수 있고 숨긴·뒤에 생긴 위협도 표시", "K-12 · K-13 · K-14 · AP-08 · NC-06",
   crash12 is None and m1.get("stopped", "").startswith("매체에 쓰지 못함") and "SYN-E09" in codes(K12) and m2["stopped"] is None and m2["done"] >= 2 and not ex(k12m, "_HiDAM_거울/남은.hidam_tmp")
   and crash13 is None and p12.startswith("위험") and (not linked or T12.unseen == ["깨진바로가기.txt"]) and len(pt) == 1 and at.get("ok") and T12.blocked is None
   and set(T12.flags) == {"_HiDAM_x/숨긴.pdf.exe", "보고서.pdf.exe", "뒤에생김.pdf.exe"} and all(ex(k12t, x) for x in T12.flags) and "정상.txt" in T12.index,
   "쓰기 실패 → 「%s」(SYN-E09), 길이 열리자 %d건 비춤, 임시 파일 치움 · 깨진 바로가기 %s · 위험 표시 3건(숨긴 것·뒤에 생긴 것 포함)을 뺀 채 매체 씀, 파일은 제자리" % (m1.get("stopped"), m2["done"], "보지 못함 1" if linked else "만들 수 없는 환경"))
k15, k15m = mk("k15"), mk("k15m"); w(k15, "DCIM/Camera/a.jpg", JPG_SHOT + b"k"); w(k15, "서류/졸업증명서.pdf", b"%PDF-1.4 g"); w(k15, "문서/입주민 공지.txt", "공지\n"); w(k15, "문서/주민등록등본.pdf", b"%PDF-1.4 j"); w(k15, "문서/비밀의 숲 대본.txt", "대본\n"); w(k15, "문서/주민센터 안내문.txt", "안내\n")
K15 = new(k15, auto=False); g0 = K15.preview()[0]; K15.set_place("DCIM/Camera/a.jpg", "08.04"); bad15 = K15.set_place("문서/입주민 공지.txt", "ZZ.99"); g1 = K15.preview()[0]
K15.plug(Medium("K15M", k15m, role="거울")); K15.confirm_first("K15M"); K15.mirror("K15M"); d15 = K15.dashboard(); got15 = sorted(k.replace(os.sep, "/") for k in snap(os.path.join(k15m, "_HiDAM_거울")))
ok("TS-108", G14, "사용자 규칙으로 등급이 낮아지지 않음 · 보호 등급이라 거울에서 빠진 것이 화면에 보임(정상이라 하지 않음) · 등급 낱말도 낱말 경계로", "K-15 · K-10 · K-27 · K-29 · SV-02·04",
   (g0["DCIM/Camera/a.jpg"]["grade"], g1["DCIM/Camera/a.jpg"]["code"], g1["DCIM/Camera/a.jpg"]["grade"]) == ("D3", "08.04", "D3") and bad15 is None
   and [g1["문서/" + x]["grade"] for x in ("입주민 공지.txt", "주민등록등본.pdf", "비밀의 숲 대본.txt", "주민센터 안내문.txt")] == ["D0", "D3", "D0", "D0"]
   and got15 == ["문서/비밀의 숲 대본.txt", "문서/입주민 공지.txt", "문서/주민센터 안내문.txt"] and d15["4_거울상태"]["protected_waiting"] == 0 and d15["5_금고"]["count"] == 3
   and all(K15.vault_restore("K15M", x) == rd(k15, x) for x in ("DCIM/Camera/a.jpg", "서류/졸업증명서.pdf", "문서/주민등록등본.pdf")),
   "꾸러미 안 사진에 사용자 규칙 08.04: 자리는 바뀌어도 등급은 D3 그대로(거울로 가지 않음) · 없는 코드 거절 · 거울 3건, 보호 등급 3건은 「비추지 못함」으로 보임")
k9, k9a, k9b = mk("k9"), mk("k9a"), mk("k9b")
for i in range(20): w(k9a, "DCIM/100CANON/IMG_%04d.jpg" % i, JPG_SHOT + b"A%d" % i); w(k9b, "DCIM/100CANON/IMG_%04d.jpg" % i, JPG_SHOT + b"B%d" % i)
for x_, t_ in ((k9a, b"[a]"), (k9b, b"[b]")): w(x_, "desktop.ini", t_); w(x_, "Thumbs.db", t_ + b"t"); w(x_, ".DS_Store", t_ + b"d")
K9 = new(k9); K9.plug(Medium("K9A", k9a)); K9.plug(Medium("K9B", k9b)); r9 = K9.reconcile(); d9 = K9.dashboard()
ok("TS-109", G14, "이름이 같은 카메라 번호 사진(서로 다른 사진)과 운영체제가 만든 파일을 판으로 묶어 묻지 않음", "K-09 · JR-2 · DUP-X", r9 == [] and d9["2_내디지털자산"]["unsettled"] == 0 and not [p for p in K9.proposals() if p["kind"] == "판 고르기"],
   "카메라 사진 20쌍·시스템 파일 3쌍: 판 묶음 0, 묻는 것 0(0.2는 23건을 물음) · 남은 제안은 매체 역할·모드뿐 %s" % sorted({p["kind"] for p in K9.proposals()}))
MEASURES = dict(no_setting=dict(asked=ms0["asked"], asked_once=ms0["asked_once"], asked_offer=ms0["asked_offer"], user_touches=ms0["user_touches"], auto=auto_done, pending_ratio=ms0["pending_ratio"]),
                after_accept=dict(asked=ms1["asked"], accepted=ms1["accepted"], user_touches=ms1["user_touches"], open=ms1["open"], pending_ratio=ms1["pending_ratio"]), steps=[(s_[0], "같음" if s_[1] else "다름") for s_ in steps])
d = dz_

here = os.path.dirname(os.path.abspath(__file__))
ARGS = [a for a in sys.argv[1:] if not a.startswith("-")]
# ===== 「늘 참」 확인: 엔진의 한 줄을 일부러 틀리게 바꾼 사본에서 해당 시나리오가 실패하는가 =====
MUTANTS = [   # (무엇을 틀리게, [(원래 줄, 바꾼 줄)...], 실패해야 하는 시나리오)
    ("같은 자리에서 내용이 바뀌어도 같은 자산으로 잇지 않음(잇는 길이 둘이라 두 줄을 함께 바꿈)", [('aid = self._join(h, prev)             # 같은 자리', 'aid = self._new_asset(h, it["size"])   # 같은 자리'),
        ("        elif b:\n            self._join(child, b)", "        elif b:\n            pass")], ["TS-64"]),
    ("다시 꽂은 매체의 앞 색인을 잇지 않음", [("            m.index = known.index\n", "            m.index = {}\n")], ["TS-61"]),
    ("복구 횟수를 자산이 아니라 경로로 셈", [('used = self.recover_count.get(aid, 0)', 'ck = "자리:" + norm(rel); used = self.recover_count.get(ck, 0)'),
        ('            self.recover_count[aid] = used + 1\n            self.led.add("LED", "복구", rel=rel, ver=ver, tier=self.tier, what="내용", asset=aid)', '            self.recover_count[ck] = used + 1\n            self.led.add("LED", "복구", rel=rel, ver=ver, tier=self.tier, what="내용", asset=aid)')], ["TS-67"]),
    ("이름 규칙 스위치를 보지 않고 늘 이름을 바꿈", [('            self._apply(auto, rename=self.rename_policy == "모드 규칙")', '            self._apply(auto, rename=True)')], ["TS-72"]),
    ("「한 번 적용」이 한 번으로 닫히지 않음", [('            self.once = False                             # 한 번 적용은', '            pass                                          # 한 번 적용은')], ["TS-69"]),
    ("무료 층에서 시스템 모드가 열림", [('        if self.tier != "구독" and mode != "일반" and not self.once:', '        if False:')], ["TS-68"]),
    ("낱말을 부분 일치로 봄", [("        if t == w or (t.startswith(w) and t[len(w):] in tails):", "        if w in t:")], ["TS-95"]),
    ("갈래를 폴더 이름의 부분 일치로 읽음", [("        if v in toks:\n            return k\n    return None\n\n\ndef gal_named", "        if v in f:\n            return k\n    return None\n\n\ndef gal_named")], ["TS-79"]),
    ("검수 뒤 바뀜 검사가 판을 견주지 않음", [('add("검수 뒤 바뀜", no,', 'False and add("검수 뒤 바뀜", no,')], ["TS-86"]),
    ("자리 기억을 보지 않고 늘 새로 판정", [('c.update(code=mem["code"], rank=mem["rank"], conf="높음", kept="자리 기억")', 'pass')], ["TS-77"]),
    ("대량 변경 멈춤 줄에 까닭 코드를 적지 않음", [('res="멈춤", rc="RC-06", medium=dev_id', 'res="멈춤", medium=dev_id')], ["TS-99"]),
    ("작업 매체에 엔진 자리를 만듦", [('        m.blocked = None\n        if not known', '        m.blocked = None\n        os.makedirs(os.path.join(m.root, "_HiDAM"), exist_ok=True)\n        if not known')], ["TS-28", "TS-92"]),
    ("옮기기 전 자리를 판 목록·원장에 남기지 않음", [("                n = self._keep_place(rel, new_rel)\n", "                n = len(self.vmeta.setdefault(c['asset'], [])) + 1; self.vmeta[c['asset']].append(dict(ver=n, kind='없음', rel=rel))\n")], ["TS-70", "TS-71"]),
    ("껐다 켤 때 복구 횟수를 읽지 않음", [('self.finals, self.recover_count = idx["finals"], idx["recover_count"]', 'self.finals = idx["finals"]')], ["TS-62"]),
    ("빈 파일도 자산으로 등록", [('            if not it["size"]:\n                it["asset"] = None\n                continue\n            h, k =', '            h, k =')], ["TS-66"]),
    ("보호 등급(D3 이상)도 확인 없이 옮김", [('how = "건드리지 않음" if d is None else ("확인 뒤" if c["grade"] >= "D3" or c["conf"] == "중간" else "자동")', 'how = "건드리지 않음" if d is None else ("확인 뒤" if c["conf"] == "중간" else "자동")')], ["TS-70"]),
    ("옛 판으로 되돌아간 것도 뒤 판으로 이음(계보의 고리)", [("        if self._desc(parent, child):                     # 옛 판으로", "        if False:                                         # 옛 판으로")], ["TS-103"]),
    ("이름만 같은 다른 것의 최종본을 덮음", [("            if cur == h or row.get(\"force\") or any(kin(x, cur) for x in [h] + list(parents)):", "            if True:")], ["TS-105"]),
    ("복구할 때 다른 판을 본 것으로 적지 않음", [("            for key, items in sets_ or [((it[\"stem\"], it[\"ext\"], 0), [])]:", "            for key, items in [((it[\"stem\"], it[\"ext\"], 0), [])]:")], ["TS-106"]),
    ("사용자 규칙이 등급을 낮춤", [('        strict += [c["fresh"]["code"]] if c["fresh"] else []', '        strict = []')], ["TS-108"]),
    ("무료 층에서 판 고르기가 열림", [('        if self.tier != "구독":\n            self.led.add("SYN", "거절", actor="사용자", res="거절", rc="RC-01", why="무료 층")\n            return None', '        pass')], ["TS-104"]),
    ('K-X1 엇갈린 기기 파일도 거울로 보냄', [('            elif rel in unsettled and rel not in self.finals:\n                skipped.append((rel, "판이 엇갈림 — 정합 먼저"))\n', '')], ['TS-119']),
    ('K-X2 보호 등급도 자동 정합에 넣음', [('if max(grades) >= "D3":', 'if False:')], ['TS-119']),
    ('K-X3 자동 실행의 구독 문을 없앰', [('        if self.tier != "구독" or not self.auto:\n            return None', '        if not self.auto:\n            return None')], ['TS-119']),
    ('K-X4 대량 변경의 10건 바닥을 없앰', [('len(have) >= 10 and', 'len(have) >= 0 and')], ['TS-119']),
    ('K-X11 미러링 해시 대조를 하지 않음', [('if sha(open(tmp, "rb").read()) != want[r]:', 'if False:')], ['TS-119']),
    ('K-X12 거울에서 물러난 것을 보류함에 두지 않고 지움', [('shutil.move(os.path.join(mroot, r), hd)', 'os.remove(os.path.join(mroot, r))')], ['TS-119']),
    ('K-X8 계보를 거꾸로 적음(0.3부터 계보를 잇는 자리)', [('        self.anc.setdefault(child, set()).add(parent)', '        self.anc.setdefault(parent, set()).add(child)')], ['TS-103']),
    ('옛 판으로 덮어쓴 글자 문서를 뒤 판으로 이음', [('            return "확인"                                 # 글자 문서는 날짜를 믿지 않는다', '            return "잇기"                                 # 글자 문서는 날짜를 믿지 않는다')], ['TS-112']),
    ('글자가 아닌 것을 옛 날짜의 판으로 덮어써도 이음', [('        if it["ext"] not in TEXT or not it["size"] or not old_it["size"]:\n            return "확인" if older else "잇기"', '        if it["ext"] not in TEXT or not it["size"] or not old_it["size"]:\n            return "잇기"')], ['TS-113']),
    ('판 확인 제안을 내지 않음', [('                        if how == "확인":', '                        if False:')], ['TS-112']),
    ('번갈아 고친 문서를 계보의 바탕에서 합치지 않음', [('                        if not self._lineage_merge(uniq, hs, e, row):', '                        if True:')], ['TS-114']),
    ('같은 줄을 두 쪽이 고친 것을 글자 단위로 합치지 않음', [('                elif (i1, i2) == (k1, k2) and len(ra) == len(rb) == i2 - i1', '                elif False and (i1, i2) == (k1, k2) and len(ra) == len(rb) == i2 - i1')], ['TS-114']),
    ('두 쪽이 같은 자리에 더한 줄을 겹침으로 봄', [('                    both.append((i1, ra, rb))', '                    return None')], ['TS-114']),
    ('같은 줄을 다르게 고쳐도 합침(겹침 검사를 끔)', [('                elif max(i1, k1) < min(i2, k2) or (i1 == i2 and k1 < i1 < k2) or (k1 == k2 and i1 < k1 < i2):\n                    return None', '                elif False:\n                    return None')], ['TS-15']),
    ('첫날: 다 담은 판을 고친 시각을 보지 않고 자동', [('            if sup and all(mt[sup[0]] >= mt[o] for o in hs):', '            if sup:')], ['TS-101']),
    ('첫날: 모두가 담은 판을 바탕으로 합치지 않음', [('            if sub and len(hs) >= 3:', '            if False:')], ['TS-115']),
    ('이름·폴더만 같은 다른 그림을 판으로 묶음', [('        return bool(ia and ib and self._aid(ia) == self._aid(ib))', '        return True')], ['TS-17']),
    ('엔진이 만든 최종본의 시각도 고친 시각으로 셈', [('                if it_["hash"] in mt and not in_ref(r_):', '                if it_["hash"] in mt:')], ['TS-115']),
    ('보호 등급을 금고 대신 거울에 그대로 비춤', [('                    vault[rel] = it["hash"]                # 보호 등급', '                    want[rel] = it["hash"]                # 보호 등급')], ['TS-44']),
    ('금고를 잠그지 않고 그대로 씀', [('    ct = bytes(a ^ b for a, b in zip(pt, _ks(key, nonce, len(pt))))', '    ct = pt')], ['TS-117']),
    ('금고 칸의 확인값을 보지 않음', [('    if not hmac.compare_digest(tag, hmac.new(key, b"mac" + nonce + ct, hashlib.sha256).digest()):', '    if False:')], ['TS-117']),
    ('금고에 간 보호 등급을 화면에서 빼지 않음(늘 살핌 필요)', [('rel not in in_vault) if has_mirror else 0', 'True) if has_mirror else 0')], ['TS-108']),
    ('받아들인 범주를 배우지 않음', [('and plan[r]["code"] in self.learned))', 'and False))')], ['TS-116']),
    ('묶음 확인의 다섯 건 문턱을 없앰', [('(not asked_before or len(wait) >= 5)', 'True')], ['TS-116']),
    ('엔진이 옮긴 파일을 다시 묶음 확인에 넣음', [(' and norm(p["rel"]) not in self.placed]', ']')], ['TS-116']),
    ('원장 파일이 같은 크기로 바뀌면 모름', [('            full = full or bool(self.rows)', '            full = full')], ['TS-118']),
    ('원장 사슬이 끊긴 뒤 예외로 죽음', [('                if not outer or "원장 사슬 끊김" not in str(e):', '                if True:')], ['TS-118']),
    ('받는 쪽이 엔진이 아니어도 받으려 함(엔진 확인을 없앰)', [(' or not (led and hasattr(led, "verify") and led.verify() and isinstance(getattr(other, "anc", None), dict)):', ':')], ['TS-118']),
    ("받아들이기 전에 권한 역할을 바로 씀", [('        self._propose("매체 역할", "역할|" + m.dev_id,', '        m.role, m.scope = role, scope\n        self._propose("매체 역할", "역할|" + m.dev_id,')], ["TS-89"]),
]

# ===== 하 OP-2: 남은 넷 =====
G15 = "하 OP-2 남은 넷(0.4)"
# TS-111 글자가 아닌 것의 같은 자산 갈라짐은 묻는다(두 매체에서 같은 그림을 저마다 고침)
q1, q1a, q1b = mk("q1"), mk("q1a"), mk("q1b"); w(q1a, "그림/로고.png", PNG + b"0"); w(q1b, "그림/로고.png", PNG + b"0")
Q1 = new(q1, auto=False); Q1.plug(Medium("QA", q1a)); Q1.plug(Medium("QB", q1b)); Q1.reconcile()
w(q1a, "그림/로고.png", PNG + b"A"); w(q1b, "그림/로고.png", PNG + b"B"); rq1 = {r["stem"]: r for r in Q1.reconcile()}
ok("TS-111", G15, "글자가 아닌 것: 같은 자산을 두 매체에서 저마다 고치면 묻는다(이름만 같은 다른 그림은 묶지 않음 — TS-17)", "SY-07 · K-16",
   rq1.get("로고", {}).get("how") == "사용자가 고름", rq1.get("로고", {}).get("why"))
# TS-112 엔진이 본 적 없는 옛 판으로 덮어씀(글자): 뒤 판으로 잇지 않고 한 번 확인 · 최종본 그대로
q2, q2a = mk("q2"), mk("q2a"); V1_ = "제목\n1장\n2장\n3장\n4장\n5장\n"; w(q2a, "doc.txt", V1_); w(q2, "doc.txt", V1_)
Q2 = new(q2, auto=False); MA2 = Medium("A", q2a); Q2.plug(MA2); w(q2a, "doc.txt", V1_ + "6장\n"); Q2.reconcile(); f2a = rdx(q2, "기준자리/doc.txt")
Q2.unplug("A"); w(q2a, "doc.txt", "옛 백업에서 되살린 전혀 옛 판\n1장\n"); Q2.plug(MA2); Q2.reconcile(); pq2 = [p for p in Q2.proposals() if p["kind"] == "판 확인"]
ok("TS-112", G15, "엔진이 본 적 없는 옛 판으로 덮어쓴 글자 문서: 뒤 판으로 잇지 않고 한 번 확인, 최종본은 그대로", "K-03 ① · SY-03",
   f2a == (V1_ + "6장\n").encode() and rdx(q2, "기준자리/doc.txt") == f2a and len(pq2) == 1 and "SYN-E10" in codes(Q2), "확인 %d건 · 최종본 그대로" % len(pq2))
# TS-113 글자가 아닌 것을 옛 날짜의 판으로 덮어씀: 잇지 않고 확인
q3, q3a = mk("q3"), mk("q3a"); w(q3a, "사진/집.jpg", JPG_SHOT + b"v2", time.time()); Q3 = new(q3, auto=False); M3 = Medium("A", q3a); Q3.plug(M3); Q3.unplug("A")
w(q3a, "사진/집.jpg", JPG_SHOT + b"v1-old", time.time() - 86400 * 30); Q3.plug(M3); Q3.preview(); pq3 = [p for p in Q3.proposals() if p["kind"] == "판 확인"]
ok("TS-113", G15, "글자가 아닌 것을 더 옛 날짜의 판으로 덮어씀(옛 백업 되살림): 뒤 판으로 잇지 않고 확인", "K-03 ① · SY-03",
   len(pq3) == 1 and not Q3._desc(sha(JPG_SHOT + b"v1-old"), sha(JPG_SHOT + b"v2")), "확인 %d건" % len(pq3))
# TS-114 USB 둘을 번갈아 20번 고침(다른 USB의 판을 베껴 오지 않음): 묻는 비율
import random as _r
_r.seed(7); q4, q4a, q4b = mk("q4"), mk("q4a"), mk("q4b"); docs4 = ["보고서.txt", "회의록.md", "예산.csv", "일정.txt", "메모.md"]
body4 = {d_: ["%s %d줄" % (d_, i) for i in range(12)] for d_ in docs4}
for d_ in docs4:
    for x_ in (q4a, q4b): w(x_, "업무/" + d_, "\n".join(body4[d_]) + "\n")
Q4 = new(q4, auto=True); Q4.plug(Medium("A", q4a)); Q4.plug(Medium("B", q4b)); cur4 = {(m_, d_): list(body4[d_]) for m_ in "AB" for d_ in docs4}; asked4 = 0
for st_ in range(20):
    m_ = "AB"[st_ % 2]; d_ = docs4[st_ % 5]; L_ = cur4[(m_, d_)]; L_[_r.randrange(len(L_))] += " 고침%d" % st_; L_.append("더함%d" % st_)
    w(q4a if m_ == "A" else q4b, "업무/" + d_, "\n".join(L_) + "\n"); la4 = Q4.auto_run("바뀌면"); asked4 += 1 if la4["waiting"] else 0
fin4 = {d_: rdx(q4, "기준자리/업무/" + d_).decode() for d_ in docs4}
keep4 = all(("고침%d" % st_) in fin4[docs4[st_ % 5]] and ("더함%d" % st_) in fin4[docs4[st_ % 5]] for st_ in range(20))   # 스무 번의 고침이 모두 최종본에(같은 줄을 두 쪽이 고친 것은 글자 단위로 함께)
MEASURE_ALT = dict(runs=20, asked=asked4, ratio=asked4 / 20)
ok("TS-114", G15, "흔한 쓰임 ①: USB 둘을 번갈아 20번 고침 — 묻는 비율 10% 아래, 두 쪽의 고친 줄이 모두 최종본에", "K-09 ① · 기-1 · 끝난 기준 ③",
   asked4 / 20 < 0.10 and keep4 and Q4.dashboard()["3_보호상태"]["state"] == "정상", "물은 자동 실행 %d / 20 · 두 쪽 줄 모두 담김 %s" % (asked4, keep4))
# TS-115 첫날 매체 넷(문서 판 10 · 카메라 번호 사진 100쌍 · 운영체제 파일 · 같은 이름 메모 · 증명사진 · 졸업여행 사진): 묻는 비율
JPGn = lambda i: b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00" + (b"photo%05d" % i) * 30
q5 = mk("q5"); M5 = [mk("q5m%d" % i) for i in range(4)]; base5 = ["사업계획서", "1. 개요", "2. 시장", "3. 제품", "4. 일정", "5. 예산", "6. 맺음"]
for i in range(10):
    nm = "문서/계획%02d.txt" % i; b0 = [x_ + " %d" % i for x_ in base5]
    w(q5, nm, "\n".join(b0) + "\n"); w(M5[0], nm, "\n".join(b0 + ["7. 더함"]) + "\n")
    w(M5[1], nm.replace(".txt", "_최종.txt"), "\n".join(b0[:3] + ["3-1. 끼움"] + b0[3:]) + "\n" if i % 2 else "\n".join(b0 + ["7. 더함", "8. 또 더함"]) + "\n")
for i in range(1, 101): w(M5[2], "DCIM/100CANON/IMG_%04d.JPG" % i, JPGn(i)); w(M5[3], "DCIM/100CANON/IMG_%04d.JPG" % i, JPGn(1000 + i))
for i, x_ in enumerate(M5):
    w(x_, "desktop.ini", "[.ShellClassInfo]\nIconIndex=%d\n" % i); w(x_, "Thumbs.db", b"\xd0\xcf\x11\xe0" + bytes([i]) * 50); w(x_, ".DS_Store", b"\x00\x00\x00\x01Bud1" + bytes([i]) * 40)
    w(x_, "메모.txt", "매체 %d에 적어 둔 서로 다른 메모\n내용 %d\n" % (i, i)); w(x_, "사진/증명사진.jpg", JPGn(5000 + i)); w(x_, "받은 파일/주민센터 안내문.pdf", b"%PDF-1.4 " + bytes([65 + i]) * 30); w(x_, "여행/졸업여행 단체.jpg", JPGn(7000 + i))
before5 = {x_: snap(x_) for x_ in M5}
Q5 = new(q5, auto=True); [Q5.plug(Medium("M%d" % i, x_)) for i, x_ in enumerate(M5)]; rows5 = Q5.reconcile()
ask5 = sum(1 for r_ in rows5 if r_["how"] in ("확인 필요", "사용자가 고름", "자동에서 뺌")); files5 = sum(len(m_.index) for m_ in Q5.media.values())
merged_odd = all(("3-1. 끼움" in rdx(q5, "기준자리/문서/계획%02d.txt" % i).decode() and "7. 더함" in rdx(q5, "기준자리/문서/계획%02d.txt" % i).decode()) for i in (1, 3, 5, 7, 9))
MEASURE_DAY1 = dict(groups=len(rows5), asked=ask5, files=files5, ratio=(ask5 / len(rows5)) if rows5 else 0.0)
ok("TS-115", G15, "흔한 쓰임 ②: 첫날 매체 넷 — 판 묶음 가운데 묻는 비율 10% 아래(이름만 같은 다른 사진·메모·시스템 파일은 묶지 않음), 매체는 그대로", "K-09 ③ · 기-1 · 끝난 기준 ③",
   rows5 and ask5 / len(rows5) < 0.10 and merged_odd and all(snap(x_) == before5[x_] for x_ in M5), "판 묶음 %d · 물음 %d · 매체 파일 %d" % (len(rows5), ask5, files5))
# TS-116 확신 「중간」의 새 문서마다 묶음 확인이 생기지 않음: 한 번 받아들인 범주는 스스로, 다른 범주는 다섯 건이 쌓일 때 한 번
q6 = mk("q6"); w(q6, "바탕화면/a.docx", b"a"); Q6 = new(q6, auto=True, mode="시스템"); Q6.auto_run("바뀌면")
pb = [p for p in Q6.proposals() if p["kind"] == "자리 묶음"]; Q6.accept(pb[0]["no"]) if pb else None; n6 = len(Q6.props)
for i in range(10): w(q6, "바탕화면/새문서%d.docx" % i, b"d%d" % i); Q6.auto_run("바뀌면")
moved6 = sum(1 for x_ in snap(q6) if x_.replace(os.sep, "/").startswith("08_자료실/08_01_문서") and "새문서" in x_)
for i in range(4): w(q6, "바탕화면/곡%d.mp3" % i, b"ID3" + bytes([i]) * 20); Q6.auto_run("바뀌면")
n6b = len(Q6.props); w(q6, "바탕화면/곡9.mp3", b"ID3" + b"9" * 20); Q6.auto_run("바뀌면"); n6c = len(Q6.props)
ok("TS-116", G15, "확신 「중간」의 새 문서: 받아들인 범주는 묻지 않고 자리가 붙음, 다른 범주는 다섯 건이 쌓였을 때 묶음 한 번", "AP-05 · CP-06 · GO-3 · K-09 · 항목 4",
   len(pb) == 1 and n6 == len(Q6.props) - (n6c - n6b) and moved6 == 10 and n6b == n6 and n6c == n6 + 1, "첫 묶음 %d → 새 문서 10건 자리 붙음 %d · 다른 범주 4건 물음 %d · 다섯째에 묶음 %d" % (len(pb), moved6, n6b - n6, n6c - n6b))
# TS-117 금고 거울: 열쇠가 없으면 멈추고 원장에 남김 · 금고 칸을 손으로 바꾸면 열지 않음
q7, q7m = mk("q7"), mk("q7m"); w(q7, "개인/여권사본.pdf", b"%PDF-1.4 secret"); Q7 = new(q7, auto=False); Q7.plug(Medium("V", q7m, role="거울")); Q7.confirm_first("V"); rv7 = Q7.mirror("V")
cells = os.listdir(os.path.join(q7m, "_HiDAM_금고")) if ex(q7m, "_HiDAM_금고") else []
cp7 = os.path.join(q7m, "_HiDAM_금고", cells[0]) if cells else None; raw7 = open(cp7, "rb").read() if cp7 else b"secret"
if cp7: open(cp7, "wb").write(raw7[:-1] + bytes([raw7[-1] ^ 1]))
ok("TS-117", G15, "금고 거울: 잠가서 비춤(원장 SYN-E11), 금고 칸이 바뀌면 열지 않음, 화면에 금고 건수", "TG-04 · K-10 · ST-01",
   rv7["vault"] == 1 and "SYN-E11" in codes(Q7) and b"secret" not in raw7 and Q7.vault_restore("V", "개인/여권사본.pdf") is None and Q7.dashboard()["5_금고"]["count"] == 1, "금고 %d · 바뀐 칸은 열지 않음" % rv7["vault"])

# TS-118 원장 사슬이 끊긴 뒤에도 죽지 않음 · 엔진이 아닌 것에서 계보를 받으려 해도 죽지 않음
q8 = mk("q8"); w(q8, "a.txt", "x\n"); Q8 = new(q8, auto=False); Q8.preview(); lk8 = os.path.join(q8, "_HiDAM", "00.02_원장.jsonl"); raw8 = open(lk8, encoding="utf-8").read()
open(lk8, "w", encoding="utf-8", newline="\n").write(raw8.replace('"엔진"', '"지원"', 1))
try: rp8 = Q8.plug(Medium("Z8", mk("q8z"))); c8 = None
except Exception as e_: rp8, c8 = None, repr(e_)
class _NotEngine: anc = {"a": {"b"}}
try: il8 = new(mk("q8b"), auto=False).import_lineage(_NotEngine); c8b = None
except Exception as e_: il8, c8b = None, repr(e_)
ok("TS-118", G15, "원장 사슬이 끊긴 뒤의 걸음은 죽지 않고 「멈춤」을 돌려주고 새 사슬을 한 번 묻는다 · 엔진이 아닌 것에서 계보를 받으려 하면 거절", "K-02 · K-31 · K-05",
   c8 is None and isinstance(rp8, dict) and "원장 사슬 끊김" in str(rp8.get("stopped")) and [p for p in Q8.proposals() if p["kind"] == "원장 새 사슬"] and c8b is None and il8 is False, (rp8, c8, il8, c8b))
# TS-119 거울·자동 실행의 문(검수 K t12에서 0.2 시나리오가 놓친 변이를 잡는다)
import hidam_app as _HA
q9, q9a, q9b, q9m = mk("q9"), mk("q9a"), mk("q9b"), mk("q9m")
for x_ in (q9a, q9b): w(x_, "개인/여권사본.txt", "여권 사본 메모\n번호 칸\n발급일\n")
Q9 = new(q9, auto=False); Q9.plug(Medium("A", q9a)); Q9.plug(Medium("B", q9b)); Q9.reconcile(); w(q9a, "개인/여권사본.txt", "여권 사본 메모\n번호 칸\n발급일\n만료일\n")
r9p = {r_["stem"]: r_ for r_ in Q9.reconcile()}.get("여권사본", {})
F9 = new(mk("q9f"), tier="무료", auto=True)
try: fa9 = F9.auto_run("바뀌면")
except Exception as e_: fa9 = repr(e_)
w(q9, "갈래.txt", "하나\n둘\n셋\n넷\n"); w(q9a, "갈래.txt", "하나\n둘\n셋\n넷\n"); Q9.reconcile(); w(q9, "갈래.txt", "하나\n둘 기기\n셋\n넷\n"); w(q9a, "갈래.txt", "하나\n둘 매체\n셋\n넷\n")
for i in range(4): w(q9, "작은/n%d.txt" % i, "n%d\n" % i)
Q9.plug(Medium("M", q9m, role="거울")); Q9.confirm_first("M"); Q9.mirror("M")
for i in range(3): w(q9, "작은/n%d.txt" % i, "바뀜 %d\n" % i)
r9m = Q9.mirror("M", auto=True)
real9 = _HA.shutil.copy2
def bad9(src, dst, *a_, **k_):
    open(dst, "wb").write(b"broken")
_HA.shutil.copy2 = bad9; w(q9, "작은/n3.txt", "또 바뀜\n")
try: r9h = Q9.mirror("M")
finally: _HA.shutil.copy2 = real9
kept9 = rd(q9m, "_HiDAM_거울/작은/n3.txt")
os.remove(os.path.join(q9, "작은/n0.txt")); r9d = Q9.mirror("M")
ok("TS-119", G15, "보호 등급의 판은 자동으로 맞추지 않음 · 무료는 자동 실행이 닫힘 · 거울이 10건이 안 되면 대량 변경으로 멈추지 않음 · 미러링은 해시를 맞대어 틀린 사본을 들이지 않음 · 물러난 것은 보류함에", "SV-03 · FN-17 · MR-16 · MR-03 · MR-05",
   r9p.get("how") == "자동에서 뺌" and fa9 is None and r9m["stopped"] is None and r9m["done"] == 3 and r9h["mismatch"] == 1 and kept9 == b"n3\n"
   and r9d["held"] == 1 and ex(q9m, "_HiDAM_보류함/작은/n0.txt") and rd(q9m, "_HiDAM_보류함/작은/n0.txt") == "바뀜 0\n".encode() and not ex(q9m, "_HiDAM_거울/갈래.txt"), (r9p.get("how"), fa9, r9m.get("stopped"), r9h.get("mismatch"), kept9, r9d.get("held")))
mut_table = []
if "--no-mutants" not in sys.argv:
    src = open(os.path.join(here, "hidam_app.py"), encoding="utf-8").read()
    for i, (name, pairs, want) in enumerate(MUTANTS, 1):
        if any(src.count(a) != 1 for a, _ in pairs):
            mut_table.append(dict(no=i, what=name, expect=want, failed=[], verdict="바꿀 줄을 찾지 못함")); continue
        msrc = src
        for a, b in pairs: msrc = msrc.replace(a, b)
        md = tempfile.mkdtemp(prefix="hidam_mut_"); open(os.path.join(md, "hidam_app.py"), "w", encoding="utf-8").write(msrc)
        outp = os.path.join(md, "r.json")
        pr_ = subprocess.run([sys.executable, os.path.abspath(__file__), outp, "--no-mutants"], env=dict(os.environ, HIDAM_ENGINE_DIR=md, PYTHONIOENCODING="utf-8"), capture_output=True, text=True, encoding="utf-8", errors="replace")
        try: failed = [c["no"] for c in json.load(open(outp, encoding="utf-8"))["cases"] if c["result"] != "통과"]; crashed = None
        except Exception: failed, crashed = [], (pr_.stderr or "").strip().split("\n")[-1][:120]
        hit = all(x in failed for x in want)
        mut_table.append(dict(no=i, what=name, expect=want, failed=failed, verdict=("잡음(시나리오가 멈춤: " + crashed + ")") if crashed else ("잡음" if hit else "못 잡음")))
        shutil.rmtree(md, ignore_errors=True)
    caught = sum(1 for m in mut_table if m["verdict"].startswith("잡음"))
    ok("TS-110", G13, "통과 조건이 「늘 참」이 아닌지: 엔진의 한 줄을 틀리게 바꾼 사본 %d가지에서 해당 시나리오가 실패하는가" % len(MUTANTS), "시험의 시험 · 검수 A (다)", caught == len(MUTANTS),
       "%d/%d 잡음 · %s" % (caught, len(MUTANTS), [(m["no"], m["verdict"]) for m in mut_table if not m["verdict"].startswith("잡음")]))
out = dict(title="HiDAM.app 기준 구현 시뮬레이션", note="만든 파일로 돌린 시뮬레이션이며 실측이 아니다", policy=POLICY, app=APP_VER,
           code_sha256=sha(open(os.path.join(ENGINE_DIR, "hidam_app.py"), "rb").read()), scenario_sha256=sha(open(os.path.abspath(__file__), "rb").read()),
           ran_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), env="Python %s · %s" % (sys.version.split()[0], sys.platform), total=len(R), passed=sum(1 for r in R if r["result"] == "통과"),
           groups=[G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, G11, G12, G13, G14], cases=R, measures=MEASURES, always_true_check=mut_table, dashboard_sample=d, ledger_tail=Z.led.rows[-5:])
json.dump(out, open(ARGS[0] if ARGS else os.path.join(here, "sim_hidam_app_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in R:
    if r["result"] != "통과" or "-v" in sys.argv: print(r["no"], r["result"], r["title"], "|", r["seen"][:150])
print("합계", out["passed"], "/", out["total"])
shutil.rmtree(T, ignore_errors=True)
