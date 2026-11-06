# AuraZip Microsoft Store MSIX 빌드 및 검증

이 문서는 **제출 전 준비**입니다. Store에 등록·제출하거나 GitHub에 푸시하지 않습니다. GitHub용 Inno Setup EXE/포터블 ZIP 및 기존 GitHub 업데이트는 별도로 유지됩니다. MSIX는 Windows 10 1809 (빌드 17763) 이상 및 Windows 11, x64 전용 full-trust 데스크톱 패키지입니다. ARM64 전용 빌드는 제공하지 않습니다.

## 사전 준비와 비용

- Windows x64, Python 3.12 x64, Windows SDK의 x64 `MakeAppx.exe` 및 로컬 서명 테스트 시 `SignTool.exe`가 필요합니다. `python -m pip install -r requirements.txt pyinstaller`로 종속성을 설치합니다. SDK는 [Microsoft Windows SDK](https://developer.microsoft.com/windows/downloads/windows-sdk/)에서 받을 수 있습니다.
- [Microsoft의 MakeAppx 설명](https://learn.microsoft.com/en-us/windows/uwp/packaging/create-app-package-with-makeappx-tool)에 따라 PyInstaller onedir 결과를 직접 패키징합니다. 같은 소스에서 반복 가능하고 Inno Setup의 기본 앱 등록, 바로가기 및 관리자 권한 단계를 재생하지 않습니다. MSIX Packaging Tool은 기존 설치 프로그램을 캡처해야 할 때 대안이지만 설치 중 레지스트리와 파일 변경도 분석·정리해야 하므로, 이 앱처럼 onedir 산출물이 이미 있는 경우 직접 패키징을 우선합니다. 두 방식의 실제 안정성을 비교 테스트한 결과는 아닙니다.
- Microsoft 문서상 [새 개발자 등록 경로](https://learn.microsoft.com/en-us/windows/apps/publish/partner-center/open-a-developer-account)는 등록비가 없습니다. [MSIX Store 제출에는 유료 CA 인증서가 필요하지 않으며](https://learn.microsoft.com/en-us/windows/msix/package/sign-msix-package-guide) Microsoft가 심사 후 패키지를 서명합니다. 무료 배포 가격은 Partner Center에서 별도로 선택합니다. 계정 검증, Microsoft 정책 변경 및 Store 심사는 별도입니다. Azure 유료 서비스는 사용하지 않습니다.

## Partner Center 제품 ID

1. [새 등록 경로](https://storedeveloper.microsoft.com/)로 개발자 계정을 만든 후 앱 이름을 예약합니다.
2. Partner Center의 앱 → **Product management → Product identity**에서 `Package/Identity/Name`, `Package/Identity/Publisher`, `Package/Properties/PublisherDisplayName`을 확인합니다. [공식 안내](https://learn.microsoft.com/en-us/windows/apps/publish/view-app-identity-details).
3. `msix/identity.example.json`을 `msix/identity.local.json`으로 복사하고 세 항목을 **정확히** 기입합니다. Publisher는 `CN=...` 전체 문자열이며 대소문자를 보존합니다. Store ID, Publisher ID, 표시 이름과 혼동하지 마세요. 이 로컬 파일은 Git에서 제외됩니다.

```powershell
Copy-Item msix/identity.example.json msix/identity.local.json
notepad msix/identity.local.json
```

```json
{
  "identity_name": "Partner Center의 Package/Identity/Name",
  "publisher": "Partner Center의 Package/Identity/Publisher 전체",
  "publisher_display_name": "Partner Center의 PublisherDisplayName"
}
```

입력값이 없으면 제출용 빌드는 중단됩니다. **테스트 전용 가상 ID는 Store ID가 아니며 Store에 제출할 수 없습니다.**

## 빌드

프로젝트 루트에서:

```powershell
# 실제 Partner Center ID 없이 패키지 생성만 검증 (서명되지 않음)
python build_msix.py --build --test-identity

# 실제 ID를 identity.local.json에 입력한 뒤 Store 제출용 패키지 생성
python build_msix.py --build
```

`build/msix-pyinstaller/dist/AuraZip`에 Store 전용 PyInstaller onedir가 만들어지고, `dist_msix/AuraZip_1.0.6.0_x64_TEST.msix` 또는 `_STORE.msix`가 생성됩니다. 기존 `dist/AuraZip`을 덮어쓰지 않습니다. `--build` 없이 `--dist <Store onedir 경로>`로 기존 결과물을 재사용할 수 있습니다. 패키저는 내장 배포판 메타데이터가 `store`가 아닌 경우 중단합니다. `--makeappx <절대 경로>`로 SDK 도구를 지정할 수 있습니다.

기본 패키지 버전은 `version.py`의 `v1.0.6` → `1.0.6.0`입니다. `--version 1.0.6.0`으로 테스트할 수 있으나 실제 배포에서는 앱 버전과 일치시키고 이전 Store 패키지보다 높여야 합니다. 네 부분의 각 값은 0–65535, 첫 부분은 1 이상이고 네 번째는 Store용으로 0이어야 합니다. [공식 버전 규칙](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/package-version-numbering).

MakeAppx 기본 매니페스트 검증을 우회하지 않으며 오류는 종료 코드와 로그로 표시합니다. 유효성 검사는 설치·인증 통과의 보증이 아닙니다. `runFullTrust`, 파일 형식 연결, 로고와 두 언어 리소스를 선언합니다. .zip/.7z는 등록만 하며 기본 앱을 강제로 바꾸지 않습니다. 사용자가 Windows의 기본 앱 설정에서 직접 선택해야 합니다.

## 로컬 설치·업데이트·제거 테스트

기본 산출물은 **미서명**입니다. 아래는 테스트 전용 ID 패키지에만 사용할 임시 자체 서명 방법입니다. 테스트 PC에서만 진행하고, 패키지 Publisher와 인증서 Subject가 정확히 같아야 합니다. [Microsoft의 자체 서명 안내](https://learn.microsoft.com/en-us/windows/msix/package/sign-msix-package-guide)를 따릅니다. 신뢰 저장소 변경에는 관리자 권한이 필요합니다. 실서비스나 실제 Store 패키지의 인증서로 사용하지 마세요.

```powershell
# 관리자 PowerShell, 프로젝트 루트. 고유 테스트 인증서를 생성하고 thumbprint를 기록합니다.
$cert = New-SelfSignedCertificate -Type Custom -KeyUsage DigitalSignature `
  -Subject 'CN=AuraZip Development Test' -CertStoreLocation 'Cert:\CurrentUser\My' `
  -TextExtension @('2.5.29.37={text}1.3.6.1.5.5.7.3.3','2.5.29.19={text}') `
  -FriendlyName 'AuraZip MSIX development test only'
Export-Certificate -Cert $cert -FilePath "$env:TEMP\AuraZip-test-public.cer"
Import-Certificate -FilePath "$env:TEMP\AuraZip-test-public.cer" -CertStoreLocation 'Cert:\LocalMachine\TrustedPeople'
$sdk = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin\*\x64\signtool.exe" | Sort-Object FullName -Descending | Select-Object -First 1
$msix = (Resolve-Path 'dist_msix/AuraZip_1.0.6.0_x64_TEST.msix').Path
& $sdk.FullName sign /fd SHA256 /sha1 $cert.Thumbprint $msix
& $sdk.FullName verify /pa $msix
Add-AppxPackage -Path $msix
Get-AppxPackage -Name 'AuraZip.DevelopmentTest' | Select-Object Name,PackageFullName,PackageFamilyName,Version
```

시작 메뉴의 AuraZip을 실행하고 보기 → 언어에서 한국어·영어를 전환합니다. 임시 ZIP/7Z 파일에서 열기, 생성, 추출 및 Windows의 **연결 프로그램** 선택 후 더블 클릭을 확인합니다. 업데이트 확인이 Microsoft Store 안내만 표시하고 GitHub 설치 파일을 내려받거나 실행하지 않는지 확인합니다. 새 창, 사용자 폴더 읽기/쓰기, 테마 설정도 확인합니다. 기본 앱을 변경해 테스트할 경우 원래 설정을 기록하고 복원하세요.

업데이트 검증에는 **동일한 테스트 Name, Publisher, 인증서**로 더 높은 버전의 두 번째 패키지가 필요합니다. 앱 프로세스를 종료한 뒤 빌드·서명·설치합니다. 이 테스트는 패키지 업그레이드 검증이며 실제 Store 업데이트 검증이 아닙니다.

```powershell
python build_msix.py --test-identity --version 1.0.6.0
$next = (Resolve-Path 'dist_msix/AuraZip_1.0.6.0_x64_TEST.msix').Path
& $sdk.FullName sign /fd SHA256 /sha1 $cert.Thumbprint $next
Add-AppxPackage -Path $next
Get-AppxPackage -Name 'AuraZip.DevelopmentTest' | Select-Object Version
```

업그레이드 후 테마·언어, 아카이브 및 기존 GitHub 설치본을 확인합니다. 테스트 종료 후 아래 명령은 **정확한 테스트 ID와 위에서 만든 인증서의 thumbprint만** 제거합니다. `$cert` 변수는 같은 PowerShell 세션에 있어야 합니다. Store/다른 앱의 패키지나 인증서는 제거하지 마세요. 테스트 패키지를 제거하면 해당 패키지의 LocalState 설정도 제거될 수 있습니다.

```powershell
Get-AppxPackage -Name 'AuraZip.DevelopmentTest' | Remove-AppxPackage
Remove-Item -LiteralPath "Cert:\LocalMachine\TrustedPeople\$($cert.Thumbprint)"
Remove-Item -LiteralPath "Cert:\CurrentUser\My\$($cert.Thumbprint)"
Remove-Item -LiteralPath "$env:TEMP\AuraZip-test-public.cer"
```

또는 Windows 11의 특별한 테스트용 unsigned OID와 `Add-AppxPackage -AllowUnsigned`를 사용할 수 있으나 별도 ID와 관리자 권한이 필요하며 Store ID와 같지 않습니다. 이 빌드 스크립트의 테스트 Publisher는 unsigned OID를 포함하지 않으므로 위의 일반적인 자체 서명 경로를 사용합니다. [Microsoft unsigned 패키지 안내](https://learn.microsoft.com/en-us/windows/msix/package/unsigned-package).

## 첫 출시와 후속 업데이트

1. 실제 Partner Center ID로 Store 패키지를 다시 빌드합니다. 로컬 테스트 ID나 테스트 인증서는 실제 제품 ID가 아닙니다.
2. Partner Center에서 새 MSIX 앱 제출을 만들고 패키지와 한국어/영어 Store 설명, 스크린샷, 가격, 국가, 연령 등급, 개인정보 및 연락처 등 요구되는 정보를 입력합니다. 제출 전 Windows App Certification Kit과 실제 사용자 시나리오를 검사합니다. 패키지 업로드 및 심사 결과는 실제로 제출해야 알 수 있습니다. [제출 안내](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/create-app-submission?pivots=store-installer-msix).
3. 게시된 이후에는 `version.py` 버전을 올리고 같은 제품 ID로 빌드하여 Partner Center에서 새 패키지를 제출합니다. Store가 배포한 앱은 Store 업데이트를 사용하며 GitHub EXE 업데이트가 비활성화됩니다.
4. 첫 게시 이후 자동화를 원한다면 [Microsoft Store Developer CLI](https://learn.microsoft.com/en-us/windows/apps/publish/msstore-dev-cli/overview)와 Partner Center에 연결된 Entra ID 및 제한된 권한을 별도로 설정하고, 버전·패키지 검증 및 승인 단계를 거쳐 제출하는 후속 워크플로를 설계합니다. 현재 자동 제출은 구현·활성화되어 있지 않습니다. 공식 문서상 최초 게시에는 Partner Center가 필요합니다.

## GitHub Actions

변경 사항을 사용자가 검토하고 이후 직접 GitHub에 반영한 다음, **Actions → Build MSIX (no Store submission) → Run workflow**를 선택합니다. ID 세 항목을 모두 비우면 테스트 ID, 세 항목을 모두 입력하면 실제 ID로 빌드합니다. 일부만 입력하면 실패합니다. 작업 완료 후 `AuraZip-MSIX-unsigned` 아티팩트에서 내려받습니다. 인증서, PFX, 비밀번호나 Store 제출 단계는 없습니다. 워크플로는 수동 실행만 지원하며 기존 `release.yml`과 독립적입니다.

## 호환성 및 한계

- Store 배포판은 실행 파일에 포함된 메타데이터로 구분하며 런타임 환경 변수를 사용하지 않습니다. 메타데이터가 없거나 손상된 패키지에서는 GitHub 업데이트가 차단됩니다. GitHub 빌드는 기존 QSettings 및 GitHub 업데이트를 유지합니다.
- Store 빌드의 테마·언어는 `%LOCALAPPDATA%\Packages\<PackageFamilyName>\LocalState\settings.ini`에 저장해 기존 GitHub 설치본의 설정을 덮어쓰지 않습니다. Store 앱 삭제 시 이 설정은 삭제될 수 있으며, 기존 설정은 자동으로 가져오지 않습니다. 같은 패키지 ID의 업데이트 시 유지되어야 하지만 실제 설치 및 업데이트 테스트로 확인해야 합니다.
- 패키지 설치 디렉터리는 읽기 전용이며 앱은 사용자 지정 경로에 저장합니다. 일반 사용자 권한과 Windows 접근 제한이 적용됩니다. 패키지에 광범위 파일 접근 권한을 추가하지 않았습니다.
- MSIX의 관리자 권한 새 창 버튼은 비활성화됩니다. 일반 새 창은 실행 파일을 다시 실행합니다. 실행 중 업데이트나 파일 연결 활성화는 실기기 확인이 필요합니다.
- 아카이브 내부 파일 추가·삭제·이름 변경은 임시 작업 폴더에서 내용을 다시 구성해 저장합니다. 큰 아카이브는 작업 시간이 걸릴 수 있으며, 암호화된 ZIP/7Z는 암호를 입력해야 편집할 수 있습니다. 단일 압축 스트림인 GZ는 내부 항목 편집을 지원하지 않습니다. Store 패키지에서의 실제 설치 후 동작은 별도 실기기 검증이 필요합니다.
- 진단: AppxDeployment-Server 이벤트 로그를 확인하고 [MSIX 문제 해결 문서](https://learn.microsoft.com/en-us/windows/msix/msix-troubleshooting-guide)를 참고합니다. 실제 설치, 업데이트 유지, 파일 연결, Store 심사·자동 업데이트는 관련 테스트를 완료하기 전까지 미검증입니다.
