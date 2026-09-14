# 開発ワークフロー

## 基本原則と正本

各端末は独立したGit cloneを持つ。コードと共通知識はGitを正本とする。
Issueは必須ではなく、bug、future task、idea、未着手課題、複数人で共有する課題を
管理する任意の手段とする。実作業開始後の現在状態は、current branch、branch-specific
handover、Git commits、関連architecture/decision文書から復元できるようにする。
中断は通常運用として扱い、一週間後でも数分で次の操作を特定できる記録を残す。

| 対象 | 役割 |
| --- | --- |
| Issue（任意） | bug、future task、idea、未着手課題、複数人で共有する課題、受入条件、担当 |
| Branch | 実際の作業コードと未完成のcheckpoint |
| PR | 完成した変更をmainに統合するためのレビュー・最終確認 |
| decision log | 設計・仕様を選んだ理由と代替案。進捗は書かない |
| handover | 特定checkpoint時点の事実、未確認事項、次の一手、再実行上の注意 |

新しいADR制度は作らない。Issueのopen/closedや中断状態を別の表・文書・Projectへ手入力で複製しない。

## 規模と影響に応じた管理

| 変更 | 記録と検証 |
| --- | --- |
| 小さくその場で完了 | 短いIssue、branch、短いPR、影響に応じた検証 |
| 複数モジュール | Issueがあれば受入条件と影響範囲を記録。引き継ぎ時はhandover |
| 装置・DB・Web等を横断 | 必要に応じIssueと段階的PR。環境別検証、復旧・切戻し方法 |
| 規模を問わず中断 | checkpointのpushとhandover |

1ファイルでも装置制御・DB更新に影響する場合は検証を厚くする。全変更に設計書・decision log・日報を要求しない。長期的に理由を残す必要がある判断だけdecision logへ書く。

## START

1. `git status --short --branch`、`git branch -vv`、`git rev-parse HEAD`でrepositoryの
   更新状態、current branch、upstream、HEADを確認する。
2. 対応するIssueがあれば目的、受入条件、担当、関連する中断情報を読む。Issueがなくても
   作業開始を妨げない。
3. branch-specific handoverを作成または確認し、README、本文書、ENVIRONMENTS、
   relevant architecture/decision文書、AIの場合はAGENTSも読む。
4. 必要ならmainからwork branchを作る。既存の作業branchを無用に改名しない。
5. baseline testを確認し、実行可能な範囲で実行する。別端末・別担当が同じbranchへ
   同時に書き込まない。

既存差分があれば内容と由来を確認し、勝手にstash・削除・commitしない。運転用cloneでは稼働中にcheckout・pull・mergeしない。開始時の自動pullは導入しない。

Issueを作成しない作業では、Issue参照を作らず、branch、commit、handover、関連文書で
目的と状態を復元可能にする。Issueへ接続できない場合もIssue番号を捏造しない。

## STOP / 中断

測定対応、時間切れ、別作業などで中断する場合は、作業を数日から数週間後に復元
できる状態にする。Issueがある場合は必要に応じて`paused`を付け、再開時に外す。

handoverには独立した完了状態を作らず、checkpoint時点の事実として記録する。

中断手順：

1. 実機・測定・DB処理を現場の手順に従って中断可能な状態にする。終了を確認できない操作は不明と記録する。
2. 差分を確認し、対象ファイルを明示して未完成コードをcommitする。無関係な変更・実データ・認証情報を含めない。未完成commitをmainに直接統合しない。
3. [テンプレート](../../handoffs/TEMPLATE.md)からbranch-specific handoverを作成・更新する。
   コードcommit、使用環境、実行したtest、未確認事項、次のactionを記録する。
4. 必要に応じてcheckpoint commitを作成する。handoverのcommitはコードcommitと分けてもよい。
5. push可能ならbranchをpushする。Issueがある場合はbranchとhandoverを関連付ける。
   Issueがない場合も、branchとGit上のhandoverから再開できる状態を残す。

実施できるtestがない場合も、未実行理由をhandoverに記録する。実機・DB・外部API操作を
行った場合は、成否・現在状態・設定・復旧上の注意を記録する。

push失敗時は「ローカル保存済み・共有未完了」とする。Issue更新だけ失敗した場合も「push済み・再開先の案内未更新」と区別する。どちらも引き継ぎ完了と報告しない。装置の中断をGit操作の成功待ちにしない。

## 再開

1. Issueがある場合はIssueから、ない場合はcurrent branchとhandoverから再開先を特定する。
   mainの`handoffs/`だけを探して中断作業の有無を判断しない。
2. 手元の差分と運転状況を確認後、remoteの対象branchを取得し、そのbranchで作業する。古いローカルbranchを無条件に上書きしない。
3. handoffのコードcommit、取得したHEAD、設定・検証環境を照合する。handoffの後に変更があれば、その差分を先に確認する。
4. 装置・試料・測定・DBの現在状態を現場の手順で確認する。中断時の状態を現在も同じと仮定しない。
5. Issueがある場合は担当と`paused`を確認し、handoverの「次に最初にやること」から始める。

測定・DB更新などを繰り返す前に、前回操作の成否と二重実行の影響を確認する。コードを再開するために装置の初期化からやり直す必要があるとは限らない。

## FINISH

| 区分 | 扱い |
| --- | --- |
| completed | 今回の実装と必要な検証を終え、PRへ変更・検証結果・制限を書く。Issueは受入条件を満たし、対応変更の統合を確認してcloseする |
| paused | 実装途中、実機試験待ち、後日継続など。上記の中断手順を実施する |
| no meaningful change | 引き継ぐ成果がなければ日報や空commitは不要。既存差分や未pushを消さず、その存在を報告する |

FINISHでは、tests、documentation、handover最終更新、PR/review、merge後の
branch/handover整理を確認する。Issueがある場合のみ、その受入条件とopen/closedを
更新する。実装終了とIssue完了は同義ではない。実機試験が受入条件なら、実装済みでも
試験待ちは未完了として扱う。

PRは関連Issue、変更理由、検証環境・対象commit・結果、未確認事項を含める。段階的PRではIssue全体の受入条件が満たされる前に自動closeしない。実機影響がある変更には切戻し方法と、コードを戻すだけでは復元できないDB・測定状態も記載する。

handoverは対応branch上で更新する。統合時に不要になったhandoverは削除し、履歴から
参照可能にする。未確認事項が残る場合はhandoverまたはIssueへ引き継ぐ。
`open/`・`archive/`による作業状態管理は導入しない。

## 実運用中のproduction code

測定中にrunning production codeを直接変更しない。問題を発見した場合は、通常は記録して
測定を継続し、別branchで修正する。運転中のcloneでcheckout・pull・mergeや実行コードの
変更を行わない。

## Emergency hotfix

緊急修正が不可避な場合は、最低限以下を記録する。

- hotfix branch
- 修正前commit
- 修正内容
- 実行したtest
- 使用したbeamline/runtime config
- rollback方法
- 測定再開時に使用したcommit

hotfixでも実機影響と未確認事項をhandoverに残す。通常の修正branchへ後から混ぜる場合は
別PRまたは明示的なreview対象として扱う。

## Software/runtime traceability

測定・解析結果を後から追跡できるよう、可能な範囲で以下を記録する。

- ZOO commit
- 使用した関連repoのcommit
- Python/runtime
- beamline
- 使用したruntime configの識別情報

具体的なファイル形式や`software_versions.json`の導入は未決定とする。

## 補助スクリプトの仕様（未実装）

`scripts/start_work.sh`はbranch・HEAD・差分・upstream・未push、現在branchのhandover、
Issueがあればそこから得た中断作業、必読文書を表示する。Issueがない場合も「Issueなし」
として継続できる。自動pull・checkout・装置接続はしない。

`scripts/finish_work.sh`は上記3区分を選択し、STOP/FINISH時のhandover作成・更新を支援する。
branch、コードcommit、host、タイムゾーン付き日時を自動取得し、Issue参照は任意とする。
人間の入力は事実・未確認・次の一手・注意に絞る。commit・pushの前に対象差分を表示し、
一括`git add .`を前提としない。

両スクリプトはZOOのPython環境や装置接続を必要としない構成とし、MacとUbuntuで確認する。Issueの取得・更新手段、認証、接続失敗時の表示は実装段階で決める。

## 導入順序

1. Git・端末の現状を確認し、大小文字衝突などの課題を記録する。
2. 本文書群で一件の中断・別端末再開を手動試行する。
3. 成功した手順を補助スクリプト化し、未push・オフライン・mainからの発見を検証する。
4. 管理用YAML、環境別の試験一覧、安全なオフライン試験、依存管理・CIを段階的に整備する。

再開試行の合格基準は、別端末の担当がIssueからcheckpointへ到達し、数分で最初の操作と再実行禁止事項を説明できること。実機操作そのものの実行は必須ではない。
