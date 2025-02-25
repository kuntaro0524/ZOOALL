import sys
from ECHA import ESAloaderAPI as ESAloaderAPI

echa_esa = ESAloaderAPI.ESAloaderAPI(13)

# get result
ppp=echa_esa.getResult(int(sys.argv[1]))
print(ppp)
