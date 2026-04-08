import pandas as pd
from UserESA import UserESA

u = UserESA(fname="dummy.xlsx", root_dir=".")
u.df = pd.DataFrame([
    {
        "mode": "single",
        "dose_ds": 9.0,
        "dist_ds": 150.0,
        "dose_list": "[1,2]",
        "dist_list": "[110,120]",
    }
])

u.checkDoseList()

print("dose_list =", u.df.loc[0, "dose_list"])
print("dist_list =", u.df.loc[0, "dist_list"])
print("dose_ds   =", u.df.loc[0, "dose_ds"])
print("dist_ds   =", u.df.loc[0, "dist_ds"])