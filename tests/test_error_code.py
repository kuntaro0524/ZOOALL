# test_error_code.py

from ErrorCode import ErrorCode


def test_to_db_value_returns_int():
    assert ErrorCode.SPACE_ACCIDENT.to_db_value() == 9999
    assert ErrorCode.UNKNOWN_MEASUREMENT_MODE.to_db_value() == 8001
    assert ErrorCode.SUCCESS.to_db_value() == 1


def test_from_code_returns_enum():
    assert ErrorCode.from_code(9999) == ErrorCode.SPACE_ACCIDENT
    assert ErrorCode.from_code(8001) == ErrorCode.UNKNOWN_MEASUREMENT_MODE
    assert ErrorCode.from_code(1) == ErrorCode.SUCCESS


def test_from_code_unknown_returns_unknown_error():
    assert ErrorCode.from_code(123456) == ErrorCode.UNKNOWN_ERROR


def test_get_message_accepts_enum():
    assert ErrorCode.getMessage(ErrorCode.SPACE_ACCIDENT) == "SPACE accident occurred"
    assert ErrorCode.getMessage(ErrorCode.UNKNOWN_MEASUREMENT_MODE) == "Unknown measurement mode"


def test_get_message_accepts_int():
    assert ErrorCode.getMessage(9999) == "SPACE accident occurred"
    assert ErrorCode.getMessage(8001) == "Unknown measurement mode"

def test_grub_failed_message():
    assert ErrorCode.SPACE_WARNING_GRAB_FAILED.to_db_value() == 9004
    assert ErrorCode.getMessage(9004) == "SPACE warning: Grub failed to pick up the sample pin"
    assert isinstance(ErrorCode.getMessage(ErrorCode.SPACE_WARNING_GRAB_FAILED), str)

def test_get_message_unknown_code():
    assert ErrorCode.getMessage(123456) == "Unknown error"


def test_get_message_is_always_string():
    values = [
        ErrorCode.SPACE_ACCIDENT,
        ErrorCode.SPACE_ACCIDENT.to_db_value(),
        9999,
        8001,
        -1,
        123456,
    ]

    for value in values:
        assert isinstance(ErrorCode.getMessage(value), str)