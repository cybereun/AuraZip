"""Per-package settings for the MSIX channel; keep legacy GitHub settings intact."""
import ctypes
import os
from pathlib import Path

from PySide6.QtCore import QSettings


def package_family_name():
    if os.name != 'nt':
        return None
    try:
        get_family = ctypes.windll.kernel32.GetCurrentPackageFamilyName
        length = ctypes.c_uint32(0)
        result = get_family(ctypes.byref(length), None)
        if result != 122 or not length.value:  # ERROR_INSUFFICIENT_BUFFER
            return None
        buffer = ctypes.create_unicode_buffer(length.value)
        return buffer.value if get_family(ctypes.byref(length), buffer) == 0 else None
    except (AttributeError, OSError):
        return None


def store_settings():
    local = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    family = package_family_name()
    directory = local / 'Packages' / family / 'LocalState' if family else local / 'AuraZip' / 'StoreDevelopment'
    directory.mkdir(parents=True, exist_ok=True)
    return QSettings(str(directory / 'settings.ini'), QSettings.IniFormat)
