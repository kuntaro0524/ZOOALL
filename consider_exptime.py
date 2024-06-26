import sys, os, math
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")

import BeamsizeConfig
import AttFactor
import KUMA

if len(sys.argv) != 3:
    print "Usage: python consider_exptime.py BEAM_H[um] BEAM_V[um] DESIRED_DOSE[MGy] WAVELENGTH[A] NFRAMES DESIRED_EXPTIME[SEC]"

beam_h = float(sys.argv[1])
beam_v = float(sys.argv[2])
dose = float(sys.argv[3])
wl = float(sys.argv[4])
nframes = int(sys.argv[5])
exp_time = float(sys.argv[6])

# Get Flux
config_dir="/isilon/blconfig/bl45xu/"
beamsizeconf=BeamsizeConfig.BeamsizeConfig(config_dir)

flux_list=beamsizeconf.getFluxListForKUMA()
index=beamsizeconf.getBeamIndexHV(beam_h,beam_v)
flux=flux_list[index]

kuma = KUMA.KUMA()
exp_time_limit = kuma.convDoseToExptimeLimit(dose,beam_h,beam_v,flux,wl)

attfac=AttFactor.AttFactor()
print "Flux density=  %5.2e [phs/sec/um^2]" % (flux/beam_h/beam_v)
print "DOSE=          %5.2f [MGy]" % dose
print "EXP_LIMIT=     %5.2f [sec]" % exp_time_limit
print "N_FRAMES=      %5d" % nframes
print "EXP_TIME=      %5.2f [sec]" % exp_time

best_transmission=exp_time_limit/float(nframes)/exp_time
print "BEST TRANS  %8.3f" % best_transmission

if best_transmission > 1.0:
    att_idx = 0
    exp_time_after = exp_time_limit / float(nframes)
    print "Exposure time was replaced by %8.3f sec" % exp_time_after
    print "Measurement time will be longer than the initial condition"
    print "Initial data collection time: %8.2f [sec]" % (exp_time * float(nframes))
    print "Current data collection time: %8.2f [sec]" % (exp_time_after * float(nframes))
else:
    best_thick=attfac.getBestAtt(wl,best_transmission)
    print "Suggested Al thickness = %8.1f[um]"%best_thick
    att_idx=attfac.getAttIndexConfig(best_thick)
