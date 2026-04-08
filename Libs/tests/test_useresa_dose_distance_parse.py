import logging
import pandas as pd

from UserESA import DoseDistanceHandler


def make_handler():
    logger = logging.getLogger("test_dose_distance_parse")
    logger.handlers = []
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.DEBUG)
    return DoseDistanceHandler(logger, debug=True)


def test_parse_series_like_accepts_plus_delimiter():
    handler = make_handler()
    vals = handler._parse_series_like("0.1+1.0+1.0")
    assert vals == [0.1, 1.0, 1.0]

def test_parse_series_like_accepts_normal():
    handler = make_handler()
    vals = handler._parse_series_like("[0.1,1.0,1.0]")
    assert vals == [0.1, 1.0, 1.0]


def test_parse_series_like_accepts_semicolon_and_comma():
    handler = make_handler()
    vals = handler._parse_series_like("100;110,120")
    assert vals == [100.0, 110.0, 120.0]


def test_parse_series_like_accepts_fullwidth_plus_and_brackets():
    handler = make_handler()
    vals = handler._parse_series_like("［0.1＋1.0＋2.0］")
    assert vals == [0.1, 1.0, 2.0]


def test_check_dose_list_accepts_legacy_plus_format():
    handler = make_handler()

    df = pd.DataFrame([
        {
            "mode": "single",
            "dose_list": "0.1+1.0",
            "dist_list": "150+110",
        }
    ])

    out = handler.check_dose_list(df)

    assert out.loc[0, "dose_list"] == "[0.1, 1]"
    assert out.loc[0, "dist_list"] == "[150, 110]"