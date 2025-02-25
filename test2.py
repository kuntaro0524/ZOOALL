import Libs.StopWatch

sw.setTime("end")
consumed_time=sw.getDsecBtw("start","end")

print consumed_time
#logfile.write("Consuming time for this crystal %5.1f[sec]\n"%(consumed_time))
