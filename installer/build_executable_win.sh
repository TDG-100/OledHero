#!/usr/bin/env sh
set -eu

APP_VERSION="$(uv run python -c 'from oledhero.version import __version__; print(__version__)')"

build_oledhero() {
    uv run nuitka \
        --standalone \
        --assume-yes-for-downloads \
        --python-flag=-m \
        --windows-console-mode=disable \
        --enable-plugin=pyside6 \
        --windows-icon-from-ico=src/oledhero/assets/OledHero.ico \
        --include-data-dir=src/oledhero/assets=oledhero/assets \
        --include-data-files=LICENSE=LICENSE \
        --include-data-dir=licenses=licenses \
        "$@" \
        src/oledhero
}

# Multi-file package used by the installer.
build_oledhero \
    --output-dir=dist/installer \
    --output-filename=OledHero.exe

# Single-file executable.
build_oledhero \
    --onefile \
    --output-dir=dist \
    --output-filename="OledHero-${APP_VERSION}-Portable.exe"
