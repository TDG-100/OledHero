from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DisplayGeometry:
    x: int
    y: int
    width: int
    height: int

    def __str__(self) -> str:
        return f"{self.width}x{self.height} at ({self.x}, {self.y})"


@dataclass(frozen=True)
class DisplayMetadata:
    geometry: DisplayGeometry
    is_primary: bool
    name: str
    manufacturer: str
    model: str
    serial_number: str

    def __str__(self) -> str:
        return "\n".join(
            [
                f"  Name:         {self.name or '-'}",
                f"  Manufacturer: {self.manufacturer or '-'}",
                f"  Model:        {self.model or '-'}",
                f"  Serial:       {self.serial_number or '-'}",
                f"  Primary:      {'yes' if self.is_primary else 'no'}",
                f"  Geometry:     {self.geometry}",
            ]
        )

    @property
    def edid_name(self) -> str:
        """A human-readable name based on EDID data."""
        return " ".join(part for part in (self.manufacturer, self.model) if part)

    @property
    def identity(self) -> str:
        """A stable identifier based on the available EDID fields."""
        parts = (self.manufacturer, self.model, self.serial_number)
        return "_".join(part.strip() or "unknown" for part in parts)


@dataclass(frozen=True)
class Display:
    id: str
    name: str
    metadata: DisplayMetadata
    brightness: int | None
    compatible: bool


class DisplayManagerProtocol(Protocol):
    def list_displays(self) -> list[Display]:
        """List all discovered displays."""

    def get_brightness(self, display_id: str) -> int:
        """Read brightness of one display by id."""

    def set_brightness(self, display_id: str, brightness: int) -> None:
        """Set brightness of one display by id."""
