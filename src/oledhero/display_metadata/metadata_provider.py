from collections.abc import Sequence
from typing import Protocol

from oledhero.display import DisplayMetadata


class DisplayMetadataError(RuntimeError):
    """Raised when display metadata cannot be discovered."""


class DisplayMetadataProvider(Protocol):
    """Discovers displays and gathers their metadata."""

    def list_display_metadata(self) -> Sequence[DisplayMetadata]:
        """Return one metadata record for each connected display."""
