# ZooConfig Phase 1 Hardware Verification Checklist

This checklist is for a beamline operator or designated verifier. It is a
runbook, not an authorization to connect to hardware. Do not execute it during
an active measurement unless the beamline operator explicitly approves the
step. The checklist must be completed separately for each beamline.

Phase 1 production code is closed for this verification. Do not edit code,
`beamline.ini`, launchers, or runtime configuration during verification.

## 1. Fixed verification target

Fill these values before starting:

| item | fixed value / entry |
| --- | --- |
| branch | `codex/phase1-zooconfig-loader` |
| verification commit | `ee593fea2ea6f55814c816d0e7eeb32ffa31bdb1` |
| remote ref | `origin/codex/phase1-zooconfig-loader` |
| rollback commit | `<last operator-approved known-good commit>` |
| beamline | `<BL32XU / BL41XU / BL45XU / other>` |
| host | `<host>` |
| verifier | `<name>` |
| scheduled window | `<date/time and timezone>` |

The verification commit must remain unchanged throughout a run. Do not use a
newer local commit or an uncommitted working tree.

## 2. Pre-verification gate

These checks do not contact hardware.

### 2.1 Repository and process safety

Run in an isolated operational clone, never in a clone running the current
production measurement:

```bash
git status --short --branch
git rev-parse HEAD
git rev-parse origin/codex/phase1-zooconfig-loader
git diff --quiet HEAD origin/codex/phase1-zooconfig-loader
git show --no-patch --format='%H%n%s' ee593fea2ea6f55814c816d0e7eeb32ffa31bdb1
```

Expected result: clean status, HEAD equals the fixed verification commit, and
local/remote are equal. **STOP** if there are local changes, a commit mismatch,
an unexpected process using the clone, or an active measurement whose safety
would be affected.

### 2.2 Runtime and configuration identity

Record, without printing secrets or the contents of the live INI:

```bash
command -v yamtbx.python
yamtbx.python -c 'import sys; print(sys.executable); print(sys.version)'
test -n "$ZOOCONFIGPATH"
test -f "$ZOOCONFIGPATH/beamline.ini"
sha256sum "$ZOOCONFIGPATH/beamline.ini"
```

Expected result: the approved `yamtbx.python` runtime is selected, the
environment variable is set, the live file exists, and its hash is recorded.
Confirm the beamline identity through the approved operator procedure; do not
infer it from an unverified path. **STOP** if `ZOOCONFIGPATH` is unset, the
file is missing, the hash/config identity is unexpected, or the runtime is not
the approved one.

### 2.3 Rollback and operational gate

- Confirm the rollback commit is available locally and remotely.
- Record the existing production commit/runtime/config identity.
- Confirm how to stop the verification before any device operation.
- Confirm that no live `beamline.ini` backup or configuration change is needed.
- Obtain operator approval for the boundary between software-only checks and
  hardware checks.

**STOP** if rollback cannot be performed without changing the running
production clone, or if the current hardware/measurement state is unknown.

## 3. Ordered verification steps

Proceed only when the previous step is PASS. The first two steps are software-
only. Step 3 may initialize device-related objects but must not send commands;
steps 4 onward require operator judgment.

### Step 1 — Import/startup smoke check (no hardware command)

Command, from the fixed clone and approved runtime:

```bash
yamtbx.python -c 'from Libs import ZooConfig; print(ZooConfig.get_config_path())'
yamtbx.python -c 'import Libs.BLFactory, Libs.BSSconfig, Libs.Device, Zoo, ZooNavigator, lets_goto_zoo'
```

Expected: imports complete without exception, no process is spawned, and no
socket/device command occurs.

Failure/STOP: any import exception, unexpected subprocess, socket attempt, or
side effect outside the test working directory. Rollback is not needed for a
software-only failure; stop and retain the fixed commit for investigation.

### Step 2 — ZooConfig and beamline.ini read (no hardware command)

Command:

```bash
yamtbx.python -c 'from Libs import ZooConfig; c=ZooConfig.load_config(); print(c.sections())'
```

Do not print secret values. Compare only approved section/key presence and the
beamline identity with the operator's expected live configuration.

Expected: `beamline.ini` is read from the recorded `ZOOCONFIGPATH`; parser
construction and ExtendedInterpolation work; no hardware process or command
occurs.

Failure/STOP: missing/incorrect section, interpolation failure, identity
mismatch, or any hardware access. No live config rollback is required.

### Step 3 — Object initialization only (no intentional hardware command)

Use the beamline's approved initialization command or a documented existing
offline/emulator mode:

```text
<operator-approved object initialization command>
```

Do not invent a new dry-run mode. Monitor socket writes, device commands,
subprocesses, and filesystem writes. Confirm expected object attributes and
initialization order only.

Expected: objects initialize with the expected config identity and no movement,
exposure, or write command.

Failure/STOP: any unexpected connection, command, movement, exposure, or
constructor exception. If hardware state changed, stop and follow the
beamline's operational recovery procedure before any Git rollback.

### Step 4 — Read-only hardware query (hardware access, no write command)

Only after operator approval, use one approved status/position/limit query:

```text
<operator-approved read-only status/position/limit command>
```

Expected: the query returns a plausible status without movement or write.

Failure/STOP: timeout, unexpected state, write/movement command, or inability
to prove the query is read-only. Do not continue to individual operations.

### Step 5 — Individual low-risk device operation (hardware command)

Select exactly one operation approved for the beamline and record before/after
state:

```text
<operator-approved single-device operation>
```

Expected: only the selected device changes as intended and returns to the
operator-approved state.

Failure/STOP: any unplanned device movement, alarm, state change, or inability
to restore the known state. Use the operational recovery procedure; Git
rollback alone cannot undo hardware state.

### Step 6 — ZOO startup to idle (hardware access may occur)

Use the existing beamline launcher, without changing it and without starting a
measurement:

```text
<operator-approved normal ZOO startup command>
```

Expected: ZOO starts, reads the expected configuration, initializes to idle,
and does not mount, expose, move samples, or start processing unexpectedly.

Failure/STOP: startup exception, wrong beamline identity, unexpected command,
or non-idle state. Stop ZOO using the normal operator procedure.

### Step 7 — Existing dry-run/emulator equivalent (if available)

Run only a documented existing mode for the specific beamline:

```text
<documented existing dry-run/emulator command, or N/A>
```

Expected: the mode exercises startup/measurement orchestration without real
exposure or sample movement. Constructor tests must not be reported as a
substitute for this step.

### Step 8 — Measurement gate (operator decision; not part of this checklist)

Before any exposure or sample movement, separately confirm beamline identity,
live-config backup/recovery point, software commit, runtime, device idle state,
operator approval, and the approved measurement protocol. A minimal real
measurement is outside this checklist and requires a new explicit approval.

## 4. Result record

| step | PASS/FAIL/N/A | date/time (TZ) | beamline | commit | runtime | config identity/hash | comment / stop reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 import |  |  |  |  |  |  |  |
| 2 config read |  |  |  |  |  |  |  |
| 3 object init |  |  |  |  |  |  |  |
| 4 read-only query |  |  |  |  |  |  |  |
| 5 individual operation |  |  |  |  |  |  |  |
| 6 ZOO idle startup |  |  |  |  |  |  |  |
| 7 dry-run/emulator |  |  |  |  |  |  |  |
| 8 measurement gate |  |  |  |  |  |  |  |

## 5. Verification boundary

Steps 1–2 are software-only and can normally be performed outside a
measurement window, subject to local clone/runtime policy. Step 3 should be
reviewed by the operator because object initialization can expose hidden
environmental side effects. Steps 4–7 require beamline operator approval.
Step 8 is not authorized by this document.

## 6. Final PR hardware-verification addendum

Append this section to the PR summary only after the checklist is completed:

```text
Hardware verification: PENDING / PASS / FAIL
Beamline(s):
Verification commit:
Runtime:
Config identity/hash:
Steps completed:
Steps skipped:
Operator/verifier:
Date/time:
Result and comments:
Rollback point:
Known limitations:
```
