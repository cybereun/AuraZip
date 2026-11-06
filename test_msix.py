"""Offline checks for Store channel isolation and MSIX metadata."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

from PySide6.QtWidgets import QApplication
import app_settings
import build_msix
import distribution
import main_window
import updater


class MsixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_version_and_manifest(self):
        self.assertEqual(build_msix.package_version('v1.0.5'), '1.0.5.0')
        for invalid in ('v0.1.2', '1.2.3.4', '1.2.65536', '1.2'):
            with self.assertRaises(ValueError):
                build_msix.package_version(invalid)
        xml = build_msix.make_manifest(build_msix.TEST_IDENTITY, '1.0.5.0')
        root = ET.fromstring(xml)
        ns = {'f': 'http://schemas.microsoft.com/appx/manifest/foundation/windows10', 'u': 'http://schemas.microsoft.com/appx/manifest/uap/windows10'}
        self.assertEqual(root.find('f:Identity', ns).attrib['ProcessorArchitecture'], 'x64')
        self.assertEqual([x.text for x in root.findall('.//u:FileType', ns)], ['.zip', '.7z'])
        self.assertEqual([x.attrib['Language'] for x in root.findall('f:Resources/f:Resource', ns)], ['ko-KR', 'en-US'])

    def test_frozen_metadata_fails_closed(self):
        with tempfile.TemporaryDirectory() as d, patch.object(sys, 'frozen', True, create=True), patch.object(distribution, '__file__', str(Path(d, 'distribution.py'))):
            self.assertEqual(distribution.distribution_channel(), 'unknown')
            metadata = Path(d, 'build_metadata', 'distribution.json')
            metadata.parent.mkdir()
            for channel, expected in [('store', False), ('github', True), ('bogus', False)]:
                metadata.write_text(json.dumps({'channel': channel}), encoding='utf8')
                self.assertEqual(distribution.github_updates_enabled(), expected)

    def test_store_update_guard_and_github_path(self):
        with patch.object(updater, 'github_updates_enabled', return_value=False), patch.object(updater, 'distribution_channel', return_value='store'), patch.object(updater, 'CheckUpdateThread') as thread, patch.object(updater.QMessageBox, 'information') as info:
            u = updater.AutoUpdater(None)
            u.check(silent=True)
            u.check(silent=False)
            thread.assert_not_called()
            info.assert_called_once()
            self.assertIn('Microsoft Store', str(info.call_args))
            dialog = updater.UpdateDialog({'tag_name': 'v9.0.0', 'download_url': 'https://example.com/setup.exe'})
            with patch.object(updater, 'DownloadUpdateThread') as download:
                dialog._start_download()
                download.assert_not_called()
            with patch.object(updater.subprocess, 'Popen') as launch:
                dialog._on_finished('setup.exe')
                launch.assert_not_called()
        with patch.object(updater, 'github_updates_enabled', return_value=True), patch.object(updater, 'CheckUpdateThread') as thread:
            updater.AutoUpdater(None).check()
            thread.return_value.start.assert_called_once()

    def test_store_settings_path_and_new_window(self):
        with tempfile.TemporaryDirectory() as d, patch.dict('os.environ', {'LOCALAPPDATA': d}), patch.object(app_settings, 'package_family_name', return_value='TestFamily_123'):
            settings = app_settings.store_settings()
            settings.setValue('theme', 'Dark Slate')
            settings.setValue('language', 'en')
            settings.sync()
            self.assertEqual(app_settings.store_settings().value('theme'), 'Dark Slate')
            self.assertEqual(app_settings.store_settings().value('language'), 'en')
            self.assertIn('TestFamily_123', settings.fileName())
        with patch.object(sys, 'frozen', True, create=True), patch.object(main_window.subprocess, 'Popen') as popen:
            main_window.MainWindow._on_new_window(None)
            popen.assert_called_once_with([sys.executable])
        with patch.object(main_window, 'github_updates_enabled', return_value=False), patch.object(main_window.ctypes, 'windll') as windll:
            main_window.MainWindow._on_admin_window(None)
            windll.shell32.ShellExecuteW.assert_not_called()


if __name__ == '__main__':
    unittest.main()
