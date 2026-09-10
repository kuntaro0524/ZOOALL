#!/bin/env python
import sys
import os
import socket
import time
import datetime


# BLFactory
import BLFactory

blf = BLFactory.BLFactory()
blf.initDevice()

# prep measureFlux
blf.device.prepScan()
flux = blf.device.measureFlux()
blf.device.finishScan()

print(f"Flux: {flux} phs/sec")
