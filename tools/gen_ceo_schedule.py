# -*- coding: utf-8 -*-
"""대표 일정 화면(schedule.html) 자료 묶음 만들기 — Opus 5.5, 이력 1240·1241.

원천 네 파일(cowork/ctl/ceo_schedule.tsv · master_milestones.tsv · schedule_master.tsv · hiven_wbs.tsv)을 읽어
열쇠로만 풀리는 암호 묶음 sched.enc.json 하나로 만든다. 화면은 원천 TSV를 읽지 않고 이 묶음만 읽는다.

암호 방식
  열쇠 → (한글 자판 입력은 화면에서 영문으로 바꾼 뒤) 앞뒤 공백 제거 · 소문자
  열쇠 확인: 통합관제 첫 화면과 같은 값(data.js의 KEYH, PBKDF2-SHA256 120000회, 소금 hiven-intro-261113)과 맞는지 먼저 본다
  암호 열쇠: PBKDF2-SHA256 120000회, 소금 hiven-sched-261113 (확인 값과 다른 소금이라 KEYH로는 풀 수 없다)
  암호: AES-256-GCM, 묶음마다 새 12바이트 IV

열쇠 값은 이 파일에도 묶음에도 적지 않는다. 실행하는 사람이 입력한다.
  python3 tools/gen_ceo_schedule.py              → 열쇠를 묻는다(화면에 안 보임)
  환경 변수 HV_SCHED_KEY 가 있으면 그것을 쓴다
  --out 경로 --no-check : 시험용 묶음(다른 열쇠)을 기본 자리 밖에 만들 때만
"""
import argparse, base64, csv, datetime, getpass, hashlib, json, os, re, sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTL = os.path.join(ROOT, 'cowork', 'ctl')
SRC = {
    'ceo': ('ceo_schedule.tsv', ['번호', '날짜', '일정', '구분', '상태', '해야 할 일', '근거']),
    'ms': ('master_milestones.tsv', ['층', '번호', '때', '갈래', '일정·마일스톤', '상태', '근거']),
    'sm': ('schedule_master.tsv', ['구분', '번호', '때', '일', '끝난 기준', '담당', '상태', '근거']),
    'wbs': ('hiven_wbs.tsv', ['번호', '갈래', '일', '시작', '끝', '선행', '상태', '근거']),
}
OUT = os.path.join(ROOT, 'sched.enc.json')
SALT_CHECK = b'hiven-intro-261113'
SALT_ENC = b'hiven-sched-261113'
ITER = 120000


def read_tsv(name, cols):
    p = os.path.join(CTL, name)
    with open(p, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    rows = [r for r in rows if any(c.strip() for c in r)]
    head = [c.strip() for c in rows[0]]
    if head[:len(cols)] != cols:
        sys.exit('머리 줄이 다름: %s → %s' % (name, head))
    body = []
    for r in rows[1:]:
        r = [c.strip() for c in r] + [''] * len(cols)
        body.append(r[:len(cols)])
    return head[:len(cols)], body, hashlib.sha256(open(p, 'rb').read()).hexdigest()


def key_check_value():
    t = open(os.path.join(ROOT, 'data.js'), encoding='utf-8').read()
    m = re.search(r"KEYH='([0-9a-f]{64})'", t)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--no-check', action='store_true')
    a = ap.parse_args()
    if a.no_check and os.path.abspath(a.out) == OUT:
        sys.exit('--no-check 는 시험 자리(--out)로만 쓴다')

    data, src = {}, {}
    for k, (name, cols) in SRC.items():
        head, body, h = read_tsv(name, cols)
        data[k] = body
        src[name] = {'줄': len(body), 'sha256': h}
    bad = [r[0] for r in data['ceo'] if not re.fullmatch(r'\d{4}-\d\d-\d\d', r[1])]
    if bad:
        sys.exit('개인 일정 날짜 꼴(YYYY-MM-DD)이 아님: %s' % ', '.join(bad))

    key = os.environ.get('HV_SCHED_KEY')
    if key is None:
        key = getpass.getpass('열쇠: ')
    key = key.strip().lower()
    if not a.no_check:
        kh = key_check_value()
        got = hashlib.pbkdf2_hmac('sha256', key.encode(), SALT_CHECK, ITER).hex()
        if not kh or got != kh:
            sys.exit('열쇠가 통합관제 열쇠와 맞지 않아 묶음을 만들지 않음')

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    plain = json.dumps({'만든때': now.strftime('%Y-%m-%d %H:%M'), '원천': src, 'ceo': data['ceo'],
                        'ms': data['ms'], 'sm': data['sm'], 'wbs': data['wbs']}, ensure_ascii=False).encode('utf-8')
    k = hashlib.pbkdf2_hmac('sha256', key.encode(), SALT_ENC, ITER)
    iv = os.urandom(12)
    ct = AESGCM(k).encrypt(iv, plain, None)
    box = {'v': 1, 'kdf': 'PBKDF2-SHA256', 'it': ITER, 'salt': SALT_ENC.decode(), 'alg': 'AES-256-GCM',
           'iv': base64.b64encode(iv).decode(), 'ct': base64.b64encode(ct).decode()}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(box, f, ensure_ascii=False)
    print('만듦: %s (%d바이트, 개인 %d줄 · 마일스톤 %d줄 · 일정 대장 %d줄 · WBS %d줄)' % (
        a.out, os.path.getsize(a.out), len(data['ceo']), len(data['ms']), len(data['sm']), len(data['wbs'])))


if __name__ == '__main__':
    main()
