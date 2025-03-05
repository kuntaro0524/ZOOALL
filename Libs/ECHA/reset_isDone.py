import ECHA.ESAloaderAPI as ESAloaderAPI


if __name__ == '__main__':
    zoo_id = 12
    esa = ESAloaderAPI.ESAloaderAPI(zoo_id)
    #conds_df = esa.getCondDataFrame()
    #print(conds_df)

    """
    for i in range(len(conds_df)):
        # zoo_samplepin_id 
        zoo_samplepin_id = conds_df.iloc[i]['zoo_samplepin_id']
        p_index = conds_df.iloc[i]['p_index']
        print("####################3")
        print(f"p_index={p_index} zoo_samplepin_id={zoo_samplepin_id}")
        print("####################3")
        # isDone をすべて０にする
        esa.setDone(p_index, zoo_samplepin_id, 0)
        # isSkip をすべて０にする
        esa.setSkip(p_index, zoo_samplepin_id, 0)
    """
    esa.setDone(3, 210, 0)