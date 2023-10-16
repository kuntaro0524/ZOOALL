import sys, os, math, numpy, socket, time, cv2
import re

import Capture
import logging
from configparser import ConfigParser, ExtendedInterpolation

def read_camera_inf(infin):
    ret = {}
    origin_shift_x, origin_shift_y = None, None
    for l in open(infin):
        if "ZoomOptions1:" in l:
            ret["zoom_opts"] = list(map(float, l[l.index(":") + 1:].split()))
        elif "OriginShiftXOptions1:" in l:
            origin_shift_x = list(map(float, l[l.index(":") + 1:].split()))
        elif "OriginShiftYOptions1:" in l:
            origin_shift_y = list(map(float, l[l.index(":") + 1:].split()))

    # TODO read tvextender

    if None not in (origin_shift_x, origin_shift_y):
        assert len(origin_shift_x) == len(origin_shift_y)
        ret["origin_shift"] = list(zip(origin_shift_x, origin_shift_y))

    return ret
# read_camera_inf()

def read_bss_config(cfgin):
    ret = {}
    for l in open(cfgin):
        if "#" in l: l = l[:l.index("#")]
        if "Microscope_Zoom_Options:" in l:
            ret["zoom_pulses"] = list(map(int, l[l.index(":") + 1:].split()))
    return ret

class CoaxImage:
    def __init__(self, blf):
        # BLFactory instance is passed from the caller
        self.blf = blf

        # Message server port is already opened in BLFactory
        self.ms = self.blf.ms

        self.thread = None
        # Device instance is already initialized in BLFactory
        self.dev = self.blf.device
        print(self.dev.isInit)

        self.logger = logging.getLogger('ZOO').getChild("CoaxImage")

        # configure file を読む
        # Get information from beamline.ini file.
        self.config = self.blf.config
        self.config.read(os.path.join(os.environ["ZOOCONFIGPATH"], "beamline.ini"))

        # camera.inf パスは beamline.ini から取得
        # section: files, option: camera_inf
        self.camera_inf_path = self.config.get("files", "camera_inf")
        # bss.config パスは beamline.ini から取得
        # section: files, option: bssconfig_file
        self.bss_config_path = self.config.get("files", "bssconfig_file")

        # beamline name is extracted from beamline.ini
        # section: beamline, option: beamline
        self.beamline = self.config.get("beamline", "beamline")

        # gonio direction : beamline.local.ini から取得
        self.gonio_direction = self.config.get("experiment", "gonio_direction")

        self.camera_inf = read_camera_inf(self.camera_inf_path)
        self.bss_config = read_bss_config(self.bss_config_path)
        self.coax_pulse2zoom = dict(list(zip(self.bss_config["zoom_pulses"], self.camera_inf["zoom_opts"])))
        self.coax_zoom2pulse = dict(list(zip(self.camera_inf["zoom_opts"], self.bss_config["zoom_pulses"])))
        self.coax_zoom2oshift = dict(list(zip(self.camera_inf["zoom_opts"], self.camera_inf["origin_shift"])))

        # self.config 'coaximage' sectionから数値を読む (beamline.ini)
        self.width = self.config.getfloat("coaximage", "width")
        self.height = self.config.getfloat("coaximage", "height")
        self.pix_size = self.config.getfloat("coaximage", "pix_size")
        self.image_size = self.config.getfloat("coaximage", "image_size")

        # zoom & coax_x pulse are read from 'beamline.ini'
        # section: inocc, option: zoom_pintx
        self.coax_pintx_pulse = self.config.getint("inocc", "zoom_pintx")

        # Coaxial pint axis is derived from 'device' instance
        self.coax_pint = self.dev.coax_pint
        # Gonio is derived from 'device' instance
        self.gonio = self.dev.gonio
        # Zoom is derived from 'device' instance
        self.zoomaxis = self.dev.zoom

        self.capture = Capture.Capture()

        # Dark experiment
        # beamline.ini has a flag for dark experiment
        # If it is True, the default bright and gain values are changed
        # section: "special_setting", option: "isDark", value type: boolean
        self.isDark = self.config.getboolean("special_setting", "isDark")

    def closeCapture(self):
        self.capture.disconnect()

    def read_camera_inf(self, infin):
        ret = {}
        origin_shift_x, origin_shift_y = None, None
        for l in open(infin):
            if "ZoomOptions1:" in l:
                ret["zoom_opts"] = list(map(float, l[l.index(":") + 1:].split()))
            elif "OriginShiftXOptions1:" in l:
                origin_shift_x = list(map(float, l[l.index(":") + 1:].split()))
            elif "OriginShiftYOptions1:" in l:
                origin_shift_y = list(map(float, l[l.index(":") + 1:].split()))
        return ret

    def read_bss_config(self, cfgin):
        ret = {}
        for l in open(cfgin):
            if "#" in l: l = l[:l.index("#")]
            if "Microscope_Zoom_Options:" in l:
                ret["zoom_pulses"] = list(map(int, l[l.index(":") + 1:].split()))

        if None not in (origin_shift_x, origin_shift_y):
            assert len(origin_shift_x) == len(origin_shift_y)
            ret["origin_shift"] = list(zip(origin_shift_x, origin_shift_y))

        return ret

    # read_camera_inf()

    def get_pixel_size(self):  # returns in microns
        # 2020/01/21 K.Hirata CentOS6 videosrv running on BSS machine
        return self.pix_size
    # get_pixel_size()

    def communicate(self, comstr):
        sending_command = comstr.encode()
        self.ms.sendall(sending_command)
        recstr = self.ms.recv(8000)
        return repr(recstr)

    def get_coax_center(self):
        zoom = self.get_zoom()
        origin_shift = self.coax_zoom2oshift[zoom]
        self.logger.info("Origin shift = %s %s" % origin_shift)
        print("origin_shift = ", origin_shift)
        return origin_shift

    # get_coax_center()

    def get_zoom(self):
        zoom_pulse = self.dev.zoom.getPosition()
        return self.coax_pulse2zoom[int(zoom_pulse)]

    """
        sp = recbuf.split("/")
        if len(sp) == 5:
            ret = sp[-2]
            r = re.search("(.*)_([0-9-]+)pulse", ret)
            if r:
                assert r.group(1) == "inactive"
                return self.coax_pulse2zoom[int(r.group(2))]
    """

    # get_zoom()

    def set_zoom(self, zoom):
        if zoom not in self.coax_zoom2pulse:
            print("Possible zoom:", list(self.coax_zoom2pulse.keys()))
            return

        zoom_pulse = self.coax_zoom2pulse[zoom]
        self.zoomaxis.move(zoom_pulse)

        # Beamline BL32XU specific code to adjust pint position
        if self.beamline == "BL32XU":
            self.coax_pint.move(self.coax_pintx_pulse)

    # set_zoom()

    # vserv control
    def set_binning(self, bin):
        if bin == 1:
            setbin = 0
        elif bin == 2:
            setbin = 1
        elif bin == 4:
            setbin = 3
        else:
            print("Invalid binning size")
            return None

        self.capture.setBinning(setbin)

    # set_binning()

    def get_cross_pix(self):
        um_per_px = self.get_pixel_size()
        origin_shift = self.get_coax_center()
        origin_shift = [x / um_per_px * 1.e3 for x in origin_shift]
        w, h = self.width, self.height
        cen_x, cen_y = w / 2 + origin_shift[0], h / 2 - origin_shift[1]
        print("cen_x = %8.2f" % cen_x)
        print("cen_y = %8.2f" % cen_y)
        return int(cen_x), int(cen_y)

    def calc_shift_by_img_px(self, sx, sy, units=("um",)):
        """
        sx,sy: x,y on videosrv's coordinate system. origin is left top.
        """
        if sx < 0 or sy < 0:
            print("Invalid sx or sy:", sx, sy)

        um_per_px = self.get_pixel_size()
        origin_shift = self.get_coax_center()
        origin_shift = [x / um_per_px * 1.e3 for x in origin_shift]
        w, h = self.width, self.height
        cen_x, cen_y = w / 2 + origin_shift[0], h / 2 - origin_shift[1]
        self.logger.debug("cen_x, cen_y = (%8.2f, %8.2f)" % (cen_x, cen_y))

        dx, dy = -(sx - cen_x), (sy - cen_y)

        ret = []
        for unit in units:
            if sx < 0 or sy < 0:
                ret.append((unit, (0, 0)))
            elif unit == "um":
                ret.append((unit, (dx * um_per_px, dy * um_per_px)))
            elif unit == "px":
                ret.append((unit, (dx, dy)))
            elif unit == "rel":
                ret.append((unit, (dx / float(w), dy / float(h))))
            else:
                raise Exception("Unknown unit: %s" % unit)

        if len(ret) == 1:
            return ret[0][1]
        else:
            return dict(ret)

    # calc_shift_by_img_px()

    def move_by_img_px(self, sx, sy):
        """
        sx,sy: x,y on shinoda's coordinate system. origin is right top.
        """
        if sx < 0 or sy < 0:
            print("Invalid sx or sy:", sx, sy)
            return
        dx, dy = self.calc_shift_by_img_px(sx, sy)
        print("move=", dx, dy)
        self.move(dx, dy)

    # move_by_img_px()
    # Calculation goniometer coordinate from given pixel coordinate
    # gcenx, gceny, gcenz should be given in unit of "mm"
    # ph: pixel coordinate of horizontal axis
    # pv: pixel coordinate of vertical axis
    def calc_gxyz_of_pix_at(self, ph, pv, gcenx, gceny, gcenz, phi):
        print("CoaxImage.calc_gxyz_of_pix_at is called")
        print("EEEEEEE ", gcenx, gceny, gcenz, phi)
        if ph < 0 or pv < 0:
            print("Invalid ph or ph:", ph, pv)
            return
            # distance from center cross [um]
        dh, dv = self.calc_shift_by_img_px(ph, pv)
        # distance from center cross [mm]
        dh_mm = dh / 1000.0
        dv_mm = dv / 1000.0
        # print "%12.4f %12.4f %12.4f"%(gcenx,gceny,gcenz)
        print("dH(mm),dV(mm)=", dh_mm, dv_mm)

        # Horizontal direction -> Gonio Y axis
        gy = gceny + dh_mm  # unit [mm]

        # Vertical direction -> Gonio X/Z axes
        mm_dx, mm_dz = self.gonio.calcUpDown(dv, phi)
        gx = gcenx + mm_dx  # unit [mm]
        gz = gcenz + mm_dz  # unit [mm]

        print("(Xpix,Ypix,GX,GY,GZ)=%5d %5d %12.5f %12.5f %12.5f" % (ph, pv, gx, gy, gz))
        print("CoaxImage.calc_gxyz_of_pix_at ends")
        # print "GX,GY,GZ=",gx,gy,gz
        return gx, gy, gz

    # calc_gxyz_of_pix_at()

    def calc_gxyz_diff_mm(self, ph, pv):
        if ph < 0 or pv < 0:
            print("Invalid ph or ph:", ph, pv)
            return
            # distance from center cross [um]
        dh, dv = self.calc_shift_by_img_px(ph, pv)
        # distance from center cross [mm]
        dh_mm = dh / 1000.0
        dv_mm = dv / 1000.0

        return dh_mm, dv_mm

    # 2016/04/13 Videoserv unstable
    def get_coax_image(self, imgout):
        print("####################################")
        print("%s size check" % imgout)
        for i in range(0, 10):
            try:
                self.capture.capture(imgout)
                while (os.path.getsize(imgout) != self.image_size):
                    print("Waiting...for generate the capture image on the storage")
                    time.sleep(1.0)
                print("%s size check Okay" % imgout)
                return True
            except:
                return False

    # get_coax_image()
    def move_to_pix_at(self, ph, pv, gcenx, gceny, gcenz, phi):
        # Calculation of gonio xyz first
        tx, ty, tz = self.calc_gxyz_of_pix_at(ph, pv, gcenx, gceny, gcenz, phi)
        print("move to %10.4f %10.4f %10.4f" % (tx, ty, tz))
        self.gonio.moveXYZmm(tx, ty, tz)


if __name__ == "__main__":
    import BLFactory
    blf = BLFactory.BLFactory()
    blf.initDevice()
    coi = CoaxImage(blf)
    coi.get_coax_image("/staff/bl44xu/BLsoft/TestZOO/testing.ppm")

