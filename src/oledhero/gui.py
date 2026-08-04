from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QStatusBar, QVBoxLayout, QWidget

from oledhero.gui.theme import APP_STYLESHEET
from oledhero.version import __version__


class GlobalActions(QWidget):
    """Action bar at the top right of the main window"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("globalActions")
        self.setMinimumWidth(260)


class DisplaySelector(QWidget):
    """Central area of the main window with display preview and selection"""

    _BACKGROUND_LOGO_OPACITY = 0.35

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("displaySelector")
        self._background_logo = QPixmap(Path(__file__).parent.parent / "assets" / "OledHero.svg")
        self._scaled_background_logo = None

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        bounds = QRectF(self.rect())
        bounds.adjust(
            bounds.width() * 0.05,
            bounds.height() * 0.05,
            -bounds.width() * 0.05,
            -bounds.height() * 0.05,
        )
        painter = QPainter(self)
        self._draw_background_logo(painter, bounds)

    def _draw_background_logo(self, painter: QPainter, bounds: QRectF) -> None:
        if self._background_logo.isNull():
            return

        logo_size = (
            bounds.size()
            .toSize()
            .scaled(
                int(bounds.width()),
                int(bounds.height()),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        )
        cached = self._scaled_background_logo
        if cached is None or cached[0] != logo_size:
            cached = (
                logo_size,
                self._background_logo.scaled(
                    logo_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ),
            )
            self._scaled_background_logo = cached

        logo = cached[1]
        target = QRectF(0, 0, logo.width(), logo.height())
        target.moveCenter(bounds.center())
        painter.save()
        painter.setOpacity(self._BACKGROUND_LOGO_OPACITY)
        painter.drawPixmap(target, logo, QRectF(logo.rect()))
        painter.restore()


class DisplaySettings(QFrame):
    """Right panel of the main window with display settings"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("displaySettings")
        self.setFixedWidth(475)


class AppStatusBar(QStatusBar):
    """Stat"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setSizeGripEnabled(True)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OledHero")
        self.resize(1400, 880)

        icon_path = Path(__file__).with_name("assets") / "OledHero.ico"
        self.setWindowIcon(QIcon(str(icon_path)))

        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(18, 16, 18, 12)
        layout.setSpacing(12)

        header = QHBoxLayout()
        branding = QVBoxLayout()
        branding.setSpacing(0)

        title = QLabel("OledHero")
        title.setObjectName("title")
        branding.addWidget(title)

        version = QLabel(f"v{__version__}")
        version.setObjectName("version")
        branding.addWidget(version)

        header.addLayout(branding)
        header.addStretch()
        header.addWidget(GlobalActions(central_widget))
        layout.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(14)
        body.addWidget(DisplaySelector(central_widget), 1)
        body.addWidget(DisplaySettings(central_widget))
        layout.addLayout(body, 1)

        self.setCentralWidget(central_widget)
        self.setStatusBar(AppStatusBar(self))
        self.setStyleSheet(APP_STYLESHEET)


def main(argv: list[str] | None = None) -> int:
    application = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
