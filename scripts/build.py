#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from oledhero.version import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PROJECT_ROOT / "dist"
WORK_DIR = DIST_DIR / ".work"
APP_NAME = "OledHero"


def run(*command: str) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def version() -> str:
    return __version__


def determine_target() -> tuple[str, str, bool]:
    # returns platform_name, suffix, is_windows
    if sys.platform == "win32":
        return "Windows-x64", ".exe", True
    elif sys.platform.startswith("linux"):
        return "Linux-x64", "", False
    raise RuntimeError(f"Unsupported operating system: {sys.platform!r}")


def nuitka_build(mode: str, executable: str, is_windows: bool) -> Path:
    arguments = [
        "uv",
        "run",
        "--locked",
        "nuitka",
        "--assume-yes-for-downloads",
        "--python-flag=-m",
        "--enable-plugin=pyside6",
        "--include-data-dir=src/oledhero/assets=oledhero/assets",
        "--include-data-files=LICENSE=LICENSE",
        "--include-data-dir=licenses=licenses",
        f"--{mode}",
        f"--output-dir={DIST_DIR if mode == 'onefile' else WORK_DIR}",
        f"--output-filename={executable}",
    ]
    if is_windows:
        arguments.extend(
            [
                "--windows-console-mode=attach",
                "--windows-icon-from-ico=src/oledhero/assets/OledHero.ico",
            ]
        )
    arguments.append("src/oledhero")
    run(*arguments)
    
    # Check output file exists
    if mode == "onefile":
        result = (DIST_DIR / executable)
    else:
        result = (WORK_DIR / "oledhero.dist" / executable)
        
    if not result.is_file():
        raise RuntimeError(f"Nuitka did not create expected file: {result}")
    return result


def make_zip(source: Path, destination: Path) -> None:
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, Path(APP_NAME) / path.relative_to(source))


def inno_setup() -> Path:
    compiler = shutil.which("ISCC.exe") or shutil.which("ISCC")
    if compiler:
        return Path(compiler)
    candidates = []
    for variable in ("LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)"):
        root = os.environ.get(variable)
        if root:
            candidates.append(Path(root) / "Programs" / "Inno Setup 6" / "ISCC.exe")
            candidates.append(Path(root) / "Inno Setup 6" / "ISCC.exe")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise RuntimeError(
        "Inno Setup 6 was not found. Install it with: "
        "winget install --id JRSoftware.InnoSetup -e -s winget"
    )


def main() -> int:
    os.chdir(PROJECT_ROOT)
    app_version = version()
    platform_name, suffix, is_windows = determine_target()
    standalone_executable = f"{APP_NAME}{suffix}"
    portable_executable = f"{APP_NAME}-{app_version}-{platform_name}{suffix}"

    run("uv", "sync", "--locked", "--group", "dev")
    shutil.rmtree(DIST_DIR, ignore_errors=True)
    WORK_DIR.mkdir(parents=True)

    print(f"Building {APP_NAME} v{app_version} for {platform_name}")
    standalone = nuitka_build("standalone", standalone_executable, is_windows)
    bundle = DIST_DIR / f"{APP_NAME}-{app_version}-{platform_name}.zip"
    make_zip(standalone.parent, bundle)

    portable = nuitka_build("onefile", portable_executable, is_windows)
    if is_windows:
        installer = DIST_DIR / f"{APP_NAME}-{app_version}-Setup-x64.exe"
        run(
            str(inno_setup()),
            f"/DMyAppVersion={app_version}",
            f"/O{DIST_DIR}",
            str(PROJECT_ROOT / "installer" / "OledHero.iss"),
        )
        if not installer.is_file():
            raise RuntimeError(f"Installer was not created: {installer}")

    print("\nBuild completed:")
    print(f"  ZIP bundle:  {bundle}")
    print(f"  Executable:  {portable}")
    if is_windows:
        print(f"  Installer:   {installer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
