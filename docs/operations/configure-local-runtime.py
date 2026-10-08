#!/usr/bin/env python3
"""Install the Git-managed zpython bundle without selecting live config."""

import argparse
import shutil
import stat
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "--replace-launchers",
        action="store_true",
        help="replace only Git-managed launcher files; profiles are preserved",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "runtime" / "zpython"
    destination = args.destination.resolve()

    destination.mkdir(parents=True, exist_ok=True)
    (destination / "bin").mkdir(exist_ok=True)
    (destination / "profiles").mkdir(exist_ok=True)

    relative_files = (
        Path("bin/zpython"),
        Path("bin/zpython-with-config"),
        Path("activate-zoo.sh"),
    )
    conflicts = [destination / relative for relative in relative_files
                 if (destination / relative).exists()]
    if conflicts and not args.replace_launchers:
        raise SystemExit(
            "Refusing to replace existing launcher(s): {}. Re-run with "
            "--replace-launchers after reviewing the diff.".format(
                ", ".join(str(path) for path in conflicts)
            )
        )

    for relative in relative_files:
        target = destination / relative
        shutil.copy2(source / relative, target)
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)

    example_target = destination / "profiles" / "beamline.conf.example"
    if not example_target.exists():
        shutil.copy2(source / "profiles" / "beamline.conf.example", example_target)

    print("Installed launcher bundle: {}".format(destination))
    print("Profiles preserved: {}".format(destination / "profiles"))
    print("No ZOOCONFIGPATH or beamline.ini was selected or changed.")


if __name__ == "__main__":
    main()
