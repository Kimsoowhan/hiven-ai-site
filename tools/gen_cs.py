#!/usr/bin/env python3
"""고객 지원 감지·분류기(대표님 11-12 16:19, 이력 907).
입력: cowork/ctl/cs_inbox.tsv(Gmail 수집분: 받은 시각, 받는 주소, 보낸 곳, 제목, 요약) → 출력: cs_tickets.tsv 신규 행.
감지 규칙: cowork/ctl/cs_rules.tsv. 비밀 값(코드·비밀번호)은 저장하지 않는다."""
import os,re
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));C=os.path.join(R,'cowork','ctl')
rules=[l.rstrip('\n').split('\t') for l in open(os.path.join(C,'cs_rules.tsv'),encoding='utf-8')][1:]
lvl={'긴급':3,'높음':2,'보통':1}
def classify(text):
  hit=[]
  for r in rules:
    for w in [x.strip() for x in r[1].split(',')]:
      if w and w.lower() in text.lower(): hit.append(r);break
  if not hit: return ('일반·확인 필요','보통','분류 확인','Sonnet(서비스)','')
  hit.sort(key=lambda r:(-lvl.get(r[3],0),-int(r[0][2:])));r=hit[0]
  return (r[2],r[3],r[4],r[5],'·'.join(h[0] for h in hit))
inbox=os.path.join(C,'cs_inbox.tsv');tk=os.path.join(C,'cs_tickets.tsv')
if not os.path.exists(inbox): print('수집분 없음');raise SystemExit
T=open(tk,encoding='utf-8').read().rstrip('\n').split('\n');seen={(l.split('\t')+['']*6)[1]+'|'+(l.split('\t')+['']*6)[5] for l in T[1:]}
n=max([int(l.split('\t')[0][3:]) for l in T[1:] if l.startswith('CS-')]+[0]);add=0
for l in open(inbox,encoding='utf-8').read().rstrip('\n').split('\n')[1:]:
  c=(l.split('\t')+['']*5)[:5]
  if c[0]+'|'+c[3] in seen: continue
  text=re.sub(r'\b\d{6}\b','******',c[3]+' '+c[4])
  cls,urg,act,own,rid=classify(text)
  n+=1;add+=1
  T.insert(1,'\t'.join(['CS-%03d'%n,c[0],c[1],'HIVEN assist(ai.kr)' if 'ai.kr' in c[1] else 'HIVEN contact(co.kr)',c[2],c[3],cls+(' · '+urg),own,'선대응 필요' if urg in('긴급','높음') else '접수','SC-17 · '+('SC-03' if cls=='보안' else 'SC-05' if cls=='기술 장애' else 'SC-00'),act+(' · 규칙 '+rid if rid else '')]))
open(tk,'w',encoding='utf-8').write('\n'.join(T)+'\n');print('신규',add,'건')
