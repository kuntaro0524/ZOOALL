# Decision log

長期的に残す設計・仕様の選択理由を記録する。作業進捗、open/closed、中断状態はIssueで管理する。新しいADR制度は導入しない。

追加時は日付、判断、背景・理由、検討した代替案、影響、関連Issue/PRを短く記す。判断を変更する場合は新しい項目から以前の項目を参照し、過去の理由を消さない。

## 2026-09-10：独立cloneと状態の正本

**判断:** 各端末は独立cloneを使い、コード・共通知識はGit、作業状態はIssueに集約する。branchは作業コード、PRはmainへの統合、handoffはcheckpoint時点の再開情報とする。

**理由:** 複数端末・人・AIが参加するため、同じworking treeや人間の記憶への依存を避ける。状態の複製による食い違いを防ぐ。

**代替案:** working treeの共有、文書・Project・handoffそれぞれでの独立した進捗管理。

**影響:** handoffには独立した完了状態を持たせない。初期段階では`handoffs/open/`と`archive/`を作らず、不要になった記録はGit履歴へ残す。

## 2026-09-10：PAUSEDを通常運用にする

**判断:** 未完成でも作業branchへcheckpointとhandoffをcommit・pushし、openなIssueの`paused`表示と再開先リンクから再開する。

**理由:** ビームラインの開発・実機試験は時間切れで中断することが多い。一週間後や別端末でも、最初から調査せず続けられる必要がある。

**代替案:** 完成までローカルに保持する、stashだけで保存する、口頭で引き継ぐ。

**影響:** pushとIssueのリンク更新までが共有手順。handoffには確認済み・未確認・次の一手・再実行禁止事項を残す。実機の現在状態は再開時に再確認する。

## 2026-09-10：管理量を変更の規模と影響に合わせる

**判断:** 小変更は短いIssueとPRを基本にし、handoffは中断・引き継ぎ時、decision logは長期的な判断時に作る。READMEを入口にして共通規則はWORKFLOWへ集約する。

**理由:** 1ファイルの変更から装置・DB・Webを横断する変更まである。全件に同じ文書量を課すと運用が続かない。

**代替案:** 全件に設計書・日報・handoffを要求する、入口と規則を多数の文書へ分散する。

**影響:** START_HEREとDEVELOPMENT_RULESは初期段階では作らない。1ファイルでも実機やDBに影響すれば検証を厚くする。

## 2026-09-10：実行設定と開発管理用YAMLを分ける

**判断:** ZOOが読む`beamline.ini`は既存方式を維持する。環境の役割・検証可能範囲・運用上の注意は、後続段階でGit管理する`config/environments.yaml`へ整理する。clone固有情報は必要に応じGit管理外の`config/local.yaml`へ分ける。

**理由:** ビームラインの実行設定と、開発・再開を支援する環境情報は目的が異なる。管理用YAMLは開始時の案内とhandoffの環境識別に役立つ。

**代替案:** `beamline.ini`をYAMLに置換する、管理用YAMLを設けず情報を散在させる、両方に同じ装置設定を書く。

**影響:** 今回は仕様の文書化まで。実行設定や起動処理を変更せず、`beamline.ini.example`も今回追加しない。YAML導入時は文書の環境表との二重管理を解消する。

## 2026-09-10：ZOO開発に使うAIモデルを作業規模で選ぶ

**判断:** 通常の調査、小〜中規模のコード修正、テスト追加、文書化、PR準備は`gpt-5.6-sol`を標準にする。複数モジュールの変更、develop/main統合、装置挙動に関わる判断、設計整理は`gpt-6-astra`を優先する。単純な検索・一覧作成は軽量モデルでもよい。

**理由:** ZOOのアルゴリズム自体が常に高度というより、古いPythonコード、BL32XU・BL45XU・BL41XUの差、設定・装置・DB・Webの関係、実機影響の判断が難しい。通常作業には速度と能力のバランスを取り、大きな判断にはより強いモデルを使う。

**運用上の制約:** モデルの判断だけで実機操作や本番DB更新を行わない。対象環境、実施した検証、未確認事項を記録する。BL32XUでの確認をBL45XU・BL41XUの合格とは扱わない。モデル選択は作業品質を補助するもので、Issue・branch・PR・handoffの正本を置き換えない。

上記の根拠は開発管理整備に関する依頼・合意。対応Issue/PRは文書作成時点で未設定であり、番号を仮定していない。

## 2026-09-14：`beamline.ini`読み込み処理を共通loaderへ段階的に集約する

**判断:** `ZOOCONFIGPATH`から`beamline.ini`を決定し、
`ConfigParser(interpolation=ExtendedInterpolation())`で読み込む機械的処理を、
独立した共通loaderへ段階的に集約する。Phase 1ではloaderと単体テストだけを
追加し、既存production moduleの移行は後続checkpointとする。

**背景:** 現在は複数moduleが`ZOOCONFIGPATH`と`beamline.ini`を個別に扱っている。
一方、設定形式、section/key、初期化順序、各classのconfig属性は既存runtimeの
一部であり、今回の目的は設定アクセス方法の共通化に限定する。

**理由:** 一度にconfig object共有まで行うと、constructor、initialization order、
hidden coupling、循環importの影響範囲が大きくなる。そのためPhase 1ではloader
のみを共通化し、singleton、global object、dependency injection、INI schema変更、
hardware/measurement logic変更を行わない。

**代替案:** 各moduleの個別読込を維持する、最初から全moduleへconfig objectを注入
する、またはglobal singletonへ置換する。前二者は重複を残し、後二者は初期化順序
と隠れた共有状態の変更が大きいため、Phase 1の範囲には採用しない。

**影響:** `ZOOCONFIGPATH`、`beamline.ini`、`ExtendedInterpolation`、既存例外挙動は
維持する。loader導入だけでは通常測定経路は変更されず、production module移行時に
個別の互換性検証が必要になる。関連Issue/PRは未設定であり、番号を仮定しない。

## 2026-09-14：Issueを任意の管理手段とし、branchとhandoverを再開の基盤とする

**判断:** Issueはbug、future task、idea、未着手課題、複数人で共有する課題に利用する
任意の管理手段とする。Issueがなくても、current branch、branch-specific handover、
Git commits、関連architecture/decision文書から作業を開始・中断・再開できるようにする。

**理由:** 実作業のcheckpointはbranchとGit commitに存在し、AI・人間間の再開に必要な
事実と次の一手はhandoverに記録できる。Issueを必須にすると、Issue未作成の小規模作業や
オフライン作業の開始・再開を不必要に妨げる。

**影響:** START/STOP/FINISHはIssueの有無に依存しない。Issueがある場合は課題の共有と
受入条件に利用するが、進捗の正本をIssueへ二重記録しない。

## 2026-09-14：runtime、live config、thin launcherの責任を分離する

**判断:** `yamtbx.python`をDIALS/cctbx/yamtbx環境を提供する標準runtime/dispatcherとし、
`ZOOCONFIGPATH`と`beamline.ini`をZOO runtime configurationとして扱う。将来の
beamline-specific launcherは主に`ZOOCONFIGPATH`を選択して`yamtbx.python`を呼ぶ薄い層とする。
live `beamline.ini`はGit pull/mergeで自動変更せず、Git側のbeamline別canonical configと
明示的な適用操作を分離する。

**理由:** Python runtime、ZOO import path、beamline設定、live適用操作を一つのlauncherや
Git操作へ結合すると、実行環境と装置設定の変更範囲が不明確になるため。

**影響:** 歴史的な`zoo.python`は直ちに削除・変更しない。canonical/live比較、beamline
identity確認、backup、explicit applyは将来の検討事項であり、今回はscriptを追加しない。

## 2026-09-14：Phase 1 production migrationを小さなcheckpointに分割する

**判断:** `ZooConfig`の正式test確認後、Phase 1のproduction migrationは一度に全moduleへ
適用せず、まず`Libs/BLFactory.py`の設定path構築・parser読込だけをloaderへ委譲する。
`BSSconfig.py`、`Device.py`、`Zoo.py`、`ZooNavigator.py`、`lets_goto_zoo.py`は別checkpoint
で評価する。

**理由:** `BLFactory`は設定読込後に既存のconfig属性、key取得、BSSconfig生成、hardware初期化
へ進むため、loader委譲だけを独立に検証できる。複数moduleを同時変更すると、constructorや
initialization orderの差異を切り分けにくくなる。

**影響:** 今回の移行ではconfig object共有、singleton化、constructor変更、initialization
order変更、hardware/device/measurement logic変更を行わない。既存のpath表示と`BLFactory.config`
属性は維持し、offline testでloader接続と代表的な設定値を確認する。

## 2026-09-14：Phase 1 migrationの完了境界とCoaxImageのPhase 2扱い

**判断:** Phase 1の対象moduleについて、`ZooConfig.load_config()`へのloader委譲と
offline回帰確認を完了した。`Libs/CoaxImage.py`はPhase 1から除外し、Phase 2の明示的課題
として残す。Phase 1の状態は「implementation complete / offline verified」とするが、
実機によるhardware verificationは未実施でありpendingとする。

**根拠:** CoaxImageのconstructorは`self.blf.config`を`self.config`として再利用し、同じ
parserへ`beamline.ini`を読み込む（`Libs/CoaxImage.py:50-54`）。単純なloader置換は
config object identity、constructor relationship、hidden couplingを変更する可能性があり、
Phase 1の責任範囲を越える。残存するstandalone utility、launcher variant、legacy/dead
example、test/fixtureの直接読み込みも、通常測定coreの安全なloader移行対象とは扱わない。

**検証:** 移行module・A分類・B分類constructor baseline・CoaxImage baselineを含むfocused
offline suiteは`42 passed`。Phase 1開始直前のbase commit
`1996d2c4aca0ac5f2cf4272320d105869c740fa5`を別worktreeへ展開し、同じruntime・同じ
書込み可能cwdで比較した結果、baseは`64 passed, 17 failed`、currentは`106 passed,
17 failed`だった。17件はtest名・失敗箇所・例外が一致した。repo直下のread-only cwdでの
current実行では`105 passed, 18 failed`となり、追加1件は`useresa.log`作成失敗である。
したがってPhase 1由来の新規regressionは0件であり、残る17件とlogging条件はUserESAの
既存test/fixture・実行環境課題として別途扱う。

**影響:** CoaxImageのconfig object identityを維持したままPhase 2で扱いを決めるまで、
production codeは変更しない。full-suite failureの原因整理とhardware verificationは
別の確認事項として残す。関連Issue/PRは未設定であり、番号を仮定しない。

## 2026-09-14：Phase 1 closure preparationの境界

**判断:** Phase 1のproduction migrationは現在のmigrated scopeで閉じ、これ以上の
production code変更は行わない。focused offline suiteは`42 passed`、base/current比較で
Phase 1由来の新規regressionは0件である。hardware verificationは未実施として別工程に
残す。UserESAの既存test failureはPhase 1とは独立したtechnical debtとして記録する。

**影響:** closureではmodule/test対応表、base/current evidence、低リスク順のhardware
verification plan、rollbackとcommit traceabilityだけを文書化する。実機接続やcommand送信、
CoaxImage移行、Phase 2のconfig object共有は行わない。main/developへのmergeは行わない。
