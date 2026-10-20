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
    image: url('__CHEVRON_DOWN__');
    width: 13px;
    height: 13px;
}
QComboBox:hover::down-arrow, QComboBox:on::down-arrow {
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


def get_theme_qss(theme_name: str = "Aura Indigo") -> str:
    """테마 이름에 따라 동적으로 QSS 스타일시트를 생성"""
    primary = "#4F46E5"
    primary_dark = "#4338CA"
    accent = "#6366F1"
    subtle_bg = "#EEF2FF"
    subtle_border = "#C7D2FE"
    bg_main = "#F1F5F9"
    bg_widget = "#F8FAFC"
    text_main = "#0F172A"
    card_bg = "#FFFFFF"

    if "Dark Slate" in theme_name:
        primary = "#818CF8"
        primary_dark = "#6366F1"
        accent = "#A5B4FC"
        subtle_bg = "#334155"
        subtle_border = "#475569"
        bg_main = "#0F172A"
        bg_widget = "#1E293B"
        text_main = "#F8FAFC"
        card_bg = "#1E293B"
    elif "Emerald Mint" in theme_name:
        primary = "#059669"
        primary_dark = "#047857"
        accent = "#10B981"
        subtle_bg = "#ECFDF5"
        subtle_border = "#A7F3D0"
        bg_main = "#F0FDF4"
        bg_widget = "#F8FAFC"
        text_main = "#0F172A"
        card_bg = "#FFFFFF"
    elif "Sunset Coral" in theme_name:
        primary = "#EA580C"
        primary_dark = "#C2410C"
        accent = "#F97316"
        subtle_bg = "#FFF7ED"
        subtle_border = "#FED7AA"
        bg_main = "#FFF7ED"
        bg_widget = "#FFFAF0"
        text_main = "#0F172A"
        card_bg = "#FFFFFF"

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

    if "Dark Slate" in theme_name:
        qss += f"""
        QWidget {{
            background-color: {bg_widget};
            color: {text_main};
        }}
        QMainWindow, QDialog {{
            background-color: {bg_main};
        }}
        QMenuBar, QMenu, QToolBar, QGroupBox, QTableWidget, QListWidget, QTextBrowser {{
            background-color: {card_bg};
            color: {text_main};
            border-color: {subtle_border};
        }}
        QTabBar::tab {{
            color: #94A3B8;
        }}
        QTabBar::tab:selected {{
            color: {accent};
            background-color: {card_bg};
            border-bottom: 2px solid {accent};
        }}
        QLineEdit, QComboBox, QSpinBox {{
            background-color: {card_bg};
            color: {text_main};
            border-color: {subtle_border};
        }}
        QPushButton {{
            background-color: {card_bg};
            color: {text_main};
            border-color: {subtle_border};
        }}
        QPushButton:hover {{
            background-color: {subtle_bg};
        }}
        QFrame#RibbonBar {{
            background-color: #1E293B;
        }}
        QFrame#RibbonBottomDivider {{
            background-color: #475569;
        }}
        QScrollArea#StartScrollArea, QWidget#StartContainer {{
            background-color: #0F172A;
        }}
        """
    return qss


def apply_theme_to_app(app, theme_name: str):
    """지정된 테마를 앱 전체에 즉시 적용"""
    qss = get_theme_qss(theme_name)
    app.setStyleSheet(qss)
