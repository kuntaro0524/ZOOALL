# Handoff: ZOO-005 portable zpython runtime

- Issue: なし（zoo-hub work item `ZOO-005`）
- Branch: `feature/ZOO-005-portable-runtime`
- コードcommit: `4336b98b483ee9031b39921d0c92a9a7ab82f7c3`
- 記録者: Codex（次担当agent向け）
- Host: `kuri04.spring8.or.jp`
- 環境: kuri04 / BL32XU開発環境（オフライン確認のみ）
- 記録日時: `2026-10-08T15:11:43+09:00`

## 完了したこと

- 手作業で`/staff/Common/kuntaro/zoodev`へ置いていた`zpython`、
  `zpython-with-config`、`activate-zoo.sh`を`runtime/zpython/`へ収容した。
- profile雛形と、既存profileを保持する配置スクリプトを追加した。
- 別host/ビームラインへの配置、読み取り専用smoke test、記録項目を
  `docs/operations/zpython-runtime.md`へ記録した。
- live `beamline.ini`、`current` symlink、装置設定を配置スクリプトの対象外にした。

## 途中のこと

- 対象ビームラインの実際のPython、kunpy、ZOO配置を確認し、現地専用profileを作る作業。
- 現地での読み取り専用import/config smoke testと、その結果の追記。
- 実機試験は読み取り専用確認の後、operatorと範囲を合意して別途実施する。

## 確認済み

- `bash -n`でGit管理する3つのshell scriptの構文を確認。
- kuri04の固定runtimeで`runtime/zpython/test/test_runtime_bundle.py`を実行し、4件成功。
  配置先移動後のprofile解決、明示config、config欠損拒否、既存launcher/profile保護を確認。
- `/tmp/zoo005-runtime-test`へ隔離配置し、ZOO `UserESA`とkunpy detector registryを
  同一processからimportできた。
- BL32XU隔離設定
  `/staff/Common/kuntaro/zoodev/configs/bl32xu-261008/beamline.ini`から
  `BL32XU`と`EIGER_X_9M`を読み取れた。
- profile未指定と`beamline.ini`欠損は、Python開始前にexit status 2で停止した。
- Git版3ファイルとkuri04配備版の`git diff --no-index`は差分なし。
- 装置接続、測定、DB/API更新は実施していない。

## まだ確認していないこと

- BL32XU実機host上の配置path、利用runtime、profile、live config identity。
- BL32XU実機hostでの読み取り専用smoke test。
- BL41XU、BL45XU、NanoTerasuでの配置と試験。
- 装置を使う動作確認。kuri04の結果を実機合格とは扱わない。

## 次に最初にやること

1. zoo-hubの`ZOO-005`と本handoffを読む。
2. 対象ビームラインの運転状態を確認し、運転用cloneを変更しない。
3. 現地のZOO/kunpy/runtime/config pathを読み取り確認して記録する。
4. 試験用の別配置先へ`configure-local-runtime.py`で展開し、現地profileを作る。
5. `docs/operations/zpython-runtime.md`の読み取り専用smoke testだけを実施する。

## 再開時に繰り返してはいけない操作・注意事項

- live `beamline.ini`をGit pull、配置スクリプト、profile作成に伴って上書きしない。
- kuri04のprofile pathを別ビームラインへそのままコピーしない。
- 運転中のcloneでcheckout、pull、merge、launcher切替を行わない。
- import/config smoke testを装置接続・測定試験へ無断で拡大しない。
- `/tmp/zoo005-runtime-test`は一時試験物であり、正本や現地runtimeとして使わない。

- 最後の操作と成否: kuri04隔離環境の読み取り専用smoke test成功。
- 中断時の観測: 装置・試料・測定・DBを操作していない。
- 再開時の確認: 現地の運転状態、各commit/path、config identityを改めて確認する。
- 使用設定・ログ: 上記BL32XU 2026-10-08隔離設定。console出力のみ。
- 復旧・切戻し上の注意: 現在のkuri04配備版はGit版と同一。現地では変更前launcherと
  `current` symlinkを記録してから切替する。
