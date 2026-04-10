import pandas as pd
import KUMA

df = pd.read_csv("dryrun_useresa_kuma_out/processed_df.csv")
row = df.iloc[0]

kuma = KUMA.KUMA()

base_dose = kuma.getDose(
    row["ds_hbeam"],
    row["ds_vbeam"],
    row["flux"],
    row["wavelength"],
    row["exp_raster"],
)

dose_per_frame = base_dose * row["att_raster"] / 100.0
dose_ds_recalc = 10.0 - dose_per_frame

print("=== inputs ===")
print("ds_hbeam     =", row["ds_hbeam"])
print("ds_vbeam     =", row["ds_vbeam"])
print("flux         =", row["flux"])
print("wavelength   =", row["wavelength"])
print("exp_raster   =", row["exp_raster"])
print("att_raster   =", row["att_raster"])

print("\n=== recalculated ===")
print("base_dose       =", base_dose)
print("dose_per_frame  =", dose_per_frame)
print("dose_ds_recalc  =", dose_ds_recalc)

print("\n=== from processed_df ===")
print("dose_per_frame(df) =", row["dose_per_frame"])
print("dose_ds(df)        =", row["dose_ds"])

print("\n=== differences ===")
print("dose_per_frame diff =", dose_per_frame - row["dose_per_frame"])
print("dose_ds diff        =", dose_ds_recalc - row["dose_ds"])
