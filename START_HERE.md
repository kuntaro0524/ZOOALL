# ZOO Development Start Here

このファイルは、ZOO開発を別端末・別セッション・別AIから再開するときの入口です。
ここには個別作業の詳細や技術仕様を複製しません。現在の状態は、Git、handover、
管理文書、実コードを確認して復元してください。

## 最初に読む文書

1. [README.md](README.md)：repositoryの概要
2. [AGENTS.md](AGENTS.md)：AI agent向けの作業ルール
3. [docs/development/WORKFLOW.md](docs/development/WORKFLOW.md)：START / STOP / FINISH、Git、handoverの正本
4. [docs/development/ENVIRONMENTS.md](docs/development/ENVIRONMENTS.md)：実行環境、設定、実機検証の制約
5. 対応branchのhandover：現在の作業状態、未確認事項、次の一手
6. 必要なarchitecture文書：構成・責任範囲・依存関係
7. [docs/development/decision_log.md](docs/development/decision_log.md)：長期的な設計判断と理由

## 情報の確認先

| 確認したい情報 | 確認先 |
| --- | --- |
| 開発・Git運用ルール | [docs/development/WORKFLOW.md](docs/development/WORKFLOW.md) |
| AI agentの作業ルール | [AGENTS.md](AGENTS.md) |
| 実行環境、beamline設定、実機検証 | [docs/development/ENVIRONMENTS.md](docs/development/ENVIRONMENTS.md) |
| configuration architecture | [docs/architecture/configuration.md](docs/architecture/configuration.md) |
| hardware verification手順 | [docs/operations/phase1-hardware-verification-checklist.md](docs/operations/phase1-hardware-verification-checklist.md) |
| 設計判断 | [docs/development/decision_log.md](docs/development/decision_log.md) |
| 現在進行中の作業・未完了事項・次の一手 | current branchのhandover（[handoffs/](handoffs/)） |
| handoverの書式 | [handoffs/TEMPLATE.md](handoffs/TEMPLATE.md) |

`docs/decisions/`はこのrepositoryには存在しません。設計判断の正本は
`docs/development/decision_log.md`です。

## 作業再開手順

1. `START_HERE.md`を読む。
2. 現在のbranchと、そのbranchに対応する最新handoverを確認する。
3. `git status`、current branch、upstream、最近のcommitを確認する。
4. 作業に必要なarchitecture文書とdecision logを読む。
5. 文書と実コードに不整合がないか確認する。
6. 現在地点、完了済み、未完了事項、次の1手を報告する。
7. その後に実装または検証を開始する。

原則として、

> 過去の作業状態を記憶や推測から復元しない。Git、handover、管理文書、実コードを確認する。

Issueは必須ではありません。Issueがある場合は目的・受入条件・共有課題を確認し、
Issueがない場合もbranch、commit、handover、関連文書から再開してください。

## 作業時の注意

- 既存の未commit変更を所有者確認なしに変更・破棄・commitしない。
- 測定中のrunning production code、live `beamline.ini`、装置状態を無断で変更しない。
- `TestScripts/`や名前だけでは安全性を判断できないscriptを一括実行しない。
- hardware、DB、外部APIへ接続する前に対象・権限・rollback・記録方法を確認する。
- 実行環境や設定の修正は、既存のruntime方針とconfiguration architectureの記述を確認してから行う。
- 作業終了時はWORKFLOWに従い、必要なtest、handover、documentation、commit、pushの状態を記録する。

## 未解決事項の扱い

個別の未解決事項はこの入口文書へ詳細を追加せず、内容に応じてcurrent branchのhandover、
architecture文書、または`docs/development/decision_log.md`へ記録してください。作業を開始した
時点で未解決事項が見つかった場合は、実装前に現在地点・影響・STOP条件を報告します。
