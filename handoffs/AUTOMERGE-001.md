# AUTOMERGE-001: ZOO測定完了JSON生成ToDo

## 状態

`TODO / NOT IMPLEMENTED`

横断作業の正本はzoo-hubの
`docs/work-items/AUTOMERGE-001.md`である。本記録はZOOALL側の実装入口だけを示す。

## 目的

ZOOが実験全体の測定とWebDBへの結果登録を完了した後、実験root directoryへ
`zoo_measurement_complete.json`をatomicに配置する。

マーカーは後続のNikuDango自動マージを開始してよいという通知であり、測定事実の正本ではない。
測定事実の正本はWebDBとする。

## 最小schema候補

```json
{
  "schema_version": 1,
  "exid": "example-exid",
  "completed_at": "2026-10-06T18:30:00+09:00",
  "status": "completed"
}
```

## ToDo

- 実験全体の正常完了を確定するZOO内の位置を特定する。
- WebDBへの最終結果登録とfile closeより後に生成する。
- 同一directory内の一時fileへ書き、renameでatomicに確定する。
- schema、正式file名、配置場所をkunpy側consumerと合わせて確定する。
- 再測定、再実行、中断、取消、異常終了時の規則を定義する。
- offline testで正常生成、途中file非検出、既存markerとの衝突を確認する。
- 実機へ適用する前にbeamline別検証とrollback手順を準備する。

## 現時点で実施していないこと

- ZOO production codeの変更
- WebDB/APIの変更
- 実機・測定操作
- marker生成testの実行

## 次の一手

zoo-hubのAUTOMERGE-001でQAとdata contractを確定した後、ZOOの正常終了経路を
read-onlyで特定し、最小実装とoffline testの作業branchを本branchまたは後継branchから開始する。
