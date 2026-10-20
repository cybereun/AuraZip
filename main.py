import os
import sys
import ctypes

# 윈도우 환경에서 실행 시 까만 터미널/콘솔 창을 백그라운드로 즉시 완전 은폐 및 작업 표시줄 아이콘 AppUserModelID 설정
if sys.platform == "win32":
    try:
        # 작업 표시줄 아이콘 분리 방지 및 전용 아이콘 표시를 위한 고유 AppID 등록
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AuraStudios.AuraZip.App.1.0.0")
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
    except Exception:
        pass

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from version import APP_NAME, APP_VERSION
from main_window import MainWindow
from theme import QSS_THEME


def main():
    # High DPI modern scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Aura Studios")

    # Set Application Icon
    asset_dir = os.path.join(os.path.dirname(__file__), "assets")
    icon_path = os.path.join(asset_dir, "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        png_path = os.path.join(asset_dir, "app_icon.png")
        if os.path.exists(png_path):
            app.setWindowIcon(QIcon(png_path))

    # Apply Next-Gen QSS Theme
    app.setStyleSheet(QSS_THEME)

    # Initial archive from command line if any
    initial_file = None
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        initial_file = sys.argv[1]

    window = MainWindow(initial_archive=initial_file)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
