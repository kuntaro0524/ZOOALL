import sys,math,numpy,os
from configparser import ConfigParser, ExtendedInterpolation
# from MyException import *
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
# ファイルと標準出力
logging.getLogger().addHandler(logging.FileHandler("koba_make_schedule.log"))
#logging.getLogger().addHandler(logging.StreamHandler())

if __name__ == "__main__":
    gonio_xyz = [-1.6280, 0.1977, -0.8195]
    start_omega = -40
    end_omega = 40
    delta_omega = 1.0

    omega_centre = (start_omega + end_omega) / 2.0
    logging.info(f"omega_centre: {omega_centre}")
    # cover area [um]
    v_cover = 50.0
    h_cover = 50.0

    # directory 
    dire = "sample03"
    prefix="data"

    # setup
    h_step = 5.0
    v_step = 5.0

    # attenuator transmission
    attenuator = 0.0126775

    # step inclined [mm]
    logging.info(f"omega_centre: {omega_centre}")

    dx = v_step * np.sin(np.radians(omega_centre)) / 1000.0
    dz = v_step * np.cos(np.radians(omega_centre)) / 1000.0
    print(f"dx={dx}, dz={dz}")

    logging.info(f"dx: {dx}, dz: {dz}")

    # number of steps
    # scan length
    # vertical scan points
    nv = int(v_cover / v_step) 
    nh = int(h_cover / h_step) 

    logging.info(f"nv: {nv}, nh: {nh}")

    # start x,y,z
    x0 = gonio_xyz[0] - float(int(nv/2)) * dx
    y0 = gonio_xyz[1] - float(int(nh/2)) * h_step/1000.0
    z0 = gonio_xyz[2] - float(int(nv/2)) * dz

    logging.info(" gonio x y z")
    logging.info(gonio_xyz)
    
    logging.info(f"x0: {x0}, y0: {y0}, z0: {z0}")

    crystal_index =0
    advanced_xyz_strings = ""
    for i in range(nh):
        for j in range(nv):
            x = x0 + float(j) * dx
            y = y0 + float(i) * h_step/1000.0
            z = z0 + float(j) * dz
            crystal_index+=1
            advanced_xyz_strings+="Advanced gonio coordinates %d: %f %f %f\n" % (crystal_index,x,y,z)
            logging.info(f"crystal_index: {crystal_index}, x: {x:10.5f}, y: {y:10.5f}, z: {z:10.5f}")
    ## number of crystal
    n_crystal = crystal_index
    ## input dictionary value to schedule_string
    schedule_string = f"""Job ID: 0
Status: 0 # -1:Undefined  0:Waiting  1:Processing  2:Success  3:Killed  4:Failure  5:Stopped  6:Skip  7:Pause
Job Mode: 0 # 0:Check  1:XAFS  2:Single  3:Multi
Crystal ID: unknown
Tray ID: Not Used
Well ID: 0 # 0:Not Used
Cleaning after mount: 0 # 0:no clean, 1:clean
Not dismount: 0 # 0:dismount, 1:not dismount
Data Directory: /user/target/Data/BL32XU_241028_Kobayashi/{dire}/data/
Sample Name: {prefix}
Serial Offset:     0
Number of Wavelengths: 1
File Name Suffix: h5
Detector Setup Level: 10
Shutterless measurement: 1 # 0:no, 1:yes
Exposure Time:   1.0000 1.000000 1.000000 1.000000 # [sec]
Direct XY: 2000.000000 2000.000000 # [pixel]
Wavelength:   0.6199 1.020000 1.040000 1.060000 # [Angstrom]
Centering: 3 # 0:Database  1:Manual  2:Auto  3:None
Detector: 0 # 0:CCD  1:IP
Scan Condition:   {start_omega}   {end_omega}  {delta_omega}  # from to step [deg]
Scan interval: 1 # [points]
Wedge number: 1  # [points]
Wedged MAD: 1  #0: No   1:Yes
Start Image Number: 1
Goniometer: 0.00000 0.00000 0.00000 0.00000 0.00000 #Phi Kappa [deg], X Y Z [mm]
CCD 2theta: 0.000000  # [deg]
Detector offset: 0.0 0.0  # [mm] Ver. Hor.
Camera Length:  110.000  # [mm]
IP read mode: 1  # 0:Single  1:Twin
CMOS frame rate: -1.000000  # [frame/s]
Beam Size: 0 # beam size is current one.
CCD Binning: 1  # 1:1x1  2:2x2
CCD Adc: 0  # 0:Normal  1:High gain 2:Low noise 3:High dynamic
CCD Transform: 1  # 0:None  1:Do
CCD Dark: 1  # 0:None  1:Measure
CCD Trigger: 0  # 0:No  1:Yes
CCD Dezinger: 0  # 0:No  1:Yes
CCD Subtract: 1  # 0:No  1:Yes
CCD Thumbnail: 0  # 0:No  1:Yes
CCD Data Format: 0  # 0:d*DTRK  1:RAXIS
Oscillation delay:   100.00  # [msec]
Anomalous Nuclei: Mn  # Mn-K
XAFS Mode: 0  # 0:Final  1:Fine  2:Coarse  3:Manual
Attenuator transmission: {attenuator}  # [mm]
XAFS Condition: 1.891430 1.901430 0.000100  # from to step [A]
XAFS Count time: 1.000000  # [sec]
XAFS Wait time: 30  # [msec]
Transfer HTPFDB: 0  # 0:No, 1:Yes
Number of Save PPM: 0
Number of Load PPM: 0
PPM save directory: /tmp
PPM load directory: /tmp
Comment:
Advanced mode: 3 # 0: none, 1: vector centering, 2: multiple centering, 3: multi-crystals
Advanced npoint: {n_crystal} # [mm]
Advanced step: 0.00000 # [mm]
Advanced interval: 1 # [frames]
Advanced shift: 0 # flag for shift
Advanced shift speed: 0.000000 # [mm/sec]
{advanced_xyz_strings}
Raster Scan Type: 2 # 0:vertical, 1:horizontal, 2: 2D
Raster Vertical Points: 10
Raster Horizontal Points: 10
Raster Vertical Step: 0.0150 # [mm]
Raster Horizontal Step: 0.0100 # [mm]
Raster Vertical Center: 0.0000 # [mm]
Raster Horizontal Center: 0.0000 # [mm]
Raster Rotation Flag: 0 # 0:not rotate, 1:rotate
Raster Rotation Range: 0.000 # [deg] rotation range
Raster Zig-Zag Flag: 1 # 0: off, 1:on
Comment:"""
    
    # write to file
    with open(f"./koba.sch", "w") as f:
        f.write(schedule_string)
