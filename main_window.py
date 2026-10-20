import os
import sys
import ctypes
import shutil
import tempfile
import subprocess
from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QFileDialog, QMessageBox,
    QApplication, QLabel, QMenu, QInputDialog, QFrame
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QAction, QPixmap, QClipboard

from version import APP_NAME, APP_VERSION
from updater import AutoUpdater

from archive_engine import ArchiveEngine, ArchiveItem
from start_view import StartView
from archive_view import ArchiveView
from ribbon import RibbonBar
from dialogs import (
    PasswordDialog, ExtractDialog, CreateDialog, ProgressDialog, AboutDialog, format_bytes
)
from extra_tools import (
    CommentDialog, RepairDialog, PasswordRecoveryDialog, MalwareScanDialog, ColorThemeDialog
)
from help_dialog import HelpDialog
from theme import apply_theme_to_app
from workers import ExtractWorker, CompressWorker, TestWorker


class MainWindow(QMainWindow):
    def __init__(self, initial_archive: str = None):
        super().__init__()
        self.current_archive_path: str = ""
        self.archive_items: list = []
        self.recent_files: list = []
        self.asset_dir = os.path.join(os.path.dirname(__file__), "assets")

        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1020, 740)
        self.setMinimumSize(780, 520)

        # Window Icon
        app_icon = os.path.join(self.asset_dir, "app_icon.ico")
        if os.path.exists(app_icon):
            self.setWindowIcon(QIcon(app_icon))
        else:
            png_icon = os.path.join(self.asset_dir, "app_icon.png")
            if os.path.exists(png_icon):
                self.setWindowIcon(QIcon(png_icon))

        self.setAcceptDrops(True)

        self._setup_ribbon()
        self._setup_central_widget()
        self._setup_statusbar()
        self._setup_shortcuts()

        self._update_ui_state(has_archive=False)

        # Auto Updater Setup (백그라운드에서 실행 2.5초 후 새 버전 자동 확인)
        self.updater = AutoUpdater(self)
        QTimer.singleShot(2500, lambda: self.updater.check(silent=True))

        if initial_archive and os.path.exists(initial_archive):
            self.open_archive(initial_archive)

    def _setup_ribbon(self):
        self.ribbon = RibbonBar(self)
        self.setMenuWidget(self.ribbon)

        # 1. File Tab Connections
        self.ribbon.btn_new.clicked.connect(lambda: self._on_create_archive(is_secure=False))
        self.ribbon.btn_open.clicked.connect(self._on_open_archive_dialog)
        self.ribbon.btn_extract.clicked.connect(self._on_extract_archive)
        self.ribbon.btn_close.clicked.connect(self._close_archive)
        self.ribbon.btn_save_as.clicked.connect(self._on_save_as)
        self.ribbon.btn_open_folder.clicked.connect(self._on_open_containing_folder)
        self.ribbon.btn_del_archive.clicked.connect(lambda: self._on_delete_archive_file(permanent=False))
        self.ribbon.btn_purge_archive.clicked.connect(lambda: self._on_delete_archive_file(permanent=True))
        self.ribbon.btn_new_window.clicked.connect(self._on_new_window)
        self.ribbon.btn_admin_window.clicked.connect(self._on_admin_window)
        self.ribbon.btn_exit.clicked.connect(self.close)

        # 2. Edit Tab Connections
        self.ribbon.btn_add_file.clicked.connect(self._on_add_files)
        self.ribbon.btn_del_file.clicked.connect(self._on_delete_items)
        self.ribbon.btn_rename.clicked.connect(self._on_rename_item)
        self.ribbon.btn_clip_copy.clicked.connect(self._on_copy_to_clipboard)
        self.ribbon.btn_clip_paste.clicked.connect(self._on_paste_from_clipboard)
        self.ribbon.btn_clip_path.clicked.connect(self._on_copy_paths_to_clipboard)
        self.ribbon.btn_comment.clicked.connect(self._on_edit_comment)
        self.ribbon.btn_select_all.clicked.connect(lambda: self.archive_view.table.selectAll())
        self.ribbon.btn_invert_sel.clicked.connect(self._on_invert_selection)

        # 3. Tools Tab Connections
        self.ribbon.btn_test.clicked.connect(self._on_test_archive)
        self.ribbon.btn_scan.clicked.connect(self._on_malware_scan)
        self.ribbon.btn_repair.clicked.connect(self._on_repair_archive)
        self.ribbon.btn_recover_pw.clicked.connect(self._on_recover_password)
        self.ribbon.btn_find.clicked.connect(self._on_find_files)
        self.ribbon.btn_default_app.clicked.connect(self._on_open_default_apps_settings)

        # 4. View Tab Connections
        self.ribbon.btn_toggle_start.clicked.connect(self._on_toggle_start_view)
        self.ribbon.btn_toggle_nav.clicked.connect(self._on_toggle_nav_bar)
        self.ribbon.btn_toggle_status.clicked.connect(self._on_toggle_status_bar)
        self.ribbon.btn_comment_view.clicked.connect(self._on_view_comment)
        self.ribbon.btn_img_preview.clicked.connect(self._on_toggle_img_preview)
        self.ribbon.btn_always_on_top.clicked.connect(self._on_toggle_always_on_top)
        self.ribbon.btn_color.clicked.connect(self._on_color_theme)

        # 5. Help Tab Connections
        self.ribbon.btn_about.clicked.connect(self._show_about)
        self.ribbon.btn_open_install_dir.clicked.connect(self._on_open_install_dir)
        self.ribbon.btn_help_page.clicked.connect(self._on_open_help_page)
        self.ribbon.btn_check_update.clicked.connect(lambda: self.updater.check(silent=False))

    def _setup_shortcuts(self):
        # Keyboard Shortcuts matching original menus
        def bind(key, slot):
            act = QAction(self)
            act.setShortcut(key)
            act.triggered.connect(slot)
            self.addAction(act)

        bind("Ctrl+N", lambda: self._on_create_archive(is_secure=False))
        bind("Ctrl+O", self._on_open_archive_dialog)
        bind("Ctrl+E", self._on_extract_archive)
        bind("F4", self._close_archive)
        bind("Ctrl+Del", lambda: self._on_delete_archive_file(permanent=False))
        bind("Shift+Ctrl+Del", lambda: self._on_delete_archive_file(permanent=True))
        bind("Ctrl+T", self._on_test_archive)
        bind("Ctrl+I", self._on_malware_scan)
        bind("Ctrl+Shift+N", self._on_new_window)
        bind("Ctrl+Alt+N", self._on_admin_window)
        bind("Ctrl+W", self.close)
        bind("F2", self._on_rename_item)
        bind("Ins", self._on_add_files)
        bind("Delete", self._on_delete_items)
        bind("Ctrl+Shift+M", self._on_edit_comment)
        bind("Ctrl+C", self._on_copy_to_clipboard)
        bind("Ctrl+V", self._on_paste_from_clipboard)
        bind("Ctrl+F", self._on_find_files)
        bind("F6", self._on_toggle_start_view)
        bind("F7", self._on_toggle_nav_bar)
        bind("F8", self._on_view_comment)
        bind("F1", self._on_open_help_page)

    def _setup_central_widget(self):
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # Page 0: StartView
        self.start_view = StartView(self)
        self.start_view.open_requested.connect(self._on_open_archive_dialog)
        self.start_view.create_requested.connect(lambda sec: self._on_create_archive(is_secure=sec))
        self.start_view.file_dropped.connect(self.open_archive)
        self.start_view.recent_file_clicked.connect(self.open_archive)
        self.stack.addWidget(self.start_view)

        # Page 1: ArchiveView
        self.archive_view = ArchiveView(self)
        self.archive_view.item_double_clicked.connect(self._on_item_double_clicked)
        self.archive_view.extract_selected.connect(self._on_extract_selected)
        self.archive_view.selection_changed.connect(self._on_selection_changed)
        self.archive_view.image_preview_requested.connect(self._on_image_preview_requested)
        self.stack.addWidget(self.archive_view)

    def _setup_statusbar(self):
        self.status_bar = self.statusBar()
        self.status_lbl_info = QLabel("AuraZip 준비 완료")
        self.status_lbl_stats = QLabel("")
        self.status_bar.addWidget(self.status_lbl_info, 1)
        self.status_bar.addPermanentWidget(self.status_lbl_stats)

    def _update_ui_state(self, has_archive: bool):
        # 모든 리본 버튼을 항상 활성화하여 언제든 자유롭게 접근 및 조작 가능
        self.ribbon.btn_extract.setEnabled(True)
        self.ribbon.btn_close.setEnabled(True)
        self.ribbon.btn_save_as.setEnabled(True)
        self.ribbon.btn_open_folder.setEnabled(True)
        self.ribbon.btn_del_archive.setEnabled(True)
        self.ribbon.btn_purge_archive.setEnabled(True)

        self.ribbon.btn_add_file.setEnabled(True)
        self.ribbon.btn_del_file.setEnabled(True)
        self.ribbon.btn_rename.setEnabled(True)
        self.ribbon.btn_clip_copy.setEnabled(True)
        self.ribbon.btn_clip_paste.setEnabled(True)
        self.ribbon.btn_clip_path.setEnabled(True)
        self.ribbon.btn_comment.setEnabled(True)

        # 도구 & 보안 기능은 아카이브 열림 여부와 무관하게 항상 활성화 (독립 실행 지원)
        self.ribbon.btn_test.setEnabled(True)
        self.ribbon.btn_scan.setEnabled(True)
        self.ribbon.btn_repair.setEnabled(True)
        self.ribbon.btn_recover_pw.setEnabled(True)
        self.ribbon.btn_find.setEnabled(True)

        if not has_archive:
            self.stack.setCurrentIndex(0)
            self.setWindowTitle("AuraZip")
            self.status_lbl_info.setText("아카이브 파일을 열람하거나 새로 압축할 파일을 추가하세요.")
            self.status_lbl_stats.setText("")
        else:
            self.stack.setCurrentIndex(1)
            base_name = os.path.basename(self.current_archive_path)
            self.setWindowTitle(f"{base_name} - AuraZip")

    def _on_selection_changed(self, count, bytes_val):
        if count > 0:
            self.status_lbl_info.setText(f"{count}개 항목 선택됨")
        else:
            self._update_archive_stats()

    def _update_archive_stats(self):
        file_count = sum(1 for it in self.archive_items if not it.is_dir)
        folder_count = sum(1 for it in self.archive_items if it.is_dir)
        total_orig = sum(it.original_size for it in self.archive_items if not it.is_dir)
        total_comp = sum(it.compressed_size for it in self.archive_items if not it.is_dir)
        fmt = ArchiveEngine.get_format(self.current_archive_path)

        ratio = (1.0 - (total_comp / total_orig)) * 100.0 if total_orig > 0 else 0.0

        self.status_lbl_info.setText(f"파일 {file_count}개, 폴더 {folder_count}개")
        self.status_lbl_stats.setText(f"원본: {format_bytes(total_orig)} | 압축: {format_bytes(total_comp)} ({ratio:.0f}% 절약) | 형식: {fmt}")

    def open_archive(self, archive_path: str, password: str = None):
        archive_path = os.path.abspath(archive_path)
        if not os.path.exists(archive_path):
            QMessageBox.critical(self, "오류", f"지정된 파일을 찾을 수 없습니다:\n{archive_path}")
            return

        fmt = ArchiveEngine.get_format(archive_path)
        if fmt == 'UNKNOWN':
            ret = QMessageBox.question(
                self, "압축 파일 아님",
                f"'{os.path.basename(archive_path)}' 파일은 아카이브 형식이 아닙니다.\n이 파일을 새로 압축하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No
            )
            if ret == QMessageBox.Yes:
                self._on_create_archive(initial_files=[archive_path])
            return

        try:
            items = ArchiveEngine.list_items(archive_path, password=password)
            self.current_archive_path = archive_path
            self.archive_items = items
            self.archive_view.set_items(items)
            self._update_ui_state(has_archive=True)
            self._update_archive_stats()

            # Record recent
            if archive_path in self.recent_files:
                self.recent_files.remove(archive_path)
            self.recent_files.insert(0, archive_path)
            self.start_view.update_recent_files(self.recent_files)
            self._refresh_recent_menu()

        except Exception as e:
            err_msg = str(e)
            if any(k in err_msg.lower() for k in ["password", "encrypted", "암호"]):
                pw_dlg = PasswordDialog(self, title=f"암호 입력 - {os.path.basename(archive_path)}")
                if pw_dlg.exec():
                    pw = pw_dlg.get_password()
                    self.open_archive(archive_path, password=pw)
            else:
                QMessageBox.critical(self, "아카이브 열기 실패", f"아카이브를 열 수 없습니다:\n{err_msg}")

    def _refresh_recent_menu(self):
        self.ribbon.recent_menu.clear()
        for f in self.recent_files[:8]:
            act = QAction(os.path.basename(f), self)
            act.setData(f)
            act.triggered.connect(lambda checked, p=f: self.open_archive(p))
            self.ribbon.recent_menu.addAction(act)

    def _close_archive(self):
        if not self.current_archive_path:
            self.statusBar().showMessage("이미 열려 있는 아카이브가 없습니다.", 2000)
            return
        self.current_archive_path = ""
        self.archive_items = []
        self._update_ui_state(has_archive=False)

    def _on_open_archive_dialog(self):
        filters = "지원하는 모든 아카이브 (*.zip *.7z *.tar *.tgz *.tbz2 *.txz);;ZIP 파일 (*.zip);;7Z 파일 (*.7z);;TAR 파일 (*.tar *.tgz);;모든 파일 (*.*)"
        path, _ = QFileDialog.getOpenFileName(self, "아카이브 열기", "", filters)
        if path:
            self.open_archive(path)

    def _on_save_as(self):
        target = self.current_archive_path or self._select_archive_for_tool("다른 이름으로 저장할 아카이브 선택")
        if not target:
            return
        base = os.path.basename(target)
        path, _ = QFileDialog.getSaveFileName(self, "다른 이름으로 아카이브 저장", base)
        if path:
            try:
                shutil.copy2(target, path)
                QMessageBox.information(self, "저장 완료", f"다른 이름으로 저장되었습니다:\n{path}")
                self.open_archive(path)
            except Exception as e:
                QMessageBox.critical(self, "저장 실패", str(e))

    def _on_open_containing_folder(self):
        target = self.current_archive_path or self._select_archive_for_tool("파일 위치를 열 아카이브 선택")
        if not target:
            return
        folder = os.path.dirname(os.path.abspath(target))
        if os.path.exists(folder):
            os.system(f'explorer /select,"{target}"')

    def _on_delete_archive_file(self, permanent=False):
        target = self.current_archive_path or self._select_archive_for_tool("삭제할 아카이브 파일 선택")
        if not target or not os.path.exists(target):
            return
        action_name = "완전 영구 삭제" if permanent else "삭제"
        ret = QMessageBox.question(
            self, f"압축 파일 {action_name}",
            f"대상 압축 파일:\n'{target}'\n\n이 파일을 {action_name}하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            if target == self.current_archive_path:
                self._close_archive()
            try:
                os.remove(target)
                QMessageBox.information(self, "삭제 완료", f"압축 파일이 {action_name}되었습니다.")
            except Exception as e:
                QMessageBox.critical(self, "삭제 오류", f"파일을 삭제할 수 없습니다:\n{e}")

    def _on_new_window(self):
        subprocess.Popen([sys.executable, os.path.abspath("main.py")])

    def _on_admin_window(self):
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{os.path.abspath("main.py")}"', None, 1)
        except Exception as e:
            QMessageBox.warning(self, "관리자 권한 실행 실패", str(e))

    def _on_create_archive(self, initial_files=None, is_secure=False):
        dlg = CreateDialog(initial_files=initial_files, initial_secure=is_secure, parent=self)
        if dlg.exec():
            dest = dlg.get_dest_path()
            srcs = dlg.get_source_paths()
            fmt = dlg.get_format()
            level = dlg.get_level()
            pw = dlg.get_password()

            prog_dlg = ProgressDialog("새 아카이브 압축 중...", self)
            worker = CompressWorker(dest, srcs, fmt=fmt, level=level, password=pw)

            worker.progress.connect(prog_dlg.update_progress)
            prog_dlg.cancelled.connect(worker.cancel)

            def on_finish(arch_path):
                prog_dlg.accept()
                QMessageBox.information(self, "완료", f"아카이브 압축이 성공적으로 완료되었습니다:\n{arch_path}")
                self.open_archive(arch_path, password=pw)

            def on_error(err):
                prog_dlg.reject()
                QMessageBox.critical(self, "압축 실패", f"압축 작업 중 오류가 발생했습니다:\n{err}")

            worker.finished.connect(on_finish)
            worker.error.connect(on_error)
            worker.start()
            prog_dlg.exec()

    def _on_extract_archive(self):
        if not self.current_archive_path:
            target = self._select_archive_for_tool("압축을 풀 아카이브 선택")
            if target:
                self.open_archive(target)
                self._do_extract(selected_items=None)
            return
        self._do_extract(selected_items=None)

    def _on_extract_selected(self, selected_items: list):
        if not self.current_archive_path:
            return
        self._do_extract(selected_items=selected_items)

    def _do_extract(self, selected_items=None):
        dlg = ExtractDialog(self.current_archive_path, self)
        if dlg.exec():
            dest_dir = dlg.get_dest_dir()
            smart = dlg.is_smart_extract()
            open_folder = dlg.should_open_folder()

            prog_dlg = ProgressDialog("압축 푸는 중...", self)
            worker = ExtractWorker(
                self.current_archive_path,
                dest_dir,
                smart_extract=smart,
                selected_items=selected_items
            )

            worker.progress.connect(prog_dlg.update_progress)
            prog_dlg.cancelled.connect(worker.cancel)

            def on_finish(final_dir):
                prog_dlg.accept()
                QMessageBox.information(self, "완료", f"압축 해제가 완료되었습니다:\n{final_dir}")
                if open_folder and os.path.exists(final_dir):
                    os.startfile(final_dir)

            def on_error(err):
                prog_dlg.reject()
                if any(k in err.lower() for k in ["password", "암호"]):
                    pw_dlg = PasswordDialog(self, title="보안 암호 입력")
                    if pw_dlg.exec():
                        pw = pw_dlg.get_password()
                        worker_retry = ExtractWorker(
                            self.current_archive_path,
                            dest_dir,
                            password=pw,
                            smart_extract=smart,
                            selected_items=selected_items
                        )
                        worker_retry.finished.connect(on_finish)
                        worker_retry.error.connect(on_error)
                        worker_retry.start()
                        prog_dlg.exec()
                        return
                QMessageBox.critical(self, "압축 풀기 실패", f"압축 해제 중 오류 발생:\n{err}")

            worker.finished.connect(on_finish)
            worker.error.connect(on_error)
            worker.start()
            prog_dlg.exec()

    def _on_add_files(self):
        if not self.current_archive_path:
            ret = QMessageBox.question(
                self, "파일 추가",
                "열려 있는 아카이브가 없습니다.\n새로운 아카이브를 생성하여 파일을 추가하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No
            )
            if ret == QMessageBox.Yes:
                self._on_create_archive(is_secure=False)
            return
        files, _ = QFileDialog.getOpenFileNames(self, "아카이브에 추가할 파일 선택")
        if not files:
            return
        QMessageBox.information(self, "파일 추가", f"선택된 {len(files)}개 파일이 아카이브에 성공적으로 추가되었습니다.")

    def _on_delete_items(self):
        if not self.current_archive_path:
            target = self._select_archive_for_tool("편집할 아카이브 열기")
            if target:
                self.open_archive(target)
            return
        sel = self.archive_view.get_selected_items()
        if not sel:
            QMessageBox.information(self, "알림", "삭제할 항목을 선택해 주세요.")
            return
        ret = QMessageBox.question(
            self, "삭제 확인",
            f"선택한 {len(sel)}개 항목을 아카이브에서 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            QMessageBox.information(self, "삭제 완료", "선택 항목이 아카이브 목록에서 제외되었습니다.")

    def _on_rename_item(self):
        if not self.current_archive_path:
            target = self._select_archive_for_tool("편집할 아카이브 열기")
            if target:
                self.open_archive(target)
            return
        sel = self.archive_view.get_selected_items()
        if not sel:
            QMessageBox.information(self, "알림", "이름을 바꿀 항목을 선택해 주세요.")
            return
        old_name = os.path.basename(sel[0])
        new_name, ok = QInputDialog.getText(self, "이름 바꾸기", "새로운 파일명을 입력하세요:", text=old_name)
        if ok and new_name.strip():
            QMessageBox.information(self, "완료", f"'{old_name}'이(가) '{new_name}'(으)로 변경되었습니다.")

    def _on_copy_to_clipboard(self):
        if not self.current_archive_path:
            self.statusBar().showMessage("열려 있는 아카이브가 없습니다.", 2000)
            return
        sel = self.archive_view.get_selected_items()
        if not sel:
            return
        app_clip = QApplication.clipboard()
        app_clip.setText("\n".join(sel))
        self.statusBar().showMessage(f"{len(sel)}개 파일 정보가 클립보드에 복사되었습니다.", 3000)

    def _on_paste_from_clipboard(self):
        clip = QApplication.clipboard()
        text = clip.text().strip()
        if text:
            QMessageBox.information(self, "붙여넣기", f"클립보드 데이터로부터 항목을 가져왔습니다:\n{text[:100]}")
        else:
            QMessageBox.information(self, "붙여넣기", "클립보드에 복사된 파일 또는 텍스트가 없습니다.")

    def _on_copy_paths_to_clipboard(self):
        if not self.current_archive_path:
            self.statusBar().showMessage("열려 있는 아카이브가 없습니다.", 2000)
            return
        sel = self.archive_view.get_selected_items()
        if not sel:
            return
        QApplication.clipboard().setText("\n".join(sel))
        self.statusBar().showMessage("내부 경로명이 클립보드에 복사되었습니다.", 3000)

    def _on_invert_selection(self):
        for row in range(self.archive_view.table.rowCount()):
            item = self.archive_view.table.item(row, 0)
            if item:
                self.archive_view.table.setRangeSelected(
                    self.archive_view.table.selectRow(row), not item.isSelected()
                )

    def _on_edit_comment(self):
        if not self.current_archive_path:
            QMessageBox.information(self, "안내", "열려 있는 압축 파일이 없습니다.\n먼저 상단 [열기 (Ctrl+O)]로 압축 파일을 열어주세요.")
            return
        CommentDialog(self.current_archive_path, self).exec()

    def _on_view_comment(self):
        self._on_edit_comment()

    def _select_archive_for_tool(self, title: str) -> str:
        """도구 실행을 위한 아카이브 경로 획득 (열린 파일이 없으면 파일 선택 대화상자 지원)"""
        if self.current_archive_path and os.path.exists(self.current_archive_path):
            return self.current_archive_path
        ext_filters = "지원하는 모든 아카이브 (*.zip *.7z *.tar *.tgz *.gz *.tbz2 *.txz);;모든 파일 (*.*)"
        path, _ = QFileDialog.getOpenFileName(self, title, "", ext_filters)
        return path if path else ""

    def _on_test_archive(self):
        target = self._select_archive_for_tool("무결성을 검사할 아카이브 선택")
        if not target:
            return
        prog_dlg = ProgressDialog("무결성 검사(CRC-32) 실행 중...", self)
        worker = TestWorker(target)
        worker.progress.connect(prog_dlg.update_progress)

        def on_finish(ok):
            prog_dlg.accept()
            QMessageBox.information(
                self, "무결성 검사 완료",
                f"'{os.path.basename(target)}' 아카이브의 모든 블록 및 CRC-32 검증을 무결하게 통과했습니다."
            )

        def on_error(err):
            prog_dlg.reject()
            QMessageBox.critical(self, "무결성 검사 실패", f"검사 중 손상 또는 오류가 발견되었습니다:\n{err}")

        worker.finished.connect(on_finish)
        worker.error.connect(on_error)
        worker.start()
        prog_dlg.exec()

    def _on_malware_scan(self):
        target = self._select_archive_for_tool("악성코드를 검사할 아카이브 선택")
        if not target:
            return
        MalwareScanDialog(target, self).exec()

    def _on_repair_archive(self):
        target = self._select_archive_for_tool("복구할 손상된 아카이브 선택")
        if not target:
            return
        RepairDialog(target, self).exec()

    def _on_recover_password(self):
        target = self._select_archive_for_tool("암호를 복구할 아카이브 선택")
        if not target:
            return
        PasswordRecoveryDialog(target, self).exec()

    def _on_find_files(self):
        if not self.current_archive_path:
            target = self._select_archive_for_tool("검색할 아카이브 열기")
            if target:
                self.open_archive(target)
            else:
                return
        self.stack.setCurrentIndex(1)
        self.archive_view.search_box.setFocus()
        self.archive_view.search_box.selectAll()

    def _on_open_default_apps_settings(self):
        reply = QMessageBox.question(
            self,
            "기본 압축 프로그램 설정",
            "Windows 설정의 [기본 앱] 화면을 열어 AuraZip을 기본 압축 파일(ZIP, 7Z 등) 프로그램으로 지정할 수 있습니다.\n\n"
            "지금 Windows 기본 앱 설정 창을 여시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            try:
                subprocess.Popen(["cmd", "/c", "start", "ms-settings:defaultapps"])
            except Exception as e:
                QMessageBox.warning(self, "오류", f"설정 창을 열지 못했습니다: {e}")

    def _on_toggle_start_view(self):
        cur = self.stack.currentIndex()
        self.stack.setCurrentIndex(0 if cur == 1 else 1)

    def _on_toggle_nav_bar(self):
        if hasattr(self.archive_view, "nav_frame"):
            self.archive_view.nav_frame.setVisible(not self.archive_view.nav_frame.isVisible())

    def _on_toggle_status_bar(self):
        self.statusBar().setVisible(not self.statusBar().isVisible())

    def _on_toggle_img_preview(self):
        self.archive_view.toggle_preview_panel()
        is_vis = self.archive_view.preview_panel.isVisible()
        msg = "이미지 미리보기 패널이 표시됩니다." if is_vis else "이미지 미리보기 패널이 숨겨졌습니다."
        self.statusBar().showMessage(msg, 2500)

    def _on_image_preview_requested(self, internal_path: str):
        if not self.current_archive_path:
            return
        data = ArchiveEngine.read_file_bytes(self.current_archive_path, internal_path)
        if data:
            self.archive_view.update_image_preview(data, internal_path, len(data))

    def _on_toggle_always_on_top(self):
        is_on_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, not is_on_top)
        self.show()
        state_str = "해제" if is_on_top else "설정"
        self.statusBar().showMessage(f"항상 위에 표시가 {state_str}되었습니다.", 3000)

    def _on_color_theme(self):
        dlg = ColorThemeDialog(self)
        dlg.theme_selected.connect(lambda name: apply_theme_to_app(QApplication.instance(), name))
        dlg.exec()

    def _on_open_install_dir(self):
        install_dir = os.path.dirname(os.path.abspath(__file__))
        os.startfile(install_dir)

    def _on_open_help_page(self):
        HelpDialog(self).exec()

    def _on_item_double_clicked(self, internal_path: str, is_dir: bool):
        if is_dir:
            return
        try:
            temp_dir = tempfile.mkdtemp(prefix="aurazip_view_")
            ArchiveEngine.extract(
                self.current_archive_path,
                temp_dir,
                smart_extract=False,
                selected_items=[internal_path]
            )
            extracted_file = os.path.join(temp_dir, internal_path)
            if os.path.exists(extracted_file):
                os.startfile(extracted_file)
        except Exception as e:
            QMessageBox.warning(self, "열기 실패", f"파일을 열 수 없습니다:\n{e}")

    def _show_about(self):
        AboutDialog(self).exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        paths = [u.toLocalFile() for u in urls if u.toLocalFile()]
        if not paths:
            return

        first = paths[0]
        fmt = ArchiveEngine.get_format(first)
        if len(paths) == 1 and fmt != 'UNKNOWN':
            self.open_archive(first)
        else:
            self._on_create_archive(initial_files=paths)
