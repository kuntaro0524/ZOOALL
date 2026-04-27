# test_record_beam_dump_failure.py

from ErrorCode import ErrorCode


class DummyNavigator:
    def __init__(self):
        self.calls = []

    def updateDBinfo(self, cond, key, value):
        self.calls.append((key, value))

    def updateTime(self, cond, key):
        self.calls.append(("time", key))

    def recordBeamDumpFailure(self, cond, job_name, status):
        message = (
            f"Beam dump occurred during job={job_name}. "
            f"BSS status={status}"
        )

        error_value = ErrorCode.BEAM_DUMP_RECOVERED.to_db_value()

        self.updateDBinfo(cond, "isDone", error_value)
        self.updateDBinfo(
            cond,
            "meas_record",
            ErrorCode.getMessage(error_value)
        )
        self.updateDBinfo(cond, "log_beam_dump", message)
        self.updateTime(cond, "meas_end")


def test_record_beam_dump_failure():
    nav = DummyNavigator()
    cond = {}

    nav.recordBeamDumpFailure(
        cond,
        job_name="raster_scan",
        status="ready_beam__dump__recovered"
    )

    result = dict(
        (k, v) for k, v in nav.calls if k != "time"
    )

    assert result["isDone"] == 4001
    assert result["meas_record"] == "Beam dump recovered"
    assert isinstance(result["meas_record"], str)
