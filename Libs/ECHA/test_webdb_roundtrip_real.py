import pytest
from ECHA.ESAloaderAPI import ESAloaderAPI

def test_webdb_roundtrip_real():
    exid = "ZOO_target_BL32XU_202603111407_echatest"
    target_id = 339

    api = ESAloaderAPI(exid)
    api.prep()

    res = api.getResult(target_id)
    sp = api.getSamplePin()

    assert len(res) > 0
    assert "isMount" in res["result_name"].values
    assert "t_meas_start" in res["result_name"].values
    assert "t_meas_end" in res["result_name"].values

    row = sp[sp["id"] == target_id]
    assert len(row) == 1
    assert int(row.iloc[0]["isDone"]) == 1
    assert int(row.iloc[0]["isSkip"]) == 0