import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QStatusBar, QVBoxLayout, QWidget

from oledhero.display import DisplayManagerProtocol
from oledhero.display_controller.monitorcontrol_controller import MonitorControlProvider
from oledhero.displaymanager import DisplayManager
from oledhero.gui.display_selector import DisplaySelector
from oledhero.gui.display_settings import DisplaySettings
from oledhero.gui.theme import APP_STYLESHEET
from oledhero.screen_capture import DirectScreenshotProvider, ScreenshotProvider
from oledhero.screen_discovery import PySide6ScreenProvider
from oledhero.version import __version__


class GlobalActions(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("globalActions")
        self.setMinimumWidth(260)


class AppStatusBar(QStatusBar):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setSizeGripEnabled(False)


class MainWindow(QMainWindow):
    def __init__(
        self,
        display_manager: DisplayManagerProtocol | None = None,
        screenshot_provider: ScreenshotProvider | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("OledHero")
        self.setFixedSize(1400, 880)
        self._display_manager = display_manager or DisplayManager(
            MonitorControlProvider(),
            PySide6ScreenProvider(),
        )
        self._screenshot_provider = screenshot_provider or DirectScreenshotProvider()

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
        display_selector = DisplaySelector(
            self._display_manager,
            central_widget,
            screenshot_provider=self._screenshot_provider,
        )
        display_settings = DisplaySettings(central_widget, display_selector.selected_display)
        display_selector.displaySelected.connect(display_settings.set_display)
        body.addWidget(display_selector, 1)
        body.addWidget(display_settings)
        layout.addLayout(body, 1)

        self.setCentralWidget(central_widget)
        self.setStatusBar(AppStatusBar(self))
        self.setStyleSheet(APP_STYLESHEET)


def main(argv: list[str] | None = None) -> int:
    application = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()
