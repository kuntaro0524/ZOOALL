import PuckExchanger
import BLFactory

blf = BLFactory.BLFactory()
blf.initDevice()
puckexchanger = PuckExchanger.PuckExchanger(blf.zoo)

puck_list=puckexchanger.getAllPuckInfoPE()
print(puck_list)