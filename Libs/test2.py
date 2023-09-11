import KUMA,inspect

kuma=KUMA.KUMA()

print(inspect.getmembers(kuma, inspect.ismethod))
