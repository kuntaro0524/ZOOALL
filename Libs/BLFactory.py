import Zoo
import Device
import socket

from configparser import ConfigParser, ExtendedInterpolation

class BLFactory:
    def __init__(self):
        # 'beamline.ini' を ConfigParser で読み込む
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.config.read(config_path)

        # configureファイルから beamline を取得
        self.beamline = self.config.get("beamline", "beamline")
        # configure ファイルから bss_serverを取得
        self.bss_server = self.config.get("server", "bss_server")
        # configure fileから blanc_address を取得
        self.blanc_address = self.config.get("server", "blanc_address")

    def initDevice(self):
        # Message server に接続
        self.ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ms.connect((self.blanc_address, 10101))
        # Device をインスタンス化
        self.device = Device.Device(self.ms)
        # Zoo もインスタンス化
        self.zoo = Zoo()
        self.zoo.connect()
        # Device のインスタンスを返す
        self.isInit=True

        return self.device

    def getGoniometer(self):
        return "goniometer"
