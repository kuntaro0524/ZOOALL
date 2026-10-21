"""PEの測定が途中で止まったとき、前回のDB（zoo_*.db）から続きを決める（ZOO45XU-006）。

DBはCSVごとに root_dir/zoo_<日時>.db として作られる。ファイル名からCSVは分からないので、
同じ root_dir にある zoo_*.db のうち、puckid の集合がCSVと一致する最新のものを前回のDBとみなす。
装置には触れない。DBの読み書きだけを行う。
"""
import glob
import os
import sqlite3

import pandas as pd

from ErrorCode import ErrorCode


def root_dir_from_csv(csv_path):
    """ZooNavigator.prepESA と同じ: 2行目の先頭列。"""
    with open(csv_path, "r") as f:
        lines = f.readlines()
    return lines[1].replace("\"", "").split(",")[0]


def csv_pucks(csv_path):
    df = pd.read_csv(csv_path)
    if "puckid" not in df.columns:
        raise RuntimeError("CSV file must contain 'puckid' column.")
    return [str(p) for p in dict.fromkeys(df["puckid"]) if str(p) not in ("nan", "")]


def read_status(db_path):
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute("select puckid, pinid, isSkip, isDone, isDS from ESA order by p_index")
        return [{"puckid": str(r[0]), "pinid": r[1], "isSkip": r[2], "isDone": r[3], "isDS": r[4]}
                for r in cur.fetchall()]
    finally:
        con.close()


def _is_remaining(row):
    # ESA.getPriorPinCond と同じ条件
    return row["isSkip"] != 1 and row["isDone"] < 1 and row["isDS"] == 0


def find_resume_db(csv_path):
    pucks = set(csv_pucks(csv_path))
    candidates = glob.glob(os.path.join(root_dir_from_csv(csv_path), "zoo_*.db"))
    for db in sorted(candidates, key=os.path.getmtime, reverse=True):
        try:
            status = read_status(db)
        except sqlite3.Error:
            continue
        if status and {r["puckid"] for r in status} == pucks:
            return db
    return None


def reset_hardware_errors(db_path):
    """装置由来のエラーコードで止まったpinを isDone=0 に戻す。戻した数を返す。"""
    codes = ErrorCode.hardware_codes()
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute("update ESA set isDone = 0 where isDone in (%s)" % ",".join("?" * len(codes)), codes)
        con.commit()
        return cur.rowcount
    finally:
        con.close()


def plan_resume(csv_path):
    """前回のDBがあれば再開の計画を返す。無ければ None（最初から測る）。
    finished: 全pinが済んでいる／planned: 未完了pinのpuck（CSVの順）／reset: 測り直しに戻した数。"""
    db = find_resume_db(csv_path)
    if db is None:
        return None
    reset = reset_hardware_errors(db)
    status = read_status(db)
    remaining = [r for r in status if _is_remaining(r)]
    planned = list(dict.fromkeys(r["puckid"] for r in remaining))
    done = sum(1 for r in status if r["isSkip"] == 1 or r["isDone"] >= 1)
    return {"db": db, "finished": len(remaining) == 0, "planned": planned,
            "reset": reset, "done": done, "total": len(status)}


def describe(csv_path, plan):
    if plan is None:
        return "%s: 前回のDBなし。最初から測る。" % csv_path
    state = "全pin済み。飛ばす" if plan["finished"] else "続きから（puck: %s）" % ", ".join(plan["planned"])
    return "%s: 前回のDB %s、%d/%d pin済み、測り直しに戻した %d pin。%s" % (
        csv_path, plan["db"], plan["done"], plan["total"], plan["reset"], state)
