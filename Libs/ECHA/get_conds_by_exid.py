import ECHA.ESAloaderAPI as ESAloaderAPI
import sys

import ECHA.ESAloaderAPI as ESAloaderAPI
import inspect

print("ESAloaderAPI module file:", ESAloaderAPI.__file__)
print("ESAloaderAPI class init signature:", inspect.signature(ESAloaderAPI.ESAloaderAPI.__init__))


if __name__ == '__main__':
    zoo_exid = sys.argv[1]
    esa = ESAloaderAPI.ESAloaderAPI(exid=zoo_exid, auto_resolve=False)

    esa.require_zoo_id()
    conds = esa.getCondDataFrame()

    print("########################33")
    print(conds)
    print("########################33")

    """
    dict_next = esa.getNextPin()
    print(dict_next)
    p_index = dict_next['p_index']
    pin_id = dict_next['zoo_samplepin_id']
    isDone = True
    cond = esa.getCond(pin_id)
    print(cond)
    isDone = 1
    esa.setDone(p_index, pin_id, isDone)
    dict_next = esa.getNextPin()
    print(dict_next)

    isDone = True
    while(isDone):
        try:
            dict_next = esa.getNextPin()
            print(dict_next)
            cond = dict_next.get('condition')
            print(cond)
            esa.setDone()
            isDone = False
            
        except Exception as e:
            print(f"Error getting next pin: {e}")

    """