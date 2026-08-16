from PySide6.QtGui import QGuiApplication, QImage, QScreen

from oledhero.display import DisplayGeometry, DisplayMetadata, Screen
from oledhero.screen_discovery.provider import ScreenProvider


class QtScreen(Screen):
    """Abstraction layer over QtScreens to make testing easier later on."""

    def __init__(self, screen: QScreen, is_primary: bool) -> None:
        self._screen = screen
        self._metadata = self._metadata_from_qscreen(screen, is_primary)

    @property
    def metadata(self) -> DisplayMetadata:
        return self._metadata

    def grab_image(self) -> QImage:
        return self._screen.grabWindow(0).toImage()

    @staticmethod
    def _metadata_from_qscreen(screen: QScreen, is_primary: bool) -> DisplayMetadata:
        geometry = screen.geometry()
        return DisplayMetadata(
            geometry=DisplayGeometry(
                x=geometry.x(),
                y=geometry.y(),
                width=geometry.width(),
                height=geometry.height(),
            ),
            is_primary=is_primary,
            name=screen.name() or "",
            manufacturer=screen.manufacturer() or "",
            model=screen.model() or "",
            serial_number=screen.serialNumber() or "",
        )


class PySide6ScreenProvider(ScreenProvider):
    """Discover connected screens through the active Qt application."""

    def list_screens(self) -> list[Screen]:
        application = QGuiApplication.instance()
        if application is None or not hasattr(application, "screens"):
            application = QGuiApplication([])

        primary_screen = application.primaryScreen()
        return [QtScreen(screen, screen == primary_screen) for screen in application.screens()]
