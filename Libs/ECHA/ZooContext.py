# ZooContext.py
class ZooContext:
    zoo_exid = None
    username = None

    @classmethod
    def set_username(cls, name):
        cls.username = name

    @classmethod
    def set_zoo_exid(cls, exid):
        cls.zoo_exid = exid

    @classmethod
    def get_username(cls):
        return cls.username

    @classmethod
    def get_zoo_exid(cls):
        return cls.zoo_exid