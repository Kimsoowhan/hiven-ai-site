# -*- coding: utf-8 -*-
"""HiDAM.app 기준 구현 0.1 (HiDAM 표준 정립서 1.0 기준)
모듈: CLS 분류 · AAD 보호 · OPT 최적화 · SEC 보안 분류 · SCT 자가 통제 · LNK 연결 · SYN 정합·미러링 · LED 원장·복구 · DSH 대시보드
원칙: 원본 내용을 고치지 않는다 · 지우지 않는다 · 값은 원장에 쓴다 · Cloud로는 메타데이터만.
표준 라이브러리만 쓴다(Windows·macOS·Linux 같은 코드)."""
import os, re, json, hashlib, shutil, difflib, time

POLICY = "HiDAM-STD-1.0"
PROTECT_EXT = {"key", "pem", "cer", "crt", "der", "pfx", "p12"}
INSTALL_EXT = {"exe", "msi", "apk", "dll", "bat", "ps1", "ttf", "otf"}
IMG = {"jpg", "jpeg", "png", "gif", "bmp", "tif", "heic", "webp"}
VID = {"mp4", "mov", "avi", "mkv", "wmv", "webm"}
AUD = {"mp3", "wav", "m4a", "flac", "ogg"}
DOC = {"pdf", "doc", "docx", "hwp", "hwpx", "xls", "xlsx", "csv", "ppt", "pptx", "txt", "md"}
TEXT = {"txt", "md", "csv", "json", "py", "html", "css", "js", "sql"}
W_CAREER = {"이력서": "02.01", "경력": "02.01", "포트폴리오": "02.03", "자격증": "01.03", "면허": "01.03",
            "졸업": "01.02", "성적": "01.02", "여권": "01.01", "신분증": "01.01", "증명사진": "01.01"}
W_ADMIN = {"세금": "07.01", "신고": "07.01", "보험": "07.02", "판결": "07.03", "민원": "07.04",
           "등본": "01.04", "증명원": "01.04"}
AREA_TAG = {"00": "D1", "01": "D3", "02": "D1", "03": "D2", "04": "D2", "05": "D1", "06": "D1", "07": "D2",
            "08": "D0", "09": "D1", "10": "D4", "97": "D3", "98": "D1", "99": "D1"}
MAGIC = {"pdf": b"%PDF", "png": b"\x89PNG", "jpg": b"\xff\xd8", "jpeg": b"\xff\xd8", "zip": b"PK", "exe": b"MZ"}
STEM_CUT = re.compile(r"(\s*-\s*복사본|\s*\(\d+\)|[_\- ]?(최종|수정|final|v\d+)|[_\- ]?\d{6,8})+$", re.I)


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Ledger:
    """LED: 사건 원장(해시 사슬). 사슬이 끊기면 그 뒤 동작을 멈춘다(K-02)."""

    def __init__(self):
        self.rows, self.head = [], "0" * 64

    def add(self, mod, act, **kw):
        if not self.verify():
            raise RuntimeError("원장 사슬 끊김 — 동작 중지")
        row = dict(n=len(self.rows) + 1, mod=mod, act=act, policy=POLICY, prev=self.head, **kw)
        row["h"] = sha(json.dumps({k: v for k, v in row.items() if k != "h"}, ensure_ascii=False, sort_keys=True).encode())
        self.rows.append(row)
        self.head = row["h"]
        return row

    def verify(self):
        prev = "0" * 64
        for r in self.rows:
            body = {k: v for k, v in r.items() if k != "h"}
            if r["prev"] != prev or sha(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()) != r["h"]:
                return False
            prev = r["h"]
        return True


def ext_of(name):
    return name.rsplit(".", 1)[1].lower() if "." in name else ""


def stem_of(name):
    base = name.rsplit(".", 1)[0] if "." in name else name
    prev = None
    while prev != base:
        prev, base = base, STEM_CUT.sub("", base)
    return base.strip().lower()


def has_shot_info(data):
    return b"Exif" in data[:65536]


# ---------- CLS · SEC ----------
def classify(rel, data, orgs=(), user_rules=None):
    """판정 순위 JR-1~8과 사진·영상 PV. (자리, 확신, 순위) — 같은 입력이면 어디서나 같은 값."""
    parts = rel.replace("\\", "/").split("/")
    name, folders, e = parts[-1], [p.lower() for p in parts[:-1]], ext_of(parts[-1])
    key = stem_of(name) + "." + e
    if user_rules and key in user_rules:
        return user_rules[key], "높음", "사용자 규칙"
    if e in PROTECT_EXT or "npki" in folders:
        return "00.04", "높음", "JR-1"
    if any(f in ("dcim", "phone data") or f.startswith("backup") or "백업" in f for f in folders):
        return "97.01", "높음", "JR-2"
    if any("kakaotalk" in f or "받은 파일" in f for f in folders):
        return "97.04", "높음", "JR-2"
    sig = []
    for o, code in orgs:
        if any(o.lower() in f for f in folders) or o.lower() in name.lower():
            sig.append((code, "JR-3"))
            break
    for w, c in W_CAREER.items():
        if w in name:
            sig.append((c, "JR-4"))
            break
    for w, c in W_ADMIN.items():
        if w in name:
            sig.append((c, "JR-5"))
            break
    if sig:
        code, rank = sig[0]
        same = all(s[0][:2] == code[:2] for s in sig)
        return code, ("높음" if len(sig) > 1 and same else "중간" if same else "낮음"), rank
    if e in IMG or e in VID:
        low = name.lower()
        if low.startswith("screenshot") or "화면 캡처" in name or "screen_recording" in low:
            return "06.10", "높음", "JR-6/PV-02"
        if low.startswith("kakaotalk_"):
            return "97.04", "중간", "JR-6/PV-03"
        if has_shot_info(data):
            return "06.01", "높음", "JR-6/PV-01"
        if any(f in ("downloads", "다운로드") for f in folders):
            return ("08.04" if e in IMG else "08.03"), "중간", "JR-6/PV-05"
        return "99.01", "낮음", "JR-8/PV-09"
    if e in AUD:
        return "08.05", "중간", "JR-6"
    if e in INSTALL_EXT:
        return "09.02", "높음", "JR-7"
    if e in DOC:
        return "08.01", "중간", "JR-6"
    return ("99.02" if not e else "99.01"), "낮음", "JR-8"


def sec_grade(code, name):
    """SEC: 영역 기본 등급에서 시작해 올리기만 한다(SV-01·02)."""
    g = "D3" if code == "00.04" else AREA_TAG.get(code[:2], "D1")
    if any(w in name for w in ("주민", "여권", "계좌", "비밀")) and g < "D3":
        g = "D3"
    return g


# ---------- AAD ----------
def aad_check(rel, data):
    """HiAad: 꽂는 순간·바뀌는 순간 검사. 위협이면 까닭을 돌려준다."""
    name, e = rel.split("/")[-1], ext_of(rel)
    if name.lower() == "autorun.inf":
        return "자동 실행 파일"
    if re.search(r"\.(pdf|jpg|docx?|txt)\.(exe|bat|ps1|scr)$", name, re.I):
        return "이중 확장자"
    if e in MAGIC and data and not data.startswith(MAGIC[e]):
        return "확장자와 실제 형식이 다름"
    if e not in ("exe", "dll", "msi") and data.startswith(b"MZ"):
        return "실행 파일이 다른 형식으로 위장"
    return None


# ---------- 매체 ----------
class Medium:
    def __init__(self, dev_id, root, kind="외장", registered=True):
        self.dev_id, self.root, self.kind, self.registered, self.plugged = dev_id, root, kind, registered, True
        self.index, self.blocked = {}, None

    def scan(self):
        self.index = {}
        for d, _, fs in os.walk(self.root):
            if os.path.basename(d).startswith("_HiDAM"):
                continue
            for f in fs:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, self.root).replace("\\", "/")
                if rel.startswith("_HiDAM"):
                    continue
                data = open(p, "rb").read()
                h = sha(data)
                self.index[rel] = dict(asset=h[:16] + "-%d" % len(data), hash=h, size=len(data),
                                       mtime=os.path.getmtime(p), stem=stem_of(f), ext=ext_of(f))
        return self.index


# ---------- 엔진 ----------
class HiDAMApp:
    def __init__(self, device_root, device_id="DEV-PC-01", tier="구독", orgs=(), mass_ratio=0.5, auto=True):
        self.dev = Medium(device_id, device_root, "기기")
        self.media, self.led, self.tier, self.orgs = {}, Ledger(), tier, orgs
        self.mass_ratio, self.auto, self.user_rules = mass_ratio, auto, {}
        self.recover_count, self.last_auto, self.finals, self.session_lock = {}, None, {}, None
        self.hold = os.path.join(device_root, "_HiDAM", "00.07_보류함")
        self.vers = os.path.join(device_root, "_HiDAM", "00.08_판보관")
        self.quar = os.path.join(device_root, "_HiDAM", "격리")
        for d in (self.hold, self.vers, self.quar):
            os.makedirs(d, exist_ok=True)

    # SCT: 한 기기 한 엔진(NC-01)
    def open_session(self, sid):
        if self.session_lock and self.session_lock != sid:
            self.led.add("SCT", "세션 거절", sid=sid, holder=self.session_lock)
            return False
        self.session_lock = sid
        return True

    # LNK + AAD: 꽂으면(AP-01~03)
    def plug(self, m):
        if len([x for x in self.media.values()]) >= 8 and m.dev_id not in self.media:
            self.led.add("LNK", "자리 없음", dev=m.dev_id)
            return "자리 없음"
        m.plugged = True
        self.media[m.dev_id] = m
        if not m.registered:
            self.led.add("SCT", "미등록 매체", dev=m.dev_id, grade="M3")
            m.blocked = "미등록 매체"
            return m.blocked
        m.scan()
        for rel in list(m.index):
            why = aad_check(rel, open(os.path.join(m.root, rel), "rb").read())
            if why:
                q = os.path.join(self.quar, m.dev_id + "_" + rel.replace("/", "_"))
                shutil.move(os.path.join(m.root, rel), q)
                m.blocked = why
                self.led.add("AAD", "격리", dev=m.dev_id, asset=m.index[rel]["asset"], why=why, grade="M3")
        if m.blocked:
            m.scan()
            return m.blocked
        self.led.add("LNK", "매체 연결", dev=m.dev_id, files=len(m.index))
        if self.auto and self.tier == "구독":
            self.auto_run("꽂으면")
        return "정상"

    def unplug(self, dev_id):
        self.media[dev_id].plugged = False
        self.led.add("LNK", "매체 분리", dev=dev_id)

    def sources(self):
        return [self.dev] + [m for m in self.media.values() if m.plugged and not m.blocked]

    # CLS: 미리 보기(무료·구독 같은 결과)
    def preview(self):
        out = {}
        for rel, it in self.dev.scan().items():
            data = open(os.path.join(self.dev.root, rel), "rb").read()
            code, conf, rank = classify(rel, data, self.orgs, self.user_rules)
            out[rel] = dict(code=code, conf=conf, rank=rank, grade=sec_grade(code, rel))
        n = max(len(out), 1)
        stat = {k: round(sum(1 for v in out.values() if v["conf"] == k) / n, 3) for k in ("높음", "중간", "낮음")}
        self.led.add("CLS", "판정", files=len(out), **{"높음": stat["높음"], "중간": stat["중간"], "낮음": stat["낮음"]})
        return out, stat

    # OPT: 중복 지도(완전 중복·판·묶음)
    def dup_map(self):
        byhash, bystem = {}, {}
        for s in self.sources():
            for rel, it in s.scan().items():
                byhash.setdefault(it["hash"], []).append((s.dev_id, rel, it["size"]))
                bystem.setdefault((it["stem"], it["ext"]), set()).add(it["hash"])
        dup = {h: v for h, v in byhash.items() if len(v) > 1}
        save = sum(v[0][2] * (len(v) - 1) for v in dup.values())
        vers = {k: len(v) for k, v in bystem.items() if len(v) > 1}
        return dict(dup_groups=len(dup), reclaim_bytes=save, version_sets=len(vers)), dup, vers

    # SYN: 판 계보와 정합 판정(SY-03~07)
    def _versions(self):
        g = {}
        for s in self.sources():
            for rel, it in s.index.items():
                g.setdefault((it["stem"], it["ext"]), []).append((s, rel, it))
        return {k: v for k, v in g.items() if len({x[2]["hash"] for x in v}) > 1}

    @staticmethod
    def _contains(big, small):
        it = iter(big)
        return all(any(x == y for y in it) for x in small)

    @staticmethod
    def _merge3(base, a, b):
        """겹치지 않게 고친 것은 자동으로 합치고, 같은 대목을 다르게 고쳤으면 None."""
        def edits(x):
            return [(i1, i2, x[j1:j2]) for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, base, x, autojunk=False).get_opcodes() if t != "equal"]
        ea, eb = edits(a), edits(b)
        for i1, i2, _ in ea:
            for k1, k2, _ in eb:
                if max(i1, k1) <= min(i2, k2):
                    return None
        out, pos = [], 0
        for i1, i2, rep in sorted(ea + eb):
            out += base[pos:i1] + rep
            pos = i2
        return out + base[pos:]

    def reconcile(self):
        res = []
        for (stem, e), items in sorted(self._versions().items()):
            uniq = {}
            for s, rel, it in items:
                uniq.setdefault(it["hash"], (s, rel, it))
            cand = list(uniq.values())
            row = dict(stem=stem, ext=e, versions=len(cand), where=[(s.dev_id, rel) for s, rel, _ in items])
            if e in TEXT:
                txt = [open(os.path.join(s.root, rel), encoding="utf-8").read().splitlines() for s, rel, _ in cand]
                top = [i for i, t in enumerate(txt) if all(self._contains(t, o) for o in txt)]
                if top:
                    s, rel, it = cand[top[0]]
                    row.update(judge="SY-최신", final_from=[s.dev_id], how="자동", why="%s의 판이 다른 판의 내용을 다 담음" % s.dev_id)
                    final = txt[top[0]]
                else:
                    final = None
                    if len(txt) == 3:  # 바탕 판 찾기: 셋 가운데 하나를 바탕으로 놓았을 때만 겹치지 않게 합쳐지는 경우
                        tries = []
                        for b in range(3):
                            o = [i for i in range(3) if i != b]
                            mg = self._merge3(txt[b], txt[o[0]], txt[o[1]])
                            if mg is not None:
                                tries.append(mg)
                        if len(tries) == 1:
                            final = tries[0]
                    if final is not None:
                        row.update(judge="SY-갈라짐", how="자동 합침", final_from=[c[0].dev_id for c in cand],
                                   why="서로 겹치지 않게 고친 대목을 합침")
                    else:
                        row.update(judge="SY-갈라짐", how="사용자가 고름", final_from=[],
                                   why="같은 대목을 다르게 고쳤거나 바탕 판이 없음 — 양쪽을 나란히 보여 줌")
                if final is not None:
                    self._write_final(stem, e, "\n".join(final).encode("utf-8"), row)
            else:
                row.update(judge="SY-갈라짐", how="사용자가 고름", final_from=[], why="글자 문서가 아님 — 차이를 보여 주고 고르게 함")
            self.led.add("SYN", "정합 판정", stem=stem, judge=row["judge"], how=row["how"])
            res.append(row)
        return res

    def _write_final(self, stem, e, data, row):
        rel = "기준자리/%s.%s" % (stem, e)
        p = os.path.join(self.dev.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.exists(p):
            self._keep_version(rel)
        open(p, "wb").write(data)
        self.finals[rel] = sha(data)
        row["final"] = rel
        self.led.add("SYN", "최종본", rel=rel, hash=sha(data)[:16], src=row["final_from"])

    def _keep_version(self, rel):
        src = os.path.join(self.dev.root, rel)
        n = len([x for x in os.listdir(self.vers) if x.startswith(rel.replace("/", "_"))]) + 1
        dst = os.path.join(self.vers, "%s.v%d" % (rel.replace("/", "_"), n))
        shutil.copy2(src, dst)
        self.led.add("LED", "판 보관", rel=rel, ver=n, hash=sha(open(src, "rb").read())[:16])
        return dst

    # SYN: 거울(MR-03·04·16) — 최종본이 선 것만
    def mirror(self, dev_id, auto=False):
        m = self.media[dev_id]
        if not m.plugged or m.blocked:
            return dict(done=0, stopped="매체 사용 불가")
        mroot = os.path.join(m.root, "_HiDAM_거울")
        os.makedirs(mroot, exist_ok=True)
        want = {rel: h for rel, h in self.finals.items() if os.path.exists(os.path.join(self.dev.root, rel))}
        have = {}
        for d, _, fs in os.walk(mroot):
            for f in fs:
                p = os.path.join(d, f)
                have[os.path.relpath(p, mroot).replace("\\", "/")] = sha(open(p, "rb").read())
        change = [r for r in want if have.get(r) != want[r]]
        gone = [r for r in have if r not in want]
        if auto and have and (len(change) + len(gone)) / max(len(have), 1) > self.mass_ratio:
            self.led.add("SYN", "자동 미러링 멈춤", dev=dev_id, why="대량 변경", change=len(change), gone=len(gone), grade="M3")
            return dict(done=0, stopped="대량 변경 — 확인 필요")
        bad = 0
        for r in change:
            dst = os.path.join(mroot, r)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(self.dev.root, r), dst)
            if sha(open(dst, "rb").read()) != want[r]:
                os.remove(dst)
                bad += 1
        for r in gone:
            hd = os.path.join(m.root, "_HiDAM_보류함", r)
            os.makedirs(os.path.dirname(hd), exist_ok=True)
            shutil.move(os.path.join(mroot, r), hd)
        out = dict(done=len(change) - bad, held=len(gone), mismatch=bad, stopped=None)
        self.led.add("SYN", "미러링", dev=dev_id, auto=auto, **{k: v for k, v in out.items() if k != "stopped"})
        return out

    def auto_run(self, trigger):
        """AP-01~12: 검사는 plug에서 끝남 → 판정 → 중복 → 정합 → 거울 → 기록."""
        if self.tier != "구독":
            return None
        rec = self.reconcile()
        res = {d: self.mirror(d, auto=True) for d, m in self.media.items() if m.plugged and not m.blocked}
        stopped = [d for d, r in res.items() if r["stopped"]]
        self.last_auto = dict(trigger=trigger, mirrored=sum(r["done"] for r in res.values()), reconciled=len(rec),
                              result="멈춤: " + ",".join(stopped) if stopped else "정상", row=len(self.led.rows))
        self.led.add("SYN", "자동 실행", **{k: v for k, v in self.last_auto.items() if k != "row"})
        return self.last_auto

    # LED: 복구(기능은 같고 횟수·책임이 다름)
    def recover(self, rel, ver, beta=False):
        used = self.recover_count.get(rel, 0)
        limit = None if self.tier == "구독" else (5 if beta else 2)
        note = None if self.tier == "구독" else "※ 책임지는 복구(원복)는 구독 서비스에 한합니다."
        if limit is not None and used >= limit and not beta:
            self.led.add("LED", "복구 한도", rel=rel, used=used)
            return dict(ok=False, name="복구(되돌리기)", note=note, left=0, guide="구독 안내")
        src = os.path.join(self.vers, "%s.v%d" % (rel.replace("/", "_"), ver))
        self._keep_version(rel)
        shutil.copy2(src, os.path.join(self.dev.root, rel))
        self.recover_count[rel] = used + 1
        self.finals[rel] = sha(open(src, "rb").read())
        self.led.add("LED", "복구", rel=rel, ver=ver, tier=self.tier)
        return dict(ok=True, name="복구(원복)" if self.tier == "구독" else "복구(되돌리기)", note=note,
                    left=None if limit is None else max(limit - used - 1, 0))

    # DSH: 대시보드 아홉 칸(기기 판)과 Cloud로 올리는 것(UD-08·09)
    def dashboard(self):
        prev, stat = self.preview()
        opt, dup, vers = self.dup_map()
        area = {}
        for v in prev.values():
            area[v["code"][:2]] = area.get(v["code"][:2], 0) + 1
        mirrors = {d: len([1 for _d, _, fs in os.walk(os.path.join(m.root, "_HiDAM_거울")) for _ in fs]) for d, m in self.media.items()}
        return {
            "1_내기기": dict(dev=self.dev.dev_id, media=[dict(dev=d, kind=m.kind, state="꽂힘" if m.plugged else "뽑힘(마지막 본 값)",
                                                              blocked=m.blocked) for d, m in self.media.items()]),
            "2_내디지털자산": dict(files=len(prev), area=area, conf=stat, dup=opt, unsettled=len(self._versions())),
            "3_보호상태": dict(quarantined=len(os.listdir(self.quar)), unregistered=[d for d, m in self.media.items() if not m.registered],
                           state="위험" if any(m.blocked for m in self.media.values()) else "정상"),
            "4_거울상태": dict(mirrors=mirrors, last_auto=self.last_auto),
            "5_금고": dict(count=0, note="기준 구현 범위 밖"),
            "6_기록": dict(events=len(self.led.rows), chain_ok=self.led.verify(), recover_used=self.recover_count),
            "7_구독회원": dict(tier=self.tier, devices=1),
            "8_설정": dict(auto=self.auto, mass_ratio=self.mass_ratio, policy=POLICY),
            "9_열쇠": dict(note="값 없음 — 이름·위치·이력만"),
        }

    def cloud_payload(self, show_names=False):
        """FN-12: 메타데이터만. 원본·내용·키 값 없음. 이름은 사용자가 켠 때만."""
        if self.tier != "구독":
            return None
        prev, stat = self.preview()
        assets = []
        for rel, it in self.dev.index.items():
            a = dict(asset=it["asset"], size=it["size"], code=prev[rel]["code"], grade=prev[rel]["grade"])
            if show_names:
                a["name"] = rel
            assets.append(a)
        return dict(dev=self.dev.dev_id, policy=POLICY, at=int(time.time()), media=[dict(dev=d, kind=m.kind) for d, m in self.media.items()],
                    assets=assets, sums=stat, events=[dict(n=r["n"], mod=r["mod"], act=r["act"]) for r in self.led.rows])
