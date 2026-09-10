# zoo/dose/parse.py
from __future__ import annotations
import re
from typing import List

_NUM  = r"(?:\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)"
_UNIT = r"(?:MGy|kGy|Gy|mm)"  # dist_ds もここで扱える
RE_NUM  = re.compile(rf"^\s*({_NUM})\s*({ _UNIT })?\s*$", re.I)
RE_RANGE = re.compile(rf"^\s*({_NUM})\s*-\s*({_NUM})\s*({ _UNIT })?\s*@\s*({_NUM})\s*$", re.I)

UNIT_SCALE = {
    "gy": 1.0, "kgy": 1e3, "mgy": 1e6,
    "mm": 1.0,
}

def _scale(val: float, unit: str | None, default_unit: str) -> float:
    u = (unit or default_unit).lower()
    if u not in UNIT_SCALE:
        raise ValueError(f"Unsupported unit: {unit!r} (default={default_unit})")
    return float(val) * UNIT_SCALE[u]

def parse_series(s: str, *, default_unit: str) -> List[float]:
    """
    受理形式:
      - 単一: '10 MGy', '8.5e6 Gy', '200' (default_unit 適用)
      - 列挙: '2, 4, 6 MGy' / '0.5, 1.0, 1.5'（末尾に共通単位があってもOK）
      - 範囲: '0.5-2.0 MGy@0.5'（端点含む）
    出力: 数値列（default_unitに基づいた基準単位に正規化）
    """
    s = (s or "").strip()
    if not s:
        return []

    # range: a-b UNIT@step
    m = RE_RANGE.match(s)
    if m:
        a, b, unit, step = m.groups()
        a, b, step = float(a), float(b), float(step)
        vals, cur = [], a
        while cur <= b + 1e-12:
            vals.append(_scale(cur, unit, default_unit))
            cur += step
        return vals

    # comma list
    if "," in s:
        parts = [p.strip() for p in s.split(",") if p.strip()]
        # 行末の共通単位ヒント（任意）
        tail_unit = None
        m_tail = re.search(rf"({ _UNIT })\s*$", s, re.I)
        if m_tail:
            tail_unit = m_tail.group(1)

        out: List[float] = []
        for p in parts:
            m = RE_NUM.match(p)
            if not m:
                raise ValueError(f"Bad token: {p!r}")
            num, u = m.groups()
            out.append(_scale(float(num), u or tail_unit, default_unit))
        return out

    # single
    m = RE_NUM.match(s)
    if m:
        num, u = m.groups()
        return [_scale(float(num), u, default_unit)]

    raise ValueError(f"Bad series string: {s!r}")
