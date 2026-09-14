# ZOO Configuration Architecture

## Scope

This document records the current ZOO configuration access pattern and the
limited Phase 1 direction. It describes the repository state; it does not
change the runtime configuration format or deployment method.

## Current structure

Historically, many ZOO modules independently performed the following sequence:

```text
os.environ["ZOOCONFIGPATH"]
    -> ZOOCONFIGPATH/beamline.ini
    -> ConfigParser(interpolation=ExtendedInterpolation())
```

For the Phase 1 production migrations, this mechanical sequence is now
delegated to `Libs/ZooConfig.py`. The migrated modules still retain their own
configuration attribute and initialization behavior; Phase 1 does not make
the parser a shared singleton.

The modules generally retain their own configuration attribute and their own
initialization behavior. This document does not imply that all configuration
objects are currently shared.

## Role of `ZOOCONFIGPATH`

`ZOOCONFIGPATH` remains the entry point to the ZOO runtime configuration. It
is not deprecated in Phase 1.

The responsibilities are distinct:

| Item | Current role |
| --- | --- |
| `yamtbx.python` | Python runtime/dispatcher; may provide the DIALS/cctbx/yamtbx environment for the process that uses it |
| `ZOOCONFIGPATH` | Selects the directory from which ZOO runtime configuration is read |
| `beamline.ini` | Stores beamline-, device-, and measurement-specific settings |

`yamtbx.python` is the current standard runtime/dispatcher for the DIALS,
cctbx, and yamtbx environment. This does not assert that every ZOO code path
has an essential DIALS/yamtbx runtime dependency. `ZOOCONFIGPATH` and
`beamline.ini` remain ZOO configuration concerns.

Historical `zoo.python` launchers were used to start a Python process based on
`yamtbx.python` while adding ZOO and `Libs` paths. They are not removed or
changed by this document. After an alternative ZOO import-path mechanism is
verified, their necessity may be reconsidered.

## Beamline-specific launcher direction

Future beamline-specific launchers such as `zoo-bl32xu`, `zoo-bl41xu`, and
`zoo-bl45xu` are intended to be thin configuration selectors. Their primary
responsibility would be to select `ZOOCONFIGPATH` and invoke `yamtbx.python`;
they are not intended to construct a separate Python runtime. No launcher
implementation or path is defined by this document.

## Live and canonical beamline configuration

The live runtime file at `ZOOCONFIGPATH/beamline.ini` is not changed
automatically by a Git pull or merge. Applying a configuration to a live
environment is an explicit operation.

The future Git-managed canonical configuration is expected to be maintained
per beamline, for example:

- `bl32xu.ini`
- `bl41xu.ini`
- `bl45xu.ini`

The exact repository placement is not decided here. A future explicit apply
operation may compare canonical and live configuration, verify beamline
identity, back up the live file, and then apply the selected configuration.
No such script is introduced in this phase.

## Target direction

Configuration file access is intended to converge on a small independent
loader:

```text
ZOO module
    -> ZooConfig
        -> ZOOCONFIGPATH
            -> beamline.ini
                -> ConfigParser(ExtendedInterpolation)
```

The loader must not import hardware or ZOO runtime classes. The current Phase
1 candidate implementation is `Libs/ZooConfig.py`, which exposes
`get_config_path()` and `load_config()`.

## Phase 1 boundary

Phase 1 standardizes only the mechanical access sequence. It preserves:

- `ZOOCONFIGPATH`
- `beamline.ini`
- existing section and key names
- `ConfigParser` with `ExtendedInterpolation`
- per-class configuration attributes
- constructor behavior and initialization order
- existing exception behavior, including `KeyError` when the environment
  variable is absent

Phase 1 does not introduce:

- a `ConfigParser` singleton or global configuration object
- universal sharing of `BLFactory.config`
- dependency injection
- INI schema changes or value changes
- launcher or `zoo.python` cleanup
- beamline-specific configuration deployment changes
- hardware, device, or measurement logic changes

## Phase 1 implementation status

The following production modules have been migrated to delegate the
`beamline.ini` load to `ZooConfig.load_config()` while preserving their local
configuration attributes and initialization order:

Core and startup path:

- `Libs/BLFactory.py`
- `Libs/BSSconfig.py`
- `Libs/Device.py`
- `Zoo.py`
- `ZooNavigator.py`
- `lets_goto_zoo.py`

Configuration-only modules:

- `KUMA.py`
- `MultiCrystal.py`
- `Libs/CryImageProc.py`
- `Libs/AttFactor.py`
- `Libs/BeamsizeConfig.py`
- `Libs/ESA.py`
- `Libs/RasterSchedule.py`
- `Libs/ScheduleBSS.py`
- `Libs/UserESA.py`
- `Libs/BSSconfig41.py`

Constructor-tested hardware-facing modules whose constructors were verified
offline before migration:

- `Libs/Capture.py`
- `Libs/Gonio44.py`
- `Libs/Count.py`
- `Libs/Zoom.py`
- `Libs/CoaxPint.py`
- `Libs/CCDlen.py`
- `Libs/Mono.py`
- `Libs/PreColli.py`
- `Libs/BaseAxis.py`
- `Libs/Gonio.py`

The focused Phase 1 regression and constructor suite passes offline. The
failure attribution audit compared the Phase 1 base commit
`1996d2c4aca0ac5f2cf4272320d105869c740fa5` with the current branch under the
same runtime and writable working directory. The base had `64 passed, 17
failed`; the current branch had `106 passed, 17 failed` because the current
branch contains additional Phase 1 tests. The same 17 UserESA failures
occurred at the same test/exception locations in both revisions. A separate
run from the read-only repository directory added one logging failure
(`useresa.log`), which is an execution-directory condition rather than a Phase
1 regression. Therefore the current state is **offline verified for the
migrated Phase 1 scope; unrelated UserESA test-infrastructure follow-up
pending; hardware verification pending**.

`Libs/CoaxImage.py` is intentionally not migrated in Phase 1. Its constructor
reuses the `BLFactory` configuration object (`Libs/CoaxImage.py:50-54`), so a
direct replacement with `ZooConfig.load_config()` could change object identity
and hidden coupling. It is an explicit Phase 2 decision, not a missed safe
migration.

Remaining direct reads are limited to standalone hardware utilities and
launcher variants, legacy/dead example blocks, tests/fixtures, and the
CoaxImage Phase 2 case. These paths are not evidence that a safe normal
measurement-core migration was missed.

## Later considerations

Phase 2 or later may evaluate:

- sharing or passing configuration objects
- duplicate `read()` calls such as those in camera/device paths
- explicit configuration errors
- migration of remaining modules
- launcher and configuration selection cleanup
- configuration validation

These are follow-up considerations, not Phase 1 behavior or acceptance
criteria.
