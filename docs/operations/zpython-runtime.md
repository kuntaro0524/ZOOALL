# zpython runtime deployment and beamline handoff

This document is the restart point for `ZOO-005`. The launcher source is kept
in Git under `runtime/zpython/`; `/staff/Common/kuntaro/zoodev` is a deployed
copy, not the source of truth.

## Safety boundary

- The installer does not copy, select, edit, or replace `beamline.ini`.
- A profile contains host-specific paths and must be created separately on
  each beamline.
- `zpython --config DIR` accepts a directory only when `DIR/beamline.ini`
  exists. This check reads the filesystem but does not initialize hardware.
- Import/config smoke tests are separate from measurement and device tests.

## Install or update the launcher bundle

From a ZOO checkout at the reviewed commit:

```bash
python3 docs/operations/configure-local-runtime.py /path/to/zoo-runtime
```

An existing launcher is not replaced by default. After reviewing the deployed
files, update only the Git-managed launcher files with:

```bash
python3 docs/operations/configure-local-runtime.py \
  --replace-launchers /path/to/zoo-runtime
```

Existing files below `profiles/` are preserved. The command never creates a
`current` symlink or fetches ZOO/kunpy; pinning those checkouts is an explicit
local operation.

## Create the local profile

Copy `profiles/beamline.conf.example` to a name that identifies the host or
beamline, then set all three paths after checking them locally:

```bash
ZOO_BASE_PYTHON=/beamline/path/to/python
KUNPY_ROOT=/beamline/path/to/kunpy
ZOO_ROOT=/beamline/path/to/ZOO
```

Do not copy the kuri04 path values unchanged to a beamline host. Keep
`ZOOCONFIGPATH` out of the profile during initial verification and pass the
test configuration explicitly with `--config`.

## Read-only smoke tests

These commands must be run before any device or measurement test:

```bash
/path/to/zoo-runtime/bin/zpython --profile PROFILE -c \
  'import UserESA; from geometry.detector_specs import get_detector_spec; print(get_detector_spec("EIGER_X_9M"))'

/path/to/zoo-runtime/bin/zpython --profile PROFILE \
  --config /path/to/isolated/config -c \
  'from Libs import ZooConfig; c=ZooConfig.load_config(); print(c.get("beamline", "beamline")); print(c.get("detector", "detector_model"))'
```

Expected for the BL32XU 2026-10-08 snapshot is `BL32XU` and
`EIGER_X_9M`. Do not use a live configuration merely to make this smoke test
pass.

Also confirm the guards:

```bash
/path/to/zoo-runtime/bin/zpython -c 'print("must not run")'
/path/to/zoo-runtime/bin/zpython --profile PROFILE \
  --config /path/that/has/no/beamline.ini -c 'print("must not run")'
```

Both commands must stop with exit status 2 before Python starts.

## Record before beamline verification

Record the following in the `ZOO-005` work item and its branch handoff:

- beamline and host;
- ZOO and kunpy full commit hashes;
- base Python/runtime path and version;
- profile name and local profile path (not its secrets, if any);
- isolated or live config path and a configuration identity such as filename,
  date, and hash;
- exact commands and outputs;
- confirmation that no measurement/device operation was started;
- previous launcher/current symlink and the local rollback operation.

Passing on kuri04 or BL32XU is not acceptance for another beamline.
