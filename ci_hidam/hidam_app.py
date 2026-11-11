# -*- coding: utf-8 -*-
"""HiDAM.app 기준 구현 0.4 (HiDAM 표준 정립서 1.0 작업본 · 코드 분류 체계 2.0 작업본 기준)
0.4(OP-2, 워크 0009 STEP 2-1)에서 닫은 것: ① 엔진이 본 적 없는 옛 판으로 덮어쓴 것을 뒤 판으로 잇지 않음(옛 날짜 · 내용이 크게 다름 → 한 번 확인)
 ② 두 매체에서 번갈아 고친 문서: 계보로 확인된 바탕에서 겹치지 않게 고친 대목을 스스로 합침(묻지 않음). 첫날 계보가 없을 때는 내용 포함과 고친 시각으로 맞춤
 ③ 보호 등급 자산의 금고 거울(거울 매체의 _HiDAM_금고에 잠가서 비춤) ④ 확신 「중간」: 한 번 받아들인 범주는 다음부터 스스로 옮기고, 묶음 확인은 쌓인 것이 다섯 건 이상일 때만
0.2 위에 「빈 곳」을 채운 판이다. 0.2의 판정(계보로 최신 판정, 최종본은 고른 판의 바이트, 거울은 역할을 준 매체에만)은 그대로다.
0.3에서 넣은 것:
 1 껐다 켜도 이어짐(장치카드·색인·판 목록·원장을 기기의 엔진 자리에 남기고 다시 읽음, 망가지면 색인을 다시 만듦)
 2 자산·판·사본의 가름(ID-11~16)   3 형식군 열둘과 낱말 경계   4 자리 기억(PL-11·12)
 5 묶음·갈래 발급(PL-04~08)        6 모드·매체 역할·묶기의 제시(proposals · accept)
 7 자리 배정과 이름(FN-03 · NM-01~07, rename_policy)   8 프로젝트 검사 아홉(8장)
 9 중복의 내용·폴더째·압축 겹       10 원장 줄의 원인·결과 칸과 사건 등록부   11 대시보드·올릴 내용의 새 칸
재검수 K(0.2를 다시 깨 본 결과)의 높음 가운데 이 판에서 함께 고친 것: K-01 재시작 · K-02 원장 한 사슬과 파일 맞대기 · K-03·04 되돌림과 다시 만든 글 ·
 K-05 받은 계보 · K-06·07 최종본의 자리 · K-08 복구 뒤 자동 실행 · K-09 꾸러미·시스템 파일 · K-10 빠진 보호 등급을 보임 · K-11 무료 층의 문 ·
 K-12 쓰지 못할 때 · K-13 읽지 못하는 파일 · K-14 위험 매체 풀기 · K-15 등급은 낮아지지 않음
최상위 목표: 사용자는 실행하고 관리만 한다. 엔진이 「정하는 일」은 자동 / 제시 / 한 번 가운데 하나다.
바꾸지 않는 원칙: 내용을 고치지 않고 지우지 않는다. 옮김·이름 바꿈은 판 목록과 원장에 남기고 복구로 되돌린다.
모듈: CLS · AAD · OPT · SEC · SCT · LNK · SYN · LED · DSH · CLD · PJT(이 판에서 더함).  표준 라이브러리만 쓴다."""
import os, re, json, hashlib, hmac, shutil, difflib, time, unicodedata, zipfile, functools

POLICY, APP_VER = "HiDAM-STD-1.0(작업)", "HDA-0.4"
FP_LEN = 16                                   # 지문에 쓰는 해시 앞자리 수(ID-15: 맞대는 것은 언제나 전체 해시)
PROTECT_EXT = {"key", "pem", "cer", "crt", "der", "pfx", "p12"}
INSTALL_EXT = {"exe", "msi", "apk", "dll", "bat", "ps1"}
FONT_EXT = {"ttf", "otf"}
IMG = {"jpg", "jpeg", "png", "gif", "bmp", "tif", "heic", "webp", "raw", "svg"}
VID = {"mp4", "mov", "avi", "mkv", "wmv", "webm"}
AUD = {"mp3", "wav", "m4a", "flac", "ogg"}
DOC = {"pdf", "doc", "docx", "hwp", "hwpx", "xls", "xlsx", "csv", "ppt", "pptx", "txt", "md"}
ARC = {"zip", "rar", "7z", "alz", "egg", "tar", "gz", "iso"}
DSN = {"dwg", "dxf", "psd", "ai", "indd", "fig", "skp", "stl"}
DEV = {"html", "css", "js", "ts", "json", "py", "java", "c", "sql"}
SYS = {"db", "sqlite", "bak", "log", "tmp", "ini", "lnk"}
TEXT = {"txt", "md", "csv", "json", "py", "html", "css", "js", "sql"}
GROUPS = (("보호", PROTECT_EXT), ("문서", DOC), ("이미지", IMG), ("동영상", VID), ("오디오", AUD), ("도면·디자인", DSN),
          ("압축·디스크 이미지", ARC), ("실행·설치·글꼴", INSTALL_EXT | FONT_EXT), ("언어·개발", DEV), ("데이터·시스템", SYS))
W_CAREER = {"이력서": "02.01", "경력": "02.01", "포트폴리오": "02.03", "자격증": "01.03", "면허": "01.03",
            "졸업": "01.02", "성적": "01.02", "여권": "01.01", "신분증": "01.01", "증명사진": "01.01"}
W_GOV = {"세금": "07.01", "신고": "07.01", "보험": "07.02", "판결": "07.03", "민원": "07.04",
         "등본": "01.04", "증명원": "01.04"}
TAILS = ("사본", "원본", "스캔", "스캔본", "증명서", "증명", "기술서", "확인서", "신청서", "신고서", "서류", "내역", "내역서",
         "영수증", "표", "증", "본", "양식", "초안", "료", "문", "서")     # 낱말 뒤에 붙어도 같은 낱말로 보는 꼬리말(낱말표의 한 칸)
GRADE_WORDS = (("주민", ("등록", "등록증", "등록번호", "번호", "등록등본", "등록초본", "등록표")), ("여권", TAILS), ("계좌", ("번호", "사본", "내역", "개설")),
               ("비밀", ("번호",)), ("신분증", TAILS))
ORG_TAILS = ("건설", "전자", "산업", "상사", "은행", "병원", "대학교", "학교", "연구소", "재단", "협회", "공사", "공단", "시청", "구청", "센터", "주식회사")
PLACEHOLDER = ("새 문서", "제목 없음", "무제", "untitled", "new document", "새 텍스트 문서", "document", "noname", "새 파일", "new file")
AREA_TAG = {"00": "D1", "01": "D3", "02": "D1", "03": "D2", "04": "D2", "05": "D1", "06": "D1", "07": "D2",
            "08": "D0", "09": "D1", "10": "D4", "97": "D3", "98": "D1", "99": "D1"}
AREA_NAME = {"00": "관리", "01": "신분_학위_자격", "02": "경력_구직", "03": "근무_프로젝트", "04": "사업_창업", "05": "학습_연구", "06": "개인_가족",
             "07": "행정_세무_법무", "08": "자료실", "09": "설치_소프트웨어", "10": "관계_네트워크", "97": "원천보관", "98": "임시", "99": "기타"}
CAT_NAME = {"00.04": "보호자산대장", "01.01": "신분증_증명사진", "01.02": "학위_졸업_성적", "01.03": "자격증_면허_수료증", "01.04": "증명서",
            "02.01": "이력서_경력기술서", "02.02": "지원_채용", "02.03": "포트폴리오_경력증빙", "03.90": "여러_조직_공통", "03.99": "조직_미상",
            "05.04": "연구_학습_노트", "06.01": "사진_영상", "06.08": "가족", "06.10": "화면_캡처_녹화",
            "07.01": "세금_신고", "07.02": "고용_사회보험", "07.03": "법원_법무", "07.04": "민원_공공기관",
            "08.01": "문서", "08.02": "도서_아티클", "08.03": "동영상", "08.04": "이미지", "08.05": "음악_오디오",
            "09.01": "운영체제_드라이버", "09.02": "업무_오피스", "09.05": "글꼴_디자인_자원",
            "97.01": "휴대폰_백업", "97.04": "메신저_받은_파일", "97.05": "다운로드_원본", "97.06": "대량_이관", "99.01": "판정_대기", "99.02": "형식_미상"}
STEM_CUT = re.compile(r"(\s*-\s*복사본|\s*\(\d+\)|[_\- ](최종|수정|final|v\d+))$", re.I)   # 날짜·번호는 떼지 않는다(다른 파일을 한 판으로 묶지 않게)
STAGES = {"00": "색인", "01": "기준원칙", "02": "사례", "03": "설정안", "04": "설계안", "05": "수행안", "06": "수행결과",
          "07": "품질검수", "08": "시범테스트", "09": "감리", "10": "관리"}
GAL_PHASE = {"01": 1, "02": 1, "03": 1, "04": 2, "05": 2, "06": 3, "08": 3, "07": 4, "09": 4}   # 갈래에 기록이 놓이면 닿은 국면(PH0 관리·PH5·6은 사용자·확장판이 줌)
BTYPES = {"00": "보관 묶음", "10": "만들기", "20": "돌리기", "30": "알아보기", "40": "사고팔기·맺기", "50": "치르기", "60": "받기", "70": "알리기", "90": "묶음의 묶음", "99": "정하지 못함"}
# 확장판(MO-08): 뼈대의 코드를 바꾸지 않는 값 꾸러미. (갈래, 보이는 이름, 이 국면부터 있어야 함). 공공 정보화 사업의 목록은 넣지 않았다(원문 확인 전, 결-18).
PACKS = {"기본": [("01", "기준원칙(지켜야 할 것)", 1), ("03", "설정안(무엇을 할지)", 2), ("04", "설계안(어떻게 만들지)", 3),
                  ("05", "수행안(어떻게 해 나갈지)", 3), ("06", "수행결과(해서 나온 것)", 4), ("07", "품질검수(안에서 확인한 것)", 5)],
         "생활": [("01", "조건·약속(계약서)", 1), ("02", "알아본 것(견적)", 2), ("05", "할 일", 3), ("06", "한 것", 4), ("07", "확인(잔금·전입 등)", 5)]}
LIFE_WORDS = ("이사", "결혼", "여행", "돌잔치", "장례", "입학", "행사")
CAUSES = ("꽂음", "바뀜", "때 됨", "사용자가 누름", "규칙", "정책 판 올림", "복구", "정합", "사용자 결정")
RESULTS = ("됨", "멈춤", "거절", "실패")
RC = {"RC-01": "무료 층", "RC-02": "미등록 매체", "RC-03": "위험 표시", "RC-04": "세션 겹침", "RC-05": "매체 자리 없음", "RC-06": "대량 변경",
      "RC-07": "해시 불일치", "RC-08": "복구 한도", "RC-09": "그 판이 없음", "RC-10": "보호 등급", "RC-11": "첫 미러링 확인 전",
      "RC-12": "열려 있거나 옮기지 못함", "RC-13": "경로 한도", "RC-14": "기능 닫힘(구독·한 번 적용 아님)", "RC-15": "일반 모드(사용자 구조 그대로)",
      "RC-16": "원장 사슬 끊김", "RC-17": "색인 파일 망가짐", "RC-18": "거울 역할이 아님", "RC-19": "꾸러미·보호 자산·기준 자리", "RC-20": "매체 사용 불가",
      "RC-21": "사용자 폴더 밖", "RC-22": "자산을 찾지 못함", "RC-23": "사용자가 골라야 함(갈라짐·계보 없음)", "RC-24": "매체에 쓰지 못함(공간 부족 등)",
      "RC-25": "받은 계보가 이 기기의 계보와 어긋남", "RC-26": "없는 자리 코드", "RC-27": "같은 자리의 내용이 옛 날짜이거나 크게 다름 — 같은 문서의 판인지 확인",
      "RC-28": "금고 열쇠 없음 또는 잠그지 못함"}
# 사건 등록부. 0.2의 번호는 그대로이고 0.3은 이어서 준다(쓴 번호를 다른 뜻으로 다시 쓰지 않는다, CD-02 · HDA-R1).
EV = {("CLS", "판정"): "CLS-E01", ("CLS", "자리 받음"): "CLS-E02", ("CLS", "자리 배정"): "CLS-E03", ("CLS", "이름 붙임"): "CLS-E04",
      ("CLS", "배정 보류"): "CLS-E05", ("CLS", "자리 기억"): "CLS-E06", ("CLS", "묶음 발급"): "CLS-E07", ("CLS", "묶음 대응"): "CLS-E08",
      ("CLS", "자산 가름"): "CLS-E09", ("CLS", "자산 맞춤"): "CLS-E10", ("CLS", "배정 거절"): "CLS-E11", ("CLS", "사용자 규칙"): "CLS-E12", ("CLS", "범주 배움"): "CLS-E13",
      ("AAD", "격리 표시"): "AAD-E01", ("AAD", "주의 표시"): "AAD-E02",
      ("SCT", "미등록 매체"): "SCT-E01", ("SCT", "세션 거절"): "SCT-E02", ("SCT", "모드 바꿈"): "SCT-E03", ("SCT", "매체 역할"): "SCT-E04",
      ("SCT", "제안"): "SCT-E05", ("SCT", "제안 받아들임"): "SCT-E06", ("SCT", "제안 물림"): "SCT-E07", ("SCT", "정책 판 올림"): "SCT-E08",
      ("SCT", "모드 거절"): "SCT-E09", ("SCT", "이름 규칙 바꿈"): "SCT-E10", ("SCT", "역할 거절"): "SCT-E11",
      ("LNK", "매체 연결"): "LNK-E01", ("LNK", "매체 분리"): "LNK-E02", ("LNK", "자리 없음"): "LNK-E03", ("LNK", "계보 받음"): "LNK-E04", ("LNK", "계보 거절"): "LNK-E05", ("LNK", "보지 못함"): "LNK-E06",
      ("SYN", "정합 판정"): "SYN-E01", ("SYN", "최종본"): "SYN-E02", ("SYN", "미러링"): "SYN-E03", ("SYN", "자동 실행"): "SYN-E04",
      ("SYN", "자동 미러링 멈춤"): "SYN-E05", ("SYN", "거절"): "SYN-E06", ("SYN", "사용자 결정"): "SYN-E07", ("SYN", "계보 잇지 않음"): "SYN-E08", ("SYN", "미러링 멈춤"): "SYN-E09", ("SYN", "판 확인 필요"): "SYN-E10", ("SYN", "금고 거울"): "SYN-E11", ("SYN", "금고 거울 멈춤"): "SYN-E12",
      ("LED", "판 보관"): "LED-E01", ("LED", "복구"): "LED-E02", ("LED", "복구 한도"): "LED-E03", ("LED", "복구 실패"): "LED-E04",
      ("LED", "원장 이어 읽음"): "LED-E05", ("LED", "색인 다시 만듦"): "LED-E06", ("LED", "원장 끝줄 고침"): "LED-E07", ("LED", "새 사슬"): "LED-E08",
      ("LED", "자리 판 보관"): "LED-E09",
      ("PJT", "국면 바뀜"): "PJT-E01", ("PJT", "기준선"): "PJT-E02", ("PJT", "검수"): "PJT-E03", ("PJT", "감리"): "PJT-E04", ("PJT", "지적·조치"): "PJT-E05",
      ("PJT", "증적 묶음"): "PJT-E06", ("PJT", "검사 결과"): "PJT-E07", ("PJT", "잇는 줄"): "PJT-E08", ("PJT", "바깥 번호"): "PJT-E09",
      ("PJT", "산출물 번호"): "PJT-E10", ("PJT", "요구"): "PJT-E11"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def ver_id(data):
    """판 식별자(VER_ID) = 내용 해시 앞 16 + 크기. 같은 내용이면 어디에 있든 같은 값."""
    return sha(data)[:FP_LEN] + "-%d" % len(data)


asset_id = ver_id      # 자산 식별자는 그 자산의 「첫 판」의 지문이다(ID-11). 첫 판에서는 두 값이 같다


def decode(data):
    """글자 문서 읽기. 못 읽으면 None(예외를 내지 않는다). (글, 부호, 줄바꿈)"""
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            s = data.decode(enc)
            return s, enc, ("\r\n" if "\r\n" in s else "\n")
        except UnicodeDecodeError:
            continue
    return None


def _ks(key, nonce, n):
    out, i = bytearray(), 0
    while len(out) < n:
        out += hmac.new(key, b"enc" + nonce + i.to_bytes(8, "big"), hashlib.sha256).digest()
        i += 1
    return bytes(out[:n])


def vault_seal(key, name, data):
    """금고 한 칸: HV1 · 덧값 16 · 암호문 · 확인값 32. 이름도 안에 잠근다(바깥 파일 이름은 해시)."""
    nonce = os.urandom(16)
    pt = name.encode("utf-8")
    pt = len(pt).to_bytes(4, "big") + pt + data
    ct = bytes(a ^ b for a, b in zip(pt, _ks(key, nonce, len(pt))))
    return b"HV1" + nonce + ct + hmac.new(key, b"mac" + nonce + ct, hashlib.sha256).digest()


def vault_open(key, blob):
    """잠근 칸을 연다. 확인값이 맞지 않으면 None(바뀌었거나 다른 열쇠)."""
    if blob[:3] != b"HV1" or len(blob) < 3 + 16 + 4 + 32:
        return None
    nonce, ct, tag = blob[3:19], blob[19:-32], blob[-32:]
    if not hmac.compare_digest(tag, hmac.new(key, b"mac" + nonce + ct, hashlib.sha256).digest()):
        return None
    pt = bytes(a ^ b for a, b in zip(ct, _ks(key, nonce, len(ct))))
    n = int.from_bytes(pt[:4], "big")
    try:
        return pt[4:4 + n].decode("utf-8"), pt[4 + n:]
    except UnicodeDecodeError:
        return None


def now_z():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Ledger:
    """LED: 사건 원장(해시 사슬). 사슬이 끊기면 그 뒤 동작을 멈춘다(K-02).
    한 줄의 꼴(코드 분류 체계 6장): 사건 식별자 · 시각 · 사건 코드 · 행위자 · 원인 · 대상 · 결과(+까닭 코드) · 정책 판 · 앱 판 · 앞 줄 해시 · 이 줄 해시."""

    def __init__(self, dev="", path=None):
        self.rows, self.dev, self.path = [], dev, path
        self.genesis = self.head = "0" * 64
        self.base, self.state = 0, "정상"                # base: 새 사슬을 시작했을 때 앞 사슬이 쓴 순번(사건 식별자를 다시 쓰지 않게)
        self.cause, self.actor, self.policy, self.fsize = "사용자가 누름", "엔진", POLICY, 0

    def follow(self, full=False):
        """같은 기기 폴더에 엔진이 둘 떠서 다른 엔진이 원장에 이어 썼으면 그 줄을 읽어 한 사슬로 잇는다(순번이 겹치지 않게).
        파일이 내가 아는 줄과 다르면(손으로 고침·잘림) 끊김으로 둔다. full=True는 줄마다 해시를 다시 셈해 맞댄다."""
        if not self.path or self.state == "끊김":
            return
        try:
            size = os.path.getsize(self.path) if os.path.exists(self.path) else 0
            mt = sha(open(self.path, "rb").read()) if size else ""     # 파일 내용의 해시(Windows는 고친 시각의 눈금이 굵어 시각으로는 같은 크기의 고침을 못 봄)
            if size == self.fsize and mt == getattr(self, "fmt", None) and not full:
                return
            full = full or bool(self.rows)
            lines = [x for x in open(self.path, "rb").read().decode("utf-8", "replace").split("\n") if x] if size else []
            rows = [json.loads(x) for x in lines]
        except (OSError, ValueError):
            self.state = "끊김"
            return
        n = len(self.rows)
        if len(rows) < n or any(rows[i].get("h") != self.rows[i]["h"] or (full and self._h(rows[i]) != rows[i].get("h")) for i in range(n)):
            self.state = "끊김"
            return
        prev = self.head
        for r in rows[n:]:
            if r.get("prev") != prev or self._h(r) != r.get("h"):
                self.state = "끊김"
                return
            prev = r["h"]
        self.rows += rows[n:]
        self.head, self.fsize, self.fmt = prev, size, mt

    def add(self, mod, act, actor=None, cause=None, res="됨", rc=None, **kw):
        self.follow()
        if not self.verify():
            raise RuntimeError("원장 사슬 끊김 — 동작 중지")
        code = EV[(mod, act)]                            # 등록부에 없는 사건은 적지 못한다(코드 없는 사건 0)
        assert res in RESULTS and (cause or self.cause) in CAUSES and (rc is None or rc in RC)
        n = self.base + len(self.rows) + 1
        row = dict(seq=n, eid="%s#%d" % (self.dev, n), at=now_z(), dev=self.dev, actor=actor or self.actor, code=code, mod=mod, act=act,
                   cause=cause or self.cause, res=res, rc=rc, policy=self.policy, app=APP_VER, prev=self.head, **kw)
        row["h"] = self._h(row)
        self.rows.append(row)
        self.head = row["h"]
        if self.path:                                    # 기기 안 파일로도 남긴다(한 줄에 한 사건)
            with open(self.path, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            self.fsize, self.fmt = os.path.getsize(self.path), sha(open(self.path, "rb").read())
        return row

    @staticmethod
    def _h(row):
        return sha(json.dumps({k: v for k, v in row.items() if k != "h"}, ensure_ascii=False, sort_keys=True).encode())

    def verify(self):
        if self.state == "끊김":
            return False
        prev = self.genesis
        for r in self.rows:
            if r["prev"] != prev or self._h(r) != r["h"]:
                return False
            prev = r["h"]
        return True

    def load(self):
        """다시 띄울 때 파일을 읽어 사슬을 잇는다. 돌려주는 값: 없음 · 이음 · 끝줄 고침 · 끊김. 예외를 내지 않는다."""
        if not self.path or not os.path.exists(self.path):
            return "없음"
        try:
            lines = open(self.path, "rb").read().decode("utf-8", "replace").split("\n")
        except OSError:
            self.state = "끊김"
            return "끊김"
        if lines and lines[-1] == "":
            lines.pop()
        rows, torn, bad = [], False, False
        for i, ln in enumerate(lines):
            try:
                r = json.loads(ln)
                if not (isinstance(r, dict) and "h" in r and "prev" in r):
                    raise ValueError
                rows.append(r)
            except ValueError:
                if i == len(lines) - 1:
                    torn = True                          # 쓰다 끊긴 마지막 줄 하나는 버리고 잇는다
                else:
                    bad = True
                break
        if rows and rows[0].get("code") == "LED-E08":   # 새 사슬의 첫 줄은 앞 사슬 파일의 해시를 앞 줄 해시로 가진다
            self.genesis, self.base = rows[0]["prev"], rows[0]["seq"] - 1
        self.rows = rows
        self.fsize, self.fmt = os.path.getsize(self.path), sha(open(self.path, "rb").read())
        self.head = rows[-1]["h"] if rows else self.genesis
        if bad or not self.verify():
            self.state = "끊김"
            return "끊김"
        if torn:
            keep = self.path + ".끝줄-%d" % int(time.time())
            shutil.copy2(self.path, keep)                # 고치기 전의 파일은 그대로 남긴다
            with open(self.path, "w", encoding="utf-8", newline="\n") as f:
                f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
            self.fsize = os.path.getsize(self.path)
            return "끝줄 고침"
        return "이음" if rows else "없음"

    def restart(self):
        """끊긴 원장을 지우지 않고 따로 두고, 그 파일의 해시를 첫 줄에 물린 새 사슬을 시작한다(사용자가 한 번 받아들인 뒤에만)."""
        old_sha, n_old, keep = "0" * 64, self.base + len(self.rows), None
        if self.path and os.path.exists(self.path):
            raw = open(self.path, "rb").read()
            old_sha, n_old = sha(raw), max(n_old, self.base + raw.count(b"\n"))
            keep = self.path + ".끊김-%d" % int(time.time())
            os.replace(self.path, keep)
        self.rows, self.genesis, self.head, self.base, self.state, self.fsize = [], old_sha, old_sha, n_old, "정상", 0
        return self.add("LED", "새 사슬", actor="사용자", cause="사용자 결정", old_file=os.path.basename(keep) if keep else None, old_sha=old_sha)


def norm(s):
    """이름을 맞대기 전에 같은 모양으로 고른다(운영체제마다 한글 자모를 다르게 적는다, TP-07 · CD-08)."""
    return unicodedata.normalize("NFC", s)


def ext_of(name):
    return name.rsplit(".", 1)[1].lower() if "." in name and not name.startswith(".") or name.count(".") > 1 else ""


def stem_cut(name):
    """이름 줄기(글자 모양 그대로): 꾸밈말과 번호를 뗀 이름. 떼고 나서 두 글자 미만이면 떼지 않은 이름을 쓴다."""
    name = norm(name)
    base = name.rsplit(".", 1)[0] if "." in name else name
    cut, prev = base, None
    while prev != cut:
        prev, cut = cut, STEM_CUT.sub("", cut)
    cut = cut.strip()
    return cut if len(cut) >= 2 else base


def stem_of(name):
    return stem_cut(name).lower()


def has_shot_info(data):
    return b"Exif" in data[:65536]


_TOK = re.compile(r"[가-힣]+|[A-Za-z]+")
_EDGE = r"[가-힣A-Za-z0-9]"


def has_word(text, w, tails=TAILS):
    """낱말 경계로 본다: 띄어쓰기·밑줄·숫자·기호·글자 종류가 바뀌는 곳이 경계다. 낱말 뒤에는 꼬리말표의 말만 붙을 수 있다.
    「졸업여행」은 졸업이 아니고 「전세금」은 세금이 아니며 「성적표」「여권사본」은 맞다."""
    w = w.lower()
    for t in _TOK.findall(norm(text).lower()):
        if t == w or (t.startswith(w) and t[len(w):] in tails):
            return True
    return False


def has_name(text, name):
    """조직·사업·프로젝트 이름: 앞뒤가 글자·숫자가 아닐 때만 그 이름으로 본다."""
    return re.search("(?<!%s)%s(?!%s)" % (_EDGE, re.escape(norm(name).lower()), _EDGE), norm(text).lower()) is not None


def gal_of(folder):
    """폴더 이름에서 갈래(00~10)를 읽는다. 마디 번호 `NN_`(앞 마디를 물려받은 `AA_NN_`의 마지막 마디)이거나 갈래 이름이 온전한 낱말일 때만.
    「사례금」「관리비」「감리교회」는 갈래가 아니다."""
    f = norm(folder)
    m = re.match(r"^((?:\d\d_)*)(\d\d)_(.+)$", f)
    if m and m.group(2) in STAGES:
        return m.group(2)
    toks = _TOK.findall(f)
    for k, v in STAGES.items():
        if v in toks:
            return k
    return None


def gal_named(folder):
    """갈래 이름이 온전한 낱말로 들어 있는 폴더(모드·프로젝트 후보를 뽑을 때는 번호만으로 보지 않는다)."""
    toks = _TOK.findall(norm(folder))
    return next((k for k, v in STAGES.items() if v in toks), None)


def in_ref(rel):
    """기기의 기준 자리(엔진이 최종본을 두는 곳) 안인가. 운영체제가 이름을 다른 자모 모양으로 돌려줘도 같게 본다."""
    return norm(rel).startswith("기준자리/")


def in_package(rel):
    """꾸러미(JR-2) 폴더 모양 안인가: 기기 백업·카메라 폴더, 메신저 받은 파일 폴더. 꾸러미는 폴더째 두고 안의 파일을 낱낱이 맞추지 않는다."""
    fo = [p.lower() for p in norm(rel).split("/")[:-1]]
    return any(f in ("dcim", "phone data") or f.startswith("backup") or has_word(f, "백업", ()) or "kakaotalk" in f or "받은 파일" in f for f in fo)


def fgroup(e):
    if not e:
        return "확장자 없음"
    return next((g for g, s in GROUPS if e in s), "기타")


def real_format(data):
    """파일 머리로 본 실제 형식(아는 것만)."""
    for e, mg in (("pdf", b"%PDF"), ("png", b"\x89PNG"), ("jpg", b"\xff\xd8"), ("gif", b"GIF8"), ("zip", b"PK\x03\x04")):
        if data[:16].lstrip().startswith(mg) or data.startswith(mg):
            return e
    return None


RANK_ORD = {"JR-1": 1, "사용자 규칙": 1.5}


def rank_ord(rank):
    if rank in RANK_ORD:
        return RANK_ORD[rank]
    m = re.match(r"JR-(\d+)", rank or "")
    return int(m.group(1)) if m else 9


# ---------- CLS · SEC ----------
def classify(rel, data, orgs=(), user_rules=None, projects=(), bundles=()):
    """판정 순위 JR-1~8과 사진·영상 PV. 돌려주는 값은 세 축을 다 담는다(용도 구별):
    code 표준 자리 · conf 확신 · rank 순위 · project 프로젝트 묶음과 갈래 · folder 사용자 구조의 자리 · bundle 받아들인 묶음 · group 형식군."""
    parts = norm(rel).replace("\\", "/").split("/")
    name, fo, e = parts[-1], parts[:-1], ext_of(parts[-1])
    folders = [p.lower() for p in fo]
    out = dict(folder="/".join(fo) or "(맨 위)", project=None, bundle=None, gal=None, group=fgroup(e))
    for pname, pcode in projects:                      # 프로젝트 축(주어진 이름): 폴더 이름이 그 이름일 때
        i = next((i for i, f in enumerate(fo) if has_name(f, pname)), None)
        if i is not None:
            g = next((x for x in map(gal_of, fo[i + 1:]) if x), None)
            out.update(project="%s-%s" % (pcode, g or "xx"), gal=g)       # 갈래를 읽지 못하면 「xx」(00 색인으로 적지 않는다)
            break
    bsig, cur = None, "/".join(folders)
    for b in sorted(bundles, key=lambda b: -len(b["folder"])):     # 받아들인 묶음(프로젝트·조직): 가장 깊은 폴더가 앞선다
        if cur == b["folder"] or cur.startswith(b["folder"] + "/"):
            if b["kind"] == "프로젝트" and not out["project"]:
                g = next((x for x in map(gal_of, fo[b["folder"].count("/") + 1:]) if x), None)
                out.update(project="%s-%s" % (b["id"], g or "xx"), gal=g)
            if not bsig:
                bsig = b["code"]
                out["bundle"] = b["id"]

    def done(code, conf, rank):
        out.update(code=code, conf=conf, rank=rank)
        return out
    if e in PROTECT_EXT or "npki" in folders:          # JR-1 보호는 사용자 규칙보다 앞선다(CP-08)
        return done("00.04", "높음", "JR-1")
    key = stem_of(name) + "." + e
    if user_rules and key in user_rules:
        return done(user_rules[key], "높음", "사용자 규칙")
    if any(f in ("dcim", "phone data") or f.startswith("backup") or has_word(f, "백업", ()) for f in folders):
        return done("97.01", "높음", "JR-2")
    if any("kakaotalk" in f or "받은 파일" in f for f in folders):
        return done("97.04", "높음", "JR-2")
    if any(f in ("downloads", "다운로드") for f in folders) and not (e in IMG or e in VID):
        return done("97.05", "높음", "JR-2")
    sig = [(bsig, "JR-3")] if bsig else []
    if not sig:
        for o, code in orgs:
            if any(has_name(f, o) for f in fo) or has_name(name, o):
                sig.append((code, "JR-3"))
                break
    for w, c in W_CAREER.items():
        if has_word(name, w):
            sig.append((c, "JR-4"))
            break
    for w, c in W_GOV.items():
        if has_word(name, w):
            sig.append((c, "JR-5"))
            break
    if sig:                                            # 첫 순위의 자리를 쓰고, 뒤 신호가 같은 영역이면 높음·다르면 중간. 받아들인 묶음은 확정 신호다(JR-9)
        code, rank = sig[0]
        return done(code, "높음" if bsig or (len(sig) > 1 and all(s[0][:2] == code[:2] for s in sig)) else "중간", rank)
    rf = real_format(data)
    if rf and e in ("pdf", "png", "jpg", "jpeg", "gif", "zip") and rf != e.replace("jpeg", "jpg"):
        e = rf                                         # 확장자와 실제 형식이 다르면 자리는 실제 형식으로 준다(표시는 AAD의 「주의」)
        out["group"] = fgroup(e)
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
    if e in FONT_EXT:
        return done("09.05", "높음", "JR-7")
    if e in INSTALL_EXT:
        return done("09.02", "높음", "JR-7")
    if e in DOC:
        return done("08.01", "중간", "JR-6")
    if e in ARC:
        return done("97.06", "중간", "JR-6")           # 압축·디스크 이미지: 꾸러미로 보고 원천보관의 대량 이관에(안은 풀지 않고 목록만)
    if e in DSN:
        return done("09.05", "중간", "JR-6")           # 도면·디자인: 묶음 신호가 없으면 디자인 자원
    if e in DEV:
        return done("05.04", "중간", "JR-6")           # 언어·개발: 묶음 신호가 없으면 연구·학습 노트
    if e in SYS:
        return done("99.01", "낮음", "JR-8")           # 데이터·시스템: 건드리지 않고 목록만
    return done("99.02", "낮음", "JR-8")               # 확장자 없음 · 표에 없는 형식(기타)


def sec_grade(code, name):
    """SEC: 영역 기본 등급에서 시작해 올리기만 한다(SV-01·02). 보호 자산은 D3 아래로 내려가지 않는다.
    등급을 올리는 낱말도 낱말 경계로 본다(「입주민 공지」「주민센터 안내문」「비밀의 숲」은 올리지 않는다. 잘못 올리면 자동 정합·거울에서 조용히 빠진다)."""
    name = norm(name)
    g = "D3" if code == "00.04" else AREA_TAG.get(code[:2], "D1")
    if ext_of(name) in PROTECT_EXT or any(has_word(name, w, t) for w, t in GRADE_WORDS):
        g = max(g, "D3")
    return g


# ---------- 이름(NM) ----------
_BAD = re.compile(r'[<>:"/\\|?*~\x00-\x1f]')
_RESERVED = {"con", "prn", "aux", "nul"} | {"com%d" % i for i in range(1, 10)} | {"lpt%d" % i for i in range(1, 10)}


def clean_name(stem):
    """NM-04: 운영체제 넷이 막는 글자의 합집합과 물결표를 빼고, 앞뒤의 빈칸과 마침표를 떼고, 새 이름에는 가운뎃점을 쓰지 않는다."""
    s = _BAD.sub("_", norm(stem)).replace("·", "_").strip(" .")
    s = re.sub(r"_{2,}", "_", s)
    if s.lower() in _RESERVED:
        s += "_"
    return s or "이름없음"


def read_ver(stem):
    """이름에서 판 번호를 읽는다. (제목, 날짜 YYMMDD 또는 None, 판, 작업본인가) / 읽지 못하면 None."""
    m = re.match(r"^(.*)-(\d{6})_(\d+\.\d+)(_작업)?$", stem)
    if m:
        return m.group(1), m.group(2), m.group(3), bool(m.group(4))
    m = re.match(r"^(.*?)[_\- ]?[vV](\d+)(?:\.(\d+))?(_작업)?$", stem) or re.match(r"^(.*?)_(\d+)\.(\d+)(_작업)?$", stem)
    if m and m.group(1):
        return m.group(1), None, "%s.%s" % (m.group(2), m.group(3) or "0"), bool(m.group(4))
    return None


def std_name(name, mtime, folder="", cat=""):
    """표준 이름(NM-01·02·04). (새 이름, 까닭) — 바꿀 것이 없으면 (원래 이름, None).
    판이 있는 문서: 제목-YYMMDD_판[_작업].확장자 / 판이 없는 것: 원래 이름을 지킴 / 엔진이 이름을 줄 때(자리만 채운 이름): YYYYMMDD_제목."""
    name = norm(name)
    e = ext_of(name)
    stem = name[:-(len(e) + 1)] if e else name
    dot = ("." + e) if e else ""
    day = time.strftime("%Y%m%d", time.localtime(mtime))          # 이름에 싣는 날짜는 사용자의 시각(그 기기의 시간대)이다
    if e in DOC:
        v = read_ver(stem)
        if v:
            title, ymd, ver, wip = v
            md = re.search(r"(?<!\d)(20\d{2})[.\-_]?(\d{2})[.\-_]?(\d{2})(?!\d)", title)
            if md and not ymd:
                ymd, title = md.group(1)[2:] + md.group(2) + md.group(3), title[:md.start()] + title[md.end():]
            title = clean_name(re.sub(r"[\s\-]+", "_", title.strip(" _-")))
            new = "%s-%s_%s%s%s" % (title, ymd or day[2:], ver, "_작업" if wip else "", dot)
            return (new, "판이 있는 문서(NM-01)") if new != name else (name, None)
    if re.sub(r"\s*\(\d+\)$", "", stem).strip().lower() in PLACEHOLDER:
        title = clean_name(re.sub(r"\s+", "_", (folder.split("/")[-1] if folder and folder != "(맨 위)" else "") or cat or "파일"))
        return "%s_%s%s" % (day, title, dot), "자리만 채운 이름 — 엔진이 이름을 줌(NM-02)"
    new = clean_name(stem) + dot
    return (new, "쓰지 않는 글자(NM-04)") if new != name else (name, None)


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


# ---------- OPT: 내용 해시 · 폴더 서명 · 압축 목록 ----------
def content_hash(data, e):
    """IX-04 내용 해시(글자 문서만): 부호·줄바꿈·공백의 차이를 고른 뒤의 해시. 글자 문서가 아니면 None."""
    if e not in TEXT:
        return None
    t = decode(data)
    if not t:
        return None
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in t[0].replace("﻿", "").splitlines()]
    return sha("\n".join(ln for ln in lines if ln).encode("utf-8"))


def zip_listing(path, limit=64 * 1024 * 1024):
    """압축 안은 풀지 않고 목록과 해시 집합으로만 적는다. 너무 크거나 못 읽으면 None."""
    try:
        with zipfile.ZipFile(path) as z:
            infos = [i for i in z.infolist() if not i.is_dir()]
            if sum(i.file_size for i in infos) > limit:
                return None
            out = {}
            for i in infos:
                with z.open(i) as f:
                    b = f.read(limit + 1)
                if len(b) > limit:
                    return None
                out[i.filename] = sha(b)
            return out
    except (zipfile.BadZipFile, OSError, RuntimeError, NotImplementedError, ValueError):
        return None


def folder_sets(index):
    """IX-12 폴더 서명의 바탕: 폴더마다 그 아래(아래 폴더까지) 파일의 전체 해시 집합. 빈 파일은 뺀다."""
    out = {}
    for rel, it in index.items():
        if not it["size"]:
            continue
        parts = rel.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            out.setdefault("/".join(parts[:i]), set()).add(it["hash"])
    return out


# ---------- 매체 ----------
ROLES = ("작업", "보관", "프로젝트", "거울", "원천")
ENGINE_DIRS = ("_HiDAM", "_HiDAM_거울", "_HiDAM_보류함", "_HiDAM_금고")      # 엔진이 만든 자리. 이름이 꼭 이것일 때만 훑기에서 뺀다(「_HiDAM_x」에 숨긴 파일은 본다)
JUNK = ("desktop.ini", "thumbs.db", ".ds_store")


def recommend_role(index):
    """RL-04: 처음 꽂은 매체를 훑어 역할을 권한다. (역할, 범위, 까닭)"""
    rels = list(index)
    if not rels:
        return "거울", None, "매체가 비어 있음"
    cam = sum(1 for r in rels if any(p.lower() in ("dcim", "camera") or re.match(r"^\d{3}[a-z_0-9]{5}$", p.lower()) for p in r.split("/")[:-1]))
    bak = sum(1 for r in rels if any(p.lower().startswith("backup") or p.lower() == "phone data" or has_word(p, "백업", ()) for p in r.split("/")[:-1]))
    if cam * 2 > len(rels):
        return "보관", "06.01", "카메라 폴더가 대부분(%d/%d)" % (cam, len(rels))
    if bak * 2 > len(rels):
        return "원천", None, "백업 폴더 모양이 대부분(%d/%d)" % (bak, len(rels))
    return "작업", None, "사람이 직접 쓰는 폴더 모양"


class Medium:
    """저장 매체 한 자리. 역할을 주면 매체가 곧 분류 체계의 한 층(폴더)이 된다.
    role 작업: 엇갈린 판이 나오는 곳 / 보관: scope에 적은 영역·범주의 집 / 프로젝트: scope에 적은 묶음의 집 / 거울: 비추는 곳 / 원천: 통째 보관(97).
    role을 주지 않으면 엔진이 권하고(RL-04), 받아들이기 전에는 작업(가장 손대지 않는 역할)으로 다룬다."""

    def __init__(self, dev_id, root, kind="외장", registered=True, role=None, scope=None):
        self.dev_id, self.root, self.kind, self.registered, self.plugged = dev_id, root, kind, registered, True
        self.role, self.role_given, self.scope = role or "작업", role is not None, scope
        self.index, self.blocked, self.flags, self.first_ok = {}, None, {}, False
        self.unseen, self.released = [], False             # 읽지 못한 파일(보지 못함) · 위험 표시 파일을 빼고 쓰기로 사용자가 정했는가

    def path(self, rel):
        return os.path.join(self.root, rel)

    def scan(self, anc=None):
        """목록·색인을 다시 만든다. 계보를 잇는 일은 엔진(_scan)이 한다. anc를 주면 0.2처럼 여기서 잇는다."""
        old, self.index, self.unseen, flags = self.index, {}, [], {}
        for d, _, fs in os.walk(self.root):
            if any(seg in ENGINE_DIRS for seg in os.path.relpath(d, self.root).split(os.sep)):
                continue
            for f in fs:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, self.root).replace("\\", "/")
                try:
                    with open(p, "rb") as fh:
                        data = fh.read()
                except OSError:
                    self.unseen.append(rel)              # 읽지 못하는 파일(깨진 바로가기·권한 없음)은 그 파일만 「보지 못함」으로 두고 나머지는 계속한다
                    continue
                h = sha(data)
                r = aad_check(rel, data)
                if r:
                    flags[rel] = list(r)
                self.index[rel] = dict(asset=None, ver=ver_id(data), hash=h, size=len(data), mtime=os.path.getmtime(p),
                                       stem=stem_of(f), ext=ext_of(f), dir=norm(os.path.dirname(rel)), chash=content_hash(data, ext_of(f)))
                if anc is not None and rel in old and old[rel]["hash"] != h:
                    anc.setdefault(h, set()).add(old[rel]["hash"])
        self.flags = flags
        return self.index


def op(cause, log=True, actor=None):
    """바깥에서 부르는 걸음의 틀: 원인(사건 한 줄의 「원인」 칸)을 정하고, 끝나면 상태를 기기에 남긴다."""
    def deco(fn):
        @functools.wraps(fn)
        def wrap(self, *a, **k):
            outer = self._depth == 0
            keep = (self.led.cause, self.led.actor, self._logging)
            if outer or cause in ("복구", "사용자 결정"):
                self.led.cause = cause(self, *a, **k) if callable(cause) else cause
            if actor and outer:
                self.led.actor = actor
            if outer:
                self._logging = log
                if self.led.cause in ("사용자 결정", "복구"):
                    self.touches += 1                     # 잣대: 사용자가 손댄 횟수(결정·복구를 한 번 누른 것이 1)
            self._depth += 1
            try:
                if outer and log:
                    self._flush()
                return fn(self, *a, **k)
            except RuntimeError as e:
                if not outer or "원장 사슬 끊김" not in str(e):
                    raise
                self.led.state = "끊김"
                self._propose("원장 새 사슬", "원장|끊김", "원장 사슬이 끊겼습니다. 끊긴 원장을 그대로 두고 새 사슬을 시작할까요", "새 사슬 시작",
                              "원장 파일이나 기억한 줄이 바뀌었습니다(K-02)", "원장에 적는 모든 걸음이 멈춘 채로 있습니다", who="한 번", log=False)
                return dict(ok=False, stopped="원장 사슬 끊김 — 동작 중지(새 사슬 확인 필요)")
            finally:
                self._depth -= 1
                self.led.cause, self.led.actor, self._logging = keep
                if outer:
                    self._save()
        return wrap
    return deco


# ---------- 엔진 ----------
class HiDAMApp:
    S_CARD, S_INDEX, S_VERS = "00.01_장치카드.json", "00.02_색인.json", "00.08_판목록.json"

    def __init__(self, device_root, device_id="DEV-PC-01", tier="구독", orgs=(), projects=(), mass_ratio=0.5, auto=True, mode=None,
                 rename_policy=None, once=False, profile="KR-P"):
        self.dev = Medium(device_id, device_root, "기기")
        self.home = os.path.join(device_root, "_HiDAM")
        os.makedirs(self.home, exist_ok=True)
        self.media, self.tier, self.orgs, self.projects = {}, tier, tuple(orgs), tuple(projects)
        self.led = Ledger(device_id, os.path.join(self.home, "00.02_원장.jsonl"))
        self.beta, self.once, self.profile = False, once, profile       # once: 기능 별도의 「한 번 적용」 문이 열렸는가
        self.mass_ratio, self.auto, self.user_rules = mass_ratio, auto, {}
        self.mode, self.mode_given = mode or "일반", mode is not None   # 모드를 주지 않으면 엔진이 권하고(MO-06) 그 전에는 일반(가장 손대지 않는 값)
        self.rename_policy = rename_policy or "보이기만"                 # 보이기만 | 모드 규칙 (NM-07: 대표님 결정 전의 기본값은 이름을 바꾸지 않음)
        self.anc, self.decided, self.finals = {}, {}, {}      # 계보(해시 → 앞 해시들) · 사용자 결정 · 최종본
        self.recover_count, self.last_auto, self.session_lock, self.skipped = {}, None, None, []
        self.assets, self.ver2asset, self.alias, self.path_asset, self.aseq = {}, {}, {}, {}, 0   # 자산 등록부 · 판 → 자산 · 옛 → 새 자산 · 자리 → 자산
        self.empties, self.splits_asked = [], {}
        self.place_mem = {}                                   # 자리 기억: 자산 → 자리·근거(PL-11·12)
        self.bundles, self.bseq, self.bmap, self.oseq = {}, {}, [], 0   # 묶음 · 범주별 마지막 번호 · 옛 → 새 대응표 · 조직 범주 순번
        self.props, self.pkeys, self.pseq = {}, {}, 0         # 제안(무엇을 · 권하는 답 · 까닭 · 받아들이지 않으면)
        self.known, self.held, self.suggest = None, [], {}    # 이미 본 자리(새 파일 가르기) · 배정 보류 · 옆에 보이는 표준 이름
        self.vmeta, self.mirror_order, self.busy, self.touches, self.no_place = {}, [], set(), 0, []
        self.last_wait, self._cur_items = None, None
        self.vault, self.learned, self._vault_want, self.placed = {}, [], {}, []   # 금고 거울(매체 → 자리 → 판 해시) · 받아들여 배운 범주(확신 중간)
        self._depth, self._logging, self._notes, self.boot = 0, False, [], []
        self.vers = os.path.join(self.home, "00.08_판보관")
        os.makedirs(self.vers, exist_ok=True)
        self._boot(mode, rename_policy)

    # ================= 1. 껐다 켜도 이어지게 =================
    def _read(self, name):
        p = os.path.join(self.home, name)
        if not os.path.exists(p):
            return None, "없음"
        try:
            d = json.loads(open(p, "rb").read().decode("utf-8"))
            if not isinstance(d, dict) or d.get("꼴") != name:
                raise ValueError
            return d, "읽음"
        except (ValueError, OSError):
            os.replace(p, p + ".망가짐-%d" % int(time.time()))   # 지우지 않고 따로 둔다
            return None, "망가짐"

    def _write(self, name, d):
        p = os.path.join(self.home, name)
        d = dict(d, 꼴=name, app=APP_VER, at=now_z())
        with open(p + ".tmp", "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(p + ".tmp", p)                         # 쓰다 꺼져도 앞 파일이 남는다

    def _boot(self, mode, rename_policy):
        st = self.led.load()
        card, s1 = self._read(self.S_CARD)
        idx, s2 = self._read(self.S_INDEX)
        vm, s3 = self._read(self.S_VERS)
        if card and st != "끊김" and card.get("led_n"):   # 원장이 뒤에서 잘렸는가(사슬은 맞아도 줄이 모자람): 장치카드에 적어 둔 마지막 줄과 맞댄다
            i = card["led_n"] - self.led.base
            if i > len(self.led.rows) or (0 < i <= len(self.led.rows) and self.led.rows[i - 1]["h"] != card["led_head"]):
                self.led.state, st = "끊김", "끊김"
        self.boot = [("원장", st), ("장치카드", s1), ("색인", s2), ("판 목록", s3)]
        if card:
            self.mode = mode or card["mode"]
            self.mode_given = self.mode_given or card["mode_given"]
            self.rename_policy = rename_policy or card["rename_policy"]
            self.user_rules, self.bundles, self.bseq, self.bmap, self.oseq = card["user_rules"], card["bundles"], card["bseq"], card["bmap"], card["oseq"]
            self.props = {int(k): v for k, v in card["props"].items()}
            self.pkeys, self.pseq, self.mirror_order, self.touches = card["pkeys"], card["pseq"], card["mirror_order"], card.get("touches", 0)
            self.no_place = card.get("no_place", [])
            self.vault, self.learned, self.placed = card.get("vault", {}), card.get("learned", []), card.get("placed", [])
            for d in card["media"]:
                m = Medium(d["dev"], d["root"], d["kind"], d["registered"], d["role"], d["scope"])
                m.first_ok, m.plugged, m.released = d["first_ok"], False, d.get("released", False)   # 다시 꽂기 전까지는 「뽑힘(마지막 본 값)」
                self.media[m.dev_id] = m
        if idx:
            self.dev.index = idx["dev_index"]
            for d, ix in idx["media_index"].items():
                if d in self.media:
                    self.media[d].index = ix
            self.anc = {k: set(v) for k, v in idx["anc"].items()}
            self.decided = {tuple(json.loads(k)): dict(hash=v["hash"], seen=set(v["seen"])) for k, v in idx["decided"].items()}
            self.finals, self.recover_count = idx["finals"], idx["recover_count"]
            self.assets, self.ver2asset, self.alias, self.path_asset, self.aseq = idx["assets"], idx["ver2asset"], idx["alias"], idx["path_asset"], idx["aseq"]
            self.place_mem, self.known, self.splits_asked = idx["place_mem"], (set(idx["known"]) if idx["known"] is not None else None), idx["splits_asked"]
            self._notes = idx.get("notes", [])
        if vm:
            self.vmeta = vm["vmeta"]
        if st == "끊김":                                 # 죽지 않는다. 적는 걸음만 멈추고, 새 사슬을 한 번 묻는다
            self._propose("원장 새 사슬", "원장|끊김", "원장 사슬이 끊겼습니다. 끊긴 원장을 그대로 두고 새 사슬을 시작할까요", "새 사슬 시작",
                          "원장 파일이 바뀌었거나 망가졌습니다(K-02)", "원장에 적는 모든 걸음이 멈춘 채로 있습니다", who="한 번", log=False)
            return
        if st in ("이음", "끝줄 고침"):
            if st == "끝줄 고침":
                self.led.add("LED", "원장 끝줄 고침", cause="복구")
            self.led.add("LED", "원장 이어 읽음", cause="복구", rows=len(self.led.rows), index=s2, card=s1)
        if "망가짐" in (s1, s2, s3) or (st in ("이음", "끝줄 고침") and "없음" in (s1, s2)):
            self.led.add("LED", "색인 다시 만듦", cause="복구", rc="RC-17", card=s1, index=s2, vers=s3)   # 다음 훑기에서 색인이 다시 선다(계보는 원장에 남은 것만큼만)
            if s3 != "읽음":
                self._rebuild_vmeta()

    def _rebuild_vmeta(self):
        """판 목록이 망가졌을 때: 원장의 「판 보관」 줄에서 다시 세운다."""
        self.vmeta = {}
        for r in self.led.rows:
            if r["code"] in ("LED-E01", "LED-E09") and r.get("aid"):
                self.vmeta.setdefault(r["aid"], []).append(dict(ver=r["ver"], kind="내용" if r["code"] == "LED-E01" else "자리", rel=r["rel"], hash=r.get("hash"), at=r["at"]))

    def _save(self):
        try:
            self._write(self.S_CARD, dict(mode=self.mode, mode_given=self.mode_given, rename_policy=self.rename_policy, user_rules=self.user_rules,
                                          bundles=self.bundles, bseq=self.bseq, bmap=self.bmap, oseq=self.oseq, props=self.props, pkeys=self.pkeys,
                                          pseq=self.pseq, mirror_order=self.mirror_order, touches=self.touches, no_place=self.no_place, vault=self.vault, learned=self.learned, placed=self.placed, led_n=self.led.base + len(self.led.rows), led_head=self.led.head,
                                          media=[dict(dev=d, root=m.root, kind=m.kind, registered=m.registered, role=m.role, scope=m.scope,
                                                      first_ok=m.first_ok, released=m.released) for d, m in self.media.items()]))
            self._write(self.S_INDEX, dict(dev_index=self.dev.index, media_index={d: m.index for d, m in self.media.items()},
                                           anc={k: sorted(v) for k, v in self.anc.items()},
                                           decided={json.dumps(list(k), ensure_ascii=False): dict(hash=v["hash"], seen=sorted(v["seen"])) for k, v in self.decided.items()},
                                           finals=self.finals, recover_count=self.recover_count, assets=self.assets, ver2asset=self.ver2asset,
                                           alias=self.alias, path_asset=self.path_asset, aseq=self.aseq, place_mem=self.place_mem,
                                           known=sorted(self.known) if self.known is not None else None, splits_asked=self.splits_asked, notes=self._notes))
            self._write(self.S_VERS, dict(vmeta=self.vmeta))
        except OSError:
            pass                                          # 남기지 못하면 다음 걸음에서 다시 남긴다

    def _note(self, mod, act, **kw):
        """보기만 하는 걸음(대시보드 등)에서 생긴 사건은 모아 두었다가 다음 적는 걸음의 맨 앞에 적는다(보기는 원장에 쓰지 않는다)."""
        if self._logging and self.led.verify():
            self.led.add(mod, act, **kw)
        else:
            self._notes.append([mod, act, kw])

    def _flush(self):
        if self._notes and self.led.verify():
            notes, self._notes = self._notes, []
            for mod, act, kw in notes:
                self.led.add(mod, act, **kw)

    # ================= 2. 자산 · 판 · 사본 =================
    def _aid(self, a):
        while a in self.alias:
            a = self.alias[a]
        return a

    @staticmethod
    def _pkey(s, rel):
        return "%s|%s" % (s.dev_id, norm(rel))

    def _new_asset(self, h, size, origin=None):
        base = h[:FP_LEN] + "-%d" % size
        aid, n = base, 1
        while aid in self.assets or aid in self.alias:    # 지문 앞자리와 크기가 같아도 전체 해시가 다르면 다른 자산이다(ID-15): 뒤에 +순번
            n += 1
            aid = "%s+%d" % (base, n)
        self.aseq += 1
        self.assets[aid] = dict(root=h, vers=[h], n=self.aseq, origin=origin)
        self.ver2asset[h] = aid
        return aid

    def _join(self, h, aid):
        aid = self._aid(aid)
        self.ver2asset[h] = aid
        if h not in self.assets[aid]["vers"]:
            self.assets[aid]["vers"].append(h)
        return aid

    def _merge(self, a, b):
        """따로 등록된 두 자산이 계보로 한 자산임이 밝혀짐: 먼저 등록된 식별자를 지키고, 다른 쪽은 대응표(alias)에 남긴다. 옛 식별자는 다시 쓰지 않는다."""
        a, b = self._aid(a), self._aid(b)
        if a == b:
            return a
        keep, drop = (a, b) if self.assets[a]["n"] < self.assets[b]["n"] else (b, a)
        for h in self.assets[drop]["vers"]:
            self._join(h, keep)
        self.alias[drop] = keep
        for k, v in list(self.path_asset.items()):
            if v == drop:
                self.path_asset[k] = keep
        if drop in self.recover_count:
            self.recover_count[keep] = self.recover_count.get(keep, 0) + self.recover_count.pop(drop)
        if drop in self.vmeta:                            # 판 보관도 한 줄로 잇는다(지키는 쪽의 번호는 그대로, 합쳐지는 쪽은 뒤에 붙음)
            for mt in self.vmeta.pop(drop):
                lst = self.vmeta.setdefault(keep, [])
                n = len(lst) + 1
                if mt["kind"] == "내용":
                    src = os.path.join(self._vdir(drop), "v%d" % mt["ver"])
                    if os.path.exists(src):
                        os.replace(src, os.path.join(self._vdir(keep), "v%d" % n))
                lst.append(dict(mt, ver=n))
        del self.assets[drop]
        self._note("CLS", "자산 맞춤", cause="정합", old=drop, new=keep)
        return keep

    def _link(self, child, parent):
        """계보를 잇는다(child가 parent의 뒤 판). 두 판이 자산으로 등록돼 있으면 같은 자산으로 맞춘다(ID-11·12)."""
        if child == parent:
            return False
        if self._desc(parent, child):                     # 옛 판으로 되돌아간 것: 「뒤 판」으로 잇지 않는다(계보에 고리가 생기면 꽂은 순서에 따라 답이 달라진다)
            self._note("SYN", "계보 잇지 않음", cause="바뀜", why="앞서 본 옛 판으로 되돌아감")
            return False
        self.anc.setdefault(child, set()).add(parent)
        a, b = self.ver2asset.get(child), self.ver2asset.get(parent)
        if a and b:
            self._merge(a, b)
        elif b:
            self._join(child, b)
        elif a:
            self._join(parent, a)

    def _register(self, s):
        """색인의 파일마다 자산을 맞춘다. 빈 파일은 자산이 아니다(ID-14). 맞대는 것은 전체 해시다(ID-15)."""
        if s is self.dev:
            self.empties = sorted(rel for rel, it in s.index.items() if not it["size"])
        for rel, it in s.index.items():
            if not it["size"]:
                it["asset"] = None
                continue
            h, k = it["hash"], self._pkey(s, rel)
            aid = self.ver2asset.get(h)
            if aid is None:
                prev = self.path_asset.get(k)
                up = next((self.ver2asset[p] for p in self.anc.get(h, ()) if p in self.ver2asset), None)
                if prev and self._aid(prev) in self.assets:
                    aid = self._join(h, prev)             # 같은 자리에서 내용이 바뀜 → 같은 자산의 새 판(ID-11)
                elif up:
                    aid = self._join(h, up)
                else:
                    aid = self._new_asset(h, it["size"])
            it["asset"] = self._aid(aid)
            self.path_asset[k] = it["asset"]

    def _bytes(self, src, rel):
        try:
            with open(src.path(rel), "rb") as f:
                return f.read()
        except OSError:
            return b""                                    # 색인 뒤에 사라진 파일: 죽지 않고 빈 것으로 본다(다음 훑기에서 색인이 맞춰진다)

    def _keep_base(self, h, s, rel):
        """글자 문서의 판을 엔진 자리(00.09_바탕)에 남긴다: 뒤에 두 매체에서 번갈아 고친 것을 합칠 때 계보로 확인된 바탕이 된다(원본은 건드리지 않음)."""
        p = os.path.join(self.home, "00.09_바탕", h)
        if os.path.exists(p):
            return
        b = self._bytes(s, rel)
        if sha(b) != h:
            return
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p + ".tmp", "wb") as f:
                f.write(b)
            os.replace(p + ".tmp", p)
        except OSError:
            pass

    def _old_bytes(self, h):
        """앞 판의 내용을 아직 어딘가에서 읽을 수 있으면 돌려준다(다른 사본, 판 보관, 남겨 둔 바탕)."""
        p = os.path.join(self.home, "00.09_바탕", h)
        if os.path.exists(p):
            b = open(p, "rb").read()
            if sha(b) == h:
                return b
        for s in [self.dev] + [m for m in self.media.values() if m.plugged]:
            for rel, it in s.index.items():
                if it["hash"] == h:
                    b = self._bytes(s, rel)
                    if sha(b) == h:
                        return b
        for aid, lst in self.vmeta.items():
            for v in lst:
                if v.get("hash") == h and v["kind"] == "내용":
                    p = os.path.join(self._vdir(aid), "v%d" % v["ver"])
                    if os.path.exists(p):
                        return open(p, "rb").read()
        return None

    def _same_line(self, s, rel, it, old_it):
        """같은 자리에서 내용이 바뀌었을 때 「앞 판의 뒤」로 볼 수 있는가. 돌려주는 값: "잇기" · "다른 글"(조용히 새 자산) · "확인"(잇지 않고 한 번 묻는다).
        ① 글자가 아닌 것은 고친 시각이 앞 판보다 이르면(옛 백업으로 덮어씀·되살림) 잇지 않는다. ② 글자 문서이고 앞 판을 읽을 수 있으면 줄이 반 넘게 같을 때만 잇는다.
        한 줄도 같지 않으면 같은 이름으로 다시 만든 다른 글, 조금만 같으면 옛 판으로 덮어쓴 모양이라 확인을 받는다(엔진이 본 적 없는 판이라도)."""
        older = it.get("mtime") is not None and old_it.get("mtime") is not None and it["mtime"] < old_it["mtime"] - 2
        if it["ext"] not in TEXT or not it["size"] or not old_it["size"]:
            return "확인" if older else "잇기"
        ob = self._old_bytes(old_it["hash"])
        ta, tb = decode(self._bytes(s, rel)), decode(ob) if ob is not None else None
        if not ta or not tb:
            return "확인" if older else "잇기"
        la, lb = ta[0].splitlines(), tb[0].splitlines()
        if max(len(la), len(lb)) < 3:
            return "잇기"                                 # 두 줄 이하끼리는 견줄 거리가 없다(양식을 채운 것 등): 0.3처럼 뒤 판으로
        r = difflib.SequenceMatcher(None, la, lb, autojunk=False).ratio()
        if r == 0:
            return "다른 글"
        if r < 0.5:
            return "확인"                                 # 글자 문서는 날짜를 믿지 않는다(날짜가 속는 경우, TS-16): 내용으로만 본다
        return "잇기"

    def _scan(self, s, lineage=True):
        old, old_flags = s.index, dict(s.flags)
        s.scan()
        for rel, r in s.flags.items():                    # 검사는 꽂을 때만이 아니라 훑을 때마다(뒤에 생긴 위협도 표시하고 뒤 걸음에서 뺀다)
            if old_flags.get(rel) != r:
                self._note("AAD", "격리 표시" if r[0] == "위험" else "주의 표시", medium=s.dev_id, ver=s.index[rel]["ver"], why=r[1],
                           grade="M3" if r[0] == "위험" else "M2", res="멈춤" if r[0] == "위험" else "됨", rc="RC-03" if r[0] == "위험" else None)
        if s.unseen:
            self._note("LNK", "보지 못함", medium=s.dev_id, files=len(s.unseen)) if getattr(s, "_unseen_n", 0) != len(s.unseen) else None
        s._unseen_n = len(s.unseen)
        if lineage:
            for rel, it in s.index.items():
                if rel in old and old[rel]["hash"] != it["hash"]:        # 같은 자리에서 바뀜 → 앞 판의 뒤를 이음
                    how = self._same_line(s, rel, it, old[rel])
                    if how == "잇기":
                        self._link(it["hash"], old[rel]["hash"])
                    else:
                        self.path_asset.pop(self._pkey(s, rel), None)
                        self._note("SYN", "계보 잇지 않음", cause="바뀜", medium=s.dev_id, ver=it["ver"],
                                   why="같은 이름으로 다시 만든 다른 글" if how == "다른 글" else "옛 날짜의 판이거나 내용이 크게 다름(옛 백업으로 덮어쓴 모양)")
                        if how == "확인":
                            self._propose("판 확인", "판확인|%s|%s" % (self._pkey(s, rel), it["hash"][:16]),
                                          "「%s」(%s)의 내용이 앞서 본 판과 크게 다르거나 더 옛 날짜입니다. 같은 문서의 새 판으로 이을까요" % (rel.split("/")[-1], s.dev_id), "따로 둠",
                                          "옛 백업으로 덮어썼거나 다른 글로 바꾼 모양입니다. 잇지 않고 따로 두었습니다(최종본은 그대로)",
                                          "따로 둔 채로 있습니다(최종본은 앞서 맞춘 판 그대로)", who="한 번", data=dict(child=it["hash"], parent=old[rel]["hash"]))
                            self._note("SYN", "판 확인 필요", cause="바뀜", medium=s.dev_id, ver=it["ver"], res="멈춤", rc="RC-27")
                if it["ext"] in TEXT and 0 < it["size"] <= 1 << 20 and self.tier == "구독":
                    self._keep_base(it["hash"], s, rel)        # 정합(구독)에서만 쓰는 바탕이라 무료에서는 남기지 않는다
        self._register(s)
        gone = {}
        for rel, it in old.items():                       # 옮김 알아보기: 사라진 자리의 자산이 새 자리에 나타나면 자리 기억이 따라간다(PL-12)
            if rel not in s.index and it.get("asset") and self._pkey(s, rel) in self.place_mem:
                gone.setdefault(self._aid(it["asset"]), []).append(rel)
        for rel in sorted(s.index):
            a = s.index[rel].get("asset")
            if rel not in old and a and gone.get(self._aid(a)):
                self.place_mem[self._pkey(s, rel)] = self.place_mem.pop(self._pkey(s, gone[self._aid(a)].pop(0)))
        return s.index

    def copies(self, aid):
        """사본(COPY) = 판 + 기기·매체 + 자리. 거울은 사본의 한 가지다(ID-16: 거울 n은 그 매체를 등록 순으로 센 번호)."""
        aid, out = self._aid(aid), []
        for s in [self.dev] + list(self.media.values()):
            for rel, it in s.index.items():
                if it.get("asset") and self._aid(it["asset"]) == aid:
                    out.append(dict(ver=it["ver"], hash=it["hash"], dev=s.dev_id, rel=rel, kind="사본", plugged=s.plugged))
        hs = set(self.assets.get(aid, {}).get("vers", ()))
        for d in self.mirror_order:
            m = self.media.get(d)
            mroot = os.path.join(m.root, "_HiDAM_거울") if m else None
            if not (m and m.plugged and os.path.isdir(mroot)):
                continue
            for dd, _, fs in os.walk(mroot):
                for f in fs:
                    data = open(os.path.join(dd, f), "rb").read()
                    if sha(data) in hs:
                        out.append(dict(ver=ver_id(data), hash=sha(data), dev=d, rel=os.path.relpath(os.path.join(dd, f), mroot).replace("\\", "/"),
                                        kind="거울 %d" % (self.mirror_order.index(d) + 1), plugged=True))
        return out

    def asset_of(self, rel, src=None):
        it = (src or self.dev).index.get(rel)
        return self._aid(it["asset"]) if it and it.get("asset") else None

    def _check_splits(self):
        """ID-13: 같은 자산의 사본이 다른 이름으로 따로 고쳐지면 「다른 자산으로 가를까요」를 제시한다."""
        by = {}
        for s in self.work_sources():
            for rel, it in s.index.items():
                if it.get("asset"):
                    by.setdefault(self._aid(it["asset"]), []).append((s, rel, it))
        for aid, cs in by.items():
            if len({c[2]["hash"] for c in cs}) < 2 or len({(c[2]["stem"], c[2]["ext"]) for c in cs}) < 2:
                continue
            vers = self.assets[aid]["vers"]
            root_stem = next(((c[2]["stem"], c[2]["ext"]) for c in sorted(cs, key=lambda c: vers.index(c[2]["hash"]))), None)
            for s, rel, it in cs:
                if (it["stem"], it["ext"]) != root_stem and it["hash"] != self.assets[aid]["root"]:
                    self._propose("자산 가르기", "가름|%s|%s" % (aid, self._pkey(s, rel)), "「%s」을(를) 다른 자산으로 가를까요" % rel.split("/")[-1], "가름",
                                  "같은 내용에서 시작했으나 다른 이름으로 따로 고쳐졌습니다(양식을 베껴 새 문서를 쓴 모양)",
                                  "한 자산의 판으로 남습니다(자산 식별자 그대로)", who="한 번", data=dict(aid=aid, dev=s.dev_id, rel=rel, hash=it["hash"]))

    def _split(self, d):
        aid = self._aid(d["aid"])
        n = 1 + sum(1 for a in list(self.assets) + list(self.alias) if a.startswith(aid + "~"))
        new = "%s~%d" % (aid, n)
        self.aseq += 1
        self.assets[new] = dict(root=d["hash"], vers=[d["hash"]], n=self.aseq, origin=aid)
        self.ver2asset[d["hash"]] = new
        if d["hash"] in self.assets[aid]["vers"]:
            self.assets[aid]["vers"].remove(d["hash"])
        self.path_asset["%s|%s" % (d["dev"], norm(d["rel"]))] = new
        self.anc.pop(d["hash"], None)                     # 새 자산의 첫 판은 앞 판을 가리키지 않는다(바탕은 origin 칸에 남음)
        self.led.add("CLS", "자산 가름", actor="사용자", old=aid, new=new, rel=d["rel"])
        self.rescan()
        return new

    # ================= SCT =================
    def open_session(self, sid):
        if self.session_lock and self.session_lock != sid:
            self.led.add("SCT", "세션 거절", res="거절", rc="RC-04", sid=sid, holder=self.session_lock)
            return False
        self.session_lock = sid
        return True

    @op("사용자 결정")
    def set_mode(self, mode):
        assert mode in ("일반", "시스템", "프로젝트")
        if self.tier != "구독" and mode != "일반" and not self.once:   # 무료는 일반만 쓴다(MO-06 · FN-17). 기능 별도의 한 번 적용이 열려 있으면 그 한 번을 위해 고를 수 있다
            self.led.add("SCT", "모드 거절", actor="사용자", res="거절", rc="RC-01", want=mode)
            return False
        self.led.add("SCT", "모드 바꿈", actor="사용자", old=self.mode, new=mode)
        self.mode, self.mode_given = mode, True
        return True

    @op("사용자 결정")
    def set_rename_policy(self, v):
        assert v in ("보이기만", "모드 규칙")
        self.led.add("SCT", "이름 규칙 바꿈", actor="사용자", old=self.rename_policy, new=v)
        self.rename_policy = v

    @op("사용자 결정")
    def set_role(self, dev_id, role, scope=None):
        assert role in ROLES
        m = self.media[dev_id]
        if self.tier != "구독" and role != "작업":         # 매체 역할은 구독 기능이다(FN-17). 무료에서는 작업 매체로만 본다
            self.led.add("SCT", "역할 거절", actor="사용자", res="거절", rc="RC-01", medium=dev_id, want=role)
            return False
        m.role, m.scope, m.first_ok, m.role_given = role, scope, False, True
        self.led.add("SCT", "매체 역할", actor="사용자", medium=dev_id, role=role, scope=scope)

    @op("사용자 결정")
    def confirm_first(self, dev_id):
        self.media[dev_id].first_ok = True
        self.led.add("SYN", "사용자 결정", actor="사용자", what="첫 미러링 확인", medium=dev_id)

    @op("정책 판 올림")
    def bump_policy(self, new_policy):
        """CP-12 · CD-10: 정책 판이 오르면 원장의 그 뒤 줄은 새 판으로 적힌다. 자리 기억은 지키고, 달라진 판정은 「자리를 바꿀까요」로만 나온다."""
        old, self.led.policy = self.led.policy, new_policy
        self.led.add("SCT", "정책 판 올림", old=old, new=new_policy)
        self._tick()

    # ================= 6. 제안 — 한 곳에서 내고 한 번에 받는다 =================
    def _propose(self, kind, key, what, answer, why, if_not, who="한 번", data=None, log=True):
        if key in self.pkeys:
            return self.props.get(self.pkeys[key])
        self.pseq += 1
        p = dict(no=self.pseq, kind=kind, key=key, what=what, answer=answer, why=why, if_not=if_not, who=who, state="열림", data=data or {}, at=now_z())
        self.props[p["no"]], self.pkeys[key] = p, p["no"]
        if log:
            self._note("SCT", "제안", no=p["no"], kind=kind, who=who)
        return p

    def proposals(self, all_=False):
        """제안 목록: 번호 · 무엇을 · 권하는 답 · 까닭 · 받아들이지 않으면 어떻게 되는지 · 누가(제시/한 번)."""
        return [dict((k, p[k]) for k in ("no", "kind", "what", "answer", "why", "if_not", "who", "state"))
                for p in sorted(self.props.values(), key=lambda p: p["no"]) if all_ or p["state"] == "열림"]

    def _close(self, key, state="닫힘(풀림)"):
        p = self.props.get(self.pkeys.get(key))
        if p and p["state"] == "열림":
            p["state"] = state

    @op("사용자 결정")
    def accept(self, no, answer=None):
        """제안 한 건을 받아들인다. answer를 주면 권한 답 대신 그 답으로(바꿀 수 있음)."""
        p = self.props[no]
        if p["state"] != "열림":
            return dict(ok=False, why="이미 닫힌 제안")
        k, d, ans = p["kind"], p["data"], answer if answer is not None else p["answer"]
        if k == "원장 새 사슬":
            self.led.restart()
            out = True
        elif ans is None:
            return dict(ok=False, why="권하는 답이 없는 제안 — 답을 골라 주어야 합니다")
        elif k == "모드":
            out = self.set_mode(ans)
        elif k == "매체 역할":
            role, scope = (ans if isinstance(ans, (list, tuple)) else (ans, d.get("scope")))
            self.set_role(d["dev"], role, scope)
            out = role
            if role == "거울" and d.get("empty"):          # 비어 있던 매체는 잃을 것이 없다: 이 받아들임이 첫 미러링의 확인을 겸한다(미리 보기 건수를 제안에 보였다)
                self.confirm_first(d["dev"])
                out = self.mirror(d["dev"])
        elif k == "위험 매체":
            m = self.media[d["dev"]]
            m.released, m.blocked = True, None
            self.led.add("LNK", "매체 연결", medium=m.dev_id, files=len(m.index), role=m.role, excluded=sum(1 for v in m.flags.values() if v[0] == "위험"))
            out = "정상"
        elif k == "첫 미러링":
            self.confirm_first(d["dev"])
            out = self.mirror(d["dev"])
        elif k == "대량 변경":
            out = self.mirror(d["dev"], auto=False)
        elif k in ("프로젝트 묶기", "조직 묶기"):
            out = self._make_group(k, d)
        elif k == "자리 바꿈":
            out = self._remember(d["mkey"], d["aid"], d["code"], d["rank"], "제안 받아들임", old=d["old"])
        elif k == "자산 가르기":
            out = self._split(d)
        elif k == "판 고르기":
            out = self.choose(d["stem"], d["ext"], ans, d["gi"])
        elif k == "자리 묶음":
            out = self._apply(set(d["rels"]), rename=self.rename_policy == "모드 규칙")
            cats = sorted({self.judge(self.dev, r2)["code"] for r2, _ in out.get("pairs", [])} | set(d.get("cats", [])))
            new_c = [c for c in cats if c not in self.learned]
            if new_c:                                     # 받아들인 범주는 배운다: 다음부터 확신 「중간」의 새 파일도 그 범주면 스스로 옮긴다(묶음 확인이 새 문서마다 생기지 않게)
                self.learned = sorted(set(self.learned) | set(new_c))
                self.led.add("CLS", "범주 배움", actor="사용자", cats=new_c)
        elif k == "판 확인":
            if ans == "뒤 판":
                self._link(d["child"], d["parent"])
            out = ans
        else:
            return dict(ok=False, why="모르는 제안")
        p["state"] = "받아들임"
        self.led.add("SCT", "제안 받아들임", actor="사용자", no=no, kind=k, answer=ans if isinstance(ans, (str, int, float, type(None))) else list(ans))
        self._tick()
        return dict(ok=True, out=out)

    @op("사용자 결정")
    def decline(self, no):
        p = self.props[no]
        if p["state"] == "열림":
            p["state"] = "물림"
            if p["kind"] == "자리 묶음":
                self.no_place = sorted(set(self.no_place) | {norm(r) for r in p["data"]["rels"]})   # 물린 것은 다시 묻지 않는다(지금 자리에 둠)
            if self.led.verify():
                self.led.add("SCT", "제안 물림", actor="사용자", no=no, kind=p["kind"])
        return True

    def _dev_folders(self):
        out = {}
        for rel in self.dev.index:
            parts = norm(rel).split("/")[:-1]
            for i in range(1, len(parts) + 1):
                out.setdefault("/".join(parts[:i]), 0)
            if parts:
                out["/".join(parts)] += 1
        return out

    def _propose_setup(self):
        """MO-06·07: 기기를 훑어 모드를 권하고, 폴더 이름과 묶인 모양에서 프로젝트·조직 후보를 뽑아 한 번 제시한다. 이름을 등록하지 않아도 돈다."""
        folders = self._dev_folders()
        kids = {}
        for f in folders:
            if "/" in f:
                kids.setdefault(f.rsplit("/", 1)[0], []).append(f.rsplit("/", 1)[1])
        staged = sum(1 for f in folders if gal_named(f.split("/")[-1]))
        if self.tier == "구독" and not self.mode_given:
            rec = "프로젝트" if staged >= 3 else "시스템"
            self._propose("모드", "모드|처음", "정리의 축(모드)을 「%s」로 할까요" % rec, rec,
                          "갈래 이름이 붙은 폴더가 %d개 있습니다" % staged if rec == "프로젝트" else "갈래 이름이 붙은 폴더가 적어(%d개) 표준 자리가 축으로 알맞습니다" % staged,
                          "일반 모드(사용자가 만든 폴더 구조 그대로)로 돕니다. 표준 자리와 등급은 옆에 붙습니다", who="제시")
        given = [n.lower() for n, _ in self.projects] + [n.lower() for n, _ in self.orgs]
        taken = [b["folder"] for b in self.bundles.values() if b["state"] == "씀" and b["kind"] != "보관"]
        cands = []
        for f in sorted(folders, key=lambda x: (x.count("/"), x)):
            base, low = f.split("/")[-1], f.lower()
            if base.startswith("기준자리") or any(has_name(base, g) for g in given) or any(low == t or low.startswith(t + "/") for t in taken + cands):
                continue
            gs = sorted({g for g in map(gal_named, kids.get(f, [])) if g})
            nums = sorted({g for g in map(gal_of, kids.get(f, [])) if g})
            if len(gs) < 2 and len(nums) >= 3:            # 갈래 이름은 없어도 00~10의 마디 번호 폴더가 셋 이상이면 후보로 낸다(생활의 일처럼 말이 다른 묶음)
                gs = nums
            if len(gs) >= 2:
                life = any(has_word(base, w) for w in LIFE_WORDS)
                cands.append(low)
                self._propose("프로젝트 묶기", "묶기|프로젝트|" + low, "「%s」 폴더를 프로젝트로 묶을까요" % f, "묶음",
                              "갈래 폴더가 %d개 있습니다(%s)" % (len(gs), "·".join(STAGES[g] for g in gs)),
                              "폴더는 사용자 구조 그대로 두고 표준 자리만 붙입니다", who="한 번",
                              data=dict(folder=f, btype="50" if life else ("10" if "04" in gs else "99"), pack="생활" if life else "기본"))
            elif "(주)" in base or "㈜" in base or any(t.endswith(tl) and len(t) > len(tl) for t in _TOK.findall(base) for tl in ORG_TAILS):
                cands.append(low)
                self._propose("조직 묶기", "묶기|조직|" + low, "「%s」 폴더를 일한 곳(조직)으로 묶을까요" % f, "묶음",
                              "폴더 이름이 조직 이름의 모양입니다", "폴더는 사용자 구조 그대로 두고 표준 자리만 붙입니다", who="한 번", data=dict(folder=f))

    def _propose_role(self, m):
        role, scope, why = recommend_role(m.index)
        if role == "작업":                                # 권하는 값이 기본값과 같으면 묻지 않는다
            return
        n = len(self.mirror_set(m)[0]) if role == "거울" else 0
        what = {"거울": "이 매체(%s)를 거울로 쓸까요. 지금 비출 것은 %d건입니다" % (m.dev_id, n),
                "보관": "이 매체(%s)를 사진·영상 보관(%s)으로 쓸까요" % (m.dev_id, scope), "원천": "이 매체(%s)를 원천 보관(통째로 받아 둔 것)으로 쓸까요" % m.dev_id}[role]
        self._propose("매체 역할", "역할|" + m.dev_id, what, role, why, "작업 매체로 다룹니다(엔진은 이 매체에 아무것도 쓰지 않습니다)", who="한 번",
                      data=dict(dev=m.dev_id, scope=scope, empty=role == "거울"))

    # ================= LNK + AAD =================
    @op("꽂음")
    def plug(self, m):
        known = self.media.get(m.dev_id)
        if len(self.media) >= 8 and not known:
            self.led.add("LNK", "자리 없음", res="거절", rc="RC-05", medium=m.dev_id)
            return "자리 없음"
        if known and known is not m:                      # 다시 꽂음: 앞서 본 색인과 받아 둔 역할을 잇는다(DUP-11·16)
            m.index = known.index
            m.released = known.released
            if not m.role_given:
                m.role, m.scope, m.first_ok, m.role_given = known.role, known.scope, known.first_ok, known.role_given
        m.plugged = True
        self.media[m.dev_id] = m
        if not m.registered:
            m.blocked = "미등록 매체"
            self.led.add("SCT", "미등록 매체", res="멈춤", rc="RC-02", medium=m.dev_id, grade="M3")
            return m.blocked
        if not os.path.isdir(m.root):
            m.plugged, m.blocked = False, None
            return "매체 사용 불가"
        m.flags = {}
        self._scan(m)                                     # 검사 결과는 표시만 한다. 옮기지 않고, 뒤 걸음에서 뺀다
        danger = sorted(r for r, v in m.flags.items() if v[0] == "위험")
        if danger and not m.released:
            m.blocked = "위험 표시 — 사용자 결정 대기"
            self._propose("위험 매체", "위험|%s|%s" % (m.dev_id, sha("|".join(danger).encode("utf-8"))[:12]),
                          "매체 %s에 위험 표시 파일이 %d건 있습니다. 그 파일을 빼고 이 매체를 쓸까요" % (m.dev_id, len(danger)), "빼고 씀",
                          "위험 표시 파일은 옮기지도 지우지도 않고 그 자리에 둔 채 모든 걸음에서 뺍니다", "이 매체는 막힌 채로 있습니다", who="한 번", data=dict(dev=m.dev_id))
            return m.blocked
        m.blocked = None
        if not known and not m.role_given and self.tier == "구독":
            self.dev.index or self._scan(self.dev)
            self._propose_role(m)
        self.led.add("LNK", "매체 연결", medium=m.dev_id, files=len(m.index), role=m.role)
        if self.auto and self.tier == "구독":
            self.auto_run("꽂으면")
        return "정상"

    @op("정합")
    def import_lineage(self, other):
        """SY-19 · PL-12: 같은 회원의 다른 기기에서 계보(해시 앞뒤)·사용자 규칙·자리 기억을 받아 온다. 원본·이름·경로는 받지 않는다.
        구독에서만 연다. 상대의 원장 사슬이 맞을 때만 받고, 이 기기가 아는 계보와 거꾸로인 줄은 받지 않는다. 받은 것은 원장에 남긴다."""
        peer = getattr(getattr(other, "dev", None), "dev_id", "확인 안 됨")
        led = getattr(other, "led", None)
        if self.tier != "구독" or not (led and hasattr(led, "verify") and led.verify() and isinstance(getattr(other, "anc", None), dict)):
            self.led.add("LNK", "계보 거절", res="거절", rc="RC-01" if self.tier != "구독" else "RC-16", peer=peer)
            return False
        got = clash = 0
        for h, ps in other.anc.items():
            for p in ps:
                if self._desc(p, h):
                    clash += 1                            # 이 기기는 거꾸로 알고 있다: 받지 않는다
                else:
                    self._link(h, p)
        if clash:
            self.led.add("LNK", "계보 거절", res="거절", rc="RC-25", peer=other.dev.dev_id, links=clash)
        for k, v in other.user_rules.items():
            if k not in self.user_rules:
                self.user_rules[k] = v
                got += 1
        for rel, it in other.dev.index.items():           # 자리 기억은 판(전체 해시)에 실어 받는다. 이름·경로는 받지 않는다
            mem = other.place_mem.get(other._pkey(other.dev, rel))
            if mem and ("판:" + it["hash"]) not in self.place_mem:
                self.place_mem["판:" + it["hash"]] = dict(mem, basis="다른 기기에서 받음(%s)" % other.dev.dev_id)
                got += 1
        self._note("LNK", "계보 받음", peer=other.dev.dev_id, links=sum(len(v) for v in other.anc.values()) - clash, rules=got)
        return True

    @op("사용자가 누름")
    def unplug(self, dev_id):
        self.media[dev_id].plugged = False
        self.led.add("LNK", "매체 분리", medium=dev_id)

    def rescan(self):
        self._scan(self.dev)
        for m in self.media.values():
            if m.plugged and not m.blocked:
                self._scan(m)

    def work_sources(self):
        """판을 찾는 곳: 기기와, 거울이 아닌 매체."""
        return [self.dev] + [m for m in self.media.values() if m.plugged and not m.blocked and m.role != "거울"]

    # ================= CLS: 판정 · 자리 기억 =================
    def _bundle_args(self, src):
        return [b for b in self.bundles.values() if b["state"] == "씀" and b["kind"] != "보관" and b["dev"] == src.dev_id]

    def judge(self, src, rel):
        """세 축의 자리와 등급. 자리 기억이 있으면 그 자리를 지킨다(PL-12). 보기만 하고 적지 않는다."""
        data = self._bytes(src, rel)
        c = classify(rel, data, self.orgs, self.user_rules, self.projects, self._bundle_args(src))
        strict = [classify(rel, data, self.orgs, None, self.projects, self._bundle_args(src))["code"]] if c["rank"] == "사용자 규칙" else []
        it = src.index.get(rel)
        aid = self._aid(it["asset"]) if it and it.get("asset") else None
        mem = self.place_mem.get(self._pkey(src, rel)) or (self.place_mem.get("판:" + it["hash"]) if it else None)
        c["asset"], c["fresh"], c["mkey"] = aid, None, self._pkey(src, rel)
        if mem and mem["code"] != c["code"]:
            c["fresh"] = dict(code=c["code"], rank=c["rank"], conf=c["conf"])
            if c["rank"] not in ("JR-1", "사용자 규칙") and mem["code"][:2] != "99":   # 보호와 사용자 규칙은 기억보다 앞서고, 판정 대기는 붙잡아 두지 않는다
                c.update(code=mem["code"], rank=mem["rank"], conf="높음", kept="자리 기억")
        if not c["bundle"]:
            c["bundle"] = next((b["id"] for b in self.bundles.values() if b["state"] == "씀" and b["kind"] == "보관" and b["dev"] == src.dev_id
                                and b["code"] == c["code"] and b["folder"] == norm(os.path.dirname(rel)).lower()), None)
        strict += [c["fresh"]["code"]] if c["fresh"] else []
        c["grade"] = max([sec_grade(x, rel) for x in [c["code"]] + strict] + [(mem or {}).get("grade", "D0")])   # 자동으로는 올리기만: 사용자 규칙·자리 기억·옮김으로 낮아지지 않는다(SV-02·04)
        c["place"] = {"일반": c["folder"], "시스템": c["code"], "프로젝트": c["project"] or c["code"]}[self.mode]
        c["place_code"] = "%s / %s%s" % (self.profile, c["bundle"] or c["code"], ("-" + c["gal"]) if c["bundle"] and c["gal"] else "")
        return c

    def _remember(self, mkey, aid, code, rank, basis, old=None, cause=None):
        """자리 기억은 사본(자산 + 놓인 자리)에 붙는다. 같은 내용의 사본이 다른 폴더에 있으면 저마다의 자리를 가진다(사본 = 판 + 기기·매체 + 논리 자리)."""
        self.place_mem[mkey] = dict(code=code, rank=rank, policy=self.led.policy, basis=basis, at=now_z())
        self._note("CLS", "자리 기억" if not old else "자리 받음", asset=aid, old=old, new=code, rank=rank, basis=basis, **(dict(cause=cause) if cause else {}))
        return code

    def _settle_places(self, judged):
        """PL-11·12: 정한 자리(확신 높음·중간, 사용자 규칙)를 자산에 붙여 기억한다. 판정 대기(99)에서 자리를 받으면 사건으로 남긴다.
        기억과 다른 새 신호가 더 앞선 순위일 때만 「자리를 바꿀까요」를 제시한다. 뒤 순위의 신호(폴더를 옮긴 것 등)로는 바꾸지 않는다."""
        for rel, c in judged.items():
            aid = c["asset"]
            if not aid:
                continue
            mk, got = c["mkey"], self.place_mem.get("판:" + self.dev.index[rel]["hash"])
            mem = self.place_mem.get(mk)
            if mem and c["grade"] > mem.get("grade", "D0"):
                mem["grade"] = c["grade"]                 # 더 엄했던 등급은 자리 기억에 실려 따라간다(INH-03)
            if mem and got and got["code"] != mem["code"] and rank_ord(got["rank"]) < rank_ord(mem["rank"]):
                self._propose("자리 바꿈", "자리|%s|%s" % (mk, got["code"]), "「%s」의 자리를 %s에서 %s(으)로 바꿀까요" % (rel.split("/")[-1], mem["code"], got["code"]),
                              got["code"], "다른 기기에서는 더 앞선 순위(%s)로 이 자리를 받았습니다" % got["rank"], "기억한 자리 %s을(를) 지킵니다" % mem["code"],
                              who="한 번", data=dict(mkey=mk, aid=aid, code=got["code"], rank=got["rank"], old=mem["code"]))
            if not mem and got:                           # 다른 기기에서 받아 둔 기억을 이 사본에 붙인다
                self._remember(mk, aid, got["code"], got["rank"], got["basis"], old=(c["fresh"] or c)["code"] if (c["fresh"] or c)["code"] != got["code"] else None)
                continue
            if not mem:
                self._remember(mk, aid, c["code"], c["rank"], "첫 판정")
                continue
            f = c["fresh"]
            if not f:
                continue
            if mem["code"][:2] == "99" or f["rank"] in ("사용자 규칙", "JR-1"):
                self._remember(mk, aid, f["code"], f["rank"], {"사용자 규칙": "사용자 규칙", "JR-1": "보호"}.get(f["rank"], "판정 대기에서 자리 받음"), old=mem["code"],
                               cause="규칙" if f["rank"] == "사용자 규칙" else None)
            elif f["conf"] != "낮음" and rank_ord(f["rank"]) < rank_ord(mem["rank"]):
                self._propose("자리 바꿈", "자리|%s|%s" % (mk, f["code"]), "「%s」의 자리를 %s에서 %s(으)로 바꿀까요" % (rel.split("/")[-1], mem["code"], f["code"]),
                              f["code"], "더 앞선 순위의 새 신호(%s)가 생겼습니다. 기억한 자리의 근거는 %s입니다" % (f["rank"], mem["rank"]),
                              "기억한 자리 %s을(를) 지킵니다" % mem["code"], who="한 번", data=dict(mkey=mk, aid=aid, code=f["code"], rank=f["rank"], old=mem["code"]))

    @op("사용자 결정")
    def set_place(self, rel, code):
        """CP-08: 사용자가 자리를 고친다. 사용자 규칙으로 남기고 다음부터 먼저 적용한다. 보호 자산은 못 바꾼다."""
        it = self.dev.index.get(rel) or self._scan(self.dev).get(rel)
        if not re.match(r"^\d\d\.\d\d$", code) or code[:2] not in AREA_NAME:
            self.led.add("CLS", "배정 거절", actor="사용자", res="거절", rc="RC-26")
            return None
        key = "%s.%s" % (it["stem"], it["ext"])
        self.user_rules[key] = code
        self.led.add("CLS", "사용자 규칙", actor="사용자", key_sha=sha(key.encode("utf-8"))[:12], to=code)
        self._tick()
        return self.judge(self.dev, rel)["code"]

    @op("사용자가 누름")
    def preview(self, log=True):
        self._scan(self.dev)
        if log:
            self._tick(scan=False)
        out = {rel: self.judge(self.dev, rel) for rel in self.dev.index}
        n = max(len(out), 1)
        stat = {k: round(sum(1 for v in out.values() if v["conf"] == k) / n, 3) for k in ("높음", "중간", "낮음")}
        if log:
            self.led.add("CLS", "판정", files=len(out), mode=self.mode, high=stat["높음"], mid=stat["중간"], low=stat["낮음"])
        return out, stat

    def _tick(self, scan=True):
        """적는 걸음마다 도는 살림: 제안 내기 → 묶음 발급 → 자리 기억 → 가르기 살핌 → 새 파일에 이름·자리 → 프로젝트 살핌."""
        if not self.led.verify():
            return
        if scan:
            self._scan(self.dev)
        self._propose_setup()
        judged = {rel: self.judge(self.dev, rel) for rel in self.dev.index}
        self._issue_bundles(judged)
        self._settle_places(judged)
        self._check_splits()
        self._new_files()
        self._project_tick()

    # ================= 5. 묶음 · 갈래 =================
    def _bundle_name(self, folder, rels):
        """PL-06: 사람이 읽는 이름 `시점_대상_내용`을 폴더 이름에서 뽑아 제시한다."""
        parts = folder.split("/")
        base = parts[-1]
        md = re.search(r"(?<!\d)(20\d{2})[.\-_]?(\d{2})?", base)
        when = (md.group(1) + (md.group(2) or "")) if md else time.strftime("%Y%m", time.localtime(min([self.dev.index[r]["mtime"] for r in rels] or [time.time()])))
        what = clean_name(re.sub(r"\s+", "_", re.sub(r"^(\d\d_)+", "", base[:md.start()] + base[md.end():] if md else base).strip(" _-"))) if base else "묶음"
        who = clean_name(re.sub(r"^(\d\d_)+", "", parts[-2])) if len(parts) > 1 else ""
        return "_".join(x for x in (when, who, what) if x)

    def _issue(self, code, folder, kind, rels, **kw):
        """PL-04: 묶음 번호는 범주 안에서 0001부터 차례로, 이 기기의 원장이 준다. 한 번 쓴 번호는 다시 쓰지 않는다."""
        self.bseq[code] = self.bseq.get(code, 0) + 1
        bid = "%s-B%04d" % (code, self.bseq[code])
        sets = folder_sets(self.dev.index)
        b = dict(id=bid, code=code, folder=norm(folder).lower(), shown=folder, kind=kind, dev=self.dev.dev_id, state="씀", name=self._bundle_name(folder, rels),
                 sig=sha("".join(sorted(sets.get(folder, ()))).encode()), reg=time.time(), btype=kw.get("btype", "00"), pack=kw.get("pack"),
                 phase=None, outs={}, oseq={}, bl=[], ac=[], au=[], finds=[], ep=[], rq=[], links=[], ext={}, last_checks=None)
        self.bundles[bid] = b
        self._note("CLS", "묶음 발급", bundle=bid, kind=kind, btype=b["btype"], name_sha=sha(b["name"].encode("utf-8"))[:12])
        return b

    def _issue_bundles(self, judged):
        """보관 묶음(유형 00): 한 폴더에 같은 범주의 자산이 둘 이상 놓이면 그 폴더를 묶음으로 알아본다. 받아들인 프로젝트·조직 폴더 안은 그 묶음이 맡는다."""
        by = {}
        for rel, c in judged.items():
            d = os.path.dirname(rel)
            if d and c["asset"] and not c["bundle"] and not in_ref(rel) and c["code"][:2] not in ("99", "00"):
                by.setdefault((c["code"], d), []).append(rel)
        for (code, d), rels in sorted(by.items()):
            if len(rels) >= 2:
                self._issue(code, d, "보관", rels)

    def _make_group(self, kind, d):
        f = d["folder"]
        rels = [r for r in self.dev.index if norm(r).lower().startswith(norm(f).lower() + "/")]
        if kind == "조직 묶기":
            self.oseq += 1                                # PL-03: 시작 순으로 01~09 · 50~89, 다 차면 여러 조직 공통(90)
            cc = self.oseq if self.oseq <= 9 else (self.oseq + 40 if self.oseq <= 49 else 90)
            return self._issue("03.%02d" % cc, f, "조직", rels)["id"]
        up = next((b for b in self.bundles.values() if b["kind"] == "조직" and b["state"] == "씀" and norm(f).lower().startswith(b["folder"] + "/")), None)
        b = self._issue(up["code"] if up else "03.99", f, "프로젝트", rels, btype=d.get("btype", "99"), pack=d.get("pack"))
        for old in [x for x in self.bundles.values() if x["kind"] == "보관" and x["state"] == "씀" and (x["folder"] + "/").startswith(b["folder"] + "/")]:
            self._retire(old, [b["id"]], "프로젝트 묶음에 듦")   # 그 폴더 안에 먼저 서 있던 보관 묶음은 새 묶음으로 대응시킨다(PL-05)
        return b["id"]

    def _retire(self, b, new_ids, why, app=None):
        b["state"] = "옛 번호"
        (app or self).bmap.append(dict(old=b["id"], new=list(new_ids), why=why, at=now_z()))
        (app or self)._note("CLS", "묶음 대응", old=b["id"], new=list(new_ids), why=why)

    @op("사용자 결정")
    def split_bundle(self, bid, folders):
        """PL-05: 묶음을 가르면 새 번호를 주고 옛 번호는 다시 쓰지 않는다. 옛 → 새 대응표가 먼저다."""
        b, new = self.bundles[bid], []
        for f in folders:
            rels = [r for r in self.dev.index if norm(r).lower().startswith(norm(f).lower() + "/")]
            new.append(self._issue(b["code"], f, b["kind"], rels, btype=b["btype"], pack=b["pack"])["id"])
        self._retire(b, new, "가름")
        return new

    @op("사용자 결정")
    def merge_bundles(self, bids, folder):
        bs = [self.bundles[x] for x in bids]
        rels = [r for r in self.dev.index if norm(r).lower().startswith(norm(folder).lower() + "/")]
        nb = self._issue(bs[0]["code"], folder, bs[0]["kind"], rels, btype=bs[0]["btype"], pack=bs[0]["pack"])
        for b in bs:
            self._retire(b, [nb["id"]], "합침")
        return nb["id"]

    def _renumber(self, b, why):
        code = b["code"]
        self.bseq[code] = self.bseq.get(code, 0) + 1
        nb = dict(b, id="%s-B%04d" % (code, self.bseq[code]))
        self.bundles[nb["id"]] = nb
        self._retire(b, [nb["id"]], why)
        self.bundles[b["id"]] = dict(id=b["id"], code=code, folder="", shown="", kind=b["kind"], dev=b["dev"], state="옛 번호", name="", sig="", reg=b["reg"])
        return nb

    @op("정합")
    def sync_bundles(self, other):
        """PL-04: 두 기기에서 따로 발급된 묶음 번호를 맞춘다. 같은 폴더(같은 폴더 서명 또는 같은 이름·같은 범주)는 같은 묶음이고,
        번호가 겹치거나 다르면 뒤에 등록된 쪽을 옮기고 대응표를 남긴다. 두 기기의 원장에 다 적는다."""
        moved = []
        live = lambda a: [b for b in a.bundles.values() if b["state"] == "씀"]
        same = lambda x, y: x["code"] == y["code"] and (x["sig"] == y["sig"] or x["folder"].split("/")[-1] == y["folder"].split("/")[-1])
        for code in sorted(set(self.bseq) | set(other.bseq)):             # 두 기기의 「마지막 번호」를 먼저 맞춘다(새 번호가 다시 겹치지 않게)
            self.bseq[code] = other.bseq[code] = max(self.bseq.get(code, 0), other.bseq.get(code, 0))
        for theirs in sorted(live(other), key=lambda b: b["reg"]):
            mine = next((b for b in live(self) if same(b, theirs)), None)
            if mine and mine["id"] == theirs["id"]:
                continue
            if mine:                                      # 같은 묶음, 다른 번호 → 뒤에 등록된 쪽이 앞 번호로 맞춘다
                late_app, late, early = (self, mine, theirs) if mine["reg"] > theirs["reg"] else (other, theirs, mine)
                occ = late_app.bundles.get(early["id"])
                if occ and occ["state"] == "씀":           # 그 번호를 이미 다른 묶음이 쓰고 있으면 그 묶음을 먼저 새 번호로
                    nb = late_app._renumber(occ, "다른 기기와 번호 겹침")
                    other.bseq[nb["code"]] = self.bseq[nb["code"]] = late_app.bseq[nb["code"]]
                    moved.append((late_app.dev.dev_id, occ["id"], nb["id"]))
                late_app._retire(late, [early["id"]], "다른 기기의 같은 묶음에 맞춤", app=late_app)
                late_app.bundles[early["id"]] = dict(late, id=early["id"], state="씀")
                if late["id"] != early["id"]:
                    late_app.bundles[late["id"]] = dict(late, state="옛 번호")
                moved.append((late_app.dev.dev_id, late["id"], early["id"]))
            else:
                clash = self.bundles.get(theirs["id"])
                if clash and clash["state"] == "씀":       # 다른 묶음, 같은 번호 → 뒤에 등록된 쪽을 새 번호로
                    late_app, late = (self, clash) if clash["reg"] > theirs["reg"] else (other, theirs)
                    nb = late_app._renumber(late, "다른 기기와 번호 겹침")
                    other.bseq[nb["code"]] = self.bseq[nb["code"]] = late_app.bseq[nb["code"]]
                    moved.append((late_app.dev.dev_id, late["id"], nb["id"]))
        other._flush() if other.led.verify() else None
        other._save()
        return moved

    # ================= 7. 자리 배정과 이름 붙이기 =================
    def _target(self, rel, c):
        """모드의 축에 맞는 자리. (폴더, 까닭) — 옮기지 않으면 (None, 까닭)."""
        if self.mode == "일반":
            return None, "일반 모드 — 사용자 구조 그대로"
        if c["rank"] == "JR-1":
            return None, "보호 자산 — 옮기지 않음"
        if c["rank"] == "JR-2":
            return None, "꾸러미 — 폴더째 두는 것(낱개로 꺼내지 않음)"
        if in_ref(rel):
            return None, "기준 자리(엔진이 만든 최종본)"
        if c["conf"] == "낮음":
            return None, "판정 대기 — 건드리지 않음"
        if self.mode == "프로젝트" and c["project"]:
            return None, "프로젝트 묶음 안 — 묶음과 갈래 폴더를 지킴"
        b = self.bundles.get(c["bundle"]) if c["bundle"] else None
        if b and b["kind"] != "보관":
            return None, "받아들인 묶음(%s) 안 — 묶음 폴더를 지킴" % b["kind"]
        aa, code = c["code"][:2], c["code"]
        d = "%s_%s" % (aa, AREA_NAME[aa])
        if "." in code:
            d += "/%s_%s_%s" % (aa, code[3:], CAT_NAME.get(code, "범주"))
        if b:
            d += "/" + b["name"]
        return d, None

    def plan_places(self):
        """FN-03 미리 보기: 무엇이 어디로, 어떤 이름으로 갈지. 아무것도 바꾸지 않는다. 실제 배정은 이 표 그대로 한다(CP-10)."""
        self._scan(self.dev)
        plan = []
        for rel in sorted(self.dev.index):
            it, c = self.dev.index[rel], self.judge(self.dev, rel)
            if not it["size"]:
                continue
            name = rel.split("/")[-1]
            sname, nwhy = std_name(name, it["mtime"], c["folder"], CAT_NAME.get(c["code"], ""))
            d, why = self._target(rel, c)
            how = "건드리지 않음" if d is None else ("확인 뒤" if c["grade"] >= "D3" or c["conf"] == "중간" else "자동")
            if d is not None and c["grade"] >= "D3":
                why = "보호 등급(%s) — 확인 없이 옮기지 않음" % c["grade"]
            plan.append(dict(rel=rel, to=d, std_name=sname, name_why=nwhy, code=c["code"], conf=c["conf"], grade=c["grade"], how=how, why=why,
                             moves=d is not None and norm(os.path.dirname(rel)) != d))
        return plan

    def _gate(self):
        if self.mode == "일반":
            return "RC-15"
        if self.tier == "구독":
            return None
        return None if self.once else "RC-14"

    @op("사용자가 누름")
    def apply_places(self, confirm=False):
        """FN-03 실제 배정. 구독(계속) 또는 기능 별도의 「한 번 적용」에서만, 기기의 사용자 폴더 안에서만. 확신 높음·보호 등급 아래만 옮긴다.
        confirm=True는 사용자가 묶음 제안을 받아들였다는 뜻으로 확신 중간까지 옮긴다. 보호 등급(D3 이상)은 여기서 옮기지 않는다."""
        rc = self._gate()
        if rc:
            self.led.add("CLS", "배정 거절", res="거절", rc=rc, tier=self.tier, mode=self.mode)
            return dict(ok=False, why=RC[rc], moved=0)
        plan = [p for p in self.plan_places() if p["to"] is not None and (p["how"] == "자동" or (confirm and p["how"] == "확인 뒤" and p["grade"] < "D3"))]
        out = self._apply({p["rel"] for p in plan}, rename=self.rename_policy == "모드 규칙")
        if self.tier != "구독":
            self.once = False                             # 한 번 적용은 한 번으로 닫힌다
        return out

    def _free_name(self, d, name, taken):
        """이름이 겹치면 순번을 붙인다(NM-02). 대소문자만 다른 이름·자모 모양만 다른 이름은 같은 이름으로 본다(NM-04)."""
        e = ext_of(name)
        stem, dot = (name[:-(len(e) + 1)], "." + name.rsplit(".", 1)[1]) if e else (name, "")
        cand, n = name, 1
        while norm(cand).lower() in taken:
            n += 1
            cand = "%s_%d%s" % (stem, n, dot)
        return cand

    def _apply(self, rels, rename):
        """옮김·이름 바꿈의 한 걸음. 옛 자리·옛 이름을 판 목록과 원장에 남긴 뒤에만 옮긴다. 못 옮기는 것은 건너뛰고 보류로 적는다."""
        self._scan(self.dev)
        moved, named, held = [], 0, []
        root = os.path.realpath(self.dev.root)
        jobs = [(rel, self.dev.index[rel], self.judge(self.dev, rel)) for rel in sorted(rels) if rel in self.dev.index]
        jobs = [(rel, it, c, self._target(rel, c)[0]) for rel, it, c in jobs]      # 갈 자리는 옮기기 전에 한꺼번에 정한다(미리 보기와 같은 값)
        for rel, it, c, d in jobs:
            name = rel.split("/")[-1]
            new_name = std_name(name, it["mtime"], c["folder"], CAT_NAME.get(c["code"], ""))[0] if rename and self.mode != "일반" else name
            d = os.path.dirname(rel) if d is None else d
            if d == norm(os.path.dirname(rel)) and new_name == name:
                continue
            if c["rank"] in ("JR-1", "JR-2") or in_ref(rel):
                held.append((rel, "RC-19"))
                continue
            ddir = os.path.join(self.dev.root, d)
            taken = {norm(x).lower() for x in os.listdir(ddir)} if os.path.isdir(ddir) else set()
            if norm(d) == norm(os.path.dirname(rel)):
                taken.discard(norm(name).lower())
            new_name = self._free_name(d, new_name, taken)
            new_rel = (d + "/" if d else "") + new_name
            dst = os.path.join(self.dev.root, new_rel)
            rc = None
            if os.path.commonpath([root, os.path.realpath(os.path.dirname(dst) or root)]) != root:
                rc = "RC-21"
            elif len(os.path.abspath(dst)) > 240:
                rc = "RC-13"                              # 운영체제의 경로 한도를 넘으면 건너뛰고 보류로 적는다
            elif rel in self.busy:
                rc = "RC-12"
            if not rc:
                n = self._keep_place(rel, new_rel)
                try:
                    os.makedirs(os.path.dirname(dst) or root, exist_ok=True)
                    os.rename(self.dev.path(rel), dst)    # 같은 기기 안의 옮김. 내용은 건드리지 않는다
                except OSError:
                    rc = "RC-12"
                    self.vmeta[c["asset"]].pop()
            if rc:
                held.append((rel, rc))
                self.led.add("CLS", "배정 보류", res="멈춤", rc=rc, asset=c["asset"], ver=it["ver"])
                continue
            k_old, k_new = self._pkey(self.dev, rel), self._pkey(self.dev, new_rel)
            self.path_asset[k_new] = c["asset"]
            if rel in self.finals:
                self.finals[new_rel] = self.finals.pop(rel)
            if self.known is not None:
                self.known.discard(norm(rel))
                self.known.add(norm(new_rel))
            bb = self.bundles.get(c["bundle"]) if c["bundle"] else None
            if bb and bb["kind"] == "보관" and bb["folder"] == norm(os.path.dirname(rel)).lower():
                bb["folder"], bb["shown"] = norm(d).lower(), d   # 보관 묶음은 폴더째 표준 자리로 간다(묶음 번호는 그대로)
            if norm(d) != norm(os.path.dirname(rel)):
                self.led.add("CLS", "자리 배정", asset=c["asset"], ver=it["ver"], hash=it["hash"], old=rel, new=new_rel, place=c["place_code"], undo=n)
            if new_name != name:
                named += 1
                self.led.add("CLS", "이름 붙임", asset=c["asset"], ver=it["ver"], old_name=name, new_name=new_name, old=rel, new=new_rel, undo=n)
            if k_old in self.place_mem:
                self.place_mem[k_new] = self.place_mem.pop(k_old)
            elif c["asset"]:
                self._remember(k_new, c["asset"], c["code"], c["rank"], "자리 배정")
            moved.append((rel, new_rel))
            self.placed = sorted(set(self.placed) | {norm(new_rel)})
        self.held = held
        self._scan(self.dev, lineage=False)
        return dict(ok=True, moved=len(moved), named=named, held=held, pairs=moved)

    def _new_files(self):
        """GO-3 · NM-06: 다음 훑기에서 처음 보인 파일. 시스템·프로젝트 모드(구독)에서는 표준 자리(와 모드 규칙이면 표준 이름)를 스스로 붙이고,
        일반 모드에서는 표준 이름과 자리를 옆에 보이기만 한다. 확신 중간과 이미 있던 파일은 모아서 한 번의 묶음 제안으로 낸다(AP-05: 다섯 묶음까지)."""
        cur = {norm(r): r for r in self.dev.index}
        first = self.known is None
        new = [] if first else [r for k, r in cur.items() if k not in self.known and not in_ref(r)]
        self.known = set(cur)
        plan = {p["rel"]: p for p in self.plan_places()} if (new or self.mode != "일반") else {}
        for r in new:
            p = plan.get(r)
            if p:
                self.suggest[r] = dict(std_name=p["std_name"], code=p["code"], to=p["to"])
        if self.mode == "일반" or self._gate():
            return
        auto = {r for r in new if (plan[r]["how"] == "자동" or (plan[r]["how"] == "확인 뒤" and plan[r]["conf"] == "중간" and plan[r]["grade"] < "D3" and plan[r]["code"] in self.learned))
                and (plan[r]["moves"] or (self.rename_policy == "모드 규칙" and plan[r]["name_why"]))}
        if auto:
            self._apply(auto, rename=self.rename_policy == "모드 규칙")
        wait = [p for p in self.plan_places() if p["to"] is not None and p["grade"] < "D3" and (p["moves"] or (self.rename_policy == "모드 규칙" and p["name_why"]))
                and not any(p["rel"] == h[0] for h in self.held) and norm(p["rel"]) not in self.no_place and norm(p["rel"]) not in self.placed]
        asked_before = any(p["kind"] == "자리 묶음" for p in self.props.values())
        if wait and (not asked_before or len(wait) >= 5) and not any(p["kind"] == "자리 묶음" and p["state"] == "열림" for p in self.props.values()):
            cats = sorted({p["code"] for p in wait})[:5]
            rels = sorted(p["rel"] for p in wait if p["code"] in cats)
            self._propose("자리 묶음", "자리묶음|" + sha("|".join(rels).encode("utf-8"))[:16],
                          "%d건을 표준 자리%s로 정리할까요(범주 %d개: %s)" % (len(rels), "와 표준 이름" if self.rename_policy == "모드 규칙" else "", len(cats), "·".join(cats)),
                          "정리", "이미 있던 파일과 확신이 중간인 새 파일입니다. 옮기기 전 자리와 이름은 판 목록과 원장에 남아 복구로 되돌릴 수 있습니다",
                          "지금 자리에 그대로 둡니다. 표준 자리와 이름은 옆에 보이기만 합니다", who="한 번", data=dict(rels=rels, cats=cats))

    # ================= OPT =================
    def dup_map(self):
        self.rescan()
        byhash = {}
        for s in self.work_sources():
            for rel, it in s.index.items():
                if it["size"]:
                    byhash.setdefault(it["hash"], []).append((s.dev_id, rel, it["size"]))
        dup = {h: v for h, v in byhash.items() if len(v) > 1}
        deep = self.dup_deep()
        return dict(dup_groups=len(dup), reclaim_bytes=sum(v[0][2] * (len(v) - 1) for v in dup.values()),
                    version_sets=len(self._version_sets()), content_groups=len(deep["content"]), set_dups=len(deep["sets"]), derived=len(deep["derived"])), dup

    def dup_deep(self):
        """중복의 나머지 겹 가운데 표준 라이브러리로 되는 것. 내용 중복(DUP-B, 글자 문서) · 폴더째 겹침(SET) · 압축 ↔ 푼 폴더(DRV).
        색인만 본다(훑기는 부르는 쪽이 한다). 엔진은 지우지 않는다. 무료는 건수만 쓴다(FN-04)."""
        srcs = self.work_sources()
        bych = {}
        for s in srcs:
            for rel, it in s.index.items():
                if it.get("chash") and it["size"]:
                    bych.setdefault(it["chash"], {}).setdefault(it["hash"], []).append((s.dev_id, rel))
        content = [dict(judge="DUP-B", why="겉만 다름(공백·줄바꿈·부호)", where=sorted(x for v in g.values() for x in v)) for g in bych.values() if len(g) > 1]
        fs = [(s.dev_id, f, hs) for s in srcs for f, hs in folder_sets(s.index).items() if len(hs) >= 2]
        sets, seen = [], []
        for i, (d1, f1, h1) in enumerate(sorted(fs, key=lambda x: (x[1].count("/"), x[0], x[1]))):
            for d2, f2, h2 in sorted(fs, key=lambda x: (x[1].count("/"), x[0], x[1]))[i + 1:]:
                if d1 == d2 and (f1.startswith(f2 + "/") or f2.startswith(f1 + "/")):
                    continue                              # 위아래 폴더는 맞대지 않는다
                if any(d1 == a and d2 == b and f1.startswith(x + "/") and f2.startswith(y + "/") for a, x, b, y in seen):
                    continue                              # 위 폴더끼리 이미 같다고 본 것의 아래는 다시 올리지 않는다(낱낱이 묻지 않게)
                inter = len(h1 & h2)
                if not inter:
                    continue
                if h1 == h2:
                    kind = "완전히 같음"
                    seen.append((d1, f1, d2, f2))
                elif h1 <= h2 or h2 <= h1:
                    kind = "한쪽이 다 들어 있음"
                elif inter * 2 >= len(h1 | h2):
                    kind = "%d%% 겹침" % round(100 * inter / len(h1 | h2))
                else:
                    continue
                sets.append(dict(judge="SET", kind=kind, a=(d1, f1, len(h1)), b=(d2, f2, len(h2)), same=inter))
        derived = []
        for s in srcs:
            for rel, it in s.index.items():
                if it["ext"] == "zip" and it["size"]:
                    ls = zip_listing(s.path(rel))
                    if not ls:
                        continue
                    zs = set(ls.values())
                    for d2, f2, h2 in fs:
                        if zs and (zs == h2 or zs <= h2):
                            derived.append(dict(judge="DRV", kind="압축 ↔ 푼 폴더", zip=(s.dev_id, rel), folder=(d2, f2), entries=len(ls),
                                                exact=zs == h2))
        return dict(content=content, sets=sets, derived=derived)

    # ================= SYN: 판 묶기 =================
    def _version_sets(self):
        """같은 것의 판: 이름 줄기와 확장자가 같고, (같은 폴더 자리이거나 글 내용이 반 넘게 겹침). 이름만으로 묶지 않는다."""
        g = {}
        for s in self.work_sources():
            for rel, it in s.index.items():
                if s.flags.get(rel) or it["size"] == 0 or in_package(rel) or it["ext"] in SYS or rel.split("/")[-1].lower() in JUNK:
                    continue                              # 위협 표시 · 빈 파일 · 꾸러미 안(폴더째 두는 것) · 프로그램과 시스템이 만든 파일은 판으로 묶지 않는다(DUP-X)
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
        ia, ib = a[2].get("asset"), b[2].get("asset")
        return bool(ia and ib and self._aid(ia) == self._aid(ib))    # 글이 아닌 것은 같은 자산(계보·같은 자리의 바뀜으로 이어진 것)일 때만. 이름과 폴더만 같은 다른 사진은 묶지 않는다

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
        """바탕이 계보로 확인된 때만 쓴다. 겹치지 않게 고친 것만 합치고, 닿거나 겹치면 None.
        두 쪽이 같은 자리에 줄을 「더하기만」 한 것은 겹침으로 보지 않고 a(먼저 고친 쪽)의 줄 뒤에 b의 줄을 잇는다(어느 쪽도 지우지 않음)."""
        def edits(x):
            out = []
            for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, base, x, autojunk=False).get_opcodes():
                if t == "replace" and i2 - i1 == j2 - j1:  # 줄 수가 같은 바꿈은 줄마다 나눈다(한쪽이 두 줄, 다른 쪽이 그 가운데 한 줄을 고친 것을 줄마다 맞대게)
                    out += [(i1 + n, i1 + n + 1, [x[j1 + n]]) for n in range(i2 - i1) if base[i1 + n] != x[j1 + n]]
                elif t != "equal":
                    out.append((i1, i2, x[j1:j2]))
            return out
        ea, eb = edits(a), edits(b)
        both, same, merged_lines = [], [], []
        for i1, i2, ra in ea:
            for k1, k2, rb in eb:
                if (i1, i2, ra) == (k1, k2, rb):
                    same.append((i1, i2))                  # 두 쪽이 똑같이 고친 대목: 한 번만
                elif i1 == i2 == k1 == k2:
                    both.append((i1, ra, rb))
                elif (i1, i2) == (k1, k2) and len(ra) == len(rb) == i2 - i1 and isinstance(ra[0], str) and len(ra[0]) != 1:
                    lines = [HiDAMApp._merge3(list(base[i1 + n]), list(ra[n]), list(rb[n])) for n in range(i2 - i1)]
                    if any(x is None for x in lines):
                        return None                        # 같은 줄 안에서도 같은 글자를 다르게 고침: 묻는다
                    merged_lines.append((i1, i2, ["".join(x) for x in lines]))   # 같은 줄을 두 쪽이 고쳤어도 글자 단위로 겹치지 않으면(줄 끝에 덧붙임 등) 합친다
                elif max(i1, k1) < min(i2, k2) or (i1 == i2 and k1 < i1 < k2) or (k1 == k2 and i1 < k1 < i2):
                    return None                            # 같은 줄을 다르게 고침(겹침): 묻는다. 맞닿은 줄을 따로 고친 것은 겹침이 아니다
        ins = {i: (ra, rb) for i, ra, rb in both}
        ea = [e for e in ea if not (e[0] == e[1] and e[0] in ins)]
        ml = {(i1, i2) for i1, i2, _ in merged_lines}
        ea = [e for e in ea if (e[0], e[1]) not in ml]
        eb = [e for e in eb if not (e[0] == e[1] and e[0] in ins) and (e[0], e[1]) not in same and (e[0], e[1]) not in ml]
        ed = sorted([(i1, i2, rep) for i1, i2, rep in ea + eb + merged_lines] + [(i, i, ra if ra == rb else ra + rb) for i, (ra, rb) in ins.items()],
                    key=lambda e: (e[0], e[1] > e[0], e[1]))
        out, pos = [], 0
        for i1, i2, rep in ed:
            out += base[pos:i1] + rep
            pos = i2
        return out + base[pos:]

    def _ancs(self, h):
        seen, todo = {h}, [h]
        while todo:
            for p in self.anc.get(todo.pop(), ()):
                if p not in seen:
                    seen.add(p)
                    todo.append(p)
        return seen

    def _lineage_merge(self, uniq, hs, e, row):
        """두 매체에서 번갈아 고친 문서: 판들의 끝(다른 판의 앞이 아닌 것)을 계보로 확인된 바탕에서 차례로 합친다.
        바탕은 두 끝이 함께 닿는 가장 가까운 앞 판이고, 그 내용은 엔진이 남겨 둔 바탕이나 판 보관에서 읽는다. 한 곳이라도 겹치면 합치지 않는다."""
        if e not in TEXT:
            return False
        heads = [h for h in hs if not any(o != h and self._desc(o, h) for o in hs)]
        if len(heads) < 2:
            return False
        txt = {}
        for h in heads:
            t = decode(open(uniq[h][0].path(uniq[h][1]), "rb").read())
            if not t:
                return False
            txt[h] = t
        heads.sort(key=lambda h: (uniq[h][2].get("mtime") or 0, h))      # 먼저 고친 쪽부터(꽂는 순서와 무관)
        cur, cur_anc = txt[heads[0]][0].splitlines(), self._ancs(heads[0])
        for h in heads[1:]:
            other = self._ancs(h)
            common = cur_anc & other
            if not common:
                return False
            near = sorted(c for c in common if not any(o != c and o in common and self._desc(o, c) for o in common))
            base = next((b for b in (self._old_bytes(c) for c in near) if b is not None), None)
            bt = decode(base) if base is not None else None
            if not bt:
                return False
            mg = self._merge3(bt[0].splitlines(), cur, txt[h][0].splitlines())
            if mg is None:
                return False
            cur, cur_anc = mg, cur_anc | other
        t0 = txt[heads[0]]
        enc, nl = t0[1], t0[2]
        data = (nl.join(cur) + (nl if t0[0].endswith(("\n", "\r\n")) else "")).encode("utf-8" if enc.startswith("utf") else enc)
        row.update(judge="SY-갈라짐", how="자동 합침", why="두 매체에서 번갈아 고침 — 계보로 확인된 바탕에서 겹치지 않게 고친 대목을 합침(앞 판들은 판 보관)")
        self._final_write(row, data, parents=heads)
        return True

    # ================= SYN: 정합 =================
    @op("사용자가 누름")
    def reconcile(self):
        if self.tier != "구독":                          # 무료: 엇갈린 건수만
            self.rescan()
            n = len(self._version_sets())
            self.led.add("SYN", "거절", res="거절", rc="RC-01", why="무료 층 — 건수만", unsettled=n)
            return dict(unsettled=n, note="정합 동기화는 구독 기능입니다")
        self.rescan()
        res, open_keys = [], set()
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
                        self._cur_items = items
                        if not self._lineage_merge(uniq, hs, e, row):
                            self._diverged(uniq, hs, e, row)
            wait = row["how"] in ("확인 필요", "사용자가 고름", "자동에서 뺌")
            self.led.add("SYN", "정합 판정", stem=stem, judge=row["judge"], how=row["how"], res="멈춤" if wait else "됨", rc=("RC-10" if row["judge"] == "SY-보류" else "RC-23") if wait else None)
            if wait:                                      # 묻는 것은 제안 목록 한 곳으로 낸다. 권하는 답이 있으면 먼저 보인다
                pk = "판|%s|%s|%d|%s" % (stem, e, gi, sha("".join(sorted(hs)).encode())[:12])
                open_keys.add(pk)
                self._propose("판 고르기", pk, "「%s.%s」의 판 %d개 가운데 최종본을 골라 주세요" % (stem, e, len(hs)), row.get("suggest"), row["why"],
                              "최종본을 만들지 않고 기다립니다. 매체의 판은 그대로 있고 거울로도 가지 않습니다", who="한 번", data=dict(stem=stem, ext=e, gi=gi))
            res.append(row)
        for k, no in self.pkeys.items():
            if k.startswith("판|") and k not in open_keys:
                self._close(k)
        self._scan(self.dev)                             # 방금 만든 최종본을 색인에 넣는다(그 뒤의 고침이 계보로 이어지게)
        self.last_wait = [r["stem"] for r in res if r["how"] in ("확인 필요", "사용자가 고름", "자동에서 뺌")]
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
            mt = {h: 0 for h in hs}                       # 고친 시각: 사용자가 둔 사본의 시각만 본다(엔진이 만든 기준자리 사본의 시각은 셈하지 않음)
            for s_, r_, it_ in (self._cur_items or []):
                if it_["hash"] in mt and not in_ref(r_):
                    mt[it_["hash"]] = max(mt[it_["hash"]], it_.get("mtime") or 0)
            if sup and all(mt[sup[0]] >= mt[o] for o in hs):  # 다른 판의 줄을 다 담고 있고 가장 나중에 고친 판: 더하기만 한 고침이다(줄을 지운 고침이면 지운 쪽이 더 나중)
                row.update(judge="SY-최신", how="자동", why="계보는 없으나 %s의 판이 다른 판의 줄을 다 담고 가장 나중에 고쳐짐 — 앞 판들은 판 보관(되돌릴 수 있음)" % uniq[sup[0]][0].dev_id)
                self._final_copy(uniq[sup[0]], row)
                for o in hs:
                    if o != sup[0]:
                        self._link(sup[0], o)
                return
            if sup:
                row.update(judge="SY-제안", how="확인 필요", suggest=uniq[sup[0]][0].dev_id,
                           why="계보가 없음. %s의 판이 다른 판의 줄을 다 담고 있어 최신으로 보이나, 다른 판이 더 나중에 고쳐져 줄을 지운 고침일 수 있음 — 확인을 받음" % uniq[sup[0]][0].dev_id)
                return
            sub = [b for b in hs if all(self._contains(lines[o], lines[b]) for o in hs) and all(mt[b] <= mt[o] for o in hs)]
            if sub and len(hs) >= 3:                      # 모두가 담고 있는 가장 이른 판을 바탕으로: 저마다 더한 것을 겹치지 않게 합친다
                base, rest = sub[0], sorted((h for h in hs if h != sub[0]), key=lambda h: (mt[h], h))
                cur = lines[rest[0]]
                for h in rest[1:]:
                    cur = self._merge3(lines[base], cur, lines[h]) if cur is not None else None
                if cur is not None:
                    enc, nl = txt[base][1], txt[base][2]
                    data = (nl.join(cur) + (nl if txt[base][0].endswith(("\n", "\r\n")) else "")).encode("utf-8" if enc.startswith("utf") else enc)
                    row.update(judge="SY-갈라짐", how="자동 합침", why="계보는 없으나 가장 이른 판을 모두가 담고 있음 — 저마다 더한 대목을 합침(앞 판들은 판 보관)")
                    self._final_write(row, data, parents=hs)
                    return
            row.update(judge="SY-갈라짐", how="사용자가 고름", why="계보가 없고 서로 없는 내용이 있음 — 나란히 보여 줌")
            return
        row.update(judge="SY-갈라짐", how="사용자가 고름", why="글자 문서가 아니거나 읽지 못하는 부호 — 차이를 보여 주고 고르게 함")

    @op("사용자 결정")
    def choose(self, stem, ext, dev_id, gi=0):
        """사용자가 판을 고른다(SY-제안·SY-갈라짐·SY-보류에 대한 답). 정합은 구독 기능이다."""
        if self.tier != "구독":
            self.led.add("SYN", "거절", actor="사용자", res="거절", rc="RC-01", why="무료 층")
            return None
        items = self._version_sets().get((stem, ext, gi))
        pick = next((x for x in items if x[0].dev_id == dev_id), None) if items else None
        if not pick:
            self.led.add("SYN", "거절", actor="사용자", res="거절", rc="RC-22", why="그 무리나 매체의 판이 없음")
            return None
        self.decided[(stem, ext, gi)] = dict(hash=pick[2]["hash"], seen={x[2]["hash"] for x in items})
        for x in items:
            if x[2]["hash"] != pick[2]["hash"]:
                self._link(pick[2]["hash"], x[2]["hash"])
        self.led.add("SYN", "사용자 결정", actor="사용자", what="판 고름", stem=stem, medium=dev_id)
        row = dict(final=None, force=True)                # 사용자가 고른 것은 앞 최종본과 계보가 닿지 않아도 그 자리에 놓는다(앞 것은 판 보관)
        self._final_copy(pick, row)
        self._scan(self.dev)
        return row["final"]

    def _final_rel(self, it, rel, rel_src):
        """최종본의 자리: 기준자리 아래에 원래 폴더를 지키고, 이름은 고른 판의 이름에서 꾸밈말만 뗀다(글자 모양은 그대로)."""
        if rel_src and in_ref(rel_src):
            return rel_src
        d = it["dir"] if it["dir"] not in ("", "기준자리") else ""
        if d.startswith("기준자리/"):
            d = d[len("기준자리/"):]
        name = rel.split("/")[-1]
        dot = ("." + name.rsplit(".", 1)[1]) if it["ext"] else ""
        return "기준자리/" + (d + "/" if d and not d.startswith("기준자리") else "") + stem_cut(name) + dot

    def _final_copy(self, picked, row):
        s, rel, it = picked
        data = open(s.path(rel), "rb").read()            # 고른 판의 바이트 그대로
        frel = self._final_rel(it, rel, rel if s is self.dev else "")
        row["final_from"] = [s.dev_id]
        self._put_final(frel, data, row, parents=[])

    def _final_write(self, row, data, parents):
        any_item = self._cur_items[0]                     # 지금 맞추고 있는 그 무리의 자리(이름 줄기가 같은 다른 무리의 자리가 아니다)
        frel = self._final_rel(any_item[2], any_item[1], "")
        row["final_from"] = sorted({x for x, _ in row["where"]})
        self._put_final(frel, data, row, parents=parents)

    def _put_final(self, frel, data, row, parents):
        h, base, n = sha(data), frel, 1
        kin = lambda a, b: a == b or self._desc(a, b) or self._desc(b, a) or (a in self.ver2asset and self._aid(self.ver2asset[a]) == self._aid(self.ver2asset.get(b, "")))
        while os.path.exists(self.dev.path(frel)):        # 그 자리에 이미 있는 것이 「같은 것」(같은 내용 · 계보가 닿음 · 같은 자산)일 때만 그 자리를 쓴다
            cur = sha(self._bytes(self.dev, frel))
            if cur == h or row.get("force") or any(kin(x, cur) for x in [h] + list(parents)):
                break
            n += 1                                        # 이름만 같은 다른 것의 최종본(또는 사용자가 둔 다른 글)이다: 덮지 않고 순번을 붙인 자리로
            stem, dot = (base.rsplit(".", 1)[0], "." + base.rsplit(".", 1)[1]) if "." in base.split("/")[-1] else (base, "")
            frel = "%s_%d%s" % (stem, n, dot)
        p = self.dev.path(frel)
        row["final"] = frel
        if os.path.exists(p):
            cur = sha(open(p, "rb").read())
            if cur == h:
                self.finals[frel] = h
                return
            self._keep_version(frel)
            self._link(h, cur)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)
        for ph in parents:
            if ph != h:
                self._link(h, ph)
        self.finals[frel] = h
        aid = self.ver2asset.get(h) or self.path_asset.get(self._pkey(self.dev, frel))
        self.led.add("SYN", "최종본", cause="정합", rel=frel, asset=self._aid(aid) if aid else None, ver=ver_id(data), hash=h, src=row.get("final_from"))

    # ================= LED: 판 보관 · 복구 =================
    def _vdir(self, aid):
        d = os.path.join(self.vers, sha(aid.encode("utf-8"))[:16])      # 자산마다 따로(이름을 바꿔도 같은 자리, 다른 자산과 섞이지 않게)
        os.makedirs(d, exist_ok=True)
        return d

    def _asset_at(self, rel, data=None):
        """그 자리의 자산. 색인에 아직 없으면 지금 내용으로 등록한다."""
        k = self._pkey(self.dev, rel)
        if data is not None:
            h = sha(data)
            aid = self.ver2asset.get(h)
            if aid is None:
                prev = self.path_asset.get(k)
                aid = self._join(h, prev) if prev and self._aid(prev) in self.assets else self._new_asset(h, len(data))
            elif k in self.path_asset and self._aid(self.path_asset[k]) != self._aid(aid):
                return self._aid(self.path_asset[k])
            self.path_asset.setdefault(k, self._aid(aid))
        a = self.path_asset.get(k)
        return self._aid(a) if a else None

    def _keep_version(self, rel):
        src = self.dev.path(rel)
        data = open(src, "rb").read()
        aid = self._asset_at(rel, data)
        lst = self.vmeta.setdefault(aid, [])
        n = len(lst) + 1
        shutil.copy2(src, os.path.join(self._vdir(aid), "v%d" % n))
        lst.append(dict(ver=n, kind="내용", rel=rel, hash=sha(data), at=now_z()))
        self.led.add("LED", "판 보관", rel=rel, ver=n, aid=aid, asset=aid, vid=ver_id(data), hash=sha(data))
        return n

    def _keep_place(self, rel, new_rel):
        """옮기기·이름 바꾸기 전의 자리와 이름을 판 목록에 남긴다(바이트는 그대로이므로 자리만 적는다)."""
        it = self.dev.index[rel]
        aid = self._asset_at(rel, open(self.dev.path(rel), "rb").read())
        lst = self.vmeta.setdefault(aid, [])
        n = len(lst) + 1
        lst.append(dict(ver=n, kind="자리", rel=rel, hash=it["hash"], to=new_rel, at=now_z()))
        self.led.add("LED", "자리 판 보관", rel=rel, ver=n, aid=aid, hash=it["hash"], to=new_rel)
        return n

    def versions(self, rel):
        """그 자리(지금 자리든 옛 자리든)의 자산이 가진 판 목록: 번호 · 내용/자리 · 그때의 자리와 이름."""
        aid = self._asset_at(rel)
        return [dict(v) for v in self.vmeta.get(aid, [])] if aid else []

    @op("복구", actor="사용자")
    def recover(self, rel, ver, beta=None):
        """판을 골라 되돌린다. 「내용」 판은 그 내용을, 「자리」 판은 그때의 자리와 이름을 되돌린다. 횟수는 자산으로 센다(이름을 바꿔도 다시 생기지 않는다)."""
        beta = self.beta if beta is None else beta
        aid = self._asset_at(rel) or ("자리:" + norm(rel))
        used = self.recover_count.get(aid, 0)
        limit = None if self.tier == "구독" else (5 if beta else 2)
        note = None if self.tier == "구독" else "※ 책임지는 복구(원복)는 구독 서비스에 한합니다."
        name = "복구(원복)" if self.tier == "구독" else "복구(되돌리기)"
        if limit is not None and used >= limit and not beta:
            self.led.add("LED", "복구 한도", res="거절", rc="RC-08", rel=rel, used=used, asset=aid)
            return dict(ok=False, name=name, note=note, left=0, guide="구독 안내")
        meta = next((v for v in self.vmeta.get(aid, []) if v["ver"] == ver), None)
        src = os.path.join(self._vdir(aid), "v%d" % ver) if meta and meta["kind"] == "내용" else None
        if not meta or (src and not os.path.exists(src)):
            self.led.add("LED", "복구 실패", res="실패", rc="RC-09", rel=rel, ver=ver, why="그 판이 없음")
            return dict(ok=False, name=name, note=note, why="그 판이 없음")
        if meta["kind"] == "자리":                        # 자리·이름 되돌리기: 그 자산의 지금 사본을 옛 자리로 옮긴다
            self._scan(self.dev, lineage=False)
            cur = next((r for r, it in sorted(self.dev.index.items()) if it.get("asset") and self._aid(it["asset"]) == aid and r == meta.get("to")), None) \
                or next((r for r, it in sorted(self.dev.index.items()) if it.get("asset") and self._aid(it["asset"]) == aid and r != meta["rel"]), None)
            dst = self.dev.path(meta["rel"])
            if not cur or os.path.exists(dst):
                self.led.add("LED", "복구 실패", res="실패", rc="RC-22", rel=rel, ver=ver, why="옮긴 사본을 찾지 못했거나 옛 자리에 다른 파일이 있음")
                return dict(ok=False, name=name, note=note, why="옮긴 사본을 찾지 못했거나 옛 자리에 다른 파일이 있음")
            self._keep_place(cur, meta["rel"])
            os.makedirs(os.path.dirname(dst) or self.dev.root, exist_ok=True)
            os.rename(self.dev.path(cur), dst)
            if cur in self.finals:
                self.finals[meta["rel"]] = self.finals.pop(cur)
            if self.known is not None:
                self.known.discard(norm(cur))
                self.known.add(norm(meta["rel"]))
            self._scan(self.dev, lineage=False)
            self.recover_count[aid] = used + 1
            self.led.add("LED", "복구", rel=meta["rel"], ver=ver, tier=self.tier, what="자리·이름", old=cur, asset=aid)
        else:
            data, p = open(src, "rb").read(), self.dev.path(rel)
            if os.path.exists(p):
                cur = sha(open(p, "rb").read())
                self._keep_version(rel)
            else:
                cur = None
                os.makedirs(os.path.dirname(p) or self.dev.root, exist_ok=True)
            shutil.copy2(src, p)
            h = sha(data)
            it = dict(stem=stem_of(os.path.basename(rel)), ext=ext_of(rel))
            sets_ = [(k, v) for k, v in self._version_sets().items() if k[0] == it["stem"] and k[1] == it["ext"]]
            for key, items in sets_ or [((it["stem"], it["ext"], 0), [])]:   # 복구는 사용자의 결정이다. 그 무리의 다른 판을 모두 「본 것」으로 적는다(자동 실행이 되돌리지 않게)
                self.decided[key] = dict(hash=h, seen={x[2]["hash"] for x in items} | {h} | ({cur} if cur else set()))
            self.finals[rel] = h
            self._scan(self.dev, lineage=False)
            self.recover_count[aid] = used + 1
            self.led.add("LED", "복구", rel=rel, ver=ver, tier=self.tier, what="내용", asset=aid)
        return dict(ok=True, name=name, note=note, left=None if limit is None else max(limit - used - 1, 0),
                    guide="구독 안내(베타 기간에는 계속 해 드립니다)" if (beta and limit is not None and used + 1 >= limit) else None)

    # ================= SYN: 거울 =================
    def mirror_set(self, m):
        """거울에 비출 것: 기기의 자산 가운데 엇갈림이 풀린 것, 보호 등급 아래, 매체의 범위(scope)에 드는 것."""
        unsettled = {rel for items in self._version_sets().values() for s, rel, _ in items if s is self.dev}
        want, skipped, vault = {}, [], {}
        for rel, it in self.dev.index.items():
            j = self.judge(self.dev, rel)
            if j["grade"] >= "D3":
                if not (self.dev.flags.get(rel) or (rel in unsettled and rel not in self.finals)):
                    vault[rel] = it["hash"]                # 보호 등급: 그대로 비추지 않고 금고 거울로(잠가서)
                else:
                    skipped.append((rel, "보호 등급 — 엇갈림이나 위협 표시가 있어 금고에도 보내지 않음"))
            elif self.dev.flags.get(rel):
                skipped.append((rel, "위협 표시 — 거울로 보내지 않음"))
            elif rel in unsettled and rel not in self.finals:
                skipped.append((rel, "판이 엇갈림 — 정합 먼저"))
            elif m.scope and not (j["code"].startswith(m.scope) or (j["project"] or "").startswith(m.scope)):
                continue
            else:
                want[rel] = it["hash"]
        self._vault_want = vault
        return want, skipped

    def _vault_key(self):
        p = os.path.join(self.home, "00.10_금고열쇠.key")
        if not os.path.exists(p):
            with open(p + ".tmp", "wb") as f:
                f.write(os.urandom(32))
            os.replace(p + ".tmp", p)
        k = open(p, "rb").read()
        return k if len(k) == 32 else None

    def _vault_mirror(self, m):
        """보호 등급 자산을 거울 매체의 _HiDAM_금고에 잠가서 비춘다(이름도 잠금, 바깥 파일 이름은 해시). 쓰고 나서 열어 해시를 맞댄다."""
        want = dict(self._vault_want)
        if not want and not self.vault.get(m.dev_id):
            return dict(done=0, kept=0, stopped=None)
        try:
            key = self._vault_key()
        except OSError:
            key = None
        if not key:
            self.led.add("SYN", "금고 거울 멈춤", res="멈춤", rc="RC-28", medium=m.dev_id)
            return dict(done=0, kept=0, stopped="금고 열쇠 없음")
        vroot = os.path.join(m.root, "_HiDAM_금고")
        have = self.vault.setdefault(m.dev_id, {})
        done_n = 0
        for rel, h in sorted(want.items()):
            fn = os.path.join(vroot, sha(rel.encode("utf-8"))[:32] + ".hv")
            if have.get(rel) == h and os.path.exists(fn):
                continue
            data = self._bytes(self.dev, rel)
            if sha(data) != h:
                continue
            try:
                os.makedirs(vroot, exist_ok=True)
                with open(fn + ".hidam_tmp", "wb") as f:
                    f.write(vault_seal(key, rel, data))
                back = vault_open(key, open(fn + ".hidam_tmp", "rb").read())
                if not back or back[0] != rel or sha(back[1]) != h:
                    os.remove(fn + ".hidam_tmp")
                    self.led.add("SYN", "거절", res="거절", rc="RC-07", why="금고 해시 불일치", medium=m.dev_id, grade="M2")
                    continue
                os.replace(fn + ".hidam_tmp", fn)
            except OSError:
                try:
                    os.path.exists(fn + ".hidam_tmp") and os.remove(fn + ".hidam_tmp")
                except OSError:
                    pass
                self.led.add("SYN", "금고 거울 멈춤", res="멈춤", rc="RC-24", medium=m.dev_id, done=done_n)
                return dict(done=done_n, kept=len(have), stopped="매체에 쓰지 못함 — 공간을 확인해 주세요")
            have[rel] = h
            done_n += 1
        if done_n:
            self.led.add("SYN", "금고 거울", medium=m.dev_id, done=done_n, kept=len(have))
        return dict(done=done_n, kept=len(have), stopped=None)

    def vault_restore(self, dev_id, rel):
        """금고 거울에서 그 자산을 열어 돌려준다(기기에는 쓰지 않는다. 복구는 사용자가 고른 자리에)."""
        m = self.media.get(dev_id)
        key_p = os.path.join(self.home, "00.10_금고열쇠.key")
        if not m or not os.path.exists(key_p):
            return None
        fn = os.path.join(m.root, "_HiDAM_금고", sha(rel.encode("utf-8"))[:32] + ".hv")
        if not os.path.exists(fn):
            return None
        back = vault_open(open(key_p, "rb").read(), open(fn, "rb").read())
        return back[1] if back and back[0] == rel else None

    @op("사용자가 누름")
    def mirror(self, dev_id, auto=False):
        m = self.media[dev_id]
        if self.tier != "구독":
            self.led.add("SYN", "거절", res="거절", rc="RC-01", why="무료 층", medium=dev_id)
            return dict(done=0, stopped="미러링은 구독 기능입니다")
        if not m.plugged or m.blocked or not os.path.isdir(m.root):
            return dict(done=0, stopped="매체 사용 불가")
        if m.role != "거울":
            return dict(done=0, stopped="거울 역할이 아닌 매체")
        if not m.first_ok:
            want, sk = self.mirror_set(m)
            self._propose("첫 미러링", "첫거울|%s|%s" % (dev_id, m.scope), "매체 %s에 처음으로 비춥니다. 비출 것은 %d건, 금고(잠가서)로 갈 보호 등급은 %d건입니다" % (dev_id, len(want), len(self._vault_want)), "비춤",
                          "처음 등록한 매체의 첫 미러링은 미리 보기와 확인을 받습니다(MR-15)", "이 매체로는 비추지 않습니다", who="한 번", data=dict(dev=dev_id))
            return dict(done=0, stopped="첫 미러링 — 미리 보기와 확인 필요", preview=len(want))
        self._scan(self.dev)
        mroot = os.path.join(m.root, "_HiDAM_거울")
        os.makedirs(mroot, exist_ok=True)
        want, skipped = self.mirror_set(m)
        have = {}
        for d, _, fs in os.walk(mroot):
            for f in fs:
                p = os.path.join(d, f)
                if f.endswith(".hidam_tmp"):              # 앞 미러링이 쓰다 만 엔진의 임시 파일: 거울이 아니다
                    try:
                        os.remove(p)
                    except OSError:
                        pass
                    continue
                have[os.path.relpath(p, mroot).replace("\\", "/")] = sha(self._bytes(Medium("", mroot), os.path.relpath(p, mroot)))
        change, gone = [r for r in want if have.get(r) != want[r]], [r for r in have if r not in want]
        altered = [r for r in change if r in have]       # 새로 생긴 것은 대량 변경으로 세지 않는다
        if auto and ((len(have) >= 10 and (len(altered) + len(gone)) / len(have) > self.mass_ratio) or (len(have) >= 3 and len(gone) == len(have))):
            self._propose("대량 변경", "대량|%s|%s" % (dev_id, sha("".join(sorted(altered + gone)).encode("utf-8"))[:12]),
                          "매체 %s의 거울에서 %d건이 한꺼번에 바뀌거나 물러납니다. 그대로 비출까요" % (dev_id, len(altered) + len(gone)), "비춤",
                          "대량 변경은 잘못 지웠거나 감염된 것이 거울까지 번지는 것을 막으려고 멈춥니다(MR-16)", "거울은 앞 모습 그대로 있습니다", who="한 번", data=dict(dev=dev_id))
            self.led.add("SYN", "자동 미러링 멈춤", res="멈춤", rc="RC-06", medium=dev_id, why="대량 변경", change=len(change), gone=len(gone), grade="M3")
            return dict(done=0, stopped="대량 변경 — 확인 필요")
        bad, done_n = 0, 0
        for r in change:
            dst = os.path.join(mroot, r)
            tmp = dst + ".hidam_tmp"
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(self.dev.path(r), tmp)
            except OSError:                               # 공간 부족 등: 죽지 않고 멈춘다. 쓰다 만 것은 치우고 앞 거울은 그대로 둔다(AP-08)
                try:
                    os.path.exists(tmp) and os.remove(tmp)
                except OSError:
                    pass
                self.led.add("SYN", "미러링 멈춤", res="멈춤", rc="RC-24", medium=dev_id, done=done_n, left=len(change) - done_n, grade="M2")
                return dict(done=done_n, held=0, mismatch=bad, skipped=len(skipped), stopped="매체에 쓰지 못함 — 공간을 확인해 주세요")
            done_n += 1
            if sha(open(tmp, "rb").read()) != want[r]:
                os.remove(tmp)                            # 앞 거울은 그대로 둔다
                bad += 1
                self.led.add("SYN", "거절", res="거절", rc="RC-07", why="해시 불일치", medium=dev_id, rel=r, grade="M2")
            else:
                os.replace(tmp, dst)
        for r in gone:                                    # 지워진 것은 보류함으로
            hd = os.path.join(m.root, "_HiDAM_보류함", r)
            try:
                os.makedirs(os.path.dirname(hd), exist_ok=True)
                shutil.move(os.path.join(mroot, r), hd)
            except OSError:
                pass
        vr = self._vault_mirror(m)
        out = dict(done=len(change) - bad, held=len(gone), mismatch=bad, skipped=len(skipped), stopped=vr["stopped"], vault=vr["done"], vault_kept=vr["kept"])
        self.skipped = skipped
        if dev_id not in self.mirror_order:
            self.mirror_order.append(dev_id)              # 거울 n: 등록 순. 매체를 빼도 번호를 다시 쓰지 않는다(ID-16)
        self.led.add("SYN", "미러링", medium=dev_id, auto=auto, done=out["done"], held=out["held"], mismatch=bad, skipped=len(skipped),
                     mirror_no=self.mirror_order.index(dev_id) + 1)
        return out

    @op(lambda self, trigger: {"꽂으면": "꽂음", "바뀌면": "바뀜", "때 되면": "때 됨"}.get(trigger, "때 됨"), actor="자동 실행")
    def auto_run(self, trigger):
        """AP-01~12: (검사는 plug에서) → 다시 읽기 → 판정·제안·새 파일에 이름과 자리 → 정합 → 거울 → 기록."""
        if self.tier != "구독" or not self.auto:
            return None
        self._tick()
        rec = self.reconcile()
        res = {d: self.mirror(d, auto=True) for d, m in self.media.items() if m.plugged and not m.blocked and m.role == "거울"}
        stopped = ["%s(%s)" % (d, r["stopped"]) for d, r in res.items() if r["stopped"]]
        wait = [r["stem"] for r in rec if r["how"] in ("확인 필요", "사용자가 고름", "자동에서 뺌")]
        self.last_auto = dict(trigger=trigger, mirrored=sum(r["done"] for r in res.values()), reconciled=len(rec), waiting=wait,
                              result=("멈춤: " + ", ".join(stopped)) if stopped else ("확인 대기 %d건" % len(wait) if wait else "정상"))
        self.led.add("SYN", "자동 실행", trigger=trigger, mirrored=self.last_auto["mirrored"], waiting=len(wait), result=self.last_auto["result"],
                     res="멈춤" if stopped else "됨", rc=("RC-06" if "대량" in stopped[0] else "RC-11" if "첫 미러링" in stopped[0] else "RC-20") if stopped else None)
        return self.last_auto

    # ================= 8. 프로젝트(PJT) =================
    def _pfiles(self, b):
        """프로젝트 묶음 안의 파일: (rel, 갈래, 자산, 색인 줄). 갈래는 묶음 폴더 바로 아래 폴더부터 읽는다."""
        out, depth = [], b["folder"].count("/") + 1
        for rel, it in sorted(self.dev.index.items()):
            low = norm(rel).lower()
            if low.startswith(b["folder"] + "/") and it.get("asset"):
                g = next((x for x in map(gal_of, norm(rel).split("/")[depth:-1]) if x), None)
                out.append((rel, g, self._aid(it["asset"]), it))
        return out

    def _alive(self, h):
        """그 판이 어딘가에 남아 있는가(기기·매체의 색인, 판 보관)."""
        if any(it["hash"] == h for s in [self.dev] + list(self.media.values()) for it in s.index.values()):
            return True
        return any(v.get("hash") == h and v["kind"] == "내용" for lst in self.vmeta.values() for v in lst)

    def _project_tick(self):
        for b in [x for x in self.bundles.values() if x["kind"] == "프로젝트" and x["state"] == "씀" and x["dev"] == self.dev.dev_id]:
            files = self._pfiles(b)
            new = []
            for rel, g, aid, it in files:                 # 산출물 번호 = 묶음-갈래.순번(갈래 폴더에 놓인 차례). 자산에 붙으므로 내용·이름이 바뀌어도 그대로다
                if g and aid not in b["outs"]:
                    b["oseq"][g] = b["oseq"].get(g, 0) + 1
                    b["outs"][aid] = dict(no="%s.%02d" % (g, b["oseq"][g]), gal=g)
                    new.append((rel, g, aid, it))
                    self._note("PJT", "산출물 번호", bundle=b["id"], out="%s-%s" % (b["id"], b["outs"][aid]["no"]), asset=aid, ver=it["ver"])
            cur = {aid: it["hash"] for _, _, aid, it in files if aid in b["outs"]}
            deliver = {b["outs"][a]["no"]: h for a, h in cur.items() if b["outs"][a]["gal"] not in ("00", "07", "09", "10")}
            ph = max([GAL_PHASE.get(b["outs"][a]["gal"], 0) for a in cur] or [0])
            if b.get("phase_set") is None and ph and ph != b["phase"]:   # 국면이 넘어갈 때 그때의 판 묶음을 기준선으로 고정한다
                self._to_phase(b, ph, deliver, "엔진이 갈래에서 읽음")
            for rel, g, aid, it in new:
                name = rel.split("/")[-1]
                if g == "07" and any(has_word(name, w) for w in ("검수조서", "검수", "승인", "점검")):
                    n = len(b["ac"]) + 1
                    pts = {k: v for k, v in deliver.items()}
                    b["ac"].append(dict(no="AC%02d" % n, doc=aid, doc_hash=it["hash"], points=pts, result=None, at=now_z()))
                    self._note("PJT", "검수", bundle=b["id"], ac="AC%02d" % n, points=len(pts))
                    self._evidence(b, "AC%02d" % n, pts)
                elif g == "09":
                    ids = re.findall(r"AU\d\d-\d{3}", name)
                    if has_word(name, "조치", TAILS + ("결과", "완료", "보고", "보고서", "계획", "확인")) and ids:
                        for f in b["finds"]:
                            if f["no"] in ids and f["state"] in ("미조치", "조치 중"):
                                f.update(state="조치 완료", by=aid, by_hash=it["hash"])   # 제시: 조치 문서가 놓임 → 조치 완료로 적어 둔다(사용자가 바꿀 수 있음)
                                self._note("PJT", "지적·조치", bundle=b["id"], find=f["no"], state="조치 완료", how="제시")
                    else:
                        n = len(b["au"]) + 1
                        b["au"].append(dict(no="AU%02d" % n, doc=aid, doc_hash=it["hash"], points=dict(deliver), at=now_z()))
                        self._note("PJT", "감리", bundle=b["id"], au="AU%02d" % n, points=len(deliver))
                        self._evidence(b, "AU%02d" % n, deliver)
            for f in b["finds"]:                          # 제시: 지적이 가리킨 산출물의 판이 올랐으면 「조치 중」
                if f["state"] == "미조치" and f.get("out") and deliver.get(f["out"]) not in (None, f.get("hash")):
                    f["state"] = "조치 중"
                    self._note("PJT", "지적·조치", bundle=b["id"], find=f["no"], state="조치 중", how="제시")
            chk = self.project_checks(b["id"])
            sig = sha(json.dumps(chk, ensure_ascii=False, sort_keys=True).encode())
            if sig != b["last_checks"]:
                b["last_checks"] = sig
                kinds = {}
                for c in chk:
                    kinds[c["check"]] = kinds.get(c["check"], 0) + 1
                self._note("PJT", "검사 결과", bundle=b["id"], found=len(chk), kinds=kinds)

    def _to_phase(self, b, ph, deliver, how):
        n = len(b["bl"]) + 1
        b["bl"].append(dict(no="BL%02d" % n, at=now_z(), frm=b["phase"], to=ph, items=dict(deliver)))
        self._note("PJT", "국면 바뀜", bundle=b["id"], old=b["phase"], new="PH%d" % ph, how=how)
        self._note("PJT", "기준선", bundle=b["id"], bl="BL%02d" % n, items=len(deliver))
        b["phase"] = ph

    def _evidence(self, b, ref, pts):
        n = len(b["ep"]) + 1
        b["ep"].append(dict(no="EP%02d" % n, ref=ref, items=dict(pts), at=now_z()))
        self._note("PJT", "증적 묶음", bundle=b["id"], ep="EP%02d" % n, ref=ref, items=len(pts))

    def _outs_now(self, b):
        return {b["outs"][aid]["no"]: (rel, it["hash"], aid) for rel, g, aid, it in self._pfiles(b) if aid in b["outs"]}

    @op("사용자 결정")
    def set_phase(self, bid, ph):
        """국면은 엔진이 갈래에서 읽어 제시하고 사용자가 바꿀 수 있다(PH0~PH6). 되돌릴 수도 있고 사건으로 남는다."""
        b = self.bundles[bid]
        self._to_phase(b, ph, {k: v[1] for k, v in self._outs_now(b).items() if k[:2] not in ("00", "07", "09", "10")}, "사용자가 정함")
        b["phase_set"] = ph

    @op("사용자 결정")
    def set_ac_result(self, bid, ac, result):
        assert result in ("합격", "조건부", "불합격")
        next(a for a in self.bundles[bid]["ac"] if a["no"] == ac)["result"] = result
        self.led.add("PJT", "검수", actor="사용자", bundle=bid, ac=ac, result=result)

    @op("사용자가 누름")
    def add_finding(self, bid, au, out_no=None):
        """감리 지적 한 건(AUnn-nnn). 가리키는 것은 산출물의 판이다(PJ-04). 엔진은 파일 안의 글을 읽지 않으므로 지적은 화면·확장판이 넣는다."""
        b = self.bundles[bid]
        n = 1 + sum(1 for f in b["finds"] if f["au"] == au)
        h = self._outs_now(b).get(out_no, (None, None))[1] if out_no else None
        f = dict(no="%s-%03d" % (au, n), au=au, out=out_no, hash=h, state="미조치", at=now_z())
        b["finds"].append(f)
        self.led.add("PJT", "지적·조치", bundle=bid, find=f["no"], state="미조치", out=out_no)
        return f["no"]

    @op("사용자 결정")
    def set_action(self, bid, find_no, state):
        assert state in ("미조치", "조치 중", "조치 완료", "확인 완료")
        next(f for f in self.bundles[bid]["finds"] if f["no"] == find_no)["state"] = state
        self.led.add("PJT", "지적·조치", actor="사용자", bundle=bid, find=find_no, state=state)

    @op("사용자가 누름")
    def add_requirement(self, bid):
        b = self.bundles[bid]
        rq = "RQ%03d" % (len(b["rq"]) + 1)
        b["rq"].append(rq)
        self.led.add("PJT", "요구", bundle=bid, rq=rq)
        return rq

    @op("사용자가 누름")
    def link(self, bid, a, b_):
        """잇는 줄(추적): 요구 → 설계 산출물 → … 양쪽이 판을 가리킨다."""
        b = self.bundles[bid]
        now = self._outs_now(b)
        b["links"].append(dict(a=a, b=b_, ah=now.get(a, (None, None))[1], bh=now.get(b_, (None, None))[1]))
        self.led.add("PJT", "잇는 줄", bundle=bid, a=a, b=b_)

    @op("사용자가 누름")
    def set_external(self, bid, out_no, value):
        """EX-12 · PJ-05: 바깥(고객·기관)의 번호는 손대지 않고 `체계 이름[판]:원래 값` 꼴 그대로 싣는다."""
        self.bundles[bid]["ext"][out_no or "(묶음)"] = value
        self.led.add("PJT", "바깥 번호", bundle=bid, out=out_no, value_sha=sha(value.encode("utf-8"))[:12])

    def project_checks(self, bid):
        """엔진이 스스로 하는 검사 아홉(코드 분류 체계 8장). 보기만 하고 적지 않는다."""
        b = self.bundles[bid]
        now, out = self._outs_now(b), []
        add = lambda check, target, detail: out.append(dict(check=check, target=target, detail=detail))
        gals = {no[:2] for no in now}
        ph = b["phase"] or 0
        if b.get("pack") in PACKS:                        # ① 있어야 할 산출물이 빠짐(확장판의 목록이 있을 때만)
            for g, title, since in PACKS[b["pack"]]:
                if ph >= since and g not in gals:
                    add("빠진 산출물", g, "%s — 「%s」 확장판의 목록, PH%d부터 있어야 함" % (title, b["pack"], since))
        for p in range(1, ph):                            # ② 국면 건너뜀
            if not any(GAL_PHASE.get(g) == p for g in gals):
                add("국면 건너뜀", "PH%d" % p, "PH%d의 기록(갈래 %s)이 없이 PH%d에 와 있음" % (p, "·".join(k for k, v in GAL_PHASE.items() if v == p), ph))
        for no, (rel, h, aid) in sorted(now.items()):     # ③ 최종본 없이 다음 국면
            v = read_ver(norm(rel).split("/")[-1].rsplit(".", 1)[0])
            if GAL_PHASE.get(no[:2], 9) < ph and v and (v[3] or float(v[2]) < 1.0):
                add("최종본 없이 다음 국면", no, "판 %s%s인 채로 PH%d에 와 있음" % (v[2], "(작업본)" if v[3] else "", ph))
        for a in b["ac"]:                                 # ④ 검수 뒤 산출물이 바뀜
            for no, h in sorted(a["points"].items()):
                if no in now and now[no][1] != h:
                    add("검수 뒤 바뀜", no, "%s이(가) 가리킨 판과 지금 판이 다름" % a["no"])
        for f in b["finds"]:                              # ⑤ 감리 지적에 조치 없음
            if f["state"] == "미조치":
                add("지적 미조치", f["no"], "조치가 없음")
        for l in b["links"]:                              # ⑥ 추적 줄 끊김
            for end in (l["a"], l["b"]):
                if not end.startswith("RQ") and end not in now:
                    add("추적 줄 끊김", "%s→%s" % (l["a"], l["b"]), "%s이(가) 없음" % end)
        for rq in b["rq"]:
            if not any(l["a"] == rq for l in b["links"]):
                add("추적 줄 끊김", rq, "요구에서 나가는 줄이 없음")
        if b["bl"]:                                       # ⑦ 기준선과 지금 판이 다름
            for no, h in sorted(b["bl"][-1]["items"].items()):
                if no in now and now[no][1] != h:
                    add("기준선과 다름", no, "%s 뒤에 판이 바뀜" % b["bl"][-1]["no"])
        for e in b["ep"]:                                 # ⑧ 증적에 든 판이 사라짐
            for no, h in sorted(e["items"].items()):
                if not self._alive(h):
                    add("증적 판 사라짐", "%s/%s" % (e["no"], no), "그 판이 기기·매체·판 보관 어디에도 없음")
        seen = {}                                         # ⑨ 바깥 번호 겹침(이 기기의 모든 묶음에 걸쳐)
        for x in self.bundles.values():
            for k, v in x.get("ext", {}).items():
                seen.setdefault(v, []).append("%s/%s" % (x["id"], k))
        for v, where in sorted(seen.items()):
            if len(where) > 1 and any(w.startswith(bid + "/") for w in where):
                add("바깥 번호 겹침", "·".join(sorted(where)), "같은 바깥 번호가 %d곳에 실림" % len(where))
        return out

    def project_view(self, bid):
        b = self.bundles[bid]
        chk = self.project_checks(bid)
        return dict(bundle=bid, btype=b["btype"], btype_name=BTYPES.get(b["btype"]), pack=b["pack"], phase="PH%d" % b["phase"] if b["phase"] is not None else None,
                    outs=len(b["outs"]), baselines=[x["no"] for x in b["bl"]], ac=[(a["no"], a["result"]) for a in b["ac"]], au=[a["no"] for a in b["au"]],
                    finds=[(f["no"], f["state"]) for f in b["finds"]], ep=[e["no"] for e in b["ep"]],
                    missing=[c["target"] for c in chk if c["check"] == "빠진 산출물"], checks=chk)

    # ================= DSH · CLD =================
    def _done_today(self, reclaim):
        """「HiDAM이 해 놓은 일」: 오늘(협정 세계시) 원장에서 센다."""
        day = now_z()[:10]
        rows = [r for r in self.led.rows if r["at"][:10] == day]
        cnt = lambda *codes: sum(1 for r in rows if r["code"] in codes and r["res"] == "됨")
        return dict(day=day, placed=cnt("CLS-E03"), named=cnt("CLS-E04"), finals=cnt("SYN-E02"), mirrored=sum(r.get("done", 0) for r in rows if r["code"] == "SYN-E03"),
                    threats=cnt("AAD-E01", "AAD-E02") + sum(1 for r in rows if r["code"] == "AAD-E01" and r["res"] == "멈춤"), bundles=cnt("CLS-E07"),
                    reclaim_bytes=reclaim, held=cnt("CLS-E05") + sum(1 for r in rows if r["code"] == "CLS-E05"))

    def measures(self):
        """최상위 목표의 잣대: 사용자가 손댄 횟수, 물은 건수(제시·한 번), 판정 대기 비율."""
        ps = list(self.props.values())
        n = max(len(self.dev.index), 1)
        pend = sum(1 for rel in self.dev.index if self.judge(self.dev, rel)["code"][:2] == "99")
        return dict(user_touches=self.touches, asked=len(ps), asked_once=sum(1 for p in ps if p["who"] == "한 번"),
                    asked_offer=sum(1 for p in ps if p["who"] == "제시"), open=sum(1 for p in ps if p["state"] == "열림"),
                    accepted=sum(1 for p in ps if p["state"] == "받아들임"), pending_ratio=round(pend / n, 3), auto_events=sum(1 for r in self.led.rows if r["actor"] != "사용자"))

    @op("사용자가 누름", log=False)
    def dashboard(self):
        prev, stat = self.preview(log=False)
        opt, dup = self.dup_map()
        by = {}
        for v in prev.values():
            k = v["place"] if self.mode != "시스템" else v["code"][:2]
            by[k] = by.get(k, 0) + 1
        mcount = lambda m: len([1 for _d, _, fs in os.walk(os.path.join(m.root, "_HiDAM_거울")) for _ in fs])
        flagged = [(d, rel, r[0], r[1]) for d, m in self.media.items() for rel, r in m.flags.items()]
        self.led.follow(full=True)                        # 화면의 「사슬 맞음」은 기억이 아니라 원장 파일과 맞대어 본다
        danger = any(m.blocked for m in self.media.values()) or not self.led.verify()
        unsettled = opt["version_sets"] if self.last_wait is None else len(self.last_wait)    # 엇갈림은 「풀리지 않은 것」만 센다(풀린 뒤 매체에 남은 옛 판은 세지 않는다)
        has_mirror = any(m.role == "거울" for m in self.media.values())
        in_vault = {rel for d, v in self.vault.items() for rel, h in v.items() if self.dev.index.get(rel, {}).get("hash") == h}
        prot = sum(1 for rel, v in prev.items() if v["grade"] >= "D3" and rel not in in_vault) if has_mirror else 0     # 거울이 있는데 금고에도 가지 못한 보호 등급: 조용히 빠지지 않게 보인다
        todo = bool(self.last_auto and self.last_auto.get("waiting")) or unsettled > 0 or prot > 0
        open_ = self.proposals()
        projs = [self.project_view(b["id"]) for b in self.bundles.values() if b["kind"] == "프로젝트" and b["state"] == "씀"]
        return {
            "1_내기기": dict(dev=self.dev.dev_id, mode=self.mode, media=[dict(dev=d, kind=m.kind, role=m.role, scope=m.scope,
                           state="꽂힘" if m.plugged else "뽑힘(마지막 본 값)", blocked=m.blocked, unseen=len(m.unseen)) for d, m in self.media.items()]),
            "2_내디지털자산": dict(files=len(prev), assets=len({v["asset"] for v in prev.values() if v["asset"]}), empties=len(self.empties), by_place=by, conf=stat,
                             dup=opt, unsettled=unsettled, bundles=sum(1 for b in self.bundles.values() if b["state"] == "씀"),
                             shown_names={r: s["std_name"] for r, s in list(self.suggest.items())[:5]}),
            "3_보호상태": dict(flagged=flagged, unregistered=[d for d, m in self.media.items() if not m.registered],
                           state="위험" if danger else ("살핌 필요" if todo or flagged else "정상")),
            "4_거울상태": dict(mirrors={d: mcount(m) for d, m in self.media.items() if m.role == "거울"}, last_auto=self.last_auto,
                           skipped=self.skipped[:5], protected_waiting=prot, protected_note="보호 등급(D3 이상) %d건이 아직 금고 거울에 가지 못했습니다" % prot if prot else None, mirror_no={d: i + 1 for i, d in enumerate(self.mirror_order)}),
            "5_금고": dict(count=len(in_vault), media={d: len(v) for d, v in self.vault.items()}, note="보호 등급 자산을 거울 매체의 _HiDAM_금고에 잠가서 비춤(이름도 잠금)"),
            "6_기록": dict(events=len(self.led.rows), chain_ok=self.led.verify(), recover_used=self.recover_count, boot=self.boot),
            "7_구독회원": dict(tier=self.tier, devices="확인 안 됨(회원·기기 등록은 Cloud 쪽)"),
            "8_설정": dict(auto=self.auto, mass_ratio=self.mass_ratio, policy=self.led.policy, app=APP_VER, mode=self.mode, rename_policy=self.rename_policy),
            "9_열쇠": dict(note="값 없음 — 이름·위치·이력만"),
            "가_한번만_봐주세요": dict(count=len(open_), once=sum(1 for p in open_ if p["who"] == "한 번"), list=open_),
            "나_HiDAM이_해놓은_일": self._done_today(opt["reclaim_bytes"]),
            "다_프로젝트": projs,
            "라_잣대": self.measures(),
        }

    @op("사용자가 누름", log=False)
    def cloud_payload(self, show_names=False):
        """FN-12: 메타데이터만. 원본·내용·키 값 없음. 이름은 사용자가 켠 때만."""
        if self.tier != "구독":
            return None
        prev, stat = self.preview(log=False)
        assets = []
        for rel, it in self.dev.index.items():
            a = dict(asset=it["asset"], ver=it["ver"], size=it["size"], code=prev[rel]["code"], grade=prev[rel]["grade"], project=prev[rel]["project"],
                     bundle=prev[rel]["bundle"])
            if show_names:
                a["name"] = rel
            assets.append(a)
        opt = self.dup_map()[0]
        projs = [dict(bundle=v["bundle"], btype=v["btype"], phase=v["phase"], missing=len(v["missing"]), checks=len(v["checks"]))
                 for v in (self.project_view(b["id"]) for b in self.bundles.values() if b["kind"] == "프로젝트" and b["state"] == "씀")]
        return dict(dev=self.dev.dev_id, policy=self.led.policy, app=APP_VER, mode=self.mode, at=int(time.time()),
                    media=[dict(dev=d, kind=m.kind, role=m.role, scope=m.scope) for d, m in self.media.items()],
                    assets=assets, sums=stat, events=[dict(seq=r["seq"], eid=r["eid"], code=r["code"], cause=r["cause"], res=r["res"], rc=r["rc"]) for r in self.led.rows],
                    proposals=dict(open=len(self.proposals()), kinds=sorted({p["kind"] for p in self.proposals()})),
                    done=self._done_today(opt["reclaim_bytes"]), projects=projs, measures=self.measures())
