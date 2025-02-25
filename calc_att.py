import AttFactor

exp_time_limit = 1.5
n_frames = 100
exp_time = 0.05
wavelength = 1.0

attfac=AttFactor.AttFactor()
print "EXP_LIMIT=    ",exp_time_limit
print "N_FRAMES=     ",n_frames
print "EXP_TIME=     ",exp_time

best_transmission=exp_time_limit/float(n_frames)/exp_time
print "BEST TRANS=", best_transmission

if best_transmission > 1.0:
    att_idx = 0
    exp_time = exp_time_limit / float(n_frames)
    print "Exposure time was replaced by %8.3f sec" % exp_time

else:
    best_thick=attfac.getBestAtt(wavelength,best_transmission)
    print "Suggested Al thickness = %8.1f[um]"%best_thick
    att_idx=attfac.getAttIndexConfig(best_thick)
