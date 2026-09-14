# Handoff: Phase 1 ZooConfig loader

- Issue: 未設定
- Branch: `codex/phase1-zooconfig-loader`
- コードcommit: `b29bb94`（Commit 1: Add shared ZooConfig loader）
- 記録者: Codex
- Host: `robo04`
- 環境: ZOO開発clone（実機操作なし）
- 記録日時: 2026-09-14（Asia/Tokyo）

## Goal

Commit 1として、`ZOOCONFIGPATH/beamline.ini`の機械的な読込だけを
`Libs/ZooConfig.py`へ切り出し、単体テストを追加する。

## Current state

- `Libs/ZooConfig.py`を新設済み。
- `Libs/tests/test_zoo_config.py`を新設済み。
- Phase 1のproduction migrationを開始済み。
- Commit 1を`b29bb94`として作成済み。
- 開発文書整合化を`6a59bdd`として作成済み。
- `Libs/BLFactory.py`のloader委譲とoffline testを`06b8c5d`として作成済み。
- `Libs/BSSconfig.py`のloader委譲とoffline testを`9faaf57`として作成済み。
- `Libs/Device.py`のloader委譲とoffline testを`041f6b2`として作成済み。
- `Zoo.py`のloader委譲とoffline testを`4b5b068`として作成済み。
- `ZooNavigator.py`のloader委譲とoffline testを`91ccdd1`として作成済み。
- `lets_goto_zoo.py`のloader委譲とoffline testを`53c3dd3`として作成済み。
- 初期migration候補6ファイルのloader委譲を完了した。
- A分類（設定読み込みのみ）の10 moduleを`88d7372`としてloaderへ移行した。
- A分類の対象は`KUMA.py`、`MultiCrystal.py`、`Libs/CryImageProc.py`、
  `Libs/AttFactor.py`、`Libs/BeamsizeConfig.py`、`Libs/ESA.py`、
  `Libs/RasterSchedule.py`、`Libs/ScheduleBSS.py`、`Libs/UserESA.py`、
  `Libs/BSSconfig41.py`である。
- A分類のloader委譲を確認するoffline testを
  `Libs/tests/test_a_config_modules_zooconfig.py`として追加した。
- `22f812a`までのPhase 1 commitとhandoverを、作業branch
  `codex/phase1-zooconfig-loader`としてoriginへpushした。
- push後にlocal `HEAD`と`origin/codex/phase1-zooconfig-loader`が一致することを確認した。
- Capture/Gonio44のbaseline constructor offline testを`844ae31`として追加した。
- baseline testではtemporary `beamline.ini`、fake server、socket fail-fast、
  process fail-fastを使用し、constructor中の通信・hardware access・外部process起動が
  ないことを確認した。
- `Libs/Capture.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  constructor testとloader委譲確認を`484bc79`としてcommit・pushした。
- `Libs/Gonio44.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  constructor testとloader委譲確認を`4dfec53`としてcommit・pushした。
- `Libs/Count.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  fake BSSconfig/serverとfail-fast socket/processを使うconstructor testを
  `c4f6c67`としてcommit・pushした。
- `Libs/Zoom.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  fake BSSconfig/Motor/serverとfail-fast socket/processを使うconstructor testを
  `3862abe`としてcommit・pushした。
- `Libs/CoaxPint.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  fake BSSconfig/Motor/serverとfail-fast socket/processを使うconstructor testを
  `57f1355`としてcommit・pushした。
- `Libs/CCDlen.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  fake BSSconfig/Motor/serverとfail-fast socket/processを使うconstructor testを
  `747afe0`としてcommit・pushした。
- `Libs/Mono.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  fake BSSconfig/Motor/serverとfail-fast socket/processを使うconstructor testを
  `7291d20`としてcommit・pushした。
- `Libs/PreColli.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  条件付きY/Z Motorとfail-fast socket/processを使うconstructor testを
  `6f45a12`としてcommit・pushした。
- `Libs/BaseAxis.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  pulse/plc分岐とfail-fast socket/processを使うconstructor testを
  `1a99ab3`としてcommit・pushした。
- `Libs/Gonio.py`のconfig読込を`ZooConfig.load_config()`へ委譲し、
  5軸Motorとfail-fast socket/processを使うconstructor testを
  `9c00171`としてcommit・pushした。
- `CoaxImage.py`のconstructor baseline testを`d68ba9f`として追加・pushした。
- B分類候補のconstructor/import経路を静的に確認した。対象constructor内に
  `socket.connect`、`sendall`、`recv`の直接呼出しは見つからなかった。
- `Libs/Motor.py:14-25`のconstructorはserver参照・軸名・unitの保持だけで、通信は
  `communicate()`以降のmethod（`Libs/Motor.py:27-30`）で行われる。
- 正式runtimeで新規unit test 5件が成功した。
- BLFactory移行を含む対象test 6件が正式runtimeで成功した。
- BSSconfig移行を含む対象test 7件が正式runtimeで成功した。
- Zoo移行を含む対象test 9件が正式runtimeで成功した。
- ZooNavigator移行を含む対象test 10件が正式runtimeで成功した。
- lets_goto_zoo移行を含む対象test 11件が正式runtimeで成功した。

## Decisions made during this work

- `ZOOCONFIGPATH`未設定時は`os.environ[...]`による従来の`KeyError`を維持する。
- `ConfigParser(interpolation=ExtendedInterpolation())`を維持する。
- `ConfigParser.read()`の不存在時挙動を維持する。
- singleton/cache/fallback/path存在チェック/hardware importは追加しない。
- Phase 1のproduction migrationはmodule単位の小さなcheckpointに分割する。
- BLFactoryではconfig属性、path表示、key取得、BSSconfig生成、初期化順序を維持した。
- BSSconfigでは`inifile_path`、`blini`、`confile`、`camerainf_path`、constructor順序を維持した。
- Deviceでは`config`属性、既存key取得、constructor順序、hardware初期化前の状態を維持した。
- ZooではBSS設定値、接続初期値、emulator初期値、constructor順序を維持した。
- ZooNavigatorでは既存config属性、key取得、constructor順序、設定初期値を維持した。
- lets_goto_zooではimport-time読込、path表示、global設定値を維持した。

## Files changed

Commit 1のコード差分:

- `Libs/ZooConfig.py`
- `Libs/tests/test_zoo_config.py`
- `Libs/BLFactory.py`
- `Libs/tests/test_blfactory_zooconfig.py`
- `Libs/BSSconfig.py`
- `Libs/tests/test_bssconfig_zooconfig.py`
- `Libs/Device.py`
- `Libs/tests/test_device_zooconfig.py`
- `Zoo.py`
- `Libs/tests/test_zoo_zooconfig.py`
- `ZooNavigator.py`
- `Libs/tests/test_zoonavigator_zooconfig.py`
- `lets_goto_zoo.py`
- `Libs/tests/test_lets_goto_zoo_zooconfig.py`

今回追加・更新した開発文書:

- `docs/architecture/configuration.md`
- `docs/development/decision_log.md`
- `handoffs/phase1-zooconfig-loader.md`
- `AGENTS.md`

## Verified

- 標準ライブラリによる手動互換性チェック成功。
- 正常読込、代表値、`${section:key}`のExtendedInterpolation、旧方式との値一致を確認。
- `ZOOCONFIGPATH`未設定時の`KeyError`を確認。
- `beamline.ini`不存在時の空読込を確認。
- AST syntax check成功。
- `/oys/xtal/dials/dials-v3-23-0/build/bin/yamtbx.python`を正式test runtimeとして確認。
- 同runtimeで`Libs/tests/test_zoo_config.py`を実行し、`5 passed in 0.06s`。
- 同runtimeで`Libs/tests/test_zoo_config.py Libs/tests/test_blfactory_zooconfig.py`を実行し、`6 passed in 0.05s`。
- 同runtimeでZooConfig、BLFactory、BSSconfigの対象testを実行し、`7 passed in 0.09s`。
- 同runtimeでZooConfig、BLFactory、BSSconfig、Deviceの対象testを実行し、`8 passed in 0.20s`。
- 同runtimeでZooConfig、BLFactory、BSSconfig、Device、Zooの対象testを実行し、`9 passed in 0.20s`。
- 同runtimeでZooConfig、BLFactory、BSSconfig、Device、Zoo、ZooNavigatorの対象testを実行し、`10 passed in 0.17s`。
- 同runtimeでZooConfig、BLFactory、BSSconfig、Device、Zoo、ZooNavigator、lets_goto_zooの対象testを実行し、`11 passed in 0.22s`。
- 初期migration完了後の同対象testを再実行し、`11 passed in 0.20s`。
- A分類移行後に対象testを再実行し、`21 passed in 0.27s`。
- 正式runtimeでCapture/Gonio44 baselineとZooConfig/A分類testを実行し、`17 passed in 0.22s`。
- Capture移行後、同runtimeでCapture/Gonio44、ZooConfig、A分類testを実行し、
  `18 passed in 0.21s`。
- Gonio44移行後、同runtimeでCapture/Gonio44、ZooConfig、A分類、初期6候補のtestを
  実行し、`25 passed in 0.30s`。
- Count移行後、同runtimeでCount、Capture/Gonio44、ZooConfig、A分類、初期6候補のtestを
  実行し、`27 passed in 0.29s`。
- Zoom移行後、同runtimeでZoom、Count、Capture/Gonio44、ZooConfig、A分類、初期6候補の
  testを実行し、`29 passed in 0.33s`。
- CoaxPint移行後、同runtimeでCoaxPint、Zoom、Count、Capture/Gonio44、ZooConfig、
  A分類、初期6候補のtestを実行し、`31 passed in 0.34s`。
- CCDlen移行後、同runtimeでCCDlen、CoaxPint、Zoom、Count、Capture/Gonio44、ZooConfig、
  A分類、初期6候補のtestを実行し、`33 passed in 0.33s`。
- Mono移行後、同runtimeでMono、CCDlen、CoaxPint、Zoom、Count、Capture/Gonio44、
  ZooConfig、A分類、初期6候補のtestを実行し、`35 passed in 0.37s`。
- PreColli移行後、同runtimeでPreColli、Mono、CCDlen、CoaxPint、Zoom、Count、
  Capture/Gonio44、ZooConfig、A分類、初期6候補のtestを実行し、`37 passed in 0.36s`。
- BaseAxis移行後、同runtimeでBaseAxis、PreColli、Mono、CCDlen、CoaxPint、Zoom、
  Count、Capture/Gonio44、ZooConfig、A分類、初期6候補のtestを実行し、`39 passed in 0.38s`。
- Gonio移行後、同runtimeでGonio、BaseAxis、PreColli、Mono、CCDlen、CoaxPint、
  Zoom、Count、Capture/Gonio44、ZooConfig、A分類、初期6候補のtestを実行し、
  `41 passed in 1.28s`。
- CoaxImage baselineを含む同runtimeの対象testを実行し、`42 passed in 1.33s`。
- `/usr/bin/python3`にはpytestがないが、正式runtimeの実行結果には影響しない。
- hardware接続、測定、外部process起動は行っていない。

## Next action

### Phase 1 completion audit status (2026-09-14)

The direct-read audit found no missed safe normal-measurement Phase 1 target.
Residual direct reads are classified as follows:

- Intentional Phase 1 exclusion / launcher or hardware path: `lets_goto_zoo_PE3.py:17-19`,
  `lets_goto_zoo_echa.py:4-8`, and the standalone `__main__` paths in
  `get_e.py:14-17`, `move_to_cmount.py:14-17`, `get_gonio.py:14-17`,
  `INOCC.py:704-707`, `Libs/PreColli.py:155-159`, `Libs/Colli.py:501-506`,
  `Libs/CCDlen.py:74-78`, and the hardware-oriented `TestScripts/`/utility scripts.
- Explicit Phase 2: `Libs/CoaxImage.py:50-54`, because `self.blf.config` is reused and
  parser identity/hidden coupling must not be changed in Phase 1.
- Test/fixture: `Libs/tests/*` and `tests/test_useresa_real_kuma.py:44`.
- Legacy/dead: triple-quoted example blocks at `Libs/Device.py:335-339` and
  `Libs/BSSconfig.py:506-509`.
- Standalone utility: `Libs/Capture.py:243` and similar `__main__` configuration setup.

No remaining active direct read was identified as a safe normal-measurement Phase 1
miss. The migrated production modules are the six core/startup modules, ten A-class
configuration-only modules, and ten B-class constructor-tested modules recorded in
`docs/architecture/configuration.md`. CoaxImage is unchanged.

Focused offline regression and constructor coverage for the migrated scope, including
the CoaxImage baseline, passes: `42 passed in 1.21s` under
`/oys/xtal/dials/dials-v3-23-0/build/bin/yamtbx.python` with repository import paths.
The broader `Libs/tests` offline run is not clean: `105 passed, 18 failed`. The failures
are concentrated in existing UserESA tests (missing manually-created config attributes,
fixture/validation mismatches, repo-root log-file creation on the read-only checkout,
and incomplete fixture keys). Because the complete-suite failure cause is not part of
this migration and the WORKFLOW STOP condition applies, Phase 1 is not marked full-suite
complete.

Current status: **Phase 1 implementation complete for the migrated scope; focused
offline verified; full-suite follow-up pending; hardware verification pending**.

### Failure attribution audit (2026-09-14)

Comparison base: `1996d2c4aca0ac5f2cf4272320d105869c740fa5` (the parent of
Commit 1, Phase 1 start). The base was run in detached worktree
`/tmp/zooall-phase1-base`; current was run from the working repository. Both
used `/oys/xtal/dials/dials-v3-23-0/build/bin/yamtbx.python`, Python 3.11.11,
pytest with `-p no:cacheprovider`, the same repository import paths, and the
same test selection. For the controlled comparison both used the same writable
cwd `/tmp/zoo-phase1-test-cwd` and excluded only
`Libs/tests/test_inventory_webdb_smoke.py`.

Controlled full-suite result:

- base: `64 passed, 17 failed`
- current: `106 passed, 17 failed`
- The pass-count difference is due to Phase 1 tests added on the current
  branch. The 17 failures below occurred in both revisions at the same
  logical test/exception locations.

| test | failure evidence | classification |
| --- | --- | --- |
| `test_useresa_define_scan_condition_dose_ratio.py::test_high_and_ultra_follow_normal_dose_ratio` | `UserESA.__new__` object has no `config` at `UserESA.py:637/639` | B: pre-existing test setup |
| `test_useresa_define_scan_condition_updates_dose_ds.py::test_define_scan_condition_updates_dose_ds_from_dose_per_frame` | same missing `config` at `defineScanCondition` | B: pre-existing test setup |
| `test_useresa_dose_distance_handler.py::test_check_dose_list_normalizes_and_pads` | length mismatch ValueError at `DoseDistanceHandler.validate_dose_dist` | B: pre-existing fixture/expectation mismatch |
| `test_useresa_dose_distance_handler.py::test_check_dose_list_requires_both_columns` | expected ValueError not raised | B: pre-existing fixture/expectation mismatch |
| `test_useresa_dose_error_flag.py::test_dose_error_flag_is_set_when_negative` | same missing `config` at `defineScanCondition` | B: pre-existing test setup |
| `test_useresa_logger_handler_duplication.py::test_useresa_does_not_duplicate_logger_handlers` | only repo-readonly run: `FileHandler('useresa.log')` raises `OSError: [Errno 30]` | C: cwd/filesystem condition; passes in controlled writable cwd |
| `test_useresa_reject_ssrox.py::test_ssrox_is_rejected` | `KeyError: 'ssrox'` from `getParams` | B: pre-existing behavior/test mismatch |
| `test_useresa_spec.py::test_check_dose_list_normalization[5,10...]` | length mismatch ValueError | B: pre-existing fixture/expectation mismatch |
| `test_useresa_spec.py::test_check_dose_list_normalization[[5, 10]...]` | length mismatch ValueError | B: pre-existing fixture/expectation mismatch |
| `test_useresa_spec.py::test_check_dose_list_rejects_multi_values_for_multi_and_mixed[multi]` | message mismatch: `does not allow` vs expected `prohibits` | B: pre-existing assertion mismatch |
| `test_useresa_spec.py::test_check_dose_list_rejects_multi_values_for_multi_and_mixed[mixed]` | same message mismatch | B: pre-existing assertion mismatch |
| `test_useresa_spec.py::test_validate_dose_dist_rejects_multiple_values_in_multi_and_mixed[multi]` | length validation occurs before expected mode message | B: pre-existing assertion/order mismatch |
| `test_useresa_spec.py::test_validate_dose_dist_rejects_multiple_values_in_multi_and_mixed[mixed]` | same validation-order mismatch | B: pre-existing assertion/order mismatch |
| `test_useresa_spec.py::test_define_scan_condition_expected_dose_math` | fixture lacks `experiment.thinnest_att_thick` | B: pre-existing fixture/config mismatch |
| `test_useresa_spec.py::test_mode_does_not_change_define_scan_condition_numeric_result_without_lists[single]` | fixture lacks `experiment.thinnest_att_thick` | B: pre-existing fixture/config mismatch |
| `test_useresa_spec.py::test_mode_does_not_change_define_scan_condition_numeric_result_without_lists[helical]` | same missing config key | B: pre-existing fixture/config mismatch |
| `test_useresa_spec.py::test_mode_does_not_change_define_scan_condition_numeric_result_without_lists[multi]` | same missing config key | B: pre-existing fixture/config mismatch |
| `test_useresa_spec.py::test_mode_does_not_change_define_scan_condition_numeric_result_without_lists[mixed]` | same missing config key | B: pre-existing fixture/config mismatch |

The current/base diff for `Libs/UserESA.py` is limited to replacing the local
parser construction/read with `ZooConfig.load_config()` plus the import; no
UserESA algorithm or assertion behavior was changed by Phase 1. The focused
Phase 1 suite remains `42 passed`. No Phase 1 regression was observed, so
offline verification is valid for the migrated scope, not for claiming the
entire pre-existing UserESA suite is green.

Separate follow-up issues, not to be repaired in this audit:

- tests using `UserESA.__new__` need an explicit config fixture before calling
  methods that read `self.config`;
- dose/distance fixtures and expected validation messages/order are inconsistent;
- UserESA fixtures need the `experiment.thinnest_att_thick` key;
- logger tests should use a writable temporary directory rather than the repo
  root.

No UserESA test, fixture, or production code was changed. The phase remains
**offline verified for the migrated scope; hardware verification pending**.

Changed production modules:

- Core/startup: `Libs/BLFactory.py`, `Libs/BSSconfig.py`, `Libs/Device.py`, `Zoo.py`,
  `ZooNavigator.py`, `lets_goto_zoo.py`.
- A: `KUMA.py`, `MultiCrystal.py`, `Libs/CryImageProc.py`, `Libs/AttFactor.py`,
  `Libs/BeamsizeConfig.py`, `Libs/ESA.py`, `Libs/RasterSchedule.py`,
  `Libs/ScheduleBSS.py`, `Libs/UserESA.py`, `Libs/BSSconfig41.py`.
- B: `Libs/Capture.py`, `Libs/Gonio44.py`, `Libs/Count.py`, `Libs/Zoom.py`,
  `Libs/CoaxPint.py`, `Libs/CCDlen.py`, `Libs/Mono.py`, `Libs/PreColli.py`,
  `Libs/BaseAxis.py`, `Libs/Gonio.py`.

Unchanged and residual-risk modules include `Libs/CoaxImage.py` (Phase 2 identity
decision), standalone hardware utilities and launcher variants, legacy/dead example
blocks, and tests/fixtures. Hardware verification of all migrated constructors and
the normal measurement path remains pending. Do not merge to `main`/`develop`.

A分類のloader委譲が完了した。残存する直接読込には、hardware/device初期化経路の
`Libs/Mono.py`、`Libs/Capture.py`、`Libs/Zoom.py`、`Libs/Count.py`、
`Libs/Gonio.py`、`Libs/Gonio44.py`、`Libs/CCDlen.py`、`Libs/PreColli.py`、
`Libs/BaseAxis.py`、`Libs/CoaxPint.py`、`Libs/CoaxImage.py`等のB分類候補と、
実行時にsocket/device操作へ進むD分類候補がある。次のactionは、B分類候補ごとに
fake server・socket fail-fast stubを使ったconstructor offline testを設計・実行すること。
constructor/import自体の外部接続が確認されたmoduleはC/Dとして移行しない。B分類の
test結果と影響範囲が明確になるまで、追加のproduction migrationを停止する。

### B分類constructor候補

以下はfake server、fake `Motor`、fakeまたはfixture化した`BSSconfig`を使えば、
constructorのloader委譲と「通信を発生させない」ことをofflineで確認できる候補である。

| module | constructor evidence | offline test scope | status |
| --- | --- | --- | --- |
| `Libs/Capture.py:14-41` | config読込とdefault値設定。接続は`connect()`の`112-117`以降 | config fixture、socket fail-fast、constructor属性 | B候補 |
| `Libs/Gonio44.py:19-28` | config読込のみ。通信は`communicate()`の`30-34`以降 | fake server、constructor属性、send/recv未呼出し | B候補 |
| `Libs/Mono.py:19-41` | `BSSconfig`、3個の`Motor`生成。通信はMotor method以降 | fake server/BSSconfig/Motor、axis値確認 | B候補 |
| `Libs/Zoom.py:11-29` | `BSSconfig`、Motor生成、pulse情報取得 | fake server/BSSconfig/Motor、axis値確認 | B候補 |
| `Libs/Count.py:16-28` | configと`BSSconfig`のみ。通信は`communicate()`の`31-37`以降 | fake server/BSSconfig、axis値確認 | B候補 |
| `Libs/Gonio.py:14-65` | 5個の`Motor`生成とBSS設定解析 | fake server/BSSconfig/Motor、全axis確認 | B候補 |
| `Libs/CCDlen.py:15-33` | Motor生成とBSS設定解析 | fake server/BSSconfig/Motor、limit値確認 | B候補 |
| `Libs/PreColli.py:18-56` | 条件付きMotor生成とBSS設定解析 | 軸なし/片軸/両軸fixtureを分けて確認 | B候補 |
| `Libs/BaseAxis.py:10-53` | 分岐ごとにMotor生成、BSSの退避情報を取得 | `pulse`/`plc`/BS/col分岐をfake化 | B候補 |
| `Libs/CoaxPint.py:13-29` | Motor生成とBSS設定解析 | fake server/BSSconfig/Motor、axis値確認 | B候補 |
| `Libs/CoaxImage.py:37-99` | 既存BLFactoryを前提に設定・camera.inf・bss.configを読込、Capture生成 | fake BLFactory、temporary auxiliary files、fake Capture | B候補（複雑） |

### C/D境界

constructor/importそのものがsocket接続するC候補は、今回の静的調査では確認できなかった。
一方、以下は同じmodule内のstandalone実行部で接続するため、その実行部はDとして扱う。

- `Libs/Mono.py:342-343`
- `Libs/Zoom.py:67-68`
- `Libs/Count.py:242-243`
- `Libs/Gonio.py:904-905`
- `Libs/PreColli.py:158-166`
- `Libs/CCDlen.py:74-79`（BLFactory初期化を含む）

これらのstandalone実行部はoffline移行対象に含めない。constructor移行を検討する場合も、
`__main__`の実機動作確認を代替したとは扱わない。

### B分類offline test設計

1. temporary `beamline.ini`と必要なauxiliary configを作成する。
2. `ZOOCONFIGPATH`をfixture directoryへ設定する。
3. `ZooConfig.load_config()`をfakeまたは実loaderで注入し、代表的section/keyを確認する。
4. `BSSconfig`、`Motor`、`Capture`、socket相当をfake化し、constructor中の通信呼出しを
   fail-fastで検出する。
5. server objectの`sendall`/`recv`がconstructor中に呼ばれないことをassertする。
6. 既存constructorの属性、axis名、beamline、limit値を旧実装相当のfixtureで比較する。
7. `__main__`ブロックは実行しない。

優先順は、まず`Capture`と`Gonio44`、次にMotor/BSSconfig依存の単純な
`Count`・`Zoom`・`CoaxPint`、その後に分岐の多い`Gonio`・`PreColli`・`BaseAxis`、
最後に`CoaxImage`とする。これらのtestが成功するまでproduction migrationは行わない。

Capture/Gonio44のbaselineは成功し、`Libs/Capture.py`は`484bc79`、
`Libs/Gonio44.py`は`4dfec53`で移行済み。次は中リスクB分類のうち、constructorが
単純な`Libs/Zoom.py`、`Libs/CoaxPint.py`を候補とする。`Libs/Count.py`は
`c4f6c67`で、`Libs/Zoom.py`は`3862abe`で、`Libs/CoaxPint.py`は`57f1355`で
移行済み。残るB分類は最後に依存の多い`CoaxImage`である。PreColli、BaseAxis、
Gonioは移行済み。CoaxImageのbaselineは成功したが、production migrationはSTOPする。
`CoaxImage.__init__`は`self.blf.config`を`self.config`へ代入して再利用し
（`Libs/CoaxImage.py:50-54`）、その後同じparserへ`beamline.ini`をreadしている。
`ZooConfig.load_config()`へ単純置換するとconfig object identityとBLFactoryとの
hidden couplingが変わるため、Phase 1のconfig object共有/constructor挙動維持の境界を
越える可能性がある。path取得だけを`ZooConfig.get_config_path()`へ委譲する案も、
loader集約の意図と既存object再利用の両立を明示的に判断するまで実装しない。
この判断が未確定のため、現時点でPhase 1 production migrationを停止する。
完了済みmoduleではfake `BSSconfig`/`Motor`とsocket fail-fastを使うconstructor testを
先行し、test成功後にのみproduction migrationを行った。CoaxImageはobject identityの
判断が未解決のため、そのmigrationを行わない。

### B分類constructor詳細監査

| module | constructorで起こること | socket/hardware command | filesystem/process | mock/offline評価 | 移行リスク |
| --- | --- | --- | --- | --- | --- |
| `Capture.py:14-41` | 環境変数、INI読込、capture default設定 | constructor接続・commandなし | constructorはINI読込のみ。接続・`os.system`は`connect`/restart後 | socket fail-fastで容易 | 低〜中 |
| `Gonio44.py:19-28` | server保持、INIからbeamline読込 | constructor commandなし。通信はmethod後 | INI読込のみ | fake serverで容易 | 低 |
| `Mono.py:19-41` | BSSconfig、INI、3 Motor生成 | Motor生成時commandなし。移動は後続method | BSS config読込 | fake BSSconfig/Motorで可能 | 中 |
| `Zoom.py:11-29` | BSSconfig、INI、Motor生成、pulse情報 | constructor commandなし。通信は`stop`等の後続method | BSS config読込 | fake server/BSSconfig/Motorで可能 | 中 |
| `Count.py:16-28` | INI、BSSconfig、counter axis名生成 | constructor commandなし。通信は`communicate`後 | BSS config読込 | fake server/BSSconfigで可能 | 中 |
| `Gonio.py:14-65` | BSSconfig、5 Motor生成、pulse情報 | constructor commandなし。移動は後続method | BSS config読込とprint | fake BSSconfig/Motorで可能 | 中〜高 |
| `CCDlen.py:15-33` | INI、BSSconfig、Motor、limit値 | constructor commandなし | BSS config読込 | fake server/BSSconfig/Motorで可能 | 中 |
| `PreColli.py:18-56` | BSSconfig、条件付きMotor、pulse情報 | constructor commandなし | BSS config読込とprint | 軸なし/片軸/両軸fixtureが必要 | 中〜高 |
| `BaseAxis.py:10-53` | axis種別ごとにBSS設定・Motor生成 | constructor commandなし | BSS config読込とprint | `pulse`/`plc`/BS/col分岐をmock可能 | 中〜高 |
| `CoaxPint.py:13-29` | BSSconfig、INI、Motor、pulse情報 | constructor commandなし | BSS config読込 | fake server/BSSconfig/Motorで可能 | 中 |
| `CoaxImage.py:37-99` | BLFactory既存config/deviceを前提、補助ファイル読込、Capture生成 | constructor自身のsocket commandなし。既存`ms`は保持 | `camera.inf`/`bss.config`読込。process起動なし | fake BLFactory、補助fixture、fake Captureが必要 | 高（依存多） |

今回の判定はconstructorの静的追跡と呼出し先確認に基づく。実際のconstructor
offline testはまだ追加・実行していない。`__main__`内のsocket接続はD扱いとして
constructor移行の安全性とは分離する。

## Do not do

- 既存checkpointへ追加commitを作成しない。launcherのruntime構築変更、
  config object共有へ進まない。
- 残存hardware/device module、測定module、launcher runtime構築を変更しない。
- B分類候補をconstructor offline testなしに移行しない。C/D分類候補は実機確認なしに触らない。
- package install/updateを行わない。
- hardware、BSS、外部API、測定processへ接続しない。
- `beamline.ini`やruntime設定を変更しない。
- 残存hardware/device moduleを追加移行しない。個別の影響評価なしにPhase 1を拡張しない。

## Known issues

- `/usr/bin/python3`にはpytestがない。正式runtimeでは対象test実行済み。
- GitHub Issueとの対応付けは未設定。Issueなしでもbranchとhandoverで再開可能。
- 初期migration後の残存moduleについては、hardware/measurement影響を伴うため未移行。
- B分類のうちCapture、Gonio44、Count、Zoom、CoaxPint、CCDlen、Mono、PreColli、
  BaseAxis、Gonioはconstructor offline testを追加・実行済み。
- Capture/Gonio44についてはbaseline constructor testを追加・実行済み。
- Captureについてはloader移行後のconstructor testも成功済み。
- Gonio44についてはloader移行後のconstructor testも成功済み。
- PreColli、BaseAxis、Gonioについてはloader移行後のconstructor testも成功済み。
- Countについてはloader移行後のconstructor testも成功済み。
- Zoomについてはloader移行後のconstructor testも成功済み。
- CoaxPintについてはloader移行後のconstructor testも成功済み。
- CCDlen、Monoについてはloader移行後のconstructor testも成功済み。
- CoaxImageについてはbaseline constructor testのみ成功。production migrationは未実施。
- CCDlenについてはloader移行後のconstructor testも成功済み。
- Monoについてはloader移行後のconstructor testも成功済み。
- C候補がないことは静的調査の範囲の結論であり、import実行時副作用を全面保証するものではない。
- CoaxImageの`self.blf.config`再利用を維持したままloader集約する方式は未決定。
- CoaxImageのconfig object identityを変更するmigrationはPhase 1 STOP条件に抵触する可能性がある。

## Phase 1 closure preparation

### Final production module list and offline evidence

The following production modules were changed by Phase 1. `ZooConfig.py` is
the new loader; all other entries delegate only the mechanical config read and
retain their local config attributes and initialization order.

| group | production module(s) | offline test | guarantee |
| --- | --- | --- | --- |
| loader | `Libs/ZooConfig.py` | `Libs/tests/test_zoo_config.py` | path construction, parser read, ExtendedInterpolation, legacy KeyError/missing-file behavior, old/new value equivalence |
| core/startup | `Libs/BLFactory.py`, `Libs/BSSconfig.py`, `Libs/Device.py`, `Zoo.py`, `ZooNavigator.py`, `lets_goto_zoo.py` | `test_blfactory_zooconfig.py`, `test_bssconfig_zooconfig.py`, `test_device_zooconfig.py`, `test_zoo_zooconfig.py`, `test_zoonavigator_zooconfig.py`, `test_lets_goto_zoo_zooconfig.py` | loader delegation plus representative config values and preserved initialization/observable state; no hardware connection in the tested path |
| config-only A | `KUMA.py`, `MultiCrystal.py`, `Libs/AttFactor.py`, `Libs/BeamsizeConfig.py`, `Libs/CryImageProc.py`, `Libs/ESA.py`, `Libs/RasterSchedule.py`, `Libs/ScheduleBSS.py`, `Libs/UserESA.py`, `Libs/BSSconfig41.py` | `Libs/tests/test_a_config_modules_zooconfig.py` | each module delegates config loading to ZooConfig without changing its local config access contract |
| constructor-tested B | `Libs/Capture.py`, `Libs/Gonio44.py`, `Libs/Count.py`, `Libs/Zoom.py`, `Libs/CoaxPint.py`, `Libs/CCDlen.py`, `Libs/Mono.py`, `Libs/PreColli.py`, `Libs/BaseAxis.py`, `Libs/Gonio.py` | `test_capture_gonio44_constructor_baseline.py`, `test_count_constructor_baseline.py`, `test_zoom_constructor_baseline.py`, `test_coaxpint_constructor_baseline.py`, `test_ccdlen_constructor_baseline.py`, `test_mono_constructor_baseline.py`, `test_precolli_constructor_baseline.py`, `test_baseaxis_constructor_baseline.py`, `test_gonio_constructor_baseline.py` | fixture-based constructor completion, no socket communication, no hardware command, no external process, and preserved observable constructor state before/after loader migration |

`Libs/CoaxImage.py` is not in the changed production list. Its baseline is
covered by `Libs/tests/test_coaximage_constructor_baseline.py`; that test
documents the offline constructor boundary only. It does not authorize a
Phase 1 migration.

### Closure evidence

- Phase 1 focused suite: `42 passed in 1.21s` under
  `/oys/xtal/dials/dials-v3-23-0/build/bin/yamtbx.python`.
- Base: `1996d2c4aca0ac5f2cf4272320d105869c740fa5`; controlled full
  `Libs/tests` run: `64 passed, 17 failed`.
- Current: `9087236`; same controlled run: `106 passed, 17 failed`.
- The 17 failing UserESA tests occurred at the same logical locations in base
  and current. The repo-readonly run's additional `useresa.log` failure is a
  writable-cwd issue and passes from `/tmp/zoo-phase1-test-cwd`.
- Therefore Phase 1 regression count is **zero**. The migrated scope is
  **offline verified**; the entire legacy UserESA suite is not claimed green.

### UserESA technical debt (out of scope)

Do not repair these during Phase 1 closure. The independent issues are:

- tests constructing `UserESA` with `__new__` without a `config` fixture;
- dose/distance fixture values inconsistent with current validation and
  expected error message/order;
- missing `experiment.thinnest_att_thick` in numeric UserESA fixtures;
- logger test writing `useresa.log` in the repository rather than a temporary
  writable directory.

### CoaxImage Phase 2 task

Keep `Libs/CoaxImage.py` unchanged. Its constructor reuses `self.blf.config`
as `self.config` and reads into that object (`Libs/CoaxImage.py:50-54`). A
simple `ZooConfig.load_config()` replacement could change parser identity and
hidden coupling. Phase 2 must first decide how to preserve or intentionally
replace that relationship, with dedicated regression coverage. No Phase 2 work
is part of this closure.

### Hardware verification plan (not executed)

The executable operator checklist is
`docs/operations/phase1-hardware-verification-checklist.md`. It fixes this
branch's verification target at `ee593fea2ea6f55814c816d0e7eeb32ffa31bdb1`
and separates software-only checks from operator-approved hardware steps.

Use the exact verification commit recorded in the handover and do not treat
one beamline result as proof for another. Execute only with the beamline
operator's approval and record beamline, host, runtime, `ZOOCONFIGPATH`/live
config identity, commit, command, result, and rollback point.

1. **Import/startup:** on an isolated operational clone, invoke the standard
   `yamtbx.python` runtime and import the migrated modules. Confirm no import
   error, unexpected process, or device command.
2. **Configuration read:** select the existing live configuration without
   editing it; confirm `ZOOCONFIGPATH/beamline.ini`, beamline identity, and
   representative sections/keys. Compare only read-only values.
3. **Device object initialization:** instantiate the normal objects in the
   approved startup order with communication monitoring. Confirm expected
   attributes and no unintended movement or write command.
4. **Read-only hardware query:** query status/position/limits only, one device
   at a time, with an operator-defined stop condition.
5. **Individual operation:** only after the preceding checks pass, test one
   approved low-risk device operation at a time, recording before/after state.
6. **ZOO startup:** launch the normal ZOO entry path and verify initialization
   and idle readiness without starting a measurement.
7. **Dry-run equivalent:** use an existing documented emulator/dry-run mode
   only if it already exists for that beamline; do not invent a new mode or
   infer that constructor tests are a dry-run.
8. **Before measurement:** confirm beamline identity, live config backup or
   recovery point, software commit, runtime, device idle state, and operator
   approval. No exposure or sample movement is part of this plan.

Rollback is to stop before the next step, restore the previously verified
working clone/commit, and restore any explicitly backed-up live configuration
only under the beamline's operational procedure. Record the failed step and
current hardware state; reverting Git alone does not undo hardware state.

### PR summary

- **Why:** remove duplicated `ZOOCONFIGPATH/beamline.ini` parser setup while
  preserving Phase 1 runtime behavior.
- **What changed:** added `Libs/ZooConfig.py` and migrated the listed core,
  A-class, and constructor-tested B-class modules; added offline tests.
- **Intentionally unchanged:** INI schema/values, constructors and order,
  config object sharing, singletonization, launchers, hardware logic,
  measurement logic, live config, and CoaxImage.
- **Tests:** focused Phase 1 suite `42 passed`; controlled base/current
  comparison found no new regression.
- **Regression comparison:** base `64/17`, current `106/17` (pass/fail) under
  identical writable-cwd conditions; the 17 failures predate Phase 1.
- **Remaining risks:** UserESA test technical debt, unverified real-beamline
  startup/device behavior, and CoaxImage config-object coupling.
- **Hardware verification:** pending; no hardware access was performed.
- **Phase 2:** decide and test the CoaxImage config identity/ownership boundary.

## Current next action

Do not change Phase 1 production code or repair UserESA tests in this audit.
The next action for the designated human verifier is to use
`docs/operations/phase1-hardware-verification-checklist.md` at the fixed
`ee593fe` commit. Hardware verification remains pending; do not merge to
`main`/`develop`. UserESA test-infrastructure follow-up remains a separate
technical-debt task.

## Last verified commit

Current branch commit: `ee593fe`

コードcommit: `b29bb94`

直近の文書commit: `6a59bdd`

直近のproduction migration commit: `88d7372`

A分類移行commit: `88d7372`

直近のhandover/remote同期確認commit: `22f812a`

Capture/Gonio44 baseline test commit: `844ae31`

Capture migration commit: `484bc79`

Gonio44 migration commit: `4dfec53`

Count migration commit: `c4f6c67`

Zoom migration commit: `3862abe`

CoaxPint migration commit: `57f1355`

CCDlen migration commit: `747afe0`

Mono migration commit: `7291d20`

PreColli migration commit: `6f45a12`

BaseAxis migration commit: `1a99ab3`

Gonio migration commit: `9c00171`

CoaxImage baseline test commit: `d68ba9f`

BSSconfig migration commit: `9faaf57`

Device migration commit: `041f6b2`

Zoo migration commit: `4b5b068`

ZooNavigator migration commit: `91ccdd1`

lets_goto_zoo migration commit: `53c3dd3`
