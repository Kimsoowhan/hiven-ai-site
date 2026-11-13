#!/usr/bin/env python3
"""하루 두 번 확인(09시·21시, 서울) — 지금 채워야 할 칸이 있는지 알려 준다. 예약·알람 없음. 모델이 움직일 때마다 한 번 돌려 본다.
쓰기: python3 tools/watch_due.py            (볼 칸이 있으면 종료 코드 3)
      python3 tools/watch_due.py add 09시|21시 "본 곳" "결과" [대상]   (대장에 한 줄 적음)"""
import sys,os,datetime
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG=os.path.join(B,'cowork','ctl','watch_log.tsv')
KST=datetime.timezone(datetime.timedelta(hours=9))
def rows():
    if not os.path.exists(LOG):return []
    return [l.split('\t') for l in open(LOG,encoding='utf-8').read().split('\n')[1:] if l.strip()]
def main():
    now=datetime.datetime.now(KST);d=now.strftime('%Y-%m-%d')
    if len(sys.argv)>1 and sys.argv[1]=='add':
        slot,where,res=sys.argv[2],sys.argv[3],sys.argv[4];tg=sys.argv[5] if len(sys.argv)>5 else 'WT-01'
        if slot not in('09시','21시'):sys.exit('칸은 09시 또는 21시')
        open(LOG,'a',encoding='utf-8').write('\t'.join([d,slot,now.strftime('%H:%M'),tg,where,res,'Fable'])+'\n');print('적음',d,slot);return
    done={(r[0],r[1]) for r in rows()}
    due=[s for s,h in(('09시',9),('21시',21)) if now.hour>=h and (d,s) not in done]
    # 어제 칸이 비었으면 「못 채움」으로 알려만 준다(꾸며 채우지 않음)
    y=(now-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    miss=[s for s in('09시','21시') if (y,s) not in done and any(r[0]<=y for r in rows())]
    if miss:print('어제 못 채운 칸:',y,' '.join(miss),'(「못 채움」으로 적을 것)')
    if due:print('지금 볼 칸:',d,' '.join(due));sys.exit(3)
    print('볼 칸 없음 ·',now.strftime('%H:%M'))
main()
