import csv
import re
import sys

# 制限時間の空欄は「制限なし」。ZooNavigator の既定値（9999 hours）に合わせる。
NO_LIMIT_HOURS = 9999.0
HOURS_PER_SHIFT = 8.0

_TIME_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*(h|m|min|s)$", re.IGNORECASE)


class PuckConfigError(ValueError):
    pass


def parse_time_limit(text):
    """'12h' -> 12.0, '90m'/'90min' -> 1.5, '2s' (2 shifts) -> 16.0 [hours].
    空欄は None（制限なし）。単位の無い値などは PuckConfigError。"""
    text = "" if text is None else str(text).strip()
    if text == "":
        return None
    m = _TIME_RE.match(text)
    if m is None:
        raise PuckConfigError(
            "制限時間 '%s' を読めません。12h（時間）、90m または 90min（分）、2s（シフト数、1シフト=8時間）の形で書いてください。" % text)
    value = float(m.group(1))
    unit = m.group(2).lower()
    if value <= 0:
        raise PuckConfigError("制限時間 '%s' は0より大きくしてください。" % text)
    if unit == "h":
        return value
    if unit == "s":
        return value * HOURS_PER_SHIFT
    return value / 60.0


def summarize(rows):
    lines = ["測定計画: %d組" % len(rows)]
    for i, r in enumerate(rows, 1):
        if r["time_limit_hour"] == NO_LIMIT_HOURS:
            lim = "制限なし"
        else:
            lim = "%s（%.2f時間）" % (r["time_limit"], r["time_limit_hour"])
        lines.append("  %d. %s  %s" % (i, r["meas_file"], lim))
    return "\n".join(lines)


class PuckConfig():
    def __init__(self, configfile):
        self.configfile = configfile
        self.isRead = False

    def readConfig(self):
        """列 meas_file, time_limit のCSVを読み、1行1組のdictのlistを返す。
        time_limit_hour は時間。空欄は NO_LIMIT_HOURS。"""
        with open(self.configfile, newline="") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames or []
            for need in ("meas_file", "time_limit"):
                if need not in cols:
                    raise PuckConfigError("%s に列 '%s' がありません（見つかった列: %s）" % (self.configfile, need, cols))
            rows = []
            for rec in reader:
                line = reader.line_num
                meas = (rec.get("meas_file") or "").strip()
                if meas == "":
                    raise PuckConfigError("%s の%d行目: meas_file が空です。" % (self.configfile, line))
                raw = (rec.get("time_limit") or "").strip()
                try:
                    hours = parse_time_limit(raw)
                except PuckConfigError as e:
                    raise PuckConfigError("%s の%d行目: %s" % (self.configfile, line, e))
                rows.append({"meas_file": meas, "time_limit": raw,
                             "time_limit_hour": NO_LIMIT_HOURS if hours is None else hours})
        if not rows:
            raise PuckConfigError("%s に測定の行がありません。" % self.configfile)
        self.puck_dict = rows
        self.isRead = True
        return rows


def _check_ext(path):
    if not (path.endswith(".csv") or path.endswith(".db")):
        raise PuckConfigError("'%s' は .csv でも .db でもありません。" % path)


def jobs_from_args(files, plan):
    """入口の引数から [(測定ファイル, 制限時間[hours] または None)] を作る。
    files と plan は同時に指定できない。"""
    if plan and files:
        raise PuckConfigError("測定ファイルと --plan は同時に指定できません。")
    if plan:
        rows = PuckConfig(plan).readConfig()
        jobs = [(r["meas_file"], r["time_limit_hour"] if r["time_limit_hour"] != NO_LIMIT_HOURS else None) for r in rows]
    elif files:
        jobs = [(f, None) for f in files]
    else:
        raise PuckConfigError("測定ファイル、または --plan を指定してください。")
    for path, _ in jobs:
        _check_ext(path)
    return jobs


if __name__ == "__main__":
    rows = PuckConfig(sys.argv[1]).readConfig()
    print(summarize(rows))
