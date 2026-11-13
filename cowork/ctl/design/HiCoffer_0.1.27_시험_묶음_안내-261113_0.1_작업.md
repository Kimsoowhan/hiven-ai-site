현행 소통 작업 규칙·시행착오 기록을 준수한다.

# HiCoffer 0.1.27 시험 묶음 안내 (실행 묶음 1.4)

작성: Opus 5.5 · 2026-11-13 · 감독: Fable 5.2 · 상태: 작업본(Fable 대조 전에는 시험 기기에 올리지 않음)
근거: /home/claude/hs/cowork/ctl/design/HiCoffer_0.1.27_재시험_계획-261113_0.1_작업.md(② · ③ · ③-2 · ④ A-14·B-11) · Fable 지시(0.1.27 시험 묶음, 일 1~3)
산출물 자리: /mnt/user-data/outputs/hct127/

## 1. 시험 대상 판 지문 (직접 다시 잼)

| 항목 | 값 | 잰 방법 |
|---|---|---|
| 소스 | /home/claude/agent 가지 ui-0.1.27, 커밋 b20fefc(HEAD), 작업 트리 변경 0 | git log · git status |
| 설치 파일 | HiCoffer_Setup_0.1.27.exe · 7,293,643바이트 · 2026-11-13 17:52:55 · SHA256 36c940802d6fe5d3892a8ac2d93b84ae4392ea121f7187183062cc6a1c55ecc0 | stat · sha256sum (installer/out) |
| HiCoffer.exe | 1,004,032바이트 · SHA256 7d74e46c8348ad0b84033080a551d1dc22b2e2204bbe3f8626e80b1f64513bd5 | src/bin · installer/payload · src/obj 세 곳 같은 값 |
| 지시문 값과 대조 | 둘 다 같음(다른 값 없음) | |
| 글꼴 6개 | installer/out/SHA256SUMS.txt의 fonts/ 6줄 = installer/payload/fonts 실측 | 러너 A-9 |

계획서 ②의 「17:44 빌드 7,293,008바이트」는 지금 파일(17:52, 7,293,643바이트)과 다르다. 지금 out 폴더의 설치 파일이 지시문 지문과 같은 판이다.

## 2. 묶음 1.4에서 바뀐 것 (1.3은 /mnt/attach/outputs/oc1/O가2_실행묶음_시험가-261113_1.3_작업/ 그대로, 해시목록_1.3 대조 12건 일치)

| 지시 항목 | 1.4에서 한 것 | 파일 |
|---|---|---|
| 대상 판·해시 | APPVER 0.1.27 · 설치 파일·HiCoffer.exe 고정값 바꿈 · ④에서 글꼴 Pretendard 6개 해시 대조, 나눔고딕·OFL.txt가 남으면 멈춤(7) · 「출발 상태(새로 깖/덮어 깖)」를 실행기록에 남김 | run_bundle.ps1 |
| 0.1.27 화면·창 이름에 기대는 항목 | 묶음은 창 제목·단추 글자에 기대지 않음. 기대는 것(프로세스 이름 · 잠금 Local\HiCofferAgent · 시험 환경 변수 두 개 · settings.ini [app] 키 · notice_version 2 · 00_관리\hcdam.ini · 주 화면 핸들)이 0.1.27 소스에서 그대로임을 확인(Program.cs:16·54 · Agent.cs:34·62·71·130~154 · MainForm.cs:153 「Hi Coffer」). 바꿀 확인 항목 없음 | 00_묶음안내.txt 0절 |
| 0.1.26 정리 순서 | 방식 넷을 더함: State(상태 기록, 읽기만) → Collect(앞 시험 기록 거둠, 원본 그대로·사본만, 대조 다르면 14) → Upgrade(덮어 깔기 확인 B-11, 판 값·exe·글꼴·설정 파일·00_관리 목록 대조, 다르면 7, -LaunchAfter면 실제 설정으로 한 번 띄움) → [제거·휴지통 이동은 묶음 밖] → CleanCheck(비움 확인, 남으면 13) → Short → Full | run_bundle.ps1 · install_state.ps1 · collect_0126.ps1 |
| 두 기기 같은 묶음 | -Device "이름" → 기기기록.tsv(기기 이름·컴퓨터 이름·제조사·모델·OS·빌드·코어·메모리·묶음 판·방식) · 환경기록 W-0. W-1은 빌드 22000 이상 Windows 11, 아래 Windows 10으로 적고 둘 다 「확인」(1.3은 10을 「Windows 11 아님」으로 적었음) | run_bundle.ps1 · env_record.ps1 |
| 증빙 폴더 이름 | C:\HCT_0127\RUN_·SHORT_·ENV_·STATE_·UPGRADE_·CLEAN_<시각>, 거둠은 C:\HCT_0126_거둠\<시각>. 0.1.26 기록(C:\HCT_시험가*)과 겹치지 않음. 결과 폴더 이름·맨 위 기록 파일 이름과 칸은 그대로 | run_bundle.ps1 |
| 가-갑·가-을 무효 사유를 시작 전에 거름 | ⓪ 안 「시작 전 확인 · 화면 잠금」(아래 3절). 가-갑 사유(안내 창 닫힘 뒤 주 화면 닫힘 · 09:17:57 뒤 PC 재시작)는 0.1.26 앱 고침과 W-7·P-9로 이미 다루고, 1.4는 가-을 첫 사건(13:33:12 화면 잠금)을 막음 | lock_check.ps1 |

바꾸지 않은 것: 시험 묶음 압축본 HCT_시험가_묶음-261112_1.0_작업.zip(1f66c88a…12fe)과 풀린 목록 해시(5c6d1c33…4a34) · ①~⑧ 단계 순서 · P-9 무효 규칙 · 창 없는 본 시험·끝난 까닭·살아 있음 기록·증적 사본 · evidence_keep·exit_trace·manifest_hash·p5_check·pack_list·resource_record 6개 파일(해시가 1.3과 같음).

## 3. 시작 전 확인 · 화면 잠금 (읽기만, 설정은 바꾸지 않음 — 바꾸는 일은 대표님)

결과 파일: <결과 폴더>\시작전확인_잠금.tsv. 아래 가운데 하나라도 걸리면 본 시험·맛보기는 시작하지 않고 종료 코드 12와 까닭을 실행기록·단계기록·끝난까닭에 남긴다. 환경만(EnvOnly)은 기록만 한다. 절전 막음(⓪)은 이 확인을 통과한 뒤에만 켠다.

| 번호 | 읽는 값 | 막는 조건 |
|---|---|---|
| L-0 | 전원 선 연결 | 막지 않음. 연결이면 AC 값, 아니면 DC 값으로 L-4 판정 |
| L-1 | 동적 잠금 EnableGoodbye(HKCU) · 정책 DynamicLock(HKLM) | 둘 중 하나라도 1 |
| L-2 | 화면 보호기 사용·다시 켤 때 로그인·대기 시간(정책 값 먼저) | 셋이 함께 켜짐(대기 > 0) |
| L-3 | 비활성 잠금 시간 InactivityTimeoutSecs | > 0 |
| L-4 | 깨어날 때 로그인 요구(CONSOLELOCK) · 화면 꺼짐 시간 · 모던 대기(S0, powercfg /a 첫 단락) · 잠금 지연 값 | 로그인 요구 + 화면 꺼짐 > 0 + 모던 대기 있음(또는 확인 안 됨) |
| L-5 | 절전 전환 | 막지 않음(⓪가 시험 동안 0으로 두고 끝에 되돌림) |
| L-6 | 지금 잠금 화면(LogonUI 프로세스) | 떠 있음 |

값을 읽지 못한 항목은 「막음(읽지 못함)」으로 막는다. Dell은 계획서 ③ 기준으로 동적 잠금이 켜져 있어 L-1로 막힐 것으로 읽힌다(기기 확인 안 됨). 잠금을 걸리지 않게 하는 방법과 자리 비움 때의 보안 대책은 계획서 ③ 1번대로 미정이며 이 묶음은 정하지 않는다.

## 4. Linux에서 한 검사 (일 2)

| 검사 | 결과 | 근거 파일 |
|---|---|---|
| 러너 1.4(정적 검사 + 절차 재현) | 219건 통과 · 실패 0 · 종료 코드 0 | /mnt/user-data/outputs/hct127/러너결과_1.4/실행기록.txt · 정적검사.tsv |
| 스크립트 문법 | 11개 .ps1 모두 UTF-8 BOM · 괄호 균형 · 금지 단어 0 · 지우기·옮기기·끄기·설정 쓰기·외부 통신 명령 0 · 실제 자료 자리 0 · 대소문자만 다른 변수 이름 0 · 시작.cmd ASCII | 정적검사.tsv |
| 표본 파일 목록·해시 | 압축본 1f66c88a…12fe 일치 · 풀린 723개 목록 해시 5c6d1c33…4a34 일치 · 종료 대조(그대로·바뀜) 재현 | 묶음목록_시작.tsv · 묶음목록_종료.tsv |
| 0.1.27 해시 대조 | 설치 파일·HiCoffer.exe 고정값 = SHA256SUMS 0.1.27 · 글꼴 6개 고정값 = SHA256SUMS = payload 실측 | 실행기록.txt A-9 |
| 잠금 판정 재현 | 12사례 기대값 일치(Dell 꼴 동적 잠금 · 정책 · 화면 보호기 · 비활성 · 모던 대기/S3 · 배터리 DC · 못 읽음 · 잠금 화면 · 걸림 없음) | 잠금판정_사례.tsv |
| 정리 순서 흐름 재현 | 13사례 종료 코드 기대값 일치 | 정리순서흐름_사례.tsv |
| 1.3 흐름·프로세스 모형 | 16사례 · 떼어 띄움·감시 둘·상대 사라짐 재현 그대로 통과 | 단계흐름_사례.tsv · 프로세스모형_재현.tsv |
| 엔진 시험 | test 프로젝트를 다시 빌드해(산출은 작업 폴더 밖 scratchpad) 재실행: PASS 201 · FAIL 0 · ALL PASS. 저장소 test/last_test.txt와 다른 줄은 시각·임시 경로·무작위 복구 코드·응답 ms뿐 | 러너결과_1.4/엔진시험_재실행-261113.txt |
| 실제 PowerShell 파서로 문법 검사 | 하지 못함: 컨테이너에 PowerShell이 없고, 받아 오는 길은 NuGet(프록시 403)·GitHub 내려받기(실행 허가 거부) 모두 막힘. 위 정적 검사로 갈음하고 Windows 표 1번에 둠 | |

러너는 Windows 실제 실행 기록이 아니라 같은 규칙의 논리 재현이다.

## 5. Windows에서 확인할 것

| 번호 | 확인할 것 | 어떻게 | 기대 |
|---|---|---|---|
| W1 | 11개 .ps1이 PowerShell 5.1에서 문법 오류 없이 읽힘 | -Mode EnvOnly -Device "이름" 한 번(쓰기는 C:\HCT_0127\ENV_<시각>만) | 종료 코드 0, 실행기록에 오류 줄 없음 |
| W2 | 시작전확인_잠금.tsv 값이 기기 설정과 맞음 | EnvOnly 결과 읽기 | Dell L-1 「막음」(동적 잠금 켜짐이면), LG L-1 「통과」 |
| W3 | powercfg /a 첫 단락 판독(한국어 출력) | L-4a 줄 | 쓸 수 있는 대기 상태 줄만 담김 |
| W4 | 잠금 설정이면 Short·Full이 12로 막히고 설정을 바꾸지 않음 | -Mode Short | 종료 코드 12, 전원설정_되돌림.txt 없음 |
| W5 | State 기록 | -Mode State | 설치상태_정리전.tsv의 판 값 0.1.26, HiCoffer.exe 해시 aeece2d3…f68c(Dell, 가-을 판), data_root, 바로가기 두 개 |
| W6 | Collect 사본·대조 | -Mode Collect | 다름·실패 0, 사본에 읽기 전용 속성, 원본 폴더 수정 시각·개수 그대로 |
| W7 | Upgrade 덮어 깔기 | -Mode Upgrade -LaunchAfter | 판 0.1.26 → 0.1.27, exe 7d74e46c…, 글꼴 6개 같음·나눔고딕 없음, 설정 파일·00_관리 목록 그대로, 주 화면 뜸 |
| W8 | 덮어 깐 뒤 화면 | 띄운 HiCoffer 화면 | 원장 사슬 경고 없음, 같은 데이터 폴더(묶음은 화면 글자를 읽지 않음) |
| W9 | 제거 뒤 비움 확인 | (묶음 밖 제거·휴지통 이동 뒤) -Mode CleanCheck | 남은 자리 0, 종료 코드 0 |
| W10 | Windows 10 기기 기록 | LG에서 State·EnvOnly | 기기기록 OS 「Windows 10」, W-1 「확인 · Windows 10」, DisplayVersion 없으면 ReleaseId |
| W11 | 본 시험 창 없는 실행·끝난 까닭·살아 있음 | -Mode Short 뒤 본 시험 | 1.3과 같음(결과_시작창_* · 끝난까닭.tsv · 살아있음_*.tsv) |
| W12 | 24시간 동안 화면 잠금 0회(A-14) | 생존감시·끝난까닭·W-7 읽기 | 묶음은 잠금·해제 사건 자체를 따로 기록하지 않음(보안 기록 4800·4801은 높은 권한이 있어야 읽힘). 시작 전 L-6과 생존 기록으로만 가림 |
| W13 | 0.1.27 탐색 창(HW-15)이 떠 있을 때 주 화면 핸들 | 시험 중에는 아무도 열지 않음 | ⑤는 시작 직후 주 화면 핸들만 봄 |

## 6. 시험 기기에 올릴 것 (일 3)

목록 파일: /mnt/user-data/outputs/hct127/HCT_0127_시험기기_올릴것-261113_1.0_작업.tsv. 자리는 시험 전용 폴더 C:\HCT_0127\올림\(HiBiz 밖). 기기마다 같은 파일·같은 해시, Dell 먼저 · LG 나중.

| 차례 | 파일 | 크기(바이트) | SHA256 | 올린 뒤 |
|---|---|---|---|---|
| 1 | HiCoffer_Setup_0.1.27.exe | 7,293,643 | 36c940802d6fe5d3892a8ac2d93b84ae4392ea121f7187183062cc6a1c55ecc0 | 다시 받아 대조 |
| 2 | HCT_시험가_묶음-261112_1.0_작업.zip | 3,087,881 | 1f66c88a57c2109a476d45e337291eb06aeae65ca5ae2a4fbcbaf622fc1712fe | 다시 받아 대조, 풀지 않음 |
| 3 | O가2_실행묶음_시험가_0127-261113_1.4_작업.zip | 69,769 | aa5d8456b1c5de80c14ae5cfaeee23c8b1757f4f795cfb261a93953f99ec2f17 | 올림\ 에 풀고 14개를 4번과 대조 |
| 4 | 해시목록_1.4-261113.txt | 2,091 | ab126bae874dd617e8a46592f87fa9cdd34396afae0fa001e740dc0a911b9fd2 | 다시 받아 대조 |
| 5 | SHA256SUMS_0.1.27.txt | 826 | 4b757b993da8e53c5c976da89d679c10cb341508e4a1f5a720d5ba4fae0122ec | 다시 받아 대조 |

1·2번은 풀린 묶음 폴더의 위 폴더(올림\)에 있으면 묶음이 찾는다. 차례(기기마다 같게): State → Collect → Upgrade -LaunchAfter → (Fable이 알린 뒤 제어판 제거·휴지통 이동) → CleanCheck → Short → 본 시험. 모든 실행에 -Device "Dell XPS 15" 또는 -Device "LG 노트북".

## 7. 관리자 권한 요구 여부 (Fable 덧 판정 확인)

HiCoffer는 관리자 권한을 요구하지 않는다: app.manifest requestedExecutionLevel asInvoker, HiCoffer.nsi RequestExecutionLevel user(37행), 설치 자리 %LOCALAPPDATA%\Programs\HiCoffer · HKCU. 설치 파일(.onInit 132~140행)과 프로그램(Program.cs 47~49행)은 높은 권한으로 실행되면 경고만 띄운다. README.txt 5행의 「관리자 권한으로 실행하지 마십시오」는 요구가 아니라 금지 안내라 실제와 맞으며, 지울 줄은 없다.

## 8. 파일 경로

- 실행 묶음 1.4: /mnt/user-data/outputs/hct127/O가2_실행묶음_시험가_0127-261113_1.4_작업/ (00_묶음안내.txt · run_bundle.ps1 · lock_check.ps1 · install_state.ps1 · collect_0126.ps1 · env_record.ps1 · 그대로인 6개 · runner_container.py · 시작.cmd) 과 같은 이름 .zip
- 해시목록: /mnt/user-data/outputs/hct127/해시목록_1.4-261113.txt
- 러너·엔진 시험 결과: /mnt/user-data/outputs/hct127/러너결과_1.4/
- 올릴 파일 사본: /mnt/user-data/outputs/hct127/HiCoffer_Setup_0.1.27.exe · HCT_시험가_묶음-261112_1.0_작업.zip · SHA256SUMS_0.1.27.txt
- 올릴 것 목록: /mnt/user-data/outputs/hct127/HCT_0127_시험기기_올릴것-261113_1.0_작업.tsv
