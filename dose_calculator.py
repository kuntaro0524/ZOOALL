import sys, os, math, time, tempfile, datetime
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")

import Raddose, AttFactor

if __name__ == "__main__":
    e = Raddose.Raddose()

    if len(sys.argv) != 8:
        print "Usage: python dose_calculator.py wavelength[A] BeamH[um] BeamV[um] Flux[phs/sec] AttThick[um] NUM_FRAME[frames] EXP_TIME[sec]"
        sys.exit()

    wavelength = float(sys.argv[1])
    beam_h = float(sys.argv[2])
    beam_v = float(sys.argv[3])
    flux = float(sys.argv[4])
    att_thick = float(sys.argv[5])
    n_frames = int(sys.argv[6])
    exp_time = float(sys.argv[7])

    # Dose for each exposure time
    en  = 12.3984 / wavelength
    # Transmission of X-rays after attenuator.
    attfac = AttFactor.AttFactor()
    trans = attfac.calcAttFac(wavelength,att_thick)
    attenuated_flux = trans * flux
    dose_per_frame = e.getDose(beam_h, beam_v, attenuated_flux, exp_time, energy=en)

    total_dose = dose_per_frame * float(n_frames)

    print ("Dose/frame=%6.3f MGy" % dose_per_frame)
    print ("Total dose=%6.3f MGy" % total_dose)
