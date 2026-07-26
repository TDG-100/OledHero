"""Run the checks and publishing steps used by GitHub Actions locally."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from build import (
    determine_target,
    release_artifact_paths,
    verify_release_artifacts,
    version,
)

APP_NAME = "OledHero"


def release_asset_names(app_version: str) -> tuple[str, ...]:
    return (
        f"{APP_NAME}-{app_version}-Windows-x64.zip",
        f"{APP_NAME}-{app_version}-Windows-x64.exe",
        f"{APP_NAME}-{app_version}-Setup-x64.exe",
        f"{APP_NAME}-{app_version}-Linux-x64.zip",
        f"{APP_NAME}-{app_version}-Linux-x64",
    )


def run(*command: str, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), file=sys.stderr, flush=True)
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        text=True,
        capture_output=capture_output,
    )


def git(*arguments: str) -> str:
    result = run("git", *arguments, capture_output=True)
    return result.stdout.strip()


def lint() -> None:
    run(sys.executable, "-m", "ruff", "check", ".")


def build_ref() -> None:
    print(f"ref={git('rev-parse', 'HEAD')}")


def verify_release(tag: str, main_ref: str) -> None:
    if not tag.startswith("v"):
        raise ValueError("Release tags must start with v (for example, v0.1.0).")
    if tag != f"v{version()}":
        raise ValueError(
            f"Release tag {tag!r} does not match application version v{version()}."
        )

    try:
        tag_commit = git("rev-parse", f"{tag}^{{commit}}")
    except subprocess.CalledProcessError as error:
        raise ValueError(
            f"Release tag {tag!r} does not exist locally. Fetch it with "
            "'git fetch --tags' or create it before verifying the release."
        ) from error

    try:
        main_commit = git("rev-parse", main_ref)
    except subprocess.CalledProcessError as error:
        raise ValueError(
            f"Main reference {main_ref!r} does not exist locally. Fetch it or "
            "pass --main-ref with an available main branch reference."
        ) from error
    if tag_commit != main_commit:
        raise ValueError(f"Release tag {tag!r} must point directly to {main_ref}.")


def verify_artifacts() -> None:
    platform_name, suffix, is_windows = determine_target()
    verify_release_artifacts(
        release_artifact_paths(version(), platform_name, suffix, is_windows)
    )


def publish_release(tag: str, assets_dir: Path, dry_run: bool) -> None:
    assets_by_name = {
        path.name: path for path in assets_dir.iterdir() if path.is_file()
    }
    required_assets = release_asset_names(version())
    missing = [name for name in required_assets if name not in assets_by_name]
    if missing:
        formatted_names = "\n  ".join(missing)
        raise RuntimeError(
            f"Release assets are incomplete in {assets_dir}; missing:\n  {formatted_names}"
        )
    assets = [assets_by_name[name] for name in required_assets]

    if dry_run:
        print(f"Would publish release {tag!r} with:")
        for asset in assets:
            print(f"  {asset}")
        return

    if not shutil.which("gh"):
        raise RuntimeError("GitHub CLI (gh) must be installed to publish a release.")

    asset_paths = [str(path) for path in assets]
    release_exists = subprocess.run(
        ["gh", "release", "view", tag], cwd=PROJECT_ROOT, check=False
    ).returncode == 0
    if release_exists:
        run("gh", "release", "upload", tag, *asset_paths, "--clobber")
    else:
        run("gh", "release", "create", tag, *asset_paths, "--title", tag, "--generate-notes")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("lint", help="Run the project linter.")
    commands.add_parser("build-ref", help="Print the checked-out commit as a GitHub output.")

    release_parser = commands.add_parser(
        "verify-release", help="Verify that a version tag points directly to main."
    )
    release_parser.add_argument("--tag", required=True)
    release_parser.add_argument("--main-ref", default="origin/main")

    commands.add_parser("verify-artifacts", help="Verify built artifacts for this platform.")

    publish_parser = commands.add_parser(
        "publish-release", help="Create or update a GitHub release with local assets."
    )
    publish_parser.add_argument("--tag", required=True)
    publish_parser.add_argument("--assets-dir", type=Path, required=True)
    publish_parser.add_argument("--dry-run", action="store_true")

    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    if arguments.command == "lint":
        lint()
    elif arguments.command == "build-ref":
        build_ref()
    elif arguments.command == "verify-release":
        verify_release(arguments.tag, arguments.main_ref)
    elif arguments.command == "verify-artifacts":
        verify_artifacts()
    elif arguments.command == "publish-release":
        publish_release(arguments.tag, arguments.assets_dir, arguments.dry_run)
    else:
        raise AssertionError(f"Unknown command: {arguments.command}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    except subprocess.CalledProcessError as error:
        print(f"error: command failed with exit code {error.returncode}", file=sys.stderr)
        raise SystemExit(error.returncode) from error
