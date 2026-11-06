"""Regression tests for archive safety tools."""
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import py7zr
import pyzipper
from PySide6.QtWidgets import QApplication, QMessageBox

from extra_tools import MalwareScanDialog, PasswordRecoveryDialog, RepairDialog
from translations import set_language


class ExtraToolsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        set_language("ko")

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="aurazip_extra_tools_test_")
        self.root = Path(self.temp_dir.name)
        self.messages = []
        self.information_patch = patch.object(
            QMessageBox, "information", side_effect=self._capture_message
        )
        self.warning_patch = patch.object(
            QMessageBox, "warning", side_effect=self._capture_message
        )
        self.critical_patch = patch.object(
            QMessageBox, "critical", side_effect=self._capture_message
        )
        self.information_patch.start()
        self.warning_patch.start()
        self.critical_patch.start()
        self.addCleanup(self.information_patch.stop)
        self.addCleanup(self.warning_patch.stop)
        self.addCleanup(self.critical_patch.stop)
        self.addCleanup(self.temp_dir.cleanup)

    def _capture_message(self, _parent, title, message, *args, **kwargs):
        self.messages.append((str(title), str(message)))

    def _scan_message(self, result):
        archive = self.root / "sample.zip"
        archive.write_bytes(b"fixture")
        dialog = MalwareScanDialog(str(archive))
        with patch("extra_tools.find_defender_executable", return_value=r"C:\Defender\MpCmdRun.exe", create=True), \
             patch("extra_tools.os.path.exists", return_value=True), \
             patch("extra_tools.subprocess.run", return_value=result):
            dialog._run_scan()
        return dialog, "\n".join(message for _, message in self.messages)

    def test_defender_nonzero_code_never_reports_safe(self):
        from subprocess import CompletedProcess

        dialog, message = self._scan_message(CompletedProcess([], 2, "", "scan error"))

        self.assertNotIn("검사 통과: 안전함", message)
        self.assertNotIn("검사 완료: 정상", message)
        self.assertFalse(dialog.result())

    def test_missing_defender_is_reported_as_unavailable(self):
        archive = self.root / "sample.zip"
        archive.write_bytes(b"fixture")
        dialog = MalwareScanDialog(str(archive))
        with patch("extra_tools.find_defender_executable", return_value=None, create=True), \
             patch("extra_tools.os.path.exists", return_value=False):
            dialog._run_scan()

        message = "\n".join(text for _, text in self.messages)
        self.assertNotIn("검사 통과: 안전함", message)
        self.assertIn("사용할 수", message)
        self.assertFalse(dialog.result())

    def test_defender_timeout_or_exception_is_not_clean(self):
        archive = self.root / "sample.zip"
        archive.write_bytes(b"fixture")
        dialog = MalwareScanDialog(str(archive))
        with patch("extra_tools.find_defender_executable", return_value=r"C:\Defender\MpCmdRun.exe", create=True), \
             patch("extra_tools.os.path.exists", return_value=True), \
             patch("extra_tools.subprocess.run", side_effect=TimeoutError("scan timed out")):
            dialog._run_scan()

        message = "\n".join(text for _, text in self.messages)
        self.assertNotIn("검사 통과: 안전함", message)
        self.assertFalse(dialog.result())

    def test_success_exit_code_is_not_asserted_as_safe(self):
        from subprocess import CompletedProcess

        dialog, message = self._scan_message(CompletedProcess([], 0, "scan completed", ""))

        self.assertNotIn("검사 통과: 안전함", message)
        self.assertIn("보호 기록", message)
        self.assertTrue(dialog.result())

    def test_defender_scan_disables_remediation(self):
        from subprocess import CompletedProcess
        from extra_tools import scan_archive_with_defender

        archive = self.root / "sample.zip"
        archive.write_bytes(b"fixture")
        with patch("extra_tools.find_defender_executable", return_value=r"C:\Defender\MpCmdRun.exe"), \
             patch("extra_tools.subprocess.run", return_value=CompletedProcess([], 0, "", "")) as run:
            scan_archive_with_defender(str(archive))

        command = run.call_args.args[0]
        self.assertIn("-DisableRemediation", command)

    def test_unsupported_repair_does_not_copy_and_claim_success(self):
        archive = self.root / "unreadable.7z"
        archive.write_bytes(b"not actually a 7z archive")
        dialog = RepairDialog(str(archive))

        dialog._run_repair()

        recovered = self.root / "unreadable_recovered.7z"
        self.assertFalse(recovered.exists())
        self.assertFalse(dialog.result())
        self.assertNotIn("복구 완료", "\n".join(text for _, text in self.messages))

    def test_zip_repair_saves_only_entries_with_valid_data(self):
        archive = self.root / "damaged.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
            zf.writestr("damaged.txt", b"bad-data")
            zf.writestr("good.txt", b"good-data")
        with zipfile.ZipFile(archive) as zf:
            info = zf.getinfo("damaged.txt")
        with archive.open("r+b") as stream:
            stream.seek(info.header_offset + 30 + len(info.filename) + len(info.extra) + 1)
            byte = stream.read(1)
            stream.seek(-1, os.SEEK_CUR)
            stream.write(bytes([byte[0] ^ 0xFF]))

        dialog = RepairDialog(str(archive))
        dialog._run_repair()

        recovered = self.root / "damaged_recovered.zip"
        with zipfile.ZipFile(recovered) as zf:
            self.assertEqual(zf.namelist(), ["good.txt"])
            self.assertEqual(zf.read("good.txt"), b"good-data")
        message = "\n".join(text for _, text in self.messages)
        self.assertIn("읽을 수 있는 ZIP 항목 1개", message)
        self.assertTrue(dialog.result())

    def test_repair_with_no_valid_zip_entries_does_not_claim_success(self):
        archive = self.root / "all-damaged.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
            zf.writestr("bad.txt", b"bad-data")
        with zipfile.ZipFile(archive) as zf:
            info = zf.getinfo("bad.txt")
        with archive.open("r+b") as stream:
            stream.seek(info.header_offset + 30 + len(info.filename) + len(info.extra) + 1)
            byte = stream.read(1)
            stream.seek(-1, os.SEEK_CUR)
            stream.write(bytes([byte[0] ^ 0xFF]))

        dialog = RepairDialog(str(archive))
        dialog._run_repair()

        self.assertFalse((self.root / "all-damaged_recovered.zip").exists())
        self.assertFalse(dialog.result())
        self.assertNotIn("복구 완료", "\n".join(text for _, text in self.messages))

    def test_password_recovery_rejects_unencrypted_zip(self):
        archive = self.root / "plain.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("plain.txt", "content")
        dialog = PasswordRecoveryDialog(str(archive))
        dialog.candidates_edit.setText("candidate")

        dialog._run_recovery()

        self.assertNotIn("암호 발견 성공", dialog.result_lbl.text())
        self.assertIn("지원하지 않는", dialog.result_lbl.text())

    def test_password_recovery_finds_aes_encrypted_zip_password(self):
        archive = self.root / "aes.zip"
        with pyzipper.AESZipFile(
            archive, "w", encryption=pyzipper.WZ_AES
        ) as zf:
            zf.setpassword(b"secret")
            zf.writestr("encrypted.txt", b"authenticated payload")
        dialog = PasswordRecoveryDialog(str(archive))
        dialog.candidates_edit.setText("wrong, secret")

        dialog._run_recovery()

        self.assertIn("secret", dialog.result_lbl.text())
        self.assertIn("암호 발견", "\n".join(title for title, _ in self.messages))

    def test_password_recovery_finds_7z_password(self):
        source = self.root / "encrypted.txt"
        source.write_bytes(b"7z encrypted payload")
        archive = self.root / "encrypted.7z"
        with py7zr.SevenZipFile(archive, "w", password="secret") as zf:
            zf.write(source, arcname="encrypted.txt")
        dialog = PasswordRecoveryDialog(str(archive))
        dialog.candidates_edit.setText("wrong, secret")

        dialog._run_recovery()

        self.assertIn("secret", dialog.result_lbl.text())
        self.assertIn("암호 발견", "\n".join(title for title, _ in self.messages))

    def test_password_recovery_reports_unsupported_format(self):
        archive = self.root / "plain.tar"
        archive.write_bytes(b"not a tar")
        dialog = PasswordRecoveryDialog(str(archive))
        dialog.candidates_edit.setText("candidate")

        dialog._run_recovery()

        self.assertIn("지원하지 않는", dialog.result_lbl.text())


if __name__ == "__main__":
    unittest.main()
