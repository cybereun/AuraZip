import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QFileDialog, QComboBox, QListWidget, QListWidgetItem,
    QProgressBar, QGroupBox, QMessageBox, QFrame, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap

from version import APP_VERSION


def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


class PasswordDialog(QDialog):
    def __init__(self, parent=None, title="보안 암호 입력"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(380, 180)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title_lbl = QLabel("🔒 암호화된 아카이브")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E1B4B;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel("내용을 열람하거나 압축을 풀려면 암호를 입력하세요:")
        desc_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        layout.addWidget(desc_lbl)

        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.Password)
        self.pw_edit.setPlaceholderText("비밀번호 입력")
        layout.addWidget(self.pw_edit)

        self.show_cb = QCheckBox("암호 문자 표시")
        self.show_cb.toggled.connect(self._toggle_show)
        layout.addWidget(self.show_cb)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.ok_btn = QPushButton("확인")
        self.ok_btn.setObjectName("PrimaryBtn")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.ok_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addLayout(btn_box)

    def _toggle_show(self, checked):
        self.pw_edit.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

    def get_password(self) -> str:
        return self.pw_edit.text()


class ExtractDialog(QDialog):
    def __init__(self, archive_path: str, parent=None):
        super().__init__(parent)
        self.archive_path = archive_path
        self.setWindowTitle("스마트 압축 풀기 - AuraZip")
        self.resize(540, 280)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 22, 22, 22)

        header_lbl = QLabel(f"📦 {os.path.basename(archive_path)} 압축 풀기")
        header_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E1B4B;")
        layout.addWidget(header_lbl)

        # Dest folder
        path_group = QGroupBox("압축 해제 대상 경로")
        path_layout = QHBoxLayout(path_group)
        self.path_edit = QLineEdit()
        default_dir = os.path.dirname(os.path.abspath(archive_path))
        self.path_edit.setText(default_dir)
        browse_btn = QPushButton("폴더 선택...")
        browse_btn.clicked.connect(self._browse)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        layout.addWidget(path_group)

        # Options
        opt_group = QGroupBox("스마트 추출 옵션")
        opt_layout = QVBoxLayout(opt_group)
        self.smart_cb = QCheckBox("스마트 풀기 (최상위 파일이 여러 개면 아카이브 폴더 생성 후 풀기)")
        self.smart_cb.setChecked(True)
        self.open_cb = QCheckBox("완료 후 대상 폴더 열기")
        self.open_cb.setChecked(True)
        opt_layout.addWidget(self.smart_cb)
        opt_layout.addWidget(self.open_cb)
        layout.addWidget(opt_group)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.ok_btn = QPushButton("압축 해제 시작")
        self.ok_btn.setObjectName("PrimaryBtn")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.ok_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addLayout(btn_box)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "압축 해제 폴더 선택", self.path_edit.text())
        if d:
            self.path_edit.setText(d)

    def get_dest_dir(self) -> str:
        return self.path_edit.text().strip()

    def is_smart_extract(self) -> bool:
        return self.smart_cb.isChecked()

    def should_open_folder(self) -> bool:
        return self.open_cb.isChecked()


class CreateDialog(QDialog):
    def __init__(self, initial_files=None, initial_secure=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("새 아카이브 압축 - AuraZip")
        self.resize(620, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 22, 22, 22)

        header_lbl = QLabel("⚡ 새로운 아카이브 패키징")
        header_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E1B4B;")
        layout.addWidget(header_lbl)

        # Dest path
        dest_group = QGroupBox("생성할 압축 파일 위치")
        dest_layout = QHBoxLayout(dest_group)
        self.dest_edit = QLineEdit()
        default_save = os.path.join(os.path.expanduser("~"), "Desktop", "AuraArchive.zip")
        self.dest_edit.setText(default_save)
        browse_btn = QPushButton("저장 위치...")
        browse_btn.clicked.connect(self._browse_save)
        dest_layout.addWidget(self.dest_edit)
        dest_layout.addWidget(browse_btn)
        layout.addWidget(dest_group)

        # Files list
        file_group = QGroupBox("압축 대상 파일 및 폴더")
        file_layout = QVBoxLayout(file_group)
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 6px; padding: 4px;")
        file_layout.addWidget(self.file_list)

        btn_row = QHBoxLayout()
        add_file_btn = QPushButton("📄 파일 추가...")
        add_file_btn.clicked.connect(self._add_files)
        add_dir_btn = QPushButton("📁 폴더 추가...")
        add_dir_btn.clicked.connect(self._add_folder)
        del_btn = QPushButton("선택 삭제")
        del_btn.clicked.connect(self._delete_selected)
        btn_row.addWidget(add_file_btn)
        btn_row.addWidget(add_dir_btn)
        btn_row.addStretch()
        btn_row.addWidget(del_btn)
        file_layout.addLayout(btn_row)
        layout.addWidget(file_group)

        # Compression Presets & Format
        opt_group = QGroupBox("압축 프리셋 및 보안")
        opt_layout = QHBoxLayout(opt_group)

        # Format
        fmt_layout = QVBoxLayout()
        fmt_layout.addWidget(QLabel("포맷:"))
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["ZIP (범용 호환)", "7Z (초고압축)", "TAR (단순 보관)", "TGZ (Gzip)"])
        self.fmt_combo.currentIndexChanged.connect(self._on_format_changed)
        fmt_layout.addWidget(self.fmt_combo)
        opt_layout.addLayout(fmt_layout, 2)

        # Level Preset
        lvl_layout = QVBoxLayout()
        lvl_layout.addWidget(QLabel("압축 프로필:"))
        self.lvl_combo = QComboBox()
        self.lvl_combo.addItems(["⚖️ 밸런스 추천 (Level 5)", "🚀 초고속 백업 (Level 1)", "💎 울트라 압축 (Level 9)", "📦 무압축 저장 (Level 0)"])
        lvl_layout.addWidget(self.lvl_combo)
        opt_layout.addLayout(lvl_layout, 3)

        # Security
        sec_layout = QVBoxLayout()
        sec_layout.addWidget(QLabel("보안 암호 (AES-256):"))
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.Password)
        self.pw_edit.setPlaceholderText("미설정 시 암호 없음")
        sec_layout.addWidget(self.pw_edit)
        opt_layout.addLayout(sec_layout, 2)

        layout.addWidget(opt_group)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.ok_btn = QPushButton("압축 실행")
        self.ok_btn.setObjectName("PrimaryBtn")
        self.ok_btn.clicked.connect(self._validate_and_accept)
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.ok_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addLayout(btn_box)

        if initial_files:
            for f in initial_files:
                self.add_path(f)

        if initial_secure:
            self.pw_edit.setFocus()

    def _on_format_changed(self, idx):
        cur_path = self.dest_edit.text()
        exts = [".zip", ".7z", ".tar", ".tgz"]
        target_ext = exts[idx]
        base, _ = os.path.splitext(cur_path)
        if base.lower().endswith('.tar'):
            base = os.path.splitext(base)[0]
        self.dest_edit.setText(base + target_ext)

    def _browse_save(self):
        ext_filters = "ZIP 아카이브 (*.zip);;7Z 아카이브 (*.7z);;TAR 아카이브 (*.tar);;TGZ 아카이브 (*.tgz);;모든 파일 (*.*)"
        path, _ = QFileDialog.getSaveFileName(self, "아카이브 저장 위치", self.dest_edit.text(), ext_filters)
        if path:
            self.dest_edit.setText(path)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "파일 선택")
        for f in files:
            self.add_path(f)

    def _add_folder(self):
        d = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if d:
            self.add_path(d)

    def add_path(self, path: str):
        path = os.path.abspath(path)
        for i in range(self.file_list.count()):
            if self.file_list.item(i).text() == path:
                return
        self.file_list.addItem(path)

    def _delete_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def _validate_and_accept(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "알림", "압축할 파일 또는 폴더를 하나 이상 추가해 주세요.")
            return
        dest = self.dest_edit.text().strip()
        if not dest:
            QMessageBox.warning(self, "알림", "저장할 압축 파일 위치를 지정해 주세요.")
            return
        self.accept()

    def get_dest_path(self) -> str:
        return self.dest_edit.text().strip()

    def get_source_paths(self) -> list:
        return [self.file_list.item(i).text() for i in range(self.file_list.count())]

    def get_format(self) -> str:
        return ["ZIP", "7Z", "TAR", "TGZ"][self.fmt_combo.currentIndex()]

    def get_level(self) -> int:
        levels = [5, 1, 9, 0]
        return levels[self.lvl_combo.currentIndex()]

    def get_password(self) -> str:
        return self.pw_edit.text().strip() or None


class ProgressDialog(QDialog):
    cancelled = Signal()

    def __init__(self, title="작업 진행 중", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(500, 190)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 22, 22, 22)

        self.status_lbl = QLabel("처리 대기 중...")
        self.status_lbl.setStyleSheet("font-weight: 700; font-size: 14px; color: #1E1B4B;")
        layout.addWidget(self.status_lbl)

        self.file_lbl = QLabel("")
        self.file_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(self.file_lbl)

        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        layout.addWidget(self.prog_bar)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.cancel_btn = QPushButton("작업 취소")
        self.cancel_btn.clicked.connect(self._on_cancel)
        btn_box.addWidget(self.cancel_btn)
        layout.addLayout(btn_box)

    def update_progress(self, current_name: str, proc_bytes: int, total_bytes: int):
        self.file_lbl.setText(current_name)
        if total_bytes > 0:
            pct = int((proc_bytes / total_bytes) * 100)
            self.prog_bar.setValue(min(100, pct))
            self.status_lbl.setText(f"진행 중: {format_bytes(proc_bytes)} / {format_bytes(total_bytes)} ({pct}%)")
        else:
            self.prog_bar.setValue(0)
            self.status_lbl.setText("처리 중...")

    def _on_cancel(self):
        self.cancel_btn.setEnabled(False)
        self.status_lbl.setText("작업을 중단하는 중입니다...")
        self.cancelled.emit()


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AuraZip 정보")
        self.setFixedSize(500, 340)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(26, 24, 26, 24)

        header_layout = QHBoxLayout()
        icon_lbl = QLabel()
        asset_ico = os.path.join(os.path.dirname(__file__), "assets", "app_icon.png")
        if os.path.exists(asset_ico):
            pix = QPixmap(asset_ico).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_lbl.setPixmap(pix)
        header_layout.addWidget(icon_lbl)

        info_layout = QVBoxLayout()
        title_lbl = QLabel("AuraZip")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: #4F46E5;")
        ver_lbl = QLabel(f"버전 {APP_VERSION} (Aura Next-Gen Core)")
        ver_lbl.setStyleSheet("color: #64748B; font-weight: 600; font-size: 12px;")
        author_lbl = QLabel("제작자: @2026Lebi")
        author_lbl.setStyleSheet("color: #4F46E5; font-weight: 700; font-size: 13px;")

        info_layout.addWidget(title_lbl)
        info_layout.addWidget(ver_lbl)
        info_layout.addWidget(author_lbl)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        desc_lbl = QLabel(
            "AuraZip은 초고속 멀티포맷 압축 및 군사 표준 보안을 지원하는 차세대 압축 유틸리티입니다.\n\n"
            "• 지원 포맷: ZIP, 7Z, TAR, TGZ, TBZ2, TXZ, GZ\n"
            "• 보안 규격: AES-256 비트 군사 표준 암호화 지원\n"
            "• 핵심 기능: 스마트 폴더 자동 추출, 실시간 검색, 용량 절약 대시보드\n"
            "• 저작권: Copyright © 2026 @2026Lebi. All rights reserved."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #334155; font-size: 12px; line-height: 1.6;")
        layout.addWidget(desc_lbl)

        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        ok_btn = QPushButton("확인")
        ok_btn.setObjectName("PrimaryBtn")
        ok_btn.setFixedWidth(90)
        ok_btn.clicked.connect(self.accept)
        btn_box.addWidget(ok_btn)
        layout.addLayout(btn_box)
