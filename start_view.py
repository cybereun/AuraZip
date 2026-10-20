import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QIcon, QColor


class HoverIconButton(QPushButton):
    """테두리가 전혀 없고 마우스 호버/선택 시 아이콘이 부드럽게 확대되는 버튼"""
    def __init__(self, icon_path: str, normal_size: int = 38, hover_size: int = 46, parent=None):
        super().__init__(parent)
        self.normal_size = normal_size
        self.hover_size = hover_size
        self.setFixedSize(54, 54)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("HeroIconBtn")

        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(normal_size, normal_size))

        # 테두리 완전 제거 및 투명 배경
        self.setStyleSheet("""
            QPushButton#HeroIconBtn {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton#HeroIconBtn:hover {
                background-color: transparent;
                border: none;
            }
            QPushButton#HeroIconBtn:pressed {
                background-color: transparent;
                border: none;
            }
        """)

        # 부드러운 스케일 애니메이션
        self.anim = QPropertyAnimation(self, b"iconSize")
        self.anim.setDuration(160)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def zoom_in(self):
        self.anim.stop()
        self.anim.setStartValue(self.iconSize())
        self.anim.setEndValue(QSize(self.hover_size, self.hover_size))
        self.anim.start()

    def zoom_out(self):
        self.anim.stop()
        self.anim.setStartValue(self.iconSize())
        self.anim.setEndValue(QSize(self.normal_size, self.normal_size))
        self.anim.start()

    def enterEvent(self, event):
        self.zoom_in()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.zoom_out()
        super().leaveEvent(event)


class ActionCard(QFrame):
    clicked = Signal()

    def __init__(self, title: str, subtitle: str, icon_name: str, badge: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("ActionCardWidget")
        self.setFixedSize(192, 142)
        self.setCursor(Qt.PointingHandCursor)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(14)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(4)
        layout.setContentsMargins(10, 10, 10, 10)

        # 1. 테두리 없는 깔끔한 아이콘 (호버/선택 시 확대)
        asset_p = os.path.join(os.path.dirname(__file__), "assets", icon_name)
        self.icon_btn = HoverIconButton(asset_p, normal_size=38, hover_size=46, parent=self)
        self.icon_btn.clicked.connect(self.clicked.emit)
        layout.addWidget(self.icon_btn, 0, Qt.AlignCenter)

        # 2. Title Label
        self.title_lbl = QLabel(title)
        self.title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_lbl)

        # 3. Subtitle Label
        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        self.sub_lbl.setWordWrap(True)
        layout.addWidget(self.sub_lbl)

        # 4. Optional Badge
        self.badge_lbl = None
        if badge:
            self.badge_lbl = QLabel(badge)
            self.badge_lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.badge_lbl, 0, Qt.AlignCenter)

    def apply_theme(self, theme: dict):
        self.setStyleSheet(f"""
            QFrame#ActionCardWidget {{
                background-color: {theme['bg_card']};
                border: 1px solid {theme['border_card']};
                border-radius: 14px;
            }}
            QFrame#ActionCardWidget:hover {{
                border: 1.5px solid {theme['border_card_hover']};
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        self.title_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {theme['text_main']};
            border: none;
            background: transparent;
        """)
        self.sub_lbl.setStyleSheet(f"""
            font-size: 11px;
            color: {theme['text_muted']};
            border: none;
            background: transparent;
        """)
        if self.badge_lbl:
            self.badge_lbl.setStyleSheet(f"""
                background-color: {theme['subtle_bg']};
                color: {theme['primary']};
                font-size: 10px;
                font-weight: 700;
                border-radius: 5px;
                padding: 1px 6px;
                border: none;
            """)

    def enterEvent(self, event):
        self.icon_btn.zoom_in()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.icon_btn.zoom_out()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class StartView(QScrollArea):
    open_requested = Signal()
    create_requested = Signal(bool)  # is_secure
    file_dropped = Signal(str)
    recent_file_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StartScrollArea")
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.current_theme = None

        # Container widget inside scroll area
        self.container = QWidget()
        self.container.setObjectName("StartContainer")
        self.container.setAttribute(Qt.WA_StyledBackground, True)
        self.setWidget(self.container)

        main_layout = QVBoxLayout(self.container)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(24, 12, 24, 14)

        # Brand Header Section
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(2)

        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        app_icon_p = os.path.join(os.path.dirname(__file__), "assets", "app_icon.png")
        if os.path.exists(app_icon_p):
            pix = QPixmap(app_icon_p).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        header_layout.addWidget(logo_lbl)

        self.title_lbl = QLabel("AuraZip")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.title_lbl)

        self.sub_lbl = QLabel("빠르고 안전한 차세대 고성능 압축 유틸리티")
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.sub_lbl)

        main_layout.addLayout(header_layout)

        # 3 Action Cards (Only icon reacts on hover!)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        cards_layout.setAlignment(Qt.AlignCenter)

        self.card_open = ActionCard("압축 파일 열기", "기존 아카이브 탐색 및 풀기", "tb_open.png")
        self.card_open.clicked.connect(self.open_requested.emit)
        cards_layout.addWidget(self.card_open)

        self.card_create = ActionCard("스마트 새로 압축", "파일/폴더를 최적 압축률로", "tb_new.png", "빠른 압축")
        self.card_create.clicked.connect(lambda: self.create_requested.emit(False))
        cards_layout.addWidget(self.card_create)

        self.card_secure = ActionCard("보안 금고 압축", "AES-256 군사 표준 암호화", "tb_secure.png", "보안 강화")
        self.card_secure.clicked.connect(lambda: self.create_requested.emit(True))
        cards_layout.addWidget(self.card_secure)

        main_layout.addLayout(cards_layout)

        # Interactive Drop Zone
        self.drop_box = QFrame()
        self.drop_box.setFixedSize(608, 80)
        drop_layout = QVBoxLayout(self.drop_box)
        drop_layout.setAlignment(Qt.AlignCenter)
        drop_layout.setSpacing(4)
        drop_layout.setContentsMargins(8, 8, 8, 8)

        self.drop_title = QLabel("압축 파일을 여기에 드래그하여 바로 열기")
        self.drop_title.setAlignment(Qt.AlignCenter)

        chips_row = QHBoxLayout()
        chips_row.setAlignment(Qt.AlignCenter)
        chips_row.setSpacing(6)
        self.chips = []
        for fmt in ["ZIP 64", "7Z Ultra", "TAR", "TGZ", "AES-256"]:
            chip = QLabel(fmt)
            chips_row.addWidget(chip)
            self.chips.append(chip)

        drop_layout.addWidget(self.drop_title)
        drop_layout.addLayout(chips_row)
        main_layout.addWidget(self.drop_box, 0, Qt.AlignCenter)

        # Recent Files Frame
        self.recent_frame = QFrame()
        self.recent_frame.setFixedWidth(608)
        recent_layout = QVBoxLayout(self.recent_frame)
        recent_layout.setContentsMargins(0, 0, 0, 0)
        recent_layout.setSpacing(4)

        self.recent_title = QLabel("최근 작업한 아카이브")
        recent_layout.addWidget(self.recent_title)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(80)
        self.recent_list.itemClicked.connect(self._on_recent_clicked)
        recent_layout.addWidget(self.recent_list)

        main_layout.addWidget(self.recent_frame, 0, Qt.AlignCenter)
        self.recent_frame.hide()

        from theme import get_theme_dict
        self.apply_theme(get_theme_dict("Aura Indigo"))

    def apply_theme(self, theme: dict):
        self.current_theme = theme
        self.container.setStyleSheet(f"""
            QWidget#StartContainer {{
                background-color: {theme['bg_canvas']};
            }}
        """)
        self.title_lbl.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 800;
            color: {theme['text_main']};
            letter-spacing: -0.5px;
            border: none;
            background: transparent;
        """)
        self.sub_lbl.setStyleSheet(f"""
            font-size: 12px;
            color: {theme['text_muted']};
            font-weight: 500;
            border: none;
            background: transparent;
        """)
        self.card_open.apply_theme(theme)
        self.card_create.apply_theme(theme)
        self.card_secure.apply_theme(theme)

        self.drop_box.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['bg_card']};
                border: 2px dashed {theme['border_card']};
                border-radius: 12px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        self.drop_title.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {theme['text_secondary']};
            border: none;
            background: transparent;
        """)
        for chip in self.chips:
            chip.setStyleSheet(f"""
                background-color: {theme['subtle_bg']};
                color: {theme['text_secondary']};
                font-size: 10px;
                font-weight: 700;
                padding: 2px 7px;
                border-radius: 5px;
                border: 1px solid {theme['border_card']};
            """)

        self.recent_title.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {theme['text_secondary']};
            border: none;
            background: transparent;
        """)
        self.recent_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme['bg_card']};
                border: 1px solid {theme['border_color']};
                border-radius: 8px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 5px 10px;
                border-radius: 5px;
                color: {theme['text_main']};
                font-weight: 500;
                font-size: 12px;
            }}
            QListWidget::item:hover {{
                background-color: {theme['subtle_bg']};
                color: {theme['primary']};
            }}
        """)

    def update_recent_files(self, files: list):
        self.recent_list.clear()
        valid = [f for f in files if os.path.exists(f)]
        if valid:
            self.recent_frame.show()
            for f in valid[:3]:
                name = os.path.basename(f)
                item = QListWidgetItem(f"📦  {name}   —  {f}")
                item.setToolTip(f)
                item.setData(Qt.UserRole, f)
                self.recent_list.addItem(item)
        else:
            self.recent_frame.hide()

    def _on_recent_clicked(self, item):
        path = item.data(Qt.UserRole)
        if path and os.path.exists(path):
            self.recent_file_clicked.emit(path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            t = self.current_theme
            bg = t['subtle_bg'] if t else "#EEF2FF"
            border = t['primary'] if t else "#6366F1"
            self.drop_box.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border: 2px dashed {border};
                    border-radius: 12px;
                }}
                QLabel {{
                    border: none;
                    background: transparent;
                }}
            """)

    def dragLeaveEvent(self, event):
        t = self.current_theme
        bg = t['bg_card'] if t else "#FFFFFF"
        border = t['border_card'] if t else "#CBD5E1"
        self.drop_box.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 2px dashed {border};
                border-radius: 12px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

    def dropEvent(self, event):
        self.dragLeaveEvent(event)
        urls = event.mimeData().urls()
        if urls:
            local_path = urls[0].toLocalFile()
            if local_path and os.path.exists(local_path):
                self.file_dropped.emit(local_path)
