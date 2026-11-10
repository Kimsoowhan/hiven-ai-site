# -*- coding: utf-8 -*-
"""HiDAM.app 기준 구현 0.2 (HiDAM 표준 정립서 1.1 · 코드 분류 체계 2.0 기준)
0.1에서 병행 검수 A가 찾은 높음 16건을 고친 판이다. 바뀐 뼈대:
 - 최신 판정은 「내용 포함」이 아니라 계보(색인이 본 앞 해시, 최종본의 바탕, 사용자의 결정)로 한다. 계보가 없으면 자동으로 정하지 않고 제안만 한다.
 - 최종본은 고른 판의 바이트 그대로다. 합친 것만 새 바이트다.
 - 거울은 사용자가 「거울」 역할을 준 매체에만, 첫 실행은 확인 뒤에만 만든다. 보호 등급(D3 이상)은 자동에서 뺀다.
 - 격리는 옮기지 않고 표시한다. 무료 층은 정합·거울을 하지 않는다. 사건마다 코드를 적는다.
 - 모드(일반·시스템·프로젝트)와 매체 역할(작업·보관·프로젝트·거울·원천)을 넣었다.
모듈: CLS · AAD · OPT · SEC · SCT · LNK · SYN · LED · DSH · CLD.  표준 라이브러리만 쓴다."""
import os, re, json, hashlib, shutil, difflib, time, unicodedata

POLICY, APP_VER = "HiDAM-STD-1.0(작업)", "HDA-0.2"
PROTECT_EXT = {"key", "pem", "cer", "crt", "der", "pfx", "p12"}
INSTALL_EXT = {"exe", "msi", "apk", "dll", "bat", "ps1", "ttf", "otf"}
IMG = {"jpg", "jpeg", "png", "gif", "bmp", "tif", "heic", "webp"}
VID = {"mp4", "mov", "avi", "mkv", "wmv", "webm"}
AUD = {"mp3", "wav", "m4a", "flac", "ogg"}
DOC = {"pdf", "doc", "docx", "hwp", "hwpx", "xls", "xlsx", "csv", "ppt", "pptx", "txt", "md"}
TEXT = {"txt", "md", "csv", "json", "py", "html", "css", "js", "sql"}
W_CAREER = {"이력서": "02.01", "경력": "02.01", "포트폴리오": "02.03", "자격증": "01.03", "면허": "01.03",
            "졸업": "01.02", "성적": "01.02", "여권": "01.01", "신분증": "01.01", "증명사진": "01.01"}
W_GOV = {"세금": "07.01", "신고": "07.01", "보험": "07.02", "판결": "07.03", "민원": "07.04",
         "등본": "01.04", "증명원": "01.04"}
AREA_TAG = {"00": "D1", "01": "D3", "02": "D1", "03": "D2", "04": "D2", "05": "D1", "06": "D1", "07": "D2",
            "08": "D0", "09": "D1", "10": "D4", "97": "D3", "98": "D1", "99": "D1"}
STEM_CUT = re.compile(r"(\s*-\s*복사본|\s*\(\d+\)|[_\- ](최종|수정|final|v\d+))$", re.I)   # 날짜·번호는 떼지 않는다(다른 파일을 한 판으로 묶지 않게)
STAGES = {"00": "색인", "01": "기준원칙", "02": "사례", "03": "설정안", "04": "설계안", "05": "수행안", "06": "수행결과",
          "07": "품질검수", "08": "시범테스트", "09": "감리", "10": "관리"}
EV = {("CLS", "판정"): "CLS-E01", ("AAD", "격리 표시"): "AAD-E01", ("AAD", "주의 표시"): "AAD-E02",
      ("SCT", "미등록 매체"): "SCT-E01", ("SCT", "세션 거절"): "SCT-E02", ("SCT", "모드 바꿈"): "SCT-E03", ("SCT", "매체 역할"): "SCT-E04",
      ("LNK", "매체 연결"): "LNK-E01", ("LNK", "매체 분리"): "LNK-E02", ("LNK", "자리 없음"): "LNK-E03",
      ("SYN", "정합 판정"): "SYN-E01", ("SYN", "최종본"): "SYN-E02", ("SYN", "미러링"): "SYN-E03", ("SYN", "자동 실행"): "SYN-E04",
      ("SYN", "자동 미러링 멈춤"): "SYN-E05", ("SYN", "거절"): "SYN-E06", ("SYN", "사용자 결정"): "SYN-E07",
      ("LED", "판 보관"): "LED-E01", ("LED", "복구"): "LED-E02", ("LED", "복구 한도"): "LED-E03", ("LED", "복구 실패"): "LED-E04"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def asset_id(data):
    """ASSET_ID = 내용 해시 앞 16 + 크기. 같은 내용이면 어디에 있든 같은 값(자리는 따로 적는다)."""
    return sha(data)[:16] + "-%d" % len(data)


def decode(data):
    """글자 문서 읽기. 못 읽으면 None(예외를 내지 않는다). (글, 부호, 줄바꿈)"""
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            s = data.decode(enc)
            return s, enc, ("\r\n" if "\r\n" in s else "\n")
        except UnicodeDecodeError:
            continue
    return None


class Ledger:
    """LED: 사건 원장(해시 사슬). 사슬이 끊기면 그 뒤 동작을 멈춘다(K-02)."""

    def __init__(self, dev="", path=None):
        self.rows, self.head, self.dev, self.path = [], "0" * 64, dev, path

    def add(self, mod, act, actor="엔진", **kw):
        if not self.verify():
            raise RuntimeError("원장 사슬 끊김 — 동작 중지")
        row = dict(seq=len(self.rows) + 1, eid="%s#%d" % (self.dev, len(self.rows) + 1), at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), dev=self.dev, actor=actor,
                   code=EV.get((mod, act), mod + "-E00"), mod=mod, act=act, policy=POLICY, prev=self.head, **kw)
        row["h"] = sha(json.dumps({k: v for k, v in row.items() if k != "h"}, ensure_ascii=False, sort_keys=True).encode())
        self.rows.append(row)
        self.head = row["h"]
        if self.path:                                    # 기기 안 파일로도 남긴다(한 줄에 한 사건)
            open(self.path, "a", encoding="utf-8").write(json.dumps(row, ensure_ascii=False) + "\n")
        return row

    def verify(self):
        prev = "0" * 64
        for r in self.rows:
            body = {k: v for k, v in r.items() if k != "h"}
            if r["prev"] != prev or sha(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()) != r["h"]:
                return False
            prev = r["h"]
        return True


def norm(s):
    """이름을 맞대기 전에 같은 모양으로 고른다(운영체제마다 한글 자모를 다르게 적는다, TP-07)."""
    return unicodedata.normalize("NFC", s)


def ext_of(name):
    return name.rsplit(".", 1)[1].lower() if "." in name else ""


def stem_of(name):
    """이름 줄기: 꾸밈말과 번호를 뗀 이름. 떼고 나서 두 글자 미만이면 떼지 않은 이름을 쓴다."""
    name = norm(name)
    base = name.rsplit(".", 1)[0] if "." in name else name
    cut, prev = base, None
    while prev != cut:
        prev, cut = cut, STEM_CUT.sub("", cut)
    cut = cut.strip()
    return (cut if len(cut) >= 2 else base).lower()


def has_shot_info(data):
    return b"Exif" in data[:65536]


# ---------- CLS · SEC ----------
def classify(rel, data, orgs=(), user_rules=None, projects=()):
    """판정 순위 JR-1~8과 사진·영상 PV. 돌려주는 값은 세 축을 다 담는다(용도 구별):
    code 표준 자리 · conf 확신 · rank 순위 · project 프로젝트 묶음과 단계 · folder 사용자 구조의 자리."""
    parts = norm(rel).replace("\\", "/").split("/")
    name, folders, e = parts[-1], [p.lower() for p in parts[:-1]], ext_of(parts[-1])
    out = dict(folder="/".join(parts[:-1]) or "(맨 위)", project=None)
    for pname, pcode in projects:                      # 프로젝트 축: 폴더에 등록한 프로젝트 이름이 있으면
        if any(pname.lower() in f for f in folders):
            st = next((k for k, v in STAGES.items() for f in folders if v in f or f.startswith(k + "_")), "00")
            out["project"] = "%s-%s" % (pcode, st)
            break

    def done(code, conf, rank):
        out.update(code=code, conf=conf, rank=rank)
        return out
    if e in PROTECT_EXT or "npki" in folders:          # JR-1 보호는 사용자 규칙보다 앞선다(CP-08)
        return done("00.04", "높음", "JR-1")
    key = stem_of(name) + "." + e
    if user_rules and key in user_rules:
        return done(user_rules[key], "높음", "사용자 규칙")
    if any(f in ("dcim", "phone data") or f.startswith("backup") or "백업" in f for f in folders):
        return done("97.01", "높음", "JR-2")
    if any("kakaotalk" in f or "받은 파일" in f for f in folders):
        return done("97.04", "높음", "JR-2")
    if any(f in ("downloads", "다운로드") for f in folders) and not (e in IMG or e in VID):
        return done("97.05", "높음", "JR-2")
    sig = []
    for o, code in orgs:
        if any(o.lower() in f for f in folders) or o.lower() in name.lower():
            sig.append((code, "JR-3"))
            break
    for w, c in W_CAREER.items():
        if w in name:
            sig.append((c, "JR-4"))
            break
    for w, c in W_GOV.items():
        if w in name:
            sig.append((c, "JR-5"))
            break
    if sig:                                            # 첫 순위의 자리를 쓰고, 뒤 신호가 같은 영역이면 높음·다르면 중간으로만 적는다
        code, rank = sig[0]
        return done(code, "높음" if len(sig) > 1 and all(s[0][:2] == code[:2] for s in sig) else "중간", rank)
    if e in IMG or e in VID:
        low = name.lower()
        if low.startswith("screenshot") or "화면 캡처" in name or "screen_recording" in low:
            return done("06.10", "높음", "JR-6/PV-02")
        if low.startswith("kakaotalk_"):
            return done("97.04", "중간", "JR-6/PV-03")
        if has_shot_info(data):
            return done("06.01", "높음", "JR-6/PV-01")
        if any(f in ("downloads", "다운로드") for f in folders):
            return done("08.04" if e in IMG else "08.03", "중간", "JR-6/PV-05")
        return done("99.01", "낮음", "JR-8/PV-09")
    if e in AUD:
        return done("08.05", "중간", "JR-6")
    if e in INSTALL_EXT:
        return done("09.02", "높음", "JR-7")
    if e in DOC:
        return done("08.01", "중간", "JR-6")
    return done("99.02" if not e else "99.01", "낮음", "JR-8")


def sec_grade(code, name):
    """SEC: 영역 기본 등급에서 시작해 올리기만 한다(SV-01·02). 보호 자산은 D3 아래로 내려가지 않는다."""
    name = norm(name)
    g = "D3" if code == "00.04" else AREA_TAG.get(code[:2], "D1")
    if ext_of(name) in PROTECT_EXT or any(w in name for w in ("주민", "여권", "계좌", "비밀", "신분증")):
        g = max(g, "D3")
    return g


# ---------- AAD ----------
def aad_check(rel, data):
    """HiAad: (수준, 까닭). 수준 「위험」은 그 매체의 자동 걸음을 멈추고 사용자 결정을 기다린다. 「주의」는 표시만 한다."""
    name, e = rel.split("/")[-1], ext_of(rel)
    if name.lower() == "autorun.inf":
        return "위험", "자동 실행 파일"
    if re.search(r"\.(pdf|jpg|docx?|txt|hwp)\.(exe|bat|ps1|scr)$", name, re.I):
        return "위험", "이중 확장자"
    is_pe = data[:2] == b"MZ" and len(data) >= 64 and b"PE\x00\x00" in data[:4096]
    if is_pe and e not in ("exe", "dll", "msi", "scr"):
        return "위험", "실행 파일이 다른 형식으로 위장"
    head = data[:16].lstrip()
    magic = {"pdf": b"%PDF", "png": b"\x89PNG", "jpg": b"\xff\xd8", "jpeg": b"\xff\xd8", "zip": b"PK"}
    if e in magic and data and not head.startswith(magic[e]) and not data.startswith(magic[e]):
        return "주의", "확장자와 실제 형식이 다름"
    return None


# ---------- 매체 ----------
ROLES = ("작업", "보관", "프로젝트", "거울", "원천")


class Medium:
    """저장 매체 한 자리. 역할을 주면 매체가 곧 분류 체계의 한 층(폴더)이 된다.
    role 작업: 엇갈린 판이 나오는 곳 / 보관: scope에 적은 영역·범주의 집 / 프로젝트: scope에 적은 묶음의 집 / 거울: 비추는 곳 / 원천: 통째 보관(97)."""

    def __init__(self, dev_id, root, kind="외장", registered=True, role="작업", scope=None):
        self.dev_id, self.root, self.kind, self.registered, self.plugged = dev_id, root, kind, registered, True
        self.role, self.scope, self.index, self.blocked, self.flags, self.first_ok = role, scope, {}, None, {}, False

    def path(self, rel):
        return os.path.join(self.root, rel)

    def scan(self, anc=None):
        old, self.index = self.index, {}
        for d, _, fs in os.walk(self.root):
            if any(seg.startswith("_HiDAM") for seg in os.path.relpath(d, self.root).split(os.sep)):
                continue
            for f in fs:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, self.root).replace("\\", "/")
                data = open(p, "rb").read()
                h = sha(data)
                self.index[rel] = dict(asset=asset_id(data), hash=h, size=len(data), mtime=os.path.getmtime(p),
                                       stem=stem_of(f), ext=ext_of(f), dir=os.path.dirname(rel))
                if anc is not None and rel in old and old[rel]["hash"] != h:   # 같은 자리에서 바뀜 → 앞 판의 뒤를 이음
                    anc.setdefault(h, set()).add(old[rel]["hash"])
        return self.index


# ---------- 엔진 ----------
class HiDAMApp:
    def __init__(self, device_root, device_id="DEV-PC-01", tier="구독", orgs=(), projects=(), mass_ratio=0.5, auto=True, mode="시스템"):
        self.dev = Medium(device_id, device_root, "기기")
        os.makedirs(os.path.join(device_root, "_HiDAM"), exist_ok=True)
        self.media, self.tier, self.orgs, self.projects = {}, tier, orgs, projects
        self.led = Ledger(device_id, os.path.join(device_root, "_HiDAM", "00.02_원장.jsonl"))
        self.beta = False
        self.mass_ratio, self.auto, self.user_rules, self.mode = mass_ratio, auto, {}, mode
        self.anc, self.decided, self.finals = {}, {}, {}      # 계보(해시 → 앞 해시들) · 사용자 결정 · 최종본
        self.recover_count, self.last_auto, self.session_lock, self.skipped = {}, None, None, []
        self.vers = os.path.join(device_root, "_HiDAM", "00.08_판보관")
        os.makedirs(self.vers, exist_ok=True)

    # ---- SCT ----
    def open_session(self, sid):
        if self.session_lock and self.session_lock != sid:
            self.led.add("SCT", "세션 거절", sid=sid, holder=self.session_lock)
            return False
        self.session_lock = sid
        return True

    def set_mode(self, mode):
        assert mode in ("일반", "시스템", "프로젝트")
        self.led.add("SCT", "모드 바꿈", actor="사용자", old=self.mode, new=mode)
        self.mode = mode

    def set_role(self, dev_id, role, scope=None):
        assert role in ROLES
        m = self.media[dev_id]
        m.role, m.scope, m.first_ok = role, scope, False
        self.led.add("SCT", "매체 역할", actor="사용자", medium=dev_id, role=role, scope=scope)

    def confirm_first(self, dev_id):
        self.media[dev_id].first_ok = True
        self.led.add("SYN", "사용자 결정", actor="사용자", what="첫 미러링 확인", medium=dev_id)

    # ---- LNK + AAD ----
    def plug(self, m):
        if len(self.media) >= 8 and m.dev_id not in self.media:
            self.led.add("LNK", "자리 없음", medium=m.dev_id)
            return "자리 없음"
        m.plugged = True
        self.media[m.dev_id] = m
        if not m.registered:
            m.blocked = "미등록 매체"
            self.led.add("SCT", "미등록 매체", medium=m.dev_id, grade="M3")
            return m.blocked
        m.scan(self.anc)
        m.flags = {}
        for rel, it in m.index.items():
            r = aad_check(rel, open(m.path(rel), "rb").read())
            if r:
                m.flags[rel] = r                       # 옮기지 않는다. 표시하고 뒤 걸음에서 뺀다
                self.led.add("AAD", "격리 표시" if r[0] == "위험" else "주의 표시", medium=m.dev_id, asset=it["asset"], why=r[1],
                             grade="M3" if r[0] == "위험" else "M2")
        if any(v[0] == "위험" for v in m.flags.values()):
            m.blocked = "위험 표시 — 사용자 결정 대기"
            return m.blocked
        m.blocked = None
        self.led.add("LNK", "매체 연결", medium=m.dev_id, files=len(m.index), role=m.role)
        if self.auto and self.tier == "구독":
            self.auto_run("꽂으면")
        return "정상"

    def import_lineage(self, other):
        """SY-19: 같은 회원의 다른 기기 원장에서 계보(해시 앞뒤)만 받아 온다. 원본·이름은 받지 않는다."""
        for h, ps in other.anc.items():
            self.anc.setdefault(h, set()).update(ps)

    def unplug(self, dev_id):
        self.media[dev_id].plugged = False
        self.led.add("LNK", "매체 분리", medium=dev_id)

    def rescan(self):
        self.dev.scan(self.anc)
        for m in self.media.values():
            if m.plugged and not m.blocked:
                m.scan(self.anc)

    def work_sources(self):
        """판을 찾는 곳: 기기와, 거울이 아닌 매체."""
        return [self.dev] + [m for m in self.media.values() if m.plugged and not m.blocked and m.role != "거울"]

    # ---- CLS ----
    def judge(self, src, rel):
        data = open(src.path(rel), "rb").read()
        c = classify(rel, data, self.orgs, self.user_rules, self.projects)
        c["grade"] = sec_grade(c["code"], rel)
        c["place"] = {"일반": c["folder"], "시스템": c["code"], "프로젝트": c["project"] or c["code"]}[self.mode]
        return c

    def preview(self, log=True):
        self.dev.scan(self.anc)
        out = {rel: self.judge(self.dev, rel) for rel in self.dev.index}
        n = max(len(out), 1)
        stat = {k: round(sum(1 for v in out.values() if v["conf"] == k) / n, 3) for k in ("높음", "중간", "낮음")}
        if log:
            self.led.add("CLS", "판정", files=len(out), mode=self.mode, high=stat["높음"], mid=stat["중간"], low=stat["낮음"])
        return out, stat

    # ---- OPT ----
    def dup_map(self):
        self.rescan()
        byhash = {}
        for s in self.work_sources():
            for rel, it in s.index.items():
                if it["size"]:
                    byhash.setdefault(it["hash"], []).append((s.dev_id, rel, it["size"]))
        dup = {h: v for h, v in byhash.items() if len(v) > 1}
        return dict(dup_groups=len(dup), reclaim_bytes=sum(v[0][2] * (len(v) - 1) for v in dup.values()),
                    version_sets=len(self._version_sets())), dup

    # ---- SYN: 판 묶기 ----
    def _version_sets(self):
        """같은 것의 판: 이름 줄기와 확장자가 같고, (같은 폴더 자리이거나 글 내용이 반 넘게 겹침). 이름만으로 묶지 않는다."""
        g = {}
        for s in self.work_sources():
            for rel, it in s.index.items():
                if s.flags.get(rel) or it["size"] == 0:
                    continue
                g.setdefault((it["stem"], it["ext"]), []).append((s, rel, it))
        sets = {}
        for (stem, e), items in g.items():
            if len({x[2]["hash"] for x in items}) < 2:
                continue
            groups = []
            for x in items:
                for grp in groups:
                    if self._same_thing(grp[0], x):
                        grp.append(x)
                        break
                else:
                    groups.append([x])
            for i, grp in enumerate(groups):
                if len({x[2]["hash"] for x in grp}) > 1:
                    sets[(stem, e, i)] = grp
        return sets

    def _same_thing(self, a, b):
        if a[2]["hash"] == b[2]["hash"] or self._desc(a[2]["hash"], b[2]["hash"]) or self._desc(b[2]["hash"], a[2]["hash"]):
            return True
        if a[2]["ext"] in TEXT:
            ta, tb = decode(open(a[0].path(a[1]), "rb").read()), decode(open(b[0].path(b[1]), "rb").read())
            if ta and tb:
                return difflib.SequenceMatcher(None, ta[0].splitlines(), tb[0].splitlines(), autojunk=False).ratio() >= 0.5
            return False
        base = lambda d: "" if d in ("기준자리", "") else d
        return base(a[2]["dir"]) == base(b[2]["dir"])     # 글이 아닌 것은 같은 폴더 자리에 있을 때만

    def _desc(self, x, y):
        """x가 y의 뒤 판인가(계보를 따라 y에 닿는가)."""
        seen, todo = set(), [x]
        while todo:
            h = todo.pop()
            for p in self.anc.get(h, ()):
                if p == y:
                    return True
                if p not in seen:
                    seen.add(p)
                    todo.append(p)
        return False

    @staticmethod
    def _contains(big, small):
        it = iter(big)
        return all(any(x == y for y in it) for x in small)

    @staticmethod
    def _merge3(base, a, b):
        """바탕이 계보로 확인된 때만 쓴다. 겹치지 않게 고친 것만 합치고, 닿거나 겹치면 None."""
        def edits(x):
            return [(i1, i2, x[j1:j2]) for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, base, x, autojunk=False).get_opcodes() if t != "equal"]
        ea, eb = edits(a), edits(b)
        if any(max(i1, k1) <= min(i2, k2) for i1, i2, _ in ea for k1, k2, _ in eb):
            return None
        out, pos = [], 0
        for i1, i2, rep in sorted(ea + eb):
            out += base[pos:i1] + rep
            pos = i2
        return out + base[pos:]

    # ---- SYN: 정합 ----
    def reconcile(self):
        if self.tier != "구독":                          # 무료: 엇갈린 건수만
            self.rescan()
            n = len(self._version_sets())
            self.led.add("SYN", "거절", why="무료 층 — 건수만", unsettled=n)
            return dict(unsettled=n, note="정합 동기화는 구독 기능입니다")
        self.rescan()
        res = []
        for (stem, e, gi), items in sorted(self._version_sets().items()):
            uniq = {}
            for s, rel, it in items:
                uniq.setdefault(it["hash"], (s, rel, it))
            hs = list(uniq)
            row = dict(stem=stem, ext=e, versions=len(hs), where=[(s.dev_id, rel) for s, rel, _ in items], final=None)
            grades = [self.judge(s, rel)["grade"] for s, rel, _ in items]
            if max(grades) >= "D3":
                row.update(judge="SY-보류", how="자동에서 뺌", why="보호 등급(%s) — 사용자가 직접 고르고 금고 거울로만 비춤" % max(grades))
            else:
                key = (stem, e, gi)
                pick = self.decided.get(key)
                if pick and pick["hash"] in uniq and set(hs) <= pick["seen"]:
                    row.update(judge="SY-최신", how="사용자 결정", why="앞서 고른 판 그대로(새 내용 없음)")
                    self._final_copy(uniq[pick["hash"]], row)
                else:
                    tops = [h for h in hs if all(h == o or self._desc(h, o) for o in hs)]
                    if tops:
                        s, rel, it = uniq[tops[0]]
                        row.update(judge="SY-최신", how="자동", why="%s의 판이 다른 판들의 뒤를 이음(계보 확인)" % s.dev_id)
                        self._final_copy(uniq[tops[0]], row)
                    else:
                        self._diverged(uniq, hs, e, row)
            self.led.add("SYN", "정합 판정", stem=stem, judge=row["judge"], how=row["how"])
            res.append(row)
        self.dev.scan(self.anc)                          # 방금 만든 최종본을 색인에 넣는다(그 뒤의 고침이 계보로 이어지게)
        return res

    def _diverged(self, uniq, hs, e, row):
        txt = {h: decode(open(uniq[h][0].path(uniq[h][1]), "rb").read()) for h in hs} if e in TEXT else {}
        if e in TEXT and all(txt.values()):
            lines = {h: txt[h][0].splitlines() for h in hs}
            bases = [b for b in hs if all(b == o or self._desc(o, b) for o in hs)]     # 모두의 앞 판(계보로 확인된 바탕)
            if bases and len(hs) == 3:
                o = [h for h in hs if h != bases[0]]
                mg = self._merge3(lines[bases[0]], lines[o[0]], lines[o[1]])
                if mg is not None:
                    enc, nl = txt[bases[0]][1], txt[bases[0]][2]
                    data = (nl.join(mg) + (nl if txt[bases[0]][0].endswith(("\n", "\r\n")) else "")).encode("utf-8" if enc.startswith("utf") else enc)
                    row.update(judge="SY-갈라짐", how="자동 합침", why="바탕 판이 계보로 확인됨 — 겹치지 않게 고친 대목을 합침")
                    self._final_write(row, data, parents=hs)
                    return
                row.update(judge="SY-갈라짐", how="사용자가 고름", why="같은 대목을 다르게 고침 — 양쪽을 나란히 보여 줌")
                return
            sup = [h for h in hs if all(self._contains(lines[h], lines[o]) for o in hs)]
            if sup:
                row.update(judge="SY-제안", how="확인 필요", suggest=uniq[sup[0]][0].dev_id,
                           why="계보가 없음. %s의 판이 다른 판의 줄을 다 담고 있어 최신으로 보이나, 줄을 지운 고침일 수도 있어 확인을 받음" % uniq[sup[0]][0].dev_id)
                return
            row.update(judge="SY-갈라짐", how="사용자가 고름", why="계보가 없고 서로 없는 내용이 있음 — 나란히 보여 줌")
            return
        row.update(judge="SY-갈라짐", how="사용자가 고름", why="글자 문서가 아니거나 읽지 못하는 부호 — 차이를 보여 주고 고르게 함")

    def choose(self, stem, ext, dev_id, gi=0):
        """사용자가 판을 고른다(SY-제안·SY-갈라짐·SY-보류에 대한 답)."""
        items = self._version_sets()[(stem, ext, gi)]
        pick = next(x for x in items if x[0].dev_id == dev_id)
        self.decided[(stem, ext, gi)] = dict(hash=pick[2]["hash"], seen={x[2]["hash"] for x in items})
        for x in items:
            if x[2]["hash"] != pick[2]["hash"]:
                self.anc.setdefault(pick[2]["hash"], set()).add(x[2]["hash"])
        self.led.add("SYN", "사용자 결정", actor="사용자", what="판 고름", stem=stem, medium=dev_id)
        row = dict(final=None)
        self._final_copy(pick, row)
        self.dev.scan(self.anc)
        return row["final"]

    def _final_rel(self, it, rel_src):
        d = it["dir"] if it["dir"] not in ("", "기준자리") else ""
        return ("기준자리/" + (d + "/" if d and not d.startswith("기준자리") else "") + "%s.%s" % (it["stem"], it["ext"])) if not rel_src.startswith("기준자리/") else rel_src

    def _final_copy(self, picked, row):
        s, rel, it = picked
        data = open(s.path(rel), "rb").read()            # 고른 판의 바이트 그대로
        frel = self._final_rel(it, rel if s is self.dev else "")
        row["final_from"] = [s.dev_id]
        self._put_final(frel, data, row, parents=[])

    def _final_write(self, row, data, parents):
        any_item = None
        for (st, e, gi), items in self._version_sets().items():
            if st == row["stem"] and e == row["ext"]:
                any_item = items[0]
                break
        frel = self._final_rel(any_item[2], "")
        row["final_from"] = sorted({x for x, _ in row["where"]})
        self._put_final(frel, data, row, parents=parents)

    def _put_final(self, frel, data, row, parents):
        p = self.dev.path(frel)
        h = sha(data)
        row["final"] = frel
        if os.path.exists(p):
            cur = sha(open(p, "rb").read())
            if cur == h:
                self.finals[frel] = h
                return
            self._keep_version(frel)
            self.anc.setdefault(h, set()).add(cur)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)
        for ph in parents:
            if ph != h:
                self.anc.setdefault(h, set()).add(ph)
        self.finals[frel] = h
        self.led.add("SYN", "최종본", rel=frel, asset=asset_id(data), src=row.get("final_from"))

    def _vdir(self, rel):
        d = os.path.join(self.vers, sha(rel.encode("utf-8"))[:16])      # 자리마다 따로(이름이 섞이지 않게)
        os.makedirs(d, exist_ok=True)
        return d

    def _keep_version(self, rel):
        src, d = self.dev.path(rel), self._vdir(rel)
        n = len(os.listdir(d)) + 1
        shutil.copy2(src, os.path.join(d, "v%d" % n))
        self.led.add("LED", "판 보관", rel=rel, ver=n, asset=asset_id(open(src, "rb").read()))
        return n

    # ---- SYN: 거울 ----
    def mirror_set(self, m):
        """거울에 비출 것: 기기의 자산 가운데 엇갈림이 풀린 것, 보호 등급 아래, 매체의 범위(scope)에 드는 것."""
        unsettled = {rel for items in self._version_sets().values() for s, rel, _ in items if s is self.dev}
        want, skipped = {}, []
        for rel, it in self.dev.index.items():
            j = self.judge(self.dev, rel)
            if j["grade"] >= "D3":
                skipped.append((rel, "보호 등급 — 금고 거울 필요"))
            elif rel in unsettled and rel not in self.finals:
                skipped.append((rel, "판이 엇갈림 — 정합 먼저"))
            elif m.scope and not (j["code"].startswith(m.scope) or (j["project"] or "").startswith(m.scope)):
                continue
            else:
                want[rel] = it["hash"]
        return want, skipped

    def mirror(self, dev_id, auto=False):
        m = self.media[dev_id]
        if self.tier != "구독":
            self.led.add("SYN", "거절", why="무료 층", medium=dev_id)
            return dict(done=0, stopped="미러링은 구독 기능입니다")
        if not m.plugged or m.blocked:
            return dict(done=0, stopped="매체 사용 불가")
        if m.role != "거울":
            return dict(done=0, stopped="거울 역할이 아닌 매체")
        if not m.first_ok:
            want, sk = self.mirror_set(m)
            return dict(done=0, stopped="첫 미러링 — 미리 보기와 확인 필요", preview=len(want))
        self.dev.scan(self.anc)
        mroot = os.path.join(m.root, "_HiDAM_거울")
        os.makedirs(mroot, exist_ok=True)
        want, skipped = self.mirror_set(m)
        have = {}
        for d, _, fs in os.walk(mroot):
            for f in fs:
                p = os.path.join(d, f)
                have[os.path.relpath(p, mroot).replace("\\", "/")] = sha(open(p, "rb").read())
        change, gone = [r for r in want if have.get(r) != want[r]], [r for r in have if r not in want]
        altered = [r for r in change if r in have]       # 새로 생긴 것은 대량 변경으로 세지 않는다
        if auto and len(have) >= 10 and (len(altered) + len(gone)) / len(have) > self.mass_ratio:
            self.led.add("SYN", "자동 미러링 멈춤", medium=dev_id, why="대량 변경", change=len(change), gone=len(gone), grade="M3")
            return dict(done=0, stopped="대량 변경 — 확인 필요")
        bad = 0
        for r in change:
            dst = os.path.join(mroot, r)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            tmp = dst + ".hidam_tmp"
            shutil.copy2(self.dev.path(r), tmp)
            if sha(open(tmp, "rb").read()) != want[r]:
                os.remove(tmp)                            # 앞 거울은 그대로 둔다
                bad += 1
                self.led.add("SYN", "거절", why="해시 불일치", medium=dev_id, rel=r, grade="M2")
            else:
                os.replace(tmp, dst)
        for r in gone:                                    # 지워진 것은 보류함으로
            hd = os.path.join(m.root, "_HiDAM_보류함", r)
            os.makedirs(os.path.dirname(hd), exist_ok=True)
            shutil.move(os.path.join(mroot, r), hd)
        out = dict(done=len(change) - bad, held=len(gone), mismatch=bad, skipped=len(skipped), stopped=None)
        self.skipped = skipped
        self.led.add("SYN", "미러링", medium=dev_id, auto=auto, done=out["done"], held=out["held"], mismatch=bad, skipped=len(skipped))
        return out

    def auto_run(self, trigger):
        """AP-01~12: (검사는 plug에서) → 다시 읽기 → 정합 → 거울 → 기록."""
        if self.tier != "구독" or not self.auto:
            return None
        rec = self.reconcile()
        res = {d: self.mirror(d, auto=True) for d, m in self.media.items() if m.plugged and not m.blocked and m.role == "거울"}
        stopped = ["%s(%s)" % (d, r["stopped"]) for d, r in res.items() if r["stopped"]]
        wait = [r["stem"] for r in rec if r["how"] in ("확인 필요", "사용자가 고름", "자동에서 뺌")]
        self.last_auto = dict(trigger=trigger, mirrored=sum(r["done"] for r in res.values()), reconciled=len(rec), waiting=wait,
                              result=("멈춤: " + ", ".join(stopped)) if stopped else ("확인 대기 %d건" % len(wait) if wait else "정상"))
        self.led.add("SYN", "자동 실행", trigger=trigger, mirrored=self.last_auto["mirrored"], waiting=len(wait), result=self.last_auto["result"])
        return self.last_auto

    # ---- LED: 복구 ----
    def recover(self, rel, ver, beta=None):
        beta = self.beta if beta is None else beta
        used = self.recover_count.get(rel, 0)
        limit = None if self.tier == "구독" else (5 if beta else 2)
        note = None if self.tier == "구독" else "※ 책임지는 복구(원복)는 구독 서비스에 한합니다."
        name = "복구(원복)" if self.tier == "구독" else "복구(되돌리기)"
        if limit is not None and used >= limit and not beta:
            self.led.add("LED", "복구 한도", rel=rel, used=used)
            return dict(ok=False, name=name, note=note, left=0, guide="구독 안내")
        src = os.path.join(self._vdir(rel), "v%d" % ver)
        if not os.path.exists(src):
            self.led.add("LED", "복구 실패", rel=rel, ver=ver, why="그 판이 없음")
            return dict(ok=False, name=name, note=note, why="그 판이 없음")
        data, p = open(src, "rb").read(), self.dev.path(rel)
        if os.path.exists(p):
            cur = sha(open(p, "rb").read())
            self._keep_version(rel)
        else:
            cur = None
            os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copy2(src, p)
        h = sha(data)
        it = dict(stem=stem_of(os.path.basename(rel)), ext=ext_of(rel))
        for key, items in list(self._version_sets().items()) + [((it["stem"], it["ext"], 0), [])]:   # 복구는 사용자의 결정이다
            if key[0] == it["stem"] and key[1] == it["ext"]:
                self.decided[key] = dict(hash=h, seen={x[2]["hash"] for x in items} | {h} | ({cur} if cur else set()))
        self.finals[rel] = h
        self.dev.scan()
        self.recover_count[rel] = used + 1
        self.led.add("LED", "복구", rel=rel, ver=ver, tier=self.tier)
        return dict(ok=True, name=name, note=note, left=None if limit is None else max(limit - used - 1, 0),
                    guide="구독 안내(베타 기간에는 계속 해 드립니다)" if (beta and limit is not None and used + 1 >= limit) else None)

    # ---- DSH · CLD ----
    def dashboard(self):
        prev, stat = self.preview(log=False)
        opt, dup = self.dup_map()
        by = {}
        for v in prev.values():
            k = v["place"] if self.mode != "시스템" else v["code"][:2]
            by[k] = by.get(k, 0) + 1
        mcount = lambda m: len([1 for _d, _, fs in os.walk(os.path.join(m.root, "_HiDAM_거울")) for _ in fs])
        flagged = [(d, rel, r[0], r[1]) for d, m in self.media.items() for rel, r in m.flags.items()]
        danger = any(m.blocked for m in self.media.values())
        todo = bool(self.last_auto and self.last_auto.get("waiting")) or opt["version_sets"] > 0
        return {
            "1_내기기": dict(dev=self.dev.dev_id, mode=self.mode, media=[dict(dev=d, kind=m.kind, role=m.role, scope=m.scope,
                           state="꽂힘" if m.plugged else "뽑힘(마지막 본 값)", blocked=m.blocked) for d, m in self.media.items()]),
            "2_내디지털자산": dict(files=len(prev), by_place=by, conf=stat, dup=opt, unsettled=opt["version_sets"]),
            "3_보호상태": dict(flagged=flagged, unregistered=[d for d, m in self.media.items() if not m.registered],
                           state="위험" if danger else ("살핌 필요" if todo or flagged else "정상")),
            "4_거울상태": dict(mirrors={d: mcount(m) for d, m in self.media.items() if m.role == "거울"}, last_auto=self.last_auto,
                           skipped=self.skipped[:5]),
            "5_금고": dict(count="확인 안 됨", note="기준 구현 범위 밖"),
            "6_기록": dict(events=len(self.led.rows), chain_ok=self.led.verify(), recover_used=self.recover_count),
            "7_구독회원": dict(tier=self.tier, devices="확인 안 됨(회원·기기 등록은 Cloud 쪽)"),
            "8_설정": dict(auto=self.auto, mass_ratio=self.mass_ratio, policy=POLICY, app=APP_VER, mode=self.mode),
            "9_열쇠": dict(note="값 없음 — 이름·위치·이력만"),
        }

    def cloud_payload(self, show_names=False):
        """FN-12: 메타데이터만. 원본·내용·키 값 없음. 이름은 사용자가 켠 때만."""
        if self.tier != "구독":
            return None
        prev, stat = self.preview(log=False)
        assets = []
        for rel, it in self.dev.index.items():
            a = dict(asset=it["asset"], size=it["size"], code=prev[rel]["code"], grade=prev[rel]["grade"], project=prev[rel]["project"])
            if show_names:
                a["name"] = rel
            assets.append(a)
        return dict(dev=self.dev.dev_id, policy=POLICY, app=APP_VER, mode=self.mode, at=int(time.time()),
                    media=[dict(dev=d, kind=m.kind, role=m.role, scope=m.scope) for d, m in self.media.items()],
                    assets=assets, sums=stat, events=[dict(seq=r["seq"], code=r["code"]) for r in self.led.rows])
