# T-W19-04 접점표 산출(Opus, 워크 0006) — 모델이 직접 실행하는 산출 스크립트(자동 실행 장치 아님)
# 입력: 사업부 설정안 6장 연동표 TSV 5권(노트북 최신본) + 결정 묶음 B-1(대표님 승인 11/05 03:54)
# 출력: cowork/ctl/bg_contact.tsv(연동 접점 30행) · cowork/ctl/bg_source.tsv(사업군별 감지 원천·경고 기준 7행)
import csv,glob,os,hashlib
U='/mnt/user-data/uploads/HiBiz/';G='/home/claude/hiven-ai-site/cowork/ctl/'
SRC=[('HiASI','31_HiASI/02_설정안(SET)/HiASI_사업_설정안_6장_연동표-261105_2.0_작업.tsv'),
 ('HiDAM','33_HiDAM/02_설정안(SET)/HiDAM_사업_설정안_6장_연동표-261105_1.0_작업.tsv'),
 ('HiICT','34_HiICT/02_설정안(SET)/HiICT_사업_설정안_6장_연동표-261105_2.0_작업.tsv'),
 ('HiServe','35_HiServe/02_설정안(SET)/HiServe_사업_설정안_6장_연동표-261106_1.0_작업.tsv'),
 ('HiTrade','37_HiTrade/02_설정안(SET)/HiTrade_사업_설정안_6장_연동표-261106_1.0_작업.tsv')]
def sev(a):  # B-1-3: 「즉시」(중지·차단 포함) = 상 → 경고 상자 즉시 반영, 「경고」 = 중, 그 외 = 하(목록만)
    return '상' if '즉시' in a else '중' if '경고' in a else '하'
REL='조치 완료 + Fable 확인 「처리 완료」'  # B-1-4
out=[['번호','원천','사업부A','사업부B','주는 것','받는 것','AICS 접점','감지 신호','경보 기준','심각도','해제 기준','원천 해시']]
n=0
for bg,p in SRC:
    raw=open(U+p,encoding='utf-8').read();h=hashlib.md5(raw.encode()).hexdigest()[:8]
    for r in list(csv.reader(raw.splitlines(),delimiter='\t'))[1:]:
        if len(r)<7:continue
        n+=1;out.append(['C-%02d'%n,os.path.basename(p),r[0],r[1],r[2],r[3],r[4],r[5],r[6],sev(r[6]),REL,h])
with open(G+'bg_contact.tsv','w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows(out)
# B-1-2: 사업군별 감지 원천·경고 기준(AICS 재설계안 2.0 §5 후보 → 확정)
S=[['사업군','감지 원천','경고 기준','연동표 접점 수','확정'],
 ['HiASI','에이전트 실행 통제 로그','안전 기능 경보'],['HiCoffer','베타 사용자 문의·오류 보고(PC 베타1, 11월 말)','응답 기한 임박·크래시'],
 ['HiDAM','분류 체계 위반·형상 불일치(HiAad 포함)','FDS 불일치 1건 이상'],['HiICT','계약·수행 일정 지연','마감 24시간 전 미완'],
 ['HiServe','제휴 서비스 품질·분쟁 접수','분쟁 1건'],['HiSilver','—(1차 배포 2027-02-25 이후, D3)','—'],['HiTrade','심사 결과·거래 이상','분쟁 경보']]
for r in S[1:]:
    r.append(str(sum(1 for x in out[1:] if r[0] in (x[2],x[3]))));r.append('대표님 승인 11/05 03:54(결정 B-1-2)')
with open(G+'bg_source.tsv','w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows(S)
print(n,'접점',{s:sum(1 for x in out[1:] if x[9]==s) for s in '상중하'})
