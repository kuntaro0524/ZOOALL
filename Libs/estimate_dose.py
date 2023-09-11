import sys, os, math, time, tempfile, datetime
import Raddose

if __name__ == "__main__":
    e = Raddose.Raddose()

    #print len(sys.argv)
    if len(sys.argv) != 5:
        print("wavelength flux beam_h beam_v")
        sys.exit(0)
    else:
        # 160509 wl=1.0A 10x15 um
        wavelength = float(sys.argv[1])
        flux = float(sys.argv[2])
        beam_h = float(sys.argv[3])
        beam_v = float(sys.argv[4])

    energy = 12.3984 / wavelength
    dose = e.getDose(beam_h, beam_v, flux, 1.0, energy=energy)
    for exptime in [1.0, 0.5, 0.05, 0.02, 0.01]:
        e_dose = dose * exptime
        print("%8.3f sec %8.1f %8.3f MGy (oxidase)" % (exptime, energy, e_dose))

    exp_10MGy = 10.0 / dose
    print("10 MGy dose -> Exposure time = %8.4f [sec]" % exp_10MGy)
    print("Photons/frame = %5.3e" % (exp_10MGy * flux))