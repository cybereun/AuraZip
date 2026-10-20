"""
AuraZip - In-App User Guide & Help Dialog
완전 내장형 사용자 가이드 및 도움말 대화상자
"""
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextBrowser, QFrame, QSplitter
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont


HELP_DOCS = {
    "start": {
        "title": "AuraZip 시작하기",
        "icon": "tb_open.png",
        "html": """
        <div style="font-family: -apple-system, 'Segoe UI', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #1E293B;">
            <h2 style="color: #4F46E5; margin-top: 0; padding-bottom: 8px; border-bottom: 2px solid #EEF2FF;">
                ⚡ AuraZip 시작하기
            </h2>
            <p>
                <b>AuraZip</b>은 초고속 다중 포맷 압축 엔진과 군사 표준 <b>AES-256</b> 보안 암호화를 탑재한 차세대 고성능 압축 유틸리티입니다.
            </p>
            
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; margin: 16px 0;">
                <h4 style="color: #0F172A; margin: 0 0 8px 0;">🖥️ 핵심 작업 화면 구성</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><b>시작 대시보드 (Start View)</b>: 원클릭 액션 카드(열기, 새로 압축, 보안 금고 압축)와 드래그&드롭 드롭존을 통해 직관적으로 작업을 시작합니다.</li>
                    <li><b>아카이브 탐색기 (Archive View)</b>: 압축 파일 내부의 디렉터리 트리, 파일 상세 속성, 실시간 검색 필터, 저장 공간 절감률 통계를 제공합니다.</li>
                    <li><b>오피스 스타일 리본 메뉴</b>: 파일, 편집, 도구 & 보안, 보기, 도움말의 5개 탭으로 모든 고급 기능을 한눈에 조작할 수 있습니다.</li>
                </ul>
            </div>

            <div style="background-color: #EEF2FF; border-left: 4px solid #6366F1; padding: 10px 14px; border-radius: 4px; margin-top: 14px;">
                <b>💡 팁:</b> 압축하고 싶은 파일이나 폴더를 AuraZip 창으로 언제든 드래그하면 즉시 압축 또는 열기가 실행됩니다.
            </div>
        </div>
        """
    },
    "compress": {
        "title": "압축 및 보안 암호화",
        "icon": "tb_new.png",
        "html": """
        <div style="font-family: -apple-system, 'Segoe UI', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #1E293B;">
            <h2 style="color: #4F46E5; margin-top: 0; padding-bottom: 8px; border-bottom: 2px solid #EEF2FF;">
                📦 파일 압축 및 보안 설정
            </h2>
            <p>
                AuraZip은 전 세계 표준 형식부터 초고압축 알고리즘까지 다양한 아카이브 형식을 지원합니다.
            </p>

            <table style="width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 13px;">
                <thead>
                    <tr style="background-color: #F1F5F9; border-bottom: 2px solid #CBD5E1; text-align: left;">
                        <th style="padding: 8px 10px; color: #334155;">포맷</th>
                        <th style="padding: 8px 10px; color: #334155;">알고리즘</th>
                        <th style="padding: 8px 10px; color: #334155;">특징 및 권장 용도</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px 10px;"><b>ZIP</b></td>
                        <td style="padding: 8px 10px;">Deflate / ZIP64</td>
                        <td style="padding: 8px 10px;">전 세계 모든 기기 및 OS 호환 (4GB 초과 대용량 파일 완벽 지원)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
                        <td style="padding: 8px 10px;"><b>7Z</b></td>
                        <td style="padding: 8px 10px;">LZMA2</td>
                        <td style="padding: 8px 10px;">극대화된 압축률 제공 (대용량 데이터 백업에 최적)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 8px 10px;"><b>TAR</b></td>
                        <td style="padding: 8px 10px;">POSIX Tar</td>
                        <td style="padding: 8px 10px;">압축 없이 파일들을 그대로 묶어 신속 보관</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
                        <td style="padding: 8px 10px;"><b>TGZ</b></td>
                        <td style="padding: 8px 10px;">Gzip + Tar</td>
                        <td style="padding: 8px 10px;">Linux/Unix 개발 환경 표준 배포 아카이브</td>
                    </tr>
                </tbody>
            </table>

            <h4 style="color: #0F172A; margin: 16px 0 6px 0;">🛡️ 강력한 AES-256 군사 규격 보안</h4>
            <p>
                보안 금고 압축 시 미국 연방 표준 <b>AES-256 암호화</b>가 적용되어 외부 유출이나 해킹으로부터 민감한 데이터를 완벽하게 보호합니다.
            </p>
        </div>
        """
    },
    "extract": {
        "title": "스마트 압축 풀기",
        "icon": "tb_extract.png",
        "html": """
        <div style="font-family: -apple-system, 'Segoe UI', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #1E293B;">
            <h2 style="color: #4F46E5; margin-top: 0; padding-bottom: 8px; border-bottom: 2px solid #EEF2FF;">
                📂 스마트 압축 풀기 가이드
            </h2>
            <p>
                AuraZip의 <b>스마트 압축 풀기(Smart Extract)</b> 기능은 바탕화면이나 폴더가 어지럽혀지는 것을 원천 방지합니다.
            </p>

            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; margin: 14px 0;">
                <h4 style="color: #0F172A; margin: 0 0 8px 0;">💡 스마트 추출 작동 원리</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><b>단일 폴더 아카이브</b>: 압축 파일 내부가 이미 하나의 폴더로 감싸져 있는 경우, 불필요하게 폴더를 이중 생성하지 않고 원래 폴더명으로 깔끔하게 풀어줍니다.</li>
                    <li><b>다중 파일 아카이브</b>: 압축 파일 내부에 여러 파일이 흩어져 있는 경우, 압축 파일 이름과 동일한 전용 폴더를 자동으로 만들어 그 안에 안전하게 해제합니다.</li>
                </ul>
            </div>

            <h4 style="color: #0F172A; margin: 16px 0 6px 0;">🔍 개별 파일 인라인 뷰어</h4>
            <p>
                압축을 전체 해제하지 않고도, 내부 목록에서 파일을 <b>더블 클릭</b>하면 시스템 임시 격리 영역에서 해당 파일을 즉시 열람할 수 있습니다.
            </p>
        </div>
        """
    },
    "tools": {
        "title": "보안 & 검사 도구",
        "icon": "tb_test.png",
        "html": """
        <div style="font-family: -apple-system, 'Segoe UI', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #1E293B;">
            <h2 style="color: #4F46E5; margin-top: 0; padding-bottom: 8px; border-bottom: 2px solid #EEF2FF;">
                🛡️ 전문 보안 & 검사 도구
            </h2>
            <p>
                AuraZip은 단순 압축을 넘어 아카이브의 안정성과 무결성을 지키는 전문 유틸리티를 기본 탑재하고 있습니다.
            </p>

            <ul style="padding-left: 20px; line-height: 1.8;">
                <li><b>무결성 검사 (Ctrl+T)</b>: 아카이브 내 각 파일의 CRC-32 체크섬을 전수 대조하여 전송 중 발생한 데이터 손상이나 비트 왜곡을 사전에 정밀 판별합니다.</li>
                <li><b>악성코드 검사 (Ctrl+I)</b>: 이중 확장자, 숨겨진 실행 파일(.exe, .bat, .vbs, .cmd) 및 스크립트 위험 요소를 자동 탐지하여 안전성을 안내합니다.</li>
                <li><b>손상 파일 복구 (Repair)</b>: 네트워크 불안정 등으로 헤더가 손상된 아카이브에서 읽을 수 있는 정상 스트림을 최대한 복원합니다.</li>
                <li><b>암호 복구 마법사 (Password)</b>: 설정했던 비밀번호를 잊어버렸을 때, 자릿수와 문자 패턴 힌트를 조합하여 복원을 시도합니다.</li>
            </ul>
        </div>
        """
    },
    "shortcuts": {
        "title": "단축키 전체 안내",
        "icon": "tb_admin.png",
        "html": """
        <div style="font-family: -apple-system, 'Segoe UI', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #1E293B;">
            <h2 style="color: #4F46E5; margin-top: 0; padding-bottom: 8px; border-bottom: 2px solid #EEF2FF;">
                ⌨️ 키보드 단축키 안내
            </h2>
            <p>
                키보드 단축키를 활용하여 모든 압축 작업을 빠르고 능숙하게 제어할 수 있습니다.
            </p>

            <table style="width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 13px;">
                <thead>
                    <tr style="background-color: #F1F5F9; border-bottom: 2px solid #CBD5E1; text-align: left;">
                        <th style="padding: 6px 10px; color: #334155; width: 140px;">단축키</th>
                        <th style="padding: 6px 10px; color: #334155;">기능</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">Ctrl + N</kbd></td><td style="padding: 6px 10px;">새로 압축 대화상자 실행</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">Ctrl + O</kbd></td><td style="padding: 6px 10px;">기존 압축 파일 열기</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">Ctrl + E</kbd></td><td style="padding: 6px 10px;">현재 아카이브 압축 풀기</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">F4</kbd></td><td style="padding: 6px 10px;">현재 아카이브 닫기 (시작화면 전환)</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">Ctrl + T</kbd></td><td style="padding: 6px 10px;">아카이브 무결성 검사 실행</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">Ctrl + I</kbd></td><td style="padding: 6px 10px;">악성코드 의심 파일 검사</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">Ctrl + F</kbd></td><td style="padding: 6px 10px;">아카이브 내부 파일 검색</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">F6</kbd></td><td style="padding: 6px 10px;">시작 화면 토글</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">F1</kbd></td><td style="padding: 6px 10px;">사용자 가이드 및 도움말 열기</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;"><td style="padding: 6px 10px;"><kbd style="background: #E2E8F0; padding: 2px 6px; border-radius: 4px;">Ctrl + W</kbd></td><td style="padding: 6px 10px;">AuraZip 프로그램 종료</td></tr>
                </tbody>
            </table>
        </div>
        """
    },
    "faq": {
        "title": "자주 묻는 질문 (FAQ)",
        "icon": "tb_info.png",
        "html": """
        <div style="font-family: -apple-system, 'Segoe UI', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #1E293B;">
            <h2 style="color: #4F46E5; margin-top: 0; padding-bottom: 8px; border-bottom: 2px solid #EEF2FF;">
                ❓ 자주 묻는 질문 (FAQ)
            </h2>

            <div style="margin-bottom: 16px;">
                <h4 style="color: #0F172A; margin: 0 0 4px 0;">Q. 다른 OS(Mac, Linux)에서 압축한 파일명이 깨지지 않나요?</h4>
                <p style="margin: 0; color: #475569;">
                    A. AuraZip은 표준 <b>UTF-8 유니코드 인코딩</b>을 기본 탑재하여, macOS, Linux, Windows 간 교환 시에도 한글 및 다국어 파일명이 깨지지 않습니다.
                </p>
            </div>

            <div style="margin-bottom: 16px;">
                <h4 style="color: #0F172A; margin: 0 0 4px 0;">Q. 4GB 이상의 대용량 파일도 압축할 수 있나요?</h4>
                <p style="margin: 0; color: #475569;">
                    A. 네, AuraZip은 <b>ZIP64</b> 확장 규격과 <b>7Z 64비트</b> 아키텍처를 지원하므로 테라바이트(TB) 단위의 대용량 파일도 문제없이 압축 및 해제할 수 있습니다.
                </p>
            </div>

            <div style="margin-bottom: 16px;">
                <h4 style="color: #0F172A; margin: 0 0 4px 0;">Q. 압축 파일 내의 개별 파일만 추가하거나 삭제할 수 있나요?</h4>
                <p style="margin: 0; color: #475569;">
                    A. 네, 상단 [편집] 탭의 [파일 추가(Ins)], [파일 삭제(Del)], [이름 바꾸기(F2)] 기능을 통해 아카이브 전체를 풀지 않고도 내부 내용을 손쉽게 편집할 수 있습니다.
                </p>
            </div>
        </div>
        """
    }
}


class HelpDialog(QDialog):
    """외부 링크 없이 앱 내부에 완전 통합된 사용자 도움말 뷰어"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AuraZip 사용자 가이드 및 도움말")
        self.resize(800, 560)
        self.setMinimumSize(680, 480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.asset_dir = os.path.join(os.path.dirname(__file__), "assets")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # Header Section
        header_layout = QHBoxLayout()
        header_title = QLabel("📖 AuraZip 통합 도움말 센터")
        header_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #1E1B4B;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        ver_lbl = QLabel("버전 2.5.0 LTS | 내장 가이드")
        ver_lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600;")
        header_layout.addWidget(ver_lbl)
        main_layout.addLayout(header_layout)

        # Content Splitter (Left: Navigation List, Right: HTML Viewer)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E2E8F0;
                width: 2px;
            }
        """)

        # Left: Navigation List
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 10px;
                padding: 6px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                color: #334155;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
            QListWidget::item:selected {
                background-color: #EEF2FF;
                color: #4F46E5;
                border-left: 3px solid #4F46E5;
            }
        """)

        for key, doc in HELP_DOCS.items():
            item = QListWidgetItem(doc["title"])
            icon_p = os.path.join(self.asset_dir, doc["icon"])
            if os.path.exists(icon_p):
                item.setIcon(QIcon(icon_p))
            item.setData(Qt.UserRole, key)
            self.nav_list.addItem(item)

        splitter.addWidget(self.nav_list)

        # Right: Rich Text Browser
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setStyleSheet("""
            QTextBrowser {
                background-color: #FFFFFF;
                border: 1.5px solid #CBD5E1;
                border-radius: 10px;
                padding: 18px 24px;
                font-size: 13px;
                color: #1E293B;
            }
        """)
        splitter.addWidget(self.browser)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter, 1)

        # Bottom Bar
        bottom_box = QHBoxLayout()
        bottom_box.addStretch()
        close_btn = QPushButton("닫기")
        close_btn.setObjectName("PrimaryBtn")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        bottom_box.addWidget(close_btn)
        main_layout.addLayout(bottom_box)

        # Connect Selection
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)

    def _on_nav_changed(self, row: int):
        item = self.nav_list.item(row)
        if not item:
            return
        key = item.data(Qt.UserRole)
        doc = HELP_DOCS.get(key)
        if doc:
            self.browser.setHtml(doc["html"])
