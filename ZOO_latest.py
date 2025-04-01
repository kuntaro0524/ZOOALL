import sys,math,numpy,os 
import socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/")
import LoopMeasurement
import Zoo
import AttFactor
import AnaShika
import Condition
import ZooNavigator
import Hebi

mat = [
              Condition.Condition(uname="wireLL",
                        pucks_and_pins=[
                                        #["CPS0297", [3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                                        #["CPS1574", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                                        ["CPS1574", [5,6,7,8,9,10,11,12,13,14,15,16]],
                                       ],
			mode="multi",
			sample_name="LL",
			wavelength=0.915, # wavelength
                        h_beam=10.0, #[um square shaped]
                        v_beam=10.0, #[um square shaped]
                        raster_exp=0.02, # [sec.] normally 0.02sec
                        osc_width=0.1, #[deg.]
                        total_osc=5.0, #[deg.]
                        exp_henderson=0.20, #[sec] This is not usefull for 'helical data collection'
                        exp_time=0.05, # do not set 5deg/sec
                        distance=150.0, #[mm]
                        att_raster=10, #[%] from 2016/10/04 # Raster attenuator transmission
                        shika_minscore=3000,
                        shika_mindist=0,
                        shika_maxhits=50,
                        loop_size="medium",
                        helical_hbeam=2.0,
                        helical_vbeam=15.0,
			hebi_att=10.0, # Attenuation factor[%] for finding left/right edges in HEBI
                        photon_density_limit=2E10,
                        ntimes=1,
                        reduced_fac=1.00,
                        offset_angle=0.0,
              ),
              Condition.Condition(uname="lys",
                        pucks_and_pins=[
                                        ["CPS0294", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                                        ["CPS1013", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                                        ["CPS1571", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]],
                                       ],
			mode="multi",
			sample_name="pino",
			wavelength=1.000, # wavelength
                        h_beam=10.0, #[um square shaped]
                        v_beam=15.0, #[um square shaped]
                        raster_exp=0.02, # [sec.] normally 0.02sec
                        osc_width=0.1, #[deg.]
                        total_osc=5.0, #[deg.]
                        exp_henderson=0.20, #[sec] This is not usefull for 'helical data collection'
                        exp_time=0.05, # do not set 5deg/sec
                        distance=150.0, #[mm]
                        att_raster=1.0, #[%] from 2016/10/04 # Raster attenuator transmission
                        shika_minscore=3000,
                        shika_mindist=0,
                        shika_maxhits=50,
                        loop_size="large",
                        helical_hbeam=2.0,
                        helical_vbeam=15.0,
			hebi_att=10.0, # Attenuation factor[%] for finding left/right edges in HEBI
                        photon_density_limit=2E10,
                        ntimes=1,
                        reduced_fac=1.00,
                        offset_angle=0.0,
              ),
              ]

if __name__ == "__main__":
        # Cmount position
        sx= 0.1829
        sy=-11.5
        sz=-0.0615
        sphi=0.0

	# Experiment note
	# LCP crystals were from wire method.
	# Matsuda picked up all of pins on 2 unipucks.
	kundir="/isilon/users/target/target/Staff/kuntaro/161123/"

        ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #ms.connect(("192.168.163.1", 10101))
        ms.connect(("172.24.242.41", 10101))

        zoo=Zoo.Zoo()
	zoo.connect()

	# tln_conds
        name="161121-screen"
        navi=ZooNavigator.ZooNavigator(zoo,ms,kundir,name,sx,sy,sz,sphi,mat)
        navi.run()

        # Finishing jobs
        navi.finishZoo()
        zoo.disconnect()
        ms.close()
