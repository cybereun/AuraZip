import os
from pathlib import Path
from types import SimpleNamespace
import base64

import pytest
from PySide6.QtCore import QEventLoop, QSettings, QTimer, Qt
from PySide6.QtWidgets import QApplication, QMessageBox

import main_window
import workers
from archive_engine import ArchiveEngine


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def make_window(tmp_path, monkeypatch, qapp):
    settings_path = tmp_path / "test-settings.ini"
    settings_factory = lambda *args, **kwargs: QSettings(str(settings_path), QSettings.IniFormat)
    monkeypatch.setattr(main_window, "QSettings", settings_factory)
    monkeypatch.setattr(main_window, "store_settings", lambda: settings_factory())
    monkeypatch.setattr(main_window, "github_updates_enabled", lambda: False)
    monkeypatch.setattr(main_window, "AutoUpdater", lambda parent: SimpleNamespace())
    return main_window.MainWindow()


class FakeSignal:
    def __init__(self):
        self.slots = []

    def connect(self, slot):
        self.slots.append(slot)

    def emit(self, *args):
        for slot in tuple(self.slots):
            slot(*args)


class FakeProgressDialog:
    instances = []

    def __init__(self, *args, **kwargs):
        self.progress = FakeSignal()
        self.cancelled = FakeSignal()
        self.closed_as = None
        self.instances.append(self)

    def update_progress(self, *args):
        pass

    def accept(self):
        self.closed_as = "accepted"

    def reject(self):
        self.closed_as = "rejected"

    def exec(self):
        return 0


def test_integrity_button_passes_saved_archive_password(tmp_path, monkeypatch, qapp):
    window = make_window(tmp_path, monkeypatch, qapp)
    archive = tmp_path / "encrypted.zip"
    archive.write_bytes(b"test")
    window.current_archive_path = str(archive)
    window.current_archive_password = "correct-secret"

    observed = {}

    def run_operation(operation, title, on_success, error_title=None):
        observed["result"] = operation(window.current_archive_password)
        observed["password"] = window.current_archive_password
        on_success(observed["result"], observed["password"])

    class FakeTestWorker:
        def __init__(self, archive_path, password=None):
            self.archive_path = archive_path
            self.password = password
            self.progress = FakeSignal()
            self.finished = FakeSignal()
            self.error = FakeSignal()

        def start(self):
            self.finished.emit(True)

    monkeypatch.setattr(window, "_start_archive_operation", run_operation)
    monkeypatch.setattr(main_window, "TestWorker", FakeTestWorker)
    monkeypatch.setattr(main_window, "ProgressDialog", FakeProgressDialog)
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *args: None))
    monkeypatch.setattr(ArchiveEngine, "test_integrity", lambda path, password=None: password == "correct-secret")

    window._on_test_archive()

    assert observed == {"result": True, "password": "correct-secret"}
    window.close()


def test_preview_and_double_click_pass_saved_archive_password(tmp_path, monkeypatch, qapp):
    window = make_window(tmp_path, monkeypatch, qapp)
    archive = tmp_path / "encrypted.7z"
    archive.write_bytes(b"test")
    window.current_archive_path = str(archive)
    window.current_archive_password = "correct-secret"
    observed = []
    opened = []

    def run_operation(operation, title, on_success, error_title=None):
        password = window.current_archive_password
        result = operation(password)
        on_success(result, password)

    def fake_extract(path, dest, password=None, **kwargs):
        target = Path(dest) / "folder" / "document.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("opened")
        observed.append(("open", password))
        return dest

    monkeypatch.setattr(window, "_start_archive_operation", run_operation)
    monkeypatch.setattr(ArchiveEngine, "read_file_bytes", lambda path, member, password=None: observed.append(("preview", password)) or b"image")
    monkeypatch.setattr(ArchiveEngine, "extract", fake_extract)
    monkeypatch.setattr(window.archive_view, "update_image_preview", lambda *args: None)
    monkeypatch.setattr(main_window.tempfile, "mkdtemp", lambda **kwargs: str(tmp_path / "view"))
    monkeypatch.setattr(main_window.os, "startfile", lambda path: opened.append(path), raising=False)
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda *args: None))

    window._on_image_preview_requested("image.png")
    window._on_item_double_clicked("folder/document.txt", False)

    assert observed == [("preview", "correct-secret"), ("open", "correct-secret")]
    assert opened == [os.path.join(str(tmp_path / "view"), "folder", "document.txt")]
    window.close()


def test_encrypted_integrity_preview_and_item_open_prompt_and_reuse_password(tmp_path, monkeypatch, qapp):
    image = tmp_path / "sample.png"
    image.write_bytes(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/"
        "l1sAAAAASUVORK5CYII="
    ))
    document = tmp_path / "readme.txt"
    document.write_text("encrypted archive preview test")
    archive = tmp_path / "encrypted.zip"
    ArchiveEngine.create(str(archive), [str(image), str(document)], fmt="ZIP", password="correct-secret")

    window = make_window(tmp_path, monkeypatch, qapp)
    window.current_archive_path = str(archive)
    window.current_archive_password = "correct-secret"
    messages = []
    opened = []
    previewed = []

    class FakePasswordDialog:
        calls = 0

        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            type(self).calls += 1
            return 1

        def get_password(self):
            return "correct-secret"

    monkeypatch.setattr(main_window, "PasswordDialog", FakePasswordDialog)
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *args: messages.append(args[1])))
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda *args: messages.append(args[1])))
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *args: messages.append(args[1])))
    monkeypatch.setattr(window.archive_view, "update_image_preview", lambda data, name, size: previewed.append((name, size, data)))
    monkeypatch.setattr(main_window.tempfile, "mkdtemp", lambda **kwargs: str(tmp_path / "opened-files"))
    monkeypatch.setattr(main_window.os, "startfile", lambda path: opened.append(Path(path).read_text()), raising=False)

    window._on_test_archive()
    assert any("무결성 검사 완료" in str(message) for message in messages)

    # A missing stored password must prompt; the entered password is retained for later actions.
    window.current_archive_password = None
    window._on_image_preview_requested("sample.png")
    assert window.current_archive_password == "correct-secret"
    assert previewed and previewed[0][0] == "sample.png"

    window._on_item_double_clicked("readme.txt", False)
    assert opened == ["encrypted archive preview test"]
    assert FakePasswordDialog.calls == 1
    assert not [message for message in messages if "실패" in str(message) or "오류" in str(message)]
    window.close()


def test_extract_worker_cancellation_discards_partial_output(tmp_path, monkeypatch):
    destination = tmp_path / "extracted"
    events = []

    def write_then_cancel(archive_path, dest_dir, **kwargs):
        stage = Path(dest_dir)
        stage.mkdir(parents=True, exist_ok=True)
        (stage / "partial.txt").write_text("partial")
        kwargs["progress_cb"]("partial.txt", 1, 1)
        return str(stage)

    monkeypatch.setattr(workers.ArchiveEngine, "extract", write_then_cancel)
    worker = workers.ExtractWorker("sample.zip", str(destination))
    worker.cancelled.connect(lambda: events.append("cancelled"))
    worker.error.connect(lambda message: events.append(("error", message)))
    worker._is_cancelled = True

    worker.run()

    assert not (destination / "partial.txt").exists()
    assert events == ["cancelled"]


def test_extract_cancellation_during_commit_rolls_back_overwritten_files(tmp_path, monkeypatch):
    destination = tmp_path / "extracted"
    destination.mkdir()
    previous = destination / "existing.txt"
    previous.write_text("previous contents")
    events = []
    worker = workers.ExtractWorker("sample.zip", str(destination))

    def prepare_staged_files(archive_path, dest_dir, **kwargs):
        stage = Path(dest_dir)
        (stage / "existing.txt").write_text("replacement")
        (stage / "new.txt").write_text("new file")
        return str(stage)

    original_replace = workers.os.replace
    replacements = 0

    def replace_then_cancel(source, target):
        nonlocal replacements
        original_replace(source, target)
        replacements += 1
        if replacements == 2:
            worker.cancel()

    monkeypatch.setattr(workers.ArchiveEngine, "extract", prepare_staged_files)
    monkeypatch.setattr(workers.os, "replace", replace_then_cancel)
    worker.cancelled.connect(lambda: events.append("cancelled"))
    worker.finished.connect(lambda path: events.append(("finished", path)))
    worker.error.connect(lambda message: events.append(("error", message)))

    worker.run()

    assert previous.read_text() == "previous contents"
    assert not (destination / "new.txt").exists()
    assert events == ["cancelled"]


def test_compress_worker_cancellation_discards_partial_archive(tmp_path, monkeypatch):
    destination = tmp_path / "partial.zip"
    events = []

    def write_then_cancel(path, source_paths, **kwargs):
        Path(path).write_bytes(b"partial archive")
        kwargs["progress_cb"]("source.txt", 1, 1)

    monkeypatch.setattr(workers.ArchiveEngine, "create", write_then_cancel)
    worker = workers.CompressWorker(str(destination), [], fmt="ZIP")
    worker.cancelled.connect(lambda: events.append("cancelled"))
    worker.error.connect(lambda message: events.append(("error", message)))
    worker._is_cancelled = True

    worker.run()

    assert not destination.exists()
    assert events == ["cancelled"]


def test_create_dialog_reports_cancellation_without_error_popup(tmp_path, monkeypatch, qapp):
    window = make_window(tmp_path, monkeypatch, qapp)
    failures = []

    class FakeCreateDialog:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return 1

        def get_dest_path(self):
            return str(tmp_path / "cancelled.zip")

        def get_source_paths(self):
            return []

        def get_format(self):
            return "ZIP"

        def get_level(self):
            return 5

        def get_password(self):
            return None

    class FakeCompressWorker:
        def __init__(self, *args, **kwargs):
            self.progress = FakeSignal()
            self.finished = FakeSignal()
            self.error = FakeSignal()
            self.cancelled = FakeSignal()

        def start(self):
            self.cancelled.emit()

        def cancel(self):
            pass

    monkeypatch.setattr(main_window, "CreateDialog", FakeCreateDialog)
    monkeypatch.setattr(main_window, "CompressWorker", FakeCompressWorker)
    monkeypatch.setattr(main_window, "ProgressDialog", FakeProgressDialog)
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *args: failures.append(args[1])))

    window._on_create_archive()

    assert window.statusBar().currentMessage() == main_window.tr("사용자가 압축을 취소했습니다.")
    assert not failures
    window.close()


def test_extract_dialog_reports_cancellation_without_error_popup(tmp_path, monkeypatch, qapp):
    window = make_window(tmp_path, monkeypatch, qapp)
    window.current_archive_path = str(tmp_path / "source.zip")
    Path(window.current_archive_path).write_bytes(b"fixture")
    failures = []

    class FakeExtractDialog:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return 1

        def get_dest_dir(self):
            return str(tmp_path / "extract-destination")

        def is_smart_extract(self):
            return True

        def should_open_folder(self):
            return False

    class FakeExtractWorker:
        def __init__(self, *args, **kwargs):
            self.progress = FakeSignal()
            self.finished = FakeSignal()
            self.error = FakeSignal()
            self.cancelled = FakeSignal()

        def start(self):
            self.cancelled.emit()

        def cancel(self):
            pass

    monkeypatch.setattr(main_window, "ExtractDialog", FakeExtractDialog)
    monkeypatch.setattr(main_window, "ExtractWorker", FakeExtractWorker)
    monkeypatch.setattr(main_window, "ProgressDialog", FakeProgressDialog)
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *args: failures.append(args[1])))

    window._do_extract()

    assert window.statusBar().currentMessage() == main_window.tr("사용자가 압축 해제를 취소했습니다.")
    assert not failures
    window.close()


def test_frozen_install_folder_uses_executable_directory(monkeypatch, tmp_path):
    executable = tmp_path / "installed" / "AuraZip.exe"
    executable.parent.mkdir()
    executable.write_bytes(b"exe")
    opened = []
    monkeypatch.setattr(main_window.sys, "frozen", True, raising=False)
    monkeypatch.setattr(main_window.sys, "executable", str(executable))
    monkeypatch.setattr(main_window.os, "startfile", lambda path: opened.append(path), raising=False)

    main_window.MainWindow._on_open_install_dir(None)

    assert opened == [str(executable.parent)]


def test_7z_extract_reports_entry_progress_and_cleans_when_cancelled(tmp_path, qapp):
    source = tmp_path / "payload.bin"
    source.write_bytes(b"payload" * 1024)
    archive = tmp_path / "payload.7z"
    ArchiveEngine.create(str(archive), [str(source)], fmt="7Z")
    progress = []
    ArchiveEngine.extract(
        str(archive), str(tmp_path / "progress-out"), smart_extract=False,
        progress_cb=lambda name, current, total: progress.append(name)
    )
    assert "payload.bin" in progress

    destination = tmp_path / "cancelled-out"
    worker = workers.ExtractWorker(str(archive), str(destination), smart_extract=False)
    events = []

    worker.progress.connect(lambda *_: worker.cancel(), Qt.DirectConnection)
    worker.cancelled.connect(lambda: events.append("cancelled"))
    worker.error.connect(lambda message: events.append(("error", message)))
    loop = QEventLoop()
    worker.cancelled.connect(loop.quit)
    worker.error.connect(lambda *_: loop.quit())
    worker.finished.connect(lambda *_: loop.quit())
    worker.start()
    QTimer.singleShot(10000, loop.quit)
    loop.exec()
    assert worker.wait(5000)

    assert not (destination / "payload.bin").exists()
    assert events == ["cancelled"]
