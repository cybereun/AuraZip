"""Regression checks for the language selector and archive operations."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

import main_window
import translations
from archive_engine import ArchiveEngine
from dialogs import CreateDialog
from extra_tools import ColorThemeDialog
from help_dialog import HelpDialog


class LanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings_path = os.path.join(self.temp.name, 'settings.ini')
        self.settings_patch = patch.object(main_window, 'QSettings', side_effect=lambda *args: QSettings(self.settings_path, QSettings.IniFormat))
        self.settings_patch.start()

    def tearDown(self):
        self.settings_patch.stop()
        translations.set_language('ko')
        self.temp.cleanup()

    def test_switch_and_restore(self):
        window = main_window.MainWindow()
        window._set_language('en')
        self.assertEqual(window.ribbon.tabs.tabText(3), 'View')
        self.assertEqual(CreateDialog().windowTitle(), 'Create archive - AuraZip')
        theme_dialog = ColorThemeDialog()
        self.assertEqual(theme_dialog.theme_combo.currentData(), 'Aura Indigo (기본 시그니처)')
        help_dialog = HelpDialog()
        self.assertNotRegex(help_dialog.browser.toPlainText(), '[가-힣]')
        second = main_window.MainWindow()
        self.assertEqual(second.ribbon.tabs.tabText(3), 'View')
        window._set_language('ko')
        self.assertEqual(window.ribbon.tabs.tabText(3), '보기')
        self.assertEqual(CreateDialog().windowTitle(), '새 아카이브 압축 - AuraZip')

    def test_zip_operations_in_both_languages(self):
        source = Path(self.temp.name, 'example.txt')
        source.write_text('AuraZip', encoding='utf-8')
        archive = str(Path(self.temp.name, 'example.zip'))
        for language in ('ko', 'en'):
            with self.subTest(language=language):
                translations.set_language(language)
                ArchiveEngine.create(archive, [str(source)])
                self.assertTrue(ArchiveEngine.list_items(archive))
                ArchiveEngine.test_integrity(archive)
                target = str(Path(self.temp.name, 'out'))
                ArchiveEngine.extract(archive, target, smart_extract=False)
                self.assertEqual(Path(target, 'example.txt').read_text(encoding='utf-8'), 'AuraZip')


if __name__ == '__main__':
    unittest.main()
