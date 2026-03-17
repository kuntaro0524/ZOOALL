# coding: UTF-8
import logging
import pandas as pd
import pytest

from UserESA import DoseDistanceHandler


def make_handler():
    logger = logging.getLogger("test_dose_distance_handler")
    logger.handlers = []
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.DEBUG)
    return DoseDistanceHandler(logger, debug=True)


def test_check_dose_list_normalizes_and_pads():
    handler = make_handler()

    df = pd.DataFrame([
        {
            "mode": "single",
            "dose_list": "[0.1, 1.0]",
            "dist_list": "[150.0]",
        }
    ])

    out = handler.check_dose_list(df)

    assert out.loc[0, "dose_list"] == "[0.1, 1]"
    assert out.loc[0, "dist_list"] == "[150, 150]"


def test_check_dose_list_requires_both_columns():
    handler = make_handler()

    df = pd.DataFrame([
        {
            "mode": "single",
            "dose_list": "[1,2]",
            "dist_list": "",
        }
    ])

    with pytest.raises(ValueError, match="dose_list and dist_list must be specified together"):
        handler.check_dose_list(df)


def test_multi_mode_prohibits_multiple_values():
    handler = make_handler()

    df = pd.DataFrame([
        {
            "mode": "multi",
            "dose_list": "[1,2]",
            "dist_list": "[100,120]",
        }
    ])

    with pytest.raises(ValueError, match="prohibits multiple values|does not allow multiple values"):
        handler.check_dose_list(df)


def test_validate_dose_dist_accepts_single_mode_single_value():
    handler = make_handler()

    cond = {
        "mode": "single",
        "dose_list": "1.0",
        "dist_list": "120.0",
    }

    assert handler.validate_dose_dist(cond) is None