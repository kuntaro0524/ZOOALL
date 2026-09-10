#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ESAloaderAPI import ESAloaderAPI

RESULT_KEYS = [
    "isMount",
    "isLoopCenter",
    "isRaster",
    "isDS",
    "scan_height",
    "scan_width",
    "n_mount",
    "nds_multi",
    "nds_helical",
    "nds_helpart",
    "data_index",
    "n_mount_fails",
    "log_mount",
    "hel_cry_size",
    "flux",
    "phs_per_deg",
    "meas_record",
]

import re
from datetime import datetime


EVENT_TO_RESULT_KEY = {
    "meas_start": "t_meas_start",
    "meas_end": "t_meas_end",
    "mount_start": "t_mount_start",
    "mount_end": "t_mount_end",
    "cent_start": "t_cent_start",
    "cent_end": "t_cent_end",
    "raster_start": "t_raster_start",
    "raster_end": "t_raster_end",
    "ds_start": "t_ds_start",
    "ds_end": "t_ds_end",
    "dismount_start": "t_dismount_start",
    "dismount_end": "t_dismount_end",
}


def zoo_time_to_web(timestr):
    dt = datetime.strptime(timestr, "%Y%m%d%H%M%S")
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def parse_event_time_string(event_str: str) -> dict[str, str]:
    """
    旧ESAの t_meas_start に入っているイベント列を解析して、
    WebDB result 用の t_* dict を返す。

    例:
    0,{meas_start_00:20260203171018},{mount_start_00:20260203171018}
    """
    results: dict[str, str] = {}

    if not event_str or event_str == "0":
        return results

    pattern = r"\{([a-zA-Z_]+)_(\d{2}):(\d{14})\}"
    for event_name, _index, timestr in re.findall(pattern, event_str):
        if event_name not in EVENT_TO_RESULT_KEY:
            continue

        try:
            iso_str = zoo_time_to_web(timestr)
            
        except ValueError:
            continue

        result_key = EVENT_TO_RESULT_KEY[event_name]
        results[result_key] = iso_str

    return results

@dataclass
class OldESARecord:
    puckid: str
    pinid: int
    sample_id: str
    sample_name: str
    isDone: Any
    row: dict[str, Any]


class ZooDBReader:
    """
    旧 sqlite3 zoo.db から ESA テーブルを直接読む。
    ESA.py を import せずに動くよう、ここでは汎用 reader を実装する。
    """

    def __init__(self, db_path: Path, logger: logging.Logger) -> None:
        self.db_path = db_path
        self.logger = logger

    @staticmethod
    def make_sample_id(puckid: str, pinid: int) -> str:
        return f"{puckid}-{int(pinid):02d}"

    def read_all(self) -> list[OldESARecord]:
        con = sqlite3.connect(str(self.db_path))
        con.row_factory = sqlite3.Row
        try:
            cur = con.cursor()
            cur.execute("SELECT * FROM ESA")
            rows = cur.fetchall()
        finally:
            con.close()

        out: list[OldESARecord] = []
        for r in rows:
            d = dict(r)
            puckid = str(d.get("puckid", "")).strip()
            pinid_raw = d.get("pinid", 0)
            try:
                pinid = int(pinid_raw)
            except Exception:
                self.logger.warning("Skip row because pinid is invalid: %s", pinid_raw)
                continue

            sample_id = self.make_sample_id(puckid, pinid)
            sample_name = str(d.get("sample_name", ""))
            is_done = d.get("isDone")
            out.append(
                OldESARecord(
                    puckid=puckid,
                    pinid=pinid,
                    sample_id=sample_id,
                    sample_name=sample_name,
                    isDone=is_done,
                    row=d,
                )
            )
        return out


class ResultImporter:
    def __init__(
        self,
        db_path: Path,
        exid: str,
        dry_run: bool,
        limit: Optional[int],
        logger: logging.Logger,
    ) -> None:
        self.db_path = db_path
        self.exid = exid
        self.dry_run = dry_run
        self.limit = limit
        self.logger = logger
        self.reader = ZooDBReader(db_path, logger)
        self.api = ESAloaderAPI(exid)

    def build_samplepin_map(self) -> dict[str, dict[str, Any]]:
        """
        WebDB 既登録の samplepin 一覧を取得し、sample_id で引けるようにする。
        条件側はすでに登録済みという前提。
        """
        self.logger.info("Fetching samplepin/condict map from WebDB for exid=%s", self.exid)
        conds_df = self.api.getCondDataFrame()

        mapping: dict[str, dict[str, Any]] = {}
        for _, row in conds_df.iterrows():
            puckid = str(row.get("puckid", "")).strip()
            pinid = int(row.get("pinid", 0))
            sample_id = f"{puckid}-{pinid:02d}"
            mapping[sample_id] = {
                "zoo_samplepin_id": int(row["id"]) if "id" in row else int(row["zoo_samplepin_id"]),
                "p_index": int(row.get("p_index", pinid)),
                "sample_name": str(row.get("sample_name", "")),
                "mode": str(row.get("mode", "")),
            }
        return mapping

    @staticmethod
    def normalize_value(key: str, value: Any) -> Optional[str]:
        if value is None:
            return None

        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")

        if key in {"isMount", "isLoopCenter", "isRaster", "isDS", "n_mount", "nds_multi", "nds_helical", "nds_helpart", "data_index", "n_mount_fails"}:
            try:
                return str(int(value))
            except Exception:
                return None

        if key in {"scan_height", "scan_width", "hel_cry_size", "flux", "phs_per_deg"}:
            try:
                return str(value)
            except Exception:
                return None

        if key in {"t_meas_start", "t_mount_end", "t_cent_start", "t_cent_end", "t_raster_start", "t_raster_end", "t_ds_start", "t_ds_end", "t_dismount_start", "t_dismount_end", "log_mount", "meas_record"}:
            s = str(value)
            if s == "None":
                return None
            return s

        return str(value)

    def build_result_payload(self, record: OldESARecord) -> dict[str, Any]:
        data_dict: dict[str, str] = {}
    
        # 1. 通常項目
        for key in RESULT_KEYS:
            if key not in record.row:
                continue
    
            # t_meas_start は特殊処理するので一旦スキップ
            if key == "t_meas_start":
                continue
    
            v = self.normalize_value(key, record.row.get(key))
            if v is None:
                continue
            data_dict[key] = v
    
        # 2. 旧ESAイベント列を展開
        raw_event_str = record.row.get("t_meas_start")
        if raw_event_str is not None:
            parsed_times = parse_event_time_string(str(raw_event_str))
            for k, v in parsed_times.items():
                data_dict[k] = v
    
        # 3. dict -> [{"k":"v"}, ...] 形式へ
        data_list = [{k: v} for k, v in data_dict.items()]
        return {"data": data_list}

    def import_one(self, old: OldESARecord, web: dict[str, Any]) -> None:
        zoo_samplepin_id = int(web["zoo_samplepin_id"])
        p_index = int(web["p_index"])
        payload = self.build_result_payload(old)

        self.logger.info(
            "Importing sample_id=%s zoo_samplepin_id=%s isDone=%s payload_keys=%s",
            old.sample_id,
            zoo_samplepin_id,
            old.isDone,
            [list(x.keys())[0] for x in payload["data"]],
        )

        if self.dry_run:
            print("[DRY-RUN] sample_id=", old.sample_id)
            print("[DRY-RUN] zoo_samplepin_id=", zoo_samplepin_id)
            print("[DRY-RUN] p_index=", p_index)
            print("[DRY-RUN] isDone=", old.isDone)
            print("[DRY-RUN] result_payload=", json.dumps(payload, ensure_ascii=False, indent=2))
            return

        if payload["data"]:
            self.api.postResult(zoo_samplepin_id, payload)

        if old.isDone is not None:
            self.api.setDone(p_index=p_index, zoo_samplepin_id=zoo_samplepin_id, isDone=int(old.isDone))

    def run(self) -> int:
        old_records = self.reader.read_all()
        samplepin_map = self.build_samplepin_map()

        target_records = old_records if self.limit is None else old_records[: self.limit]

        n_ok = 0
        n_skip = 0
        for old in target_records:
            web = samplepin_map.get(old.sample_id)
            if web is None:
                self.logger.warning("No WebDB samplepin found for sample_id=%s", old.sample_id)
                n_skip += 1
                continue
            self.import_one(old, web)
            n_ok += 1

        self.logger.info("Finished. imported=%d skipped=%d", n_ok, n_skip)
        return 0


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Import result records from old zoo.db into WebDB")
    p.add_argument("db_path", help="Path to zoo_*.db")
    p.add_argument("--exid", required=True, help="EXID already registered in WebDB")
    p.add_argument("--dry-run", action="store_true", help="Print mapping/payload only")
    p.add_argument("--limit", type=int, default=None, help="Import only first N ESA rows")
    return p


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("import_results_from_zoodb")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(h)
    return logger


def main() -> int:
    args = build_argparser().parse_args()
    logger = setup_logger()

    importer = ResultImporter(
        db_path=Path(args.db_path).resolve(),
        exid=args.exid,
        dry_run=args.dry_run,
        limit=args.limit,
        logger=logger,
    )
    return importer.run()


if __name__ == "__main__":
    sys.exit(main())