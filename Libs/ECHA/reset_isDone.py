import ECHA.ESAloaderAPI as ESAloaderAPI
import sys

if __name__ == '__main__':
    exid = sys.argv[1]
    esa = ESAloaderAPI.ESAloaderAPI(exid)

    # EXIDのzoo_samplepinの情報を取得
    conds_df = esa.getSamplePinInfo()
    print(conds_df.columns)
    # conds_df['p_index'] で 全p_indexのisSkipをリセットする
    for p_index in conds_df['p_index'].unique():
        pin_info = conds_df[conds_df['p_index'] == p_index].iloc[0]
        pin_id = pin_info['id']
        print(pin_info['isSkip'], pin_info['isDone'])
        p_index = pin_info['p_index']
        if pin_info['isSkip'] == 1:
            print(f"Unsetting isSkip for pin_id={pin_id}")
        if pin_info['isDone'] == 1:
            esa.setDone(p_index, zoo_samplepin_id=pin_id, isDone=0)