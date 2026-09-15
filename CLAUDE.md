# Claude Code entry point

このrepositoryだけを読んで作業を開始しないでください。最初にcross-repository architecture
の正本であるzoo-hub（`git@github.com:kuntaro0524/zoo-hub.git`）を見つけ、次を読みます。

1. `zoo-hub/START_HERE.md`
2. `zoo-hub/HOW_TO_WORK.md`
3. `zoo-hub/docs/work-items/registry.md`
4. 対応するwork-item file

zoo-hubは、隣接clone、site/environment固有の既知の場所、または上記remote identityから
探します。見つからない場合はユーザーに場所を確認し、ZOOの古い文書だけで新規workを開始
しません。

既存作業は、registry → work-item → ZOOのbranch → 実際のGit HEAD/status → `Exact next action`
の順で復元します。新規作業は重複確認後にwork-itemを登録してから開始します。

ZOO固有の詳細は`START_HERE.md`、`AGENTS.md`、`docs/development/WORKFLOW.md`、handoverを
読みます。重要なdecision、中断、完了判定はzoo-hubのwork-item systemに記録し、unrelatedな
変更・未追跡ファイル・実機状態を無断で変更、削除、commitしません。
