import os
import sys
import json
import re
import tempfile
import subprocess
import urllib.request
import urllib.error

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QMessageBox, QFrame, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont, QPixmap

from version import APP_NAME, APP_VERSION, GITHUB_API_LATEST


def parse_version(v_str: str):
    """'v1.0.1' -> (1, 0, 1) tuple"""
    clean = re.sub(r'^[vV]', '', v_str.strip())
    parts = []
    for p in clean.split('.'):
        digits = re.match(r'\d+', p)
        if digits:
            parts.append(int(digits.group(0)))
        else:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def is_newer_version(remote_v: str, local_v: str) -> bool:
    try:
        return parse_version(remote_v) > parse_version(local_v)
    except Exception:
        return False


class CheckUpdateThread(QThread):
    update_found = Signal(dict)
    no_update = Signal(str)
    check_error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            req = urllib.request.Request(
                GITHUB_API_LATEST,
                headers={"User-Agent": f"{APP_NAME}-Updater/{APP_VERSION}"}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.status != 200:
                    self.check_error.emit(f"HTTP {response.status}")
                    return
                data = json.loads(response.read().decode("utf-8"))

            tag_name = data.get("tag_name", "")
            if not tag_name:
                self.no_update.emit(APP_VERSION)
                return

            if is_newer_version(tag_name, APP_VERSION):
                # Find installer asset (.exe)
                assets = data.get("assets", [])
                download_url = None
                asset_name = ""
                asset_size = 0

                # Prefer AuraZip_Setup*.exe or any .exe
                for a in assets:
                    name = a.get("name", "")
                    if name.lower().endswith(".exe") and "setup" in name.lower():
                        download_url = a.get("browser_download_url")
                        asset_name = name
                        asset_size = a.get("size", 0)
                        break

                if not download_url:
                    for a in assets:
                        name = a.get("name", "")
                        if name.lower().endswith(".exe"):
                            download_url = a.get("browser_download_url")
                            asset_name = name
                            asset_size = a.get("size", 0)
                            break

                info = {
                    "tag_name": tag_name,
                    "title": data.get("name", tag_name),
                    "body": data.get("body", "새로운 버전이 출시되었습니다."),
                    "download_url": download_url,
                    "asset_name": asset_name,
                    "asset_size": asset_size,
                    "html_url": data.get("html_url", "")
                }
                self.update_found.emit(info)
            else:
                self.no_update.emit(APP_VERSION)

        except urllib.error.HTTPError as e:
            if e.code == 404:
                # No release yet
                self.no_update.emit(APP_VERSION)
            else:
                self.check_error.emit(f"서버 응답 오류 (HTTP {e.code})")
        except Exception as e:
            self.check_error.emit(str(e))


class DownloadUpdateThread(QThread):
    progress = Signal(int, int, int)  # percent, downloaded, total
    finished = Signal(str)           # local file path
    failed = Signal(str)

    def __init__(self, url: str, asset_name: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.asset_name = asset_name
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            temp_dir = tempfile.gettempdir()
            filename = self.asset_name if self.asset_name else "AuraZip_Setup_Update.exe"
            target_path = os.path.join(temp_dir, filename)

            req = urllib.request.Request(
                self.url,
                headers={"User-Agent": f"{APP_NAME}-Updater/{APP_VERSION}"}
            )

            with urllib.request.urlopen(req, timeout=30) as resp, open(target_path, "wb") as out_file:
                total_size = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                block_size = 65536  # 64KB

                while not self._is_cancelled:
                    chunk = resp.read(block_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = int((downloaded / total_size) * 100)
                        self.progress.emit(pct, downloaded, total_size)

            if self._is_cancelled:
                if os.path.exists(target_path):
                    try:
                        os.remove(target_path)
                    except Exception:
                        pass
                self.failed.emit("다운로드가 취소되었습니다.")
                return

            self.finished.emit(target_path)
        except Exception as e:
            self.failed.emit(f"다운로드 실패: {str(e)}")


class UpdateDialog(QDialog):
    def __init__(self, update_info: dict, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.download_thread = None

        self.setWindowTitle(f"{APP_NAME} 소프트웨어 업데이트")
        self.setFixedSize(520, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        asset_dir = os.path.join(os.path.dirname(__file__), "assets")
        icon_path = os.path.join(asset_dir, "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header with Icon and Version Info
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        asset_dir = os.path.join(os.path.dirname(__file__), "assets")
        png_icon = os.path.join(asset_dir, "app_icon.png")
        icon_lbl = QLabel()
        if os.path.exists(png_icon):
            icon_lbl.setPixmap(QPixmap(png_icon).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_lbl.setFixedSize(64, 64)
        header_layout.addWidget(icon_lbl)

        v_layout = QVBoxLayout()
        v_layout.setSpacing(4)
        title_lbl = QLabel(f"<b>새로운 {APP_NAME} 업데이트가 있습니다!</b>")
        title_lbl.setStyleSheet("font-size: 15px; color: #1E293B; font-weight: bold;")
        v_layout.addWidget(title_lbl)

        cur_v = APP_VERSION
        new_v = self.update_info.get("tag_name", "")
        ver_lbl = QLabel(f"현재 버전: <span style='color:#64748B;'>{cur_v}</span>  ➔  최신 버전: <b style='color:#4F46E5;'>{new_v}</b>")
        ver_lbl.setStyleSheet("font-size: 12px;")
        v_layout.addWidget(ver_lbl)

        rel_title = self.update_info.get("title", "")
        if rel_title and rel_title != new_v:
            t_lbl = QLabel(f"릴리즈: {rel_title}")
            t_lbl.setStyleSheet("font-size: 11px; color: #475569;")
            v_layout.addWidget(t_lbl)

        header_layout.addLayout(v_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(line)

        # Release Notes Label & Text
        notes_lbl = QLabel("업데이트 주요 변경 사항:")
        notes_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #334155;")
        layout.addWidget(notes_lbl)

        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setPlainText(self.update_info.get("body", "세부 릴리즈 노트가 없습니다."))
        self.notes_text.setStyleSheet("""
            QTextEdit {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Malgun Gothic', 'Segoe UI', sans-serif;
                font-size: 11px;
                color: #334155;
            }
        """)
        layout.addWidget(self.notes_text)

        # Progress Section (Initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #CBD5E1;
                border-radius: 5px;
                text-align: center;
                height: 20px;
                font-size: 11px;
                font-weight: bold;
                color: #1E293B;
                background-color: #F1F5F9;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06B6D4, stop:1 #6366F1);
                border-radius: 4px;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #64748B;")
        self.status_lbl.setVisible(False)
        layout.addWidget(self.status_lbl)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.btn_later = QPushButton("나중에")
        self.btn_later.setCursor(Qt.PointingHandCursor)
        self.btn_later.setFixedHeight(34)
        self.btn_later.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 12px;
                color: #475569;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #1E293B;
            }
        """)
        self.btn_later.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_later)

        self.btn_update = QPushButton("지금 업데이트 및 재시작")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.setFixedHeight(34)
        self.btn_update.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
                border: none;
                border-radius: 6px;
                padding: 0 18px;
                font-size: 12px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338CA, stop:1 #0891B2);
            }
            QPushButton:disabled {
                background-color: #94A3B8;
            }
        """)
        self.btn_update.clicked.connect(self._start_download)
        btn_layout.addWidget(self.btn_update)

        layout.addLayout(btn_layout)

    def _start_download(self):
        download_url = self.update_info.get("download_url")
        if not download_url:
            # Fallback: Open browser if no direct .exe asset
            html_url = self.update_info.get("html_url")
            if html_url:
                import webbrowser
                webbrowser.open(html_url)
            else:
                QMessageBox.warning(self, "업데이트 안내", "직접 다운로드할 수 있는 설치 파일이 없습니다. 릴리즈 페이지를 확인해주세요.")
            self.accept()
            return

        self.btn_update.setEnabled(False)
        self.btn_later.setEnabled(False)
        self.btn_update.setText("다운로드 중...")
        self.progress_bar.setVisible(True)
        self.status_lbl.setVisible(True)
        self.status_lbl.setText("업데이트 설치 파일을 다운로드하고 있습니다...")

        asset_name = self.update_info.get("asset_name", "AuraZip_Setup_Update.exe")
        self.download_thread = DownloadUpdateThread(download_url, asset_name, self)
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.finished.connect(self._on_finished)
        self.download_thread.failed.connect(self._on_failed)
        self.download_thread.start()

    def _on_progress(self, pct, downloaded, total):
        self.progress_bar.setValue(pct)
        mb_down = downloaded / (1024 * 1024)
        if total > 0:
            mb_tot = total / (1024 * 1024)
            self.status_lbl.setText(f"다운로드 중: {mb_down:.1f} MB / {mb_tot:.1f} MB ({pct}%)")
        else:
            self.status_lbl.setText(f"다운로드 중: {mb_down:.1f} MB")

    def _on_finished(self, target_path):
        self.status_lbl.setText("다운로드 완료! 설치 프로그램을 시작하고 AuraZip을 재시작합니다...")
        self.progress_bar.setValue(100)

        # Launch the installer executable
        try:
            # Inno Setup flags: /CLOSEAPPLICATIONS tells installer to close current app if running
            subprocess.Popen([target_path, "/CLOSEAPPLICATIONS"])
        except Exception as e:
            QMessageBox.critical(self, "실행 오류", f"설치 프로그램 실행 중 오류가 발생했습니다:\n{str(e)}")
            self.reject()
            return

        # Quit AuraZip cleanly
        QApplication.quit()
        sys.exit(0)

    def _on_failed(self, err_msg):
        self.btn_update.setEnabled(True)
        self.btn_later.setEnabled(True)
        self.btn_update.setText("재시도")
        self.status_lbl.setText(f"<font color='#EF4444'>{err_msg}</font>")
        QMessageBox.warning(self, "다운로드 실패", err_msg)


class AutoUpdater:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.check_thread = None

    def check(self, silent=True):
        self.silent = silent
        self.check_thread = CheckUpdateThread(self.parent)
        self.check_thread.update_found.connect(self._on_update_found)
        self.check_thread.no_update.connect(self._on_no_update)
        self.check_thread.check_error.connect(self._on_check_error)
        self.check_thread.start()

    def _on_update_found(self, info):
        dialog = UpdateDialog(info, self.parent)
        dialog.exec()

    def _on_no_update(self, cur_ver):
        if not self.silent:
            QMessageBox.information(
                self.parent,
                "업데이트 확인",
                f"현재 최신 버전({cur_ver})을 사용하고 있습니다.\n새로운 업데이트가 없습니다."
            )

    def _on_check_error(self, err):
        if not self.silent:
            QMessageBox.warning(
                self.parent,
                "업데이트 확인 실패",
                f"업데이트 정보를 확인하는 중 네트워크 오류가 발생했습니다:\n{err}"
            )
