import sys
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")
import KUMA

if __name__ == "__main__":
    kuma=KUMA.KUMA()

    dose = 10.0 # [MGy]
    wavelength = 1.0 #[A]
    exptime = 0.01 #[sec]
    total_osc = 180.0 #[deg]
    stepphi = 0.1 #[deg]
    dist_vec = 100.0 #[um]
    phosec_meas = 1.8E13 #[phs/sec]
    beam_vert = 20.0 #[um]

    photon_density_limit=kuma.convDoseToDensityLimit(dose, wavelength)

    for dist_vec in range(50,500,10.0):
        transmission=kuma.estimateAttFactor(exptime,total_osc,stepphi,dist_vec,phosec_meas,beam_vert)
        #print "%e"%photon_density_limit
        print "%5.2f [um] crystal Trans =" % dist_vec, transmission
