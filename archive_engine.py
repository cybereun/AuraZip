import os
from translations import tr, trf
import sys
import shutil
import tempfile
import gzip
import zlib
import zipfile
import tarfile
import time
import inspect
from pathlib import PurePosixPath
from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Any

try:
    import py7zr
except ImportError:
    py7zr = None

try:
    import pyzipper
except ImportError:
    pyzipper = None

try:
    from py7zr.callbacks import ExtractCallback
except ImportError:
    ExtractCallback = None


if ExtractCallback is not None:
    class _SevenZipProgressCallback(ExtractCallback):
        def __init__(self, progress_cb, total_bytes: int):
            self.progress_cb = progress_cb
            self.total_bytes = total_bytes
            self.processed_bytes = 0
            self.current_name = ""
            self.current_bytes = 0
            self.cancel_requested = False

        @staticmethod
        def _as_int(value) -> int:
            try:
                return max(0, int(value))
            except (TypeError, ValueError):
                return 0

        def _emit(self):
            if self.progress_cb and not self.cancel_requested:
                current = min(self.total_bytes, self.processed_bytes + self.current_bytes)
                try:
                    self.progress_cb(self.current_name, current, self.total_bytes)
                except InterruptedError:
                    # py7zr invokes this callback on its reporter thread. The
                    # worker notices cancellation after extraction and drops
                    # the staged tree, so the reporter must not abort itself.
                    self.cancel_requested = True

        def report_start_preparation(self):
            pass

        def report_start(self, processing_file_path: str, processing_bytes: str):
            self.current_name = processing_file_path
            self.current_bytes = 0
            self._emit()

        def report_update(self, decompressed_bytes: str):
            self.current_bytes += self._as_int(decompressed_bytes)
            self._emit()

        def report_end(self, processing_file_path: str, wrote_bytes: str):
            written = self._as_int(wrote_bytes)
            self.current_bytes = max(self.current_bytes, written)
            self.current_name = processing_file_path
            self._emit()
            self.processed_bytes = min(self.total_bytes, self.processed_bytes + self.current_bytes)
            self.current_bytes = 0

        def report_warning(self, message: str):
            pass

        def report_postprocess(self):
            pass
else:
    _SevenZipProgressCallback = None


@dataclass
class ArchiveItem:
    name: str              # Internal path inside archive
    display_name: str      # Base file/folder name
    is_dir: bool
    original_size: int
    compressed_size: int
    ratio: float
    mtime: Optional[float]
    crc: str
    is_encrypted: bool
    kind: str


class ArchiveEngine:
    SUPPORTED_EXTENSIONS = {
        '.zip': 'ZIP',
        '.7z': '7Z',
        '.tar': 'TAR',
        '.tar.gz': 'TGZ',
        '.tgz': 'TGZ',
        '.tar.bz2': 'TBZ2',
        '.tbz2': 'TBZ2',
        '.tar.xz': 'TXZ',
        '.txz': 'TXZ',
        '.gz': 'GZ',
    }

    @staticmethod
    def get_format(archive_path: str) -> str:
        low = archive_path.lower()
        for ext, fmt in ArchiveEngine.SUPPORTED_EXTENSIONS.items():
            if low.endswith(ext):
                return fmt
        return 'UNKNOWN'

    @staticmethod
    def _gzip_member_name(archive_path: str) -> str:
        fallback = os.path.basename(archive_path)
        if fallback.lower().endswith('.gz'):
            fallback = fallback[:-3]
        try:
            with open(archive_path, 'rb') as stream:
                header = stream.read(10)
                if len(header) != 10 or header[:2] != b'\x1f\x8b':
                    return fallback or 'decompressed'
                flags = header[3]
                if flags & 0x04:
                    extra_len = int.from_bytes(stream.read(2), 'little')
                    stream.seek(extra_len, os.SEEK_CUR)
                if flags & 0x08:
                    name_bytes = bytearray()
                    while True:
                        value = stream.read(1)
                        if not value or value == b'\0':
                            break
                        name_bytes.extend(value)
                    stored_name = os.fsdecode(bytes(name_bytes))
                    stored_name = stored_name.replace('\\', '/').rsplit('/', 1)[-1]
                    if stored_name:
                        return stored_name
        except OSError:
            pass
        return fallback or 'decompressed'

    @staticmethod
    def list_items(archive_path: str, password: Optional[str] = None) -> List[ArchiveItem]:
        fmt = ArchiveEngine.get_format(archive_path)
        items: List[ArchiveItem] = []

        if fmt == 'ZIP':
            opener = pyzipper.AESZipFile if pyzipper else zipfile.ZipFile
            with opener(archive_path, 'r') as zf:
                if password:
                    zf.setpassword(password.encode('utf-8'))
                for info in zf.infolist():
                    is_dir = info.is_dir()
                    orig = info.file_size
                    comp = info.compress_size
                    ratio = (1.0 - (comp / orig)) * 100.0 if orig > 0 else 0.0
                    try:
                        mtime = time.mktime(info.date_time + (0, 0, -1))
                    except Exception:
                        mtime = None

                    # Encryption flag in ZIP flag_bits bit 0
                    is_encrypted = (info.flag_bits & 0x1) != 0

                    crc_str = f"{info.CRC:08X}" if info.CRC else "-"
                    norm_name = info.filename.replace('\\', '/').rstrip('/')
                    display_name = os.path.basename(norm_name) or norm_name
                    ext = "" if is_dir else os.path.splitext(display_name)[1].lower()
                    kind = "폴더" if is_dir else (f"{ext[1:].upper()} 파일" if ext else "파일")

                    items.append(ArchiveItem(
                        name=norm_name,
                        display_name=display_name,
                        is_dir=is_dir,
                        original_size=orig,
                        compressed_size=comp,
                        ratio=max(0.0, min(100.0, ratio)),
                        mtime=mtime,
                        crc=crc_str,
                        is_encrypted=is_encrypted,
                        kind=kind
                    ))

        elif fmt == '7Z' and py7zr:
            with py7zr.SevenZipFile(archive_path, mode='r', password=password) as sz:
                is_archive_enc = bool(getattr(sz, 'password_protected', False) or sz.needs_password())
                for entry in sz.list():
                    is_dir = entry.is_directory
                    orig = entry.uncompressed or 0
                    comp = entry.compressed or 0
                    ratio = (1.0 - (comp / orig)) * 100.0 if orig > 0 else 0.0
                    mtime = entry.creationtime.timestamp() if entry.creationtime else None
                    crc_str = f"{entry.crc32:08X}" if entry.crc32 is not None else "-"
                    norm_name = entry.filename.replace('\\', '/').rstrip('/')
                    display_name = os.path.basename(norm_name) or norm_name
                    ext = "" if is_dir else os.path.splitext(display_name)[1].lower()
                    kind = "폴더" if is_dir else (f"{ext[1:].upper()} 파일" if ext else "파일")

                    items.append(ArchiveItem(
                        name=norm_name,
                        display_name=display_name,
                        is_dir=is_dir,
                        original_size=orig,
                        compressed_size=comp,
                        ratio=max(0.0, min(100.0, ratio)),
                        mtime=mtime,
                        crc=crc_str,
                        is_encrypted=is_archive_enc,
                        kind=kind
                    ))

        elif fmt in ('TAR', 'TGZ', 'TBZ2', 'TXZ'):
            mode = 'r:*'
            with tarfile.open(archive_path, mode) as tf:
                for member in tf.getmembers():
                    is_dir = member.isdir()
                    orig = member.size
                    comp = orig  # Tar doesn't store per-file compressed size
                    ratio = 0.0
                    mtime = float(member.mtime) if member.mtime else None
                    norm_name = member.name.replace('\\', '/').rstrip('/')
                    display_name = os.path.basename(norm_name) or norm_name
                    ext = "" if is_dir else os.path.splitext(display_name)[1].lower()
                    kind = "폴더" if is_dir else (f"{ext[1:].upper()} 파일" if ext else "파일")

                    items.append(ArchiveItem(
                        name=norm_name,
                        display_name=display_name,
                        is_dir=is_dir,
                        original_size=orig,
                        compressed_size=comp,
                        ratio=ratio,
                        mtime=mtime,
                        crc="-",
                        is_encrypted=False,
                        kind=kind
                    ))

        elif fmt == 'GZ':
            crc = 0
            original_size = 0
            with gzip.open(archive_path, 'rb') as stream:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    original_size += len(chunk)
                    crc = zlib.crc32(chunk, crc)
            display_name = ArchiveEngine._gzip_member_name(archive_path)
            ext = os.path.splitext(display_name)[1].lower()
            compressed_size = os.path.getsize(archive_path)
            ratio = (1.0 - compressed_size / original_size) * 100.0 if original_size else 0.0
            items.append(ArchiveItem(
                name=display_name,
                display_name=os.path.basename(display_name),
                is_dir=False,
                original_size=original_size,
                compressed_size=compressed_size,
                ratio=max(0.0, min(100.0, ratio)),
                mtime=os.path.getmtime(archive_path),
                crc=f'{crc & 0xFFFFFFFF:08X}',
                is_encrypted=False,
                kind=f'{ext[1:].upper()} 파일' if ext else '파일'
            ))

        return items

    @staticmethod
    def read_file_bytes(archive_path: str, internal_path: str, password: Optional[str] = None) -> Optional[bytes]:
        """아카이브 내부의 단일 파일을 디스크 추출 없이 메모리로 초고속 직접 로드 (실시간 미리보기용)"""
        fmt = ArchiveEngine.get_format(archive_path)
        norm_target = internal_path.replace('\\', '/').strip('/')

        try:
            if fmt == 'ZIP':
                opener = pyzipper.AESZipFile if pyzipper else zipfile.ZipFile
                with opener(archive_path, 'r') as zf:
                    if password:
                        zf.setpassword(password.encode('utf-8'))
                    for name in zf.namelist():
                        if name.replace('\\', '/').strip('/') == norm_target:
                            return zf.read(name)

            elif fmt == '7Z' and py7zr:
                # py7zr 1.x removed read(); extract only the requested member
                # into a short-lived directory and read it back safely.
                parts = PurePosixPath(norm_target).parts
                if not parts or any(part in ('', '.', '..') for part in parts):
                    return None
                with tempfile.TemporaryDirectory(prefix='aurazip_preview_') as temp_dir:
                    try:
                        extracted_path = ArchiveEngine._safe_member_path(temp_dir, norm_target)
                    except ValueError:
                        return None
                    with py7zr.SevenZipFile(archive_path, mode='r', password=password) as sz:
                        sz.extract(path=temp_dir, targets=[norm_target])
                    if os.path.isfile(extracted_path):
                        with open(extracted_path, 'rb') as stream:
                            return stream.read()

            elif fmt == 'GZ':
                stored_name = ArchiveEngine._gzip_member_name(archive_path)
                if norm_target == stored_name:
                    with gzip.open(archive_path, 'rb') as stream:
                        return stream.read()

            elif fmt in ('TAR', 'TGZ', 'TBZ2', 'TXZ'):
                mode = 'r:*'
                with tarfile.open(archive_path, mode) as tf:
                    for member in tf.getmembers():
                        if member.name.replace('\\', '/').strip('/') == norm_target:
                            f = tf.extractfile(member)
                            return f.read() if f else None
        except Exception as e:
            error_text = str(e).lower()
            if any(token in error_text for token in ('password', 'encrypted', '암호')):
                raise
            return None
        return None

    @staticmethod
    def extract(archive_path: str,
                dest_dir: str,
                password: Optional[str] = None,
                smart_extract: bool = True,
                selected_items: Optional[List[str]] = None,
                progress_cb: Optional[Callable[[str, int, int], None]] = None) -> str:
        """
        Extracts archive to dest_dir. If smart_extract is True and archive has
        multiple top-level items, extracts into a folder named after the archive stem.
        Returns final extraction directory.
        """
        fmt = ArchiveEngine.get_format(archive_path)
        items = ArchiveEngine.list_items(archive_path, password)

        # Smart extract: inspect top-level items
        final_dest = dest_dir
        if smart_extract and fmt != 'GZ':
            top_level_names = set()
            for it in items:
                parts = it.name.split('/')
                if parts:
                    top_level_names.add(parts[0])
            
            archive_stem = os.path.splitext(os.path.basename(archive_path))[0]
            # Handle .tar.gz -> strip .tar as well
            if archive_stem.lower().endswith('.tar'):
                archive_stem = os.path.splitext(archive_stem)[0]

            if len(top_level_names) > 1 or (len(top_level_names) == 1 and not any(it.is_dir and it.name == list(top_level_names)[0] for it in items)):
                final_dest = os.path.join(dest_dir, archive_stem)

        os.makedirs(final_dest, exist_ok=True)
        total_bytes = sum(it.original_size for it in items)
        processed_bytes = 0

        target_names = set(selected_items) if selected_items else None

        if fmt == 'GZ':
            items = ArchiveEngine.list_items(archive_path, password)
            if items and (not target_names or items[0].name in target_names):
                output_path = os.path.join(final_dest, os.path.basename(items[0].name))
                if progress_cb:
                    progress_cb(items[0].name, processed_bytes, total_bytes)
                with gzip.open(archive_path, 'rb') as source, open(output_path, 'wb') as target:
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        target.write(chunk)
                        processed_bytes += len(chunk)
                        if progress_cb:
                            progress_cb(items[0].name, processed_bytes, total_bytes)

        elif fmt == 'ZIP':
            opener = pyzipper.AESZipFile if pyzipper else zipfile.ZipFile
            with opener(archive_path, 'r') as zf:
                if password:
                    zf.setpassword(password.encode('utf-8'))
                
                infolist = zf.infolist()
                for info in infolist:
                    norm = info.filename.replace('\\', '/').rstrip('/')
                    if target_names and norm not in target_names and not any(norm.startswith(t + '/') for t in target_names):
                        continue

                    if progress_cb:
                        progress_cb(norm, processed_bytes, total_bytes)

                    zf.extract(info, final_dest)
                    processed_bytes += info.file_size

        elif fmt == '7Z' and py7zr:
            with py7zr.SevenZipFile(archive_path, mode='r', password=password) as sz:
                callback = None
                extract_method = sz.extract if target_names else sz.extractall
                if progress_cb and _SevenZipProgressCallback is not None:
                    try:
                        if "callback" in inspect.signature(extract_method).parameters:
                            callback = _SevenZipProgressCallback(progress_cb, total_bytes)
                    except (TypeError, ValueError):
                        callback = None

                if target_names:
                    kwargs = {"callback": callback} if callback is not None else {}
                    sz.extract(path=final_dest, targets=list(target_names), **kwargs)
                else:
                    kwargs = {"callback": callback} if callback is not None else {}
                    sz.extractall(path=final_dest, **kwargs)
            processed_bytes = total_bytes

        elif fmt in ('TAR', 'TGZ', 'TBZ2', 'TXZ'):
            with tarfile.open(archive_path, 'r:*') as tf:
                members = tf.getmembers()
                for m in members:
                    norm = m.name.replace('\\', '/').rstrip('/')
                    if target_names and norm not in target_names and not any(norm.startswith(t + '/') for t in target_names):
                        continue
                    if progress_cb:
                        progress_cb(norm, processed_bytes, total_bytes)
                    tf.extract(m, final_dest)
                    processed_bytes += m.size

        if progress_cb:
            progress_cb(tr("완료"), total_bytes, total_bytes)

        return final_dest

    @staticmethod
    def create(archive_path: str,
               source_paths: List[str],
               fmt: str = 'ZIP',
               level: int = 5,
               password: Optional[str] = None,
               progress_cb: Optional[Callable[[str, int, int], None]] = None) -> None:
        """
        Creates an archive from source_paths (files or directories).
        fmt: 'ZIP', '7Z', 'TAR', 'TGZ', 'TBZ2', 'TXZ', or single-file 'GZ'
        level: 0 (Store), 1 (Fast), 5 (Normal), 9 (Maximum)
        """
        fmt = fmt.upper()
        # Collect all files to archive
        file_entries: List[tuple] = []  # (abs_path, arc_name, size, is_dir)
        total_bytes = 0

        if password and fmt not in ('ZIP', '7Z'):
            raise ValueError(tr('이 형식은 암호화를 지원하지 않습니다. ZIP 또는 7Z를 선택하세요.'))
        if password and fmt == 'ZIP' and pyzipper is None:
            raise RuntimeError(tr('ZIP 암호화 모듈을 사용할 수 없어 암호화된 파일을 만들 수 없습니다.'))
        if fmt == 'GZ' and (len(source_paths) != 1 or not os.path.isfile(source_paths[0])):
            raise ValueError(tr('GZ 형식은 일반 파일 하나만 압축할 수 있습니다. 폴더나 여러 파일은 ZIP을 사용하세요.'))

        for src in source_paths:
            src = os.path.abspath(src)
            if not os.path.exists(src):
                continue
            if os.path.isfile(src):
                size = os.path.getsize(src)
                file_entries.append((src, os.path.basename(src), size, False))
                total_bytes += size
            elif os.path.isdir(src):
                base_dir = os.path.basename(src)
                for root, dirs, files in os.walk(src):
                    rel = os.path.relpath(root, src)
                    # Store otherwise-lost empty folders as explicit entries.
                    if not dirs and not files:
                        arc_dir = base_dir if rel == '.' else os.path.join(base_dir, rel).replace('\\', '/')
                        file_entries.append((root, arc_dir.rstrip('/') + '/', 0, True))
                    for f in files:
                        p = os.path.join(root, f)
                        size = os.path.getsize(p)
                        arc_rel = os.path.normpath(os.path.join(base_dir, rel, f) if rel != '.' else os.path.join(base_dir, f))
                        file_entries.append((p, arc_rel.replace('\\', '/'), size, False))
                        total_bytes += size

        output_path = os.path.normcase(os.path.realpath(os.path.abspath(archive_path)))
        for src, _, _, _ in file_entries:
            if os.path.normcase(os.path.realpath(src)) == output_path:
                raise ValueError(tr('압축 파일을 압축 대상에 포함할 수 없습니다. 다른 저장 위치를 선택하세요.'))

        if fmt == 'GZ' and (len(file_entries) != 1 or file_entries[0][3]):
            raise ValueError(tr('GZ 형식은 일반 파일 하나만 압축할 수 있습니다. 폴더나 여러 파일은 ZIP을 사용하세요.'))

        processed_bytes = 0

        # Ensure parent dir exists
        os.makedirs(os.path.dirname(os.path.abspath(archive_path)), exist_ok=True)

        if fmt == 'GZ':
            src, _, size, _ = file_entries[0]
            with open(archive_path, 'wb') as raw, gzip.GzipFile(
                filename=os.path.basename(src), fileobj=raw, mode='wb', compresslevel=level
            ) as stream:
                processed_bytes = 0
                with open(src, 'rb') as source:
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        stream.write(chunk)
                        processed_bytes += len(chunk)
                        if progress_cb:
                            progress_cb(os.path.basename(src), processed_bytes, size)

        elif fmt == 'ZIP':
            compress_type = zipfile.ZIP_STORED if level == 0 else zipfile.ZIP_DEFLATED
            compress_level = level if level > 0 else None

            if password and pyzipper:
                zf = pyzipper.AESZipFile(
                    archive_path, 'w',
                    compression=compress_type,
                    compresslevel=compress_level,
                    encryption=pyzipper.WZ_AES
                )
                zf.setpassword(password.encode('utf-8'))
            else:
                zf = zipfile.ZipFile(
                    archive_path, 'w',
                    compression=compress_type,
                    compresslevel=compress_level
                )

            with zf:
                for abs_p, arc_n, size, _is_dir in file_entries:
                    if progress_cb:
                        progress_cb(arc_n, processed_bytes, total_bytes)
                    zf.write(abs_p, arc_n)
                    processed_bytes += size

        elif fmt == '7Z' and py7zr:
            filters = [{'id': py7zr.FILTER_LZMA2, 'preset': level}]
            with py7zr.SevenZipFile(archive_path, 'w', password=password, filters=filters) as sz:
                for abs_p, arc_n, size, _is_dir in file_entries:
                    if progress_cb:
                        progress_cb(arc_n, processed_bytes, total_bytes)
                    sz.write(abs_p, arc_n)
                    processed_bytes += size

        elif fmt in ('TAR', 'TGZ', 'TBZ2', 'TXZ'):
            mode = {'TAR': 'w', 'TGZ': 'w:gz', 'TBZ2': 'w:bz2', 'TXZ': 'w:xz'}[fmt]
            kwargs = {}
            if fmt in ('TGZ', 'TBZ2'):
                kwargs['compresslevel'] = level
            elif fmt == 'TXZ':
                kwargs['preset'] = level
            with tarfile.open(archive_path, mode, **kwargs) as tf:
                for abs_p, arc_n, size, _is_dir in file_entries:
                    if progress_cb:
                        progress_cb(arc_n, processed_bytes, total_bytes)
                    tf.add(abs_p, arcname=arc_n, recursive=False)
                    processed_bytes += size

        else:
            raise ValueError(trf('지원하지 않는 아카이브 형식입니다: ZXPH0XZ', fmt))

        if progress_cb:
            progress_cb(tr("완료"), total_bytes, total_bytes)

    @staticmethod
    def test_integrity(archive_path: str,
                       password: Optional[str] = None,
                       progress_cb: Optional[Callable[[str, int, int], None]] = None) -> bool:
        """
        Tests CRC and integrity of the archive.
        Returns True if passed, raises Exception on corruption or wrong password.
        """
        fmt = ArchiveEngine.get_format(archive_path)
        items = ArchiveEngine.list_items(archive_path, password)
        total_items = len(items)
        
        if fmt == 'ZIP':
            opener = pyzipper.AESZipFile if pyzipper else zipfile.ZipFile
            with opener(archive_path, 'r') as zf:
                if password:
                    zf.setpassword(password.encode('utf-8'))
                
                bad_file = zf.testzip()
                if bad_file:
                    raise ValueError(trf('손상된 파일 발견: ZXPH0XZ', bad_file))

                for idx, info in enumerate(zf.infolist()):
                    if progress_cb:
                        progress_cb(info.filename, idx + 1, total_items)
                    # Read to verify CRC
                    with zf.open(info) as f:
                        while f.read(1024 * 1024):
                            pass

        elif fmt == '7Z' and py7zr:
            with py7zr.SevenZipFile(archive_path, 'r', password=password) as sz:
                # Some valid 7z archives omit packed-stream CRC metadata, so
                # test() returns None even though their contents are sound.
                # testzip() decompresses entries and reports actual CRC errors.
                bad_file = sz.testzip()
                if bad_file:
                    raise ValueError(trf('손상된 파일 발견: ZXPH0XZ', bad_file))

        elif fmt == 'GZ':
            with gzip.open(archive_path, 'rb') as stream:
                while stream.read(1024 * 1024):
                    pass

        elif fmt in ('TAR', 'TGZ', 'TBZ2', 'TXZ'):
            with tarfile.open(archive_path, 'r:*') as tf:
                for idx, m in enumerate(tf.getmembers()):
                    if progress_cb:
                        progress_cb(m.name, idx + 1, total_items)
                    if m.isfile():
                        f = tf.extractfile(m)
                        if f:
                            while f.read(1024 * 1024):
                                pass

        if progress_cb:
            progress_cb(tr("무결성 검사 완료"), total_items, total_items)
        return True

    @staticmethod
    def _safe_member_path(root: str, member_name: str) -> str:
        normalized = member_name.replace('\\', '/').strip('/')
        parts = PurePosixPath(normalized).parts
        if not parts or any(part in ('', '.', '..') for part in parts) or ':' in parts[0]:
            raise ValueError(tr('아카이브 내부 경로가 올바르지 않습니다.'))
        root = os.path.abspath(root)
        target = os.path.abspath(os.path.join(root, *parts))
        if os.path.commonpath([root, target]) != root:
            raise ValueError(tr('아카이브 내부 경로가 올바르지 않습니다.'))
        return target

    @staticmethod
    def _rewrite_archive(archive_path: str, transform, password: Optional[str] = None) -> None:
        archive_path = os.path.abspath(archive_path)
        fmt = ArchiveEngine.get_format(archive_path)
        if fmt in ('UNKNOWN', 'GZ'):
            raise ValueError(tr('이 파일 형식은 내부 항목 편집을 지원하지 않습니다.'))

        parent = os.path.dirname(archive_path)
        archive_comment = None
        if fmt == 'ZIP':
            with zipfile.ZipFile(archive_path, 'r') as source_zip:
                archive_comment = source_zip.comment

        original_items = ArchiveEngine.list_items(archive_path, password=password)
        with tempfile.TemporaryDirectory(prefix='.aurazip-edit-', dir=parent) as temp_dir:
            content_dir = os.path.join(temp_dir, 'contents')
            os.makedirs(content_dir)
            ArchiveEngine.extract(
                archive_path, content_dir, password=password, smart_extract=False
            )

            # zipfile extraction may not restore timestamps; retain the archive's
            # member times where the platform exposes them.
            for item in original_items:
                if item.mtime is None:
                    continue
                try:
                    target = ArchiveEngine._safe_member_path(content_dir, item.name)
                    if os.path.exists(target):
                        os.utime(target, (item.mtime, item.mtime))
                except (OSError, ValueError):
                    continue

            transform(content_dir)
            output_path = os.path.join(temp_dir, 'rewritten-archive')
            sources = [os.path.join(content_dir, name) for name in sorted(os.listdir(content_dir))]
            ArchiveEngine.create(output_path, sources, fmt=fmt, level=5, password=password)
            if fmt == 'ZIP' and archive_comment is not None:
                with zipfile.ZipFile(output_path, 'a') as output_zip:
                    output_zip.comment = archive_comment
            os.replace(output_path, archive_path)

    @staticmethod
    def add_files(
        archive_path: str,
        source_paths: List[str],
        password: Optional[str] = None,
        member_prefix: str = ''
    ) -> int:
        if not source_paths:
            return 0

        added = 0

        def add_to_tree(content_dir: str) -> None:
            nonlocal added
            destination_dir = content_dir
            if member_prefix:
                destination_dir = ArchiveEngine._safe_member_path(content_dir, member_prefix)
                os.makedirs(destination_dir, exist_ok=True)
            for source in source_paths:
                source = os.path.abspath(source)
                if not os.path.isfile(source) and not os.path.isdir(source):
                    raise ValueError(trf('추가할 파일을 찾을 수 없습니다: ZXPH0XZ', source))
                name = os.path.basename(source)
                stem, ext = os.path.splitext(name)
                destination = os.path.join(destination_dir, name)
                suffix = 2
                while os.path.exists(destination):
                    destination = os.path.join(destination_dir, f'{stem} ({suffix}){ext}')
                    suffix += 1
                if os.path.isdir(source):
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination)
                added += 1

        ArchiveEngine._rewrite_archive(archive_path, add_to_tree, password=password)
        return added

    @staticmethod
    def remove_items(archive_path: str, member_names: List[str], password: Optional[str] = None) -> int:
        removed = 0

        def remove_from_tree(content_dir: str) -> None:
            nonlocal removed
            for member_name in member_names:
                target = ArchiveEngine._safe_member_path(content_dir, member_name)
                if os.path.isdir(target):
                    shutil.rmtree(target)
                    removed += 1
                elif os.path.isfile(target):
                    os.remove(target)
                    removed += 1

        ArchiveEngine._rewrite_archive(archive_path, remove_from_tree, password=password)
        return removed

    @staticmethod
    def rename_item(archive_path: str, member_name: str, new_name: str, password: Optional[str] = None) -> str:
        new_name = new_name.strip()
        if (not new_name or new_name in ('.', '..') or
                any(char in new_name for char in '<>:"/\\|?*') or
                any(ord(char) < 32 for char in new_name)):
            raise ValueError(tr('새 이름에는 파일명으로 사용할 수 없는 문자가 있습니다.'))
        renamed_path = ''

        def rename_in_tree(content_dir: str) -> None:
            nonlocal renamed_path
            source = ArchiveEngine._safe_member_path(content_dir, member_name)
            if not os.path.exists(source):
                raise FileNotFoundError(tr('이름을 바꿀 항목을 찾을 수 없습니다.'))
            target = os.path.join(os.path.dirname(source), new_name)
            if os.path.exists(target):
                raise FileExistsError(tr('같은 이름의 항목이 이미 있습니다.'))
            os.rename(source, target)
            renamed_path = os.path.relpath(target, content_dir).replace('\\', '/')

        ArchiveEngine._rewrite_archive(archive_path, rename_in_tree, password=password)
        return renamed_path
