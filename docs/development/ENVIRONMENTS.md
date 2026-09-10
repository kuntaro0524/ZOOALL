# 開発環境と設定

## 環境の役割

各端末は独立cloneを使用する。端末間のコード共有はcommit・push・取得で行う。作業状態と再開先はIssueから確認する。

| 環境ID（予定） | OS | 役割 | 検証上の扱い |
| --- | --- | --- | --- |
| `bl32xu` | Ubuntu | 主にZOO実機運転・実機試験 | BL32XUでの結果として記録 |
| `bl45xu` | Ubuntu | 主にZOO実機運転・試験 | 物理アクセスが難しい。次回の確認操作と現場対応の要否を具体化 |
| `office_mac` | macOS | 主開発、コード編集、情報整理 | 実機を使わない検証が中心 |
| `laptop_mac` | macOS | 自宅等での補助開発 | 独立cloneから再開。主開発端末の未push変更には依存しない |

host名と環境IDは別情報。host名だけでビームラインや装置操作の許可を判定しない。運転中のcloneではcheckout・pull・mergeや実行コード変更を行わない。試験用cloneが別途必要かは各現場の運用を確認して決める。

## ZOOの実行設定と開発管理情報

`beamline.ini`はZOOが読み込むビームライン設定ファイルである。`Libs/BLFactory.py`、`Libs/Device.py`等は`ZOOCONFIGPATH`の配下から読み込む。開発支援スクリプト用の設定とは区別する。

| ファイル・情報 | 役割と方針 |
| --- | --- |
| `beamline.ini` | 装置・ビームラインの実行設定。今回の管理整備では配置・読込方式を変更しない |
| `ZOOCONFIGPATH` | ZOOが設定を探すディレクトリ。既存起動方法に従う |
| `config/environments.yaml`（未作成） | Git管理する共通知識。環境ID、役割、実施できる検証、運用上の注意 |
| `config/local.yaml`（未作成・必要時のみ） | Git管理外。このcloneの環境IDやローカルパス。導入時には例ファイルとgitignoreも用意する |

管理用YAMLへ装置アドレス・校正値などの実行設定を転記しない。`beamline.ini`の代替ローダーも追加しない。YAML導入後は環境ごとの構造化情報をYAMLに集約し、この文書には意味・利用方法を残す。表とYAMLを手動で二重更新する運用にはしない。

実機試験のhandoffには使用環境、コードcommit、設定の所在と識別情報を残す。設定のhash等は同一性確認に利用できるが、それだけで設定を復元できるわけではない。端末限定の設定やログは、別担当がどう参照できるかも記す。認証情報や実データの不用意なGit追加は避ける。

## 検証の区分

| 区分 | 実行前に確認すること | 記録すること |
| --- | --- | --- |
| オフライン | 装置・外部APIへ接続せず、検証用データだけを使うか | 対象commit、実行環境、手順、結果 |
| DB/API統合 | 接続先が検証用か、書込範囲、復旧方法 | 接続先の識別情報、更新対象、結果、未復旧事項 |
| 実機 | 対象BL、運転状況、操作範囲、現場の実施条件 | 設定識別情報、試料・測定ID、操作と成否、ログ、未確認事項 |

BL32XUでの合格をBL45XUでの合格とは扱わない。Macでの検証も実機確認の代わりにはならない。実施していない試験は未確認と書く。

現在の`TestScripts/`は実機やAPIを更新するスクリプトを含む。例として`TestScripts/20_set_beamsize.py`はビームサイズを変更し、`TestScripts/ECHA/Abstract/parameter_update_test.py`は測定情報を更新する。名前による一括テスト実行は行わない。安全に実行可能な一覧と`TESTING.md`は後続段階で整備する。

## 2026-09-10の調査記録

この節はローカルcloneを調査した時点の事実であり、現在の作業状態や課題の進捗表ではない。対応作業の状態はIssueで管理する。

- HEADは`7ebd3bd`、branchは`main`。originは`git@github.com:kuntaro0524/ZOOALL.git`。mainのupstream設定は確認できなかった。
- 開始時点で` shell_scripts/BSS_startup.sh`に差分があった。由来を確定せず、編集・取り消し・commitしていない。
- 調査時点ではGit管理対象に大小文字だけが異なる4組があった。内容が完全一致し、リポジトリ内の参照もなかったため、`Libs/Arg.py`、`Libs/Flux.py`、`Libs/Spline.py`、`shell_scripts/BSS_startup.sh`を正として小文字側を削除した。このcloneの`core.ignorecase`は`true`であり、MacとUbuntuの独立clone運用に必要な整理である。外部から小文字名を直接呼び出していないことは別途確認する。
- `beamline.ini`はgitignore対象。`Libs/`にはビームライン別・日付別のINIがGit管理されていた。ファイル名だけでは現用か判断できない。
- `zoo.python`は`zoo.python.bl44xu`へのリンク。各`zoo.python.*`はPython環境や端末パスを指定している。`Libs/ConfigFile.py`には別形式の設定への固定パスも残る。
- 標準的なPython依存定義・テストランナー設定・`.github/`は見当たらなかった。Git履歴にはPRマージがある。
- GitHub上の最新Issue・保護設定・権限、他端末のclone・実行commit・現用設定は未確認。fetch、実機操作、試験実行は行っていない。

後続の棚卸しでは各端末の実行commit、Python環境、設定の所在、運転用cloneと試験作業の関係を確認する。運用改善のために現用設定を一括置換しない。
