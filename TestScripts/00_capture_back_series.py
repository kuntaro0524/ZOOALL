import sys,os,math,socket
import numpy as np
import BLFactory
import time

if __name__ == "__main__":
    blf = BLFactory.BLFactory()
    blf.initDevice()

    fileroot = os.environ['PWD']

    # brightness pattern
    # bright_list: 1000, 2000, 3000, 4000
    bright_list = np.arange(500, 4000, 1000)
    gain_list = np.arange(4000, 20000, 6000)

    for brightness in bright_list:
        for gain in gain_list:
            blf.device.capture.setGain(gain)
            blf.device.capture.setBright(brightness)
            # make a filename with 'brightness'
            filename = fileroot + '/pin_' + str(brightness) + '-' + str(gain) + '.ppm'
            blf.device.capture.capture(filename)
            time.sleep(0.5)