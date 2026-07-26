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