Libs/AttFactor.py
/staff/config/bl44xu//bss/bss.config
#SmarGon_Z#

#  -----------------------------------------------

#     BL44XU BSS Config File  2005/04/05 (ueno)

#  -----------------------------------------------

#

BL_Name:BL44XU

BL_Object:44in

#BL_Global_Path:/isilon/users/users44/users44/2022B/

BL_Global_Path:/user/users44/2023B/

#BL_Global_Path:/home/bluser/2019B/

#BL_Global_Path:/work/

BL_IC1Range:10000.0

#

#  -----------------------------------------------

#    _/_/_/ Message Server (BL-WS) _/_/_/

#  -----------------------------------------------

#

Ms_IP:172.24.242.57

Ms_Port:10101

# 201203 If Ms_Communicatio_Delay which sets time of query is none, Default value is 300000(=300msec.).  500000=500msec.=0.5sec.

Ms_Communication_Delay: 500000

#

#--------------------------------------------------------------

# ST VME axis

#--------------------------------------------------------------

_axis_begin:

_axis_comment: st slit1 hall blade, used in scantool

_axis_name:st1_slit_1_hall

_cunit: pulse

_sense:1

_datum_mode:01011

_home_shift:0

_home_value:0.0

_val2pulse:2000

_speed0:500

_rise0:20

_fall0:20

_backlash0:100

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:500

_speed2:10

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: st slit1 ring blade, used in scantool

_axis_name:st1_slit_1_ring

_cunit: pulse

_sense:1

_datum_mode:11010

_home_shift:0

_home_value:0.0

_val2pulse:2000

_speed0:500

_rise0:20

_fall0:20

_backlash0:100

_cw_limit0:100000

_ccw_limit0:-100000

_speed1:500

_speed2:10

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: st slit1 upper blade, used in scantool

_axis_name:st1_slit_1_upper

_cunit: pulse

_sense:1

_datum_mode:01011

_home_shift:0

_home_value:0.0

_val2pulse:2000

_speed0:500

_rise0:20

_fall0:20

_backlash0:100

_cw_limit0:8150

_ccw_limit0:-2150

_speed1:500

_speed2:10

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: st slit1 lower blade, used in scantool

_axis_name:st1_slit_1_lower

_cunit: pulse

_sense:1

_datum_mode:11010

_home_shift:0

_home_value:0.0

_val2pulse:2000

_speed0:500

_rise0:20

_fall0:20

_backlash0:100

_cw_limit0:2150

_ccw_limit0:-8150

_speed1:500

_speed2:10

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: st slit1 vertical, used in scantool

_axis_name:st1_slit_1_z

_cunit: pulse

_sense:-1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:4000

_speed0:3000

_rise0:50

_fall0:50

_backlash0:400

_cw_limit0:25000

_ccw_limit0:-32000

_speed1:5000

_speed2:1000

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: st slit1 horizontal, used in scantool

_axis_name:st1_slit_1_y

_cunit: pulse

_sense:-1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:4000

_speed0:5000

_rise0:50

_fall0:50

_backlash0:400

_cw_limit0:25000

_ccw_limit0:-25000

_speed1:5000

_speed2:1000

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: st slit2 width, used in scantool

_axis_name:st1_slit_2_width

_cunit: pulse

_sense:1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:1000

_speed0:1000

_rise0:50

_fall0:50

_backlash0:100

_cw_limit0:8150

_ccw_limit0:-2150

_speed1:1000

_speed2:200

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: st slit2 height, used in scantool

_axis_name:st1_slit_2_height

_cunit:pulse

_sense:1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:1000

_speed0:1000

_rise0:50

_fall0:50

_backlash0:100

_cw_limit0:4000

_ccw_limit0:-8150

_speed1:1000

_speed2:200

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: st slit2 vertical, used in scantool

_axis_name:st1_slit_2_z

_cunit: pulse

_sense:-1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:4000

_speed0:5000

_rise0:50

_fall0:50

_backlash0:400

_cw_limit0:25000

_ccw_limit0:-25000

_speed1:5000

_speed2:1000

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: st slit2 horizontal, used in scantool

_axis_name:st1_slit_2_y

_cunit: pulse

_sense:1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:4000

_speed0:5000

_rise0:50

_fall0:50

_backlash0:400

_cw_limit0:25000

_ccw_limit0:-25000

_speed1:5000

_speed2:1000

_upper_limit:99999.

_lower_limit:-99999.

_axis_end:

#

_axis_begin:

_axis_comment: gonio mu, used in scantool

_axis_name:st1_gonio_1_mu

_cunit:pulse

_sense:1

_datum_mode:00101

_home_shift:

_home_value:0

_val2pulse:200

_speed0:500

_rise0:20

_fall0:20

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:500

_speed2:500

_upper_limit:99999999.9

_lower_limit:-99999999.9

_axis_end:

#

#_axis_begin:

##_axis_comment: gonio spindle axis   free rotation 

##_axis_comment: gonio spindle axis, ws new version

###_axis_comment: SmarGon gonio spindle axis, ws new version

##_axis_comment: gonio spindle axis, ws new version

#_axis_name:st1_gonio_1_omega

#_cunit:pulse

#_sense:1

#_datum_mode:00000

#_home_shift:0.0

#_home_value:119

#_val2pulse:6667

#_speed0:1200000

#_rise0:1

#_fall0:1

#_backlash0:0

#_cw_limit0:99999999

#_ccw_limit0:-99999999

#_speed1:600000

#_speed2:6000

#_upper_limit:1270.0

#_lower_limit:-1270.0

#_axis_end:

#

_axis_begin:

#_axis_comment: gonio spindle axis   free rotation 

#_axis_comment: gonio spindle axis, ws new version

_axis_comment: SmarGon gonio spindle axis, ws new version

_axis_name:SmarGon_OMEGA

_cunit:pulse

_sense:-1

_datum_mode:00000

_home_shift:0.0

_home_value:0.0

_val2pulse:10000

_speed0:1100000

_rise0:1

_fall0:1

_backlash0:0

_cw_limit0:99999999

_ccw_limit0:-99999999

_speed1:600000

_speed2:6000

_upper_limit:1270.0

_lower_limit:-1270.0

_axis_end:



# Dabutteru?

#_axis_begin:

##_axis_comment: gonio x axis with encoder,  plate x axis, used in scantool, ws new version

##_axis_comment: SmarGon gonio x axis,  plate x axis, used in scantool, ws new version

##_axis_name:SmarGon_Z

##_cunit:pulse

##_sense:-1

##_datum_mode:00000

##_home_shift:0

##_home_value:0.0

##_val2pulse:100000

##_val2encoder:100000

##_speed0:50000

###180514_speed0:30000

###180403_speed0:20000

###171005_speed0:50000

##_rise0:200

##_fall0:200

###171005_rise0:10

###171005_fall0:10

##_backlash0:0

##_cw_limit0:1000000

##_ccw_limit0:-1000000

##_speed1:30000

###171005_speed1:50000

##_speed2:20000

###_upper_limit: 99999.

###_lower_limit:-99999.

##_upper_limit: 2.3

##_lower_limit:-2.3

##_axis_end:

#

_axis_begin:

_axis_comment: SmarGon gonio phi axis, ws new version

_axis_name:SmarGon_PHI

_cunit:pulse

_sense:-1

_datum_mode:00000

_home_shift:0.0

_home_value:0.0

_val2pulse:10000

_speed0:200000

_rise0:10

_fall0:10

_backlash0:0

_cw_limit0:99999999

_ccw_limit0:-99999999

_speed1:30000

_speed2:5000

_upper_limit:1270.0

_lower_limit:-1270.0

_axis_end:

#

_axis_begin:

_axis_comment: SmarGon gonio chi axis, ws new version

_axis_name:SmarGon_CHI

_cunit:pulse

_sense:1

_datum_mode:00000

_home_shift:0.0

_home_value:0.0

_val2pulse:10000

_speed0:50000

_rise0:10

_fall0:10

_backlash0:0

_cw_limit0:99999999

_ccw_limit0:-99999999

_speed1:30000

_speed2:5000

#_upper_limit:89.5

_upper_limit:36.0

_lower_limit:-0.5

_axis_end:

#

_axis_begin:

#_axis_comment: gonio x axis with encoder,  plate x axis, used in scantool, ws new version

_axis_comment: SmarGon gonio x axis,  plate x axis, used in scantool, ws new version

_axis_name:SmarGon_Z

_cunit:pulse

_sense:-1

_datum_mode:00000

_home_shift:0

_home_value:0.0

_val2pulse:100000

_val2encoder:100000

_speed0:50000

#180514_speed0:30000

#180403_speed0:20000

#171005_speed0:50000

_rise0:200

_fall0:200

#171005_rise0:10

171005_fall0:10

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:30000

#171005_speed1:50000

_speed2:20000

#_upper_limit: 99999.

#_lower_limit:-99999.

_upper_limit: 4.6

_lower_limit:-4.6

_axis_end:

#

_axis_begin:

#_axis_comment: gonio z axis with encoder,  plate z axis, used in scantool, ws new version

_axis_comment: SmarGon gonio z axis,  plate z axis, used in scantool, ws new version

_axis_name:SmarGon_Y

_cunit:pulse

_sense:1

_datum_mode:00000

_home_shift:0

_home_value:0.0

_val2pulse:100000

_val2encoder:100000

_speed0:50000

#180514_speed0:30000

#180403_speed0:20000

#171005_speed0:50000

_rise0:200

_fall0:200

#171005_rise0:10

#171005_fall0:10

_backlash0:0

_cw_limit0:5000000

_ccw_limit0:-1000000

_speed1:30000

#171005_speed1:50000

_speed2:20000

_upper_limit: 4.6

_lower_limit:-4.6

_axis_end:

#

_axis_begin:bss.config_20221215

#_axis_comment: gonio y axis with encoder,  plate z axis, used in scantool, ws new version

_axis_comment: SmarGon gonio y axis,  plate z axis, used in scantool, ws new version

_axis_name:SmarGon_X

_cunit: pulse

_sense:1

_datum_mode:00000

_home_shift:0

_home_value:0.0

_val2pulse:100000

_val2encoder:100000

_speed0:50000

_rise0:200

_fall0:200

_backlash0:0

_cw_limit0:100000000

_ccw_limit0:-100000000

_speed1:30000

_speed2:20000

_upper_limit:11.7

_lower_limit:-99999.

_axis_end:

#

#_axis_begin:

#_axis_comment: gonio x axis with encoder,  plate x axis, used in scantool, ws new version

#_axis_name:st1_gonio_1_x

#_cunit:pulse

#_sense:-1

#_datum_mode:00101

#_home_shift:0

#_home_value:0.0

#_val2pulse:10000

#_val2encoder:10000

#_speed0:3000

###180514_speed0:30000

###180403_speed0:20000

###171005_speed0:50000

#_rise0:200

#_fall0:200

###171005_rise0:10

###171005_fall0:10

#_backlash0:0

#_cw_limit0:1000000

#_ccw_limit0:-1000000

#_speed1:3000

##171005_speed1:50000

#_speed2:2000

#_upper_limit: 99999.

#_lower_limit:-99999.

bss.config_20221215#_axis_end:

#

#_axis_begin:

#_axis_comment: gonio z axis with encoder,  plate z axis, used in scantool, ws new version

#_axis_name:st1_gonio_1_z

#_cunit:pulse

#_sense:1

#_datum_mode:10100

##_home_shift:0

#_home_value:0.0

#_val2pulse:10000

#_val2encoder:10000

#_speed0:5000

##180514_speed0:30000

###180403_speed0:20000

###171005_speed0:50000

#_rise0:200

#_fall0:200

###171005_rise0:10

###171005_fall0:10

#_backlash0:0

#_cw_limit0:5000000

#_ccw_limit0:-1000000

#_speed1:3000

##171005_speed1:50000

#_speed2:2000

#_upper_limit:99999.

#_lower_limit:-99999.

#_axis_end:

#

#_axis_begin:

#_axis_comment: gonio y axis with encoder,  plate z axis, used in scantool, ws new version

#_axis_name:st1_gonio_1_y

#_cunit: pulse

#_sense:1

#_datum_mode:00101

#_home_shift:0

#_home_value:0.0

#_val2pulse:10000

#_val2encoder:10000

#_speed0:5000

#_rise0:200

#_fall0:200

#_backlash0:0

#_cw_limit0:100000000

#_ccw_limit0:-100000000

#_speed1:5000

#_speed2:2000

#_upper_limit:99999.

#_lower_limit:-99999.

#_axis_end:

##

_axis_begin:

_axis_comment: camera 2theta1

_axis_name:st1_ip_1_x

_cunit: pulse

_sense:1

_datum_mode:11010

_home_shift:0

_home_value:0

_val2pulse:112500

_speed0:3000

_rise0:200

_fall0:200

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:1000

_speed2:50

_upper_limit:15.0

_lower_limit:0.0

_axis_end:

#

##

#_axis_begin:

#_axis_comment: attenuator unit1, used in scantool

#_axis_name:st1_att_1_rx

#_cunit:pulse

#_sense:-1

#_datum_mode:01010

#_home_shift:-14

#_home_value:0.0

#_val2pulse:50

#_speed0:100

#_rise0:20

#_fall0:20

#_backlash0:50

#_cw_limit0:1000000

#_ccw_limit0:-1000000

#_speed1:50

#_speed2:10

#_upper_limit:9999.9

#_lower_limit:-9999.9

#_axis_end:

#

_axis_begin:

_axis_comment: attenuator unit1, used in scantool

_axis_name:st1_att_1_rx

_cunit:pulse

_sense:-1

_datum_mode:01010

_home_shift:-140

_home_value:0.0

_val2pulse:200

_speed0:1500

_rise0:20

_fall0:20

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:1000

_speed2:50

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: stage direction

_axis_name:st1_stage_1_rz

_cunit: pulse

_sense:1

_datum_mode:00110

_home_shift:0

_home_value:0.0

_val2pulse:366300

_speed0:2000

_rise0:20

_fall0:20

_backlash0:-1000

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:2000

_speed2:250

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: stage height, used in scantool

_axis_name:st1_stage_1_z

_cunit:pulse

_sense:-1

_datum_mode:10100

_home_shift:0

_home_value:0.0

_val2pulse:54054

_speed0:10000

_rise0:200

_fall0:200

_backlash0:1000

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:10000

_speed2:2000

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: stage horizontal, used in scantool

_axis_name:st1_stage_1_y

_cunit:pulse

_sense:1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:10000

_speed0:10000

_rise0:50

_fall0:50

_backlash0:2000

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:10000

_speed2:2000

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: collimator XXX, used in scantool

_axis_name:st1_col_1_x

_cunit:pulse

_sense:-1

_datum_mode:10100

_home_shift:0

_home_value:-13.

_val2pulse:4000

_speed0:3000

_rise0:50

_fall0:50

_backlash0:-200

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:3000

_speed2:500

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: collimator YYY, used in scantool

_axis_name:st1_col_1_y

_cunit:pulse

_sense:1

_datum_mode:00101

_home_shift:0

_home_value:0

_val2pulse:4000

_speed0:3000

_rise0:50

_fall0:50

_backlash0:200

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:3000

_speed2:500

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: collimator ZZZ, used in scantool

_axis_name:st1_col_1_z

_cunit:pulse

_sense:-1

_datum_mode:10100

_home_shift:0

_home_value:0.0

_val2pulse:4000

_speed0:3000

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:3000

_speed2:500

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: sample light

_axis_name:st1_light_1_z

_cunit: pulse

_sense:-1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:200

_speed0:8000

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:10000000

_ccw_limit0:-10000000

_speed1:4000

_speed2:500

_upper_limit:211.

_lower_limit:-19.

_axis_end:

#

_axis_begin:

_axis_comment: beam stop z, evacuate, used in scantool

_axis_name:st1_bs_1_z

_cunit: pulse

_sense:-1

_datum_mode:00101

_home_shift:0

_home_value:-214

_val2pulse:2000

_speed0:40000

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:40000

_speed2:1000

_upper_limit:1000000.

_lower_limit:-1000000.

_axis_end:

#

#

_axis_begin:

_axis_comment: beam stop x, variable distance

_axis_name:st1_bs_1_x

_cunit: pulse

_sense:-1

_datum_mode:00101

_home_shift:0

_home_value:11.0

_val2pulse:200

_speed0:4000

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:4000

_speed2:1000

#_upper_limit:51.

_upper_limit:83.

#_lower_limit:16.0

_lower_limit:20.

#_lower_limit:30.0

_axis_end:

#

_axis_begin:

_axis_comment: beam stop y, used in scantool

_axis_name:st1_bs_1_y

_cunit: pulse

_sense:1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:1000

_speed0:500

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:500

_speed2:200

_upper_limit:1000000.

_lower_limit:-1000000.

_axis_end:

#

_axis_begin:

_axis_comment: ssd position 

_axis_name:st1_ssd_1_z

_cunit: pulse

_sense:1

_datum_mode:01011

_home_shift:0

_home_value:0.0

_val2pulse:500

_speed0:10000

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:4000

_speed2:500

_upper_limit:1000000.

_lower_limit:-1000000.

_axis_end:

#

#_axis_begin:

#_axis_comment: robot x

#_axis_name:st1_robot_1_x

#_cunit:pulse

#_sense:1

#_datum_mode:00101

#_home_shift:0

#_home_value:0

#_val2pulse:500

#_speed0:1000

#_rise0:50

#_fall0:50

#_backlash0:0

#_cw_limit0:1000000

#_ccw_limit0:-1000000

#_speed1:1000

#_speed2:500

#_upper_limit:507.1

#_lower_limit:77.4

#_axis_end:

#

#_axis_begin:

#_axis_comment: robot y

#_axis_name:st1_robot_1_y

#_cunit:pulse

#_sense:1

#_datum_mode:00101

#_home_shift:0

#_home_value:0

#_val2pulse:500

#_speed0:1000

#_rise0:50

#_fall0:50

#_backlash0:0

#_cw_limit0:1000000

#_ccw_limit0:-1000000

#_speed1:1000

#_speed2:500

#_upper_limit:507.1

#_lower_limit:77.4

#_axis_end:

#

_axis_begin:

#_axis_comment: microscope zoom axis

_axis_comment: microscope axis

_axis_name:st1_video_1_zoom

_cunit:pulse

_sense:1

_datum_mode:11010

_home_shift:0

_home_value:0.0

_val2pulse:1

_speed0:1500

_rise0:20

_fall0:20

_backlash0:0

_cw_limit0:-100

_ccw_limit0:-20000

_speed1:3000

_speed2:500

_upper_limit:-200.

_lower_limit:-20000.

_axis_end:

#

_axis_begin:

_axis_comment: microscope focus axis 

_axis_name:st1_video_1_focus

_cunit: pulse

_sense:1

_datum_mode:11010

_home_shift:0

_home_value:0.0

_val2pulse:1

_speed0:500

_rise0:10

_fall0:10

_backlash0:0

_cw_limit0:1000

_ccw_limit0:-1000

_speed1:3000

_speed2:500

_upper_limit:1000.

_lower_limit:-1000.

_axis_end:

#

_axis_begin:

_axis_comment: cameralength1

_axis_name:st1_ccd_1_x

_cunit: pulse

_sense:1

_datum_mode:11010

_home_shift:0

#_home_value:1256.

#180406 _home_value:1257.8

#190930_home_value:1273.2

#191003_home_value:1274.7

#220410_home_value:1273.2

#221117_home_value:1272.9

#230116_home_value:1271.7

#231002_home_value:1272.9

_home_value:1274.5

_val2pulse:100

#_speed0:2500

_speed0:10000

_rise0:300

_fall0:300

_backlash0:0

_cw_limit0:500000

_ccw_limit0:-500000

_speed1:1000

_speed2:50

#_upper_limit:601.

#_upper_limit:901.

_upper_limit:1400.

#_upper_limit:801.

#180406 _lower_limit:99.

#_lower_limit:115.5

_lower_limit:131.

#_lower_limit:120.

#_lower_limit:80.

#_lower_limit:75.

_axis_end:

#

_axis_begin:

_axis_comment: camera horizontal offset1

_axis_name:st1_ccd_1_y

_cunit: pulse

_sense:1

_datum_mode:1100

_home_shift:0

_home_value:0.0

_val2pulse:1000

_speed0:5000

_rise0:100

_fall0:100

_backlash0:0

_cw_limit0:150000

_ccw_limit0:-150000

_speed1:1000

_speed2:50

_upper_limit:1000.

_lower_limit:-1000.

_axis_end:

#

_axis_begin:

_axis_comment: camera vertical offset1

_axis_name:st1_ccd_1_z

_cunit: pulse

_sense:1

_datum_mode:1011

_home_shift:0

_home_value:0.0

_val2pulse:1786

_speed0:1500

_rise0:300

_fall0:300

_backlash0:0

_cw_limit0:360000

_ccw_limit0:-100000

_speed1:1000

_speed2:50

_upper_limit:250.

_lower_limit:-200.

_axis_end:

#

_axis_begin:

#_axis_comment: cryo vertical

_axis_comment: cryostream evacuate axis

_axis_name:st1_cryo_1_x

_cunit: pulse

_sense:-1

_datum_mode:10100

_home_shift:0

#_home_value:8.5

_home_value:0

_val2pulse:4000

_speed0:5000

#_speed0:7500

_rise0:300

_fall0:300

_backlash0:0

_cw_limit0:10000000

_ccw_limit0:-8000000

_speed1:5000

_speed2:500

_upper_limit:30.

#_lower_limit:6.5

#_lower_limit:0

_lower_limit:-30

_axis_end:

#

_axis_begin:

_axis_comment: microscope x axis, used in scantool

_axis_name:st1_video_2_x

_cunit: pulse

_sense:-1

_datum_mode:10100

_home_shift:0

_home_value:0.0

_val2pulse:40000

_speed0:10000

_rise0:50

_fall0:50

_backlash0:0

#_cw_limit0:1000000

#_ccw_limit0:-1000000

_cw_limit0:5000000

_ccw_limit0:-5000000

_speed1:10000

_speed2:5000

#_upper_limit:20.

#_lower_limit:-20.

_upper_limit:100.

_lower_limit:-100.

_axis_end:

#

_axis_begin:

_axis_comment: microscope y axis, used in scantool

_axis_name:st1_video_2_y

_cunit: pulse

_sense:1

_datum_mode:10100

_home_shift:0

_home_value:0.0

_val2pulse:40000

_speed0:10000

_rise0:50

_fall0:50

_backlash0:0

#_cw_limit0:1000000

#_ccw_limit0:-1000000

_cw_limit0:5000000

_ccw_limit0:-5000000

_speed1:10000

_speed2:5000

#_upper_limit:20.

#_lower_limit:-20.

_upper_limit:100.

_lower_limit:-100.

_axis_end:

#

_axis_begin:

_axis_comment: microscope z axis, used in scantool

_axis_name:st1_video_2_z

_cunit: pulse

_sense:-1

_datum_mode:00101

_home_shift:0

_home_value:0.0

_val2pulse:40000

_speed0:10000

_rise0:50

_fall0:50

_backlash0:0

#_cw_limit0:1000000

#_ccw_limit0:-1000000

_cw_limit0:-80000

_ccw_limit0:-120000

_speed1:10000

_speed2:5000

#_upper_limit:20.

#_lower_limit:-20.

_upper_limit:100.

_lower_limit:-100.

_axis_end:

#

_axis_begin:

_axis_comment: microscope zoom axis, used in scantool

_axis_name:st1_video_2_zoom

_cunit: pulse

_sense:1

_datum_mode:1100

_home_shift:0

_home_value:0.0

_val2pulse:1

_speed0:6000

_rise0:600

_fall0:600

_backlash0:0

_cw_limit0:100000

_ccw_limit0:-100000

_speed1:1000

_speed2:50

_upper_limit:50000

_lower_limit:17000

_axis_end:

#

_axis_begin:

_axis_comment: gonio zz axis, used in scantool

_axis_name:st1_gonio_1_zz

_cunit: pulse

_sense:1

_datum_mode:101

_home_shift:0

_home_value:0.0

_val2pulse:100000

_speed0:30000

_rise0:10

_fall0:10

_backlash0:0

_cw_limit0:2000000

_ccw_limit0:-2000000

_speed1:20000

_speed2:10000

_upper_limit:10.

_lower_limit:-10.

_axis_end:

#

_axis_begin:

_axis_comment: collimator x, evacuate axis, used in scantool

_axis_name:st1_col_2_x

_cunit:pulse

_sense:-1

_datum_mode:11010

_home_shift:0

_home_value:0.

_val2pulse:2000

_speed0:30000

#_speed0:15000

#_speed0:40000

_rise0:20

_fall0:20

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:5000

_speed2:500

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: collimator2 y, evacuate axis, used in scantool

_axis_name:st1_col_2_y

_cunit:pulse

_sense:1

_datum_mode:00101

_home_shift:0

_home_value:0.

_val2pulse:40000

_speed0:160000

_rise0:50

_fall0:50

#_backlash0:4000

_backlash0:0

_cw_limit0:600000

_ccw_limit0:-1200000

_speed1:40000

_speed2:20000

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: collimator2 z, used in scantool

_axis_name:st1_col_2_z

_cunit:pulse

_sense:1

_datum_mode:10100

_home_shift:0

_home_value:0.

_val2pulse:40000

_speed0:10000

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:1000000

_ccw_limit0:-1000000

_speed1:6000

_speed2:2000

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: bpm y, used in scantool

_axis_name:st1_bpm_1_y

_cunit:pulse

_sense:1

_datum_mode:10100

_home_shift:0

_home_value:0.

_val2pulse:40000

_speed0:75000

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:10000000

_ccw_limit0:-10000000

_speed1:75000

_speed2:10000

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: bpm z, used in scantool

_axis_name:st1_bpm_1_z

_cunit:pulse

_sense:-1

_datum_mode:10100

_home_shift:0

_home_value:0.

_val2pulse:40000

_speed0:50000

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:10000000

_ccw_limit0:-10000000

_speed1:50000

_speed2:10000

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

_axis_begin:

_axis_comment: camera cover z

_axis_name:st1_cover_1_z

_cunit:pulse

_sense:1

_datum_mode:1011

_home_shift:0

_home_value:0.

_val2pulse:53

_speed0:10000

_rise0:50

_fall0:50

_backlash0:0

_cw_limit0:10000000

_ccw_limit0:-10000000

_speed1:2000

_speed2:200

_upper_limit:9999.9

_lower_limit:-9999.9

_axis_end:

#

#--------------------------------------------------------------

# DIO axis

#--------------------------------------------------------------

#

_axis_begin:

_axis_comment: st shutter control axis

_axis_name:st1_shutter_1

_cunit: digital

_axis_end:

#

_axis_begin:

_axis_comment: st shutter2 control axis

_axis_name:st1_shutter_2

_cunit: digital

_axis_end:

#

_axis_begin:

_axis_comment: ccd trigger

_axis_name:st1_ccd_1

_cunit: digital

_axis_end:

#

# 2021.3.31 added

_axis_begin:

_axis_comment: ln2defroster axis

_axis_name:st1_blower_1

_cunit: digital

_axis_end:

#

#--------------------------------------------------------------

# Virtual axis

#--------------------------------------------------------------

#

# Oscillation axis

_axis_begin:

_axis_comment: oscillation control axis

_axis_name:st1_control_1

_axis_end:

#

# Shutterless scan axis

_axis_begin:

_axis_comment: shutterless scan control 

_axis_name:st1_exposure_1

_axis_end:

#

_axis_begin:

_axis_comment: st slit1 width, used in scantool

_axis_name:st1_slit_1_width

_cunit: mm

_axis_end:

#

_axis_begin:

_axis_comment:st slit1 height, used in scantool

_axis_name:st1_slit_1_height

_cunit: mm

_axis_end:

#

# Not used at BL44XU becasue actaul axes exist

#

#_axis_begin:

#_axis_comment: st slit1 horizontal, used in scantool

#_axis_name:st1_slit_1_horizontal

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: st slit1 vertical, used in scantool

#_axis_name:st1_slit_1_vertical

#_cunit: mm

#_axis_end:

#

## Oscillation axis

#_axis_begin:

#_axis_comment: oscillation control axis

#_axis_name:st1_control_1

#_axis_end:

#

# Stage tune axis

_axis_begin:

_axis_comment: stage tune axis

_axis_name:st1_stage_1

_counter_channel: 2

#

# Tune condition can be defined in bl41xu.config

#_scan_measuretime:200

#_scan_fwidth0:0.3

#_scan_fstep0:0.01

#_scan_fwidth1:0.1

#_scan_fstep1:0.005

_axis_end:

#

#

# Dtheta1 tune axis

_axis_begin:

_axis_comment: monochro tune axis

_axis_name:st1_dtheta1

_counter_channel: 0

_scan_width0:1200

_scan_step0:30

_scan_width1:100

_scan_step1:40

# Define detune_position here, if you use MOSTAB with I0 or RC mode

#_detune_position:0.8

_axis_end:

#

#--------------------------------------------------------------

# TC VME axis

#--------------------------------------------------------------

#

_axis_begin:

_axis_comment: monochro control object

_axis_name:tc1_stmono_1

_cunit: angstrome

_axis_end:

#

#

_axis_begin:

_axis_comment: monochro dtheta1, used in scantool

_axis_name:tc1_stmono_1_dtheta1

_cunit: pulse

_val2pulse: 100

_axis_end:

#

_axis_begin:

_axis_comment: id-gap, used in scantool

_axis_name:id_gap

_cunit: mm

_axis_end:

#

# TC slit axis

#_axis_begin:

#_axis_comment: tc slit1 width

#_axis_name:tc1_slit_1_width

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: tc slit1 height

#_axis_name:tc1_slit_1_height

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: tc slit1 horizontal, used in scantool

#_axis_name:tc1_slit_1_horizontal

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: tc slit1 vertical, used in scantool

#_axis_name:tc1_slit_1_vertical

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: tc slit2 width

#_axis_name:tc1_slit_2_width

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: tc slit2 height

#_axis_name:tc1_slit_2_height

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: tc slit2 horizontal, used in scantool

#_axis_name:tc1_slit_2_horizontal

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: tc slit2 vertical, used in scantool

#_axis_name:tc1_slit_2_vertical

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: used in scantool

#_axis_name: tc1_m70h_1_y

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: used in scantool

#_axis_name: tc1_m70h_1_z

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: used in scantool

#_axis_name: tc1_m70h_1_ty

#_cunit: mrad

#_axis_end:

#

#_axis_begin:

#_axis_comment: used in scantool

#_axis_name: tc1_m70h_1_tz

#_cunit: mrad

#_axis_end:

#

#_axis_begin:

#_axis_comment: used in scantool

#_axis_name: tc1_m33v_1_y

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: used in scantool

#_axis_name: tc1_m33v_1_z

#_cunit: mm

#_axis_end:

#

#_axis_begin:

#_axis_comment: used in scantool

#_axis_name: tc1_m33v_1_ty

#_cunit: mrad

#_axis_end:

#

#_axis_begin:

#_axis_comment: used in scantool

#_axis_name: tc1_m33v_1_tz

#_cunit: mrad

#_axis_end:

#

#

#--------------------------------------------------------------

# Counter axis

#--------------------------------------------------------------

#

_axis_begin:

_axis_comment: counter board control axis

_axis_name:st1_counter_1

_axis_end:

#

#

#--------------------------------------------------------------

# DA axis

#--------------------------------------------------------------

#

#

_axis_begin:

_axis_comment: sca1 voltage control

_axis_name:st1_sca_1

_axis_end:

#

_axis_begin:

_axis_comment: sca2 voltage control

_axis_name:st1_sca_2

_axis_end:

#

#

#

#  -----------------------------------------------

#    _/_/_/ Equipment stage _/_/_/

#  -----------------------------------------------

#

#_stage_begin:

#_stage_comment: RIGAKU HTP STAGE

#_stage_end:

#

#  -----------------------------------------------

#    _/_/_/ IP (DIP6040) _/_/_/

#  -----------------------------------------------

#

##_detector_begin:

##_detector_comment: ccd detector on stage1

##_Name:DIP6040

##_IP:172.16.1.12

##_Port:10101

###   next two lines have no effect on ADSC-CCD

###_Parallel_Process: no

###_Process_Directory: /image/.jhead

##_Expose_Delay: 0.0

###_Dark_Update_Interval: 0

##_detector_end:

#

#  -----------------------------------------------

#    _/_/_/ CCD (Rayonix MX225HE) _/_/_/

#  -----------------------------------------------

#_detector_begin:

#_detector_comment: ccd detector on stage1

#_Name:MAR300HE

##   Frame Grabber (det_api_workstation)

## For Isulon 180205   

#_IP:192.168.223.22

##_IP:172.16.1.14

#_Port:2222

##   next two lines have no effect on ADSC-CCD

##_Parallel_Process: no

##_Process_Directory: /image/.jhead

#_Expose_Delay: 0.0

#_Dark_Update_Interval: 3600

#_detector_end:

#

# -----------------------------------------------

# _/_/_/ EIGER16M _/_/_/

# -----------------------------------------------

#

_detector_begin:

_detector_comment: 2dpx detector on stage1

_Name:EIGER16M

#_IP:192.168.163.204

_IP:192.168.223.171

_Port:80

_Dark_Update_Interval: 0

_ADC_Mode_Selectable: n

#following 3 lines are necessary even for pilatus

_Binning_Dimensions: 1

_Readout_Times:0.0042016

_Frame_Transfer_Time:0.00002

_Shutterless_Measurement_Selectable:y

#_External_Trigger_Mode:10000

_External_Trigger_Mode:10001

#_External_Trigger_Mode:11111

_Max_Images_Per_File:100

#_Max_Images_Per_File:50

_Auto_Summation_Enabled:y

_Data_Compression_Enabled:y

_Data_Compression_Type:bslz4

#_Data_Compression_Type:lz4

_FlatField_Correction_Applied:y

_Start_Download_On_Acquisition:y

#_Filewriter_Enabled:y

#_Monitor_Enabled:y

#_Stream_Enabled:y

_ROI_Mode_Selectable: y

_detector_end:

#

#  ------------------------------------------------

#    _/_/_/ Crystal Centering Server _/_/_/

#  ------------------------------------------------

#

#Ccenter_IP:192.168.215.1

Ccenter_IP:127.0.0.1

#Ccenter_IP:172.16.1.101

Ccenter_Port:10101

Ccenter_Brightness: 32767

Ccenter_Hue: 32767

Ccenter_Color: 32767

Ccenter_Contrast: 50000

# when centering starts, what should be done?   on, off, or none?

Ccenter_Light_Condition: on

Ccenter_Cryostream_Condition: on

Ccenter_Collimator_Condition: off

Ccenter_Sync_Gonio_Translation: y

#

#

#  ------------------------------------------------

#    _/_/_/ Crystal Goniometer _/_/_/

#  ------------------------------------------------

_gonio_begin:

_gonio_comment: SmarGon

_gonio_IP:192.168.223.23

_gonio_Port:23

_gonio_end:

#

#  ------------------------------------------------

#    _/_/_/ Crystal Mount Server _/_/_/

#  ------------------------------------------------

#

#--- for simulation ---

#Cmount_IP:127.0.0.1

#

#Cmount_IP:172.16.1.31

Cmount_IP:192.168.223.25

#

Cmount_Port:3665

#Cmount_Gonio_Phi:0.0

#Cmount_Gonio_Kappa:0.0

#Cmount_Gonio_X:0.0

#Cmount_Gonio_Y:0.0

#Cmount_Gonio_Z:0.0

#Cmount_Gonio_Omega:0.0



# SmarGon 2022.10.18

Cmount_Gonio_X_Magnet:0.1050

Cmount_Gonio_Y_Magnet:6.1520

#Cmount_Gonio_Y_Magnet:6.1520

##Cmount_Gonio_Y_Magnet:7.8120

##Cmount_Gonio_Z_Magnet:-0.280

Cmount_Gonio_Z_Magnet:-0.280

##Cmount_Gonio_Z_Magnet:0.1610

##Cmount_Gonio_Chi:-0.00000

Cmount_Gonio_Chi:-0.5000

Cmount_Gonio_Phi:0.00000



# Airbearing

#Cmount_Gonio_X_Magnet:1.09600

#Cmount_Gonio_Y_Magnet:-6.81980

#201001 ZZ=0.5267 notokino atai# Cmount_Gonio_Z_Magnet:-0.73000

#Cmount_Gonio_Z_Magnet:-1.61800



#SmarGon Magpin 2019.10.01

#201001 Remove SmarGon Cmount_Gonio_X_Magnet:-0.20000

#201001 Remove SmarGon Cmount_Gonio_Y_Magnet:8.04600

#200127 ZZ=1.7656 notokino atai# Cmount_Gonio_Z_Magnet:-0.20000

#201001 Remove SmarGon Cmount_Gonio_Z_Magnet:-0.065

#Cmount_Gonio_Chi is changed 2020/04/02

#201001 Remove SmarGon Cmount_Gonio_Chi:-0.50000

#201001 Remove SmarGon Cmount_Gonio_Phi:0.00000

#

#Cmount_Gonio_Z_Offset_Used: y

#Cmount_Lhead_Offset_Used: y

#Cmount_Reference_Stage_Horizontal: 8.7969

#Cmount_Reference_Stage_Height: 6.2250

Cmount_Gonio_Z_Offset2_Used: n

#Cmount_Gonio_Z_Offset2_Used: y

Cmount_Reference_Gonio_ZZ: 0.8407

#

#150926Cmount_Gonio_Z_Magnet:5.91294

#Cmount_Gonio_Z_Magnet:5.16294

Cmount_Gonio_Omega:0.0

Cmount_Camera_Twotheta: 0.0

#Cmount_Camera_Distance_Threshold: 210.0

#160328

#Cmount_Camera_Distance_Threshold: 300.0 #180928

Cmount_Camera_Distance_Threshold: 210.0

Cmount_Collimator_Condition: off // "on", "off" or "table" etc.

Cmount_Cryostream_Condition: off

Cmount_Beamstop_Condition: off 

# ueno jul 2009

#Cmount_Pin_Expansion_Delay:  0

#Cmount_Pin_Expansion_Delay:  120

#

#Cmount_Type: SPACE_EVC

Cmount_Type: SPACE_TWIN

#

Cmount_Action_During_Cleaning:y

#

#Cmount_Lhead_Sense:1

#Cmount_Max_Tray_Number:2

Cmount_Max_Tray_Number:8

#

# for encoder

Cmount2_IP:192.168.223.26

Cmount2_Port:3665

#

#

#  ------------------------------------------------

#    _/_/_/ Attenuator  _/_/_/

#  ------------------------------------------------

#

##_attenuator_begin:

###

##_attenuator_unit_begin:

##_attenuator_unit_comment: attenuator unit1

##Attenuator1_0: Al 0um

##Attenuator1_1: Al 200um

##Attenuator1_2: Al 300um

##Attenuator1_3: Al 400um

##Attenuator1_4: Al 500um

##Attenuator1_5: Al 600um

##Attenuator1_6: Al 700um

##Attenuator1_7: Al 800um

##Attenuator1_8: Al 1300um

##Attenuator1_9: Al 1500um

##Attenuator1_10: Al 1700um

##Attenuator1_11: Al 1900um

##Attenuator1_12: Al 2200um

##Attenuator1_13: Al 2400um

##Attenuator1_14: Al 2600um

##Attenuator1_15: Al 3000um

##Attenuator1_16: Al 3500um

##Attenuator1_17: Al 6500um

##Attenuator1_18: Pb 100um

##Attenuator1_19: Pb 1000um

##Attenuator1_20: Auto

##_attenuator_unit_end:

###

##Attenuator_Menu_Label_0: [None] {0}

##Attenuator_Menu_Label_1: [Al 0.2mm] {1}

##Attenuator_Menu_Label_2: [Al 0.3mm] {2}

##Attenuator_Menu_Label_3: [Al 0.4mm] {3}

##Attenuator_Menu_Label_4: [Al 0.5mm] {4}

##Attenuator_Menu_Label_5: [Al 0.6mm] {5}

##Attenuator_Menu_Label_6: [Al 0.7mm] {6}

##Attenuator_Menu_Label_7: [Al 0.8mm] {7}

##Attenuator_Menu_Label_8: [Al 1.3mm] {8}

##Attenuator_Menu_Label_9: [Al 1.5mm] {9}

##Attenuator_Menu_Label_10: [Al 1.7mm] {10}

##Attenuator_Menu_Label_11: [Al 1.9mm] {11}

##Attenuator_Menu_Label_12: [Al 2.2mm] {12}

##Attenuator_Menu_Label_13: [Al 2.4mm] {13}

##Attenuator_Menu_Label_14: [Al 2.6mm] {14}

##Attenuator_Menu_Label_15: [Al 3.0mm] {15}

##Attenuator_Menu_Label_16: [Al 3.5mm] {16}

##Attenuator_Menu_Label_17: [Al 6.5mm] {17}

##Attenuator_Menu_Label_18: [Pb 0.1mm] {18}

##Attenuator_Menu_Label_19: [Pb 1.0mm] {19}

##Attenuator_Menu_Label_20: [Auto] {20}

###

##_attenuator_end:

#

_attenuator_begin:

#

_attenuator_unit_begin:

_attenuator_unit_comment: attenuator unit1

ttenuator1_0: Al 0um

Attenuator1_1: Al 25um

Attenuator1_2: Al 50um

Attenuator1_3: Al 100um

Attenuator1_4: Al 200um

Attenuator1_5: Al 300um

Attenuator1_6: Al 400um

Attenuator1_7: Al 500um

Attenuator1_8: Al 600um

Attenuator1_9: Al 700um

Attenuator1_10: Al 800um

Attenuator1_11: Al 900um

Attenuator1_12: Al 1000um

Attenuator1_13: Al 1100um

Attenuator1_14: Al 1200um

Attenuator1_15: Al 1300um

Attenuator1_16: Al 1400um

Attenuator1_17: Al 1500um

Attenuator1_18: Al 1600um

Attenuator1_19: Al 1700um

Attenuator1_20: Al 1800um

Attenuator1_21: Al 1900um

Attenuator1_22: Al 2000um

Attenuator1_23: Al 2100um

Attenuator1_24: Al 2200um

Attenuator1_25: Al 2300um

Attenuator1_26: Al 2400um

Attenuator1_27: Al 2500um

Attenuator1_28: Al 2600um

Attenuator1_29: Al 3000um

Attenuator1_30: Al 3500um

Attenuator1_31: Al 6500um

Attenuator1_32: Pb 100um

Attenuator1_33: Pb 1000um

Attenuator1_34: Au 10um

Attenuator1_35: Al 0um

Attenuator1_36: Auto

_attenuator_unit_end:

#

Attenuator_Menu_Label_0: [None] {0}

Attenuator_Menu_Label_1: [Al 0.025mm] {1}

Attenuator_Menu_Label_2: [Al 0.050mm] {2}

Attenuator_Menu_Label_3: [Al 0.100mm] {3}

Attenuator_Menu_Label_4: [Al 0.200mm] {4}

Attenuator_Menu_Label_5: [Al 0.300mm] {5}

Attenuator_Menu_Label_6: [Al 0.400mm] {6}

Attenuator_Menu_Label_7: [Al 0.500mm] {7}

Attenuator_Menu_Label_8: [Al 0.600mm] {8}

Attenuator_Menu_Label_9: [Al 0.700mm] {9}

Attenuator_Menu_Label_10: [Al 0.800mm] {10}

Attenuator_Menu_Label_11: [Al 0.900mm] {11}

Attenuator_Menu_Label_12: [Al 1.000mm] {12}

Attenuator_Menu_Label_13: [Al 1.100mm] {13}

Attenuator_Menu_Label_14: [Al 1.200mm] {14}

Attenuator_Menu_Label_15: [Al 1.300mm] {15}

Attenuator_Menu_Label_16: [Al 1.400mm] {16}

Attenuator_Menu_Label_17: [Al 1.500mm] {17}

Attenuator_Menu_Label_18: [Al 1.600mm] {18}

Attenuator_Menu_Label_19: [Al 1.700mm] {19}

Attenuator_Menu_Label_20: [Al 1.800mm] {20}

Attenuator_Menu_Label_21: [Al 1.900mm] {21}

Attenuator_Menu_Label_22: [Al 2.000mm] {22}

Attenuator_Menu_Label_23: [Al 2.100mm] {23}

Attenuator_Menu_Label_24: [Al 2.200mm] {24}

Attenuator_Menu_Label_25: [Al 2.300mm] {25}

Attenuator_Menu_Label_26: [Al 2.400mm] {26}

Attenuator_Menu_Label_27: [Al 2.500mm] {27}

Attenuator_Menu_Label_28: [Al 2.600mm] {28}

Attenuator_Menu_Label_29: [Al 3.000mm] {29}

Attenuator_Menu_Label_30: [Al 3.500mm] {30}

Attenuator_Menu_Label_31: [Al 6.500mm] {31}

Attenuator_Menu_Label_32: [Pb 0.100mm] {32}

Attenuator_Menu_Label_33: [Pb 1.000mm] {33}

Attenuator_Menu_Label_34: [Au 0.010mm] {34}

Attenuator_Menu_Label_35: [None] {35}

Attenuator_Menu_Label_36: [Auto] {36}

#

_attenuator_end:

#

#  ------------------------------------------------

#    _/_/_/ Remote PLC Control _/_/_/

#  ------------------------------------------------

#

Remote_PLC_Control: No

Close_Shutters_After_Experiment: yes

#

#

#  ------------------------------------------------

#    _/_/_/ Printer Name _/_/_/

#  ------------------------------------------------

#

Printer_Name: lp

#

#

#  ------------------------------------------------

#    _/_/_/ Shutter _/_/_/

#  ------------------------------------------------

Shutter_Backlight_Condition:none

#

#  ------------------------------------------------

#    _/_/_/ Light1 _/_/_/

#  ------------------------------------------------

#

Light_1_On_Position:210.

##Light_1_Off_Position:210.0 # 191002 For Helical scan check

Light_1_Off_Position:-11.5 

#

Light_Collide_Cameralength: 210.

#Light_Collide_Cameralength: 200.

#Light_1_On_Position: 220.25

#Light_1_Off_Position: 304.25

#Light_1_Off_Position: 353.0

#

#

#  ------------------------------------------------

#    _/_/_/ SSD1 _/_/_/

#  ------------------------------------------------

#

Ssd_1_On_Position: 60.0

Ssd_1_Off_Position: 25.0

#Ssd_1_Off_Position: 10.0

#

#  ------------------------------------------------

#    _/_/_/ Beam stop _/_/_/

#  ------------------------------------------------

#

# In phi0.7mm straight beamstopper, the On_position and Evacuate_Y_Position values must input each value at x=20.

Beam_Stop_1_On_Position: -8.037

#Beam_Stop_1_Off_Position: -214.

Beam_Stop_1_Off_Position: -190.

Beam_Stop_Evacuate_X_Position: 20

#Beam_Stop_Evacuate_X_Position: 30

Beam_Stop_Evacuate_Y_Position: -2.278

Beam_Stop_Min_Diatance_to_Detector: 80.

#Beam_Stop_Min_Diatance_to_Detector: 75.   #091125

#Beam_Stop_Min_Diatance_to_Detector: 125.	#DIP6040

#091006 straight stopper 0.7mm

#Beam_Stop_1_On_Position: -1.942

#Beam_Stop_1_Off_Position: -227.

#Beam_Stop_Evacuate_X_Position: 16

#Beam_Stop_Evacuate_Y_Position: -1.122

#Beam_Stop_Min_Diatance_to_Detector: 105.

#Beam_Stop_Collide_Cameralength: 500

#SmarGon_Z#

#

#  ------------------------------------------------

#    _/_/_/ Stage-Backlight _/_/_/

#  ------------------------------------------------

Stage_Backlight_Condition: off



#  ------------------------------------------------

#    _/_/_/ Collimator _/_/_/

#  ------------------------------------------------

#Collimator_1_On_Position: -8.0

#Collimator_1_Off_Position: -15.0

# Position_1: insert 1st, evacuate 2nd: col_1_x

# Position_2: insert 2nd, evacuate 1st:col_1_z

# Normal

Collimator_1_On_Position:  -75.0745

##Collimator_1_On_Position:  -40.0 #191002 For Helical scan check

Collimator_1_Off_Position:  -40.0

#

Collimator_2_On_Position:  -4.500000

Collimator_2_Off_Position:  -4.500000

#

#  ------------------------------------------------

#    _/_/_/ Detector cover _/_/_/

#  ------------------------------------------------

Camera_Cover_1_on_Possition:2.83

Camera_Cover_1_off_Possition:372.0

#

#  ------------------------------------------------

#    _/_/_/ Detector evacuation  _/_/_/

#  ------------------------------------------------

Evacuate_Camera_Distance1: 800

#Evacuate_Camera_Distance1: 450

#

#  ------------------------------------------------

#    _/_/_/ Microscope _/_/_/

#  ------------------------------------------------

#

#Microscope_Max_Zoom_Position: -300

#Microscope_Min_Zoom_Position: -13500. 

# Microscope_Min_Zoom_Position: -3000. 

#Microscope_Max_Zoom_Ratio:9.

#Microscope_Min_Zoom_Ratio:0.8

#Microscope_Zoom_Options: -300 -13500.

Microscope_Zoom_Options: 49300 18000

# Microscope_Min_Zoom_Ratio:7.2

#

#  ------------------------------------------------

#    _/_/_/ Cryo-stream _/_/_/

#  ------------------------------------------------

#

# Normal&SPACE

#Cryostream_1_On_Position: 9.0  # 160907made(20KCRYO) no atai

#Cryostream_1_Off_Position: 13.0

Cryostream_1_On_Position: -10.5 #191002kara(4KCRYO) sample kara 8.5mm no ichi

#Cryostream_1_On_Position: -6.0 # For SPACE test

Cryostream_1_Off_Position: -6.0   #191002 sample kara 13.0mm no ichi

#

#---------------------------------------------------------------------

#       Table of beam stop position

#

#  1: camera distance (mm), 2: beam stop position (mm)

#---------------------------------------------------------------------

#_beamstop_table_begin

#_beamstop_position: 150. 15.

#_beamstop_position: 200. 20.

#_beamstop_position: 300. 30.

#_beamstop_position: 450. 45.

#_beamstop_position: 550. 55.

#_beamstop_position: 600. 60.

#_beamstop_table_end

#

#

#---------------------------------------------------------------------

#       Calibration line for calculating beamstop y & z position

#

#	y = a * x + b

#	z = a * x + b

#

#	x: x position of beamstop (mm)

#	y,z: y & z position of beamstop (mm)

#	a: slope of the calibration line

#	b: intercept of the calibration line

#---------------------------------------------------------------------



#231001

_beamstop_calibration_line_begin:

_beamstop_y_slope: -0.00348333

_beamstop_y_intercept: -2.20833

_beamstop_z_slope:  0.000466667

_beamstop_z_intercept: -8.04633

_beamstop_calibration_line_end:



#230511

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00375

#_beamstop_y_intercept: -0.707

#_beamstop_z_slope:  0.0007

#_beamstop_z_intercept: -8.3435

#_beamstop_calibration_line_end:





#230408

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00363333

#_beamstop_y_intercept: -0.715333

#_beamstop_z_slope:  0.0007

#_beamstop_z_intercept: -8.337

#_beamstop_calibration_line_end:



#230116

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00341667

#_beamstop_y_intercept: -0.709667

#_beamstop_z_slope:  0.000658333

#_beamstop_z_intercept: -8.38117

#_beamstop_calibration_line_end:



#221130

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00361667

#_beamstop_y_intercept: -0.832667

#_beamstop_z_slope:  0.000583333

#_beamstop_z_intercept: -8.30367

#_beamstop_calibration_line_end:



#221004

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00383333

#_beamstop_y_intercept: -0.833333

#_beamstop_z_slope:  0.00015

#_beamstop_z_intercept: -8.434

#_beamstop_calibration_line_end:

#220707

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00401667 

#_beamstop_y_intercept: -0.828667

#_beamstop_z_slope:  0.000133333

#_beamstop_z_intercept: -8.37567

#_beamstop_calibration_line_end:



#220701

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00375

#_beamstop_y_intercept: -0.832

#_beamstop_z_slope:  0.000266667

#_beamstop_z_intercept: -8.34533

#_beamstop_calibration_line_end:



#220606

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: 0.00005

#_beamstop_y_intercept: -1.085

#_beamstop_z_slope:  0.0003

#_beamstop_z_intercept: -6.768

#_beamstop_calibration_line_end:



#220511

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00358333

#_beamstop_y_intercept: -0.896333

#_beamstop_z_slope:  0.000133333

#_beamstop_z_intercept: -6.57067

#_beamstop_calibration_line_end:



#220511_2

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00411667

#_beamstop_y_intercept: -0.853667

#_beamstop_z_slope:  0.000116667

#_beamstop_z_intercept: -6.38667

#_beamstop_calibration_line_end:



#220409

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00425

#_beamstop_y_intercept: -0.865

#_beamstop_z_slope:  -0.00191667

#_beamstop_z_intercept: -6.38667

#_beamstop_calibration_line_end:







#210510-BS1

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00433333

#_beamstop_y_intercept: -0.652333

#_beamstop_z_slope:  0.000416667

#_beamstop_z_intercept: -6.43333

#_beamstop_calibration_line_end:







#210510-BS3

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00365

#_beamstop_y_intercept: -1.108

#_beamstop_z_slope:  0.000233333

#_beamstop_z_intercept: -6.25267

#_beamstop_calibration_line_end:



#210405

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00405

#_beamstop_y_intercept: -0.568

#_beamstop_z_slope:  0.000416667

#_beamstop_z_intercept: -6.04633

#_beamstop_calibration_line_end:

#210405-2

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00423333

#_beamstop_y_intercept: -0.986333

#_beamstop_z_slope:  0.0003

#_beamstop_z_intercept: -5.967

#_beamstop_calibration_line_end:





#210120-2

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00413333

#_beamstop_y_intercept: -0.891333 

#_beamstop_z_slope:  0.000433333

#_beamstop_z_intercept: -6.22867

#_beamstop_calibration_line_end:



#210120

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00308333

#_beamstop_y_intercept: 0.278

#_beamstop_z_slope:  0.0003

#_beamstop_z_intercept: -6.146

#_beamstop_calibration_line_end:

#

#210119

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00393333

#_beamstop_y_intercept: -0.216333

#_beamstop_z_slope:  0.0003

#_beamstop_z_intercept: -5.486

#_beamstop_calibration_line_end:



#201013_2

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00436667

#_beamstop_y_intercept: -0.924667

#_beamstop_z_slope:  0.000433333

#_beamstop_z_intercept: -6.03867

#_beamstop_calibration_line_end:



#201013

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00436667

#_beamstop_y_intercept: -0.924667

#_beamstop_z_slope:  0.0046

#_beamstop_z_intercept: -6.372

#_beamstop_calibration_line_end:





#200930

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.004

#_beamstop_y_intercept: -0.909

#_beamstop_z_slope:  0.000483333

#_beamstop_z_intercept: -6.06367

#_beamstop_calibration_line_end:





#200725

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00415

#_beamstop_y_intercept: -2.066

#_beamstop_z_slope:  -0.000216667

#_beamstop_z_intercept: -4.18367

#_beamstop_calibration_line_end:



#200716_2

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00393333

#_beamstop_y_intercept: -2.09133

#_beamstop_z_slope:  -0.000033333

#_beamstop_z_intercept: -4.18833

#_beamstop_calibration_line_end:



#200716

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00416667

#_beamstop_y_intercept: -2.19767

#_beamstop_z_slope:  0.0065

#_beamstop_z_intercept: -4.324

#_beamstop_calibration_line_end:



#200714

#_beamstop_calibration_line_begin:

#_beamstop_y_slope: -0.00401667

#_beamstop_y_intercept: -2.32367

#_beamstop_z_slope:  0.000233333

#_beamstop_z_intercept: -5.70667

#_beamstop_calibration_line_end:



#  ------------------------------------------------

#    _/_/_/ Debug mode flag  _/_/_/

#  ------------------------------------------------

#

Debug_Mode: no

#

#

#  -----------------------------------------------

#    _/_/_/ Insertion Device  _/_/_/

#  -----------------------------------------------

# Relation between E(keV) and ID gap (mm) is approximated by

#    ID Gap = P1 * ln(P2/E - 1) + P3

ID_Coeff_P1:-5.01107

ID_Coeff_P2:18.7587

#For_High_En_high_reso

#ID_Coeff_P3:13.10618

#original_value

ID_Coeff_P3:14.112

#

# --- For 7GeV

#ID_Coeff_P1:-5.03991

#ID_Coeff_P2:14.4925

#ID_Coeff_P3:14.1056

# --- end

#

# --- For 7GeV for 3rd

#ID_Coeff_P1:-5.03991

#ID_Coeff_P2:43.4775

#ID_Coeff_P3:14.1056

# --- end

#

#

Counter1_Channel:0

#

#

  -----------------------------------------------

#    _/_/_/ Goniometer Oscillation Condition _/_/_/

#  -----------------------------------------------

Osc_Speed_Lower_Limit: 100

Osc_Step_Lower_Limit: 0.001

#Osc_Speed_Lower_Limit: 50

#Osc_Speed_Upper_Limit: 16000

#Osc_Speed_Upper_Limit: 4000000

Osc_Speed_Upper_Limit: 67000

Oneway_Max_Exposure_Time:0.19

#Oneway_Max_Exposure_Time:0.001

#Oneway_Max_Exposure_Time:5.0

Osc_Turnover_Time:50.0

#Osc_Turnover_Time:100.0

Osc_Accel_Upper_Limit:0

Osc_Initial_Speed:1

#Osc_Speed_Lower_Limit: 100

#Osc_Speed_Lower_Limit: 50

#Osc_Speed_Upper_Limit: 16000

#Osc_Speed_Upper_Limit: 4000000

#Oneway_Max_Exposure_Time:0.19

#Oneway_Max_Exposure_Time:30.1

#Osc_Turnover_Time:1000.0

Osc_Offset_Time:21.0

Osc_Offset_Time_1:21.0

Osc_Offset_Time_2:0.0

Osc_Offset_Time_d:0

#  ------------------------------------------------

#    _/_/_/ Directory permission  _/_/_/

#  ------------------------------------------------

Directory_Permission: 750

#

#  ------------------------------------------------

#for intensity logging

#  ------------------------------------------------

_axis_begin:

_axis_comment: intensity logging used in scantool

_axis_name:intensity_logging

_sunit:sec

_axis_end:

#

#  ------------------------------------------------

#    _/_/_/ etc  _/_/_/

#  ------------------------------------------------

#

Light_Position_Increment:2.0

#

#Tune_like_BL41XU:n

Tune_like_BL41XU:y

#

XFEL_Test_Mode:n

#

Disable_Auto_Centering: y

#

#Evacuate_after_Measurement:n

#

#Disable_Evacuation_after_Diffraction_Scan:n

#

File_Numbering_Digits: 6

#_Menu_Time_Digits: 2

#_Menu_Angle_Digits: 3

#

#Set_Auto_Directory_Default:y

#

#Set_Attenuator_by_Transmission:y

#

#Set_Beamsize_in_Job: n

#

#

#  ------------------------------------------------

#    _/_/_/ Shutterless scan conditions  _/_/_/

#  ------------------------------------------------

#

_Shutterless_Scan_Speed_Limits:65535,655350, 6553500

## This value of 1.0 is also okay 170517 see Note17 p95

_Shutterless_Scan_Takeoff_Coefficient:1.0

#_Shutterless_Scan_Takeoff_Coefficient:0.97

_Shutterless_Scan_Initial_Speed:1

#Shutterless_Scan_Initial_Speed:10 #airbear

#_Shutterless_Scan_Delay_Time:800   #220426

_Shutterless_Scan_Delay_Time:200   #220419

#_Shutterless_Scan_Delay_Time:400  #220419moto

#_Shutterless_Scan_Delay_Time:100

_Shutterless_Scan_Offset_Time:12.0

#_Shutterless_Scan_Offset_Time:30.5 #airbear

_Shutterless_Scan_Offset_Time_1:12.0

#_Shutterless_Scan_Offset_Time_1:30.5 #airbear

_Shutterless_Scan_Offset_Time_2:0.0

_Shutterless_Scan_Offset_Time_d:0

## This value of 0.0 is also okay 170517 see Note17 p95

_Shutterless_Scan_Readout_Time:-10.75

#_Shutterless_Scan_Readout_Time:-8 #airbear

#

#  ------------------------------------------------

#  _/_/_/ twobrade shutter mode mode _/_/_/

#  ------------------------------------------------

TwoBrade_Shutter:y

#  ------------------------------------------------

#    _/_/_/ Diffraction scan ZigZag test mode _/_/_/

#  ------------------------------------------------

#

Test0_Mode: y

Test1_Mode: y

#

# for SmarGon

Ignore_Axis_Initialization:y

#

#



#============ECHA TEST=============



#Echa_API_Server: http://dcha-spx.spring8.or.jp:3001/api1.0.2

#Echa_Facility_Name: SPring-8

#Echa_Beamline_Name: BL44XU

#Echa_Force_User_Name:users44

#Echa_Force_User_Password:bl44xu@sp8



#===================================

##############################
##############################
