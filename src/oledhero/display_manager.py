from typing import Self

from oledhero.display import (
    Display,
    DisplayManagerProtocol,
    DisplayMetadata,
)
from oledhero.display_controller.controller_provider import (
    DDCCIController,
    ControllerProvider,
)
from oledhero.display_metadata.metadata_provider import DisplayMetadataProvider


class DisplayNotFoundError(ValueError):
    """Raised when an operation refers to an undiscovered display."""


class DisplayNotCompatibleError(ValueError):
    """Raised when an operation calls DDC/CI on an incompatible display."""


class DisplayManager(DisplayManagerProtocol):
    def __init__(
        self,
        metadata_provider: DisplayMetadataProvider,
        controller_provider: ControllerProvider,
    ) -> None:
        self._metadata_provider = metadata_provider
        self._controller_provider = controller_provider
        self._displays: list[Display] = {}
        self._controllers: list[DDCCIController] = {}

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._displays = []
        self._controllers = []

    def _name_monitor(self, idx: int, metadata: DisplayMetadata, controller: DDCCIController) -> str:
        if metadata is None:
            return "unknown"
        return metadata.edid_name or metadata.name

    def list_displays(self) -> list[Display]:
        self._controllers = self._controller_provider.list_ddcci_controllers()
        metadata = self._metadata_provider.list_display_metadata()

        # TODO check if lists are actually same length

        # match controllers to metadata - lists are aligned by index
        self._displays = []
        for idx, (mdata, controller) in enumerate(zip(metadata, self._controllers), start=1):
            is_compatible = controller.is_supported()
            dp = Display(
                id=f"display-{idx}",  # id used by DDC/CI controller
                name=self._name_monitor(idx, mdata, controller),
                metadata=mdata,
                brightness=controller.get_brightness() if is_compatible else None,
                compatible=is_compatible,
            )
            self._displays.append(dp)
        return self._displays

    def get_brightness(self, display_id: str) -> int | None:
        controller = self._find_controller(display_id)
        return controller.get_brightness()

    def set_brightness(self, display_id: str, brightness: int) -> None:
        controller = self._find_controller(display_id)
        return controller.set_brightness(brightness)

    def _find_controller(self, display_id: str) -> DDCCIController:
        # TODO this is pretty dumb, i could just use the index instead but this could be used for identification in ui
        for idx, monitor in enumerate(self._controllers, start=1):
            if display_id == f"display-{idx}":
                return monitor
        raise DisplayNotFoundError(f"Display with id {display_id} not found.")
