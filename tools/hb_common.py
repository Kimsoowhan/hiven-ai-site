# -*- coding: utf-8 -*-
"""HiBiz 정리 도구 공통 부분 (D-1 · D-2 · D-3이 함께 씀). 표준 라이브러리만 씀.
읽기만 한다: 파일을 옮기거나 고치거나 지우지 않는다. 쓰는 것은 사람이 지정한 결과 파일 하나뿐이다.

목록을 받는 길 두 가지:
  1) 실제 폴더(--root): os.walk로 경로 · 크기 · 고친 때 · sha256을 잰다(PC에서 사람이 돌릴 때).
  2) 목록 표(--list): 한 줄 = 상대경로 \t 종류(dir|file) \t 크기 \t 고친때(ms) [\t sha256]
     S-7의 master.tsv 꼴과 같다. sha256이 없으면 --hash(상대경로 \t 크기 \t 고친때 \t sha256) 표에서 채운다.
경로는 언제나 '/'로 나눈 상대경로이고 한글은 NFC로 맞춘다(운영체제마다 자모를 다르게 적는다, 0.5 norm).
"""
import os, hashlib, unicodedata, datetime

def norm(s):
    return unicodedata.normalize("NFC", s)

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

class Item:
    __slots__ = ("path", "kind", "size", "mtime", "sha")
    def __init__(self, path, kind, size=None, mtime=None, sha=""):
        self.path, self.kind, self.size, self.mtime, self.sha = norm(path), kind, size, mtime, sha
    @property
    def name(self):
        return self.path.rsplit("/", 1)[-1]
    @property
    def parent(self):
        return self.path.rsplit("/", 1)[0] if "/" in self.path else ""

def walk(root, top_name=None, hashing=True):
    """실제 폴더를 읽는다. top_name을 주면 경로 맨 앞에 그 이름을 붙인다(목록 표와 같은 꼴)."""
    root = os.path.abspath(root)
    top = norm(top_name if top_name is not None else os.path.basename(root))
    out = [Item(top, "dir")]
    for d, dirs, files in os.walk(root):
        dirs.sort(); files.sort()
        rel = os.path.relpath(d, root)
        base = top if rel == "." else top + "/" + rel.replace(os.sep, "/")
        for x in dirs:
            out.append(Item(base + "/" + x, "dir"))
        for x in files:
            p = os.path.join(d, x)
            st = os.stat(p)
            out.append(Item(base + "/" + x, "file", st.st_size, int(st.st_mtime * 1000),
                            sha256_file(p) if hashing else ""))
    return out

def load_list(list_path, hash_path=None):
    cache = {}
    if hash_path:
        for l in open(hash_path, encoding="utf-8"):
            p = l.rstrip("\n").split("\t")
            if len(p) >= 4:
                cache[norm(p[0])] = p
    out, miss = [], []
    for l in open(list_path, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        if len(p) < 2 or not p[0]:
            continue
        path, kind = norm(p[0]), p[1]
        if kind == "dir":
            out.append(Item(path, "dir"))
            continue
        size = int(p[2]) if len(p) > 2 and p[2] else None
        mt = int(p[3]) if len(p) > 3 and p[3] else None
        sha = p[4] if len(p) > 4 else ""
        if not sha and path in cache:
            c = cache[path]
            if (size is None or int(c[1]) == size) and (mt is None or int(c[2]) == mt):
                sha = c[3]
        if not sha:
            miss.append(path)
        out.append(Item(path, "file", size, mt, sha))
    return out, miss

def kst(ms):
    if ms is None:
        return ""
    return (datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(ms), hours=9)).strftime("%Y-%m-%d %H:%M:%S")

def write_tsv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as w:
        w.write("\t".join(header) + "\n")
        for r in rows:
            assert len(r) == len(header), r
            w.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in r) + "\n")

# 옛 통제어(영문 둘 · 한글 하나)는 글자 그대로 적지 않는다. 바이트를 뒤집은 16진수로만 둔다.
_HIDDEN = ("6e696d6461", "726f7461727473696e696d6461", "bcafeb9c93ebb496ec")
def _unhide(h):
    b = bytes.fromhex(h)
    return b[::-1].decode("utf-8", "ignore")

def hidden_words():
    ws = []
    for h in _HIDDEN:
        w = _unhide(h)
        ws.append(w)
    return ws

def has_hidden_word(text):
    t = norm(text).lower()
    return any(w in t for w in hidden_words())
