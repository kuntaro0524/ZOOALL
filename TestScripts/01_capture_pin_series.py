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
    bright_list = np.arange(500, 4000, 200)

    for brightness in bright_list:
        blf.device.capture.setBright(brightness)
        # make a filename with 'brightness'
        filename = fileroot + '/pin_' + str(brightness) + '.ppm'
        blf.device.capture.capture(filename)
        time.sleep(0.5)
