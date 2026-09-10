import pandas as pd
from UserESA import UserESA

u = UserESA(fname="dummy.xlsx", root_dir=".")
u.df = pd.DataFrame([
    {"zoomcap_flag": "Yes"},
    {"zoomcap_flag": "No"},
    {"zoomcap_flag": "Unavailable"},
    {"zoomcap_flag": None},
])

u.checkZoomFlag()
print(u.df["zoomcap_flag"].tolist())