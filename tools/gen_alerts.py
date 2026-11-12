#!/usr/bin/env python3
"""SC-07 경보 원장 갱신(Fable W0010 T-3, 이력 910): 모델이 호출될 때마다(커밋 관문마다) 실측 원천에서 경보를 만든다.
원천: model_control_history(열린 지시 거부), model_calls(지시자 호출), cs_tickets(고객 지원 열린 건), approval_line(결재 대기), HiClo 판정 정지(마지막 판정 11-03 20:54, PC 실측 16:27)."""
import datetime,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));C=os.path.join(R,'cowork','ctl')
now=datetime.datetime.utcnow()+datetime.timedelta(hours=9);ts=now.strftime('%Y-%m-%d %H:%M')
def rows(f):
  p=os.path.join(C,f)
  return [l.rstrip('\n').split('\t') for l in open(p,encoding='utf-8')][1:] if os.path.exists(p) else []
A=[];n=0
def add(rule,lv,tgt,txt,key,act,st):
  global n;n+=1;A.append(['AL-%03d'%n,ts,rule,lv,tgt,txt,'',key,act,st,''])
hc=datetime.datetime(2026,11,3,20,54);h=int((now-hc).total_seconds()//3600)
add('CR-01 원천 정지','경고','HiClo 판정','HiClo 마지막 판정 11-03 20:54 뒤 %d시간 갱신 없음(PC 실측: 93_25_HiClo_앱 마지막 파일 11-03 20:54)'%h,'HiClo_기억상태-261103.json','재가동 방법 결정 반영(결재 A-008 허가 15:47)','조치 중')
for c in rows('model_control_history.tsv'):
  if len(c)>9 and c[1]>='2026-11-12' and c[5] in ('지시거부','위반') and not any(k in c[9] for k in('조치 완료','처리됨')):
    add('CR-02 지시 거부','경보' if '조치 중' in c[9] else '위기',c[4],'이력 #'+c[0]+' '+c[9],'#'+c[0],'지시자 재확인','조치 중' if '조치 중' in c[9] else '미조치')
for c in rows('model_calls.tsv'):
  add('CR-03 지시자 호출','경보',c[1],'#'+c[3]+' 깜빡임 '+c[4]+'분','#'+c[3],c[5],'미조치')
for c in rows('cs_tickets.tsv'):
  if len(c)>8 and c[8]!='종결': add('CR-04 고객 지원','경보' if c[8]=='선대응 필요' else '관찰',c[7],c[0]+' '+c[5],c[0],c[10][:60],'미조치' if c[8]=='선대응 필요' else '조치 중')
for c in rows('approval_line.tsv'):
  if len(c)>7 and c[7]=='결재 대기': add('CR-05 결재 대기','관찰','대표님 결재',c[0]+' '+c[4][:50],c[0],'SC-00 결재','대기')
open(os.path.join(C,'alerts.tsv'),'w',encoding='utf-8').write('\n'.join(['경보 번호\t발생 시각\t규칙\t등급\t대상\t내용\t사건 코드\t추적 열쇠값\t조치\t상태\t해제 시각']+['\t'.join(a) for a in A])+'\n')
print('경보',len(A),'건')
