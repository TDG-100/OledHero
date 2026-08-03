from PySide6.QtGui import QGuiApplication, QScreen

from oledhero.display import DisplayGeometry, DisplayMetadata
from oledhero.display_metadata.metadata_provider import (
    DisplayMetadataError,
    DisplayMetadataProvider,
)


class QtDisplayError(DisplayMetadataError):
    """Raised when Qt cannot report connected displays."""


class PySide6MetadataProvider(DisplayMetadataProvider):
    def __init__(self) -> None:
        pass

    def list_display_metadata(self) -> list[DisplayMetadata]:

        # only spawn application if necessary (try to use existing one)
        application = QGuiApplication.instance()
        if application is None or not hasattr(application, "screens"):
            application = QGuiApplication([])

        primary_screen = application.primaryScreen()
        displays = [
            self._metadata_from_qscreen(screen, screen == primary_screen)
            for screen in application.screens()
        ]  # fmt: skip

        return displays

    def _metadata_from_qscreen(self, screen: QScreen, is_primary: bool) -> DisplayMetadata:

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
