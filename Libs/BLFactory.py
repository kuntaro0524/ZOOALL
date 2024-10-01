import Zoo
import Device
import socket
import Gonio44
import Gonio
import os

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
        # Zoo をインスタンス化して利用する
        self.zoo = Zoo.Zoo()
        self.zoo.connect()
        # Device をインスタンス化
        # この時点では gonio は未定義
        self.device = Device.Device(self.ms)
        self.device.init()
        # beamline に応じて Gonioインスタンスを生成する
        if self.beamline == "BL44XU":
            print("BL44XU!")
            # BSS server port を取得
            bss_server_port = self.zoo.getBSSr()
            # gonio44 をインスタンス化
            self.gonio = Gonio44.Gonio44(bss_server_port)
        else:
            self.gonio = Gonio.Gonio(self.ms)
        
        # Device に gonio をセット
        self.device.setGonio(self.gonio)

        # Device のインスタンスを返す
        self.isInit=True

    def getGoniometer(self):
        if self.isInit==False:
            self.initDevice()
        else:
            return self.device.gonio

# mainが実装されていない場合は、以下のコードが実行される
if __name__=="__main__":
    blf = BLFactory()
    blf.initDevice()
    # gonio = blf.getGoniometer()
    # print(gonio.getXYZmm())

    print("OPEN")
    import time

    blf.gonio.rotatePhi(225.0)