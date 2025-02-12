import ECHA.ESAloaderAPI as ESAloaderAPI

if __name__ == '__main__':
    zoo_id = 12
    esa = ESAloaderAPI.ESAloaderAPI(zoo_id)

    next_dict = esa.getNextPin()

    # next_dict がNoneの場合には測定を終了する
    if next_dict is None:
        print("No more pins")
        sys.exit(0)

    # set Done
    p_index = next_dict['p_index']
    zoo_samplepin_id = next_dict['zoo_samplepin_id']

    print(f"p_index={p_index} zoo_samplepin_id={zoo_samplepin_id}")
    esa.setDone(p_index, zoo_samplepin_id, 1)

    # get next pin
    next_df = esa.getNextPin()
    print(next_df['zoo_samplepin_id'])