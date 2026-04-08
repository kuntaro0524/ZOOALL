import numpy as np
import pandas as pd
from UserESA import UserESA

u = UserESA(fname="dummy.xlsx", root_dir=".")
u.df = pd.DataFrame([
    {
        "mode": "single",
        "dose_list": "[1,2]",
        "dist_list": np.nan,
    }
])

try:
    u.checkDoseList()
    print("NG: ValueError が出るべき")
except ValueError as e:
    print("OK:", e)