"""Build a readable third-party license notice for packaged AuraZip builds."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
import sys


PACKAGED_DISTRIBUTIONS = (
    "PySide6",
    "PySide6_Essentials",
    "PySide6_Addons",
    "PySide6_Pdf",
    "shiboken6",
    "py7zr",
    "pyzipper",
    "pycryptodomex",
    "psutil",
    "texttable",
    "inflate64",
    "pybcj",
    "pyppmd",
    "multivolumefile",
    "backports.zstd",
    "brotli",
    "PyInstaller",
    "setuptools",
)

QT_DISTRIBUTIONS = {"pyside6", "pyside6_essentials", "pyside6_addons", "pyside6_pdf", "shiboken6"}


def _is_license_file(path: Path) -> bool:
    name = path.name.lower()
    return name.startswith(("license", "copying", "notice")) and path.suffix.lower() in {
        ".txt", ".md", ".rst", ".html", ".rtf", ""
    }


def _license_paths(dist) -> list[Path]:
    found = []
    for item in dist.files or ():
        relative = Path(str(item).replace("\\", "/"))
        if not _is_license_file(relative):
            continue
        if relative.name.lower().startswith("licenseref-qt-commercial"):
            continue
        path = Path(dist.locate_file(item))
        if path.is_file():
            found.append(path)
    return sorted(set(found), key=lambda path: path.as_posix().lower())


def _project_url(dist) -> str:
    for value in dist.metadata.get_all("Project-URL", ()):
        label, separator, url = value.partition(",")
        if separator and label.strip().lower() in {"homepage", "source", "repository"}:
            return url.strip()
    return dist.metadata.get("Home-page", "")


def create_license_bundle(output_path: str | Path, *, project_root: str | Path | None = None) -> Path:
    """Collect licenses for the runtime libraries and build bootloader."""
    root = Path(project_root) if project_root else Path(__file__).resolve().parent
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    qt_version = metadata.version("PySide6")
    qt_major_minor = ".".join(qt_version.split(".")[:2])

    sections: list[str] = [
        "AuraZip - Open Source Software Notices",
        "=" * 42,
        "",
        "This file identifies open-source software included in this AuraZip build and reproduces available license texts.",
        "Component versions below are generated from the exact build environment and should be refreshed when dependencies change.",
        "AuraZip itself is distributed under the MIT License (see the AuraZip section below).",
        "AuraZip source and build instructions: https://github.com/cybereun/AuraZip",
        "",
        "Qt for Python (PySide6/Shiboken6) and Qt libraries",
        "-" * 45,
        "PySide6 and Shiboken6 are offered under LGPLv3, GPLv3, and commercial terms. This distribution uses the LGPLv3 option for Qt components available under LGPLv3. GPL-only Qt Virtual Keyboard artifacts are excluded by the build configuration.",
        f"Qt also contains module-specific third-party components. The Qt {qt_version} third-party license index is available at:",
        f"https://doc.qt.io/qt-{qt_major_minor}/licenses-used-in-qt.html",
        f"Qt documents that only components actually shipped with an application need to be acknowledged. The PyPI Qt {qt_version} wheel used by this build does not provide its installation SBOM; review the module list and SBOM when preparing a Store release.",
        "",
    ]

    own_license = root / "LICENSE"
    if not own_license.is_file():
        raise FileNotFoundError(f"AuraZip license is missing: {own_license}")
    sections.extend(["AuraZip - MIT License", "-" * 25, own_license.read_text(encoding="utf-8").strip(), ""])

    qt_license = root / "licenses" / "LGPL-3.0.txt"
    if not qt_license.is_file():
        raise FileNotFoundError(f"Qt LGPLv3 license text is missing: {qt_license}")
    gpl_license = root / "licenses" / "GPL-3.0.txt"
    if not gpl_license.is_file():
        raise FileNotFoundError(f"GNU GPLv3 license text required by LGPLv3 is missing: {gpl_license}")
    sections.extend([
        "GNU General Public License, version 3.0 (provided with the Qt LGPLv3 terms)",
        "-" * 76,
        gpl_license.read_text(encoding="utf-8").strip(),
        "",
        "GNU Lesser General Public License, version 3.0 (Qt)",
        "-" * 52,
        qt_license.read_text(encoding="utf-8").strip(),
        "",
    ])

    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        raise FileNotFoundError(f"Python license text is missing: {python_license}")
    sections.extend(["Python runtime - PSF License Agreement", "-" * 38, python_license.read_text(encoding="utf-8").strip(), ""])

    for distribution_name in PACKAGED_DISTRIBUTIONS:
        try:
            dist = metadata.distribution(distribution_name)
        except metadata.PackageNotFoundError as exc:
            raise RuntimeError(f"Required packaged distribution is missing: {distribution_name}") from exc

        normalized_name = (dist.metadata.get("Name") or distribution_name).lower().replace("-", "_")
        declared_license = dist.metadata.get("License") or "See included license text"
        sections.extend([
            f"{dist.metadata.get('Name', distribution_name)} {dist.version}",
            "-" * (len(f"{dist.metadata.get('Name', distribution_name)} {dist.version}")),
            f"Declared license: {declared_license}",
        ])
        project_url = _project_url(dist)
        if project_url:
            sections.append(f"Project: {project_url}")

        license_files = _license_paths(dist)
        if normalized_name in QT_DISTRIBUTIONS:
            sections.append("License: see the Qt LGPLv3 license text above; GPL-only modules are not licensed under this selection.")
        elif not license_files:
            raise RuntimeError(f"No license text found for packaged distribution: {distribution_name}")

        for license_file in license_files:
            sections.extend([
                "",
                f"[{license_file.name}]",
                license_file.read_text(encoding="utf-8", errors="replace").strip(),
            ])
        sections.append("")

    text = "\n".join(sections).rstrip() + "\n"
    output.write_text(text, encoding="utf-8", newline="\n")
    return output
