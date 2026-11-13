#!/usr/bin/env python3
# 대표 지시 한 장씩 쌓기(261113 이력 1129). 모델통제 이력에서 「대표님」으로 시작하는 줄마다 텍스트 한 장을 만든다.
#   gen   : 없는 장을 모두 만든다(있는 장은 원문이 새로 잡혔을 때만 다시 씀). 색인 ceo_orders_index.tsv 갱신
#   check : 이력에 대표님 줄이 있는데 장이 없으면 「실패:」, PC 폴더에 올린 기록(ceo_orders_pc.tsv)이 없으면 「알림:」
import sys,os,re,json,glob,collections
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H=R+'/cowork/ctl/model_control_history.tsv';D=R+'/cowork/ctl/ceo_orders/';IDX=R+'/cowork/ctl/ceo_orders_index.tsv';PC=R+'/cowork/ctl/ceo_orders_pc.tsv'
def hist(): return [r for r in (l.rstrip('\n').split('\t') for l in open(H,encoding='utf-8-sig')) if len(r)>=10 and re.match(r'\s*대표님',r[6]) and r[0].isdigit()]
def names():
    seen=collections.Counter();out=[]
    for r in hist():
        m=re.search(r'(\d\d):(\d\d)',r[3]);hm=(m.group(1)+m.group(2)) if m else '0000'
        n='대표지시_%s-%s_%s'%(r[0].zfill(4),r[1][2:].replace('-',''),hm);seen[n]+=1
        out.append((r,n+('' if seen[n]==1 else '_%d'%seen[n])+'.txt'))
    return out
def raws():
    raw=collections.OrderedDict()
    for f in glob.glob('/root/.claude/projects/-home-claude/*.jsonl'):
        for l in open(f,errors='ignore'):
            try:o=json.loads(l)
            except Exception: continue
            if o.get('type')=='user':
                c=(o.get('message') or {}).get('content')
                if isinstance(c,str): full=c
                elif isinstance(c,list):
                    if any(isinstance(x,dict) and x.get('type')=='tool_result' for x in c): continue
                    full='\n'.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
                else: continue
            elif o.get('type')=='attachment' and (o.get('attachment') or {}).get('type')=='queued_command':
                p=o['attachment'].get('prompt'); full=p if isinstance(p,str) else '\n'.join(x.get('text','') for x in p if isinstance(x,dict))
            else: continue
            m=re.search(r'Message sent at \w+ (\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d) local',full)
            b=re.sub(r'<system-reminder>.*?</system-reminder>','',full,flags=re.S).strip()
            if not m or not b or re.match(r'(Stop hook feedback|\[SYSTEM NOTIFICATION|This session is being continued|Another Claude session|<local-command|<command-name>)',b): continue
            b=re.sub(r'@"/mnt/user-data/attachments/[^"]+"\s*','(앞 답변의 한 대목을 가리키심) ',b)
            k=(m.group(1)+'-'+m.group(2)+'-'+m.group(3),m.group(4)+':'+m.group(5));raw.setdefault(k,[])
            if b not in raw[k]: raw[k].append(b)
    return raw
def gen():
    os.makedirs(D,exist_ok=True);raw=raws();used=set();idx=[];new=[]
    for r,name in names():
        orig=None;cand=[]
        tm=re.search(r'\((\d\d):(\d\d)',r[6]);m=re.search(r'(\d\d):(\d\d)',r[3])
        if tm: cand.append((r[1],tm.group(1)+':'+tm.group(2)))
        if m: cand.append((r[1],m.group(1)+':'+m.group(2)))
        for k in cand:
            if k in raw and k not in used: orig='\n\n'.join(raw[k]);used.add(k);break
        p=D+name;old=open(p,encoding='utf-8').read() if os.path.exists(p) else None
        if old is not None and not orig:
            # 원문이 이미 든 장은 지키고, 조치·상태만 바뀐 요지 장은 다시 씀
            if '[인식 원문]' in old: idx.append([r[0],r[1],r[3],name,'원문 있음',r[5],r[4]]);continue
        b='대표 지시 한 장 — 이력 %s\n\n때: %s (%s)\n받은 모델: %s\n이력 구분: %s\n창: 페이블 261104\n\n'%(r[0],r[1],r[3],r[4],r[5])
        if orig: b+='[인식 원문] (이 창 기록 그대로, 음성 인식 글자 포함)\n%s\n\n'%orig
        b+='[이력에 적힌 말씀 요지]%s\n%s\n\n[원인]\n%s\n\n[조치]\n%s\n\n[상태] %s\n\n'%('' if orig else ' (원문은 이 창 기록에 남아 있지 않아 이력의 요지를 적음)',r[6],r[7],r[8],r[9])
        b+='맞대는 자리: SC-17 말 명령 · SC-13 모델통제 이력의 번호 %s (원천 cowork/ctl/model_control_history.tsv)\n'%r[0]
        if b!=old: open(p,'w',encoding='utf-8').write(b);new.append(name)
        idx.append([r[0],r[1],r[3],name,'원문 있음' if orig else '이력 요지',r[5],r[4]])
    # 이력 줄과 시각이 맞지 않은 원문도 한 장씩
    for k,v in raw.items():
        if k in used: continue
        name='대표지시_원문-%s_%s.txt'%(k[0][2:].replace('-',''),k[1].replace(':',''));p=D+name
        b='대표 지시 한 장 — 원문(이력 번호와 시각이 따로 맞지 않은 말씀)\n\n때: %s %s\n창: 페이블 261104\n\n[인식 원문] (이 창 기록 그대로, 음성 인식 글자 포함)\n%s\n\n맞대는 자리: 같은 시각대의 SC-17 말 명령 · 모델통제 이력\n'%(k[0],k[1],'\n\n'.join(v))
        if not os.path.exists(p) or open(p,encoding='utf-8').read()!=b: open(p,'w',encoding='utf-8').write(b);new.append(name)
        idx.append(['원문',k[0],k[0][5:].replace('-','/')+' '+k[1],name,'원문 있음','원문','—'])
    # 예전 기록에서 원문으로 만든 장은 기록이 사라져도 색인에 남김
    have={x[3] for x in idx}
    for f in sorted(os.listdir(D)):
        if f.startswith('대표지시_원문-') and f not in have:
            m=re.match(r'대표지시_원문-(\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)',f);idx.append(['원문','20%s-%s-%s'%m.group(1,2,3),'%s/%s %s:%s'%m.group(2,3,4,5),f,'원문 있음','원문','—'])
    open(IDX,'w',encoding='utf-8').write('이력 번호\t날짜\t시각\t파일\t본문 갈래\t이력 구분\t받은 모델\n'+'\n'.join('\t'.join(x) for x in idx)+'\n')
    print('대표 지시 장 %d · 이번에 쓴 장 %d'%(len(idx),len(new)))
    for n in new: print('쓴 장\t'+n)
def check():
    bad=0;up={}
    if os.path.exists(PC):
        for l in open(PC,encoding='utf-8'):
            a=l.rstrip('\n').split('\t')
            if len(a)>1: up[a[0]]=a[1]
    import hashlib;wait=0;tot=0
    for r,name in names():
        tot+=1
        if not os.path.exists(D+name): print('실패: 이력 %s 대표 지시 장 없음(python3 tools/ceo_order_file.py gen)'%r[0]);bad+=1;continue
        if up.get(name)!=hashlib.md5(open(D+name,'rb').read()).hexdigest(): wait+=1
    if wait: print('실패: 대표 지시 장 %d장이 91_02_01_대표지시 폴더에 없음 또는 다름 — python3 tools/ceo_pc_sync.py pending → PC 올림 → 다시 받기 → verify (이력 1180)'%wait);bad+=wait
    print('대표 지시 장 점검: 이력의 대표님 줄 %d · 장 없음 %d · 폴더 올림 대기 %d'%(tot,bad,wait));sys.exit(1 if bad else 0)
if __name__=='__main__': (check if sys.argv[1:2]==['check'] else gen)()
