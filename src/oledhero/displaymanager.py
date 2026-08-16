from collections.abc import Sequence
from dataclasses import dataclass

import rapidfuzz

from oledhero.display import Display, DisplayManagerProtocol, DisplayMetadata, Screen
from oledhero.display_controller.controller_provider import (
    ControllerProvider,
    DDCCIController,
    DDCCIUnsupportedError,
)
from oledhero.screen_discovery.provider import ScreenProvider

FUZZY_MATCH_SCORE_CUTOFF = 80.0


@dataclass(frozen=True)
class DisplayControllerPair:
    display: Display
    controller: DDCCIController | None


class DisplayManager(DisplayManagerProtocol):
    def __init__(self, controller_provider: ControllerProvider, screen_provider: ScreenProvider) -> None:
        self._controller_provider = controller_provider
        self._screen_provider = screen_provider
        self._displays: dict[str, DisplayControllerPair] = {}

    def list_displays(self) -> list[Display]:
        pairs = self._list_display_controller_pairs()
        self._displays = {pair.display.id: pair for pair in pairs}
        return [pair.display for pair in pairs]

    def get_brightness(self, display_id: str) -> int:
        return self._get_controller(display_id).get_brightness()

    def set_brightness(self, display_id: str, brightness: int) -> None:
        self._get_controller(display_id).set_brightness(brightness)

    def _get_controller(self, display_id: str) -> DDCCIController:
        if display_id not in self._displays:
            self.list_displays()
        pair = self._displays.get(display_id)
        if pair is None:
            raise ValueError(f"unknown display id: {display_id}")
        if pair.controller is None or not pair.display.compatible:
            raise DDCCIUnsupportedError(f"display does not support DDC/CI brightness control: {display_id}")
        return pair.controller

    def _list_display_controller_pairs(self) -> list[DisplayControllerPair]:
        screens = list(self._screen_provider.list_screens())
        controllers = list(self._controller_provider.list_ddcci_controllers())

        displays: list[DisplayControllerPair] = []
        for s_idx, c_idx in self._pair_controllers(screens, controllers):
            controller = controllers[c_idx]
            compatible = False
            brightness = None
            if controller is not None and controller.is_supported():
                compatible = controller.is_supported()
                brightness = controller.get_brightness()

            displays.append(
                DisplayControllerPair(
                    display=Display(
                        screen=screens[s_idx],
                        brightness=brightness,
                        compatible=compatible,
                    ),
                    controller=controller,
                )
            )

        return displays

    def _pair_controllers(self, screens: Sequence[Screen], controllers: Sequence[DDCCIController]) -> list[tuple[int, int]]:
        """Pair controllers based on identification hints and metadata."""

        pairs: list[tuple[int, int]] = []
        paired_screen_indexes: set[int] = set()
        paired_controller_indexes: set[int] = set()

        # Try to match using hints, candidates are [score, controller index, screen index].
        candidates: list[tuple[int, int, int]] = []
        for controller_index, controller in enumerate(controllers):
            hints = controller.identification_hints()
            for screen_index, screen in enumerate(screens):
                candidates.append(
                    (
                        self._match_score(screen.metadata, hints),
                        controller_index,
                        screen_index,
                    )
                )

        # Sort by score
        candidates.sort(key=lambda candidate: (-candidate[0], candidate[1], candidate[2]))

        # This will pair the best match first as list is sorted by score
        for score, controller_index, screen_index in candidates:
            if score == 0:
                # No hint matches
                break

            if controller_index in paired_controller_indexes or screen_index in paired_screen_indexes:
                # Already paired
                continue

            # Make new pair
            pairs.append((screen_index, controller_index))
            paired_screen_indexes.add(screen_index)
            paired_controller_indexes.add(controller_index)

        # Fallback to index pairing for remaining data
        remaining_metadata = [index for index in range(len(screens)) if index not in paired_screen_indexes]
        remaining_controllers = [index for index in range(len(controllers)) if index not in paired_controller_indexes]

        # Match by orignal index first (as providers returned them)
        for controller_index in remaining_controllers:
            if controller_index in remaining_metadata:
                pairs.append((controller_index, controller_index))
                remaining_metadata.remove(controller_index)
                remaining_controllers.remove(controller_index)

        # Pair all remaining
        pairs.extend(zip(remaining_metadata, remaining_controllers))

        return sorted(pairs)

    def _match_score(self, metadata: DisplayMetadata, hints: list[str]) -> int:
        metadata_identifiers = (metadata.name, metadata.model, metadata.edid_name, metadata.serial_number)

        scores = [rapidfuzz.fuzz.WRatio(hint, identifier) 
                for hint in hints 
                for identifier in metadata_identifiers
                ]  # fmt: skip
        return sum(score for score in scores if score >= FUZZY_MATCH_SCORE_CUTOFF)
