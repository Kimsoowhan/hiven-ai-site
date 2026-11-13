#!/usr/bin/env python3
# 턴 종료 관문: 작업 모델은 답을 끝내기 전에 이 검사를 돌린다(수행 체계 9절).
# 사용: python3 tools/turn_end_check.py "Sonnet 5.5"
# 종료 코드 0 = 턴 종료 가능, 1 = 턴 종료 금지(남은 줄을 계속 수행)
import sys,os,csv
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=R+'/cowork/ctl/work_queue.tsv'
m=sys.argv[1] if len(sys.argv)>1 else ''
rows=list(csv.DictReader(open(P,encoding='utf-8-sig'),delimiter='\t'))
bad=[]
for r in rows:
    if m and m.split()[0] not in r['맡는 모델']: continue
    s=r['상태'].strip()
    if s=='끝':
        if not r['끝 증거'].strip(): bad.append((r,'「끝」인데 끝 증거(파일·해시·실측)가 비어 있음'))
    elif s=='막힘':
        n=len([x for x in r['시도한 길'].split('|') if x.strip()])
        if n<3: bad.append((r,'「막힘」인데 시도한 길이 %d개(3개 이상이어야 함)'%n))
        if not r['판정 요청'].strip(): bad.append((r,'「막힘」인데 Fable 판정 요청 번호가 없음'))
    else:
        bad.append((r,'상태 「%s」 — 아직 수행하지 않았거나 수행 중'%s))
if bad:
    print('턴 종료 금지 · 남은 줄 %d (%s)'%(len(bad),m or '전체'))
    for r,w in bad: print(' - %s %s: %s'%(r['번호'],r['일감'][:40],w))
    print('위 줄을 위에서부터 계속 수행한다. 답을 끝내지 않는다.')
    sys.exit(1)
print('턴 종료 가능 · 남은 줄 0 (%s)'%(m or '전체'))
