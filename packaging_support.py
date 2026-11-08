"""Small helpers used by the PyInstaller spec and its validation tests."""


def filter_qt_virtual_keyboard(entries):
    """Remove GPL-only Qt Virtual Keyboard binaries/data from a PyInstaller TOC."""
    filtered = []
    for entry in entries:
        searchable = "/".join(str(part) for part in entry if isinstance(part, (str, bytes)))
        if "virtualkeyboard" not in searchable.lower():
            filtered.append(entry)
    return filtered
