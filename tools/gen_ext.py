#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SC-18~SC-21 게시 원천을 HiBiz 41~44 대장(작업 사본)에서 낸다. (2026-11-13 Fable 지시 · Opus 5.5)

  원천(작업 사본, 고치지 않음)              → 게시 원천(cowork/ctl/)               화면
  ext/stk.tsv       (41 Stakeholder 목록)   → ext_stakeholder.tsv                  SC-18
  ext/stk_alert.tsv (41 받은 얼럿 기록)     → ext_stakeholder_alerts.tsv           SC-18
  ext/ptn.tsv       (42 협력사·이해관계자)  → ext_partner.tsv                      SC-19
  ext/sla.tsv       (42 협의·SLA·MOU)       → ext_sla_mou.tsv                      SC-19
  ext/ctr.tsv       (43 계약 대장)          → ext_contract.tsv                     SC-21
  pip/pol.tsv       (44_10 약관·정책 목록)  → policy_list.tsv                      SC-20 ①
  pip/mem.tsv       (44_21 회원 관리 대장)  → member_ledger.tsv                    SC-20 ②
  pip/beta.tsv      (44_22 베타 설치 대장)  → beta_ledger.tsv                      SC-20 ③
  pip/pi.tsv        (44_20 개인정보 처리)   → pip_ledger.tsv                       SC-20 ④

규칙
- 공개 저장소(hs)에 대표님 개인 일정을 싣지 않는다: Stakeholder 목록의 「요금·한도」 칸에 결제일·결제 문구가 있으면 그 칸을 「확인 안 됨」으로 바꿔 낸다.
- 그 밖의 값은 바꾸지 않는다(줄바꿈은 LF로 맞춤). 칸 수가 머리글과 다른 줄이 있으면 멈춘다.
- 값을 지어내지 않는다. 원천이 머리글만 있으면 머리글만 낸다(화면은 0건).

쓰는 법:  python3 tools/gen_ext.py [원천 폴더(기본 /mnt/user-data/outputs)] [저장소 맨 위(기본 지금 폴더)] [--check]
  --check : 쓰지 않고 지금 게시 원천과 같은지만 본다(다르면 종료 코드 1).
"""
import os, sys

NA = '확인 안 됨'
MAP = [
    ('ext/stk.tsv', 'ext_stakeholder.tsv'),
    ('ext/stk_alert.tsv', 'ext_stakeholder_alerts.tsv'),
    ('ext/ptn.tsv', 'ext_partner.tsv'),
    ('ext/sla.tsv', 'ext_sla_mou.tsv'),
    ('ext/ctr.tsv', 'ext_contract.tsv'),
    ('pip/pol.tsv', 'policy_list.tsv'),
    ('pip/mem.tsv', 'member_ledger.tsv'),
    ('pip/beta.tsv', 'beta_ledger.tsv'),
    ('pip/pi.tsv', 'pip_ledger.tsv'),
]
PRIVATE_COL = {'ext_stakeholder.tsv': ('요금·한도', ('결제일', '결제 ', '결제('))}


def build(src_path, out_name):
    raw = open(src_path, encoding='utf-8').read().replace('\r\n', '\n').replace('\r', '\n')
    lines = [l for l in raw.split('\n') if l != '']
    if not lines:
        raise SystemExit('머리글 없음: ' + src_path)
    head = lines[0].split('\t')
    rows = [l.split('\t') for l in lines[1:]]
    for i, r in enumerate(rows, 2):
        if len(r) != len(head):
            raise SystemExit('%s %d줄: 칸 %d개(머리글 %d개)' % (src_path, i, len(r), len(head)))
    masked = 0
    if out_name in PRIVATE_COL:
        cname, words = PRIVATE_COL[out_name]
        if cname not in head:
            raise SystemExit('%s: 「%s」 칸 없음' % (src_path, cname))
        ci = head.index(cname)
        for r in rows:
            if any(w in r[ci] for w in words):
                r[ci] = NA
                masked += 1
    text = '\t'.join(head) + '\n' + ''.join('\t'.join(r) + '\n' for r in rows)
    return text, len(rows), masked


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    src = args[0] if len(args) > 0 else '/mnt/user-data/outputs'
    root = args[1] if len(args) > 1 else os.getcwd()
    out_dir = os.path.join(root, 'cowork', 'ctl')
    if not os.path.isdir(out_dir):
        raise SystemExit('게시 원천 폴더 없음: ' + out_dir)
    diff = 0
    for s, o in MAP:
        sp = os.path.join(src, s)
        if not os.path.exists(sp):
            raise SystemExit('원천 없음: ' + sp)
        text, n, masked = build(sp, o)
        op = os.path.join(out_dir, o)
        old = open(op, encoding='utf-8').read() if os.path.exists(op) else None
        same = old == text
        if check:
            print('%-28s %3d줄 %s' % (o, n, '같음' if same else '다름'))
            diff += 0 if same else 1
            continue
        if not same:
            with open(op, 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)
        print('%-28s %3d줄 %s%s' % (o, n, '그대로' if same else '씀', (' · 가린 칸 %d' % masked) if masked else ''))
    if check and diff:
        sys.exit(1)


if __name__ == '__main__':
    main()
