# 開発ワークフロー

## 基本原則と正本

各端末は独立したGit cloneを持つ。コードと開発知識はGit、作業状態はGitHub Issueを正本とする。中断は通常運用として扱い、一週間後でも数分で次の操作を特定できる記録を残す。

| 対象 | 役割 |
| --- | --- |
| Issue | これから行う作業、バグ、改善、受入条件、担当、現在の作業状態 |
| Branch | 実際の作業コードと未完成のcheckpoint |
| PR | 完成した変更をmainに統合するためのレビュー・最終確認 |
| decision log | 設計・仕様を選んだ理由と代替案。進捗は書かない |
| handoff | 特定checkpoint時点の事実、未確認事項、次の一手、再実行上の注意 |

新しいADR制度は作らない。Issueのopen/closedや中断状態を別の表・文書・Projectへ手入力で複製しない。

## 規模と影響に応じた管理

| 変更 | 記録と検証 |
| --- | --- |
| 小さくその場で完了 | 短いIssue、branch、短いPR、影響に応じた検証 |
| 複数モジュール | Issueに受入条件と影響範囲。引き継ぎ時だけhandoff |
| 装置・DB・Web等を横断 | 必要に応じ親子Issueと段階的PR。環境別検証、復旧・切戻し方法 |
| 規模を問わず中断 | checkpointのpushとhandoff |

1ファイルでも装置制御・DB更新に影響する場合は検証を厚くする。全変更に設計書・decision log・日報を要求しない。長期的に理由を残す必要がある判断だけdecision logへ書く。

## 作業開始

1. `git status --short --branch`、`git branch -vv`、`git rev-parse HEAD`でbranch・差分・upstream・HEADを確認する。
2. 対象Issueの目的、受入条件、担当、中断情報を読む。新規作業は短いIssueを作成し、作業branchと対応づける。
3. README、本文書、ENVIRONMENTSと対象handoffを読む。AIはAGENTSも読む。
4. 新規実装はmainから作業branchを作る。命名は`work/123-short-topic`を基本とし、既存の作業branchを無用に改名しない。
5. 別端末・別担当が同じbranchへ同時に書き込まないよう、Issue上で引き継ぎ先を明確にする。同時作業は別branchに分ける。

既存差分があれば内容と由来を確認し、勝手にstash・削除・commitしない。運転用cloneでは稼働中にcheckout・pull・mergeしない。開始時の自動pullは導入しない。

Issueへ接続できない緊急の継続作業ではローカル保存を優先する。Issue番号を捏造せず、handoffに「Issue参照未設定」と記録し、接続回復後に対応づける。これは共有未完了であり、通常の別端末引き継ぎ完了とは扱わない。

## PAUSED / 中断

Issueはopenのまま`paused`ラベルを付ける。再開時に外す。ラベルの導入・GitHub更新がまだできない場合はIssue本文の一か所を暫定の中断表示とし、ラベル導入時に二重表示を解消する。

handoffには独立した状態フィールドや完了チェックリストを作らない。「完了したこと」はcheckpoint時点の事実であり、Issueの完了状態ではない。

中断手順：

1. 実機・測定・DB処理を現場の手順に従って中断可能な状態にする。終了を確認できない操作は不明と記録する。
2. 差分を確認し、対象ファイルを明示して未完成コードをcommitする。無関係な変更・実データ・認証情報を含めない。未完成commitをmainに直接統合しない。
3. [テンプレート](../../handoffs/TEMPLATE.md)から`handoffs/issue-123-short-topic.md`を作成・更新する。コードcommitを記録し、handoffを別commitで保存する。コード変更がない場合は検証・調査対象の既存commitを参照する。
4. branchをpushし、handoffを含むcommitがremote branchへ反映されたことを確認する。
5. Issueにbranchとhandoffへのリンクを置き、`paused`にする。handoffリンクはpushしたcommitに固定し、次のcheckpointで置き換える。進捗本文をIssueへ転載しない。

push失敗時は「ローカル保存済み・共有未完了」とする。Issue更新だけ失敗した場合も「push済み・再開先の案内未更新」と区別する。どちらも引き継ぎ完了と報告しない。装置の中断をGit操作の成功待ちにしない。

## 再開

1. Issueからbranchとhandoffを特定する。mainの`handoffs/`だけを探して中断作業の有無を判断しない。
2. 手元の差分と運転状況を確認後、remoteの対象branchを取得し、そのbranchで作業する。古いローカルbranchを無条件に上書きしない。
3. handoffのコードcommit、取得したHEAD、設定・検証環境を照合する。handoffの後に変更があれば、その差分を先に確認する。
4. 装置・試料・測定・DBの現在状態を現場の手順で確認する。中断時の状態を現在も同じと仮定しない。
5. Issueの担当を確認して`paused`を外し、handoffの「次に最初にやること」から始める。

測定・DB更新などを繰り返す前に、前回操作の成否と二重実行の影響を確認する。コードを再開するために装置の初期化からやり直す必要があるとは限らない。

## 作業終了

| 区分 | 扱い |
| --- | --- |
| completed | 今回の実装と必要な検証を終え、PRへ変更・検証結果・制限を書く。Issueは受入条件を満たし、対応変更の統合を確認してcloseする |
| paused | 実装途中、実機試験待ち、後日継続など。上記の中断手順を実施する |
| no meaningful change | 引き継ぐ成果がなければ日報や空commitは不要。既存差分や未pushを消さず、その存在を報告する |

実装終了とIssue完了は同義ではない。実機試験が受入条件なら、実装済みでも試験待ちはopenのまま。調査のみでも次回に必要な結論が得られたらIssueまたはhandoffへ残す。

PRは関連Issue、変更理由、検証環境・対象commit・結果、未確認事項を含める。段階的PRではIssue全体の受入条件が満たされる前に自動closeしない。実機影響がある変更には切戻し方法と、コードを戻すだけでは復元できないDB・測定状態も記載する。

handoffは対応branch上で更新する。統合時に不要になったhandoffは削除し、履歴から参照可能にする。未確認事項が残る場合は先にIssueへ引き継ぐ。`open/`・`archive/`による作業状態管理は導入しない。

## 補助スクリプトの仕様（未実装）

`scripts/start_work.sh`はbranch・HEAD・差分・upstream・未push、現在branchのhandoff、Issueから得た中断作業、必読文書を表示する。接続できない場合は「Issue状態未確認」とする。自動pull・checkout・装置接続はしない。

`scripts/finish_work.sh`は上記3区分を選択し、paused時のhandoff作成・更新を支援する。branch、コードcommit、host、タイムゾーン付き日時を自動取得し、Issue参照は初回指定後に引き継ぐ。人間の入力は事実・未確認・次の一手・注意に絞る。commit・pushの前に対象差分を表示し、一括`git add .`を前提としない。

両スクリプトはZOOのPython環境や装置接続を必要としない構成とし、MacとUbuntuで確認する。Issueの取得・更新手段、認証、接続失敗時の表示は実装段階で決める。

## 導入順序

1. Git・端末の現状を確認し、大小文字衝突などの課題を記録する。
2. 本文書群で一件の中断・別端末再開を手動試行する。
3. 成功した手順を補助スクリプト化し、未push・オフライン・mainからの発見を検証する。
4. 管理用YAML、環境別の試験一覧、安全なオフライン試験、依存管理・CIを段階的に整備する。

再開試行の合格基準は、別端末の担当がIssueからcheckpointへ到達し、数分で最初の操作と再実行禁止事項を説明できること。実機操作そのものの実行は必須ではない。
