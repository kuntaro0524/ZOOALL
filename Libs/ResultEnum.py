from enum import Enum, auto

class ResultCentering(Enum):
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    NO_CONTOUR = auto()

class ResultDatacollection(Enum):
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()