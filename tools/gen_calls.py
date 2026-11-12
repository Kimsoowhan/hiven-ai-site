#!/usr/bin/env python3
"""지시자 호출 원장(대표님 11-12 15:38, 이력 889): 조치 안 된 지시 거부가 1분 넘게 이어지면 지시자에게 호출을 남긴다."""
import datetime,os,re
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));C=os.path.join(R,'cowork','ctl')
H=[l.rstrip('\n').split('\t') for l in open(os.path.join(C,'model_control_history.tsv'),encoding='utf-8')][1:]
now=datetime.datetime.utcnow()+datetime.timedelta(hours=9)
def caller(m): return 'Opus 5.5' if re.search('Sonnet|Haiku',m) else 'Fable 5.2' if 'Opus' in m else '대표님 결재함'
out=['호출 시각\t지시자\t작업 모델\t이력\t지속(분)\t호출 문구']
for c in H:
  if len(c)>9 and c[5]=='지시거부' and not re.search('조치 완료|처리됨|조치 중',c[9]):
    m=re.search(r'(\d+)/(\d+) (\d+):(\d+)',c[3]);
    if not m: continue
    t=datetime.datetime(now.year,int(m[1]),int(m[2]),int(m[3]),int(m[4]));age=int((now-t).total_seconds()//60)
    if age>=1: out.append('\t'.join([now.strftime('%Y-%m-%d %H:%M'),caller(c[4]),c[4],c[0],str(age),'작업 모델에 내린 지시를 다시 확인하라']))
open(os.path.join(C,'model_calls.tsv'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print('호출',len(out)-1,'건')
