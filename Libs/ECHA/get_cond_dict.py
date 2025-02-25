import ECHA.ESAloaderAPI as ESAloaderAPI
import sys

if __name__ == '__main__':
    zoo_id = int(sys.argv[1])
    esa = ESAloaderAPI.ESAloaderAPI(zoo_id)

    next_dict = esa.getNextPin()
    print(next_dict)

    # set Done
    p_index = next_dict['p_index']
    zoo_samplepin_id = next_dict['zoo_samplepin_id']

    # get condition
    print(esa.getCond(zoo_samplepin_id))