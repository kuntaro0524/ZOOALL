import sys
import pandas as pd
import KUMA


def calc_useresa_style_dose_per_frame(ds_hbeam, ds_vbeam, flux, wavelength, exp_raster):
    """
    UserESA.defineScanCondition() の normal 系に合わせた計算
    photons_per_image = 4E10
    att_raster = 4E10 / (flux * exp_raster) * 100
    dose_per_frame = KUMA.getDose(...) * att_raster / 100
    """
    kuma = KUMA.KUMA()

    base_dose = kuma.getDose(
        ds_hbeam,
        ds_vbeam,
        flux,
        wavelength,
        exp_raster
    )

    photons_per_image = 4.0e10
    att_raster = photons_per_image / (flux * exp_raster) * 100.0
    dose_per_frame = base_dose * att_raster / 100.0

    return base_dose, att_raster, dose_per_frame


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_kuma_beam_monotonic.py processed_df.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    df = pd.read_csv(csv_path)
    row = df.iloc[0]

    flux = float(row["flux"])
    wavelength = float(row["wavelength"])
    exp_raster = float(row["exp_raster"])

    print("=== reference row from processed_df.csv ===")
    print(f"flux       = {flux}")
    print(f"wavelength = {wavelength}")
    print(f"exp_raster = {exp_raster}")
    print(f"orig beam  = {row['ds_hbeam']} x {row['ds_vbeam']} um")
    if "dose_per_frame" in row.index:
        print(f"orig dose_per_frame(df) = {row['dose_per_frame']}")
    if "dose_ds" in row.index:
        print(f"orig dose_ds(df)        = {row['dose_ds']}")
    print()

    # beam size を系統的に変える
    beam_list = [
        (5.0, 5.0),
        (10.0, 10.0),
        (10.0, 15.0),
        (15.0, 15.0),
        (20.0, 20.0),
        (30.0, 30.0),
    ]

    results = []
    for hbeam, vbeam in beam_list:
        base_dose, att_raster, dose_per_frame = calc_useresa_style_dose_per_frame(
            hbeam, vbeam, flux, wavelength, exp_raster
        )
        dose_ds = 10.0 - dose_per_frame

        results.append({
            "ds_hbeam": hbeam,
            "ds_vbeam": vbeam,
            "base_dose_MGy": base_dose,
            "att_raster_percent": att_raster,
            "dose_per_frame_MGy": dose_per_frame,
            "dose_ds_MGy": dose_ds,
        })

    out_df = pd.DataFrame(results)

    print("=== beam size scan ===")
    print(out_df.to_string(index=False))

    print()
    print("=== monotonic check by area ===")
    out_df["area"] = out_df["ds_hbeam"] * out_df["ds_vbeam"]
    out_df = out_df.sort_values("area").reset_index(drop=True)

    print(out_df[["ds_hbeam", "ds_vbeam", "area", "dose_per_frame_MGy", "dose_ds_MGy"]].to_string(index=False))

    # 単調性の簡易チェック
    dose_list = out_df["dose_per_frame_MGy"].tolist()
    is_nonincreasing = all(dose_list[i] >= dose_list[i + 1] for i in range(len(dose_list) - 1))

    print()
    if is_nonincreasing:
        print("OK: beam area が大きくなるにつれて dose_per_frame は単調非増加です。")
    else:
        print("WARNING: beam area と dose_per_frame の単調関係が崩れています。")


if __name__ == "__main__":
    main()
