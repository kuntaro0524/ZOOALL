# -*- coding: utf-8 -*-
"""ZOO45XU-006: PEの測定を途中から再開するための判定の試験。装置にも beamline.ini にも触れない。"""
import os
import sqlite3
import sys
import time

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Libs"))
import ZooResume as zr
from ErrorCode import ErrorCode

NOT_MOUNTED = "Not-Mounted"


def make_csv(tmp_path, name, rows, root=None):
    """ESAのCSVの代わり。2行目の先頭列が root_dir、puckid 列がある。"""
    root = str(root or tmp_path)
    df = pd.DataFrame({"root_dir": [root] * len(rows),
                       "puckid": [r[0] for r in rows],
                       "pinid": [r[1] for r in rows]})
    p = tmp_path / name
    df.to_csv(p, index=False)
    return str(p)


def make_db(path, rows, mtime=None):
    """rows: (puckid, pinid, isSkip, isDone, isDS)"""
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE ESA (p_index int, puckid char, pinid int, isSkip int, isDone int, isDS int)")
    for i, r in enumerate(rows):
        con.execute("INSERT INTO ESA VALUES (?,?,?,?,?,?)", (i,) + tuple(r))
    con.commit()
    con.close()
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return str(path)


def test_hardware_codes_are_space_codes():
    codes = set(ErrorCode.hardware_codes())
    assert codes == {9001, 9002, 9003, 9004, 9997, 9998, 9999}
    assert ErrorCode.CENTERING_FAILURE.value not in codes
    assert ErrorCode.SUCCESS.value not in codes


def test_root_dir_from_csv(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1)], root=tmp_path / "root")
    assert zr.root_dir_from_csv(csv) == str(tmp_path / "root")


def test_no_db_means_fresh(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1), ("P2", 1)])
    assert zr.plan_resume(csv) is None


def test_unfinished_db_gives_remaining_pucks(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1), ("P1", 2), ("P2", 1), ("P3", 1)])
    make_db(tmp_path / "zoo_1.db", [
        ("P1", 1, 0, 1, 1),      # 成功
        ("P1", 2, 0, 1, 1),
        ("P2", 1, 0, 0, 0),      # 途中で落ちた
        ("P3", 1, 0, 0, 0),
    ])
    plan = zr.plan_resume(csv)
    assert plan["finished"] is False
    assert plan["planned"] == ["P2", "P3"]
    assert plan["done"] == 2 and plan["total"] == 4


def test_finished_db_is_skipped(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1), ("P2", 1)])
    make_db(tmp_path / "zoo_1.db", [("P1", 1, 0, 1, 1), ("P2", 1, 0, 2003, 1)])
    plan = zr.plan_resume(csv)
    assert plan["finished"] is True
    assert plan["planned"] == []


def test_skipped_pins_are_not_remaining(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1), ("P2", 1)])
    make_db(tmp_path / "zoo_1.db", [("P1", 1, 1, 0, 0), ("P2", 1, 0, 1, 1)])
    assert zr.plan_resume(csv)["finished"] is True


def test_hardware_errors_are_reset_but_sample_errors_are_not(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1), ("P1", 2), ("P2", 1), ("P3", 1)])
    db = make_db(tmp_path / "zoo_1.db", [
        ("P1", 1, 0, 9999, 0),   # SPACE事故 -> 測り直す
        ("P1", 2, 0, 9004, 0),   # つかみ失敗 -> 測り直す
        ("P2", 1, 0, 1001, 0),   # センタリング失敗 -> 飛ばしたまま
        ("P3", 1, 0, 1, 1),
    ])
    plan = zr.plan_resume(csv)
    assert plan["reset"] == 2
    assert plan["planned"] == ["P1"]
    con = sqlite3.connect(db)
    got = dict(((p, n), d) for p, n, d in con.execute("select puckid,pinid,isDone from ESA"))
    con.close()
    assert got == {("P1", 1): 0, ("P1", 2): 0, ("P2", 1): 1001, ("P3", 1): 1}


def test_db_of_another_csv_is_not_used(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1), ("P2", 1)])
    make_db(tmp_path / "zoo_1.db", [("Q1", 1, 0, 0, 0)])   # 同じ root_dir にある別CSVのDB
    assert zr.plan_resume(csv) is None


def test_newest_matching_db_is_used(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1)])
    now = time.time()
    make_db(tmp_path / "zoo_old.db", [("P1", 1, 0, 1, 1)], mtime=now - 1000)     # 前の完走した回
    make_db(tmp_path / "zoo_new.db", [("P1", 1, 0, 0, 0)], mtime=now)           # 落ちた回
    plan = zr.plan_resume(csv)
    assert plan["db"].endswith("zoo_new.db")
    assert plan["finished"] is False


def test_unreadable_db_is_ignored(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1)])
    (tmp_path / "zoo_bad.db").write_text("not a database")
    assert zr.plan_resume(csv) is None


def test_describe_mentions_counts(tmp_path):
    csv = make_csv(tmp_path, "a.csv", [("P1", 1), ("P2", 1)])
    make_db(tmp_path / "zoo_1.db", [("P1", 1, 0, 1, 1), ("P2", 1, 0, 0, 0)])
    s = zr.describe(csv, zr.plan_resume(csv))
    assert "1/2" in s and "zoo_1.db" in s and "P2" in s
