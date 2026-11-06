import os
import shutil
import tempfile
from translations import tr
from PySide6.QtCore import QThread, Signal
from archive_engine import ArchiveEngine


class ArchiveEditWorker(QThread):
    completed = Signal(object)
    error = Signal(str)

    def __init__(self, operation):
        super().__init__()
        self.operation = operation

    def run(self):
        try:
            self.completed.emit(self.operation())
        except Exception as exc:
            self.error.emit(str(exc))


class ExtractWorker(QThread):
    progress = Signal(str, int, int)      # current_file, current_bytes, total_bytes
    finished = Signal(str)                # output directory
    error = Signal(str)
    cancelled = Signal()

    def __init__(self, archive_path: str, dest_dir: str, password: str = None, smart_extract: bool = True, selected_items=None):
        super().__init__()
        self.archive_path = archive_path
        self.dest_dir = dest_dir
        self.password = password
        self.smart_extract = smart_extract
        self.selected_items = selected_items
        self._is_cancelled = False

    def run(self):
        stage_dir = None
        rollback_dir = None
        created_destination = False
        completed = False
        try:
            destination = os.path.abspath(self.dest_dir)
            created_destination = not os.path.isdir(destination)
            os.makedirs(destination, exist_ok=True)
            stage_dir = tempfile.mkdtemp(prefix=".aurazip-extract-", dir=destination)
            rollback_dir = tempfile.mkdtemp(prefix=".aurazip-rollback-", dir=destination)

            def cb(curr_name, proc, total):
                if self._is_cancelled:
                    raise InterruptedError(tr("사용자가 압축 해제를 취소했습니다."))
                self.progress.emit(curr_name, proc, total)

            out_dir = ArchiveEngine.extract(
                self.archive_path,
                stage_dir,
                password=self.password,
                smart_extract=self.smart_extract,
                selected_items=self.selected_items,
                progress_cb=cb
            )
            if self._is_cancelled:
                raise InterruptedError(tr("사용자가 압축 해제를 취소했습니다."))

            relative_out = os.path.relpath(os.path.abspath(out_dir), stage_dir)
            final_dir = destination if relative_out == "." else os.path.join(destination, relative_out)
            self._merge_staged_directory(out_dir, final_dir, rollback_dir, lambda: self._is_cancelled)
            completed = True
            self.finished.emit(final_dir)
        except InterruptedError:
            self.cancelled.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            if stage_dir:
                shutil.rmtree(stage_dir, ignore_errors=True)
            if rollback_dir:
                shutil.rmtree(rollback_dir, ignore_errors=True)
            if created_destination and not completed:
                try:
                    if os.path.isdir(destination) and not os.listdir(destination):
                        os.rmdir(destination)
                except OSError:
                    pass

    @staticmethod
    def _merge_staged_directory(staged_dir: str, destination: str, rollback_dir: str, is_cancelled) -> None:
        """Commit staged files with rollback if cancellation or a write error occurs."""
        created_dirs = []
        installed_paths = []
        backups = []

        def ensure_directory(path: str) -> None:
            if os.path.lexists(path):
                if os.path.isdir(path) and not os.path.islink(path):
                    return
                raise FileExistsError(path)
            parent = os.path.dirname(path)
            if parent and parent != path:
                ensure_directory(parent)
            os.mkdir(path)
            created_dirs.append(path)

        def backup_existing(source_is_dir: bool, target_path: str) -> None:
            if not os.path.lexists(target_path):
                return
            target_is_dir = os.path.isdir(target_path) and not os.path.islink(target_path)
            if target_is_dir != source_is_dir:
                raise FileExistsError(target_path)
            relative = os.path.relpath(target_path, destination)
            backup_path = os.path.join(rollback_dir, relative)
            ensure_directory(os.path.dirname(backup_path))
            os.replace(target_path, backup_path)
            backups.append((backup_path, target_path))

        def require_not_cancelled() -> None:
            if is_cancelled():
                raise InterruptedError(tr("사용자가 압축 해제를 취소했습니다."))

        try:
            ensure_directory(destination)
            for current, dirs, files in os.walk(staged_dir, topdown=True, followlinks=False):
                relative = os.path.relpath(current, staged_dir)
                target_root = destination if relative == "." else os.path.join(destination, relative)
                ensure_directory(target_root)

                for name in list(dirs):
                    require_not_cancelled()
                    source_path = os.path.join(current, name)
                    target_path = os.path.join(target_root, name)
                    if os.path.islink(source_path):
                        backup_existing(False, target_path)
                        require_not_cancelled()
                        os.replace(source_path, target_path)
                        installed_paths.append(target_path)
                        dirs.remove(name)
                    else:
                        if os.path.lexists(target_path):
                            if not os.path.isdir(target_path) or os.path.islink(target_path):
                                raise FileExistsError(target_path)
                        else:
                            ensure_directory(target_path)

                for name in files:
                    require_not_cancelled()
                    source_path = os.path.join(current, name)
                    target_path = os.path.join(target_root, name)
                    source_is_dir = os.path.isdir(source_path) and not os.path.islink(source_path)
                    backup_existing(source_is_dir, target_path)
                    require_not_cancelled()
                    os.replace(source_path, target_path)
                    installed_paths.append(target_path)

            require_not_cancelled()
        except Exception:
            for path in reversed(installed_paths):
                try:
                    if os.path.islink(path) or not os.path.isdir(path):
                        os.remove(path)
                    else:
                        shutil.rmtree(path)
                except OSError:
                    pass
            for backup_path, target_path in reversed(backups):
                try:
                    ensure_directory(os.path.dirname(target_path))
                    os.replace(backup_path, target_path)
                except OSError:
                    pass
            for path in reversed(created_dirs):
                try:
                    os.rmdir(path)
                except OSError:
                    pass
            raise

    def cancel(self):
        self._is_cancelled = True


class CompressWorker(QThread):
    progress = Signal(str, int, int)      # current_file, current_bytes, total_bytes
    finished = Signal(str)                # archive path
    error = Signal(str)
    cancelled = Signal()

    def __init__(self, archive_path: str, source_paths: list, fmt: str = 'ZIP', level: int = 5, password: str = None):
        super().__init__()
        self.archive_path = archive_path
        self.source_paths = source_paths
        self.fmt = fmt
        self.level = level
        self.password = password
        self._is_cancelled = False

    def run(self):
        staged_archive = None
        try:
            target = os.path.abspath(self.archive_path)
            target_parent = os.path.dirname(target)
            os.makedirs(target_parent, exist_ok=True)
            for source in self.source_paths:
                if os.path.isfile(source) and os.path.normcase(os.path.realpath(source)) == os.path.normcase(os.path.realpath(target)):
                    raise ValueError(tr("압축 파일을 압축 대상에 포함할 수 없습니다. 다른 저장 위치를 선택하세요."))
            fd, staged_archive = tempfile.mkstemp(
                prefix=".aurazip-compress-", suffix=".tmp", dir=target_parent
            )
            os.close(fd)

            def cb(curr_name, proc, total):
                if self._is_cancelled:
                    raise InterruptedError(tr("사용자가 압축을 취소했습니다."))
                self.progress.emit(curr_name, proc, total)

            ArchiveEngine.create(
                staged_archive,
                self.source_paths,
                fmt=self.fmt,
                level=self.level,
                password=self.password,
                progress_cb=cb
            )
            if self._is_cancelled:
                raise InterruptedError(tr("사용자가 압축을 취소했습니다."))
            os.replace(staged_archive, target)
            staged_archive = None
            self.finished.emit(target)
        except InterruptedError:
            self.cancelled.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            if staged_archive and os.path.exists(staged_archive):
                try:
                    os.remove(staged_archive)
                except OSError:
                    pass

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
