import os,sys
import KUMA
import LoopMeasurement
import BLfactory
    #def genMultiSchedule(self, phi_mid, glist, cond, flux, prefix="multi", same_point=True):

blf = BLfactory.BLFactory()

root_dir = os.path.abspath("./")

lm = LoopMeasurement.LoopMeasurement(blf,root_dir,"multi")

min_score = 20
max_score = 50

# format
# 25: 2d_016555    -1.0636    -1.7850    -0.1174       60.0
gfile = sys.argv[1]
lines = open(gfile,'r').readlines()

glist = []
for line in lines:
    cols = line.split()
    # 1st column: score after rid of ":"
    score = int(cols[0].replace(":",""))
    # id
    scanid = cols[1]
    # x,y,z
    x = float(cols[2])
    y = float(cols[3])
    z = float(cols[4])
    # phi
    phi = float(cols[5])
    glist.append(x,y,z)

phi_mid = 60.0
cond = {
    'ds_hbeam':10.0,
    'ds_vbeam':15.0,
    'dose_ds':10.0,
    'dist_ds':125.0,
    'wavelength':1.0, 
    'exp_ds':0.02, 
    'total_osc':5.0, 
    'osc_width': 0.1, 
    'reduced_fact':1.0, 
    'ntimes':1
}

flux = 5E12

lm.genMultiSchedule(phi_mid,glist,cond,flux,prefix='multi',same_point=True)