import io
import os
import pandas as pd
import pytest

from UserESA import UserESA
from KUMA import KUMA
from HEBI import HEBI

# --- 1. setup ---

@pytest.fixture
def sample_excel_df():
    """Excel読み込み相当のDataFrameを模倣"""
    data = {
        "puckid": [1, 2, 3],
        "pinid": [1, 1, 1],
        "sample_name": ["testA", "testB", "testC"],
        "mode": ["single", "multi", "single"],
        "resolution_limit": [1.5, 2.0, 1.2],
        "dose_list": ["{1.0, 2.0, 5.0}", "{1.0}", "{10.0, 5.0}"],
        "dist_list": ["{100.0, 120.0, 140.0}", "{150.0}", "{120.0}"],
    }
    return pd.DataFrame(data)

@pytest.fixture
def tmp_useresa(tmp_path, sample_excel_df):
    """UserESAを初期化してExcel→CSV変換を実行"""
    df = sample_excel_df
    csv_path = tmp_path / "UNKO.csv"

    useresa = UserESA(fname=str(tmp_path / "dummy.xlsx"))
    useresa.df = df
    useresa.checkDoseList()  # dose_list/dist_list → dose_ds/dist_ds
    useresa.df.to_csv(csv_path, index=False)
    return csv_path

# --- 2. tests ---

def test_dose_dist_conversion(tmp_useresa):
    """Excelからのdose_list/dist_listがCSVに正しく反映されるか"""
    df = pd.read_csv(tmp_useresa)

    assert "dose_ds" in df.columns
    assert "dist_ds" in df.columns
    assert df.loc[0, "dose_ds"] == "{1, 2, 5}" or "1" in df.loc[0, "dose_ds"]
    assert "{" in df.loc[0, "dist_ds"]

def test_padding_policy(tmp_useresa):
    """長さ不一致時の補間ルール確認"""
    df = pd.read_csv(tmp_useresa)
    dose_vals = [float(x) for x in df.loc[0, "dose_ds"].strip("{}").split(",")]
    dist_vals = [float(x) for x in df.loc[0, "dist_ds"].strip("{}").split(",")]
    assert len(dose_vals) == len(dist_vals)

def test_mode_multi_raises(sample_excel_df):
    """mode='multi'で複数dose→例外"""
    df = sample_excel_df.copy()
    # ← 複数値のある行に multi を当てる（例: index=0 には {1,2,5} が入ってる）
    df.loc[0, "mode"] = "multi"

    useresa = UserESA(fname="dummy.xlsx")
    useresa.df = df

    # ← 例外を投げる処理を実行する必要がある
    with pytest.raises(ValueError):
        useresa.checkDoseList()

def test_kuma_hebi_integration(tmp_useresa):
    """生成したCSVでKUMA/HEBIが正しくDose計算できるか"""
    df = pd.read_csv(tmp_useresa)
    dose_ds = df.loc[0, "dose_ds"]
    dist_ds = df.loc[0, "dist_ds"]

    cond = {
        "ds_hbeam": 10.0,  # [μm] 例：水平ビームサイズ
        "ds_vbeam": 15.0,  # [μm] 例：垂直ビームサイズ
        "dose_ds": dose_ds,
        "dist_ds": dist_ds,
        "mode": "single",
        "wavelength": 1.0,
        "exp_ds": 0.02,
        "total_osc": 180.0,
        "osc_width": 0.1,
        "reduced_fact": 0.2,
        "ntimes": 3,
    }
    flux = 1e11
    dist_vec = 100.0

    kuma = KUMA()
    exp_time, mod_trans = kuma.getBestCondsSingle(cond, flux)
    assert isinstance(exp_time, float)
    assert isinstance(mod_trans, float)

    hebi = HEBI()
    hebi.plan_something(cond)  # 実行できること自体を確認（例外なし）
