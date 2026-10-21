# -*- coding: utf-8 -*-
"""ZOO45XU-005: 時間制限つき測定の指定（PuckConfig）の仕様試験。装置には触れない。"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Libs"))
import PuckConfig as pc


@pytest.mark.parametrize("text, hours", [
    ("12h", 12.0),
    ("12H", 12.0),
    ("1.5h", 1.5),
    ("90m", 1.5),
    ("90min", 1.5),
    ("90 min", 1.5),
    ("2s", 16.0),
    ("0.5s", 4.0),
    (" 30m ", 0.5),
])
def test_parse_time_limit(text, hours):
    assert pc.parse_time_limit(text) == pytest.approx(hours)


@pytest.mark.parametrize("text", ["5", "abc", "h", "-3h", "0h", "12hours", "1h30m", "nan"])
def test_parse_time_limit_rejects(text):
    with pytest.raises(pc.PuckConfigError):
        pc.parse_time_limit(text)


@pytest.mark.parametrize("text", ["", "   "])
def test_blank_is_no_limit(text):
    assert pc.parse_time_limit(text) is None


def write(tmp_path, body):
    f = tmp_path / "plan.csv"
    f.write_text(body)
    return str(f)


def test_read_five_or_more_rows(tmp_path):
    body = "meas_file,time_limit\n" + "".join("/d/%d_zoo.csv,%dh\n" % (i, i + 1) for i in range(6))
    rows = pc.PuckConfig(write(tmp_path, body)).readConfig()
    assert len(rows) == 6
    assert rows[5]["meas_file"] == "/d/5_zoo.csv"
    assert rows[5]["time_limit_hour"] == pytest.approx(6.0)


def test_blank_limit_uses_default_hours(tmp_path):
    rows = pc.PuckConfig(write(tmp_path, "meas_file,time_limit\na.csv,\n")).readConfig()
    assert rows[0]["time_limit_hour"] == pc.NO_LIMIT_HOURS


def test_error_has_line_number(tmp_path):
    body = "meas_file,time_limit\na.csv,12h\nb.csv,5\n"
    with pytest.raises(pc.PuckConfigError) as e:
        pc.PuckConfig(write(tmp_path, body)).readConfig()
    assert "3行目" in str(e.value)


def test_missing_column(tmp_path):
    with pytest.raises(pc.PuckConfigError) as e:
        pc.PuckConfig(write(tmp_path, "file,time\na.csv,1h\n")).readConfig()
    assert "meas_file" in str(e.value)


def test_missing_file_name(tmp_path):
    with pytest.raises(pc.PuckConfigError) as e:
        pc.PuckConfig(write(tmp_path, "meas_file,time_limit\n,1h\n")).readConfig()
    assert "2行目" in str(e.value)


def test_empty_plan(tmp_path):
    with pytest.raises(pc.PuckConfigError):
        pc.PuckConfig(write(tmp_path, "meas_file,time_limit\n")).readConfig()


def test_summary_lists_all(tmp_path):
    rows = pc.PuckConfig(write(tmp_path, "meas_file,time_limit\na.csv,12h\nb.csv,\n")).readConfig()
    s = pc.summarize(rows)
    assert "2組" in s and "a.csv" in s and "制限なし" in s


# ---- 入口の引数（lets_goto_zoo.py が使う）----
def test_jobs_plain_files_have_no_limit():
    jobs = pc.jobs_from_args(["a.csv", "b.db"], None)
    assert jobs == [("a.csv", None), ("b.db", None)]


def test_jobs_plan_file(tmp_path):
    plan = write(tmp_path, "meas_file,time_limit\na.csv,90m\nb.csv,2s\n")
    jobs = pc.jobs_from_args([], plan)
    assert jobs == [("a.csv", pytest.approx(1.5)), ("b.csv", pytest.approx(16.0))]


def test_jobs_plan_and_files_conflict(tmp_path):
    plan = write(tmp_path, "meas_file,time_limit\na.csv,1h\n")
    with pytest.raises(pc.PuckConfigError):
        pc.jobs_from_args(["x.csv"], plan)


def test_jobs_need_something():
    with pytest.raises(pc.PuckConfigError):
        pc.jobs_from_args([], None)


def test_jobs_unknown_extension():
    with pytest.raises(pc.PuckConfigError):
        pc.jobs_from_args(["a.txt"], None)
