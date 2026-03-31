import sys
import types


def _install_stub_modules():
    stub_names = [
        "LoopMeasurement",
        "AttFactor",
        "StopWatch",
        "AnaHeatmap",
        "CrystalList",
    ]
    for name in stub_names:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    if "ZooMyException" not in sys.modules:
        exc_mod = types.ModuleType("ZooMyException")

        class ZooMyException(Exception):
            pass

        exc_mod.ZooMyException = ZooMyException
        sys.modules["ZooMyException"] = exc_mod


_install_stub_modules()

from HEBI import HEBI


class DummyHEBI(HEBI):
    def __init__(self):
        self.logger = types.SimpleNamespace(
            info=lambda *a, **k: None,
            debug=lambda *a, **k: None,
            warning=lambda *a, **k: None,
            error=lambda *a, **k: None,
            write=lambda *a, **k: None,
        )
        self.phosec_meas = 1.0e12
        self.min_score = 15
        self.max_score = 200
        self.naname_include = True
        self.vscan_length = 1000.0
        self.limit_of_vert_velocity = 400.0
        self.gaburiyoru_ntimes = 5
        self.gaburiyoru_h_length = 10
        self.min_score_smallbeam = 6
        self.debug = False
        self.debug_LR = False


def make_cond(
    dose_ds=10.0,
    dist_ds=120.0,
    dose_list="",
    dist_list="",
    ds_hbeam=10.0,
    ds_vbeam=10.0,
    total_osc=10.0,
):
    return {
        "dose_ds": dose_ds,
        "dist_ds": dist_ds,
        "dose_list": dose_list,
        "dist_list": dist_list,
        "ds_hbeam": ds_hbeam,
        "ds_vbeam": ds_vbeam,
        "total_osc": total_osc,
    }


def print_table(title, rows):
    print()
    print("=" * 90)
    print(title)
    print("=" * 90)
    header = f"{'idx':>3} | {'branch':<8} | {'prefix':<12} | {'dose_ds':>8} | {'dist_ds':>8}"
    print(header)
    print("-" * len(header))
    for i, row in enumerate(rows):
        print(
            f"{i:>3} | "
            f"{row['branch']:<8} | "
            f"{row['prefix']:<12} | "
            f"{row['dose_ds']:>8.3f} | "
            f"{row['dist_ds']:>8.3f}"
        )
    print("=" * 90)


def main():
    hebi = DummyHEBI()
    records = []

    class DummyZoo:
        def doDataCollection(self, schedule):
            records.append(schedule)

        def waitTillReady(self):
            pass

        def doRaster(self, *args, **kwargs):
            pass

    class DummyLM:
        def genSingleSchedule(
            self, start_phi, end_phi, center_xyz, cond, phosec, prefix, same_point=True
        ):
            return {
                "branch": "single",
                "prefix": prefix,
                "dose_ds": float(cond["dose_ds"]),
                "dist_ds": float(cond["dist_ds"]),
            }

        def genHelical(
            self, start_phi, end_phi, left_xyz, right_xyz, prefix, phosec, cond
        ):
            return {
                "branch": "helical",
                "prefix": prefix,
                "dose_ds": float(cond["dose_ds"]),
                "dist_ds": float(cond["dist_ds"]),
            }

    hebi.zoo = DummyZoo()
    hebi.lm = DummyLM()

    left_xyz = (0.0, 0.0, 0.0)
    right_xyz_small = (0.0, 0.005, 0.0)   # 5 um -> small crystal
    right_xyz_large = (0.0, 0.050, 0.0)   # 50 um -> helical

    # Case 1
    records.clear()
    cond = make_cond(
        dose_ds=8.0,
        dist_ds=125.0,
        dose_list="",
        dist_list="",
        ds_hbeam=10.0,
    )
    hebi.doHelical(left_xyz, right_xyz_small, cond, phi_face=0.0, prefix="test")
    print_table("CASE 1: small crystal / normal single-condition", records)

    # Case 2
    records.clear()
    cond = make_cond(
        dose_ds=999.0,
        dist_ds=125.0,
        dose_list="[1, 5, 10]",
        dist_list="",
        ds_hbeam=10.0,
    )
    hebi.doHelical(left_xyz, right_xyz_small, cond, phi_face=0.0, prefix="test")
    print_table("CASE 2: small crystal / dose_list only", records)

    # Case 3
    records.clear()
    cond = make_cond(
        dose_ds=999.0,
        dist_ds=999.0,
        dose_list="[1, 5, 10]",
        dist_list="[120, 110, 100]",
        ds_hbeam=10.0,
    )
    hebi.doHelical(left_xyz, right_xyz_large, cond, phi_face=0.0, prefix="test")
    print_table("CASE 3: large crystal / dose_list + dist_list", records)


if __name__ == "__main__":
    main()