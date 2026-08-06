import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QStatusBar, QVBoxLayout, QWidget

from oledhero.display import DisplayManagerProtocol
from oledhero.display_controller.monitorcontrol_controller import MonitorControlProvider
from oledhero.display_metadata.pyside6_metadata import PySide6MetadataProvider
from oledhero.displaymanager import DisplayManager
from oledhero.gui.display_selector import DisplaySelector
from oledhero.gui.theme import APP_STYLESHEET
from oledhero.version import __version__


class GlobalActions(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("globalActions")
        self.setMinimumWidth(260)


class DisplaySettings(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("displaySettings")
        self.setFixedWidth(475)


class AppStatusBar(QStatusBar):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setSizeGripEnabled(False)


class MainWindow(QMainWindow):
    def __init__(self, display_manager: DisplayManagerProtocol | None = None) -> None:
        super().__init__()
        self.setWindowTitle("OledHero")
        self.setFixedSize(1400, 880)
        self._display_manager = display_manager or DisplayManager(
            MonitorControlProvider(),
            PySide6MetadataProvider(),
        )

        icon_path = Path(__file__).parent.parent / "assets" / "OledHero.ico"
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
        body.addWidget(DisplaySelector(self._display_manager, central_widget), 1)
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
