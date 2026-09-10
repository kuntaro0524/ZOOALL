import logging
import pandas as pd
import pytest

from UserESA import DoseDistanceHandler


def make_handler():
    logger = logging.getLogger("test_useresa")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.DEBUG)
    return DoseDistanceHandler(logger, debug=True)


# -----------------------------
# validate_dose_dist() tests
# -----------------------------

def test_validate_accepts_empty_both():
    h = make_handler()
    cond = {
        "mode": "single",
        "dose_list": "",
        "dist_list": "",
    }
    h.validate_dose_dist(cond)


def test_validate_accepts_dose_only_single():
    h = make_handler()
    cond = {
        "mode": "single",
        "dose_list": "5,10,20",
        "dist_list": "",
    }
    h.validate_dose_dist(cond)


def test_validate_accepts_dose_and_dist_same_length():
    h = make_handler()
    cond = {
        "mode": "helical",
        "dose_list": "5,10,20",
        "dist_list": "100,110,120",
    }
    h.validate_dose_dist(cond)


def test_validate_rejects_dist_only():
    h = make_handler()
    cond = {
        "mode": "single",
        "dose_list": "",
        "dist_list": "100,110",
    }
    with pytest.raises(ValueError, match="dist_list cannot be specified without dose_list"):
        h.validate_dose_dist(cond)


def test_validate_rejects_length_mismatch():
    h = make_handler()
    cond = {
        "mode": "single",
        "dose_list": "5,10,20",
        "dist_list": "100,110",
    }
    with pytest.raises(ValueError, match="same length"):
        h.validate_dose_dist(cond)


@pytest.mark.parametrize("mode", ["multi", "mixed", "ssrox"])
def test_validate_rejects_multiple_values_for_forbidden_modes(mode):
    h = make_handler()
    cond = {
        "mode": mode,
        "dose_list": "5,10",
        "dist_list": "",
    }
    with pytest.raises(ValueError, match="does not allow multiple values"):
        h.validate_dose_dist(cond)


@pytest.mark.parametrize("mode", ["quick", "screening"])
def test_validate_accepts_quick_and_screening(mode):
    h = make_handler()
    cond = {
        "mode": mode,
        "dose_list": "",
        "dist_list": "",
    }
    h.validate_dose_dist(cond)


def test_validate_rejects_unknown_mode():
    h = make_handler()
    cond = {
        "mode": "weird_mode",
        "dose_list": "",
        "dist_list": "",
    }
    with pytest.raises(ValueError, match="Unknown mode"):
        h.validate_dose_dist(cond)


# -----------------------------
# _parse_series_like() tests
# -----------------------------

def test_parse_empty_returns_none():
    h = make_handler()
    assert h._parse_series_like("") is None


def test_parse_single_number():
    h = make_handler()
    assert h._parse_series_like("5") == [5.0]


def test_parse_csv_numbers():
    h = make_handler()
    assert h._parse_series_like("5,10,20") == [5.0, 10.0, 20.0]


def test_parse_bracketed_numbers():
    h = make_handler()
    assert h._parse_series_like("[5, 10, 20]") == [5.0, 10.0, 20.0]


def test_parse_plus_and_semicolon():
    h = make_handler()
    assert h._parse_series_like("5+10;20") == [5.0, 10.0, 20.0]


def test_parse_fullwidth_chars():
    h = make_handler()
    assert h._parse_series_like("［5，10，20］") == [5.0, 10.0, 20.0]


def test_parse_bad_token_raises():
    h = make_handler()
    with pytest.raises(ValueError, match="Bad numeric token"):
        h._parse_series_like("[5, abc, 20]")


# -----------------------------
# _serialize_list_for_csv() tests
# -----------------------------

def test_serialize_none():
    h = make_handler()
    assert h._serialize_list_for_csv(None) == ""


def test_serialize_empty():
    h = make_handler()
    assert h._serialize_list_for_csv([]) == ""


def test_serialize_single():
    h = make_handler()
    assert h._serialize_list_for_csv([5.0]) == "5"


def test_serialize_multiple():
    h = make_handler()
    assert h._serialize_list_for_csv([5.0, 10.0, 20.0]) == "[5, 10, 20]"


# -----------------------------
# check_dose_list() tests
# -----------------------------

def test_check_dose_list_normalizes_dataframe():
    h = make_handler()
    df = pd.DataFrame([
        {
            "mode": "single",
            "dose_list": "5,10,20",
            "dist_list": "100,110,120",
        }
    ])

    out = h.check_dose_list(df)

    assert out.loc[0, "dose_list"] == "[5, 10, 20]"
    assert out.loc[0, "dist_list"] == "[100, 110, 120]"


def test_check_dose_list_accepts_dose_only():
    h = make_handler()
    df = pd.DataFrame([
        {
            "mode": "single",
            "dose_list": "5,10,20",
            "dist_list": "",
        }
    ])

    out = h.check_dose_list(df)

    assert out.loc[0, "dose_list"] == "[5, 10, 20]"
    assert out.loc[0, "dist_list"] == ""


def test_check_dose_list_rejects_dist_only():
    h = make_handler()
    df = pd.DataFrame([
        {
            "mode": "single",
            "dose_list": "",
            "dist_list": "100,110",
        }
    ])

    with pytest.raises(ValueError, match="dist_list cannot be specified without dose_list"):
        h.check_dose_list(df)


def test_check_dose_list_rejects_length_mismatch():
    h = make_handler()
    df = pd.DataFrame([
        {
            "mode": "single",
            "dose_list": "5,10,20",
            "dist_list": "100,110",
        }
    ])

    with pytest.raises(ValueError, match="same length"):
        h.check_dose_list(df)


@pytest.mark.parametrize("mode", ["multi", "mixed", "ssrox"])
def test_check_dose_list_rejects_multiple_values_for_forbidden_modes(mode):
    h = make_handler()
    df = pd.DataFrame([
        {
            "mode": mode,
            "dose_list": "5,10",
            "dist_list": "",
        }
    ])

    with pytest.raises(ValueError, match="does not allow multiple values"):
        h.check_dose_list(df)
