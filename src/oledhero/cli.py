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

    hello_world = subparsers.add_parser("hello", help="Display a hello message.")
    hello_world.add_argument("--name", required=True, help="Name of the user to greet.")
    hello_world.set_defaults(handler=_cmd_hello)

    goodbye = subparsers.add_parser("bye", help="Display a goodbye message.")
    goodbye.set_defaults(handler=_cmd_goodbye)

    brightness = subparsers.add_parser("brightness", help="Brightness commands.")
    brightness.add_argument(
        "--set", type=int, required=False, help="Brightness level (0-100)."
    )
    brightness.set_defaults(handler=_cmd_brightness)

    return parser


def _cmd_hello(args: argparse.Namespace) -> str:
    return f"Hi {args.name}, I'm OledHero!"


def _cmd_goodbye(args: argparse.Namespace) -> str:
    return "Sad to see you go!"


def _cmd_version(args: argparse.Namespace) -> str:
    from oledhero.version import __version__


def _cmd_brightness(args: argparse.Namespace) -> str:
    from oledhero.display_controller.monitorcontrol_controller import (
        MonitorControlProvider,
        MonitorControlController,
    )

    monitor_controllers:list[MonitorControlController] = MonitorControlProvider().list_ddcci_controllers()

    if args.set is not None:
        for controller in monitor_controllers:
            controller.set_brightness(args.set)
        return f"Brightness set to {args.set}."

    return str([controller.get_brightness() for controller in monitor_controllers])
