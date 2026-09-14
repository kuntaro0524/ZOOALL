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
- `/usr/bin/python3`にはpytestがないが、正式runtimeの実行結果には影響しない。
- hardware接続、測定、外部process起動は行っていない。

## Next action

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
単純な`Libs/Count.py`、`Libs/Zoom.py`、`Libs/CoaxPint.py`を候補とする。
いずれも`BSSconfig`読込とMotor生成を含むため、fake `BSSconfig`/`Motor`と
socket fail-fastを使うconstructor testを先に追加・実行する。test成功前のproduction
移行は行わない。

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
- B分類constructorの実行test自体はまだ追加・実行していない。今回の確認は静的解析のみ。
- Capture/Gonio44についてはbaseline constructor testを追加・実行済み。
- Captureについてはloader移行後のconstructor testも成功済み。
- Gonio44についてはloader移行後のconstructor testも成功済み。
- C候補がないことは静的調査の範囲の結論であり、import実行時副作用を全面保証するものではない。

## Last verified commit

コードcommit: `b29bb94`

直近の文書commit: `6a59bdd`

直近のproduction migration commit: `88d7372`

A分類移行commit: `88d7372`

直近のhandover/remote同期確認commit: `22f812a`

Capture/Gonio44 baseline test commit: `844ae31`

Capture migration commit: `484bc79`

Gonio44 migration commit: `4dfec53`

BSSconfig migration commit: `9faaf57`

Device migration commit: `041f6b2`

Zoo migration commit: `4b5b068`

ZooNavigator migration commit: `91ccdd1`

lets_goto_zoo migration commit: `53c3dd3`
