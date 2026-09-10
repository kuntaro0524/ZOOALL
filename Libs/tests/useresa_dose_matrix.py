import logging
import pandas as pd
import numpy as np
import UserESA as useresa_module
from UserESA import UserESA


# -----------------------------
# Fake KUMA
# -----------------------------
class FakeKUMAEngine:
    def getDose(self, beam_h, beam_v, flux, energy, exp_time):
        """
        仮定:
        - flux density = 1E10 photons/sec/um^2
        - 2E10 photons/um^2 で 10 MGy

        この関数は「100% transmission時の dose」を返す。
        defineScanCondition() 側でさらに att_raster/100 が掛かる。
        """
        area = beam_h * beam_v
        photons_per_um2 = (flux * exp_time) / area
        dose = 10.0 * (photons_per_um2 / 2.0e10)
        return dose

class FakeKUMAModule:
    @staticmethod
    def KUMA():
        return FakeKUMAEngine()


# UserESA.py 内で参照している KUMA を丸ごと差し替え
useresa_module.KUMA = FakeKUMAModule


# -----------------------------
# Dummy ESA
# -----------------------------
class DummyESA(UserESA):
    def __init__(self):
        # UserESA.__init__ は呼ばない
        self.debug = False
        self.isDoseError = False
        self.logger = logging.getLogger("DummyESA")
        self.logger.setLevel(logging.WARNING)
        if not self.logger.handlers:
            self.logger.addHandler(logging.StreamHandler())

def simulate_beam(v_um, h_um, total_dose=10.0):
    area = v_um * h_um  # um^2

    flux_density = 1.0e10  # photons/sec/um^2
    flux = flux_density * area  # photons/sec

    photons_per_frame = 4.0e10
    min_exptime = 0.01

    t_req = photons_per_frame / flux
    exptime = max(t_req, min_exptime)

    transmission = photons_per_frame / (flux * exptime)

    # 2E10 photons/um^2 -> 10 MGy
    dose_per_frame = 20.0 / area  # MGy
    dose_ds = total_dose - dose_per_frame

    return {
        "beam_v": v_um,
        "beam_h": h_um,
        "area": area,
        "flux": flux,
        "t_req": t_req,
        "exptime": exptime,
        "transmission": transmission * 100.0,
        "dose_per_frame": dose_per_frame,
        "dose_ds": dose_ds,
    }

def build_base_row(mode, exp, vbeam, hbeam, dose_list=None, dist_list=None):
    flux_density = 1.0e10  # photons/sec/um^2
    area = float(vbeam) * float(hbeam)
    flux = flux_density * area

    photons_per_frame = 4.0e10
    min_exptime = 0.01

    # 4E10 photons/frame を達成するのに必要な露光時間
    t_req = photons_per_frame / flux

    # 露光時間は 0.01 sec 未満にしない
    exp_raster = max(t_req, min_exptime)

    return {
        "puckid": "PUCK01",
        "pinid": 1,
        "sample_name": "dummy",
        "mode": mode,
        "desired_exp": exp,
        "wavelength": 1.0,
        "exp_raster": exp_raster,
        "ds_vbeam": float(vbeam),
        "ds_hbeam": float(hbeam),
        "flux": flux,
        "dose_list": dose_list if dose_list is not None else "",
        "dist_list": dist_list if dist_list is not None else "",
        "dose_ds": 10.0,
        "att_raster": 100.0,
        "hebi_att": 100.0,
        "score_max": 100,
        "ntimes": 1,
    }

def run_matrix():
    modes = ["single", "helical", "multi", "mixed"]
    exps = [
        "scan_only",
        "normal",
        "phasing",
        "rapid",
        "high_dose_scan",
        "ultra_high_dose_scan",
    ]

    vbeams = [5.0, 10.0, 20.0]
    hbeams = [5.0, 10.0, 20.0]

    rows = []

    # 1. 通常運用
    for mode in modes:
        for exp in exps:
            for vbeam in vbeams:
                for hbeam in hbeams:
                    esa = DummyESA()
                    esa.df = pd.DataFrame([
                        build_base_row(
                            mode=mode,
                            exp=exp,
                            vbeam=vbeam,
                            hbeam=hbeam,
                            dose_list="",
                            dist_list="",
                        )
                    ])

                    esa.defineScanCondition()
                    r = esa.df.iloc[0]

                    rows.append({
                        "case": "normal_input",
                        "mode": mode,
                        "exp": exp,
                        "ds_vbeam": r.get("ds_vbeam"),
                        "ds_hbeam": r.get("ds_hbeam"),
                        "beam_size(vert x hori)": f"{r.get('ds_vbeam'):g} x {r.get('ds_hbeam'):g}",
                        "dose_list": r.get("dose_list"),
                        "dist_list": r.get("dist_list"),
                        "att_raster": r.get("att_raster"),
                        "hebi_att": r.get("hebi_att"),
                        "ppf_raster": r.get("ppf_raster"),
                        "dose_per_frame": r.get("dose_per_frame"),
                        "flux": r.get("flux"),
                        "dose_ds": r.get("dose_ds"),
                        "score_max": r.get("score_max"),
                    })

    # 2. dose_list のみ
    for mode in ["single", "helical"]:
        for exp in exps:
            for vbeam in vbeams:
                for hbeam in hbeams:
                    esa = DummyESA()
                    esa.df = pd.DataFrame([
                        build_base_row(
                            mode=mode,
                            exp=exp,
                            vbeam=vbeam,
                            hbeam=hbeam,
                            dose_list="[5,10]",
                            dist_list="",
                        )
                    ])

                    esa.defineScanCondition()
                    r = esa.df.iloc[0]

                    rows.append({
                        "case": "dose_list_only",
                        "mode": mode,
                        "exp": exp,
                        "ds_vbeam": r.get("ds_vbeam"),
                        "ds_hbeam": r.get("ds_hbeam"),
                        "beam_size(vert x hori)": f"{r.get('ds_vbeam'):g} x {r.get('ds_hbeam'):g}",
                        "dose_list": r.get("dose_list"),
                        "dist_list": r.get("dist_list"),
                        "att_raster": r.get("att_raster"),
                        "hebi_att": r.get("hebi_att"),
                        "ppf_raster": r.get("ppf_raster"),
                        "dose_per_frame": r.get("dose_per_frame"),
                        "flux": r.get("flux"),
                        "dose_ds": r.get("dose_ds"),
                        "score_max": r.get("score_max"),
                    })

    # 3. dose_list + dist_list
    for mode in ["single", "helical"]:
        for exp in exps:
            for vbeam in vbeams:
                for hbeam in hbeams:
                    esa = DummyESA()
                    esa.df = pd.DataFrame([
                        build_base_row(
                            mode=mode,
                            exp=exp,
                            vbeam=vbeam,
                            hbeam=hbeam,
                            dose_list="[5,10]",
                            dist_list="[120,110]",
                        )
                    ])

                    esa.defineScanCondition()
                    r = esa.df.iloc[0]

                    rows.append({
                        "case": "dose_list_and_dist_list",
                        "mode": mode,
                        "exp": exp,
                        "ds_vbeam": r.get("ds_vbeam"),
                        "ds_hbeam": r.get("ds_hbeam"),
                        "beam_size(vert x hori)": f"{r.get('ds_vbeam'):g} x {r.get('ds_hbeam'):g}",
                        "dose_list": r.get("dose_list"),
                        "dist_list": r.get("dist_list"),
                        "att_raster": r.get("att_raster"),
                        "hebi_att": r.get("hebi_att"),
                        "ppf_raster": r.get("ppf_raster"),
                        "dose_per_frame": r.get("dose_per_frame"),
                        "flux": r.get("flux"),
                        "dose_ds": r.get("dose_ds"),
                        "score_max": r.get("score_max"),
                    })

    df = pd.DataFrame(rows)

    for col in ["att_raster", "hebi_att", "ppf_raster", "dose_per_frame", "dose_ds"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df_print = df.copy()
    df_print["flux"] = df_print["flux"].map(lambda x: f"{x:.3e}")
    df_print["att_raster"] = df_print["att_raster"].round(6)
    df_print["hebi_att"] = df_print["hebi_att"].round(6)
    df_print["ppf_raster"] = df_print["ppf_raster"].round(3)
    df_print["dose_per_frame"] = df_print["dose_per_frame"].round(6)
    df_print["dose_ds"] = df_print["dose_ds"].round(6)

    print("\n=== Full Dose Matrix ===\n")
    print(df_print.to_markdown(index=False))
    df.to_csv("useresa_dose_matrix_full.csv", index=False)

    # 要約1
    summary1 = (
        df.groupby(["case", "mode", "exp"], as_index=False)
        .agg(
            dose_per_frame_min=("dose_per_frame", "min"),
            dose_per_frame_max=("dose_per_frame", "max"),
            dose_ds_min=("dose_ds", "min"),
            dose_ds_max=("dose_ds", "max"),
            att_raster_min=("att_raster", "min"),
            att_raster_max=("att_raster", "max"),
        )
    )

    summary1_print = summary1.copy()
    for col in summary1_print.columns:
        if col.endswith("_min") or col.endswith("_max"):
            summary1_print[col] = pd.to_numeric(summary1_print[col], errors="coerce").round(6)

    print("\n=== Summary: case x mode x exp ===\n")
    print(summary1_print.to_markdown(index=False))
    summary1.to_csv("useresa_dose_matrix_summary_by_mode_exp.csv", index=False)

    # 要約2
    summary2 = (
        df.groupby(["case", "beam_size(vert x hori)", "exp"], as_index=False)
        .agg(
            dose_per_frame_min=("dose_per_frame", "min"),
            dose_per_frame_max=("dose_per_frame", "max"),
            dose_ds_min=("dose_ds", "min"),
            dose_ds_max=("dose_ds", "max"),
        )
    )

    summary2_print = summary2.copy()
    for col in summary2_print.columns:
        if col.endswith("_min") or col.endswith("_max"):
            summary2_print[col] = pd.to_numeric(summary2_print[col], errors="coerce").round(6)

    print("\n=== Summary: case x beam size x exp ===\n")
    print(summary2_print.to_markdown(index=False))
    summary2.to_csv("useresa_dose_matrix_summary_by_beam_exp.csv", index=False)

    # 期待値チェック
    expected_rows = []
    for _, row in df.iterrows():
        if row["case"] in ("dose_list_only", "dose_list_and_dist_list"):
            expected = 0.001
        else:
            if row["exp"] in ("normal", "scan_only", "phasing", "rapid"):
                expected = 0.2
            elif row["exp"] == "high_dose_scan":
                expected = 0.3
            elif row["exp"] == "ultra_high_dose_scan":
                expected = 0.6
            else:
                expected = np.nan

        ok = np.isclose(row["dose_per_frame"], expected, atol=1e-9)

        expected_rows.append({
            "case": row["case"],
            "mode": row["mode"],
            "exp": row["exp"],
            "beam_size(vert x hori)": row["beam_size(vert x hori)"],
            "dose_per_frame": row["dose_per_frame"],
            "expected_dose_per_frame": expected,
            "match": ok,
        })

    check_df = pd.DataFrame(expected_rows)
    print("\n=== Expected-value check ===\n")
    print(check_df.to_markdown(index=False))
    check_df.to_csv("useresa_dose_matrix_expected_check.csv", index=False)

    if check_df["match"].all():
        print("\nALL CHECKS PASSED")
    else:
        print("\nSOME CHECKS FAILED")

    print("\n=== Beam size simulation (flux density fixed) ===")

    beam_list = [
        (5, 5),
        (5, 10),
        (10, 10),
        (10, 20),
        (20, 20),
        (10, 50),
        (30, 30),
        (20, 50),
        (50, 50),
        (100, 100),
    ]

    rows = []
    for v, h in beam_list:
        res = simulate_beam(v, h)
        rows.append(res)

    df_sim = pd.DataFrame(rows)

    # 見やすく丸める
    df_sim["flux"] = df_sim["flux"].map(lambda x: f"{x:.3e}")
    df_sim["t_req"] = df_sim["t_req"].round(5)
    df_sim["exptime"] = df_sim["exptime"].round(5)
    df_sim["transmission"] = df_sim["transmission"].round(2)
    df_sim["dose_per_frame"] = df_sim["dose_per_frame"].round(5)
    df_sim["dose_ds"] = df_sim["dose_ds"].round(5)

    # 表示順を指定
    df_sim = df_sim[
        [
            "beam_v",
            "beam_h",
            "area",
            "flux",
            "t_req",
            "exptime",
            "transmission",
            "dose_per_frame",
            "dose_ds",
        ]
    ]

    print("\n=== Beam size simulation (flux density fixed) ===\n")
    print(df_sim.to_markdown(index=False))

    print(df_sim)

if __name__ == "__main__":
    run_matrix()
