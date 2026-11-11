# -*- coding: utf-8 -*-
"""검수 K의 높음 15건(K-01~K-15)을 K가 적은 「기대」 그대로 판정한다. K의 재현 스크립트(t1~t11)의 입력을 따르고,
결과를 글로 보지 않고 값으로 맞댄다. 엔진 폴더는 HIDAM_APP으로 준다. 대상 폴더에는 쓰지 않는다(임시 폴더만)."""
import os, sys, json, shutil, tempfile, time, random
sys.dont_write_bytecode = True
sys.path.insert(0, os.environ.get("HIDAM_APP", "/home/claude/op2/eng04"))
import hidam_app as H
from hidam_app import HiDAMApp, Medium, sha
T = tempfile.mkdtemp(prefix="kj_")
def mk(n):
    p = os.path.join(T, n); os.makedirs(p, exist_ok=True); return p
def w(root, rel, data, mtime=None):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(data if isinstance(data, bytes) else data.encode("utf-8"))
    if mtime: os.utime(p, (mtime, mtime))
def rd(root, rel):
    p = os.path.join(root, rel or "\0없음")
    return open(p, "rb").read() if rel and os.path.exists(p) else None
def tree(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f); out[os.path.relpath(p, root)] = sha(open(p, "rb").read())
    return out
def recd(app):
    r = app.reconcile()
    return {(x["stem"], x["ext"]): x for x in r} if isinstance(r, list) else {}
OUT = []
def J(no, title, expect, cond, seen):
    OUT.append(dict(k=no, title=title, expect=expect, result="통과" if cond else "남음", seen=str(seen)[:300]))
def run(no, title, expect, fn):
    try:
        cond, seen = fn()
    except Exception as e:
        cond, seen = False, "예외: " + repr(e)
    J(no, title, expect, cond, seen)
V1 = "제목\n1장\n2장\n3장\n4장\n5장\n"; V2 = V1 + "6장\n"

def k01():
    root, A = mk("k01"), mk("k01a"); w(A, "doc.txt", V1); w(root, "doc.txt", V1)
    a = HiDAMApp(root, auto=False); a.plug(Medium("A", A)); w(A, "doc.txt", V2); r0 = recd(a)[("doc", "txt")]
    w(A, "doc.txt", V2 + "7장\n")
    b = HiDAMApp(root, auto=False); b.plug(Medium("A", A)); r1 = recd(b)[("doc", "txt")]
    f = mk("k01f"); w(f, "a.txt", "x\n"); fa = HiDAMApp(f, tier="무료", auto=False)
    fa._keep_version("a.txt"); w(f, "a.txt", "y\n"); fa._keep_version("a.txt"); w(f, "a.txt", "z\n")
    used = [fa.recover("a.txt", 1)["ok"] for _ in range(2)]
    fb = HiDAMApp(f, tier="무료", auto=False); third = fb.recover("a.txt", 1)["ok"]
    ok = r0["how"] == "자동" and r1["judge"] == "SY-최신" and r1["how"] == "자동" and len(b.anc) > 0 and b.finals and used == [True, True] and third is False
    return ok, "재시작 뒤 %s/%s · 계보 %d · 최종본 기억 %d · 무료 복구 %s → 다시 띄운 뒤 셋째 %s" % (r1["judge"], r1["how"], len(b.anc), len(b.finals), used, third)

def k02():
    root = mk("k02"); w(root, "a.txt", "x\n"); e1 = HiDAMApp(root); e2 = HiDAMApp(root); e1.preview(); e2.preview(); e1.preview(); e2.plug(Medium("Z", mk("k02z")))
    rows = [json.loads(x) for x in open(e1.led.path, encoding="utf-8")]
    prev, okc = "0" * 64, True
    for x in rows:
        okc &= x["prev"] == prev; prev = x["h"]
    eids = [x["eid"] for x in rows]
    e3 = HiDAMApp(root); lines = open(e3.led.path, encoding="utf-8").read().split("\n"); r0 = json.loads(lines[0]); r0["act"] = "고침"; lines[0] = json.dumps(r0, ensure_ascii=False)
    open(e3.led.path, "w", encoding="utf-8").write("\n".join(lines))
    try:
        res = e3.plug(Medium("Y", mk("k02y"))); crashed = False
    except Exception as e:
        res, crashed = repr(e), True
    d = e3.dashboard()
    ok = okc and len(eids) == len(set(eids)) and not crashed and d["6_기록"]["chain_ok"] is False and d["3_보호상태"]["state"] == "위험"
    return ok, "엔진 둘: 줄 %d 사슬 %s 겹친 식별자 %d · 첫 줄을 고친 뒤 꽂기 → %s(예외 %s) · 화면 사슬 %s · %s" % (len(rows), okc, len(eids) - len(set(eids)), res, crashed, d["6_기록"]["chain_ok"], d["3_보호상태"]["state"])

def k03():
    app = HiDAMApp(mk("k03"), auto=False); A = mk("k03a"); w(A, "doc.txt", V1); mA = Medium("A", A); app.plug(mA); w(app.dev.root, "doc.txt", V1)
    w(A, "doc.txt", V2); recd(app); app.unplug("A"); w(A, "doc.txt", "옛 백업에서 되살린 전혀 옛 판\n1장\n"); app.plug(mA); recd(app)
    fin1 = rd(app.dev.root, "기준자리/doc.txt"); asked = [p for p in app.proposals() if p["kind"] == "판 확인"]
    b = HiDAMApp(mk("k03b"), auto=False); X = "작년 여행 계획\n제주\n3박\n렌터카\n"; Y = "올해 예산 메모\n식비\n교통\n통신\n"; P, Q = mk("k03p"), mk("k03q")
    w(P, "메모.txt", X); w(Q, "메모.txt", X); b.plug(Medium("A", P)); b.plug(Medium("B", Q)); os.remove(os.path.join(P, "메모.txt")); w(P, "메모.txt", Y)
    r = recd(b).get(("메모", "txt")); fin2 = rd(b.dev.root, r["final"]) if r and r.get("final") else None
    ok = fin1 == V2.encode() and len(asked) == 1 and fin2 != Y.encode() and (r is None or r["how"] != "자동" or fin2 == X.encode())
    return ok, "① 최종본 그대로 %s · 확인 %d건 ② 다시 만든 다른 글 → %s" % (fin1 == V2.encode(), len(asked), (r or {}).get("how", "묶지 않음(다른 자산)"))

def k04():
    res = []
    for order in ("AB", "BA"):
        app = HiDAMApp(mk("k04" + order), auto=False); A, B = mk("k04a" + order), mk("k04b" + order); w(A, "doc.txt", V1); w(B, "doc.txt", V1)
        for x in order: app.plug(Medium(x, A if x == "A" else B))
        w(A, "doc.txt", V2); w(B, "doc.txt", V2); recd(app); w(A, "doc.txt", V1); r = recd(app)[("doc", "txt")]
        cyc = app._desc(sha(V1.encode()), sha(V2.encode())) and app._desc(sha(V2.encode()), sha(V1.encode()))
        res.append((rd(app.dev.root, r["final"]) if r.get("final") else None, r["how"], cyc))
    return res[0][0] == res[1][0] and not res[0][2] and not res[1][2], "꽂는 순서 AB/BA 최종본 같음 %s · 고리 %s" % (res[0][0] == res[1][0], (res[0][2], res[1][2]))

def k05():
    app = HiDAMApp(mk("k05"), auto=False); A, B = mk("k05a"), mk("k05b"); w(A, "doc.txt", V1); w(B, "doc.txt", V1); app.plug(Medium("A", A)); app.plug(Medium("B", B))
    w(A, "doc.txt", V2); recd(app)                                   # 이 기기는 v1 → v2를 안다
    o = HiDAMApp(mk("k05o"), device_id="DEV-PC-02", auto=False); o.anc = {sha(V1.encode()): {sha(V2.encode())}}
    n = len(app.led.rows); app.import_lineage(o); r = recd(app)[("doc", "txt")]
    logged = [x["code"] for x in app.led.rows[n:] if x["code"] in ("LNK-E04", "LNK-E05")]
    class Fake: anc = {sha(V1.encode()): {sha(V2.encode())}}
    fake = app.import_lineage(Fake)
    fr = HiDAMApp(mk("k05f"), tier="무료", auto=False); fr.import_lineage(o)
    ok = rd(app.dev.root, r["final"]) == V2.encode() and "LNK-E05" in logged and fake is not True and not fr.anc
    return ok, "거꾸로 받은 계보 → 최종본 v2 %s · 원장 %s · 엔진이 아닌 것 → %s · 무료 → 닫힘 %s" % (rd(app.dev.root, r["final"]) == V2.encode(), logged, fake, not fr.anc)

def k06():
    app = HiDAMApp(mk("k06"), auto=False); A, B = mk("k06a"), mk("k06b"); w(A, "메모.txt", "가 메모\n하나\n둘\n"); w(B, "메모.txt", "나 메모\n셋\n넷\n")
    w(app.dev.root, "메모.txt", "가 메모\n하나\n둘\n"); app.plug(Medium("A", A)); app.plug(Medium("B", B)); recd(app)
    w(A, "메모.txt", "가 메모\n하나\n둘\n가 고침\n"); recd(app); w(B, "메모.txt", "나 메모\n셋\n넷\n나 고침\n"); recd(app)
    finals = {k: rd(app.dev.root, k) for k in app.finals}
    hasA = any(v and v.startswith("가 메모".encode()) and "가 고침".encode() in v for v in finals.values())
    clobber = any(v and "가".encode() in v[:3] and "나 고침".encode() in v for v in finals.values())
    return hasA and not clobber, "최종본 %s · 가 메모 지켜짐 %s · 덮임 %s" % (sorted(finals), hasA, clobber)

def k07():
    app = HiDAMApp(mk("k07"), auto=False); A, B = mk("k07a"), mk("k07b")
    for x in (A, B): w(x, "가/목록.txt", "하나\n둘\n셋\n"); w(x, "나/목록.txt", "빨강\n주황\n노랑\n초록\n파랑\n보라\n")
    app.plug(Medium("A", A)); app.plug(Medium("B", B)); recd(app)
    w(A, "가/목록.txt", "하나\n둘\n셋\n넷\n"); w(A, "나/목록.txt", "빨강 A\n주황\n노랑\n초록\n파랑\n보라\n"); w(B, "나/목록.txt", "빨강\n주황\n노랑\n초록\n파랑\n보라 B\n"); recd(app)
    g, n = rd(app.dev.root, "기준자리/가/목록.txt"), rd(app.dev.root, "기준자리/나/목록.txt")
    return g == "하나\n둘\n셋\n넷\n".encode() and n == "빨강 A\n주황\n노랑\n초록\n파랑\n보라 B\n".encode(), "가 %s · 나 %s" % (g, n)

def k08():
    app = HiDAMApp(mk("k08"), auto=True); A, B = mk("k08a"), mk("k08b"); c = lambda n: "".join("%d장\n" % i for i in range(1, n + 1))
    w(app.dev.root, "책.txt", c(3)); w(A, "책.txt", c(3)); w(B, "책.txt", c(3)); app.plug(Medium("A", A)); app.plug(Medium("B", B))
    w(A, "책.txt", c(4)); app.auto_run("바뀌면"); w(B, "책.txt", c(5)); app.auto_run("바뀌면")
    fr = [k for k in app.finals if k.endswith("책.txt")][0]; vs = app.versions(fr); v4 = next((v["ver"] for v in vs if v.get("hash") == sha(c(4).encode())), None)
    rv = app.recover(fr, v4) if v4 else {"ok": False}; app.auto_run("바뀌면")
    return rv.get("ok") and rd(app.dev.root, fr) == c(4).encode(), "복구 %s → 자동 실행 뒤 %s" % (rv.get("ok"), (rd(app.dev.root, fr) or b"").count(b"\n"))

def k09():
    random.seed(7); app = HiDAMApp(mk("k09"), auto=True); A, B = mk("k09a"), mk("k09b"); docs = ["보고서.txt", "회의록.md", "예산.csv", "일정.txt", "메모.md"]
    body = {d: ["%s %d줄" % (d, i) for i in range(12)] for d in docs}
    for d in docs:
        for x in (A, B): w(x, "업무/" + d, "\n".join(body[d]) + "\n")
    app.plug(Medium("A", A)); app.plug(Medium("B", B)); cur = {(m, d): list(body[d]) for m in "AB" for d in docs}; asked = 0; seen_p = set(app.pkeys)
    for st in range(20):
        m = "AB"[st % 2]; d = docs[st % 5]; L = cur[(m, d)]; L[random.randrange(len(L))] += " 고침%d" % st; L.append("더함%d" % st)
        w(A if m == "A" else B, "업무/" + d, "\n".join(L) + "\n"); la = app.auto_run("바뀌면")
        newp = [k for k in app.pkeys if k not in seen_p and k.startswith("판|")]; seen_p |= set(app.pkeys); asked += 1 if (newp or la["waiting"]) else 0
    u1 = asked / 20
    JPGn = lambda i: b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00" + (b"photo%05d" % i) * 30
    app2 = HiDAMApp(mk("k09u2"), auto=True); M = [mk("k09m%d" % i) for i in range(4)]; pc = app2.dev.root
    base = ["사업계획서", "1. 개요", "2. 시장", "3. 제품", "4. 일정", "5. 예산", "6. 맺음"]
    for i in range(10):
        nm = "문서/계획%02d.txt" % i; b0 = [x + " %d" % i for x in base]
        w(pc, nm, "\n".join(b0) + "\n"); w(M[0], nm, "\n".join(b0 + ["7. 더함"]) + "\n")
        w(M[1], nm.replace(".txt", "_최종.txt"), "\n".join(b0[:3] + ["3-1. 끼움"] + b0[3:]) + "\n" if i % 2 else "\n".join(b0 + ["7. 더함", "8. 또 더함"]) + "\n")
    for i in range(1, 101): w(M[2], "DCIM/100CANON/IMG_%04d.JPG" % i, JPGn(i)); w(M[3], "DCIM/100CANON/IMG_%04d.JPG" % i, JPGn(1000 + i))
    for i, m in enumerate(M):
        w(m, "desktop.ini", "[.ShellClassInfo]\nIconIndex=%d\n" % i); w(m, "Thumbs.db", b"\xd0\xcf\x11\xe0" + bytes([i]) * 50); w(m, ".DS_Store", b"\x00\x00\x00\x01Bud1" + bytes([i]) * 40)
        w(m, "메모.txt", "매체 %d에 적어 둔 서로 다른 메모\n내용 %d\n" % (i, i)); w(m, "사진/증명사진.jpg", JPGn(5000 + i))
        w(m, "받은 파일/주민센터 안내문.pdf", b"%PDF-1.4 " + bytes([65 + i]) * 30); w(m, "여행/졸업여행 단체.jpg", JPGn(7000 + i))
    for i, m in enumerate(M): app2.plug(Medium("M%d" % i, m))
    rows = app2.reconcile(); ask2 = sum(1 for r in rows if r["how"] in ("확인 필요", "사용자가 고름", "자동에서 뺌"))
    u2 = ask2 / max(len(rows), 1)
    return u1 < 0.10 and u2 < 0.10, "① 번갈아 20번: 물은 걸음 %d / 20 = %.0f%% · ③ 첫날 매체 넷: 판 묶음 %d 가운데 물음 %d = %.0f%%" % (asked, u1 * 100, len(rows), ask2, u2 * 100)

def k10():
    app = HiDAMApp(mk("k10"), auto=False); pc = app.dev.root; M = mk("k10m")
    w(pc, "DCIM/Camera/IMG_1.jpg", b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00" + b"p" * 50); w(pc, "서류/졸업증명서.pdf", b"%PDF-1.4 g"); w(pc, "일반.txt", "보통\n")
    app.plug(Medium("MIR", M, role="거울")); app.confirm_first("MIR"); r = app.mirror("MIR"); d = app.dashboard()
    plain = os.path.join(M, "_HiDAM_거울"); leaked = any(f.endswith(("IMG_1.jpg", "졸업증명서.pdf")) for _, _, fs in os.walk(plain) for f in fs)
    back = app.vault_restore("MIR", "서류/졸업증명서.pdf") == rd(pc, "서류/졸업증명서.pdf") and app.vault_restore("MIR", "DCIM/Camera/IMG_1.jpg") == rd(pc, "DCIM/Camera/IMG_1.jpg")
    # 금고가 서지 못하면(열쇠를 만들 수 없음) 「정상」이라 하지 않는다
    app2 = HiDAMApp(mk("k10b"), auto=False); w(app2.dev.root, "서류/졸업증명서.pdf", b"%PDF-1.4 h"); M2 = mk("k10m2"); app2.plug(Medium("MIR", M2, role="거울")); app2.confirm_first("MIR")
    app2._vault_key = lambda: None; app2.mirror("MIR"); d2 = app2.dashboard()
    ok = r.get("vault") == 2 and not leaked and back and d["5_금고"]["count"] == 2 and d["4_거울상태"]["protected_waiting"] == 0 and d2["3_보호상태"]["state"] != "정상" and d2["4_거울상태"]["protected_waiting"] == 1
    return ok, "금고 %s칸 · 그대로 비친 보호 자산 %s · 열면 같음 %s · 금고가 못 선 때 화면 %s(남은 %d)" % (r.get("vault"), leaked, back, d2["3_보호상태"]["state"], d2["4_거울상태"]["protected_waiting"])

def k11():
    f = HiDAMApp(mk("k11"), tier="무료", auto=False); A = mk("k11a"); w(A, "계획.txt", "a\n"); w(f.dev.root, "계획.txt", "a\nb\n"); f.plug(Medium("A", A))
    ch = f.choose("계획", "txt", "A"); f.set_role("A", "보관", "08"); f.set_mode("프로젝트"); o = HiDAMApp(mk("k11o"), device_id="DEV-PC-02"); o.anc = {"x": {"y"}}; f.import_lineage(o)
    ok = f.mode == "일반" and ch is None and not os.path.exists(os.path.join(f.dev.root, "기준자리")) and f.media["A"].role == "작업" and not f.anc
    return ok, "모드 %s · 고르기 %s · 역할 %s · 계보 받기 %s" % (f.mode, ch, f.media["A"].role, "열림" if f.anc else "닫힘")

def k12():
    import builtins
    app = HiDAMApp(mk("k12"), auto=False); M = mk("k12m"); w(app.dev.root, "a.txt", "a\n"); w(app.dev.root, "b.txt", "b\n"); app.plug(Medium("M", M, role="거울")); app.confirm_first("M")
    real = H.shutil.copy2; n = [0]
    def full(src, dst, *a, **k):
        n[0] += 1
        if n[0] >= 2: raise OSError(28, "No space left on device")
        return real(src, dst, *a, **k)
    H.shutil.copy2 = full
    try:
        r1 = app.mirror("M"); crash = None
    except Exception as e:
        r1, crash = None, repr(e)
    H.shutil.copy2 = real
    r2 = app.mirror("M"); tmp = [f for _, _, fs in os.walk(M) for f in fs if f.endswith(".hidam_tmp")]
    ok = crash is None and r1 and str(r1.get("stopped", "")).startswith("매체에 쓰지 못함") and r2["stopped"] is None and r2["done"] >= 1 and not tmp
    return ok, "가득 참 → %s · 다음 미러링 %s건 · 임시 파일 %d" % ((r1 or {}).get("stopped", crash), r2["done"], len(tmp))

def k13():
    app = HiDAMApp(mk("k13"), auto=False); A = mk("k13a"); w(A, "정상.txt", "ok\n")
    try: os.symlink(os.path.join(A, "없는곳"), os.path.join(A, "깨진.txt")); ln = True
    except OSError: ln = False
    w(A, "못읽음.txt", "x\n"); os.chmod(os.path.join(A, "못읽음.txt"), 0)
    try:
        r = app.plug(Medium("A", A)); crash = None
    except Exception as e:
        r, crash = None, repr(e)
    os.chmod(os.path.join(A, "못읽음.txt"), 0o644)
    m = app.media.get("A")
    return crash is None and r == "정상" and m and "정상.txt" in m.index, "꽂음 %s · 보지 못함 %s · 링크 %s" % (r or crash, m.unseen if m else None, ln)

def k14():
    app = HiDAMApp(mk("k14"), auto=False); A = mk("k14a"); w(A, "정상.txt", "ok\n"); w(A, "보고서.pdf.exe", b"MZ" + b"x" * 80); w(A, "_HiDAM_x/숨긴.pdf.exe", b"MZ" + b"y" * 80)
    r = app.plug(Medium("A", A)); pr = [p for p in app.proposals() if p["kind"] == "위험 매체"]; a = app.accept(pr[0]["no"]) if pr else {}
    m = app.media["A"]; w(A, "뒤에.pdf.exe", b"MZ" + b"z" * 80); app.rescan()
    return r.startswith("위험") and a.get("ok") and m.blocked is None and set(m.flags) == {"보고서.pdf.exe", "_HiDAM_x/숨긴.pdf.exe", "뒤에.pdf.exe"}, "풀림 %s · 표시 %s" % (a.get("ok"), sorted(m.flags))

def k15():
    app = HiDAMApp(mk("k15"), auto=False); pc = app.dev.root; w(pc, "DCIM/Camera/a.jpg", b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00" + b"k" * 40)
    g0 = app.preview()[0]["DCIM/Camera/a.jpg"]["grade"]; app.set_place("DCIM/Camera/a.jpg", "08.04"); g1 = app.preview()[0]["DCIM/Camera/a.jpg"]
    return g0 == "D3" and g1["code"] == "08.04" and g1["grade"] == "D3", "규칙 전 %s → 규칙 뒤 %s %s" % (g0, g1["code"], g1["grade"])

for no, title, exp, fn in [
    ("K-01", "재시작해도 계보·결정·복구 횟수가 이어짐", "앞에서 쌓은 계보로 SY-최신·자동, 무료 복구 2회가 다시 생기지 않음", k01),
    ("K-02", "같은 폴더의 엔진 둘 · 원장 파일 손으로 고침", "사슬 유지, 사건 식별자 겹침 0, 고친 것을 앎(죽지 않고 멈춤)", k02),
    ("K-03", "옛 백업으로 덮어씀 · 지웠다 다른 글로 다시 만듦", "확인을 받음 · ②는 다른 자산", k03),
    ("K-04", "v1→v2 뒤 한쪽만 v1로 되돌림", "한 가지 답(꽂는 순서 무관), 고리 없음", k04),
    ("K-05", "틀린 계보를 받음", "받지 않거나 확인, 원장에 남김, 무료 닫힘", k05),
    ("K-06", "두 매체의 같은 이름 다른 메모", "최종본도 따로(덮지 않음)", k06),
    ("K-07", "같은 줄기의 무리 둘, 뒤 무리가 자동 합침", "합친 것은 자기 자리에", k07),
    ("K-08", "복구 뒤 바뀐 것 없이 자동 실행", "복구한 판 그대로", k08),
    ("K-09", "흔한 쓰임 둘(USB 둘 번갈아 20번 · 첫날 매체 넷)", "사용자는 손대지 않음 — 묻는 비율 10% 아래(끝난 기준 ③)", k09),
    ("K-10", "보호 등급 자산의 거울", "조용히 빠지지 않음: 금고 거울로 지키고, 못 지키면 「정상」이라 하지 않음", k10),
    ("K-11", "무료 층의 문", "구독 기능 닫힘, 모드는 일반만", k11),
    ("K-12", "거울 매체가 가득 참", "멈추고 까닭을 적음, 다음 미러링이 돎", k12),
    ("K-13", "깨진 바로가기 · 읽을 수 없는 파일", "그 파일만 보지 못함, 나머지 계속", k13),
    ("K-14", "위험 표시 매체", "사용자 결정으로 풀 수 있음, 숨긴·뒤에 생긴 위협도 표시", k14),
    ("K-15", "꾸러미 사진에 사용자 규칙", "등급은 더 엄했던 값을 지킴", k15)]:
    run(no, title, exp, fn)
res = dict(engine=H.APP_VER, engine_sha256=sha(open(H.__file__, "rb").read()), ran_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           env="Python %s · %s" % (sys.version.split()[0], sys.platform), high_total=len(OUT), high_left=sum(1 for x in OUT if x["result"] != "통과"), cases=OUT)
json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else "k_judge_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in OUT: print(x["k"], x["result"], "|", x["seen"][:200])
print("높음 남음", res["high_left"], "/", res["high_total"], "·", res["engine"])
shutil.rmtree(T, ignore_errors=True)
