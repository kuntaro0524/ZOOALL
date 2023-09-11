import os,sys, logging, logging.config
import numpy as np
import BSSconfig, AttFactor

# Balance exposure time

class ExposureConditioner():

    def __init__(self, blconfig_file):
        self.blconfig_file = blconfig_file
        self.attfactor_class = AttFactor.AttFactor()
        self.logger = logging.getLogger('ZOO').getChild("ExpConds")
        self.flag_integer_freq = True

    def balanceExposure(self, wavelength, exptime, transmission, isRaster=True):
        # constant value
        constant = exptime * transmission

        # if input transmission is 1.0 -> no need to modify exposure condition
        if transmission == 1.0:
            self.logger.info("No need to modify the exposure condition!")
            new_exptime = exptime

        else:
            # check if attenuator thickness is available or not
            self.bssconfig_class = BSSconfig.BSSconfig()
            thinnest_att_um = self.bssconfig_class.getThinnestAtt()

            # Check transmission
            trans_at_thinnest = self.attfactor_class.calcAttFac(wavelength, thinnest_att_um)
            self.logger.info("Input    transmission= %9.5f " % transmission)
            self.logger.info("Thinnest transmission= %9.5f " % trans_at_thinnest)

            # Compare transmission of 'input' and 'calculated from thinnest thickness'
            if trans_at_thinnest < transmission:
                self.logger.info("Thickness is over than transmission.")
                elongate_ratio = transmission / trans_at_thinnest
                self.logger.info("Elongation factor : %8.5f " % elongate_ratio)
                if elongate_ratio > 2.0 and isRaster==True:
                    self.logger.info("Elongated time is over than 2.0...But continued")
                new_exptime = exptime * elongate_ratio
                self.logger.info("Elongated exposure time: %8.5f [sec] (original %8.5f[sec]" % (new_exptime, exptime))
            else:
                self.logger.info("No modifications are required by considering 'thinnest thickness of attenuator'")
                new_exptime = exptime
                trans_at_thinnest = transmission

        if self.flag_integer_freq:
            good_exptime, final_freq = self.calculateGoodExpTime(new_exptime)
            mod_add = constant / good_exptime
            if mod_add > 1.0:
                mod_add = 1.0
                curr_mult = good_exptime * mod_add
                diff_mult = curr_mult - constant
                change_ratio = diff_mult / constant *100.0
                self.logger.info("Change ratio= %9.5f perc." % change_ratio)

            self.logger.info("The final exposure time and transmission %9.6f sec(freq. %5d) / %8.5f[percent]" % (good_exptime, final_freq, mod_add))

        return mod_add, good_exptime, final_freq

    def calculateGoodExpTime(self, exptime):
        # allowed frequency of detector
        allowed_freq = np.arange(1,201)
        # current frequency
        curr_freq = 1.0 / exptime

        for chk_index, start in enumerate(allowed_freq):
            if chk_index == len(allowed_freq)-1:
                break
            start_freq = start
            end_freq = allowed_freq[chk_index+1]
            # print(start_freq, end_freq)

            if start_freq < curr_freq <= end_freq:
                break

        # 2020/11/02 Thinner attenuation factor should be selected.
        # Reasons: if an ideal value of attenuator thickness is between 100% ~ transmission of 'thinnest' attenuator thickness
        # we should evaluate 'transmission' again by self.balanceExposure. Its quite stupid.
        # A thicker attenuator will give 'transmission' larger than 100%. But it is not avoidable on current BSS.
        final_freq = allowed_freq[chk_index+1]
        good_exptime = 1.0 / allowed_freq[chk_index+1]

        self.logger.info("The integer frequency for input %5d" % (final_freq))

        return good_exptime, final_freq

if __name__ == "__main__":

    logname = "logfile.txt"
    beamline="BL32XU"
    logger = logging.getLogger('ZOO')
    logging.config.fileConfig('/isilon/%s/BLsoft/PPPP/10.Zoo/Libs/logging.conf' % beamline, defaults={'logfile_name': logname})
    logger = logging.getLogger('ZOO')

    expcon = ExposureConditioner("/isilon/blconfig/bl32xu/bss/bss.config")
    a,b,c = expcon.balanceExposure(1.0, 0.12213, 1.0, isRaster=True)

    print((a,b,c))
    # print expcon.calculateGoodExpTime(0.01112222)