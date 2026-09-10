# ZOOALL

ZOOの装置制御・測定・データ処理を扱うPythonシステムです。コードと共通知識はこのGitリポジトリ、作業状態はGitHub Issueを正本とします。各端末は独立したcloneを使用します。

## 開発を始めるとき

1. [開発ワークフロー](docs/development/WORKFLOW.md)を読み、Issue・branch・既存差分を確認してください。
2. 中断作業はIssueにあるbranchとhandoffへのリンクから再開してください。mainにhandoffがなくても、中断作業がないとは限りません。
3. [環境と設定の説明](docs/development/ENVIRONMENTS.md)で対象環境と検証上の制約を確認してください。AIは[AGENTS.md](AGENTS.md)も読みます。

中断は通常運用です。未完成でも対象branchへcheckpointと[handoff](handoffs/TEMPLATE.md)をcommit・pushし、次の最初の操作を残します。詳細と例外時の扱いはワークフローを参照してください。

設計を選んだ理由は[decision log](docs/development/decision_log.md)に残します。進捗や完了状態は転載しません。

## 主な構成

| 場所 | 主な内容 |
| --- | --- |
| ルートのPythonファイル | ZOO起動、測定の統括、測定操作 |
| `Libs/` | 装置制御、DB/API、画像解析などのライブラリ |
| `TestScripts/` | 実機・API操作を含む試験スクリプト |
| `ZOOGUI/`, `KUMAGUI/` | GUI関連 |
| `KAMOscripts/`, `AutoProcCommand/` | データ処理関連 |
| `shell_scripts/` | 装置起動・運用関連のスクリプト |
| `docs/development/`, `handoffs/` | 開発ルール・判断理由・再開情報 |

`test`という名前は安全な自動テストであることを保証しません。実機・外部DBへの接続や更新がないか、実行前に確認してください。

`scripts/start_work.sh`、`scripts/finish_work.sh`と管理用YAMLは未実装です。現在は文書の手順で運用します。

## 過去の記録（既存本文）

# New Centering.py
## Challenge is True
#              if challenge==True and n_good == len(phi_list):
#                               break
#
#
#

README

2020/05/26 ZOO_ALL : branch BL32XU

2019/06/26 KUMA.py was copied from BL45XU

2018/04/13

2016/05/14
Facing algorhythm was changed but only 15 seconds difference 
compared to the previous one....

# Challenge is True only in 'loop finding'
new al:
2016-05-14 10:49:52.654304 2016-05-14 10:50:59.329782 0:01:06.675478
phi=198.0 for facing

old al:
2016-05-14 10:52:27.956139 2016-05-14 10:53:49.400480 0:01:21.444341
200.0 for facing

# Challenge is False
new al
2016-05-14 11:01:49.492805 2016-05-14 11:03:04.815910 0:01:15.323105

old al
2016-05-14 10:57:56.053784 2016-05-14 10:59:24.311595 0:01:28.257811


# Another loop
# All new
2016-05-14 11:10:22.667304 2016-05-14 11:11:26.278537 0:01:03.611233

# All old
2016-05-14 11:12:07.918708 2016-05-14 11:13:27.526993 0:01:19.608285

2022-04-21 14:24 test to upload to bitbucket

# Python 3 version is now 'main' branch
2023/05/31

2024/05/17
これから少し編集しようかなと思います

2024/06/28
Rough tests Okay at BL41XU at branch 
https://github.com/kuntaro0524/ZOOALL/commits/bl41xu_240627 

after BL41XU test, I evaluated the code at BL32XU.
multi, mixed, helical were okay.
Then, I merged 'bl41xu_240627' branch to 'main'.
Now I can remove 'bl41xu_240627' branch.

2024/07/04 Test
