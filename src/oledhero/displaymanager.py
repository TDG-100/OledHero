from collections.abc import Sequence
from dataclasses import dataclass

import rapidfuzz

from oledhero.display import Display, DisplayManagerProtocol, DisplayMetadata
from oledhero.display_controller.controller_provider import (
    ControllerProvider,
    DDCCIController,
    DDCCIUnsupportedError,
)
from oledhero.display_metadata.metadata_provider import DisplayMetadataProvider

FUZZY_MATCH_SCORE_CUTOFF = 80.0


@dataclass(frozen=True)
class DisplayControllerPair:
    display: Display
    controller: DDCCIController


class DisplayManager(DisplayManagerProtocol):
    def __init__(self, controller_provider: ControllerProvider, metadata_provider: DisplayMetadataProvider) -> None:
        self._controller_provider = controller_provider
        self._metadata_provider = metadata_provider
        self._displays: dict[str, DisplayControllerPair] = {}

    def list_displays(self) -> list[Display]:
        self._displays = self._list_display_controller_pairs()
        return [display_controller_pair.display for display_controller_pair in self._displays]

    def get_brightness(self, display_id: str) -> int:
        return self._get_controller(display_id).get_brightness()

    def set_brightness(self, display_id: str, brightness: int) -> None:
        self._get_controller(display_id).set_brightness(brightness)

    def _get_controller(self, display_id: str) -> DDCCIController:
        if display_id not in self._controllers_by_display_id:
            displays = self.list_displays()
            if display_id not in {display.id for display in displays}:
                raise ValueError(f"unknown display id: {display_id}")

        try:
            return self._controllers_by_display_id[display_id]
        except KeyError as error:
            raise DDCCIUnsupportedError(f"display does not support DDC/CI brightness control: {display_id}") from error

    def _list_display_controller_pairs(self) -> list[DisplayControllerPair]:
        metadata = list(self._metadata_provider.list_display_metadata())
        controllers = list(self._controller_provider.list_ddcci_controllers())

        displays: list[DisplayControllerPair] = []
        for c_idx, m_idx in self._pair_controllers(metadata, controllers):
            compatible = controllers[c_idx].is_supported()
            brightness = controllers[c_idx].get_brightness() if compatible else None

            displays.append(
                DisplayControllerPair(
                    display=Display(
                        id=metadata[m_idx].identity,
                        name=metadata[m_idx].edid_name,
                        metadata=metadata[m_idx],
                        brightness=brightness,
                        compatible=compatible,
                    ),
                    controller=controllers[c_idx],
                )
            )

        return displays

    def _pair_controllers(self, metadata: Sequence[DisplayMetadata], controllers: Sequence[DDCCIController]) -> list[tuple[int, int]]:
        """Pair controllers based on identification hints and metadata."""

        pairs: list[tuple[int, int]] = []
        paired_metadata_indexes: set[int] = set()
        paired_controller_indexes: set[int] = set()

        # Try to match using hints, candidates are [score, controller index, metadata index].
        candidates: list[tuple[int, int, int]] = []
        for controller_index, controller in enumerate(controllers):
            hints = controller.identification_hints()
            for metadata_index, display_metadata in enumerate(metadata):
                candidates.append(
                    (
                        self._match_score(display_metadata, hints),
                        controller_index,
                        metadata_index,
                    )
                )

        # Sort by score
        candidates.sort(key=lambda candidate: (-candidate[0], candidate[1], candidate[2]))

        # This will pair the best match first as list is sorted by score
        for score, controller_index, metadata_index in candidates:
            if score == 0:
                # No hint matches
                break

            if controller_index in paired_controller_indexes or metadata_index in paired_metadata_indexes:
                # Already paired
                continue

            # Make new pair
            pairs.append((metadata_index, controller_index))
            paired_metadata_indexes.add(metadata_index)
            paired_controller_indexes.add(controller_index)

        # Fallback to index pairing for remaining data
        remaining_metadata = [index for index in range(len(metadata)) if index not in paired_metadata_indexes]
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
