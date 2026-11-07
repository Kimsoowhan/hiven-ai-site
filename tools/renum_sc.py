# -*- coding: utf-8 -*-
"""SC 메뉴 번호 재배정 (대표님 지시 2026-11-07 14:42·14:45): 이상징후 및 보안체계(구 SC-16)=SC-02, 침입 예측·예방·대응·조치(구 SC-15)=SC-03, 구 SC-02~14는 SC-04~16으로 두 칸씩 내린다. (14:50 대표님 지정 순서로 최종 확정: MAP은 원래 번호 → 최종 번호. 실제 적용은 1~3단계로 나누어 같은 최종 결과)
현재 화면·표시 위치를 가리키는 파일에만 적용한다. 이력·기록 파일(model_control_history 등)은 당시 번호 그대로 두고, 대응표(sc_renumber_261107.json)로 읽는다."""
import re, sys, os, json, hashlib
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
MAP = {1: 1, 15: 3, 16: 2, 2: 4, 3: 5, 4: 15, 5: 13, 6: 6, 7: 12, 8: 9, 9: 11, 10: 16, 11: 10, 12: 8, 13: 14, 14: 7}   # 최종(14:50, 대표님 지정 순서)
MAP_DONE = True
FILES = ['app.js','data.js','sec.js','sec2.js','views0.js','views1.js','views2.js','views3.js','views4.js','views5.js','views6.js','views7.js',
 'tools/gen_aics_src.py','tools/gen_meta.py','tools/index_build.py','tools/praise_watch.py','tools/gen_six.py','tools/gen_sec_structure.py','tools/gen_views8.py','tools/man_src.py','tools/man_work.py','tools/man_bench.py',
 'cowork/publish_meta.json','cowork/README.md','cowork/ctl/emergency_manual.md','cowork/ctl/aics_docgen.tsv','cowork/ctl/bg_contact.tsv','cowork/ctl/model_control_index.json']
KEEP = ['cowork/ctl/model_control_history.tsv','cowork/ctl/model_control_history_작업본_261107_1106강도재산정전.tsv','cowork/ctl/history_reclass_log.tsv','cowork/ctl/history_wordfix_log.tsv','cowork/ctl/aics_changes.tsv','cowork/ctl/aics_qa.tsv','cowork/ctl/trace_h.tsv','cowork/ctl/trace_v.tsv','cowork/ctl/qa_checks.tsv','cowork/progress.json','cowork/board.md','cowork/log.tsv','cowork/reports','cowork/SC-13_추이그래프_확정사양.md']
OUT = os.path.join(ROOT, 'cowork', 'ctl', 'sc_renumber_261107.json')
if os.path.exists(OUT) and '--force' not in sys.argv:
    print('이미 적용됨:', OUT); sys.exit(0)
def sub(m): return 'SC-%02d' % MAP[int(m.group(1))]
rx = re.compile(r'SC-(0[1-9]|1[0-6])')
rep = {}
for f in FILES:
    p = os.path.join(ROOT, f)
    if not os.path.exists(p): rep[f] = 'missing'; continue
    s = open(p, encoding='utf-8').read()
    t, n = rx.subn(sub, s)
    if n: open(p, 'w', encoding='utf-8', newline='').write(t)
    rep[f] = n
doc = dict(instruction='대표님 2026-11-07 14:42 — 이상징후 및 보안체계를 SC-02로 올리고 기존 SC-02~15는 한 단계씩 하위로', map_old_to_new={'SC-%02d' % k: 'SC-%02d' % v for k, v in sorted(MAP.items())},
           names={'SC-01':'종합 현황','SC-02':'이상징후 및 보안체계 시스템(구 SC-16)','SC-03':'사업군 통제(구 SC-02)','SC-04':'구동 상태(구 SC-03)','SC-05':'말 명령(구 SC-04)','SC-06':'문서 자동 생성(구 SC-05)','SC-07':'체계 배포(구 SC-06)','SC-08':'고객 지원(구 SC-07)','SC-09':'수집·연동(구 SC-08)','SC-10':'검수·품질(구 SC-09)','SC-11':'대응·경보(구 SC-10)','SC-12':'형상·변경(구 SC-11)','SC-13':'통합사업 작업상황(구 SC-12)','SC-14':'모델 통제 상황(구 SC-13)','SC-15':'베타1 배포 모니터링(구 SC-14)','SC-16':'침입 예측·예방·대응·조치 시스템(구 SC-15)'},
           changed=rep, kept_as_history=KEEP, note='KEEP 목록은 당시 번호 그대로 두었다. 읽을 때 map_old_to_new로 대응한다. CSS 클래스·요소 이름(sc12, sc13 등)은 내부 이름이라 바꾸지 않았다.')
json.dump(doc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False))
