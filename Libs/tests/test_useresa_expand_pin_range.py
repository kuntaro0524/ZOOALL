import logging
from UserESA import UserESA


def make_useresa():
    u = UserESA.__new__(UserESA)
    u.logger = logging.getLogger("test_expand_pin_range")
    u.logger.handlers = []
    u.logger.addHandler(logging.NullHandler())
    return u


def test_expand_pin_range_dash():
    u = make_useresa()
    assert u.expandPinRange("1-4") == [1, 2, 3, 4]


def test_expand_pin_range_plus():
    u = make_useresa()
    assert u.expandPinRange("1+2+3") == [1, 2, 3]


def test_expand_pin_range_semicolon():
    u = make_useresa()
    assert u.expandPinRange("1;2;3") == [1, 2, 3]


def test_expand_pin_range_single():
    u = make_useresa()
    assert u.expandPinRange("5") == ["5"]
