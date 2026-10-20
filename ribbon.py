import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QFrame, QToolButton, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QAction, QColor, QFont, QFontMetrics


class RibbonButton(QToolButton):
    def __init__(self, text: str, icon_name: str, is_large: bool = True, min_width: int = 0, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCursor(Qt.PointingHandCursor)
        self.asset_dir = os.path.join(os.path.dirname(__file__), "assets")
        
        icon_path = os.path.join(self.asset_dir, icon_name)
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))

        if is_large:
            self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.setIconSize(QSize(28, 28))
            
            # 글꼴 메트릭스를 기준으로 텍스트가 절대 잘리거나 생략(...)되지 않도록 너비 자동 계산
            btn_font = QFont("Malgun Gothic", 9)
            btn_font.setBold(True)
            self.setFont(btn_font)
            fm = QFontMetrics(btn_font)
            
            lines = text.split("\n")
            max_line_width = max(fm.horizontalAdvance(l.strip()) for l in lines) if lines else 50
            # 텍스트 좌우 여백 및 패딩 24px 부여 (최소 68px 이상)
            calc_width = max(68, max_line_width + 24)
            btn_width = max(calc_width, min_width)
            
            self.setFixedSize(btn_width, 70)
            self.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 8px;
                    font-family: 'Malgun Gothic', 'Segoe UI', sans-serif;
                    font-size: 11px;
                    font-weight: 600;
                    color: #334155;
                    padding: 3px 2px;
                    text-align: center;
                }
                QToolButton:hover {
                    background-color: #EEF2FF;
                    border-color: #C7D2FE;
                    color: #4F46E5;
                }
                QToolButton:pressed {
                    background-color: #E0E7FF;
                }
                QToolButton:disabled {
                    color: #CBD5E1;
                }
            """)
        else:
            self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.setIconSize(QSize(18, 18))
            self.setFixedHeight(22)
            self.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 500;
                    color: #334155;
                    padding: 2px 6px;
                    text-align: left;
                }
                QToolButton:hover {
                    background-color: #EEF2FF;
                    border-color: #C7D2FE;
                    color: #4F46E5;
                }
                QToolButton:pressed {
                    background-color: #E0E7FF;
                }
                QToolButton:disabled {
                    color: #CBD5E1;
                }
            """)


class RibbonGroup(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("RibbonGroupFrame")
        self.setStyleSheet("""
            QFrame#RibbonGroupFrame {
                background-color: transparent;
                border-right: 1px solid #E2E8F0;
                margin-right: 4px;
                padding-right: 6px;
            }
            QLabel#RibbonGroupTitle {
                color: #94A3B8;
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                border: none;
                background: transparent;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 6, 4)
        layout.setSpacing(2)

        # Content horizontal layout
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)
        layout.addLayout(self.content_layout, 1)

        # Bottom title
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("RibbonGroupTitle")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_lbl, 0, Qt.AlignBottom)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_small_column(self, widgets: list):
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(2)
        col.setAlignment(Qt.AlignVCenter)
        for w in widgets:
            col.addWidget(w)
        self.content_layout.addLayout(col)


class RibbonBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RibbonBar")
        self.setFixedHeight(124)
        self.setStyleSheet("""
            QFrame#RibbonBar {
                background-color: #FFFFFF;
                border-bottom: 1.5px solid #E2E8F0;
            }
            QTabWidget::pane {
                border: none;
                background-color: #FFFFFF;
                top: -1px;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #64748B;
                font-size: 12px;
                font-weight: 700;
                padding: 6px 16px;
                border: none;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:hover {
                color: #4F46E5;
                background-color: #F8FAFC;
            }
            QTabBar::tab:selected {
                color: #4F46E5;
                border-bottom: 2px solid #4F46E5;
                background-color: #FFFFFF;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self._build_file_tab()
        self._build_edit_tab()
        self._build_tools_tab()
        self._build_view_tab()
        self._build_help_tab()

    def _create_tab_page(self) -> tuple:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignLeft)
        return page, layout

    def _build_file_tab(self):
        page, layout = self._create_tab_page()

        # Group 1: 기본 작업
        grp_basic = RibbonGroup("기본 작업", page)
        self.btn_new = RibbonButton("새로 압축\n(Ctrl+N)", "tb_new.png", is_large=True)
        self.btn_open = RibbonButton("열기\n(Ctrl+O)", "tb_open.png", is_large=True)
        self.btn_extract = RibbonButton("압축 풀기\n(Ctrl+E)", "tb_extract.png", is_large=True)
        self.btn_close = RibbonButton("닫기\n(F4)", "tb_delete.png", is_large=True)
        grp_basic.add_widget(self.btn_new)
        grp_basic.add_widget(self.btn_open)
        grp_basic.add_widget(self.btn_extract)
        grp_basic.add_widget(self.btn_close)
        layout.addWidget(grp_basic)

        # Group 2: 아카이브 관리
        grp_manage = RibbonGroup("아카이브 관리", page)
        self.btn_save_as = RibbonButton("다른 이름으로 저장...", "tb_copy.png", is_large=False)
        self.btn_open_folder = RibbonButton("파일 위치 폴더 열기", "tb_folder_open.png", is_large=False)
        self.btn_del_archive = RibbonButton("압축 파일 삭제 (Ctrl+Del)", "tb_delete.png", is_large=False)
        self.btn_purge_archive = RibbonButton("압축 파일 완전 삭제 (Shift+Ctrl+Del)", "tb_delete.png", is_large=False)
        grp_manage.add_small_column([self.btn_save_as, self.btn_open_folder])
        grp_manage.add_small_column([self.btn_del_archive, self.btn_purge_archive])
        layout.addWidget(grp_manage)

        # Group 3: 창 및 세션 관리
        grp_window = RibbonGroup("창 및 세션", page)
        self.btn_new_window = RibbonButton("새 창 띄우기 (Ctrl+Shift+N)", "tb_new_window.png", is_large=False)
        self.btn_admin_window = RibbonButton("새 창 (관리자 권한)", "tb_admin.png", is_large=False)
        self.btn_exit = RibbonButton("AuraZip 종료 (Ctrl+W)", "tb_delete.png", is_large=False)
        grp_window.add_small_column([self.btn_new_window, self.btn_admin_window, self.btn_exit])
        layout.addWidget(grp_window)

        # Group 4: 최근 파일
        grp_recent = RibbonGroup("최근 기록", page)
        self.btn_recent = RibbonButton("최근 파일\n목록", "tb_open.png", is_large=True)
        self.recent_menu = QMenu(self)
        self.btn_recent.setMenu(self.recent_menu)
        self.btn_recent.setPopupMode(QToolButton.InstantPopup)
        grp_recent.add_widget(self.btn_recent)
        layout.addWidget(grp_recent)

        self.tabs.addTab(page, "파일 / 홈")

    def _build_edit_tab(self):
        page, layout = self._create_tab_page()

        # Group 1: 항목 조작
        grp_items = RibbonGroup("파일 조작", page)
        self.btn_add_file = RibbonButton("파일 추가\n(Ins)", "tb_add.png", is_large=True)
        self.btn_del_file = RibbonButton("파일 삭제\n(Del)", "tb_delete.png", is_large=True)
        self.btn_rename = RibbonButton("이름 바꾸기\n(F2)", "tb_rename.png", is_large=True)
        grp_items.add_widget(self.btn_add_file)
        grp_items.add_widget(self.btn_del_file)
        grp_items.add_widget(self.btn_rename)
        layout.addWidget(grp_items)

        # Group 2: 클립보드
        grp_clip = RibbonGroup("클립보드", page)
        self.btn_clip_copy = RibbonButton("클립보드로 복사 (Ctrl+C)", "tb_copy.png", is_large=False)
        self.btn_clip_paste = RibbonButton("클립보드에서 붙여넣기 (Ctrl+V)", "tb_paste.png", is_large=False)
        self.btn_clip_path = RibbonButton("파일 경로명 복사", "tb_copy.png", is_large=False)
        grp_clip.add_small_column([self.btn_clip_copy, self.btn_clip_paste, self.btn_clip_path])
        layout.addWidget(grp_clip)

        # Group 3: 메타데이터 & 선택
        grp_meta = RibbonGroup("주석 & 선택", page)
        self.btn_comment = RibbonButton("설명 편집\n(주석)", "tb_comment.png", is_large=True)
        self.btn_select_all = RibbonButton("모두 선택 (Ctrl+A)", "tb_add.png", is_large=False)
        self.btn_invert_sel = RibbonButton("선택 반전", "tb_rename.png", is_large=False)
        grp_meta.add_widget(self.btn_comment)
        grp_meta.add_small_column([self.btn_select_all, self.btn_invert_sel])
        layout.addWidget(grp_meta)

        self.tabs.addTab(page, "편집")

    def _build_tools_tab(self):
        page, layout = self._create_tab_page()

        # Group 1: 무결성 & 보안 검사
        grp_security = RibbonGroup("보안 & 검사", page)
        self.btn_test = RibbonButton("무결성 검사\n(Ctrl+T)", "tb_test.png", is_large=True, min_width=88)
        self.btn_scan = RibbonButton("악성코드 검사\n(Ctrl+I)", "tb_scan.png", is_large=True, min_width=92)
        grp_security.add_widget(self.btn_test)
        grp_security.add_widget(self.btn_scan)
        layout.addWidget(grp_security)

        # Group 2: 아카이브 복구
        grp_repair = RibbonGroup("복구 도구", page)
        self.btn_repair = RibbonButton("손상 파일 복구\n(Repair)", "tb_repair.png", is_large=True, min_width=98)
        self.btn_recover_pw = RibbonButton("암호 복구\n(Password)", "tb_unlock.png", is_large=True, min_width=92)
        grp_repair.add_widget(self.btn_repair)
        grp_repair.add_widget(self.btn_recover_pw)
        layout.addWidget(grp_repair)

        # Group 3: 파일 찾기
        grp_search = RibbonGroup("탐색", page)
        self.btn_find = RibbonButton("파일 찾기\n(Ctrl+F)", "tb_search.png", is_large=True, min_width=84)
        grp_search.add_widget(self.btn_find)
        layout.addWidget(grp_search)

        self.tabs.addTab(page, "도구 & 보안")

    def _build_view_tab(self):
        page, layout = self._create_tab_page()

        # Group 1: 레이아웃
        grp_layout = RibbonGroup("화면 표시", page)
        self.btn_toggle_start = RibbonButton("시작 화면 (F6)", "tb_open.png", is_large=False)
        self.btn_toggle_nav = RibbonButton("경로 내비게이션 (F7)", "tb_folder_open.png", is_large=False)
        self.btn_toggle_status = RibbonButton("상태 표시줄 표시", "tb_info.png", is_large=False)
        grp_layout.add_small_column([self.btn_toggle_start, self.btn_toggle_nav, self.btn_toggle_status])
        layout.addWidget(grp_layout)

        # Group 2: 미리보기 & 옵션
        grp_preview = RibbonGroup("보기 옵션", page)
        self.btn_comment_view = RibbonButton("파일 설명창 (F8)", "tb_comment.png", is_large=False)
        self.btn_img_preview = RibbonButton("이미지 미리보기 사용", "tb_web.png", is_large=False)
        self.btn_always_on_top = RibbonButton("항상 위에 표시", "tb_admin.png", is_large=False)
        grp_preview.add_small_column([self.btn_comment_view, self.btn_img_preview, self.btn_always_on_top])
        layout.addWidget(grp_preview)

        # Group 3: 테마 & 스타일
        grp_theme = RibbonGroup("테마 설정", page)
        self.btn_color = RibbonButton("색상 / 테마\n설정", "tb_color.png", is_large=True, min_width=86)
        grp_theme.add_widget(self.btn_color)
        layout.addWidget(grp_theme)

        self.tabs.addTab(page, "보기")

    def _build_help_tab(self):
        page, layout = self._create_tab_page()

        # Group 1: 정보 & 폴더
        grp_help = RibbonGroup("프로그램 안내", page)
        self.btn_about = RibbonButton("AuraZip 정보\n(About)", "tb_info.png", is_large=True, min_width=96)
        self.btn_open_install_dir = RibbonButton("설치 폴더 열기\n(Explorer)", "tb_folder_open.png", is_large=True, min_width=108)
        self.btn_help_page = RibbonButton("사용자 가이드\n(도움말)", "tb_web.png", is_large=True, min_width=108)
        grp_help.add_widget(self.btn_about)
        grp_help.add_widget(self.btn_open_install_dir)
        grp_help.add_widget(self.btn_help_page)
        self.btn_check_update = RibbonButton("업데이트 확인\n(Update)", "tb_admin.png", is_large=True, min_width=96)
        grp_help.add_widget(self.btn_check_update)
        layout.addWidget(grp_help)

        self.tabs.addTab(page, "도움말")
