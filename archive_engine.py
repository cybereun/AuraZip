import os
import sys
import shutil
import tempfile
import zipfile
import tarfile
import time
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
    }

    @staticmethod
    def get_format(archive_path: str) -> str:
        low = archive_path.lower()
        for ext, fmt in ArchiveEngine.SUPPORTED_EXTENSIONS.items():
            if low.endswith(ext):
                return fmt
        return 'UNKNOWN'

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
                with py7zr.SevenZipFile(archive_path, mode='r', password=password) as sz:
                    all_extracted = sz.read([internal_path])
                    if internal_path in all_extracted:
                        return all_extracted[internal_path].read()
                    for name, bio in all_extracted.items():
                        if name.replace('\\', '/').strip('/') == norm_target:
                            return bio.read()

            elif fmt in ('TAR', 'TGZ', 'TBZ2', 'TXZ'):
                mode = 'r:*'
                with tarfile.open(archive_path, mode) as tf:
                    for member in tf.getmembers():
                        if member.name.replace('\\', '/').strip('/') == norm_target:
                            f = tf.extractfile(member)
                            return f.read() if f else None
        except Exception as e:
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
        if smart_extract:
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

        if fmt == 'ZIP':
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
                if target_names:
                    sz.extract(path=final_dest, targets=list(target_names))
                else:
                    sz.extractall(path=final_dest)
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
            progress_cb("완료", total_bytes, total_bytes)

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
        fmt: 'ZIP', '7Z', 'TAR', 'TGZ'
        level: 0 (Store), 1 (Fast), 5 (Normal), 9 (Maximum)
        """
        fmt = fmt.upper()
        # Collect all files to archive
        file_entries: List[tuple] = []  # (abs_path, arc_name, size)
        total_bytes = 0

        for src in source_paths:
            src = os.path.abspath(src)
            if not os.path.exists(src):
                continue
            if os.path.isfile(src):
                size = os.path.getsize(src)
                file_entries.append((src, os.path.basename(src), size))
                total_bytes += size
            elif os.path.isdir(src):
                base_dir = os.path.basename(src)
                for root, dirs, files in os.walk(src):
                    rel = os.path.relpath(root, src)
                    for f in files:
                        p = os.path.join(root, f)
                        size = os.path.getsize(p)
                        arc_rel = os.path.normpath(os.path.join(base_dir, rel, f) if rel != '.' else os.path.join(base_dir, f))
                        file_entries.append((p, arc_rel.replace('\\', '/'), size))
                        total_bytes += size

        processed_bytes = 0

        # Ensure parent dir exists
        os.makedirs(os.path.dirname(os.path.abspath(archive_path)), exist_ok=True)

        if fmt == 'ZIP':
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
                for abs_p, arc_n, size in file_entries:
                    if progress_cb:
                        progress_cb(arc_n, processed_bytes, total_bytes)
                    zf.write(abs_p, arc_n)
                    processed_bytes += size

        elif fmt == '7Z' and py7zr:
            filters = [{'id': py7zr.FILTER_LZMA2, 'preset': level}]
            with py7zr.SevenZipFile(archive_path, 'w', password=password, filters=filters) as sz:
                for abs_p, arc_n, size in file_entries:
                    if progress_cb:
                        progress_cb(arc_n, processed_bytes, total_bytes)
                    sz.write(abs_p, arc_n)
                    processed_bytes += size

        elif fmt in ('TAR', 'TGZ'):
            mode = 'w:gz' if fmt == 'TGZ' else 'w'
            compress_level = level if fmt == 'TGZ' else None
            kwargs = {'compresslevel': compress_level} if compress_level is not None else {}
            with tarfile.open(archive_path, mode, **kwargs) as tf:
                for abs_p, arc_n, size in file_entries:
                    if progress_cb:
                        progress_cb(arc_n, processed_bytes, total_bytes)
                    tf.add(abs_p, arcname=arc_n)
                    processed_bytes += size

        if progress_cb:
            progress_cb("완료", total_bytes, total_bytes)

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
                    raise ValueError(f"손상된 파일 발견: {bad_file}")

                for idx, info in enumerate(zf.infolist()):
                    if progress_cb:
                        progress_cb(info.filename, idx + 1, total_items)
                    # Read to verify CRC
                    with zf.open(info) as f:
                        while f.read(1024 * 1024):
                            pass

        elif fmt == '7Z' and py7zr:
            with py7zr.SevenZipFile(archive_path, 'r', password=password) as sz:
                if not sz.test():
                    raise ValueError("7Z 아카이브 무결성 검사 실패")

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
            progress_cb("무결성 검사 완료", total_items, total_items)
        return True
