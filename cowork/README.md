# /cowork — 통합사업관리 작업상황 게시본 (SC-12 v2)
대시보드 hiven.ai.kr 의 SC-12 가 이 폴더의 파일을 읽어 진척도를 보여 준다. **푸시가 곧 게시**다. 자동 동기화·예약작업·GitHub Actions는 없다(AICS 보류 정책).

## 파일
| 파일 | 내용 | 누가 쓰나 | 언제 |
|---|---|---|---|
| progress.json | 기계용 진척도(updated, items[], models{}, week). SC-12 화면의 원천 | 각 모델(자기 줄만)·Fable | 상태 바뀔 때마다, board.md와 동시에 |
| board.md | COM 진행상황판 사본(표 그대로). 원본은 COM 폴더 | 각 모델(자기 줄만)·Fable | progress.json과 동시에 |
| reports/index.json | 일일보고 목록. 배열, 한 건 = {"file","model","date","title"} | 각 모델 | 일일보고를 저장할 때 한 줄 추가 |
| reports/일일보고_<모델>_YYMMDD.txt | 일일보고 6줄 | 각 모델 | 작업 종료 시 |
| log.tsv | 시각 \t 모델 \t W# \t 상태 \t 메모 (append만) | 각 모델·Fable | 상태 바뀔 때마다 |
| 일일보고_템플릿.txt | 일일보고 양식 | — | — |

## 갱신 절차 (원본 보존: COM 폴더의 같은 파일이 원본)
1. COM 원본(진행상황판·일일보고·태스크대장)을 먼저 갱신한다.
2. 같은 내용을 이 폴더에 반영한다: progress.json(해당 W# 줄의 status·score·output·self_check·fable·approved·tasks, 맨 위 updated, models, week 재계산) → board.md 사본 → log.tsv 한 줄 추가 → 일일보고면 reports/ 에 txt 저장 + index.json 한 줄 추가.
3. 커밋 메시지: 「W# 상태 · 모델 · 시각」. 푸시는 Fable 검수·대표님 승인 뒤 Fable 지시로만(G4).
4. 삭제·이름변경 금지. 갱신과 추가만.

## 점수·권한
- 점수: 대기 0 / 진행 중 30 / 완료·검수 대기 70 / Fable 통과 90 / 승인·반영 100. 주간 = 전체 평균, 모델별 = 담당 W# 평균.
- 0→30, 30→70: 모델 본인 / 70→90, 재작업·위반: Fable / 90→100: 대표님 「승인」 후 Fable이 기입.

## 화면(SC-12)이 하는 일
카드 4(주간·모델별·오늘 완료/검수 대기·마지막 갱신) · W1~W13 막대 · 일일보고 목록(클릭 펼침) · 변경 로그 최근 30줄 · 30초마다 자동 새로고침. 파일을 못 읽으면 「게시본 없음 · 마지막 성공 시각」을 표시한다.
