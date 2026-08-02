from collections.abc import Sequence
from typing import Protocol


class DDCCIUnsupportedError(RuntimeError):
    """Raised when a monitor does not support DDC/CI brightness control."""


class DDCCIController(Protocol):
    """Controls one physical monitor discovered through DDC/CI."""

    def is_supported(self) -> bool:
        """Check if the monitor supports DDC/CI brightness control."""

    def get_brightness(self) -> int:
        """Read the monitor current brightness."""

    def set_brightness(self, brightness: int) -> None:
        """Set the monitor brightness to a value in a range from 0 to 100."""


class ControllerProvider(Protocol):
    """Discovers available DDC/CI controllers."""

    def list_ddcci_controllers(self) -> Sequence[DDCCIController]:
        """Return one controller for each monitor reachable via DDC/CI."""
