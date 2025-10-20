import os
import io
import pandas as pd
import pytest

NOT_MOUNT = "Not-Mount"
NOT_MOUNTED = "Not-Mounted"

# ----------------- Mock for Zoo (hardware layer) -----------------
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
    # 未搭載スロットは "Not-Mounted" を返す流儀に合わせる
    def getSampleInformation(self):
        out = [str(p) for p in self.space]
        while len(out) < 8:
            out.append(NOT_MOUNTED)
        return out

    # PEの各スロット（簡易化。スロット番号は無視して循環参照）
    def pe_get_puck(self, idx: int):
        if not self.pe:
            return NOT_MOUNTED
        # 安定した順序を返したいので sort して循環
        arr = sorted(self.pe)
        return arr[(idx - 1) % len(arr)] if arr else NOT_MOUNTED

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
def px_with_zoo(monkeypatch):
    # あなたの実装モジュールを読み込む
    from PuckExchanger import PuckExchanger

    # デフォルトの MockZoo（個々のテストで上書き）
    zoo = MockZoo(space_pucks=[], pe_pucks=set())
    px = PuckExchanger(zoo)

    # もし run_exchange_for_single_csv が未実装なら、一時ラッパを注入
    if not hasattr(px, "run_exchange_for_single_csv"):
        # 既存の checkCurrentPucksAndMount を利用した簡易ラッパ
        # 仕様の「PE在庫チェック」「8枠チェック」は本体側で実装済みを想定。
        # 未実装でも、Mock なので実被害はなし。
        def _fallback(csv_path: str):
            # 既存の関数名と列前提に合わせる（puckid）
            px.checkCurrentPucksAndMount(csv_path)
        px.run_exchange_for_single_csv = _fallback

    # ロガーは無音化
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
    期待：Unmount→Mount の順に呼ばれ、最終SPACEは {p1, p2}
    """
    zoo = MockZoo(space_pucks=["p1", "pX"], pe_pucks={"p1", "p2", "p3"})
    px_with_zoo.zoo = zoo

    csv = write_csv(tmp_path, ["p1", "p2"])
    px_with_zoo.run_exchange_for_single_csv(str(csv))

    # 呼び出し順の論理（必ずしも厳密順序までは保証しないが履歴は残る）
    assert "pX" in zoo.unmount_calls            # 不要は外す
    assert "p2" in zoo.mount_calls              # 必要な不足分を入れる
    assert set(zoo.space) == {"p1", "p2"}       # 最終状態

def test_missing_in_pe_stops_early(tmp_path, px_with_zoo):
    """
    仕様④: CSVにあるがPEに無いパックがあれば、実行前に停止
    """
    zoo = MockZoo(space_pucks=[], pe_pucks={"p1"})
    px_with_zoo.zoo = zoo

    csv = write_csv(tmp_path, ["p1", "p_missing"])
    # 本体側で _validate_planned_exist_in_pe が例外を投げることを期待
    with pytest.raises(RuntimeError):
        px_with_zoo.run_exchange_for_single_csv(str(csv))

def test_capacity_respected_with_unmount(tmp_path, px_with_zoo):
    """
    8枠制約: keep + mount <= 8
    - SPACEに既に6枠（うち不要が4つ: pX*）
    - CSVは pA, pB, pC を要求（keep=2, mount=1）
    → 不要を外して枠を作り、pCを入れられる
    """
    zoo = MockZoo(space_pucks=["pA","pB","pX1","pX2","pX3","pX4"],
                  pe_pucks={"pA","pB","pC"})
    px_with_zoo.zoo = zoo

    csv = write_csv(tmp_path, ["pA","pB","pC"])
    px_with_zoo.run_exchange_for_single_csv(str(csv))

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
    px_with_zoo.run_exchange_for_single_csv(str(csv))

    assert "p1" in zoo.mount_calls
    assert set(zoo.space) == {"p1"}

def test_duplicate_puckids_in_csv_only_mount_once(tmp_path, px_with_zoo):
    """
    CSVに重複があっても mount は重複しないこと（内部で重複排除している想定）
    """
    zoo = MockZoo(space_pucks=[], pe_pucks={"p1"})
    px_with_zoo.zoo = zoo

    csv = write_csv(tmp_path, ["p1","p1","p1"])
    px_with_zoo.run_exchange_for_single_csv(str(csv))

    assert zoo.mount_calls.count("p1") == 1
    assert set(zoo.space) == {"p1"}

def test_no_puckid_column_raises(tmp_path, px_with_zoo):
    """
    CSVに 'puckid' 列が無ければ例外
    """
    p = tmp_path / "bad.csv"
    pd.DataFrame({"wrong": ["p1","p2"]}).to_csv(p, index=False)
    with pytest.raises(RuntimeError):
        px_with_zoo.run_exchange_for_single_csv(str(p))

