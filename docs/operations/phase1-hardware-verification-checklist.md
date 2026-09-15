# ZooConfig Phase 1 Hardware Verification Checklist

This checklist is for a beamline operator or designated verifier. It is a
runbook, not an authorization to connect to hardware. Do not execute it during
an active measurement unless the beamline operator explicitly approves the
step. The checklist must be completed separately for each beamline.

Phase 1 production code is closed for this verification. Do not edit code,
`beamline.ini`, launchers, or runtime configuration during verification.

## Current Phase 1 status

| item | current status |
| --- | --- |
| implementation | COMPLETE |
| focused offline tests | PASS 42/42 (previously recorded; not rerun in this documentation update) |
| regression comparison | Phase 1による新規regressionなし |
| BL32XU limited live verification | PASS |
| full hardware-dependent verification | DEFERRED |
| CoaxImage | Phase 2 |
| launcher/runtime import-path cleanup | future work |
| main/develop integration | NOT YET DONE |

## 1. Fixed verification target

The completed BL32XU limited run is recorded in section 4. For any future run,
confirm these entries and obtain separate approval before executing the runbook:

| item | fixed value / entry |
| --- | --- |
| branch | `codex/phase1-zooconfig-loader` |
| verification commit | `346d40b8a277f01096572feb12532c965b50aebb` |
| remote ref | `origin/codex/phase1-zooconfig-loader` |
| rollback commit | `<last operator-approved known-good commit>` |
| beamline | `BL32XU` |
| host | `bl32upc4.spring8.or.jp` |
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
git show --no-patch --format='%H%n%s' 346d40b8a277f01096572feb12532c965b50aebb
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

Historical smoke-check command examples, not the exact successful BL32XU
invocation. The standard runtime rebuilds PYTHONPATH; the completed run added
repository root and root/Libs to sys.path after startup (see section 4).
These examples alone do not reproduce that import-path setup:

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

### BL32XU limited live verification record

This record reflects the verifier's supplied results, recorded on 2026-09-15
(Asia/Tokyo). The execution timestamp and verifier name were not supplied.
No tests, imports, hardware communication, or live configuration changes were
performed as part of this documentation update. BL32XU results do not establish
BL41XU or BL45XU verification.

#### Environment

| item | recorded value |
| --- | --- |
| repository | `/staff/bl32xu/Staff/kuntaro/zoo_project/zoo_phase1_verify` |
| branch | `codex/phase1-zooconfig-loader` |
| latest code / restoration commit | `346d40b8a277f01096572feb12532c965b50aebb` |
| host | `bl32upc4.spring8.or.jp` |
| runtime | `/oys/xtal/dials/dials-v3-23-0/build/bin/yamtbx.python` |
| Python | `3.11.11` |
| ZOOCONFIGPATH | `/staff/bl32xu/BLsoft/ZOO32XU` |
| actual configuration file | `/staff/bl32xu/BLsoft/ZOO32XU/beamline.ini` |
| beamline.ini SHA256 | `7c26879a5b0f648809290a420f8ad9adba4470deb1a8fb1174de2dd7b2834b65` |

#### Results

| check | result | boundary |
| --- | --- | --- |
| ZooConfig import | PASS | software import |
| ZooConfig.get_config_path() | PASS | configuration path resolution |
| ZooConfig.load_config() | PASS | configuration load |
| Actual BL32XU beamline.ini read | PASS | recorded live file above |
| Major application imports | PASS | repository root and root/Libs added to sys.path after Python startup; includes ZooNavigator after DiffscanMaster restoration |
| BLFactory constructor | PASS | constructor only; initDevice() not called |
| Zoo constructor | PASS | constructor generation |
| TCP connection to BSS server 192.168.163.2:5555 | PASS | connection only; no BSS command sent |
| Local socket close | PASS | socket closed locally without sending a BSS command |
| Read-only BSS command | DEFERRED | hardware not sufficiently started |
| BLFactory.initDevice() | DEFERRED | hardware not sufficiently started |
| Device.init() | DEFERRED | hardware not sufficiently started |
| Hardware object initialization | DEFERRED | hardware not sufficiently started |
| Hardware position/status query | DEFERRED | hardware not sufficiently started |
| Device movement | DEFERRED | hardware not sufficiently started |
| ZOO startup-to-idle test | DEFERRED | hardware not sufficiently started |
| Measurement test | DEFERRED | hardware not sufficiently started |

DEFERRED means not performed and postponed, not FAIL. The beamline hardware
was not sufficiently started during this verification window. Constructor and
TCP connection PASS do not establish device initialization, BSS command,
startup-to-idle, or measurement success. No dry-run/emulator result was supplied.

#### DiffscanMaster.py repository consistency issue

During live verification, importing ZooNavigator initially failed because
`DiffscanMaster.py` was absent from the Phase 1 branch. `ZooNavigator.py` uses
both `import DiffscanMaster` and `DiffscanMaster.HITO(...)`.

The verifier inspected the working BL32XU repository `/user/target/JunkZoo`:
branch `develop`, commit `4fbaf9be974ca728d23c3281b76b881c6f5509d8`.
It contains `DiffscanMaster.py` with `class HITO():`; `origin/develop` also
contains the same file. History showed its deletion in commit `c500557`,
`DiffscanMaster.py was renamed to HITO.py`.

The file was restored from `origin/develop:DiffscanMaster.py` in commit
`346d40b Restore DiffscanMaster.py lost during branch merge`. The verifier ran
`cmp DiffscanMaster.py <(git show origin/develop:DiffscanMaster.py)` and
confirmed `IDENTICAL TO origin/develop`.

This is a pre-existing repository consistency issue originating in past branch
merge / rename history, not a regression introduced by ZooConfig Phase 1.
The restoration was already committed before this documentation-only update.

#### Launcher/runtime import-path finding

The standard `/oys/xtal/dials/dials-v3-23-0/build/bin/yamtbx.python` rebuilds
PYTHONPATH at startup, so simply setting ZOO repository root / Libs in the
shell PYTHONPATH did not preserve those import paths. For the successful
application import check, repository root and repository root/Libs were added
to `sys.path` after Python startup. Historical `zoo.python` launchers were
also confirmed to add ZOO root / Libs themselves.

This is a separate launcher/runtime/import-path architecture issue, not a
ZooConfig Phase 1 defect. Cleanup is future work; no launcher or runtime fix
is included here.

## 5. Verification boundary

Steps 1–2 are software-only and can normally be performed outside a
measurement window, subject to local clone/runtime policy. Step 3 should be
reviewed by the operator because object initialization can expose hidden
environmental side effects. Steps 4–7 require beamline operator approval.
Step 8 is not authorized by this document.

## 6. Final PR hardware-verification addendum

When preparing a later PR, report the limited PASS and full hardware DEFERRED
separately; do not describe this checklist as fully passed:

```text
BL32XU limited live verification: PASS
Full hardware-dependent verification: DEFERRED
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
