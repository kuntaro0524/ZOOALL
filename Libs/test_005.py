from UserESA import UserESA

u = UserESA(fname="dummy.xlsx", root_dir=".")

cond = {
    "mode": "helical",
    "dose_list": "[1,2]",
    "dist_list": "[110,120]",
}

try:
    u.validateDoseDist(cond)
    print("OK")
except ValueError as e:
    print("NG",e)
