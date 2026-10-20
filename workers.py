import os
from PySide6.QtCore import QThread, Signal
from archive_engine import ArchiveEngine


class ExtractWorker(QThread):
    progress = Signal(str, int, int)      # current_file, current_bytes, total_bytes
    finished = Signal(str)                # output directory
    error = Signal(str)

    def __init__(self, archive_path: str, dest_dir: str, password: str = None, smart_extract: bool = True, selected_items=None):
        super().__init__()
        self.archive_path = archive_path
        self.dest_dir = dest_dir
        self.password = password
        self.smart_extract = smart_extract
        self.selected_items = selected_items
        self._is_cancelled = False

    def run(self):
        try:
            def cb(curr_name, proc, total):
                if self._is_cancelled:
                    raise InterruptedError("사용자가 압축 해제를 취소했습니다.")
                self.progress.emit(curr_name, proc, total)

            out_dir = ArchiveEngine.extract(
                self.archive_path,
                self.dest_dir,
                password=self.password,
                smart_extract=self.smart_extract,
                selected_items=self.selected_items,
                progress_cb=cb
            )
            self.finished.emit(out_dir)
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._is_cancelled = True


class CompressWorker(QThread):
    progress = Signal(str, int, int)      # current_file, current_bytes, total_bytes
    finished = Signal(str)                # archive path
    error = Signal(str)

    def __init__(self, archive_path: str, source_paths: list, fmt: str = 'ZIP', level: int = 5, password: str = None):
        super().__init__()
        self.archive_path = archive_path
        self.source_paths = source_paths
        self.fmt = fmt
        self.level = level
        self.password = password
        self._is_cancelled = False

    def run(self):
        try:
            def cb(curr_name, proc, total):
                if self._is_cancelled:
                    raise InterruptedError("사용자가 압축을 취소했습니다.")
                self.progress.emit(curr_name, proc, total)

            ArchiveEngine.create(
                self.archive_path,
                self.source_paths,
                fmt=self.fmt,
                level=self.level,
                password=self.password,
                progress_cb=cb
            )
            self.finished.emit(self.archive_path)
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._is_cancelled = True


class TestWorker(QThread):
    progress = Signal(str, int, int)
    finished = Signal(bool)
    error = Signal(str)

    def __init__(self, archive_path: str, password: str = None):
        super().__init__()
        self.archive_path = archive_path
        self.password = password

    def run(self):
        try:
            def cb(curr_name, proc, total):
                self.progress.emit(curr_name, proc, total)

            ok = ArchiveEngine.test_integrity(self.archive_path, self.password, progress_cb=cb)
            self.finished.emit(ok)
        except Exception as e:
            self.error.emit(str(e))
