import sys,os
import AttFactor

att=AttFactor.AttFactor()
wl=1.0

start_phi=0
end_phi=180
osc_width=0.1

flux_beam=2.0E13
total_photons=7.0E11

# total oscillation range
total_osc=end_phi-start_phi

# Multi conditions
n_frames=int(total_osc/osc_width)
print(n_frames)

# Total photons/frame
phs_per_frame=total_photons/float(n_frames)
print("Aimed flux/frame: %5.2e"%(phs_per_frame))

# Exposure time for full flux
ff_exptime=phs_per_frame/flux_beam
print("Full flux exposure time for aimed flux=%13.8f sec/frame"%ff_exptime)

# Suitable exposure time range
# 5 deg/frame FIXED
exptime=osc_width/5.0
print("Attenuation factor for 1sec exposure/frame",ff_exptime/exptime)
transmission=ff_exptime/exptime
print(transmission)

# Suitable attenuation factor
att_thick=att.getBestAtt(wl,transmission)
trans=att.calcAttFac(wl,att_thick)

print("%8.1f[um] Transmission=%12.8f"%(att_thick,trans))

# Final calculation
exptime=ff_exptime/trans

att_idx=att.getAttIndexConfig(att_thick)

print(att_idx,exptime)
