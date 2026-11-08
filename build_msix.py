"""Build an unsigned MSIX from an explicitly Store-flavoured PyInstaller onedir build."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from string import Template
from xml.sax.saxutils import escape

from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from version import APP_VERSION

TEST_IDENTITY = {
    'identity_name': 'AuraZip.DevelopmentTest',
    'publisher': 'CN=AuraZip Development Test',
    'publisher_display_name': 'AuraZip Development Test',
}


def package_version(value):
    match = re.fullmatch(r'[vV]?(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?', value)
    if not match:
        raise ValueError('Version must be vMAJOR.MINOR.BUILD or MAJOR.MINOR.BUILD.0')
    parts = [int(p or 0) for p in match.groups()]
    if not 1 <= parts[0] <= 65535 or any(p > 65535 for p in parts) or parts[3] != 0:
        raise ValueError('Store versions require major 1..65535, other fields 0..65535, and revision 0')
    return '.'.join(map(str, parts))


def read_identity(args):
    if args.test_identity:
        return TEST_IDENTITY.copy()
    config = Path(args.identity_config)
    if not config.is_file():
        raise ValueError(f'Identity config not found: {config}. Supply Partner Center values or --test-identity.')
    identity = json.loads(config.read_text(encoding='utf-8-sig'))
    for key in TEST_IDENTITY:
        if not isinstance(identity.get(key), str) or not identity[key].strip():
            raise ValueError(f'Missing Partner Center {key}; use --test-identity for a non-Store test package.')
        identity[key] = identity[key].strip()
    if not re.fullmatch(r'[A-Za-z0-9.-]{3,50}', identity['identity_name']):
        raise ValueError('Invalid package identity name (3-50 ASCII letters, digits, dots or hyphens).')
    if not identity['publisher'].startswith('CN=') or 'OID.2.25.311729368913984317654407730594956997722=1' in identity['publisher']:
        raise ValueError('Publisher must be the exact Partner Center publisher, not an unsigned-test OID.')
    return identity


def find_makeappx(explicit=None):
    if explicit:
        path = Path(explicit)
        if path.is_file():
            return path.resolve()
        raise FileNotFoundError(f'MakeAppx not found: {path}')
    kits = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Windows Kits' / '10' / 'bin'
    candidates = list(kits.glob('*/x64/makeappx.exe'))
    candidates.sort(key=lambda p: tuple(int(x) for x in p.parent.parent.name.split('.')), reverse=True)
    if not candidates:
        raise FileNotFoundError('Windows SDK x64 MakeAppx.exe not found; install Windows SDK or use --makeappx.')
    return candidates[0]


def make_manifest(identity, version):
    values = {k: escape(v, {'"': '&quot;'}) for k, v in identity.items()}
    values['version'] = version
    return Template((ROOT / 'msix' / 'AppxManifest.xml.in').read_text(encoding='utf-8-sig')).substitute(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='Build a separate Store-flavoured PyInstaller onedir first')
    parser.add_argument('--dist', type=Path, default=ROOT / 'build' / 'msix-pyinstaller' / 'dist' / 'AuraZip')
    parser.add_argument('--identity-config', default=ROOT / 'msix' / 'identity.local.json')
    parser.add_argument('--test-identity', action='store_true', help='Use temporary identity; package is not for Store submission')
    parser.add_argument('--version', default=APP_VERSION)
    parser.add_argument('--makeappx')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist_msix')
    args = parser.parse_args()
    if os.name != 'nt' or struct.calcsize('P') != 8:
        raise RuntimeError('An x64 Windows Python environment is required.')
    identity = read_identity(args)
    version = package_version(args.version)
    makeappx = find_makeappx(args.makeappx)
    if args.build:
        env = os.environ.copy()
        env['AURAZIP_BUILD_CHANNEL'] = 'store'
        build_root = ROOT / 'build' / 'msix-pyinstaller'
        subprocess.run([sys.executable, '-m', 'PyInstaller', str(ROOT / 'AuraZip.spec'), '--noconfirm', '--clean',
                        '--distpath', str(build_root / 'dist'), '--workpath', str(build_root / 'work')], cwd=ROOT, env=env, check=True)
        args.dist = build_root / 'dist' / 'AuraZip'
    dist = args.dist.resolve()
    metadata = dist / '_internal' / 'build_metadata' / 'distribution.json'
    if not (dist / 'AuraZip.exe').is_file() or not metadata.is_file():
        raise ValueError(f'Not a complete PyInstaller onedir output: {dist}')
    if json.loads(metadata.read_text(encoding='utf-8')) != {'channel': 'store'}:
        raise ValueError('Refusing to package a non-Store PyInstaller build.')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir.resolve() / f"AuraZip_{version}_x64_{'TEST' if args.test_identity else 'STORE'}.msix"
    with tempfile.TemporaryDirectory(prefix='aurazip-msix-') as temporary:
        stage = Path(temporary) / 'package'
        shutil.copytree(dist, stage)
        (stage / 'AppxManifest.xml').write_text(make_manifest(identity, version), encoding='utf-8')
        assets = stage / 'Assets'
        assets.mkdir(exist_ok=True)
        with Image.open(ROOT / 'assets' / 'app_icon.png') as icon:
            icon = icon.convert('RGBA')
            for name, size in [('StoreLogo.png', 50), ('Square44x44Logo.png', 44), ('Square150x150Logo.png', 150)]:
                resized = icon.copy()
                resized.thumbnail((size, size), Image.Resampling.LANCZOS)
                canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                canvas.alpha_composite(resized, ((size - resized.width) // 2, (size - resized.height) // 2))
                canvas.save(assets / name)
        print('Packaging using', makeappx, flush=True)
        try:
            result = subprocess.run([str(makeappx), 'pack', '/o', '/d', str(stage), '/p', str(output)],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as exc:
            if exc.stdout:
                print(exc.stdout, file=sys.stderr, end='')
            raise
        if result.stdout:
            lines = result.stdout.splitlines()
            print('\n'.join(lines[-5:]))
    upload_package = None
    if not args.test_identity:
        # Partner Center accepts a plain .msix, but Microsoft recommends an
        # .msixupload container. A symbol file is optional for desktop apps.
        upload_package = output.with_suffix('.msixupload')
        with zipfile.ZipFile(upload_package, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as bundle:
            bundle.write(output, arcname=output.name, compress_type=zipfile.ZIP_STORED)
    print(f"{'TEST ONLY - NOT FOR STORE' if args.test_identity else 'Partner Center identity'}: {output}")
    if upload_package:
        print(f'Partner Center upload package: {upload_package}')
    print('Package is unsigned; see docs/MICROSOFT_STORE.md before testing or submitting.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'MSIX build failed: {exc}', file=sys.stderr)
        sys.exit(1)
