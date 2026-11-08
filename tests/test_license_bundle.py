from pathlib import Path

from license_bundle import create_license_bundle
from packaging_support import filter_qt_virtual_keyboard


def test_license_bundle_contains_runtime_licenses(tmp_path):
    output = create_license_bundle(tmp_path / "THIRD_PARTY_NOTICES.txt")

    text = output.read_text(encoding="utf-8")
    assert "AuraZip" in text
    assert "PySide6" in text
    assert "LGPL-3.0" in text
    assert "py7zr" in text
    assert "GNU LESSER GENERAL PUBLIC LICENSE" in text
    assert "GNU GENERAL PUBLIC LICENSE" in text
    assert "Version 3, 29 June 2007" in text
    assert "6. Conveying Non-Source Forms." in text
    assert "PyInstaller" in text
    assert "Python Software Foundation License Version 2." in text


def test_qt_virtual_keyboard_artifacts_are_removed_only():
    entries = [
        ("PySide6/Qt6VirtualKeyboard.dll", "C:/qt/Qt6VirtualKeyboard.dll", "BINARY"),
        (
            "PySide6/plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll",
            "C:/qt/qtvirtualkeyboardplugin.dll",
            "BINARY",
        ),
        ("PySide6/Qt6Widgets.dll", "C:/qt/Qt6Widgets.dll", "BINARY"),
    ]

    assert filter_qt_virtual_keyboard(entries) == [entries[2]]
