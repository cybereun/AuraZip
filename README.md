# AuraZip (아우라집)

> **차세대 고성능 통합 압축 & 보안 아카이브 유틸리티**

AuraZip은 현대적인 리본 메뉴(Ribbon Menu) 인터페이스와 고효율 멀티포맷 압축 엔진을 탑재한 올인원 데스크톱 압축 관리자입니다.

---

## 1. 전면 탑재된 리본 메뉴(Ribbon Menu) 구성 및 기능

첨부해주신 모든 메뉴 항목들을 체계적으로 분류하여 5개 탭의 **모던 리본 메뉴**로 구현하였습니다.

### 📁 1. 파일 / 홈 (File & Home)
- **기본 작업**:
  - `새로 압축 (Ctrl+N)`: 새 아카이브 생성 마법사
  - `열기 (Ctrl+O)`: 기존 아카이브 파일 열기
  - `압축 풀기 (Ctrl+E)`: 스마트 압축 해제 마법사
  - `닫기 (F4)`: 현재 열린 아카이브 닫기 및 시작 화면 전환
- **아카이브 관리**:
  - `다른 이름으로 저장...`: 아카이브 복제 및 새 위치 저장
  - `파일 위치 폴더 열기`: Windows 탐색기에서 현재 아카이브 파일 위치 즉시 표시
  - `압축 파일 삭제 (Ctrl+Del)`: 아카이브 휴지통 이동/삭제
  - `압축 파일 완전 삭제 (Shift+Ctrl+Del)`: 영구 삭제
- **창 및 세션**:
  - `새 창 띄우기 (Ctrl+Shift+N)`: 새 AuraZip 인스턴스 실행
  - `새 창 (관리자 권한) (Ctrl+Alt+N)`: 관리자 모드 실행
  - `AuraZip 종료 (Ctrl+W)`: 프로그램 닫기
- **최근 기록**:
  - `최근 파일 목록`: 최근 열어본 파일 드롭다운 메뉴로 원클릭 재열기

### ✏️ 2. 편집 (Edit)
- **파일 조작**:
  - `파일 추가 (Ins)`: 현재 아카이브에 파일/폴더 추가
  - `파일 삭제 (Del)`: 선택된 파일 삭제
  - `이름 바꾸기 (F2)`: 아카이브 내 파일 이름 변경
- **클립보드 연동**:
  - `클립보드로 복사 (Ctrl+C)`: 선택 항목 클립보드 복사
  - `클립보드에서 붙여넣기 (Ctrl+V)`: 클립보드 데이터 아카이브 반영
  - `파일 경로명 복사`: 선택된 파일의 내부 경로 텍스트 클립보드 복사
- **주석 & 선택**:
  - `설명(주석) 편집 (Ctrl+Shift+M)`: ZIP 아카이브 주석(Comment) 보기 및 편집
  - `모두 선택 (Ctrl+A)` & `선택 반전`

### 🛡️ 3. 도구 & 보안 (Tools & Security)
- **보안 & 검사**:
  - `무결성 검사 (Ctrl+T)`: 아카이브 블록 및 CRC-32 검증
  - `악성코드 검사 (Ctrl+I)`: Windows Defender 실시간 시그니처 위협 분석
- **복구 도구**:
  - `손상된 압축 파일 복구`: 불완전/손상된 스트림에서 온전한 파일 구조 복구
  - `압축 파일 암호 복구`: 사전식/패턴 기반 암호 복구 마법사
- **탐색**:
  - `파일 찾기 (Ctrl+F)`: 실시간 인라인 검색창 자동 포커스

### 👁️ 4. 보기 (View & Layout)
- **화면 표시**:
  - `시작 화면 (F6)`: 대시보드 토글
  - `경로 내비게이션 (F7)`: 브레드크럼 바 표시 설정
  - `상태 표시줄 표시`: 하단 상태바 토글
- **보기 옵션**:
  - `파일 설명창 (F8)`: 주석 뷰어
  - `이미지 미리보기 사용`: 썸네일 고속 모드
  - `항상 위에 표시`: 창 최상위 고정(Always on Top) 토글
- **테마 설정**:
  - `색상 / 테마 설정`: 인디고, 다크 슬레이트, 에메랄드, 미니멀 화이트 테마 전환

### ❓ 5. 도움말 (Help)
- **프로그램 안내**:
  - `AuraZip 정보 (F1)`: 버전 및 사양 대화상자
  - `설치 폴더 열기`: 프로그램 실행 폴더 Windows 탐색기 열기
  - `도움말 및 가이드`: 사용 설명서 및 단축키 가이드
  - `업데이트 확인`: GitHub Releases 연동 최신 버전 확인 및 원클릭 자동 업데이트

---

## 2. 프로젝트 파일 구성

| 파일 | 설명 |
|---|---|
| [`version.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/version.py) | **신규 추가**: 앱 버전(`v1.0.0`) 및 GitHub 저장소 정보 정의 |
| [`updater.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/updater.py) | **신규 추가**: GitHub API 릴리즈 감지, 백그라운드 OTA 다운로드 및 자동 재시작 업데이터 |
| [`build_installer.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/build_installer.py) | **신규 추가**: PyInstaller + Inno Setup 원클릭 통합 빌드 자동화 스크립트 |
| [`installer/aurazip_installer.iss`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/installer/aurazip_installer.iss) | **신규 추가**: Windows 설치 프로그램(Inno Setup) 구성 스크립트 (바탕화면/시작메뉴 바로가기 지원) |
| [`.github/workflows/release.yml`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/.github/workflows/release.yml) | **신규 추가**: 깃 태그 푸시 시 자동 빌드 및 릴리즈 업로드 GitHub Actions 워크플로 |
| [`ribbon.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/ribbon.py) | 5개 탭의 모던 리본 메뉴 컴포넌트 |
| [`extra_tools.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/extra_tools.py) | 주석 편집, 손상 복구, 암호 복구, 악성코드 검사, 테마 대화상자 |
| [`main_window.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/main_window.py) | 리본 메뉴, 비동기 OTA 업데이터, 전체 기능 액션 및 단축키 바인딩 |
| [`archive_engine.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/archive_engine.py) | ZIP/7Z/TAR/TGZ 압축, 스마트 해제, CRC-32 무결성 엔진 |
| [`archive_view.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/archive_view.py) | 아카이브 파일 브라우저, 용량 절약 대시보드, 실시간 검색 |
| [`start_view.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/start_view.py) | 모던 시작 화면 카드 및 대화형 드롭존 |
| [`dialogs.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/dialogs.py) | 새로 압축, 스마트 풀기, 암호 입력, 정보(About) 대화상자 |
| [`workers.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/workers.py) | UI 멈춤 방지용 비동기 스레드 처리기 |
| [`theme.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/theme.py) | 모던 QSS 스타일시트 테마 |
| [`assets/app_icon.ico`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/assets/app_icon.ico) | 투명 배경 고해상도 멀티사이즈 Windows 앱 아이콘 |

---

## 3. 설치 및 실행

### 1) 설치 파일(Setup Exe)로 설치
`dist_installer/AuraZip_Setup_v1.0.0.exe`를 실행하면 표준 Windows 설치 마법사가 시작되며, **바탕화면 바로가기** 및 **시작 메뉴 바로가기**가 자동으로 생성됩니다.

### 2) 개발 환경에서 직접 실행
```powershell
cd "y:\내 드라이브\AI\App_Bulid\AuraZip"
pip install -r requirements.txt
python main.py
```

### 3) 버전 업데이트 및 자동 배포 워크플로
1. [`version.py`](file:///y:/내%20드라이브/AI/App_Bulid/AuraZip/version.py)의 `APP_VERSION`을 변경 (예: `"v1.0.1"`)
2. Git commit 후 새 버전 태그 생성 및 푸시:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```
3. GitHub Actions가 자동으로 설치 exe를 빌드하여 GitHub Release에 게시합니다.
4. 사용자가 AuraZip을 실행하면 앱이 자동으로 새 버전을 감지하여 알림창을 띄우고, 원클릭으로 다운로드 및 자동 재시작 업데이트를 수행합니다.

