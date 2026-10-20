"""
AuraZip - Next-Gen Modern UI Theme & Stylesheet
"""
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets").replace("\\", "/")
CHEVRON_DOWN = f"{ASSETS_DIR}/chevron_down.png"
CHEVRON_ACTIVE = f"{ASSETS_DIR}/chevron_down_active.png"

QSS_THEME_RAW = """
/* Global Reset */
QWidget {
    font-family: 'Pretendard', 'Segoe UI', 'Malgun Gothic', -apple-system, sans-serif;
    font-size: 13px;
    color: #0F172A;
    background-color: #F8FAFC;
    selection-background-color: #6366F1;
    selection-color: #FFFFFF;
}

QLabel {
    border: none;
    background: transparent;
}

/* Main Window */
QMainWindow {
    background-color: #F1F5F9;
}

/* Menu Bar */
QMenuBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 500;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 6px;
    color: #334155;
}
QMenuBar::item:selected {
    background-color: #EEF2FF;
    color: #4F46E5;
}
QMenu {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 6px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 6px;
    font-size: 12px;
}
QMenu::item:selected {
    background-color: #EEF2FF;
    color: #4F46E5;
}
QMenu::separator {
    height: 1px;
    background-color: #F1F5F9;
    margin: 4px 6px;
}

/* ToolBar - Modern Pill Floating Style */
QToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    spacing: 8px;
    padding: 8px 14px;
}
QToolButton {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 600;
    color: #334155;
}
QToolButton:hover {
    background-color: #EEF2FF;
    border-color: #C7D2FE;
    color: #4F46E5;
}
QToolButton:pressed {
    background-color: #E0E7FF;
    border-color: #818CF8;
}
QToolButton:disabled {
    background-color: #F8FAFC;
    border-color: #F1F5F9;
    color: #94A3B8;
}

/* Path & Breadcrumb Bar */
QFrame#NavFrame {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 6px 14px;
}
QLineEdit#PathEdit {
    background-color: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    color: #334155;
    font-weight: 500;
}
QLineEdit#PathEdit:focus {
    border-color: #6366F1;
    background-color: #FFFFFF;
}

/* Efficiency Stats Banner */
QFrame#StatsBanner {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EEF2FF, stop:1 #E0F2FE);
    border-bottom: 1px solid #C7D2FE;
    padding: 8px 16px;
}
QLabel#StatsTitle {
    font-size: 12px;
    font-weight: 600;
    color: #312E81;
}
QLabel#StatsPill {
    background-color: #FFFFFF;
    border: 1px solid #C7D2FE;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
    color: #4F46E5;
}

/* Search Box */
QLineEdit#SearchBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    min-width: 180px;
}
QLineEdit#SearchBox:focus {
    border-color: #6366F1;
}

/* Table Widget */
QTableWidget {
    background-color: #FFFFFF;
    border: none;
    gridline-color: transparent;
    selection-background-color: #EEF2FF;
    selection-color: #312E81;
    outline: none;
}
QTableWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #F1F5F9;
}
QTableWidget::item:hover {
    background-color: #F8FAFC;
}
QTableWidget::item:selected {
    background-color: #EEF2FF;
    color: #312E81;
    font-weight: 600;
}
QHeaderView::section {
    background-color: #F8FAFC;
    color: #64748B;
    font-weight: 600;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    border-right: 1px solid #F1F5F9;
}

/* Status Bar */
QStatusBar {
    background-color: #FFFFFF;
    border-top: 1px solid #E2E8F0;
    font-size: 12px;
    color: #64748B;
    padding: 4px 12px;
}

/* Buttons */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    color: #334155;
}
QPushButton:hover {
    background-color: #F8FAFC;
    border-color: #94A3B8;
    color: #0F172A;
}
QPushButton:pressed {
    background-color: #F1F5F9;
}
QPushButton#PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #4F46E5);
    border: 1px solid #4338CA;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton#PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #4338CA);
}
QPushButton#PrimaryBtn:pressed {
    background: #3730A3;
}

/* Forms & Inputs */
QLineEdit, QSpinBox {
    background-color: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #0F172A;
}
QLineEdit:focus, QSpinBox:focus {
    border-color: #6366F1;
}

/* Distinctive & Crisp Dropdown Buttons (선명한 윤곽과 세련된 입체 드롭다운 버튼) */
QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F8FAFC);
    border: 1.5px solid #64748B;
    border-radius: 8px;
    padding: 6px 36px 6px 12px;
    font-size: 13px;
    font-weight: 600;
    color: #0F172A;
    min-height: 24px;
}
QComboBox:hover {
    border: 1.5px solid #4F46E5;
    background: #FFFFFF;
}
QComboBox:focus, QComboBox:on {
    border: 2px solid #4338CA;
    background: #FFFFFF;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1.5px solid #64748B;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F8FAFC, stop:1 #E2E8F0);
}
QComboBox:hover::drop-down {
    background: #EEF2FF;
    border-left: 1.5px solid #4F46E5;
}
QComboBox:on::drop-down {
    background: #E0E7FF;
    border-left: 2px solid #4338CA;
}
QComboBox::down-arrow {
    subcontrol-origin: padding;
    subcontrol-position: center;
    image: url('__CHEVRON_DOWN__');
    width: 12px;
    height: 12px;
}
QComboBox::down-arrow:hover, QComboBox::down-arrow:on {
    image: url('__CHEVRON_ACTIVE__');
}

/* ComboBox Dropdown Popup List */
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1.5px solid #64748B;
    border-radius: 8px;
    padding: 4px;
    outline: none;
    selection-background-color: #EEF2FF;
    selection-color: #4F46E5;
}
QComboBox QAbstractItemView::item {
    height: 30px;
    padding: 4px 10px;
    border-radius: 6px;
    color: #1E293B;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #EEF2FF;
    color: #4F46E5;
    font-weight: 700;
}

/* Progress Bar */
QProgressBar {
    background-color: #E2E8F0;
    border: none;
    border-radius: 8px;
    text-align: center;
    color: #0F172A;
    font-weight: 700;
    height: 22px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #06B6D4);
    border-radius: 8px;
}

/* GroupBox */
QGroupBox {
    font-weight: 700;
    font-size: 13px;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 18px;
    background-color: #FFFFFF;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 12px;
    color: #1E293B;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #F8FAFC;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 24px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* Ribbon Bar & Boundary Divider */
QFrame#RibbonBar {
    background-color: #F1F5F9;
}
QFrame#RibbonBottomDivider {
    background-color: #94A3B8;
    border: none;
}
QScrollArea#StartScrollArea, QWidget#StartContainer {
    background-color: #F1F5F9;
}
"""

QSS_THEME = (
    QSS_THEME_RAW
    .replace("__CHEVRON_DOWN__", CHEVRON_DOWN)
    .replace("__CHEVRON_ACTIVE__", CHEVRON_ACTIVE)
)


THEMES = {
    "Aura Indigo (기본 시그니처)": {
        "name": "Aura Indigo",
        "is_dark": False,
        "primary": "#4F46E5",
        "primary_dark": "#4338CA",
        "primary_light": "#6366F1",
        "accent": "#6366F1",
        "subtle_bg": "#EEF2FF",
        "subtle_border": "#C7D2FE",
        "bg_window": "#F1F5F9",
        "bg_canvas": "#F1F5F9",
        "bg_card": "#FFFFFF",
        "bg_ribbon_tab": "#F1F5F9",
        "bg_ribbon_pane": "#FFFFFF",
        "ribbon_divider": "#94A3B8",
        "text_main": "#0F172A",
        "text_secondary": "#334155",
        "text_muted": "#64748B",
        "border_color": "#E2E8F0",
        "border_card": "#E2E8F0",
        "border_card_hover": "#6366F1",
        "btn_hover": "#EEF2FF",
        "btn_hover_border": "#C7D2FE",
        "btn_pressed": "#E0E7FF",
    },
    "Dark Slate (다크 슬레이트 모드)": {
        "name": "Dark Slate",
        "is_dark": True,
        "primary": "#818CF8",
        "primary_dark": "#6366F1",
        "primary_light": "#A5B4FC",
        "accent": "#38BDF8",
        "subtle_bg": "#334155",
        "subtle_border": "#475569",
        "bg_window": "#0F172A",
        "bg_canvas": "#0F172A",
        "bg_card": "#1E293B",
        "bg_ribbon_tab": "#0F172A",
        "bg_ribbon_pane": "#1E293B",
        "ribbon_divider": "#475569",
        "text_main": "#F8FAFC",
        "text_secondary": "#E2E8F0",
        "text_muted": "#94A3B8",
        "border_color": "#334155",
        "border_card": "#334155",
        "border_card_hover": "#818CF8",
        "btn_hover": "#334155",
        "btn_hover_border": "#6366F1",
        "btn_pressed": "#1E293B",
    },
    "Emerald Mint (에메랄드 민트)": {
        "name": "Emerald Mint",
        "is_dark": False,
        "primary": "#059669",
        "primary_dark": "#047857",
        "primary_light": "#10B981",
        "accent": "#10B981",
        "subtle_bg": "#ECFDF5",
        "subtle_border": "#A7F3D0",
        "bg_window": "#F0FDF4",
        "bg_canvas": "#F0FDF4",
        "bg_card": "#FFFFFF",
        "bg_ribbon_tab": "#E6F7EC",
        "bg_ribbon_pane": "#FFFFFF",
        "ribbon_divider": "#6EE7B7",
        "text_main": "#064E3B",
        "text_secondary": "#065F46",
        "text_muted": "#047857",
        "border_color": "#D1FAE5",
        "border_card": "#D1FAE5",
        "border_card_hover": "#10B981",
        "btn_hover": "#ECFDF5",
        "btn_hover_border": "#A7F3D0",
        "btn_pressed": "#D1FAE5",
    },
    "Sunset Coral (선셋 코랄 모드)": {
        "name": "Sunset Coral",
        "is_dark": False,
        "primary": "#EA580C",
        "primary_dark": "#C2410C",
        "primary_light": "#F97316",
        "accent": "#F97316",
        "subtle_bg": "#FFF7ED",
        "subtle_border": "#FED7AA",
        "bg_window": "#FFF7ED",
        "bg_canvas": "#FFF7ED",
        "bg_card": "#FFFFFF",
        "bg_ribbon_tab": "#FFEDD5",
        "bg_ribbon_pane": "#FFFFFF",
        "ribbon_divider": "#FDBA74",
        "text_main": "#7C2D12",
        "text_secondary": "#9A3412",
        "text_muted": "#C2410C",
        "border_color": "#FFEDD5",
        "border_card": "#FFEDD5",
        "border_card_hover": "#F97316",
        "btn_hover": "#FFF7ED",
        "btn_hover_border": "#FED7AA",
        "btn_pressed": "#FFEDD5",
    }
}


def get_theme_dict(theme_name: str = "Aura Indigo") -> dict:
    """테마 이름에 해당하는 세부 팔레트 딕셔너리 반환"""
    for key, val in THEMES.items():
        if key in theme_name or theme_name in key:
            return val
        if val["name"].lower() in theme_name.lower():
            return val
    return THEMES["Aura Indigo (기본 시그니처)"]


def get_theme_qss(theme_name: str = "Aura Indigo") -> str:
    """테마 이름에 따라 동적으로 최적화된 QSS 스타일시트를 생성"""
    t = get_theme_dict(theme_name)
    primary = t["primary"]
    primary_dark = t["primary_dark"]
    accent = t["accent"]
    subtle_bg = t["subtle_bg"]
    subtle_border = t["subtle_border"]
    bg_main = t["bg_canvas"]
    card_bg = t["bg_card"]
    text_main = t["text_main"]

    qss = (
        QSS_THEME_RAW
        .replace("#4F46E5", primary)
        .replace("#4338CA", primary_dark)
        .replace("#6366F1", accent)
        .replace("#EEF2FF", subtle_bg)
        .replace("#C7D2FE", subtle_border)
        .replace("__CHEVRON_DOWN__", CHEVRON_DOWN)
        .replace("__CHEVRON_ACTIVE__", CHEVRON_ACTIVE)
    )

    if t["is_dark"]:
        qss += f"""
        QWidget {{
            color: {t['text_main']};
            selection-background-color: {t['primary']};
            selection-color: #FFFFFF;
        }}
        QLabel {{
            color: {t['text_main']};
            border: none;
            background: transparent;
        }}
        QLabel#DialogHeader {{
            font-size: 15px;
            font-weight: 700;
            color: {t['text_main']};
        }}
        QMainWindow, QDialog {{
            background-color: {t['bg_window']};
            color: {t['text_main']};
        }}
        QMenuBar {{
            background-color: {t['bg_card']};
            border-bottom: 1px solid {t['border_color']};
            color: {t['text_main']};
        }}
        QMenuBar::item {{
            color: {t['text_secondary']};
            background: transparent;
        }}
        QMenuBar::item:selected {{
            background-color: {t['subtle_bg']};
            color: {t['primary']};
        }}
        QMenu {{
            background-color: {t['bg_card']};
            border: 1px solid {t['border_color']};
            color: {t['text_main']};
        }}
        QMenu::item {{
            color: {t['text_secondary']};
        }}
        QMenu::item:selected {{
            background-color: {t['subtle_bg']};
            color: {t['primary']};
        }}
        QStatusBar {{
            background-color: {t['bg_card']};
            border-top: 1px solid {t['border_color']};
            color: {t['text_muted']};
        }}
        QFrame#StatsBanner {{
            background-color: {t['bg_card']};
            border-bottom: 1px solid {t['border_color']};
        }}
        QLabel#StatsTitle {{
            color: {t['text_main']};
        }}
        QLabel#StatsPill {{
            background-color: {t['subtle_bg']};
            border: 1px solid {t['border_color']};
            color: {t['primary']};
        }}
        QFrame#NavFrame {{
            background-color: {t['bg_window']};
            border-bottom: 1px solid {t['border_color']};
        }}
        QLineEdit#PathEdit {{
            background-color: {t['bg_card']};
            border: 1px solid {t['border_color']};
            color: {t['text_main']};
        }}
        QLineEdit#PathEdit:focus {{
            border-color: {t['primary']};
            background-color: {t['bg_window']};
        }}
        QLineEdit#SearchBox {{
            background-color: {t['bg_card']};
            border: 1px solid {t['border_color']};
            color: {t['text_main']};
        }}
        QLineEdit#SearchBox:focus {{
            border-color: {t['primary']};
        }}
        QLineEdit, QSpinBox {{
            background-color: {t['bg_card']};
            border: 1.5px solid {t['border_color']};
            color: {t['text_main']};
        }}
        QLineEdit:focus, QSpinBox:focus {{
            border-color: {t['primary']};
            background-color: {t['bg_window']};
        }}
        QComboBox {{
            background: {t['bg_card']};
            border: 1.5px solid {t['border_color']};
            color: {t['text_main']};
        }}
        QComboBox:hover {{
            border-color: {t['primary']};
        }}
        QComboBox:focus, QComboBox:on {{
            border-color: {t['primary']};
            background: {t['bg_window']};
        }}
        QComboBox::drop-down {{
            background: {t['subtle_bg']};
            border-left: 1.5px solid {t['border_color']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {t['bg_card']};
            border: 1.5px solid {t['border_color']};
            color: {t['text_main']};
            selection-background-color: {t['subtle_bg']};
            selection-color: {t['primary']};
        }}
        QComboBox QAbstractItemView::item {{
            color: {t['text_main']};
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: {t['subtle_bg']};
            color: {t['primary']};
        }}
        QPushButton {{
            background-color: {t['subtle_bg']};
            color: {t['text_main']};
            border: 1px solid {t['border_color']};
        }}
        QPushButton:hover {{
            background-color: #475569;
            border-color: {t['primary']};
        }}
        QPushButton#PrimaryBtn {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t['primary_light']}, stop:1 {t['primary']});
            color: #FFFFFF;
            border: none;
        }}
        QTableWidget {{
            background-color: {t['bg_card']};
            color: {t['text_main']};
            gridline-color: {t['border_color']};
            border: none;
        }}
        QHeaderView::section {{
            background-color: {t['bg_window']};
            color: {t['text_muted']};
            border-bottom: 1px solid {t['border_color']};
            border-right: 1px solid {t['border_color']};
        }}
        QTableWidget::item:selected {{
            background-color: {t['subtle_bg']};
            color: {t['primary']};
        }}
        QScrollBar:vertical {{
            background: {t['bg_window']};
        }}
        QScrollBar::handle:vertical {{
            background: {t['subtle_border']};
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t['primary']};
        }}
        QScrollArea#StartScrollArea, QWidget#StartContainer {{
            background-color: {t['bg_canvas']};
        }}
        """
    else:
        # Light theme variants (Emerald, Sunset, Aura Indigo)
        qss += f"""
        QLabel#DialogHeader {{
            font-size: 15px;
            font-weight: 700;
            color: {t['text_main']};
        }}
        QMainWindow, QDialog {{
            background-color: {bg_main};
        }}
        QScrollArea#StartScrollArea, QWidget#StartContainer {{
            background-color: {bg_main};
        }}
        QFrame#StatsBanner {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t['subtle_bg']}, stop:1 {t['bg_window']});
            border-bottom: 1px solid {t['border_color']};
        }}
        QLabel#StatsTitle {{
            color: {t['text_main']};
        }}
        QLabel#StatsPill {{
            background-color: {t['bg_card']};
            border: 1px solid {t['border_color']};
            color: {t['primary']};
        }}
        QFrame#NavFrame {{
            background-color: {t['bg_window']};
            border-bottom: 1px solid {t['border_color']};
        }}
        QPushButton#PrimaryBtn {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t['primary_light']}, stop:1 {primary});
            color: #FFFFFF;
        }}
        QPushButton#PrimaryBtn:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {primary}, stop:1 {primary_dark});
        }}
        """
    return qss


def apply_theme_to_app(app, theme_name: str):
    """지정된 테마를 앱 전체에 즉시 적용"""
    qss = get_theme_qss(theme_name)
    app.setStyleSheet(qss)
