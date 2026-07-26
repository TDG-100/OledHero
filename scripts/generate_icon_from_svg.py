"""Render the bundled SVG application icon as a ICO resource."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = PROJECT_ROOT / "src" / "oledhero" / "assets" / "OledHero.svg"
ICO_PATH = SVG_PATH.with_suffix(".ico")
ICON_SIZE = 256


def main() -> None:
    renderer = QSvgRenderer(str(SVG_PATH))
    if not renderer.isValid():
        raise ValueError(f"Unable to render SVG icon: {SVG_PATH}")

    image = QImage(ICON_SIZE, ICON_SIZE, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    if not image.save(str(ICO_PATH)):
        raise OSError(f"Unable to write Windows icon: {ICO_PATH}")


if __name__ == "__main__":
    main()
