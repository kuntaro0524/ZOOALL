# zoo/dose/fields.py
# 251007 ChatGPT
from __future__ import annotations
from typing import Dict, List
from dose.parse import parse_series

def get_series(row, key, default_unit="MGy", required=False):
    # 元の値を文字列で取得
    s = row.get(key, "")
    if s is None:
        s = ""
    s = str(s).strip()

    # 追加：全角→半角の統一（カンマ/カッコ）
    trans = str.maketrans({
        '（': '(', '）': ')',
        '［': '[', '］': ']',
        '｛': '{', '｝': '}',
        '，': ',',
        '　': ' '
    })
    s = s.translate(trans)

    # 追加：外側のカッコをはがす（{…} / […] / (…))
    if (s.startswith('{') and s.endswith('}')) or \
       (s.startswith('[') and s.endswith(']')) or \
       (s.startswith('(') and s.endswith(')')):
        s = s[1:-1].strip()

    # 空なら既存ポリシーに合わせる
    if not s:
        if required:
            raise ValueError(f"{key} is required")
        return []

    # ここから先は従来通り：正規化後の文字列を parse_series に渡す
    return parse_series(s, default_unit=default_unit)

def get_dose_ds(row: Dict[str, str]) -> List[float]:
    return get_series(row, "dose_ds", default_unit="Gy", required=False)

def get_dist_ds(row: Dict[str, str]) -> List[float]:
    return get_series(row, "dist_ds", default_unit="mm", required=False)
