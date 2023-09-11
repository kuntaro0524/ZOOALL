import sys, os, math, cv2, socket, time, copy


class Condition:
    def __init__(self, uname, pucks_and_pins, mode, sample_name, wavelength, h_beam, v_beam, raster_exp, osc_width,
                 total_osc,
                 exp_henderson, exp_time, distance, att_raster, shika_minscore, shika_mindist, shika_maxhits, loop_size,
                 helical_hbeam, helical_vbeam, hebi_att, photon_density_limit, ntimes, reduced_fac, offset_angle):
        # adopt init args
        for k, v in list(locals().items()):
            if k == "self": continue
            setattr(self, k, v)
        self._check_errors()
        self.shika_maxscore = 1000

    # __init__()

    def _check_errors(self):
        # comment out 170721 K.Hirata because BSS never mind
        # prohibit_chars = set(" /_*")
        # assert not prohibit_chars.intersection(self.uname)

        assert type(self.pucks_and_pins) == list
        assert all([len(x) == 2 for x in self.pucks_and_pins])
        for puck, pins in self.pucks_and_pins:
            assert type(puck) == str
            # assert not prohibit_chars.intersection(puck)
            assert all([1 <= x <= 16 for x in pins])

    # _check_errors()

    def show(self):
        print(self.uname)
        for pp in self.pucks_and_pins:
            print("", pp)

    def customized_copy(self, **kwds):
        c = copy.copy(self)
        for k, v in list(kwds.items()):
            assert hasattr(c, k)
            setattr(c, k, v)
        self._check_errors()
        return c

    # customized_copy()
    def setFluxPerDataset(self, flux_per_dataset):
        self.flux_per_dataset = flux_per_dataset

    def setBeamsizeList(self, beamsize_list):
        self.beamsize_list = beamsize_list

    def setRotSpeedList(self, rotspeed_list):
        self.rotspeed_list = rotspeed_list

    def setRotSpeed(self, rotspeed):
        self.rot_speed = rotspeed

    # ystep in [um]
    def setYstep(self, ystep):
        if ystep > 1000.0:
            print("Something wrong in setYstep in Condition")
            system.exit(1)
        self.y_step = ystep

    def make_shika_direction(self, scandir):
        ofs = open(os.path.join(scandir, "shika_auto.config"), "w")
        if self.shika_minscore is not None: ofs.write("min_score= %.3f\n" % self.shika_minscore)
        if self.shika_mindist is not None: ofs.write("min_dist= %.3f\n" % self.shika_mindist)
        ofs.close()

    # make_shika_direction()

    def setMixed(self, hel_min_size, hel_max_size, rot_part, rot_full):
        self.hel_min_size = hel_min_size
        self.hel_max_size = hel_max_size
        self.hel_rot_part = rot_part
        self.hel_rot_full = rot_full

    def setShikaMax(self, max_score):
        self.shika_maxscore = max_score


# class Condition

if __name__ == "__main__":
    cond = Condition(uname="lys-1A",
                     pucks_and_pins=[
                         ["CPS0389", [6]],
                     ],
                     mode="study",
                     sample_name="lys",
                     wavelength=1.0000,  # wavelength
                     h_beam=10.0,  # [um square shaped]
                     v_beam=15.0,  # [um square shaped]
                     raster_exp=0.02,  # [sec.] normally 0.02sec
                     osc_width=1.00,  # [deg.]
                     total_osc=180.0,  # [deg.]
                     exp_henderson=0.05,  # [sec] This is not usefull for 'helical data collection'
                     exp_time=0.10,  # do not set 5deg/sec
                     distance=250.0,  # [mm]
                     att_raster=2,  # [%] from 2016/10/04 # Raster attenuator transmission
                     shika_minscore=30,
                     shika_mindist=0,
                     shika_maxhits=100,
                     loop_size="medium",
                     helical_hbeam=2.0,
                     helical_vbeam=15.0,
                     hebi_att=10.0,  # Attenuation factor[%] for finding left/right edges in HEBI
                     photon_density_limit=2E10,
                     ntimes=1,
                     reduced_fac=1.00,
                     offset_angle=0.0,
                     )
    print(cond.reduced_fac)
    cond.setFlux(1E13)
    print(cond.flux)
