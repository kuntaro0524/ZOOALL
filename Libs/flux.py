import sys,os,math,numpy,socket
import Device
import Flux

#host = '172.24.242.41'
# BL44XU
host = '172.24.242.57'
port = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

dev=Device.Device(s)
dev.init()
energy = dev.mono.getE()

ipin,iic=dev.countPin(pin_ch=3)

print("IPIN",ipin)

pin_uA=ipin/100.0
iic_nA=iic/100.0

# E=12.3984 keV 
# 2.72924+09 photons/1uA
f = Flux.Flux(energy)
photon_flux=f.calcFluxFromPIN(pin_uA)

print("IC=%7.1f nA PIN=%8.2f uA %8.2e phs/sec"%(iic_nA,pin_uA,photon_flux))
