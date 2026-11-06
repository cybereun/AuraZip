from translations import tr, trf
import os
import sys
import zipfile
import shutil
import subprocess
import glob
import tempfile
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QProgressBar, QMessageBox, QComboBox, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap

try:
    import py7zr
except ImportError:
    py7zr = None

try:
    import pyzipper
except ImportError:
    pyzipper = None


class RepairNotSupportedError(ValueError):
    """Raised when a format cannot be reliably salvaged by this application."""


class PasswordRecoveryNotSupportedError(ValueError):
    """Raised when the archive format or encryption mode cannot be checked."""


@dataclass(frozen=True)
class RepairResult:
    path: str
    recovered_count: int
    skipped_count: int


@dataclass(frozen=True)
class DefenderScanResult:
    status: str
    detail: str
    exit_code: int | None = None


def find_defender_executable() -> str | None:
    """Locate the installed Defender CLI, including its versioned platform path."""
    candidates = []
    for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
        program_files = os.environ.get(env_name)
        if program_files:
            candidates.append(os.path.join(program_files, "Windows Defender", "MpCmdRun.exe"))

    program_data = os.environ.get("ProgramData")
    if program_data:
        platform_dir = os.path.join(program_data, "Microsoft", "Windows Defender", "Platform")
        candidates.extend(glob.glob(os.path.join(platform_dir, "*", "MpCmdRun.exe")))

    path_candidate = shutil.which("MpCmdRun.exe")
    if path_candidate:
        candidates.append(path_candidate)

    existing = []
    seen = set()
    for candidate in candidates:
        normalized = os.path.normcase(os.path.abspath(candidate))
        if normalized not in seen and os.path.isfile(candidate):
            seen.add(normalized)
            existing.append(candidate)

    # Prefer Defender's current platform binary when present.
    platform_candidates = [path for path in existing if "\\Platform\\" in path]
    if platform_candidates:
        return max(platform_candidates, key=lambda path: os.path.getmtime(path))
    return existing[0] if existing else None


def scan_archive_with_defender(archive_path: str, defender_path: str | None = None) -> DefenderScanResult:
    """Run the Defender custom-file scan and describe its result without false-safe claims."""
    if not os.path.isfile(archive_path):
        return DefenderScanResult("error", tr("검사할 파일을 찾을 수 없습니다."))

    defender_path = defender_path or find_defender_executable()
    if not defender_path:
        return DefenderScanResult("unavailable", tr("Windows Defender 검사 도구를 사용할 수 없습니다."))

    command = [
        defender_path, "-Scan", "-ScanType", "3", "-File", os.path.abspath(archive_path),
        "-DisableRemediation",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return DefenderScanResult("error", trf("Windows Defender 검사에 실패했습니다: ZXPH0XZ", str(exc)))
    except Exception as exc:
        return DefenderScanResult("error", trf("Windows Defender 검사 중 예기치 않은 오류가 발생했습니다: ZXPH0XZ", str(exc)))

    if result.returncode == 0:
        # Microsoft documents exit code 0 as either no malware or malware remediated.
        # Protection History is needed to distinguish those outcomes.
        detail = tr(
            "Defender 검사가 완료되었습니다. 종료 코드 0은 위협이 없었거나 위협이 제거되었음을 뜻할 수 있습니다. "
            "안전 판정으로 간주하지 말고 Windows 보안의 보호 기록을 확인하세요."
        )
        return DefenderScanResult("completed", detail, result.returncode)
    if result.returncode == 2:
        detail = tr(
            "Defender가 미조치 위협, 추가 조치 필요 또는 검사 오류를 보고했습니다. "
            "Windows 보안의 보호 기록과 Defender 로그를 확인하세요."
        )
        return DefenderScanResult("attention", detail, result.returncode)

    diagnostic = (result.stderr or result.stdout or "").strip()
    detail = trf("Defender 검사에 실패했습니다 (종료 코드 ZXPH0XZ). ZXPH1XZ", str(result.returncode), diagnostic)
    return DefenderScanResult("error", detail, result.returncode)


def repair_archive(archive_path: str, progress_callback=None) -> RepairResult:
    """Salvage CRC-valid entries from a readable ZIP central directory only."""
    if not archive_path.lower().endswith(".zip"):
        raise RepairNotSupportedError(
            tr("이 형식의 복구는 지원하지 않습니다. ZIP에서 읽을 수 있는 항목만 부분 복구할 수 있습니다.")
        )
    if not os.path.isfile(archive_path):
        raise FileNotFoundError(tr("복구할 파일을 찾을 수 없습니다."))

    base, ext = os.path.splitext(archive_path)
    recovered_path = f"{base}_recovered{ext}"
    if os.path.exists(recovered_path):
        raise FileExistsError(trf("복구 결과 파일이 이미 있습니다. 덮어쓰지 않았습니다: ZXPH0XZ", recovered_path))

    output_dir = os.path.dirname(os.path.abspath(recovered_path))
    fd, temp_path = tempfile.mkstemp(prefix=".aurazip-repair-", suffix=".zip", dir=output_dir)
    os.close(fd)
    recovered_count = 0
    skipped_count = 0

    try:
        with zipfile.ZipFile(archive_path, "r") as source, zipfile.ZipFile(
            temp_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as target:
            target.comment = source.comment
            entries = source.infolist()
            total = max(1, len(entries))
            for index, info in enumerate(entries):
                try:
                    data = source.read(info)
                    target.writestr(info, data)
                    recovered_count += 1
                except Exception:
                    skipped_count += 1
                if progress_callback:
                    progress_callback(index + 1, total)

        if recovered_count == 0:
            raise ValueError(tr("읽을 수 있는 ZIP 항목이 없어 복구 결과를 만들지 않았습니다."))

        with zipfile.ZipFile(temp_path, "r") as check_archive:
            bad_name = check_archive.testzip()
            if bad_name:
                raise zipfile.BadZipFile(trf("복구 결과 검증에 실패했습니다: ZXPH0XZ", bad_name))

        os.replace(temp_path, recovered_path)
        return RepairResult(recovered_path, recovered_count, skipped_count)
    except Exception:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise


def recover_archive_password(archive_path: str, candidates: list[str]) -> str | None:
    """Try candidates only against actually encrypted ZIP or 7Z payloads."""
    extension = os.path.splitext(archive_path)[1].lower()
    if extension == ".zip":
        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                encrypted_entries = [
                    info for info in archive.infolist()
                    if not info.is_dir() and info.flag_bits & 0x1
                ]
        except Exception as exc:
            raise ValueError(trf("ZIP 아카이브를 읽을 수 없습니다: ZXPH0XZ", str(exc))) from exc
        if not encrypted_entries:
            raise PasswordRecoveryNotSupportedError(tr("이 ZIP은 암호화되지 않았습니다."))
        if pyzipper is None and any(_zip_has_aes_extra(info) for info in encrypted_entries):
            raise PasswordRecoveryNotSupportedError(tr("AES ZIP 암호 검증 모듈을 사용할 수 없습니다."))

        opener = pyzipper.AESZipFile if pyzipper is not None else zipfile.ZipFile
        for candidate in candidates:
            try:
                with opener(archive_path, "r") as archive:
                    archive.setpassword(candidate.encode("utf-8"))
                    # Use ZipInfo objects from the same library instance. The
                    # stdlib ZipInfo objects used for preflight are not accepted
                    # by pyzipper.open().
                    current_encrypted = [
                        info for info in archive.infolist()
                        if not info.is_dir() and info.flag_bits & 0x1
                    ]
                    for info in current_encrypted:
                        with archive.open(info, "r") as stream:
                            while stream.read(1024 * 1024):
                                pass
                return candidate
            except Exception:
                continue
        return None

    if extension == ".7z":
        if py7zr is None:
            raise PasswordRecoveryNotSupportedError(tr("7Z 암호 검증 모듈을 사용할 수 없습니다."))
        encrypted = False
        try:
            with py7zr.SevenZipFile(archive_path, mode="r") as archive:
                encrypted = bool(archive.needs_password())
        except Exception as exc:
            if "password" in str(exc).lower():
                encrypted = True
            else:
                raise ValueError(trf("7Z 아카이브를 확인할 수 없습니다: ZXPH0XZ", str(exc))) from exc
        if not encrypted:
            raise PasswordRecoveryNotSupportedError(tr("이 7Z는 암호화되지 않았습니다."))

        for candidate in candidates:
            try:
                with py7zr.SevenZipFile(archive_path, mode="r", password=candidate) as archive:
                    if archive.testzip() is None:
                        return candidate
            except Exception:
                continue
        return None

    raise PasswordRecoveryNotSupportedError(tr("암호 복구는 암호화된 ZIP 또는 7Z만 지원합니다."))


def _zip_has_aes_extra(info: zipfile.ZipInfo) -> bool:
    """Return whether a ZIP member uses WinZip AES (extra field 0x9901)."""
    extra = info.extra
    offset = 0
    while offset + 4 <= len(extra):
        field_id = int.from_bytes(extra[offset:offset + 2], "little")
        size = int.from_bytes(extra[offset + 2:offset + 4], "little")
        if field_id == 0x9901:
            return True
        offset += 4 + size
    return False


class CommentDialog(QDialog):
    def __init__(self, archive_path: str, parent=None):
        super().__init__(parent)
        self.archive_path = archive_path
        self.setWindowTitle(tr('압축 파일 설명(주석) 편집 - AuraZip'))
        self.setFixedSize(460, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        lbl = QLabel(trf("📄 'ZXPH0XZ' 주석/설명:", f'{os.path.basename(archive_path)}'))
        lbl.setStyleSheet("font-weight: 700; color: #1E293B;")
        layout.addWidget(lbl)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(tr('압축 파일에 포함할 설명이나 코멘트를 입력하세요...'))
        self.text_edit.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 8px; padding: 8px;")
        layout.addWidget(self.text_edit)

        # Load existing comment if ZIP
        if archive_path.lower().endswith('.zip') and os.path.exists(archive_path):
            try:
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    if zf.comment:
                        self.text_edit.setPlainText(zf.comment.decode('utf-8', errors='ignore'))
            except Exception:
                pass

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        save_btn = QPushButton(tr('저장'))
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self._save_comment)
        cancel_btn = QPushButton(tr('닫기'))
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

    def _save_comment(self):
        new_comment = self.text_edit.toPlainText().strip()
        if self.archive_path.lower().endswith('.zip') and os.path.exists(self.archive_path):
            try:
                with zipfile.ZipFile(self.archive_path, 'a') as zf:
                    zf.comment = new_comment.encode('utf-8')
                QMessageBox.information(self, tr('완료'), tr('주석이 성공적으로 저장되었습니다.'))
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, tr('오류'), trf('주석 저장 실패: ZXPH0XZ', f'{e}'))
        else:
            QMessageBox.information(self, tr('알림'), tr('현재 포맷에서는 주석 저장을 지원하지 않거나 읽기 전용입니다.'))
            self.accept()


class RepairDialog(QDialog):
    def __init__(self, archive_path: str, parent=None):
        super().__init__(parent)
        self.archive_path = archive_path
        self.setWindowTitle(tr('손상된 압축 파일 복구 - AuraZip'))
        self.setFixedSize(480, 240)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title_lbl = QLabel(tr('🛠️ 손상된 아카이브 복구 마법사'))
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(
            trf(
                '대상 파일: ZXPH0XZ\nZIP 중앙 디렉터리를 읽을 수 있는 경우 CRC 검증을 통과한 항목만 새 파일로 부분 복구합니다. '
                '7Z/TAR 복구와 손상된 중앙 디렉터리 또는 압축 데이터 복원은 지원하지 않습니다.',
                f'{os.path.basename(archive_path)}'
            )
        )
        desc_lbl.setStyleSheet("color: #64748B; font-size: 12px; line-height: 1.4;")
        layout.addWidget(desc_lbl)

        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        layout.addWidget(self.prog_bar)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.start_btn = QPushButton(tr('복구 시작'))
        self.start_btn.setObjectName("PrimaryBtn")
        self.start_btn.clicked.connect(self._run_repair)
        close_btn = QPushButton(tr('닫기'))
        close_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.start_btn)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)

    def _run_repair(self):
        self.start_btn.setEnabled(False)
        self.prog_bar.setValue(0)
        try:
            result = repair_archive(
                self.archive_path,
                progress_callback=lambda current, total: self.prog_bar.setValue(int(current * 95 / total))
            )
            self.prog_bar.setValue(100)
            QMessageBox.information(
                self,
                tr('부분 복구 완료'),
                trf(
                    '읽을 수 있는 ZIP 항목 ZXPH0XZ개를 새 파일로 저장했습니다. 제외된 항목: ZXPH1XZ개.\n'
                    '이 기능은 손상된 중앙 디렉터리나 압축 스트림 자체를 복원하지 않습니다.\n\nZXPH2XZ',
                    str(result.recovered_count), str(result.skipped_count), result.path
                )
            )
            self.accept()
        except Exception as e:
            self.prog_bar.setValue(0)
            QMessageBox.warning(self, tr('복구할 수 없음'), trf('복구하지 못했습니다: ZXPH0XZ', f'{e}'))
            self.start_btn.setEnabled(True)


class PasswordRecoveryDialog(QDialog):
    def __init__(self, archive_path: str, parent=None):
        super().__init__(parent)
        self.archive_path = archive_path
        self.setWindowTitle(tr('압축 파일 암호 복구 - AuraZip'))
        self.setFixedSize(480, 260)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title_lbl = QLabel(tr('🔑 아카이브 암호 복구 / 힌트 마법사'))
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(tr('암호화된 ZIP 또는 7Z에서 입력한 후보 암호를 검증합니다. 후보 목록 검색이며 암호 해독을 보장하지 않습니다:'))
        desc_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        layout.addWidget(desc_lbl)

        self.candidates_edit = QLineEdit("1234, 123456, 0000, password, admin, 1111")
        self.candidates_edit.setPlaceholderText(tr('쉼표(,)로 구분된 비밀번호 후보들'))
        layout.addWidget(self.candidates_edit)

        self.result_lbl = QLabel(tr('대기 중...'))
        self.result_lbl.setStyleSheet("font-weight: 600; color: #4F46E5;")
        layout.addWidget(self.result_lbl)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        start_btn = QPushButton(tr('암호 탐색 시작'))
        start_btn.setObjectName("PrimaryBtn")
        start_btn.clicked.connect(self._run_recovery)
        close_btn = QPushButton(tr('닫기'))
        close_btn.clicked.connect(self.reject)
        btn_box.addWidget(start_btn)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)

    def _run_recovery(self):
        cands = [c.strip() for c in self.candidates_edit.text().split(',') if c.strip()]
        if not cands:
            QMessageBox.warning(self, tr('알림'), tr('테스트할 비밀번호 후보를 하나 이상 입력해 주세요.'))
            return

        try:
            found = recover_archive_password(self.archive_path, cands)
        except PasswordRecoveryNotSupportedError as exc:
            self.result_lbl.setText(trf('지원하지 않는 암호 복구 대상: ZXPH0XZ', str(exc)))
            QMessageBox.warning(self, tr('지원하지 않음'), str(exc))
            return
        except Exception as exc:
            self.result_lbl.setText(trf('아카이브를 확인할 수 없습니다: ZXPH0XZ', str(exc)))
            QMessageBox.warning(self, tr('확인 실패'), trf('암호 검사를 시작할 수 없습니다: ZXPH0XZ', str(exc)))
            return

        if found:
            self.result_lbl.setText(trf('🎉 암호 발견 성공: ZXPH0XZ', f'{found}'))
            QMessageBox.information(self, tr('암호 발견'), trf('올바른 암호를 찾았습니다!\n\n암호: ZXPH0XZ', f'{found}'))
        else:
            self.result_lbl.setText(tr('후보 암호가 아카이브 내용을 검증하지 못했습니다. 이는 암호를 찾지 못했다는 뜻이며, 복구 불가능하다는 의미는 아닙니다.'))
            QMessageBox.warning(self, tr('후보 확인 결과'), tr('입력된 후보 중 아카이브 내용을 정상 검증한 암호가 없습니다.'))


class MalwareScanDialog(QDialog):
    def __init__(self, archive_path: str, parent=None):
        super().__init__(parent)
        self.archive_path = archive_path
        self.setWindowTitle(tr('압축 파일 악성코드 및 보안 검사 - AuraZip'))
        self.setFixedSize(500, 240)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 22, 22, 22)

        header_lbl = QLabel(tr('🛡️ Windows Defender 파일 검사'))
        header_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #1E293B;")
        layout.addWidget(header_lbl)

        self.info_lbl = QLabel(trf('검사 대상: ZXPH0XZ\nDefender로 아카이브 파일을 검사합니다. 검사 결과는 안전을 보증하지 않습니다.', f'{os.path.basename(archive_path)}'))
        self.info_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        layout.addWidget(self.info_lbl)

        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        layout.addWidget(self.prog_bar)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.scan_btn = QPushButton(tr('보안 검사 실행'))
        self.scan_btn.setObjectName("PrimaryBtn")
        self.scan_btn.clicked.connect(self._run_scan)
        close_btn = QPushButton(tr('닫기'))
        close_btn.clicked.connect(self.reject)
        btn_box.addWidget(self.scan_btn)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)

    def _run_scan(self):
        self.scan_btn.setEnabled(False)
        self.prog_bar.setValue(0)
        result = scan_archive_with_defender(self.archive_path)
        self.info_lbl.setText(result.detail)

        if result.status == "completed":
            self.prog_bar.setValue(100)
            QMessageBox.information(self, tr('Defender 검사 완료'), result.detail)
            self.accept()
        else:
            QMessageBox.warning(self, tr('Defender 검사 결과 확인 필요'), result.detail)
            self.scan_btn.setEnabled(True)


class ColorThemeDialog(QDialog):
    theme_selected = Signal(str)

    def __init__(self, current_theme: str = "Aura Indigo (기본 시그니처)", parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('색상 및 테마 설정 - AuraZip'))
        self.setFixedSize(380, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 22, 22, 22)

        title_lbl = QLabel(tr('🎨 테마 프리셋 선택'))
        title_lbl.setObjectName("DialogHeader")
        layout.addWidget(title_lbl)

        self.theme_combo = QComboBox()
        theme_names = [
            "Aura Indigo (기본 시그니처)",
            "Dark Slate (다크 슬레이트 모드)",
            "Emerald Mint (에메랄드 민트)",
            "Sunset Coral (선셋 코랄 모드)"
        ]
        for name in theme_names:
            self.theme_combo.addItem(tr(name), name)

        for i in range(self.theme_combo.count()):
            txt = self.theme_combo.itemData(i)
            if current_theme in txt or txt in current_theme:
                self.theme_combo.setCurrentIndex(i)
                break

        layout.addWidget(self.theme_combo)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        apply_btn = QPushButton(tr('적용'))
        apply_btn.setObjectName("PrimaryBtn")
        apply_btn.clicked.connect(self._apply)
        close_btn = QPushButton(tr('취소'))
        close_btn.clicked.connect(self.reject)
        btn_box.addWidget(apply_btn)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)

    def _apply(self):
        self.theme_selected.emit(self.theme_combo.currentData())
        self.accept()
