# -*- coding: utf-8 -*-
"""대표 일정 화면(schedule.html) 자료 묶음 만들기 — Opus 5.5, 이력 1240·1241·1249.

원천 네 파일(cowork/ctl/ceo_schedule.tsv · master_milestones.tsv · schedule_master.tsv · hiven_wbs.tsv)을 읽어
잠그는 값(sched.pub.json)으로만 잠근 암호 묶음 sched.enc.json 하나로 만든다. 화면은 원천 TSV를 읽지 않고 이 묶음만 읽는다.
이 도구는 열쇠를 묻지도, 알지도 않는다(이력 1249 공개 키 방식).
열쇠는 통합관제(IC)와 같은 열쇠다(11-13 17:08). 잠그는 값도 통합관제 열쇠에서 나온다.

암호 방식(묶음 v2, ECIES)
  화면(sched-core.js): 열쇠 → PBKDF2-SHA256(120000회, 소금 hiven-sched-ec-261113, 48바이트) → P-256 개인 값 d = c mod (n-1) + 1
                       (FIPS 186-4 부록 B.4.1). 공개 값을 압축 꼴 33바이트 base64url(44자)로 보인 것이 「잠그는 값」.
  이 도구: 묶을 때마다 새 임시 키 짝(P-256) → ECDH(임시 개인, 잠그는 값) → HKDF-SHA256(소금 = 임시 공개 65바이트 ‖ 잠그는 값 33바이트,
           info hiven-sched-ecies-v2) → AES-256-GCM(새 12바이트 IV, 덧붙임 자료 hiven-sched-v2)

쓰는 법
  python3 tools/gen_ceo_schedule.py --pub <잠그는 값>   → sched.pub.json 을 쓰고 묶음을 만든다(처음 한 번, 또는 열쇠가 바뀐 뒤)
  python3 tools/gen_ceo_schedule.py                     → 저장소의 sched.pub.json 으로 묶음을 다시 만든다(원천 표가 바뀔 때마다)
  --out 경로 --pub-file 경로 : 시험용으로 기본 자리 밖에 만들 때
"""
import argparse, base64, csv, datetime, hashlib, json, os, re, sys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTL = os.path.join(ROOT, 'cowork', 'ctl')
SRC = {
    'ceo': ('ceo_schedule.tsv', ['번호', '날짜', '일정', '구분', '상태', '해야 할 일', '근거']),
    'ms': ('master_milestones.tsv', ['층', '번호', '때', '갈래', '일정·마일스톤', '상태', '근거']),
    'sm': ('schedule_master.tsv', ['구분', '번호', '때', '일', '끝난 기준', '담당', '상태', '근거']),
    'wbs': ('hiven_wbs.tsv', ['번호', '갈래', '일', '시작', '끝', '선행', '상태', '근거']),
}
OUT = os.path.join(ROOT, 'sched.enc.json')
PUB = os.path.join(ROOT, 'sched.pub.json')
INFO = b'hiven-sched-ecies-v2'
AAD = b'hiven-sched-v2'


def read_tsv(name, cols):
    p = os.path.join(CTL, name)
    with open(p, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    rows = [r for r in rows if any(c.strip() for c in r)]
    head = [c.strip() for c in rows[0]]
    if head[:len(cols)] != cols:
        sys.exit('머리 줄이 다릅니다: %s → %s' % (name, head))
    body = []
    for r in rows[1:]:
        r = [c.strip() for c in r] + [''] * len(cols)
        body.append(r[:len(cols)])
    return head[:len(cols)], body, hashlib.sha256(open(p, 'rb').read()).hexdigest()


def b64u_dec(s):
    s = s.strip()
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def load_pub(txt):
    """잠그는 값(base64url 압축 33바이트) → 공개 키. 곡선 위의 점이 아니면 멈춘다."""
    try:
        raw = b64u_dec(txt)
        if len(raw) != 33 or raw[0] not in (2, 3):
            raise ValueError('길이·머리 바이트')
        return raw, ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), raw)
    except Exception as e:  # 잘못 붙인 값
        sys.exit('잠그는 값이 올바르지 않습니다(%s). 화면에 보인 44자를 그대로 붙이십시오.' % e)


def check_chk():
    """sched-core.js 의 열쇠 확인 값(CHK)이 data.js(KEYH)와 같은지 — 다르면 화면이 통합관제 열쇠가 아닌 값에 잠그는 값을 내줄 수 있다."""
    d = open(os.path.join(ROOT, 'data.js'), encoding='utf-8').read()
    c = open(os.path.join(ROOT, 'sched-core.js'), encoding='utf-8').read()
    m1 = re.search(r"KEYH='([0-9a-f]{64})'", d)
    m2 = re.search(r"CHK=\{h:'([0-9a-f]{64})'", c)
    if not (m1 and m2 and m1.group(1) == m2.group(1)):
        sys.exit('sched-core.js 의 열쇠 확인 값(CHK)이 data.js 의 KEYH 와 다릅니다. 먼저 맞추십시오.')


def seal(raw_pub, pub, plain):
    eph = ec.generate_private_key(ec.SECP256R1())
    epk = eph.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    z = eph.exchange(ec.ECDH(), pub)
    k = HKDF(algorithm=hashes.SHA256(), length=32, salt=epk + raw_pub, info=INFO).derive(z)
    iv = os.urandom(12)
    ct = AESGCM(k).encrypt(iv, plain, AAD)
    return {'v': 2, 'alg': 'ECIES-P256-HKDF-SHA256-AES-256-GCM', 'kdf': 'PBKDF2-SHA256', 'it': 120000,
            'salt': 'hiven-sched-ec-261113', 'rk': base64.urlsafe_b64encode(raw_pub).rstrip(b'=').decode(),
            'epk': base64.b64encode(epk).decode(), 'iv': base64.b64encode(iv).decode(), 'ct': base64.b64encode(ct).decode()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pub', help='화면에 보인 잠그는 값(44자). 주면 sched.pub.json 에 적는다')
    ap.add_argument('--pub-file', default=PUB)
    ap.add_argument('--out', default=OUT)
    a = ap.parse_args()

    check_chk()

    if a.pub:
        raw, pub = load_pub(a.pub)
        with open(a.pub_file, 'w', encoding='utf-8') as f:
            json.dump({'v': 2, 'curve': 'P-256', '잠그는 값': a.pub.strip(),
                       '설명': '대표 일정 묶음을 잠그는 공개 값. 공개해도 되며 이 값으로 열쇠를 알 수 없다(이력 1249).'},
                      f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('적음: %s' % a.pub_file)
    else:
        if not os.path.exists(a.pub_file):
            sys.exit('%s 가 없습니다. 대표님 화면에 보인 잠그는 값을 --pub 로 주십시오.' % a.pub_file)
        raw, pub = load_pub(json.load(open(a.pub_file, encoding='utf-8'))['잠그는 값'])

    data, src = {}, {}
    for k, (name, cols) in SRC.items():
        head, body, h = read_tsv(name, cols)
        data[k] = body
        src[name] = {'줄': len(body), 'sha256': h}
    bad = [r[0] for r in data['ceo'] if not re.fullmatch(r'\d{4}-\d\d-\d\d', r[1])]
    if bad:
        sys.exit('개인 일정 날짜 꼴(YYYY-MM-DD)이 아닙니다: %s' % ', '.join(bad))

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    plain = json.dumps({'만든때': now.strftime('%Y-%m-%d %H:%M'), '원천': src, 'ceo': data['ceo'],
                        'ms': data['ms'], 'sm': data['sm'], 'wbs': data['wbs']}, ensure_ascii=False).encode('utf-8')
    box = seal(raw, pub, plain)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(box, f, ensure_ascii=False)
    print('만듦: %s (%d바이트, 개인 %d줄 · 마일스톤 %d줄 · 일정 대장 %d줄 · WBS %d줄)' % (
        a.out, os.path.getsize(a.out), len(data['ceo']), len(data['ms']), len(data['sm']), len(data['wbs'])))


if __name__ == '__main__':
    main()
