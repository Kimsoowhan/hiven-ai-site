# HiCoffer Android — 개발 환경 뼈대 0.0.1 (작업본)
근거: HiCoffer_Android_설계안 1.1(T-W35-01) · 결정 A1(Android 8.0 = 최소 SDK 26) · A3(「모든 파일 접근」 미사용) · A5(GitHub Actions 빌드)
- app/ : Kotlin + Jetpack Compose, 화면 1개(뼈대). 인터넷·모든 파일 접근·카메라 권한 없음(최종 매니페스트에서 검사)
- app/src/main/assets/hidam-rules.json : Hi DAM 공용 분류 규칙(Mbiz 시험판 shared 사본)
- .github/workflows/android.yml : 디버그 APK 빌드 → 권한 정책 검사 → APK SHA256 → 결과물 보관
- 삭제 기능 없음(격리·이동·되돌리기만). 스토어 등록은 법인 설립 뒤.
