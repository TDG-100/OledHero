from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0

    try:
        output = handler(args)
        if output:
            print(output)
        return 0
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oledhero",
        description="OLEDHero",
    )

    parser.add_argument(
        "--version",
        action="store_const",
        const=_cmd_version,
        dest="handler",
        help="Display the OLEDHero version.",
    )

    subparsers = parser.add_subparsers(dest="command")

    brightness = subparsers.add_parser("brightness", help="Brightness commands.")
    brightness.add_argument("--set", type=int, required=False, help="Brightness level (0-100).")
    brightness.set_defaults(handler=_cmd_brightness)

    metadata = subparsers.add_parser("metadata", help="Display available metadata")
    metadata.set_defaults(handler=_cmd_metadata)

    displays = subparsers.add_parser(
        "displays",
        aliases=["display"],
        help="Display paired metadata and controller information.",
    )
    displays.set_defaults(handler=_cmd_displays)

    return parser


def _cmd_version(args: argparse.Namespace) -> str:
    from oledhero.version import __version__

    return __version__


def _cmd_brightness(args: argparse.Namespace) -> str:
    from oledhero.display_controller.monitorcontrol_controller import (
        MonitorControlController,
        MonitorControlProvider,
    )

    monitor_controllers: list[MonitorControlController] = MonitorControlProvider().list_ddcci_controllers()

    if args.set is not None:
        for controller in monitor_controllers:
            controller.set_brightness(args.set)
        return f"Brightness set to {args.set}."

    brightness_levels = [controller.get_brightness() for controller in monitor_controllers]

    return "\n".join(f"Monitor {i + 1}: {brightness}%" for i, brightness in enumerate(brightness_levels))


def _cmd_metadata(args: argparse.Namespace) -> str:
    from oledhero.display_metadata.pyside6_metadata import PySide6MetadataProvider

    metadata = PySide6MetadataProvider().list_display_metadata()
    return "\n\n".join(f"Display {index}\n{display}" 
                       for index, display in enumerate(metadata, start=1)
                       )  # fmt: skip


def _cmd_displays(args: argparse.Namespace) -> str:
    from oledhero.display_controller.monitorcontrol_controller import MonitorControlProvider
    from oledhero.display_metadata.pyside6_metadata import PySide6MetadataProvider
    from oledhero.displaymanager import DisplayManager

    displays = DisplayManager(
        MonitorControlProvider(),
        PySide6MetadataProvider(),
    ).list_displays()

    return "\n\n".join(f"Display {index}\n{display}" for index, display in enumerate(displays, start=1))
