from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from PySide6.QtCore import SignalInstance
from PySide6.QtGui import QImage

from oledhero.display import Display


@dataclass(frozen=True, slots=True)
class Screenshot:
    """
    Screenshot with display metadata.
    """
    
    image: QImage
    timestamp_ns: int


class ScreenshotProvider(Protocol):

    def request_screenshots(self) -> list[Screenshot]:
        """Request screenshots"""
