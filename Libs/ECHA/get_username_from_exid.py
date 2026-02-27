import ECHA.ESAloaderAPI as ESAloaderAPI
import sys

import ECHA.ESAloaderAPI as ESAloaderAPI
import inspect

print("ESAloaderAPI module file:", ESAloaderAPI.__file__)
print("ESAloaderAPI class init signature:", inspect.signature(ESAloaderAPI.ESAloaderAPI.__init__))


if __name__ == '__main__':
    zoo_exid = sys.argv[1]
    esa = ESAloaderAPI.ESAloaderAPI(exid=zoo_exid)

    #esa.require_zoo_id()
    conds = esa.getCondDataFrame()