import config_loaders.ESAloaderAPI as ESAloaderAPI

# もしもmainが定義されていない場合以下を実行
if __name__ == '__main__':
    # class をインスタンス化
    zoo_id = 5
    esa_loader = ESAloaderAPI.ESAloaderAPI(zoo_id)
    # esa_loader.updateCond(21525, "isDone", "12")

    json_list = []
    # 21525 - 21529 の isDone を 12 に変更
    for i in range(21525, 21530):
        # json形式
        json_tmp = {"measure_id": i, "parameter_name": "isDone", "value": "12"}
        json_list.append(json_tmp)

    # json_list を引数にして updateConds を実行
    esa_loader.updateConds(json_list)

    # 確認作業
    # measurement_id = 21520 の isDoneの確認
    print("###################################")
    conds_df = esa_loader.getCondDataFrame()
    # isDoneの確認
    # conds_df 'measure_id' と 'isDone' のみを表示
    print(conds_df[['measure_id', 'isDone']])