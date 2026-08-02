# OLEDHero

OLEDHero helps protect your OLED display from burn-in without alarming the king (anti-cheat) or annoying the peasants and vassals (you).

## Goals

- Avoid triggering anti-cheat systems, so OLEDHero does not become the villain.
- Control monitor brightness directly through DDC/CI.
- Avoid overlays, gamma adjustments, and capture hooks.
- Reduce the risk of burn-in by lowering brightness when static content is displayed.
- Protect and configure each monitor independently.

## Distant Goals

### Hardware Accessory

One future idea is a small USB-powered PCB with distance and presence sensors.
It would detect whether someone is actually sitting in front of a monitor and could be configured like any other activity detector.
The idea is inspired by the presence-detection and burn-in protection features used by some monitor manufacturers.

# Development

## Development Environment

The Python project is managed with [uv](https://docs.astral.sh/uv/getting-started/installation/) and built with [Nuitka](https://nuitka.net/).

### Workspace Setup

Prerequisites:
- [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Install VS Code](https://code.visualstudio.com/) or any other IDE you like

Clone the repository and ooppen the folder in VS Code:
```
git clone https://github.com/TDG-100/OledHero oledhero
```

Install all python dependencies and create the python virtual environment using uv.
```
uv sync
```

It is also advisable to install the recommended extensions for VS Code when prompted to.

# Building Executables

## Prerequisites:

### Windows
Windows builds require [InnoSetup](https://github.com/jrsoftware/issrc) for
the installer. Install it once using:
```
winget install --id JRSoftware.InnoSetup -e -s winget -i
```

### Linux

Linux requires some standard build tools. On Debian/Ubuntu install them using:
```
sudo apt install build-essential patchelf
```

## Build Script

Run the `build.py` script to build
- `OledHero-<version>-<platform>.zip` — portable ZIP bundle.
- `OledHero-<version>-Windows-x64.exe` or
  `OledHero-<version>-Linux-x64` — single-file executable.
- Windows only: `OledHero-<version>-Setup-x64.exe` — Inno Setup installer.

This script builds native applications. Meaning Windows applications are built on Windows and Linux applications on Linux, there is no cross-compilation for nuitka.

```
uv run python scripts/build.py
```

## Manual Builds
### Windows:

You can find the executable in
`dist/OledHero.exe` after building with Nuitka:

```
uv run --locked nuitka \
  --assume-yes-for-downloads \
  --python-flag=-m \
  --enable-plugin=pyside6 \
  --include-data-dir=src/oledhero/assets=oledhero/assets \
  --include-data-files=LICENSE=LICENSE \
  --include-data-dir=licenses=licenses \
  --onefile \
  --output-dir=dist \
  --output-filename=OledHero.exe \
  --windows-console-mode=attach \
  --windows-icon-from-ico=src/oledhero/assets/OledHero.ico \
  src/oledhero
```

### Linux:

You can find the executable in
`dist/OledHero` after building with Nuitka:

```
uv run --locked nuitka \
  --assume-yes-for-downloads \
  --python-flag=-m \
  --enable-plugin=pyside6 \
  --include-data-dir=src/oledhero/assets=oledhero/assets \
  --include-data-files=LICENSE=LICENSE \
  --include-data-dir=licenses=licenses \
  --onefile \
  --output-dir=dist \
  --output-filename=OledHero \
  src/oledhero
```

## Continuous Integration and Releases

The pipeline will automatically builds artifacts for Linux and Windows when a tag in the from of `vX.X.X` is pushed to the main branch.
