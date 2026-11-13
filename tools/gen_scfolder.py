#!/usr/bin/env python3
# 화면 ↔ HiBiz 원천 폴더 ↔ 원천 대장 정합표(aics_scfolder.tsv). HiBiz 실측(hibiz_tree.tsv)과 화면 구조표(sc_structure.tsv)로 만든다. Fable 5.2 · 대표님 11-13 19:13 지시
import re
C='cowork/ctl/'
tree=[l.split('\t') for l in open(C+'hibiz/hibiz_tree.tsv',encoding='utf-8').read().split('\n')[1:] if l]
tops=sorted(set(r[0].split('/')[0] for r in tree));files=[r[0] for r in tree if r[1]=='file']
LED={'SC-00':['대표지시_'],'SC-01':['고객'],'SC-05':['폴더안내'],'SC-08':['HIVEN_서비스_기반_목록','HIVEN_분류_체계_총괄서','HIVEN_협업_분류_체계'],'SC-09':['HIVEN_배포_판_대장'],'SC-15':['HiBiz_문서_규칙표','HiBiz_문서_생애_절차','HiBiz_규칙_검사_결과','HiBiz_실측_싱크_기록'],'SC-17':['대표지시_'],'SC-18':['Stakeholder_목록','받은_얼럿'],'SC-19':['협력사_목록','SLA_MOU'],'SC-20':['정관_대장','HIVEN_정관_초안','이용약관_정책_목록','회원_관리_대장','베타_설치_대장','개인정보_처리_대장','개인정보_처리_위탁_국외_이전_목록'],'SC-21':['계약_대장','계약_갈래_열']}
out=[]
for l in open(C+'sc_structure.tsv',encoding='utf-8').read().split('\n')[1:]:
    c=l.split('\t')
    if len(c)<6: continue
    fo=[t for t in tops if t in c[5] or re.search(r'(^|[^0-9])%s_HIV'%re.escape(t[:2]),c[5])]
    have=[k for k in LED.get(c[0],[]) if any(k in f for f in files)];miss=[k for k in LED.get(c[0],[]) if k not in have]
    st='맞음' if fo and not miss else ('폴더 빠짐' if not fo else '대장 빠짐: '+' · '.join(miss))
    out.append([c[0],c[1],c[2],' · '.join(fo),' · '.join(have) or '-',st])
open(C+'aics_scfolder.tsv','w',encoding='utf-8').write('화면\t이름\t흐름 자리\tHiBiz 원천 폴더(실측에 있는 것)\t원천 대장(실측에 있는 것)\t정합\n'+''.join('\t'.join(r)+'\n' for r in out))
import collections;print(collections.Counter(r[5].split(':')[0] for r in out))
