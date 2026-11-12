# -*- coding: utf-8 -*-
# 0.5 추가 시나리오(TS-120~): Fable 변이(fb_mut.py seed 20261111)에서 살아남은 줄을 잡고, 매체 셋·문서 하나 번갈아 꼴을 고정한다.
# sim_hidam_app.py 안에서 exec로 돌린다(같은 도우미 w · rd · ex · mk · ok · new · codes · snap을 씀). 시뮬레이션.
import random as _r5
G16 = "하 OP-2 0.5 Fable 검수 보강"

def _walk(tag, seed, nmed, docs, steps, pick, mid):
    """매체 여럿에서 무작위로 고치고 걸음마다 자동 실행. 돌려줌: 묻지 않고 빠진 고침 수 · 물은 걸음 · 걸음 전후 매체 같음 수 · 문서별 열린 물음 최대."""
    _r5.seed(seed); app = new(mk(tag), auto=True); R_ = [mk("%s_%d" % (tag, i)) for i in range(nmed)]
    body = {d_: ["%s %d줄" % (d_, i) for i in range(12)] for d_ in docs}
    for d_ in docs:
        for x_ in R_: w(x_, "업무/" + d_, "\n".join(body[d_]) + "\n")
    for i, x_ in enumerate(R_): app.plug(Medium("M%d" % i, x_))
    cur = {(i, d_): list(body[d_]) for i in range(nmed) for d_ in docs}; marks, asked, same, seen, open_max = [], 0, 0, set(app.pkeys), 0
    for st in range(steps):
        m_, d_ = pick(st, nmed, docs); L = cur[(m_, d_)]; L[_r5.randrange(len(L))] += " 고침%d" % st
        if mid and st % 3 == 0: L.insert(_r5.randrange(1, len(L)), "끼움%d" % st)
        else: L.append("더함%d" % st)
        w(R_[m_], "업무/" + d_, "\n".join(L) + "\n"); marks.append((d_, "고침%d" % st))
        b_ = [snap(x_) for x_ in R_]; la = app.auto_run("바뀌면"); same += [snap(x_) for x_ in R_] == b_
        newp = [k for k in app.pkeys if k not in seen and k.startswith(("판|", "판확인|"))]; seen |= set(app.pkeys); asked += bool(newp or la["waiting"])
        per = {}
        for p in app.props.values():
            if p["state"] == "열림" and p["kind"] in ("판 고르기", "판 확인"): per[p["key"].split("|")[1]] = per.get(p["key"].split("|")[1], 0) + 1
        open_max = max([open_max] + list(per.values()))
    waiting = set(app.last_wait or [])
    fin = {d_: (rd(app.dev.root, "기준자리/업무/" + d_).decode() if ex(app.dev.root, "기준자리/업무/" + d_) else "") for d_ in docs}
    silent = [(d_, g) for d_, g in marks if g not in fin[d_] and d_.rsplit(".", 1)[0] not in waiting]
    return dict(silent=len(silent), asked=asked, steps=steps, same=same, open_max=open_max, state=app.dashboard()["3_보호상태"]["state"])

D5_ = ["보고서.txt", "회의록.md", "예산.csv", "일정.txt", "메모.md"]
w3 = [_walk("w3s%d" % s_, s_, 3, D5_ + ["계획.txt"], 30, lambda st, n, docs: (_r5.randrange(n), _r5.choice(docs)), True) for s_ in (11, 12, 13)]
ok("TS-120", G16, "매체 셋 · 무작위 30걸음: 묻지 않고 빠진 고침 0 · 참 겹침만 물음 · 원본 매체 그대로", "A·B(Fable 검수 F17) · RL-06",
   all(x["silent"] == 0 and x["same"] == x["steps"] and x["asked"] <= 3 for x in w3), [(x["silent"], x["asked"], x["same"]) for x in w3])
w1 = [_walk("w1s%d" % s_, s_, 2, ["보고서.txt"], 20, lambda st, n, docs: (st % 2, docs[0]), False) for s_ in (21, 22, 23)]
ok("TS-121", G16, "문서 하나를 두 매체에서 번갈아 20번: 빠진 고침 0 · 한 문서에 열린 물음은 늘 하나 이하", "C(Fable 검수 F17) · RL-06",
   all(x["silent"] == 0 and x["open_max"] <= 1 and x["same"] == x["steps"] for x in w1), [(x["silent"], x["asked"], x["open_max"]) for x in w1])

# TS-122 「정상」 금지 원칙: 최종본에 들지 않은 판이 있으면 정상이 아님(합치지 못하게 만든 경우)
g2, g2a, g2b = mk("g2"), mk("g2a"), mk("g2b")
for x_ in (g2a, g2b): w(x_, "업무/글.txt", "가\n나\n다\n라\n")
G2_ = new(g2, auto=True); G2_.plug(Medium("A", g2a)); G2_.plug(Medium("B", g2b)); G2_.auto_run("바뀌면")
w(g2a, "업무/글.txt", "가\n너\n다\n라\n"); w(g2b, "업무/글.txt", "가\n냐\n다\n라\n"); la2 = G2_.auto_run("바뀌면")
fin2 = rd(g2, "기준자리/업무/글.txt").decode() if ex(g2, "기준자리/업무/글.txt") else ""
ok("TS-122", G16, "같은 글자를 두 매체가 다르게 고침: 최종본에 한쪽만 든 채 「정상」이 되지 않고 물음 하나", "A(Fable 검수 F17) · SY",
   la2["result"] != "정상" and la2["waiting"] == ["글"] and not ("너" in fin2 and "냐" in fin2) and sum(1 for p in G2_.props.values() if p["state"] == "열림" and p["kind"] == "판 고르기") == 1,
   (la2["result"], la2["waiting"]))

# TS-123 묶음 번호: 옮긴 번호도 빈 번호 없이 이어짐 · 같은 묶음은 먼저 등록된 쪽 번호로 · 상대에만 있는 묶음은 그대로 받음
ex_, ey_ = mk("ex5"), mk("ey5")
[w(ex_, "사진/제주/J_%d.jpg" % i, JPG_SHOT + b"j" + bytes([i])) for i in range(2)]; X5 = new(ex_, device_id="DEV-PC-X5", auto=False); X5.preview()
[w(ey_, "사진/부산/B_%d.jpg" % i, JPG_SHOT + b"b" + bytes([i])) for i in range(2)]; Y5 = new(ey_, device_id="DEV-PC-Y5", auto=False); Y5.preview()
[w(ey_, "사진/제주/J_%d.jpg" % i, JPG_SHOT + b"j" + bytes([i])) for i in range(2)]; Y5.preview()
X5.sync_bundles(Y5)
nums = sorted({int(b["id"].rsplit("B", 1)[1]) for a_ in (X5, Y5) for b in a_.bundles.values() if b["id"].startswith("06.01-B")})
jeju = [b["id"] for a_ in (X5, Y5) for b in a_.bundles.values() if b["state"] == "씀" and b["folder"].endswith("제주")]
ez_, ew_ = mk("ez5"), mk("ew5"); Z5 = new(ez_, device_id="DEV-PC-Z5", auto=False); Z5.preview()
[w(ew_, "사진/부산/B_%d.jpg" % i, JPG_SHOT + b"b" + bytes([i])) for i in range(2)]; W5 = new(ew_, device_id="DEV-PC-W5", auto=False); W5.preview()
try: zr = Z5.sync_bundles(W5)
except Exception as e_: zr = repr(e_)
ok("TS-123", G16, "두 기기 묶음 번호 맞춤: 새 번호는 빈 번호 없이 이어지고, 같은 묶음은 먼저 등록된 기기의 번호, 한쪽에만 있는 묶음은 죽지 않고 그대로", "PL-04 · T-108",
   nums == list(range(1, max(nums) + 1)) and X5.bseq["06.01"] == max(nums) and jeju == ["06.01-B0001", "06.01-B0001"] and isinstance(zr, list),
   (nums, jeju, zr if isinstance(zr, str) else "됨"))

# TS-124 복구(자리): 한 번 되돌리면 횟수 1 · 옛 자리에 다른 파일이 있으면 거절 · 계보를 새로 잇지 않음
s5 = mk("s5"); fill(s5); S5 = new(s5, mode="시스템", auto=False); ap5 = dict(S5.apply_places()["pairs"])
n1 = ap5.get("사진/IMG_1.jpg"); v1 = [v for v in S5.versions(n1) if v["kind"] == "자리"]; anc0 = sum(len(v) for v in S5.anc.values()); np0 = len(S5.props)
rv1 = S5.recover(n1, v1[0]["ver"]); anc1 = sum(len(v) for v in S5.anc.values()); np1 = len(S5.props)
cnt = sorted(S5.recover_count.values())
n2 = ap5.get("프로그램/설치.exe"); v2 = [v for v in S5.versions(n2) if v["kind"] == "자리"]; w(s5, "프로그램/설치.exe", b"another")
rv2 = S5.recover(n2, v2[0]["ver"])
ok("TS-124", G16, "복구(자리·이름): 횟수는 한 번에 1 · 옛 자리를 다른 파일이 차지하면 거절(RC-22) · 되돌리며 계보나 제안을 새로 만들지 않음", "RS · LED · RL",
   rv1["ok"] and cnt == [1] and rv2["ok"] is False and S5.led.rows[-1].get("rc") == "RC-22" and anc1 == anc0 and np1 == np0, (rv1["ok"], cnt, rv2.get("ok"), anc0, anc1, np0, np1))

# TS-125 따로 등록된 두 자산이 한 자산으로 밝혀지면 먼저 등록된 식별자를 지킴
m5 = mk("m5"); w(m5, "가.txt", "첫째\n"); M5 = new(m5, auto=False); M5.preview(); w(m5, "나.txt", "둘째\n"); M5.preview()
ia, ib = M5._aid(M5.dev.index["가.txt"]["asset"]), M5._aid(M5.dev.index["나.txt"]["asset"])
M5._link(M5.dev.index["나.txt"]["hash"], M5.dev.index["가.txt"]["hash"])
ok("TS-125", G16, "두 자산이 계보로 하나가 되면 먼저 등록된 식별자를 지키고 다른 쪽은 대응표", "ID-11·12",
   ia != ib and M5._aid(ib) == ia and M5.alias.get(ib) == ia, (ia, ib, M5._aid(ib)))

# TS-126 보호(JR-1)는 자리 기억보다 앞섬 · 자리 기억은 일반 파일엔 지켜짐
j5 = mk("j5"); w(j5, "NPKI/signCert.der", b"0\x82cert"); w(j5, "문서/메모.txt", "메모\n"); J5 = new(j5, auto=False); J5.preview()
J5.place_mem[J5._pkey(J5.dev, "NPKI/signCert.der")] = dict(code="06.01", rank="JR-4", basis="시험")
J5.place_mem[J5._pkey(J5.dev, "문서/메모.txt")] = dict(code="05.04", rank="JR-4", basis="시험")
jg1, jg2 = J5.judge(J5.dev, "NPKI/signCert.der"), J5.judge(J5.dev, "문서/메모.txt")
ok("TS-126", G16, "보호 자산은 자리 기억이 있어도 보호 자리 · 일반 파일은 자리 기억을 지킴", "PL-12 · JR-1 · CP-08",
   jg1["code"] == "00.04" and jg2["code"] == "05.04" and jg2.get("kept") == "자리 기억", (jg1["code"], jg2["code"]))

# TS-127 거울: 같은 폴더에서 둘 이상 지워져도 모두 보류함으로
h5, h5m = mk("h5"), mk("h5m"); [w(h5, "작은/n%d.txt" % i, "n%d\n" % i) for i in range(4)]
H5 = new(h5, auto=False); H5.plug(Medium("M", h5m, role="거울")); H5.confirm_first("M"); H5.mirror("M")
os.remove(os.path.join(h5, "작은/n0.txt")); os.remove(os.path.join(h5, "작은/n1.txt")); rh5 = H5.mirror("M")
ok("TS-127", G16, "거울에서 물러난 것이 같은 폴더에 둘 이상이어도 모두 보류함으로 옮김", "MR-05",
   rh5["held"] == 2 and ex(h5m, "_HiDAM_보류함/작은/n0.txt") and ex(h5m, "_HiDAM_보류함/작은/n1.txt") and not ex(h5m, "_HiDAM_거울/작은/n1.txt"), rh5)

# TS-128 제안 물리기는 참을 돌려줌 · 묶음 분류: 조직 묶음은 프로젝트로 적지 않음, 조직 아래 프로젝트는 조직 번호를 받음
o5 = mk("o5"); [w(o5, "회사가/과제나/0%d_설계안/d%d.docx" % (i, i), b"d%d" % i) for i in range(1, 3)]; w(o5, "회사가/공문/a.pdf", b"%PDF-1.4 a")
O5 = new(o5, auto=False); O5.preview(); og = O5._make_group("조직 묶기", dict(folder="회사가")); pg = O5._make_group("프로젝트 묶기", dict(folder="회사가/과제나"))
oj = O5.judge(O5.dev, "회사가/공문/a.pdf"); u5m = mk("u5m"); O5.plug(Medium("U5", u5m)); rp = [p for p in O5.proposals() if p["kind"] == "매체 역할"]
dr = O5.decline(rp[0]["no"]) if rp else None
ok("TS-128", G16, "조직 아래 프로젝트 묶음은 조직 번호 · 조직에만 든 파일은 프로젝트 없음 · 제안을 물리면 참", "PL-03 · PL-05 · SCT",
   O5.bundles[pg]["code"] == O5.bundles[og]["code"] and oj.get("project") is None and dr is True, (O5.bundles[og]["code"], O5.bundles[pg]["code"], oj.get("project"), dr))

# TS-129 무료 기기에서 계보를 받으려 하면 RC-01로 거절 · 받은 파일(다운로드) 폴더의 문서는 97.05
f5 = new(mk("f5"), tier="무료", auto=False); y5 = new(mk("y5"), auto=False); fl = f5.import_lineage(y5)
ok("TS-129", G16, "무료 기기의 계보 받기는 RC-01 거절 · 다운로드 폴더 문서는 97.05, 사진은 아님", "FN · LNK · JR-2",
   fl is False and f5.led.rows[-1].get("rc") == "RC-01" and classify("Downloads/설명서.pdf", b"%PDF-1.4 x")["code"] == "97.05" and classify("Downloads/사진.jpg", JPG_SHOT)["code"] != "97.05",
   (fl, f5.led.rows[-1].get("rc")))

# TS-130 폴더째 겹침: 작은 폴더가 큰 폴더에 다 들어 있으면 「한쪽이 다 들어 있음」(작은 쪽이 앞에 와도)
k5 = mk("k5"); [w(k5, "가/f%d.bin" % i, b"same%d" % i) for i in range(2)]; [w(k5, "나/f%d.bin" % i, b"same%d" % i) for i in range(3)]
K5 = new(k5, auto=False); K5.preview(); dd5 = K5.dup_deep()
kk = {(x["a"][1], x["b"][1]): x["kind"] for x in dd5["sets"]}
ok("TS-130", G16, "폴더째 겹침: 작은 폴더가 큰 폴더에 다 들어 있음", "SET · IX-12", kk.get(("가", "나")) == "한쪽이 다 들어 있음" or kk.get(("나", "가")) == "한쪽이 다 들어 있음", kk)

# TS-131 금고 거울: 쓰다 실패하면 임시 칸을 남기지 않고 멈춤
v5, v5m = mk("v5"), mk("v5m"); w(v5, "개인/여권사본.pdf", b"%PDF-1.4 secret5"); V5 = new(v5, auto=False); V5.plug(Medium("V", v5m, role="거울")); V5.confirm_first("V")
_rep = _HA.os.replace
def _bad_rep(a_, b_, *k_):
    if str(b_).endswith(".hv"): raise OSError("시험: 쓰기 실패")
    return _rep(a_, b_, *k_)
_HA.os.replace = _bad_rep
try: rv5 = V5.mirror("V")
finally: _HA.os.replace = _rep
left5 = [f_ for f_ in (os.listdir(os.path.join(v5m, "_HiDAM_금고")) if ex(v5m, "_HiDAM_금고") else []) if f_.endswith(".hidam_tmp")]
ok("TS-131", G16, "금고 칸을 쓰다 실패하면 임시 칸을 지우고 멈춤(원장 RC-24)", "TG-04 · MR",
   rv5.get("stopped") and not left5 and "RC-24" in [r_.get("rc") for r_ in V5.led.rows[-3:]], (rv5.get("stopped"), left5))

# TS-132 내용 복구는 계보를 거꾸로 잇지 않고, 되돌린 판을 「옛 판 덮어씀」으로 다시 판정하지 않음
c5 = mk("c5"); w(c5, "a.txt", "첫 판\n하나\n둘\n셋\n"); C5 = new(c5, auto=False); C5.preview(); h1_ = C5.dev.index["a.txt"]["hash"]; C5._keep_version("a.txt")
w(c5, "a.txt", "둘째 판\n하나\n둘\n셋\n넷\n"); C5.preview(); h2_ = C5.dev.index["a.txt"]["hash"]; C5._keep_version("a.txt"); w(c5, "a.txt", "셋째 판\n하나\n둘\n셋\n넷\n다섯\n"); C5.preview()
n5r = len(C5.led.rows); v15 = [v["ver"] for v in C5.versions("a.txt") if v.get("hash") == h1_]; rc5 = C5.recover("a.txt", v15[0]) if v15 else dict(ok=False)
ok("TS-132", G16, "내용 복구 뒤에도 계보는 첫 판 → 둘째 판 그대로이고, 복구 걸음에서 판을 새로 판정하는 사건(SYN-E08)이 없음", "RS · LNK · RL-06",
   rc5["ok"] and rd(c5, "a.txt").startswith("첫 판".encode()) and not C5._desc(h1_, h2_) and "SYN-E08" not in codes(C5, n5r), (rc5["ok"], C5._desc(h1_, h2_), codes(C5, n5r)))

# TS-133 금고 칸 머리글(HV1)이 바뀌면 열지 않음
vk = b"k" * 32; cell = _HA.vault_seal(vk, "개인/a.pdf", b"secret"); bad = b"XV1" + cell[3:]
ok("TS-133", G16, "금고 칸: 머리글이 다르면 확인값이 맞아도 열지 않음 · 바르면 열림", "TG-04",
   _HA.vault_open(vk, bad) is None and _HA.vault_open(vk, cell) == ("개인/a.pdf", b"secret"), "머리글 바꾼 칸 거절")

# TS-134 이름 규칙 「모드 규칙」: 자리는 그대로이고 이름만 바꿀 새 파일도 자동으로 이름이 붙음(묻지 않음)
n5 = mk("n5"); w(n5, "문서/있던것.txt", "x\n"); N5 = new(n5, mode="시스템", rename_policy="모드 규칙"); N5.preview()
w(n5, "문서/여덟~메모.txt", "메모\n"); _pp = N5.plan_places
def _one():
    out_ = [p for p in _pp() if p["rel"] == "문서/여덟~메모.txt"]
    for p in out_: p.update(how="자동", moves=False, name_why=p.get("name_why") or "꾸밈말", conf="높음")
    return out_
N5.plan_places = _one
try: N5.auto_run("바뀌면")
finally: N5.plan_places = _pp
ok("TS-134", G16, "「모드 규칙」에서 옮길 필요 없이 이름만 바꿀 새 파일도 자동으로 표준 이름(원장 CLS-E04)", "NM-01~06 · T-118",
   not ex(n5, "문서/여덟~메모.txt") and "CLS-E04" in codes(N5), sorted(k for k in snap(n5) if "메모" in k))

# ===== 0.5 엔진 줄이 바뀐 뒤 Fable 변이(같은 seed)에서 새로 살아남은 줄을 잡는 시나리오 =====
# TS-135 프로젝트 검사: 줄이 하나도 없는 요구는 끊김으로 · 한 곳에만 실린 바깥 번호는 겹침이 아님
rq2_ = P.add_requirement(hb["id"]); P.set_external(hb["id"], "08.01", "고객산출물:D-99"); c7 = P.project_checks(hb["id"])
ok("TS-135", G16, "다른 줄이 있어도 나가는 줄 없는 요구는 「추적 줄 끊김」 · 한 곳에만 실린 바깥 번호는 겹침이 아님", "8장 검사 ⑥·⑨",
   rq2_ in [c["target"] for c in c7 if c["check"] == "추적 줄 끊김"] and len([c for c in c7 if c["check"] == "바깥 번호 겹침"]) == 1, [(c["check"], c["target"]) for c in c7 if c["check"] in ("추적 줄 끊김", "바깥 번호 겹침")])

# TS-136 화면 숫자: 묶음은 쓰는 것만 · 프로젝트 칸은 프로젝트 묶음만 · 오늘 막은 위협은 위협 사건만 셈
d5 = O5.dashboard(); live5 = sum(1 for b in O5.bundles.values() if b["state"] == "씀")
ok("TS-136", G16, "화면: 묶음 수 = 쓰는 묶음 · 프로젝트 칸 = 프로젝트 묶음 · 위협 수는 다른 「멈춤」을 세지 않음", "UV · ST-01",
   d5["2_내디지털자산"]["bundles"] == live5 and live5 >= 1 and len(d5["다_프로젝트"]) == sum(1 for b in O5.bundles.values() if b["kind"] == "프로젝트" and b["state"] == "씀") and V5._done_today(0)["threats"] == 0,
   (d5["2_내디지털자산"]["bundles"], live5, len(d5["다_프로젝트"]), V5._done_today(0)["threats"]))

# TS-137 죽지 않음: 알던 내용을 새 자리에 복사 · 없는 매체나 열쇠 없이 금고 열기 · 읽지 못하는 글자 문서를 번갈아 고침
a5 = mk("a5"); w(a5, "x/a.txt", "같은 내용\n"); A5_ = new(a5, auto=False); A5_.preview(); w(a5, "y/b.txt", "같은 내용\n")
try:
    A5_.preview(); cp5 = A5_._aid(A5_.dev.index["y/b.txt"]["asset"]) == A5_._aid(A5_.dev.index["x/a.txt"]["asset"])
    w(a5, "z/c.txt", "같은 내용\n"); A5_._keep_version("z/c.txt"); cp5 = cp5 and A5_._asset_at("z/c.txt") == A5_._aid(A5_.dev.index["x/a.txt"]["asset"])
except Exception as e_: cp5 = repr(e_)
kp5 = os.path.join(V5.home, "00.10_금고열쇠.key"); kb5 = kp5 + ".시험"
try:
    vr0 = V5.vault_restore("없는매체", "개인/여권사본.pdf")
    if os.path.exists(kp5): os.rename(kp5, kb5)
    vr1 = V5.vault_restore("V", "개인/여권사본.pdf")
except Exception as e_: vr0 = vr1 = repr(e_)
finally:
    if os.path.exists(kb5): os.rename(kb5, kp5)
u5, u5a, u5b = mk("u5"), mk("u5a"), mk("u5b")
for x_ in (u5a, u5b): w(x_, "업무/옛글.txt", "하나\n둘\n셋\n")
U5 = new(u5, auto=True); U5.plug(Medium("A", u5a)); U5.plug(Medium("B", u5b)); U5.auto_run("바뀌면")
open(os.path.join(u5a, "업무/옛글.txt"), "wb").write(b"\xff\x80 A\n\xff\n"); open(os.path.join(u5b, "업무/옛글.txt"), "wb").write(b"\xff\x80 B\n\xff\n")
try: lu5 = U5.auto_run("바뀌면")
except Exception as e_: lu5 = dict(result=repr(e_), waiting=[])
ok("TS-137", G16, "알던 내용을 새 자리에 복사해도 같은 자산 · 없는 매체나 열쇠 없이 금고를 열면 None · 읽지 못하는 글자 문서를 두 매체에서 고치면 죽지 않고 물음", "ID · TG-04 · SY",
   cp5 is True and vr0 is None and vr1 is None and lu5["result"] != "정상" and "옛글" in lu5["waiting"], (cp5, vr0, vr1, lu5["result"], lu5["waiting"]))

# TS-138 조직 후보: 「상사」 같은 꼬리말이 붙은 폴더는 보관 묶음이 먼저 서 있어도 조직 후보 · 평범한 매체는 백업으로 보지 않음
t5 = mk("t5"); [w(t5, "한빛상사/q%d.pdf" % i, b"%%PDF-1.4 q%d" % i) for i in range(3)]; T5 = new(t5, auto=False); T5.preview()
og5 = [p for p in T5.proposals(True) if p["kind"] == "조직 묶기" and "한빛상사" in p["what"]]
[w(t5, "자료/x%d.pdf" % i, b"%%PDF-1.4 x%d" % i) for i in range(2)]; T5.preview(); w(t5, "자료/누리전자/r.pdf", b"%PDF-1.4 r"); T5.preview()
og5b = [p for p in T5.proposals(True) if p["kind"] == "조직 묶기" and "누리전자" in p["what"]]
og5 = og5 if og5b and any(b_["kind"] == "보관" and b_["folder"] == "자료" for b_ in T5.bundles.values()) else []
ok("TS-138", G16, "꼬리말(상사)로 조직 후보를 뽑음 · 평범한 문서 매체는 백업 보관으로 권하지 않음", "PL-03 · RL-04",
   len(og5) == 1 and "백업" not in _HA.recommend_role({"문서/a.txt": {}, "문서/b.txt": {}, "사진/c.jpg": {}})[2], (len(og5), _HA.recommend_role({"문서/a.txt": {}, "문서/b.txt": {}, "사진/c.jpg": {}})))

# TS-139 받아들인 조직 묶음 안의 파일은 자리를 옮기지 않음(갈 자리 없음)
o6 = mk("o6"); w(o6, "회사가/공문/a.pdf", b"%PDF-1.4 a"); w(o6, "회사가/공문/b.pdf", b"%PDF-1.4 b"); O6 = new(o6, auto=False, mode="시스템"); O6.preview(); O6._make_group("조직 묶기", dict(folder="회사가"))
pp5 = [p for p in O6.plan_places() if p["rel"] == "회사가/공문/a.pdf"]
ok("TS-139", G16, "조직 묶음 안 파일의 갈 자리는 없음(None) — 묶음 폴더를 지킴", "PL-05 · CP",
   len(pp5) == 1 and pp5[0]["to"] is None, [(p["to"], p.get("why")) for p in pp5])

# TS-140 원장 끝줄이 같은 길이로 바뀌면(사슬은 맞아도 장치카드의 끝줄과 다름) 끊김으로 봄
l5 = mk("l5"); w(l5, "a.txt", "1\n"); L5 = new(l5, auto=False); L5.preview(); L5._save(); lp5 = L5.led.path; del L5
rows5 = [json.loads(x_) for x_ in open(lp5, encoding="utf-8").read().splitlines() if x_.strip()]
last5 = dict(rows5[-1], at="2000-01-01T00:00:00Z"); last5["h"] = _HA.Ledger._h(last5); rows5[-1] = last5
open(lp5, "w", encoding="utf-8", newline="\n").write("".join(json.dumps(r_, ensure_ascii=False) + "\n" for r_ in rows5))
L5b = new(l5, auto=False)
ok("TS-140", G16, "원장 끝줄을 같은 줄 수로 바꿔 쓰면 다시 띄울 때 「끊김」", "LED · K-02", dict(L5b.boot).get("원장") == "끊김", L5b.boot)

# TS-141 긴 줄(200자 넘음)도 앞머리를 고친 줄을 같은 줄로 맞대어 합침
LL5 = ("가나다라마바사아자차카타파하 " * 20).strip()
mg5 = HiDAMApp._merge3(["첫", LL5, "끝"], ["첫", "새줄", "거" + LL5[1:], "끝"], ["첫", LL5 + " B", "끝"])
ok("TS-141", G16, "긴 줄의 앞머리를 고치고 줄을 끼운 쪽과 끝에 덧붙인 쪽을 합침(같은 줄로 맞댐)", "SY · 합침",
   mg5 is not None and mg5[2] == "거" + LL5[1:] + " B", "합침 됨" if mg5 else "합치지 못함")
