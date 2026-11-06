import json,re,sys,glob,datetime
# 칭찬 사전: 만족·잘했다는 뜻. 인사(아침·저녁·밤 인사)는 제외
PRAISE=[r'잘했',r'잘 했',r'훌륭',r'좋았',r'좋겠다고 했',r'마음에 들',r'만족',r'맘에 들',r'고마워',r'고맙',r'감사',r'수고',r'최고',r'굿(?!모닝|나잇|이브닝|애프터눈)',r'땡큐',r'땡스',r'좋아',r'좋네',r'좋은 (?:판단|생각|부분|방법|결과)',r'멋져',r'멋지',r'대단',r'완벽',r'\bgood\b',r'\bgreat\b',r'\bnice\b',r'\bexcellent\b',r'\bawesome\b',r'\bperfect\b',r'\bthank(?:s| you| u)?\b',r'\bthx\b',r'\bthnx\b',r'\btnx\b',r'\bthanx\b',r'\bty\b',r'\bwell done\b',r'\bgood job\b',r'\bbravo\b',r'\bthx\b',r'\bthnx\b',r'\bthanx\b',r'\btks\b',r'\bty\b',r'\btysm\b',r'\bthank\s*u\b',r'쌩큐',r'쌩유',r'땡스',r'\bgj\b',r'\bgg\b']
OKW=[r'\bok(?:ay)?\b',r'오케이',r'오키',r'알겠어',r'승인']
GREET=[r'good\s+(?:morning|evening|night|afternoon|day)',r'굿\s*(?:모닝|나잇|이브닝|애프터눈)',r'좋은\s*(?:아침|저녁|밤|하루)',r'안녕',r'잘\s*자',r'굿밤']
pr=re.compile('|'.join(PRAISE),re.I); gr=re.compile('|'.join(GREET),re.I); okr=re.compile('|'.join(OKW),re.I)
def classify(t):
    t2=okr.sub(' ',gr.sub(' ',t))   # 인사·OK류(답변)를 먼저 지운 뒤 칭찬어를 찾는다
    m=pr.findall(t2)
    return m
if __name__=='__main__':
    since=datetime.datetime(2026,11,1,tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    for f in glob.glob('/root/.claude/projects/*/*.jsonl'):
        for ln in open(f,encoding='utf-8',errors='ignore'):
            try:d=json.loads(ln)
            except: continue
            if d.get('type')!='user': continue
            c=d.get('message',{}).get('content')
            if isinstance(c,list):
                c=' '.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
            if not isinstance(c,str): continue
            c=re.sub(r'<system-reminder>.*?</system-reminder>','',c,flags=re.S).strip()
            if not c or c.startswith('This session is being continued'): continue
            ts=d.get('timestamp','')
            try: dt=datetime.datetime.fromisoformat(ts.replace('Z','+00:00')).astimezone(since.tzinfo)
            except: continue
            if dt<since: continue
            m=classify(c)
            g=bool(gr.search(c))
            if m or g:
                print(dt.strftime('%m/%d %H:%M'),f.split('/')[-1][:8],'칭찬' if m else '인사(제외)',sorted(set(x.lower() for x in m)),'|',c[:110].replace('\n',' '))
