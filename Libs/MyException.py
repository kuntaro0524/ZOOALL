class MyException(Exception): pass
class MovementFailed(Exception): pass
class NandaKandaExcept(Exception): pass
class verticalCenteringFailed(Exception): pass
class VscanZOOfailed(Exception): pass
class FailedToGetVcenter(Exception): pass
class SameVerticalCordinates(Exception): pass
class CrystalIsTooSmall(Exception): pass

# Related to 'centering' crystals.
class RecoverableCenteringError(MyException):
    """Exception raised when centering fails but can be recovered."""
    pass

class FatalCenteringError(MyException):
    """Critical error in centering : Experiment should be aborted."""
    pass