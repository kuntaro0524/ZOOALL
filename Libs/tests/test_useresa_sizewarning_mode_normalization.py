import pandas as pd
from UserESA import UserESA


class DummyLogger:
    def __init__(self):
        self.messages = []

    def warning(self, msg):
        self.messages.append(msg)


def test_sizewarning_accepts_mode_with_spaces_and_case():
    u = UserESA.__new__(UserESA)
    u.logger = DummyLogger()

    u.df = pd.DataFrame([
        {
            "mode": " Multi ",
            "ds_hbeam": 10.0,
            "ds_vbeam": 8.0,
            "max_crystal_size": 25.0,
            "puckid": "PK1",
            "pinid": 1,
        }
    ])

    u.sizeWarning()

    assert any("multi" in str(msg).lower() for msg in u.logger.messages)
