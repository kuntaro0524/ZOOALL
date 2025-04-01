import os
from configparser import ConfigParser, ExtendedInterpolation
import BSSconfig  # BSSconfig モジュールをインポート
import Motor

class BaseAxis:
    # axis_type
    # "pulse": パルスモーター
    # "plc": PLC
    def __init__(self, server, axis_config_key, axis_type="pulse", isEvacuate=False):
        self.s = server
        
        # BSSconfig の設定読み込み
        self.bssconf = BSSconfig.BSSconfig()
        self.bl_object = self.bssconf.getBLobject()

        # beamline.ini を読み込む
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.config.read(f"{os.environ['ZOOCONFIGPATH']}/beamline.ini")

        try:
            if axis_type.lower() == "pulse":
                # もしもbeam stopperならば特別になる→ビームラインごとにY,Zの退避軸が異なる
                # axis_config_key には "bs" を含めておけばここに来るようにする（bss.configを調べてから軸名が決まるので）
                if axis_config_key.find("bs") != -1:
                    # 退避軸を探すための文字列は beamline.ini にある
                    evac_char = self.config.get("axes", "bs_evacinfo")
                    self.axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateAxis(evac_char)
                    self.full_axis_name = f"bl_{self.bl_object}_{self.axis_name}"
                    self.motor = Motor.Motor(self.s, self.full_axis_name, "pulse")
                    self.v2p, self.sense, self.home = self.bssconf.getPulseInfo(self.axis_name)
                elif axis_config_key.find("col") != -1:
                    # 退避軸を探すための文字列は beamline.ini にある
                    evac_char = self.config.get("axes", "col_evacinfo")
                    self.axis_name, self.on_pulse, self.off_pulse = self.bssconf.getEvacuateAxis(evac_char)
                    self.full_axis_name = f"bl_{self.bl_object}_{self.axis_name}"
                    self.motor = Motor.Motor(self.s, self.full_axis_name, "pulse")
                    self.v2p, self.sense, self.home = self.bssconf.getPulseInfo(self.axis_name)
                else:
                    # 軸の設定を取得
                    self.axis_name = self.config.get("axes", axis_config_key)
                    self.full_axis_name = f"bl_{self.bl_object}_{self.axis_name}"
                    # モーターオブジェクトを作成
                    self.motor = Motor.Motor(self.s, self.full_axis_name, "pulse")
                    # パルス情報の取得
                    self.v2p, self.sense, self.home = self.bssconf.getPulseInfo(self.axis_name)

                    # 退避軸の設定(BSはすでにやっている)
                    # lightでないことを確認する 'axis_config_key' に 'light' が含まれてる場合は light
                    if axis_config_key.find("light") == -1:
                        self.on_pulse, self.off_pulse = self.bssconf.getLightEvacuateInfo(self.axis_name)
                    elif isEvacuate:
                        self.on_pulse, self.off_pulse = self.bssconf.getEvacuateInfo(self.axis_name)
    
                print(f"[INFO] {self.__class__.__name__} initialized: {self.axis_name}")

            elif axis_type.lower() == "plc":
                # 軸の設定を取得
                self.axis_name = self.config.get("axes", axis_config_key)
                self.full_axis_name = f"bl_{self.bl_object}_{self.axis_name}"

        except Exception as e:
            print(f"[ERROR] {e}")
            raise