from collections.abc import Sequence
from typing import Protocol

from oledhero.display import Screen


class ScreenProvider(Protocol):
    """Screen provider abstraction used to discover available screens."""

    def list_screens(self) -> Sequence[Screen]:
        """Return one screen object for each connected display."""
