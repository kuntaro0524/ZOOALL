# -*- coding: utf-8 -*-
import pandas as pd
import pytest

NOT_MOUNT = "Not-Mount"
NOT_MOUNTED = "Not-Mounted"

# ----------------- Mock hardware layer (Zoo) -----------------
class MockZoo:
    """
    SPACE: 最大8枠を list で保持（搭載中パックID）
    PE   : 保管中パックIDを set で保持
    物理動作は行わず、メソッド呼び出し履歴を記録
    """
    def __init__(self, space_pucks=None, pe_pucks=None):
        self.space = list(space_pucks or [])
        self.pe = set(pe_pucks or [])
        self.mount_calls = []
        self.unmount_calls = []

    # SPACEの現況（本番は getSampleInformation() を使う）
    # 未搭載スロットは "Not-Mounted" で埋める想定
    def getSampleInformation(self):
        out = [str(p) for p in self.space]
        while len(out) < 8:
            out.append(NOT_MOUNTED)
        return out

    # PEの各スロット（簡易化。スロット番号は無視して循環参照）
    def pe_get_puck(self, idx: int):
        if not self.pe:
            return NOT_MOUNTED
        arr = sorted(self.pe)
        return arr[(idx - 1) % len(arr)]

    # SPACE→PE
    def pe_unmount_puck(self, puck_id: str):
        self.unmount_calls.append(puck_id)
        if puck_id in self.space:
            self.space.remove(puck_id)
            self.pe.add(puck_id)

    # PE→SPACE
    def pe_mount_puck(self, puck_id: str):
        self.mount_calls.append(puck_id)
        if puck_id in self.pe:
            if len(self.space) >= 8:
                raise RuntimeError("SPACE is full")
            self.pe.remove(puck_id)
            self.space.append(puck_id)

# ----------------- helpers -----------------
def write_csv(tmp_path, puck_ids, name="user.csv"):
    p = tmp_path / name
    pd.DataFrame({"puckid": puck_ids}).to_csv(p, index=False)
    return p

# ----------------- fixture -----------------
@pytest.fixture
def px_with_zoo():
    # あなたの実装モジュールを読み込む
    from PuckExchanger import PuckExchanger
    px = PuckExchanger() if PuckExchanger.__init__.__code__.co_argcount == 1 else PuckExchanger(None)
    # ダミーロガー
    class _L:
        def info(self, *a, **k): pass
        def error(self, *a, **k): pass
    px.logger = _L()
    return px

# ----------------- tests -----------------

def test_keep_unmount_mount_flow(tmp_path, px_with_zoo):
    """
    - CSV: p1, p2
    - SPACE: [p1, pX] -> p1はkeep, pXはunmount
    - PE: {p1, p2, p3} -> p2がmount
    期待：Unmount→Mount の順で呼ばれ、最終SPACEは {p1, p2}
    """
    zoo = MockZoo(space_pucks=["p1", "pX"], pe_pucks={"p1", "p2", "p3"})
    px_with_zoo.zoo = zoo

    csv = write_csv(tmp_path, ["p1", "p2"])
    px_with_zoo.checkCurrentPucksAndMount(str(csv))

    assert "pX" in zoo.unmount_calls
    assert "p2" in zoo.mount_calls
    assert set(zoo.space) == {"p1", "p2"}

def test_missing_in_pe_stops_early(tmp_path, px_with_zoo):
    """
    仕様④: CSVにあるがPEに無いパックがあれば、実行前に停止（RuntimeError）
    """
    zoo = MockZoo(space_pucks=[], pe_pucks={"p1"})
    px_with_zoo.zoo = zoo

    csv = write_csv(tmp_path, ["p1", "p_missing"])
    with pytest.raises(RuntimeError):
        px_with_zoo.checkCurrentPucksAndMount(str(csv))

def test_capacity_respected_with_unmount(tmp_path, px_with_zoo):
    """
    8枠制約: keep + mount <= 8
    - SPACEに6枠（不要が4つ: pX*）
    - CSVは pA, pB, pC を要求（keep=2, mount=1）
    → 不要を外して枠を作り、pCを入れられる
    """
    zoo = MockZoo(space_pucks=["pA","pB","pX1","pX2","pX3","pX4"],
                  pe_pucks={"pA","pB","pC"})
    px_with_zoo.zoo = zoo

    csv = write_csv(tmp_path, ["pA","pB","pC"])
    px_with_zoo.checkCurrentPucksAndMount(str(csv))

    assert "pC" in zoo.mount_calls
    assert any(u.startswith("pX") for u in zoo.unmount_calls)
    assert set(zoo.space) == {"pA","pB","pC"}

def test_not_mounted_slots_are_ignored(tmp_path, px_with_zoo):
    """
    "Not-Mount"/"Not-Mounted" は未搭載扱いで無視される前提を確認
    """
    zoo = MockZoo(space_pucks=[], pe_pucks={"p1"})
    px_with_zoo.zoo = zoo

    csv = write_csv(tmp_path, ["p1"])
    px_with_zoo.checkCurrentPucksAndMount(str(csv))

    assert "p1" in zoo.mount_calls
    assert set(zoo.space) == {"p1"}

def test_duplicate_puckids_in_csv_only_mount_once(tmp_path, px_with_zoo):
    """
    CSVに重複があっても mount は重複しないこと（内部で重複排除している前提）
    """
    zoo = MockZoo(space_pucks=[], pe_pucks={"p1"})
    px_with_zoo.zoo = zoo

    csv = write_csv(tmp_path, ["p1","p1","p1"])
    px_with_zoo.checkCurrentPucksAndMount(str(csv))

    assert zoo.mount_calls.count("p1") == 1
    assert set(zoo.space) == {"p1"}

def test_no_puckid_column_raises(tmp_path, px_with_zoo):
    """
    CSVに 'puckid' 列が無ければ RuntimeError
    """
    from pathlib import Path
    p = tmp_path / "bad.csv"
    pd.DataFrame({"wrong": ["p1","p2"]}).to_csv(p, index=False)
    with pytest.raises(RuntimeError):
        px_with_zoo.checkCurrentPucksAndMount(str(p))

def test_capacity_violation_raises(tmp_path, px_with_zoo):
    """
    8枠超過になる計画は RuntimeError を投げる想定の検証。
    例：
      - SPACE に keep 対象が 7個
      - CSV で追加 mount が 2個必要 → 7 + 2 = 9 > 8 でエラー
    """
    zoo = MockZoo(
        space_pucks=["k1","k2","k3","k4","k5","k6","k7"],  # 既に7枠
        pe_pucks={"k1","k2","k3","k4","k5","k6","k7","m1","m2"}
    )
    px_with_zoo.zoo = zoo
    csv = write_csv(tmp_path, ["k1","k2","k3","k4","k5","k6","k7","m1","m2"])
    with pytest.raises(RuntimeError):
        px_with_zoo.checkCurrentPucksAndMount(str(csv))

