#from Libs.Libs import BeamsizeConfig
import BeamsizeConfig

config_dir="/isilon/blconfig/bl32xu/"
beamsizeconf=BeamsizeConfig.BeamsizeConfig(config_dir)

flux_list=beamsizeconf.getFluxListForKUMA()
index=beamsizeconf.getBeamIndexHV(20,20)

flux=flux_list[index]
