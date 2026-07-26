#!/usr/bin/env sh
set -eu

# Always run from repository root
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

APP_VERSION="$(uv run oledhero --version)"

case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
        PLATFORM="windows"
        EXECUTABLE_NAME="OledHero.exe"
        ;;
    Linux*)
        PLATFORM="linux"
        EXECUTABLE_NAME="OledHero"
        ;;
    *)
        echo "Unsupported operating system: $(uname -s)" >&2
        exit 1
        ;;
esac

echo ""
echo "##############################################"
echo "Building OledHero v${APP_VERSION} for ${PLATFORM}"
echo "##############################################"
echo ""

# Cleanup previous builds
rm -rf dist
mkdir -p dist

build_oledhero() {
    if [ "$PLATFORM" = "windows" ]; then
        set -- \
            --windows-console-mode=attach \
            --windows-icon-from-ico=src/oledhero/assets/OledHero.ico \
            "$@"
    fi

    uv run nuitka \
        --assume-yes-for-downloads \
        --python-flag=-m \
        --enable-plugin=pyside6 \
        --include-data-dir=src/oledhero/assets=oledhero/assets \
        --include-data-files=LICENSE=LICENSE \
        --include-data-dir=licenses=licenses \
        "$@" \
        src/oledhero
}

# Multi-file package used by the installer.
build_oledhero \
    --standalone \
    --output-dir=dist/installer \
    --output-filename="$EXECUTABLE_NAME"

# Single-file executable.
build_oledhero \
    --onefile \
    --output-dir=dist \
    --output-filename="$EXECUTABLE_NAME"

echo ""
echo "##############################################"
echo "               Build completed                "
echo "##############################################"
echo ""

if [ "$PLATFORM" = "windows" ]; then
    echo "Standalone: dist/installer/oledhero.dist/OledHero.exe"
    echo "Portable:   dist/OledHero.exe"
else
    echo "Standalone: dist/installer/oledhero.dist/OledHero"
    echo "Portable:   dist/OledHero"
fi