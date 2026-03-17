import re
from datetime import datetime

def parse_zoo_time(s: str) -> dict:
    """
    ZOO DB の t_meas_start 文字列を解析して
    {parameter_name: iso_time} の dict を返す。

    例
    input:
        "0,{meas_start_00:20260203171018},{mount_end_00:20260203171129}"

    output:
        {
            "t_meas_start": "2026-02-03T17:10:18",
            "t_mount_end": "2026-02-03T17:11:29"
        }
    """

    result = {}

    if not s:
        return result

    # {key_index:timestamp}
    pattern = r"\{([a-zA-Z_]+)_\d+:(\d{14})\}"

    for name, ts in re.findall(pattern, s):

        dt = datetime.strptime(ts, "%Y%m%d%H%M%S")
        iso = dt.strftime("%Y-%m-%dT%H:%M:%S")

        result[f"t_{name}"] = iso

    return result

def test_zoodb_time_parser_smoke():
    s = "{mount_end_00:20260203171129}"

    d = parse_zoo_time(s)

    assert "t_mount_end" in d
    assert d["t_mount_end"].startswith("2026-02-03T17:11")