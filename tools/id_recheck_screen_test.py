#!/usr/bin/env python3
"""신분 재확인 화면 시험 — Opus 5.5 · 2026-11-13 (이력 1255·1256, 정책 11절 신-4).
  가) hs 첫 화면 SC-00·SC-17 의 「신분 재확인」 한 줄(id-recheck.js)
  나) hiven-ic id.html 의 재확인 주소(?why=…)와 보내는 값
바깥 주소(ic.hiven.ai.kr 등)는 모두 막고 몇 번 부르려 했는지 센다. 서버는 이 컴퓨터 안(127.0.0.1)에서만 띄운다.
결과: cowork/ctl/id_recheck_screen_test.tsv (비밀번호·열쇠 값 없음 · 시험용 값은 무작위)
사용: python3 tools/id_recheck_screen_test.py [hiven-ic 폴더(기본 ../hiven-ic)]
"""
import sys, os, json, threading, functools, http.server, socketserver, datetime, hashlib, secrets
from playwright.sync_api import sync_playwright

HS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HS, '..', 'hiven-ic'))
OUT = os.path.join(HS, 'cowork', 'ctl', 'id_recheck_screen_test.tsv')
W = 400


def serve(root):
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Q, directory=root)
    s = socketserver.ThreadingTCPServer(('127.0.0.1', 0), h)
    s.daemon_threads = True
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, s.server_address[1]


HOLD_H = '보류 번호\t올린 때\t이력 번호\t지시 때\t까닭\t갈래\t상태\t닫은 때\t통과 기록\n'


def hold_rows(n):
    out = []
    for i in range(1, n + 1):
        st = '보류' if i % 3 == 0 else ('무효(통과 없음)' if i % 3 == 1 else '통과 · 이어서 수행')
        out.append('IDH-%03d\t2026-11-13 10:%02d\t%d\t2026-11-13 10:%02d\t무입력 3%d분(기준 30분 넘음)\t배포\t%s\t\t' % (i, i, 1300 + i, i, i % 10, st))
    return HOLD_H + '\n'.join(out) + '\n'


R = []


def ok(no, name, cond, val):
    R.append([no, name, '통과' if cond else '실패', str(val)[:300]])


def page_setup(b, port, hold_text):
    ctx = b.new_context(viewport={'width': W, 'height': 800})
    pg = ctx.new_page()
    st = {'ext': [], 'hold': 0, 'err': [], 'cons': []}

    def route(r):
        u = r.request.url
        if not u.startswith('http://localhost:%d' % port):
            st['ext'].append(u)
            return r.abort()
        if '/cowork/ctl/id_recheck_hold.tsv' in u:
            st['hold'] += 1
            return r.fulfill(status=200, body=hold_text[0].encode('utf-8'), headers={'content-type': 'text/plain; charset=utf-8'})
        return r.continue_()
    pg.route('**/*', route)
    pg.on('pageerror', lambda e: st['err'].append(str(e)))
    pg.on('console', lambda m: m.type == 'error' and st['cons'].append(m.text))
    return ctx, pg, st


def hs_tests(b, port):
    hold = [HOLD_H]
    ctx, pg, st = page_setup(b, port, hold)
    pg.goto('http://localhost:%d/index.html' % port, wait_until='load')
    pg.wait_for_function("typeof render==='function'")
    pg.evaluate("render('SC-00')")
    pg.wait_for_function("(document.querySelector('#hv-idh-00 button')||{}).textContent && !/읽는 중/.test(document.querySelector('#hv-idh-00 button').textContent)", timeout=15000)
    t = pg.inner_text('#hv-idh-00 button')
    ok('화-1', 'SC-00 한 줄(빈 표): 보류 0 · 무효 0 · 통과 0', t == '신분 재확인 · 보류 0 · 무효 0 · 통과 0', t)
    ok('화-2', 'SC-00 한 줄이 「대표님 결재」 알림 상자(al-00) 앞에 있음', pg.evaluate("(function(){var a=document.getElementById('hv-idh-00'),b=document.getElementById('al-00');return !!(a&&b&&(a.compareDocumentPosition(b)&4))})()"), '')
    pg.click('#hv-idh-00 button')
    ok('화-3', '빈 표를 누르면 「기록이 없습니다」 안내', '기록이 없습니다' in pg.inner_text('#hv-idh-00 .idh-t'), '')
    # 표 채움(20줄) → 지시 대장이 바뀐 것처럼 기척을 바꾸면 한 번만 다시 읽음
    n0 = st['hold']
    pg.wait_for_timeout(3500)
    ok('화-4', '바뀐 것이 없으면 3.5초 동안 다시 읽지 않음(폴링 없음)', st['hold'] == n0, '읽은 횟수 %d → %d' % (n0, st['hold']))
    hold[0] = hold_rows(20)
    pg.evaluate("window.hvCmdLive={H:(window.hvCmdLive||{}).H||[],L:((window.hvCmdLive||{}).L||[]).concat([['9999','11/13 23:59','시험','','']])}")
    pg.wait_for_function("/보류 6/.test(document.querySelector('#hv-idh-00 button').textContent)", timeout=5000)
    pg.wait_for_timeout(2500)
    ok('화-5', '지시 대장이 바뀐 때 한 번만 다시 읽음', st['hold'] == n0 + 1, '읽은 횟수 %d → %d' % (n0, st['hold']))
    t = pg.inner_text('#hv-idh-00 button')
    ok('화-6', '20줄: 보류 6 · 무효 7 · 통과 7', t == '신분 재확인 · 보류 6 · 무효 7 · 통과 7', t)
    rows = pg.evaluate("[].map.call(document.querySelectorAll('#hv-idh-00 .idh-t table tr'),function(r){return r.cells[0]?r.cells[0].textContent:''}).slice(1)")
    ok('화-7', '근거 표 첫 쪽: 최신순 15줄(IDH-020 부터)', len(rows) == 15 and rows[0] == 'IDH-020' and rows[-1] == 'IDH-006', rows[:2] + rows[-1:])
    pg.click("#hv-idh-00 .idh-t button:has-text('다음 ▶')")
    rows2 = pg.evaluate("[].map.call(document.querySelectorAll('#hv-idh-00 .idh-t table tr'),function(r){return r.cells[0]?r.cells[0].textContent:''}).slice(1).filter(Boolean)")
    ok('화-8', '다음 ▶: 둘째 쪽 5줄(IDH-005~001), 빈 줄로 높이 고정', rows2 == ['IDH-005', 'IDH-004', 'IDH-003', 'IDH-002', 'IDH-001'] and pg.evaluate("document.querySelectorAll('#hv-idh-00 .idh-t table tr').length") == 16, rows2)
    for k in ('00', '17'):
        if k == '17':
            pg.evaluate("render('SC-17')")
            pg.wait_for_function("(document.querySelector('#hv-idh-17 button')||{}).textContent && !/읽는 중/.test(document.querySelector('#hv-idh-17 button').textContent)", timeout=15000)
            t = pg.inner_text('#hv-idh-17 button')
            ok('화-9', 'SC-17 한 줄(같은 원천, 다시 읽지 않음)', t == '신분 재확인 · 보류 6 · 무효 7 · 통과 7', t)
            ok('화-10', 'SC-17 한 줄이 cq-16 앞에 있음', pg.evaluate("(function(){var a=document.getElementById('hv-idh-17'),b=document.getElementById('cq-16');return !!(a&&b&&(a.compareDocumentPosition(b)&4))})()"), '')
            pg.click('#hv-idh-17 button')
        m = pg.evaluate("(function(k){var b=document.querySelector('#hv-idh-'+k+' button');return {doc:document.documentElement.scrollWidth,win:innerWidth,bs:b.scrollWidth,bc:b.clientWidth,tw:document.querySelector('#hv-idh-'+k+' .idh-t').getBoundingClientRect().right}})('%s')" % k)
        ok('화-%s' % ('11' if k == '00' else '12'), 'SC-%s 400px: 가로 밀림 0 · 한 줄 글자 잘림 없음 · 표 상자는 화면 안' % k,
           m['doc'] <= m['win'] and m['bs'] <= m['bc'] and m['tw'] <= m['win'], m)
    ok('화-13', '바깥 주소(ic.hiven.ai.kr 등) 호출: 이 한 줄이 만든 것 0건', not any('id_recheck' in u or '__id' in u for u in st['ext']), '막은 바깥 호출 전체 %d건(기존 화면 몫): %s' % (len(st['ext']), sorted(set(u.split('/')[2] for u in st['ext']))))
    ok('화-14', '스크립트 오류 0', not st['err'], st['err'])
    ctx.close()
    return st


def ic_tests(b, port):
    pw = secrets.token_hex(8)  # 시험용 무작위 값(기록하지 않음)
    res = []
    for q, why in (('?why=risk&kind=%EB%B0%B0%ED%8F%AC&no=1260&win=261104', 'risk'), ('?why=idle&win=261104', 'idle'), ('?why=evil&kind=x&no=a1', ''), ('', '')):
        ctx = b.new_context(viewport={'width': W, 'height': 800})
        pg = ctx.new_page()
        sent, ext, err = [], [], []

        def route(r):
            u = r.request.url
            if '/__id/state' in u:
                return r.fulfill(status=200, body='{"set":true,"hours":8}', headers={'content-type': 'application/json'})
            if '/__id/verify' in u:
                sent.append(json.loads(r.request.post_data or '{}'))
                return r.fulfill(status=200, body='{"ok":true}', headers={'content-type': 'application/json'})
            if not u.startswith('http://localhost:%d' % port):
                ext.append(u)
                return r.abort()
            return r.continue_()
        pg.route('**/*', route)
        pg.on('pageerror', lambda e: err.append(str(e)))
        pg.goto('http://localhost:%d/id.html%s' % (port, q))
        pg.wait_for_timeout(300)
        if not q:
            pg.fill('#win', '261104')
        pg.fill('#pw', pw)
        pg.click('#go')
        pg.wait_for_function("document.getElementById('msg').textContent.length>0")
        m = pg.evaluate("({ttl:document.getElementById('ttl').textContent,re:document.getElementById('re').hidden?'':document.getElementById('re').textContent,win:document.getElementById('win').value,msg:document.getElementById('msg').textContent,doc:document.documentElement.scrollWidth,iw:innerWidth})")
        s = sent[0] if sent else {}
        res.append((q, why, m, s, ext, err))
        ctx.close()
    (q, _, m, s, e1, r1), (q2, _, m2, s2, e2, r2), (q3, _, m3, s3, e3, r3), (q4, _, m4, s4, e4, r4) = res
    ok('신-1', 'id.html 둘째 겹 재확인 주소: 제목 「대표 신분 재확인」 · 까닭(배포·이력 1260) · 창 번호 채움',
       m['ttl'] == '대표 신분 재확인' and '배포' in m['re'] and '이력 1260' in m['re'] and m['win'] == '261104', m['re'])
    ok('신-2', '보내는 값: why=risk · kind=배포 · no=1260 (통과 기록에 재확인 시각·까닭이 남음)', s.get('why') == 'risk' and s.get('kind') == '배포' and s.get('no') == '1260', {k: v for k, v in s.items() if k != 'pw'})
    ok('신-3', '통과 문구: 보류한 지시를 이어서 수행', '신분 재확인 통과' in m['msg'], m['msg'])
    ok('신-4', '무입력 재확인 주소: why=idle 만 보냄', s2.get('why') == 'idle' and 'kind' not in s2 and '30분' in m2['re'], m2['re'])
    ok('신-5', '정해지지 않은 까닭(?why=evil): 재확인 표시·값 없음(첫 확인과 같음)', m3['ttl'] == '대표 신분 확인' and not m3['re'] and 'why' not in s3, {k: v for k, v in s3.items() if k != 'pw'})
    ok('신-6', '주소에 까닭이 없으면 첫 확인 그대로', m4['ttl'] == '대표 신분 확인' and 'why' not in s4 and '신분 확인 통과' in m4['msg'], m4['msg'])
    ok('신-7', 'id.html 400px 가로 밀림 0(네 경우)', all(x[2]['doc'] <= x[2]['iw'] for x in res), [x[2]['doc'] for x in res])
    ok('신-8', 'id.html 스크립트 오류 0 · 바깥 주소 호출 0', not any(x[5] for x in res) and not any(x[4] for x in res), [x[5] for x in res] + [x[4] for x in res])


def main():
    s1, p1 = serve(HS)
    s2, p2 = serve(IC)
    with sync_playwright() as p:
        b = p.chromium.launch()
        try:
            hs_tests(b, p1)
        except Exception as e:
            ok('화-x', '화면 시험 진행 중 멈춤', False, repr(e))
        try:
            ic_tests(b, p2)
        except Exception as e:
            ok('신-x', 'id.html 시험 진행 중 멈춤', False, repr(e))
        b.close()
    s1.shutdown()
    s2.shutdown()
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')
    hj = hashlib.sha256(open(os.path.join(HS, 'id-recheck.js'), 'rb').read()).hexdigest()[:12]
    hi = hashlib.sha256(open(os.path.join(IC, 'id.html'), 'rb').read()).hexdigest()[:12]
    with open(OUT, 'w', encoding='utf-8', newline='') as o:
        o.write('번호\t사례\t판정\t잰 값\t시험한 때\tid-recheck.js sha256 앞 12자\tid.html sha256 앞 12자\n')
        for r in R:
            o.write('\t'.join(x.replace('\t', ' ').replace('\n', ' ') for x in r) + '\t%s\t%s\t%s\n' % (stamp, hj, hi))
    bad = [r for r in R if r[2] != '통과']
    for r in R:
        print(r[0], r[2], '·', r[1], '' if r[2] == '통과' else '· ' + r[3])
    print('화면 시험', '통과' if not bad else '실패 %d건' % len(bad), '· %d건 · 기록 %s' % (len(R), OUT))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
