# test_zoo_navigator_error_record.py

from ErrorCode import ErrorCode


class DummyNavigator:
    def __init__(self):
        self.calls = []

    def updateDBinfo(self, cond, param_name, value):
        self.calls.append((param_name, value))

    def record_error(self, cond, error_code):
        self.updateDBinfo(cond, "isDone", error_code.to_db_value())
        self.updateDBinfo(cond, "meas_record", ErrorCode.getMessage(error_code))


def test_meas_record_is_string_when_error_code_is_used():
    nav = DummyNavigator()
    cond = {}

    nav.record_error(cond, ErrorCode.SPACE_ACCIDENT)

    values = dict(nav.calls)

    assert values["isDone"] == 9999
    assert values["meas_record"] == "SPACE accident occurred"
    assert isinstance(values["meas_record"], str)


def test_meas_record_is_string_for_unknown_mode():
    nav = DummyNavigator()
    cond = {}

    nav.record_error(cond, ErrorCode.UNKNOWN_MEASUREMENT_MODE)

    values = dict(nav.calls)

    assert values["isDone"] == 8001
    assert values["meas_record"] == "Unknown measurement mode"
    assert isinstance(values["meas_record"], str)