import monitorcontrol
from monitorcontrol import Monitor, VCPError

from oledhero.display_controller.controller_provider import (
    ControllerProvider,
    DDCCIController,
    DDCCIUnsupportedError,
)

VCP_COMMAND_BRIGHTNESS = 0x10


class MonitorControlController(DDCCIController):
    def __init__(self, monitor_id, monitor):
        super().__init__()
        self._monitor_id: int = monitor_id
        self._monitor: Monitor = monitor
        self._max_brightness: int | None = None
        self._is_supported: bool | None = None
        self._identification_hints: list[str] = []

        # check for capability, max brightness and model hints
        self._is_supported = self.is_supported()
        self.get_brightness() if self._is_supported else None
        self._read_identification_hints() if self._is_supported else None

    def is_supported(self) -> bool:
        try:
            with self._monitor:
                capabilities = self._monitor.get_vcp_capabilities()
                self._is_supported = VCP_COMMAND_BRIGHTNESS in capabilities.get("vcp", {})
                return self._is_supported
        except VCPError:
            return False

    def identification_hints(self) -> list[str]:
        return self._identification_hints

    def get_brightness(self) -> int:
        try:
            with self._monitor:
                current, maximum = self._monitor.vcp.get_vcp_feature(VCP_COMMAND_BRIGHTNESS)
                self._max_brightness = maximum
            return current
        except VCPError as error:
            raise DDCCIUnsupportedError(f"Could not read brightness: {error}") from error

    def set_brightness(self, brightness: int) -> None:

        if brightness < 0 or brightness > 100:
            raise ValueError("brightness must be between 0 and 100")

        # Map brightness to monitor range
        monitor_brightness = int((brightness / 100) * self._max_brightness)

        try:
            with self._monitor:
                self._monitor.set_luminance(monitor_brightness)
        except VCPError as error:
            raise DDCCIUnsupportedError(f"Could not set brightness: {error}") from error

    def _read_identification_hints(self) -> list[str]:
        description = getattr(getattr(self._monitor, "vcp", None), "description", "")
        if description and description not in self._identification_hints:
            self._identification_hints.append(str(description))

        try:
            with self._monitor:
                capabilities = self._monitor.get_vcp_capabilities()
                model = capabilities.get("model")
                if model and model not in self._identification_hints:
                    self._identification_hints.append(str(model))
                return self._identification_hints
        except VCPError:
            return False


class MonitorControlProvider(ControllerProvider):
    def list_ddcci_controllers(self) -> list[DDCCIController]:
        return [
            MonitorControlController(idx, monitor) 
            for idx, monitor in enumerate(monitorcontrol.get_monitors())
        ]  # fmt: skip
