"""Common access to ZOO's runtime beamline configuration.

This module intentionally owns only the environment-variable lookup,
``beamline.ini`` path construction, and ConfigParser creation/read.  It does
not import ZOO runtime or hardware modules and does not cache configuration.
"""

import os
from configparser import ConfigParser, ExtendedInterpolation


def get_config_path():
    """Return the runtime ``beamline.ini`` path.

    ``os.environ`` is intentionally used with subscription syntax to retain
    the existing ``KeyError`` behavior when ``ZOOCONFIGPATH`` is unset.
    """

    return os.path.join(os.environ["ZOOCONFIGPATH"], "beamline.ini")


def load_config():
    """Load and return the runtime ``beamline.ini`` configuration."""

    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(get_config_path())
    return config
