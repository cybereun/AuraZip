"""Offline translations for the AuraZip interface."""
from PySide6.QtCore import QSettings
from distribution import github_updates_enabled
from app_settings import store_settings
import re

EN = {"'ZXPH0XZ' 아카이브의 모든 블록 및 CRC-32 검증을 무결하게 통과했습니다.": "All blocks and CRC-32 verification of the 'ZXPH0XZ' archive "
                                                    'passed flawlessly.',
 'GZ (단일 파일)': 'GZ (single file)',
 'GZ 형식은 일반 파일 하나만 압축할 수 있습니다. 폴더나 여러 파일은 ZIP을 사용하세요.': 'GZ can compress one regular file only. Use ZIP for folders or multiple files.',
 '암호화 미지원 형식': 'Encryption is not supported by this format',
 '이 형식은 암호화를 지원하지 않습니다. ZIP 또는 7Z를 선택하세요.': 'This format does not support encryption. Choose ZIP or 7Z.',
'압축 파일을 압축 대상에 포함할 수 없습니다. 다른 저장 위치를 선택하세요.': 'The archive cannot also be used as an input file. Choose a different output location.',
 'ZIP 암호화 모듈을 사용할 수 없어 암호화된 파일을 만들 수 없습니다.': 'The ZIP encryption module is unavailable, so an encrypted archive cannot be created.',
 '지원하지 않는 아카이브 형식입니다: ZXPH0XZ': 'Unsupported archive format: ZXPH0XZ',
 '아카이브 내부 경로가 올바르지 않습니다.': 'The path inside the archive is invalid.',
 '이 파일 형식은 내부 항목 편집을 지원하지 않습니다.': 'This file format does not support editing internal items.',
 '아카이브를 처리하고 있습니다...': 'Processing the archive...',
 '아카이브에 파일 추가 중...': 'Adding files to the archive...',
 '파일 추가 실패': 'Failed to add files',
 '아카이브 항목 삭제 중...': 'Deleting archive items...',
 '아카이브 항목 이름 변경 중...': 'Renaming archive item...',
 '이름 변경 실패': 'Failed to rename item',
 '클립보드': 'Clipboard',
 '복사 실패': 'Copy failed',
 '클립보드로 복사 중...': 'Copying to the clipboard...',
 '클립보드 파일을 붙여넣는 중...': 'Pasting clipboard files...',
 '붙여넣기 실패': 'Paste failed',
 '이미지 미리보기를 불러오는 중...': 'Loading image preview...',
 '미리보기 실패': 'Preview failed',
 '아카이브 파일을 여는 중...': 'Opening archive item...',
 '아카이브 항목을 처리할 수 없습니다.': 'Could not process the archive item.',
 '지원하는 모든 아카이브 (*.zip *.7z *.tar *.tgz *.tbz2 *.txz *.gz);;ZIP 파일 (*.zip);;7Z 파일 (*.7z);;TAR 파일 (*.tar *.tgz);;모든 파일 (*.*)': 'Supported archives (*.zip *.7z *.tar *.tgz *.tbz2 *.txz *.gz);;ZIP files (*.zip);;7Z files (*.7z);;TAR files (*.tar *.tgz);;All files (*.*)',
 'ZIP 아카이브 (*.zip);;7Z 아카이브 (*.7z);;TAR 아카이브 (*.tar);;TGZ 아카이브 (*.tgz);;GZ 파일 (*.gz);;모든 파일 (*.*)': 'ZIP archives (*.zip);;7Z archives (*.7z);;TAR archives (*.tar);;TGZ archives (*.tgz);;GZ files (*.gz);;All files (*.*)',
 '추가할 파일을 찾을 수 없습니다: ZXPH0XZ': 'Could not find the file to add: ZXPH0XZ',
 '새 이름에는 파일명으로 사용할 수 없는 문자가 있습니다.': 'The new name contains characters that are not allowed in file names.',
 '이름을 바꿀 항목을 찾을 수 없습니다.': 'Could not find the item to rename.',
 '같은 이름의 항목이 이미 있습니다.': 'An item with that name already exists.',
 '이름을 바꿀 아카이브 항목은 하나만 선택해 주세요.': 'Select only one archive item to rename.',
 '선택한 ZXPH0XZ개 항목을 삭제했습니다.': 'Deleted ZXPH0XZ selected archive items.',
 '클립보드에서 파일을 찾을 수 없습니다.': 'No files were found on the clipboard.',
 '클립보드 파일을 아카이브에 붙여넣었습니다.': 'Clipboard files were added to the archive.',
 '클립보드 파일을 임시 폴더에 준비했습니다.': 'Archive files were prepared in a temporary folder for the clipboard.',
 "'ZXPH0XZ' 파일은 아카이브 형식이 아닙니다.\n이 파일을 새로 압축하시겠습니까?": "The file 'ZXPH0XZ' is not in archive format.\n"
                                                     'Would you like to recompress this file?',
 "'ZXPH0XZ'이(가) 'ZXPH1XZ'(으)로 변경되었습니다.": "'ZXPH0XZ' has been changed to 'ZXPH1XZ'.",
 '0% 절약': '0% savings',
 '7Z (초고압축)': '7Z (ultra high compression)',
 '7Z 64비트': '7Z 64bit',
 ': 네트워크 불안정 등으로 헤더가 손상된 아카이브에서 읽을 수 있는 정상 스트림을 최대한 복원합니다.': ': Restore normal, readable streams as much as '
                                                             'possible from archives whose headers have been '
                                                             'damaged due to network instability, etc.',
 ': 설정했던 비밀번호를 잊어버렸을 때, 자릿수와 문자 패턴 힌트를 조합하여 복원을 시도합니다.': ': If you forget your password, try to restore it by '
                                                         'combining the digits and character pattern hint.',
 ': 아카이브 내 각 파일의 CRC-32 체크섬을 전수 대조하여 전송 중 발생한 데이터 손상이나 비트 왜곡을 사전에 정밀 판별합니다.': ': The CRC-32 checksums of each '
                                                                              'file in the archive are compared '
                                                                              'to accurately determine in advance '
                                                                              'any data damage or bit distortion '
                                                                              'that occurred during transmission.',
 ': 압축 파일 내부가 이미 하나의 폴더로 감싸져 있는 경우, 불필요하게 폴더를 이중 생성하지 않고 원래 폴더명으로 깔끔하게 풀어줍니다.': ': If the inside of the '
                                                                                'compressed file is already '
                                                                                'wrapped in a single folder, '
                                                                                'unzip it neatly with the '
                                                                                'original folder name without '
                                                                                'creating double folders '
                                                                                'unnecessarily.',
 ': 압축 파일 내부에 여러 파일이 흩어져 있는 경우, 압축 파일 이름과 동일한 전용 폴더를 자동으로 만들어 그 안에 안전하게 해제합니다.': ': If there are multiple files '
                                                                                 'scattered inside the compressed '
                                                                                 'file, a dedicated folder with '
                                                                                 'the same name as the compressed '
                                                                                 'file is automatically created '
                                                                                 'and safely released within it.',
 ': 압축 파일 내부의 디렉터리 트리, 파일 상세 속성, 실시간 검색 필터, 저장 공간 절감률 통계를 제공합니다.': ': Provides directory tree inside compressed '
                                                                   'file, detailed file properties, real-time '
                                                                   'search filter, and storage space reduction '
                                                                   'rate statistics.',
 ': 원클릭 액션 카드(열기, 새로 압축, 보안 금고 압축)와 드래그&드롭 드롭존을 통해 직관적으로 작업을 시작합니다.': ': Start work intuitively through one-click '
                                                                      'action cards (open, new compression, '
                                                                      'security vault compression) and drag & '
                                                                      'drop drop zone.',
 ': 이중 확장자, 숨겨진 실행 파일(.exe, .bat, .vbs, .cmd) 및 스크립트 위험 요소를 자동 탐지하여 안전성을 안내합니다.': ': Automatically detects double '
                                                                                  'extensions, hidden executable '
                                                                                  'files (.exe, .bat, .vbs, .cmd) '
                                                                                  'and script risks to ensure '
                                                                                  'safety.',
 ': 파일, 편집, 도구 & 보안, 보기, 도움말의 5개 탭으로 모든 고급 기능을 한눈에 조작할 수 있습니다.': ': You can operate all advanced features at a '
                                                                 'glance with five tabs: File, Edit, Tools & '
                                                                 'Security, View, and Help.',
 '<b>새로운 ZXPH0XZ 업데이트가 있습니다!</b>': '<b>There is a new ZXPH0XZ update!</b>',
 '<b>파일명:</b> ZXPH0XZ': '<b>File name:</b> ZXPH0XZ',
 '<b>파일명:</b> ZXPH0XZ<br><b>해상도:</b> ZXPH1XZ × ZXPH2XZ px<br><b>크기:</b> ZXPH3XZ': '<b>File name:</b> '
                                                                                  'ZXPH0XZ<br><b>Resolution:</b> '
                                                                                  'ZXPH1XZ × ZXPH2XZ '
                                                                                  'px<br><b>Size:</b> ZXPH3XZ',
 'A. AuraZip은 표준': 'A. AuraZip is the standard',
 'A. 네, AuraZip은': 'A. Yes, AuraZip',
 'A. 네, 상단 [편집] 탭의 [파일 추가(Ins)], [파일 삭제(Del)], [이름 바꾸기(F2)] 기능을 통해 아카이브 전체를 풀지 않고도 내부 내용을 손쉽게 편집할 수 있습니다.': 'A. '
                                                                                                            'Yes, '
                                                                                                            'you '
                                                                                                            'can '
                                                                                                            'easily '
                                                                                                            'edit '
                                                                                                            'the '
                                                                                                            'internal '
                                                                                                            'contents '
                                                                                                            'without '
                                                                                                            'unpacking '
                                                                                                            'the '
                                                                                                            'entire '
                                                                                                            'archive '
                                                                                                            'through '
                                                                                                            'the '
                                                                                                            '[Add '
                                                                                                            'File '
                                                                                                            '(Ins)], '
                                                                                                            '[Delete '
                                                                                                            'File '
                                                                                                            '(Del)], '
                                                                                                            'and '
                                                                                                            '[Rename '
                                                                                                            '(F2)] '
                                                                                                            'functions '
                                                                                                            'in '
                                                                                                            'the '
                                                                                                            '[Edit] '
                                                                                                            'tab '
                                                                                                            'at '
                                                                                                            'the '
                                                                                                            'top.',
 'AES-256 군사 표준 암호화': 'AES-256 encryption',
 'AES-256 암호화': 'AES-256 encryption',
 'AuraZip 사용자 가이드 및 도움말': 'AuraZip User Guide and Help',
 'AuraZip 시작하기': 'Get started with AuraZip',
 'AuraZip 정보': 'About AuraZip',
 'AuraZip 정보\n(About)': 'About AuraZip\n(About)',
 'AuraZip 종료 (Ctrl+W)': 'Exit AuraZip (Ctrl+W)',
 'AuraZip 준비 완료': 'AuraZip is ready',
 'AuraZip 프로그램 종료': 'AuraZip program termination',
 'AuraZip은 단순 압축을 넘어 아카이브의 안정성과 무결성을 지키는 전문 유틸리티를 기본 탑재하고 있습니다.': 'AuraZip is equipped with a professional '
                                                                  'utility that goes beyond simple compression '
                                                                  'and protects the stability and integrity of '
                                                                  'the archive.',
 'AuraZip은 전 세계 표준 형식부터 초고압축 알고리즘까지 다양한 아카이브 형식을 지원합니다.': 'AuraZip supports a variety of archive formats, from '
                                                          'world standard formats to ultra-high compression '
                                                          'algorithms.',
 'AuraZip은 초고속 멀티포맷 압축 및 군사 표준 보안을 지원하는 차세대 압축 유틸리티입니다.\n\n• 지원 포맷: ZIP, 7Z, TAR, TGZ, TBZ2, TXZ, GZ\n• 보안 규격: AES-256 비트 군사 표준 암호화 지원\n• 핵심 기능: 스마트 폴더 자동 추출, 실시간 검색, 용량 절약 대시보드\n• 저작권: Copyright © 2026 @2026Lebi. All rights reserved.': 'AuraZip '
                                                                                                                                                                                                                                             'is '
                                                                                                                                                                                                                                             'a '
                                                                                                                                                                                                                                             'next-generation '
                                                                                                                                                                                                                                             'compression '
                                                                                                                                                                                                                                             'utility '
                                                                                                                                                                                                                                             'that '
                                                                                                                                                                                                                                             'supports '
                                                                                                                                                                                                                                             'ultra-fast '
                                                                                                                                                                                                                                             'multi-format '
                                                                                                                                                                                                                                             'compression '
                                                                                                                                                                                                                                             'and '
                                                                                                                                                                                                                                             'military-standard '
                                                                                                                                                                                                                                             'security.\n'
                                                                                                                                                                                                                                             '\n'
                                                                                                                                                                                                                                             '• '
                                                                                                                                                                                                                                             'Supported '
                                                                                                                                                                                                                                             'formats: '
                                                                                                                                                                                                                                             'ZIP, '
                                                                                                                                                                                                                                             '7Z, '
                                                                                                                                                                                                                                             'TAR, '
                                                                                                                                                                                                                                             'TGZ, '
                                                                                                                                                                                                                                             'TBZ2, '
                                                                                                                                                                                                                                             'TXZ, '
                                                                                                                                                                                                                                             'GZ\n'
                                                                                                                                                                                                                                             '• '
                                                                                                                                                                                                                                             'Security '
                                                                                                                                                                                                                                             'standard: '
                                                                                                                                                                                                                                             'Supports '
                                                                                                                                                                                                                                             'AES-256 '
                                                                                                                                                                                                                                             'bit '
                                                                                                                                                                                                                                             'military '
                                                                                                                                                                                                                                             'standard '
                                                                                                                                                                                                                                             'encryption\n'
                                                                                                                                                                                                                                             '• '
                                                                                                                                                                                                                                             'Core '
                                                                                                                                                                                                                                             'features: '
                                                                                                                                                                                                                                             'Smart '
                                                                                                                                                                                                                                             'folder '
                                                                                                                                                                                                                                             'auto-extraction, '
                                                                                                                                                                                                                                             'real-time '
                                                                                                                                                                                                                                             'search, '
                                                                                                                                                                                                                                             'capacity-saving '
                                                                                                                                                                                                                                             'dashboard\n'
                                                                                                                                                                                                                                             '• '
                                                                                                                                                                                                                                             'Copyright: '
                                                                                                                                                                                                                                             'Copyright '
                                                                                                                                                                                                                                             '© '
                                                                                                                                                                                                                                             '2026 '
                                                                                                                                                                                                                                             '@2026Lebi. '
                                                                                                                                                                                                                                             'All '
                                                                                                                                                                                                                                             'rights '
                                                                                                                                                                                                                                             'reserved.',
 'AuraZip의': 'AuraZip',
 'Linux/Unix 개발 환경 표준 배포 아카이브': 'Linux/Unix development environment standard distribution archive',
 'Q. 4GB 이상의 대용량 파일도 압축할 수 있나요?': 'Q. Can I compress large files larger than 4GB?',
 'Q. 다른 OS(Mac, Linux)에서 압축한 파일명이 깨지지 않나요?': 'Q. Are compressed file names broken on other OSs (Mac, Linux)?',
 'Q. 압축 파일 내의 개별 파일만 추가하거나 삭제할 수 있나요?': 'Q. Can I only add or delete individual files within a compressed file?',
 'TAR (단순 보관)': 'TAR (simple archive)',
 'UTF-8 유니코드 인코딩': 'UTF-8 Unicode encoding',
 'Windows 설정의 [기본 앱] 화면을 열어 AuraZip을 기본 압축 파일(ZIP, 7Z 등) 프로그램으로 지정할 수 있습니다.\n\n지금 Windows 기본 앱 설정 창을 여시겠습니까?': 'You '
                                                                                                               'can '
                                                                                                               'set '
                                                                                                               'AuraZip '
                                                                                                               'as '
                                                                                                               'the '
                                                                                                               'default '
                                                                                                               'compressed '
                                                                                                               'file '
                                                                                                               '(ZIP, '
                                                                                                               '7Z, '
                                                                                                               'etc.) '
                                                                                                               'program '
                                                                                                               'by '
                                                                                                               'opening '
                                                                                                               'the '
                                                                                                               '[Default '
                                                                                                               'apps] '
                                                                                                               'screen '
                                                                                                               'in '
                                                                                                               'Windows '
                                                                                                               'Settings.\n'
                                                                                                               '\n'
                                                                                                               'Would '
                                                                                                               'you '
                                                                                                               'like '
                                                                                                               'to '
                                                                                                               'open '
                                                                                                               'the '
                                                                                                               'Windows '
                                                                                                               'default '
                                                                                                               'app '
                                                                                                               'settings '
                                                                                                               'window '
                                                                                                               'now?',
 'ZIP (범용 호환)': 'ZIP (universal compatible)',
 'ZXPH0XZ 소프트웨어 업데이트': 'ZXPH0XZ Software Update',
 'ZXPH0XZ% 용량 절약': 'ZXPH0XZ% capacity savings',
 'ZXPH0XZ개 파일 정보가 클립보드에 복사되었습니다.': 'ZXPH0XZ file information has been copied to the clipboard.',
 'ZXPH0XZ개 항목 선택됨': 'ZXPH0XZ items selected',
 '⌨️ 키보드 단축키 안내': '⌨️ Keyboard shortcut information',
 '▲ 상위 폴더': '▲ Parent folder',
 '◀ 뒤로': '◀ Back',
 '⚖️ 밸런스 추천 (Level 5)': '⚖️ Balance Recommendation (Level 5)',
 '⚡ AuraZip 시작하기': '⚡ Get started with AuraZip',
 '⚡ 새로운 아카이브 패키징': '⚡ New archive packaging',
 '✅ 검사 통과: 안전함\n\nZXPH0XZ': '✅ Passed inspection: Safe\n\nZXPH0XZ',
 '❌ 후보군 중에서 일치하는 암호를 찾지 못했습니다.': '❌ No matching password was found among the candidates.',
 '❓ 자주 묻는 질문 (FAQ)': '❓ Frequently Asked Questions (FAQ)',
 '가 적용되어 외부 유출이나 해킹으로부터 민감한 데이터를 완벽하게 보호합니다.': 'is applied to completely protect sensitive data from external '
                                               'leaks or hacking.',
 '검사 대상: ZXPH0XZ\n보안 위협 시그니처 및 악성 스크립트 실행 패턴을 분석합니다.': 'Checked for: ZXPH0XZ\n'
                                                       'Analyzes security threat signatures and malicious script '
                                                       'execution patterns.',
 '검사 중 손상 또는 오류가 발견되었습니다:\nZXPH0XZ': 'Damage or errors were found during testing:\nZXPH0XZ',
 '검색할 아카이브 열기': 'Open an archive to search',
 '결과': 'result',
 '경로 내비게이션 (F7)': 'Route navigation (F7)',
 '관리자 권한 실행 실패': 'Failed to run administrator privileges',
 '극대화된 압축률 제공 (대용량 데이터 백업에 최적)': 'Provides maximized compression ratio (optimal for large data backup)',
 '기능': 'function',
 '기능은 바탕화면이나 폴더가 어지럽혀지는 것을 원천 방지합니다.': 'This function prevents your desktop or folders from becoming cluttered.',
 '기본 압축 프로그램 설정': 'Set default compression program',
 '기본 앱 설정\n(Default)': 'Default app settings\n(Default)',
 '기본 작업': 'Basic actions',
 '기존 아카이브 탐색 및 풀기': 'Browse and extract archives',
 '기존 압축 파일 열기': 'Open an existing compressed file',
 '나중에': 'later',
 '내부 경로명이 클립보드에 복사되었습니다.': 'The internal pathname has been copied to the clipboard.',
 '내용을 열람하거나 압축을 풀려면 암호를 입력하세요:': 'Enter your password to view or unzip the contents:',
 '다른 이름으로 아카이브 저장': 'Save archive as',
 '다른 이름으로 저장...': 'Save As...',
 '다른 이름으로 저장되었습니다:\nZXPH0XZ': 'Saved as:\nZXPH0XZ',
 '다른 이름으로 저장할 아카이브 선택': 'Select archive to save as',
 '다운로드 실패': 'Download failed',
 '다운로드 완료! 설치 프로그램을 시작하고 AuraZip을 재시작합니다...': 'Download complete! Start the installer and restart AuraZip...',
 '다운로드 중...': 'Downloading...',
 '다운로드 중: ZXPH0XZ MB': 'Downloading: ZXPH0XZ MB',
 '다운로드 중: ZXPH0XZ MB / ZXPH1XZ MB (ZXPH2XZ%)': 'Downloading: ZXPH0XZ MB / ZXPH1XZ MB (ZXPH2XZ%)',
 '다중 파일 아카이브': 'Multi-file archive',
 '단일 폴더 아카이브': 'Single folder archive',
 '단축키': 'shortcut key',
 '단축키 전체 안내': 'Full guide to shortcut keys',
 '닫기': 'Close',
 '닫기\n(F4)': 'Close\n(F4)',
 '대기 중...': 'Waiting...',
 "대상 압축 파일:\n'ZXPH0XZ'\n\n이 파일을 ZXPH1XZ하시겠습니까?": 'Target compressed file:\n'
                                                 "'ZXPH0XZ'\n"
                                                 '\n'
                                                 'Do you want to ZXPH1XZ this file?',
 '대상 파일: ZXPH0XZ\n손상되거나 불완전한 헤더를 검사하여 온전한 데이터 스트림을 구조화된 새 아카이브로 복구합니다.': 'Target file: ZXPH0XZ\n'
                                                                         'It scans for corrupted or incomplete '
                                                                         'headers and recovers intact data '
                                                                         'streams into a new, structured archive.',
 '더블 클릭': 'double click',
 '도구 & 보안': 'Tools & Security',
 '도움말': 'Help',
 '릴리즈: ZXPH0XZ': 'Release: ZXPH0XZ',
 '모두 선택 (Ctrl+A)': 'Select All (Ctrl+A)',
 '목록에서 이미지를\n클릭하면 즉시 표시됩니다.': 'select an image from the list\nClick on it and it will appear immediately.',
 '무결성 검사\n(Ctrl+T)': 'integrity check\n(Ctrl+T)',
 '무결성 검사 (Ctrl+T)': 'Integrity Check (Ctrl+T)',
 '무결성 검사 실패': 'Integrity check failed',
 '무결성 검사 완료': 'Integrity check completed',
 '무결성 검사(CRC-32) 실행 중...': 'Running integrity check (CRC-32)...',
 '무결성을 검사할 아카이브 선택': 'Select an archive to check integrity',
 '미리보기를 불러올 수 없습니다.': 'Preview cannot be loaded.',
 '미설정 시 암호 없음': 'No password if not set',
 '버전 2.5.0 LTS | 내장 가이드': 'Version 2.5.0 LTS | built-in guide',
 '버전 ZXPH0XZ (Aura Next-Gen Core)': 'Version ZXPH0XZ (Aura Next-Gen Core)',
 '보기': 'View',
 '보기 옵션': 'View Options',
 '보안': 'security',
 '보안 & 검사': 'Security & Inspection',
 '보안 & 검사 도구': 'Security & Scan Tools',
 '보안 강화': 'Increased security',
 '보안 검사 결과': 'Security check results',
 '보안 검사 실행': 'Run security check',
 '보안 금고 압축': 'Secure archive',
 '보안 금고 압축 시 미국 연방 표준': 'US Federal Standards for Compressing Secure Vaults',
 '보안 암호 (AES-256):': 'Secure Cipher (AES-256):',
 '보안 암호화를 탑재한 차세대 고성능 압축 유틸리티입니다.': 'A next-generation, high-performance compression utility with secure '
                                    'encryption.',
 '복구 도구': 'recovery tool',
 '복구 시작': 'Start recovery',
 '복구 오류': 'recovery error',
 '복구 완료': 'Recovery complete',
 '복구 중 오류가 발생했습니다: ZXPH0XZ': 'An error occurred during recovery: ZXPH0XZ',
 '복구할 손상된 아카이브 선택': 'Select corrupted archive to recover',
 '붙여넣기': 'paste',
 '비밀번호 입력': 'Enter password',
 '빠르고 안전한 차세대 고성능 압축 유틸리티': 'A fast and secure archive utility',
 '빠른 압축': 'fast compression',
 '사용자 가이드\n(도움말)': 'user guide\n(Help)',
 '사용자 가이드 및 도움말 열기': 'Open User Guide and Help',
 '삭제 오류': 'delete error',
 '삭제 완료': 'Deletion complete',
 '삭제 확인': 'Confirm deletion',
 '삭제할 아카이브 파일 선택': 'Select archive files to delete',
 '삭제할 항목을 선택해 주세요.': 'Please select the item you want to delete.',
 '상태 표시줄 표시': 'Show status bar',
 '새 아카이브 압축 - AuraZip': 'New archive compression - AuraZip',
 '새 아카이브 압축 중...': 'Compressing new archive...',
 '새 창 (관리자 권한)': 'New window (Administrator privileges)',
 '새 창 띄우기 (Ctrl+Shift+N)': 'Open a new window (Ctrl+Shift+N)',
 '새로 압축\n(Ctrl+N)': 'Create archive\n(Ctrl+N)',
 '새로 압축 대화상자 실행': 'Launch the New Compress dialog box',
 '새로운 파일명을 입력하세요:': 'Enter a new file name:',
 '색상 / 테마\n설정': 'Color/Theme\nsettings',
 '색상 및 테마 설정 - AuraZip': 'Color and Theme Settings - AuraZip',
 '생성할 압축 파일 위치': 'Location of compressed file to be created',
 '선택 반전': 'Invert selection',
 '선택 삭제': 'Remove selected',
 '선택 항목이 아카이브 목록에서 제외되었습니다.': 'The selection has been excluded from the archive list.',
 '선택된 ZXPH0XZ개 파일이 아카이브에 성공적으로 추가되었습니다.': 'The selected ZXPH0XZ files have been successfully added to the '
                                          'archive.',
 '선택한 ZXPH0XZ개 항목을 아카이브에서 삭제하시겠습니까?': 'Are you sure you want to delete the selected ZXPH0XZ items from the '
                                      'archive?',
 '선택한 항목은\n이미지 파일이 아닙니다.': 'The selected item is\nIt is not an image file.',
 '선택한 항목은\n폴더입니다.': "The selected item is\nIt's a folder.",
 '설명 편집\n(주석)': 'Edit comment',
 '설정 창을 열지 못했습니다: ZXPH0XZ': 'Failed to open settings window: ZXPH0XZ',
 '설치 폴더 열기\n(Explorer)': 'Open the installation folder\n(Explorer)',
 '설치 프로그램 실행 중 오류가 발생했습니다:\nZXPH0XZ': 'An error occurred while running the installer:\nZXPH0XZ',
 '손상 파일 복구\n(Repair)': 'Corrupt File Recovery\n(Repair)',
 '손상 파일 복구 (Repair)': 'Repair damaged files',
 '손상된 압축 파일 복구 - AuraZip': 'Repair Corrupted Compressed Files - AuraZip',
 '수정한 날짜': 'Date modified',
 '쉼표(,)로 구분된 비밀번호 후보들': 'Password candidates separated by commas (,)',
 '스마트 새로 압축': 'Create archive',
 '스마트 압축 풀기': 'Smart Unzip',
 '스마트 압축 풀기 - AuraZip': 'Smart Unzip - AuraZip',
 '스마트 압축 풀기(Smart Extract)': 'Smart Extract',
 '스마트 추출 옵션': 'Smart extraction options',
 '스마트 풀기 (최상위 파일이 여러 개면 아카이브 폴더 생성 후 풀기)': 'Smart unpack (if there are multiple top-level files, unpack after '
                                           'creating an archive folder)',
 '시작 대시보드 (Start View)': 'Start Dashboard (Start View)',
 '시작 화면 (F6)': 'Start screen (F6)',
 '시작 화면 토글': 'Start screen toggle',
 '실행 오류': 'execution error',
 '아카이브 관리': 'Archive Management',
 '아카이브 내부 파일 검색': 'Search for files inside archives',
 '아카이브 무결성 검사 실행': 'Run archive integrity check',
 '아카이브 압축이 성공적으로 완료되었습니다:\nZXPH0XZ': 'Archive compression completed successfully:\nZXPH0XZ',
 '아카이브 열기': 'Open archive',
 '아카이브 열기 실패': 'Failed to open archive',
 '아카이브 저장 위치': 'Archive storage location',
 '아카이브 탐색기 (Archive View)': 'Archive View',
 '아카이브 파일을 열람하거나 새로 압축할 파일을 추가하세요.': 'Browse archive files or add new files to compress.',
 '아카이브를 열 수 없습니다:\nZXPH0XZ': 'Unable to open archive:\nZXPH0XZ',
 '아카이브에 추가할 파일 선택': 'Select files to add to archive',
 '아키텍처를 지원하므로 테라바이트(TB) 단위의 대용량 파일도 문제없이 압축 및 해제할 수 있습니다.': 'architecture, you can compress and decompress even '
                                                            'large files in the terabyte (TB) unit without any '
                                                            'problems.',
 '악성코드 검사\n(Ctrl+I)': 'Malware scan\n(Ctrl+I)',
 '악성코드 검사 (Ctrl+I)': 'Malicious code scan (Ctrl+I)',
 '악성코드 의심 파일 검사': 'Scan suspicious files for malicious code',
 '악성코드를 검사할 아카이브 선택': 'Select archives to scan for malware',
 '안내': 'Information',
 '알고리즘': 'algorithm',
 '알림': 'Notice',
 '암호 문자 표시': 'Show password characters',
 '암호 발견': 'password discovery',
 '암호 복구\n(Password)': 'Recover password',
 '암호 복구 마법사 (Password)': 'Password Recovery Wizard (Password)',
 '암호 탐색 시작': 'Start exploring passwords',
 '암호를 복구할 아카이브 선택': 'Select the archive from which you want to recover the password',
 '압축 대상 파일 및 폴더': 'Compressed files and folders',
 '압축 및 보안 암호화': 'Compression and secure encryption',
 '압축 실패': 'Compression failed',
 '압축 실행': 'compressed execution',
 '압축 없이 파일들을 그대로 묶어 신속 보관': 'Quick storage of files by bundling them without compression',
 '압축 작업 중 오류가 발생했습니다:\nZXPH0XZ': 'An error occurred during the compression operation:\nZXPH0XZ',
 '압축 크기': 'compressed size',
 '압축 파일 ZXPH0XZ': 'Compressed file ZXPH0XZ',
 '압축 파일 삭제 (Ctrl+Del)': 'Delete compressed file (Ctrl+Del)',
 '압축 파일 설명(주석) 편집 - AuraZip': 'Edit compressed file description (comment) - AuraZip',
 '압축 파일 아님': 'Not a compressed file',
 '압축 파일 악성코드 및 보안 검사 - AuraZip': 'Compressed file malware and security scanning - AuraZip',
 '압축 파일 암호 복구 - AuraZip': 'Compressed File Password Recovery - AuraZip',
 '압축 파일 열기': 'Open compressed file',
 '압축 파일 완전 삭제 (Shift+Ctrl+Del)': 'Completely delete compressed files (Shift+Ctrl+Del)',
 '압축 파일에 포함할 설명이나 코멘트를 입력하세요...': 'Please enter any description or comments you would like to include in the '
                                  'compressed file...',
 '압축 파일을 여기에 드래그하여 바로 열기': 'Drag compressed files here to open them right away',
 '압축 파일이 ZXPH0XZ되었습니다.': 'The compressed file has become ZXPH0XZ.',
 '압축 푸는 중...': 'Unzipping...',
 '압축 풀기\n(Ctrl+E)': 'Extract\n(Ctrl+E)',
 '압축 풀기 실패': 'Decompression failed',
 '압축 프로필:': 'Compression Profile:',
 '압축 프리셋 및 보안': 'Compression Presets and Security',
 '압축 해제 대상 경로': 'Unzip destination path',
 '압축 해제 시작': 'Start decompressing',
 '압축 해제 중 오류 발생:\nZXPH0XZ': 'Error occurred during decompression:\nZXPH0XZ',
 '압축 해제 폴더 선택': 'Select unzipped folder',
 '압축 해제가 완료되었습니다:\nZXPH0XZ': 'Decompression is complete:\nZXPH0XZ',
 '압축률': 'compressibility',
 '압축으로 절약된 용량 비율': 'Percentage of space saved by compression',
 '압축을 전체 해제하지 않고도, 내부 목록에서 파일을': 'Files can be selected from the internal list without having to completely '
                                 'decompress them.',
 '압축을 풀 아카이브 선택': 'Select the archive to extract',
 '압축하고 싶은 파일이나 폴더를 AuraZip 창으로 언제든 드래그하면 즉시 압축 또는 열기가 실행됩니다.': 'Any time you drag the file or folder you want to '
                                                               'compress into the AuraZip window, it will '
                                                               'compress or open it immediately.',
 '압축할 파일 또는 폴더를 하나 이상 추가해 주세요.': 'Please add one or more files or folders to compress.',
 '업데이트 설치 파일을 다운로드하고 있습니다...': 'Downloading update installation files...',
 '업데이트 안내': 'Update information',
 '업데이트 정보를 확인하는 중 네트워크 오류가 발생했습니다:\nZXPH0XZ': 'A network error occurred while checking update information:\n'
                                              'ZXPH0XZ',
 '업데이트 주요 변경 사항:': 'Major changes in the update:',
 '업데이트 확인': 'Check for updates',
 '업데이트 확인\n(Update)': 'Check for updates\n(Update)',
 '업데이트 확인 실패': 'Update check failed',
 '열기\n(Ctrl+O)': 'Open\n(Ctrl+O)',
 '열기 실패': 'Open failed',
 '열려 있는 아카이브가 없습니다.': 'There are no archives open.',
 '열려 있는 아카이브가 없습니다.\n새로운 아카이브를 생성하여 파일을 추가하시겠습니까?': 'There are no archives open.\n'
                                                    'Would you like to create a new archive and add files to it?',
 '열려 있는 압축 파일이 없습니다.\n먼저 상단 [열기 (Ctrl+O)]로 압축 파일을 열어주세요.': 'There are no compressed files open.\n'
                                                           'First, open the compressed file using [Open (Ctrl+O)] '
                                                           'at the top.',
 '열린 아카이브 없음 (Ctrl+O로 열기)': 'No archives open (open with Ctrl+O)',
 '오류': 'Error',
 '오피스 스타일 리본 메뉴': 'Office Style Ribbon Menu',
 '올바른 암호를 찾았습니다!\n\n암호: ZXPH0XZ': 'You found the correct password!\n\nPassword: ZXPH0XZ',
 '완료': 'Completed',
 '완료 후 대상 폴더 열기': 'Open the destination folder after completion',
 '원본 크기': 'original size',
 '원본: ZXPH0XZ | 압축: ZXPH1XZ (ZXPH2XZ% 절약) | 형식: ZXPH3XZ': 'Original: ZXPH0XZ | Compression: ZXPH1XZ (ZXPH2XZ% '
                                                          'savings) | Format: ZXPH3XZ',
 '은 초고속 다중 포맷 압축 엔진과 군사 표준': 'Ultra-fast multi-format compression engine and military standard',
 '을 기본 탑재하여, macOS, Linux, Windows 간 교환 시에도 한글 및 다국어 파일명이 깨지지 않습니다.': 'Equipped as standard, Korean and '
                                                                      'multilingual file names are not broken '
                                                                      'even when exchanged between macOS, Linux, '
                                                                      'and Windows.',
 '이름': 'name',
 '이름 바꾸기': 'rename',
 '이름 바꾸기\n(F2)': 'rename\n(F2)',
 '이름을 바꿀 항목을 선택해 주세요.': 'Please select the item you want to rename.',
 '이미 열려 있는 아카이브가 없습니다.': 'There are no archives already open.',
 '이미지 미리보기 사용': 'Use image preview',
 '자주 묻는 질문 (FAQ)': 'Frequently Asked Questions (FAQ)',
 '자주 사용하는 비밀번호 후보군(사전) 또는 힌트를 입력하여 유효한 암호를 탐색합니다:': 'Search for valid passwords by entering a dictionary of '
                                                    'frequent password candidates or a hint:',
 '작업 취소': 'Cancel operation',
 '작업을 중단하는 중입니다...': 'Aborting work...',
 '재시도': 'retry',
 '저장': 'save',
 '저장 실패': 'save failed',
 '저장 완료': 'Save completed',
 '저장 위치...': 'Save to...',
 '저장할 압축 파일 위치를 지정해 주세요.': 'Please specify the location of the compressed file to be saved.',
 '적용': 'Apply',
 '전 세계 모든 기기 및 OS 호환 (4GB 초과 대용량 파일 완벽 지원)': 'Compatible with all devices and OSs around the world (fully '
                                             'supports large files exceeding 4GB)',
 '정상 스트림 ZXPH0XZ개 항목을 복구하여 저장했습니다:\nZXPH1XZ': 'Normal Stream ZXPH0XZ items were recovered and saved:\nZXPH1XZ',
 '제공된 후보군 목록에서 유효한 암호가 발견되지 않았습니다.': 'No valid password was found in the provided candidate list.',
 '제작자: @2026Lebi': 'Created by: @2026Lebi',
 '종류': 'type',
 '주석 & 선택': 'Annotation & Selection',
 '주석 저장 실패: ZXPH0XZ': 'Failed to save comment: ZXPH0XZ',
 '주석이 성공적으로 저장되었습니다.': 'Your comment has been saved successfully.',
 '지금 업데이트 및 재시작': 'Update and restart now',
 '지원되지 않는 이미지 포맷입니다.': 'Unsupported image format.',
 '지정된 파일을 찾을 수 없습니다:\nZXPH0XZ': 'The specified file cannot be found:\nZXPH0XZ',
 '직접 다운로드할 수 있는 설치 파일이 없습니다. 릴리즈 페이지를 확인해주세요.': 'There are no installation files available for direct download. '
                                                'Please check the releases page.',
 '진행 중: ZXPH0XZ / ZXPH1XZ (ZXPH2XZ%)': 'In Progress: ZXPH0XZ / ZXPH1XZ (ZXPH2XZ%)',
 '창 및 세션': 'windows and sessions',
 '처리 대기 중...': 'Waiting for processing...',
 '처리 중...': 'Processing...',
 '최근 기록': 'Recent records',
 '최근 작업한 아카이브': 'Recent archives',
 '최근 파일\n목록': 'Recent\nfiles',
 '취소': 'Cancel',
 '클립보드': 'Clipboard',
 '클립보드 데이터로부터 항목을 가져왔습니다:\nZXPH0XZ': 'Items were retrieved from clipboard data:\nZXPH0XZ',
 '클립보드로 복사 (Ctrl+C)': 'Copy to clipboard (Ctrl+C)',
 '클립보드에 복사된 파일 또는 텍스트가 없습니다.': 'No files or text were copied to the clipboard.',
 '클립보드에서 붙여넣기 (Ctrl+V)': 'Paste from clipboard (Ctrl+V)',
 '키보드 단축키를 활용하여 모든 압축 작업을 빠르고 능숙하게 제어할 수 있습니다.': 'Take advantage of keyboard shortcuts to quickly and masterfully '
                                                 'control all compression operations.',
 '탐색 & 시스템': 'Navigation & System',
 '테마 설정': 'Theme',
 '테스트할 비밀번호 후보를 하나 이상 입력해 주세요.': 'Please enter at least one password candidate to test.',
 '특징 및 권장 용도': 'Features and Recommended Use',
 '파일 / 홈': 'File / Home',
 '파일 ZXPH0XZ개  |  원본 ZXPH1XZ -> 압축 ZXPH2XZ': 'ZXPH0XZ files |  Original ZXPH1XZ -> Compressed ZXPH2XZ',
 '파일 ZXPH0XZ개, 폴더 ZXPH1XZ개': 'ZXPH0XZ files, ZXPH1XZ folders',
 '파일 경로명 복사': 'Copy file path name',
 '파일 삭제\n(Del)': 'Delete file\n(Del)',
 '파일 선택': 'Select file',
 '파일 설명창 (F8)': 'File description window (F8)',
 '파일 위치 폴더 열기': 'Open file location folder',
 '파일 위치를 열 아카이브 선택': 'Select archive to open file location',
 '파일 조작': 'File actions',
 '파일 찾기\n(Ctrl+F)': 'Find files\n(Ctrl+F)',
 '파일 추가': 'Add file',
 '파일 추가\n(Ins)': 'Add file\n(ins)',
 '파일/폴더를 최적 압축률로': 'Compress files and folders',
 '파일을 삭제할 수 없습니다:\nZXPH0XZ': 'Cannot delete files:\nZXPH0XZ',
 '파일을 열 수 없습니다:\nZXPH0XZ': "Can't open file:\nZXPH0XZ",
 '편집': 'Edit',
 '편집할 아카이브 열기': 'Open archive for editing',
 '포맷': 'Format',
 '포맷:': 'Format:',
 '폴더 선택': 'Select folder',
 '폴더 선택...': 'Select folder...',
 '프로그램 안내': 'Program Information',
 '하면 시스템 임시 격리 영역에서 해당 파일을 즉시 열람할 수 있습니다.': "This will allow you to view the file immediately from the system's "
                                            'temporary quarantine area.',
 '항상 위에 표시': 'Always on top',
 '항상 위에 표시가 ZXPH0XZ되었습니다.': 'It was always marked ZXPH0XZ on top.',
 "현재 버전: <span style='color:#64748B;'>ZXPH0XZ</span>  ➔  최신 버전: <b style='color:#4F46E5;'>ZXPH1XZ</b>": 'Current '
                                                                                                        'version: '
                                                                                                        '<span '
                                                                                                        "style='color:#64748B;'>ZXPH0XZ</span> "
                                                                                                        '➔ Latest '
                                                                                                        'version: '
                                                                                                        '<b '
                                                                                                        "style='color:#4F46E5;'>ZXPH1XZ</b>",
 '현재 아카이브 닫기 (시작화면 전환)': 'Close current archive (switch start screen)',
 '현재 아카이브 압축 풀기': 'Unzip the current archive',
 '현재 최신 버전(ZXPH0XZ)을 사용하고 있습니다.\n새로운 업데이트가 없습니다.': 'I am currently using the latest version (ZXPH0XZ).\n'
                                                   'There are no new updates.',
 '현재 포맷에서는 주석 저장을 지원하지 않거나 읽기 전용입니다.': 'The current format does not support saving comments or is read-only.',
 '화면 표시': 'Display',
 '확인': 'OK',
 '확장 규격과': 'Extended specifications and',
 '🎉 암호 발견 성공: ZXPH0XZ': '🎉 Password found successfully: ZXPH0XZ',
 '🎨 테마 프리셋 선택': '🎨Choose theme preset',
 '💎 울트라 압축 (Level 9)': '💎 Ultra Compression (Level 9)',
 '💡 스마트 추출 작동 원리': '💡 How Smart Extraction Works',
 '💡 팁:': '💡 Tips:',
 '📁 폴더 추가...': '📁 Add folder...',
 '📂 스마트 압축 풀기 가이드': '📂 Smart Unzip Guide',
 '📂 열려 있는 아카이브가 없습니다. 상단 [열기 (Ctrl+O)]를 클릭하세요.': '📂 There are no archives open. Click [Open (Ctrl+O)] at the top.',
 "📄 'ZXPH0XZ' 주석/설명:": "📄 'ZXPH0XZ' Comments/Description:",
 '📄 파일 추가...': '📄Add files...',
 '📖 AuraZip 통합 도움말 센터': '📖 AuraZip Integrated Help Center',
 '📦 ZXPH0XZ 압축 풀기': '📦 Unzip ZXPH0XZ',
 '📦 무압축 저장 (Level 0)': '📦 Uncompressed storage (Level 0)',
 '📦 선택 항목 풀기...': '📦 Unpack selection...',
 '📦 파일 압축 및 보안 설정': '📦 File compression and security settings',
 "🔍 'ZXPH0XZ' 검색 결과가 없습니다.": "🔍 There are no search results for 'ZXPH0XZ'.",
 '🔍 개별 파일 인라인 뷰어': '🔍 Individual file inline viewer',
 '🔍 파일명 즉시 검색...': '🔍 Instant file name search...',
 '🔑 아카이브 암호 복구 / 힌트 마법사': '🔑 Archive Password Recovery/Hint Wizard',
 '🔒 암호화된 아카이브': '🔒 Encrypted archives',
 '🖥️ 핵심 작업 화면 구성': '🖥️ Core task screen composition',
 '🖼️ 이미지 미리보기': '🖼️ Image preview',
 '🚀 초고속 백업 (Level 1)': '🚀 Ultra-fast backup (Level 1)',
 '🛠️ 손상된 아카이브 복구 마법사': '🛠️ Corrupted Archive Recovery Wizard',
 '🛡️ Windows Defender & 무결성 보안 분석': '🛡️ Windows Defender & Integrity Security Analysis',
 '🛡️ 강력한 AES-256 군사 규격 보안': '🛡️Strong AES-256 military-spec security',
 '🛡️ 전문 보안 & 검사 도구': '🛡️ Professional security & scanning tools'}

EN.update({
    '이 버전은 Microsoft Store에서 업데이트합니다. Microsoft Store의 라이브러리에서 업데이트를 확인하세요.': 'This version is updated through Microsoft Store. Check for updates in the Microsoft Store library.',
    '배포판 정보를 확인할 수 없어 자동 업데이트를 사용할 수 없습니다.': 'Updates are unavailable because the distribution channel could not be verified.',
    '언어 / Language': 'Language',
    '압축 실행': 'Create archive',
    '생성할 압축 파일 위치': 'Archive destination',
    '압축 대상 파일 및 폴더': 'Files and folders to compress',
    '보안 암호 (AES-256):': 'Password (AES-256):',
    '미설정 시 암호 없음': 'Optional password',
    '새 아카이브 압축 - AuraZip': 'Create archive - AuraZip',
    '⚡ 새로운 아카이브 패키징': '⚡ Create a new archive',
    '⚖️ 밸런스 추천 (Level 5)': '⚖️ Balanced (Level 5)',
    '압축 파일이 ZXPH0XZ되었습니다.': 'Archive operation completed: ZXPH0XZ.',
    '항상 위에 표시가 ZXPH0XZ되었습니다.': 'Always on top: ZXPH0XZ.',
    '보안 암호 입력': 'Enter password', '작업 진행 중': 'Operation in progress',
    '완전 영구 삭제': 'permanently delete', '삭제': 'delete',
    '해제': 'disabled', '설정': 'enabled', '폴더': 'Folder', '파일': 'File',
    '이미지 미리보기 패널이 표시됩니다.': 'Image preview is shown.',
    '이미지 미리보기 패널이 숨겨졌습니다.': 'Image preview is hidden.',
    '알려진 바이러스나 위험한 익스플로잇 패턴이 감지되지 않았습니다.': 'No known viruses or dangerous exploit patterns were detected.',
    'Windows Defender 실시간 서명 검사 통과 (위협 없음)': 'Windows Defender scan passed (no threats found).',
    '검사 완료: 정상': 'Scan completed.',
    '자체 시그니처 분석 완료 (위협 요소 없음)': 'Local signature analysis completed (no threats found).',
    '사용자가 압축 해제를 취소했습니다.': 'Extraction was cancelled.',
    '사용자가 압축을 취소했습니다.': 'Compression was cancelled.',
    '7Z 아카이브 무결성 검사 실패': '7Z archive integrity check failed.',
    '무결성 검사 완료': 'Integrity check complete',
    '암호 입력 - ZXPH0XZ': 'Enter password - ZXPH0XZ',
    '손상된 파일 발견: ZXPH0XZ': 'Corrupted file found: ZXPH0XZ',
    '서버 응답 오류 (HTTP ZXPH0XZ)': 'Server error (HTTP ZXPH0XZ)',
    '다운로드 실패: ZXPH0XZ': 'Download failed: ZXPH0XZ',
    '다운로드가 취소되었습니다.': 'Download cancelled.',
    '새로운 버전이 출시되었습니다.': 'A new version is available.',
    '세부 릴리즈 노트가 없습니다.': 'No release notes are available.',
    'Aura Indigo (기본 시그니처)': 'Aura Indigo (default)',
    'Dark Slate (다크 슬레이트 모드)': 'Dark Slate',
    'Emerald Mint (에메랄드 민트)': 'Emerald Mint',
    'Sunset Coral (선셋 코랄 모드)': 'Sunset Coral',
    '지원하는 모든 아카이브 (*.zip *.7z *.tar *.tgz *.tbz2 *.txz);;ZIP 파일 (*.zip);;7Z 파일 (*.7z);;TAR 파일 (*.tar *.tgz);;모든 파일 (*.*)': 'Supported archives (*.zip *.7z *.tar *.tgz *.tbz2 *.txz);;ZIP files (*.zip);;7Z files (*.7z);;TAR files (*.tar *.tgz);;All files (*.*)',
    '지원하는 모든 아카이브 (*.zip *.7z *.tar *.tgz *.gz *.tbz2 *.txz);;모든 파일 (*.*)': 'Supported archives (*.zip *.7z *.tar *.tgz *.gz *.tbz2 *.txz);;All files (*.*)',
    'ZIP 아카이브 (*.zip);;7Z 아카이브 (*.7z);;TAR 아카이브 (*.tar);;TGZ 아카이브 (*.tgz);;모든 파일 (*.*)': 'ZIP archives (*.zip);;7Z archives (*.7z);;TAR archives (*.tar);;TGZ archives (*.tgz);;All files (*.*)',
    '검사할 파일을 찾을 수 없습니다.': 'The file to scan could not be found.',
    'Defender로 아카이브 파일을 검사합니다. 검사 결과는 안전을 보증하지 않습니다.': 'Defender will scan the archive file. A scan result does not guarantee safety.',
    '🛡️ Windows Defender 파일 검사': '🛡️ Windows Defender file scan',
    'Windows Defender 검사 도구를 사용할 수 없습니다.': 'The Windows Defender scanning tool is unavailable.',
    'Windows Defender 검사에 실패했습니다: ZXPH0XZ': 'Windows Defender scan failed: ZXPH0XZ',
    'Windows Defender 검사 중 예기치 않은 오류가 발생했습니다: ZXPH0XZ': 'An unexpected error occurred during the Windows Defender scan: ZXPH0XZ',
    'Defender 검사가 완료되었습니다. 종료 코드 0은 위협이 없었거나 위협이 제거되었음을 뜻할 수 있습니다. 안전 판정으로 간주하지 말고 Windows 보안의 보호 기록을 확인하세요.': 'Defender finished scanning. Exit code 0 can mean no threat was found or that a threat was remediated. This is not a safety verdict; check Windows Security Protection History.',
    'Defender가 미조치 위협, 추가 조치 필요 또는 검사 오류를 보고했습니다. Windows 보안의 보호 기록과 Defender 로그를 확인하세요.': 'Defender reported an unremediated threat, required action, or a scan error. Check Windows Security Protection History and Defender logs.',
    'Defender 검사에 실패했습니다 (종료 코드 ZXPH0XZ). ZXPH1XZ': 'Defender scan failed (exit code ZXPH0XZ). ZXPH1XZ',
    'Defender 검사 완료': 'Defender scan completed',
    'Defender 검사 결과 확인 필요': 'Defender scan needs review',
    '이 형식의 복구는 지원하지 않습니다. ZIP에서 읽을 수 있는 항목만 부분 복구할 수 있습니다.': 'Repair is not supported for this format. Only readable entries from ZIP files can be partially recovered.',
    '복구할 파일을 찾을 수 없습니다.': 'The file to repair could not be found.',
    '복구 결과 파일이 이미 있습니다. 덮어쓰지 않았습니다: ZXPH0XZ': 'The recovery output already exists and was not overwritten: ZXPH0XZ',
    '읽을 수 있는 ZIP 항목 ZXPH0XZ개를 새 파일로 저장했습니다. 제외된 항목: ZXPH1XZ개.\n이 기능은 손상된 중앙 디렉터리나 압축 스트림 자체를 복원하지 않습니다.\n\nZXPH2XZ': 'Saved ZXPH0XZ readable ZIP entries to a new file. Skipped entries: ZXPH1XZ.\nThis feature does not reconstruct a damaged central directory or compressed stream.\n\nZXPH2XZ',
    '읽을 수 있는 ZIP 항목이 없어 복구 결과를 만들지 않았습니다.': 'No recovery output was created because no ZIP entries could be read.',
    '복구 결과 검증에 실패했습니다: ZXPH0XZ': 'Recovery output validation failed: ZXPH0XZ',
    'ZIP 중앙 디렉터리를 읽을 수 있는 경우 CRC 검증을 통과한 항목만 새 파일로 부분 복구합니다. 7Z/TAR 복구와 손상된 중앙 디렉터리 또는 압축 데이터 복원은 지원하지 않습니다.': 'If the ZIP central directory is readable, only entries that pass CRC validation are partially recovered into a new file. 7Z/TAR recovery and reconstruction of damaged central directories or compressed data are not supported.',
    '암호화된 ZIP 또는 7Z에서 입력한 후보 암호를 검증합니다. 후보 목록 검색이며 암호 해독을 보장하지 않습니다:': 'Checks candidate passwords against encrypted ZIP or 7Z archives. This searches only the supplied list and cannot guarantee recovery:',
    '부분 복구 완료': 'Partial recovery completed',
    '복구할 수 없음': 'Recovery unavailable',
    '복구하지 못했습니다: ZXPH0XZ': 'Could not recover the archive: ZXPH0XZ',
    '이 ZIP은 암호화되지 않았습니다.': 'This ZIP is not encrypted.',
    'AES ZIP 암호 검증 모듈을 사용할 수 없습니다.': 'The AES ZIP password verification module is unavailable.',
    'ZIP 아카이브를 읽을 수 없습니다: ZXPH0XZ': 'Could not read ZIP archive: ZXPH0XZ',
    '7Z 암호 검증 모듈을 사용할 수 없습니다.': 'The 7Z password verification module is unavailable.',
    '7Z 아카이브를 확인할 수 없습니다: ZXPH0XZ': 'Could not inspect 7Z archive: ZXPH0XZ',
    '이 7Z는 암호화되지 않았습니다.': 'This 7Z archive is not encrypted.',
    '암호 복구는 암호화된 ZIP 또는 7Z만 지원합니다.': 'Password recovery supports encrypted ZIP or 7Z archives only.',
    '지원하지 않는 암호 복구 대상: ZXPH0XZ': 'Unsupported password recovery target: ZXPH0XZ',
    '지원하지 않음': 'Unsupported',
    '아카이브를 확인할 수 없습니다: ZXPH0XZ': 'Could not inspect the archive: ZXPH0XZ',
    '암호 검사를 시작할 수 없습니다: ZXPH0XZ': 'Could not start password verification: ZXPH0XZ',
    '후보 암호가 아카이브 내용을 검증하지 못했습니다. 이는 암호를 찾지 못했다는 뜻이며, 복구 불가능하다는 의미는 아닙니다.': 'None of the candidate passwords validated the archive contents. This only means no candidate matched; it does not mean the password cannot be recovered.',
    '입력된 후보 중 아카이브 내용을 정상 검증한 암호가 없습니다.': 'None of the supplied candidates successfully validated the archive contents.',
    '후보 확인 결과': 'Candidate check result',
})

_settings = QSettings("AuraStudios", "AuraZip") if github_updates_enabled() else store_settings()
_language = _settings.value("language", "ko")

def set_language(language):
    global _language
    _language = language if language in ("ko", "en") else "ko"

def tr(text):
    return EN.get(text, text) if _language == "en" else text

def trf(template, *values):
    result = tr(template)
    for index, value in enumerate(values):
        result = result.replace(f"ZXPH{index}XZ", str(value))
    return result.replace("{{", "{").replace("}}", "}")

def translate_html(html):
    if _language != "en":
        return html
    parts = re.split(r"(<[^>]*>)", html)
    for index in range(0, len(parts), 2):
        raw = parts[index]
        stripped = raw.strip()
        if stripped in EN:
            parts[index] = raw.replace(stripped, EN[stripped], 1)
    return "".join(parts)
