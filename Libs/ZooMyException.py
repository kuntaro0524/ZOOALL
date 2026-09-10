class ZooMyException(Exception): pass
MyException = ZooMyException
class MovementFailed(Exception): pass
class NandaKandaExcept(Exception): pass
class verticalCenteringFailed(Exception): pass
class VscanZOOfailed(Exception): pass
class FailedToGetVcenter(Exception): pass
class SameVerticalCordinates(Exception): pass
class CrystalIsTooSmall(Exception): pass

# Related to 'centering' crystals.
class RecoverableCenteringError(ZooMyException):
    """Exception raised when centering fails but can be recovered."""
    pass

class FatalCenteringError(ZooMyException):
    """Critical error in centering : Experiment should be aborted."""
    pass
class BeamDumpRecoveredException(Exception):
    """
    BSS が ready_beam__dump__recovered を返した場合に、
    当該 pin の残り処理を中断して次 pin へ進むための内部例外。
    """
    pass