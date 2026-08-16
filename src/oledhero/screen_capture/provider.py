from dataclasses import dataclass
from typing import Protocol

from PySide6.QtGui import QImage

from oledhero.display import Display


@dataclass(frozen=True, slots=True)
class Screenshot:
    """Captured image with capture timestamp."""

    image: QImage
    timestamp_ns: int


class ScreenshotProvider(Protocol):
    """
    Shared screenshot provider with caching.
    """

    def get_screenshot(self, display: Display) -> Screenshot | None:
        """Return an available screenshot for one display."""
