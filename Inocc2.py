import sys,os,math,numpy,socket,time
import re
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/03.GUI/04.SACLA-KUMA/Libs")
from Gonio import *
from Capture import *
from DrawPolygonMouse import *

def read_camera_inf(infin):
	ret = {}
	origin_shift_x, origin_shift_y = None, None
	for l in open(infin):
		if "ZoomOptions1:" in l:
			ret["zoom_opts"] = map(float, l[l.index(":")+1:].split())
		elif "OriginShiftXOptions1:" in l:
			origin_shift_x = map(float, l[l.index(":")+1:].split())
		elif "OriginShiftYOptions1:" in l:
			origin_shift_y = map(float, l[l.index(":")+1:].split())

	# TODO read tvextender

	if None not in (origin_shift_x, origin_shift_y):
		assert len(origin_shift_x) == len(origin_shift_y)
		ret["origin_shift"] = zip(origin_shift_x, origin_shift_y)

	return ret
# read_camera_inf()

def read_bss_config(cfgin):
	ret = {}
	for l in open(cfgin):
		if "#" in l: l = l[:l.index("#")]
		if "Microscope_Zoom_Options:" in l:
			ret["zoom_pulses"] = map(int, l[l.index(":")+1:].split())
	return ret

class crycen:
	def __init__ (self, ms):
		self.enable_xmlrpc = True
		self.xmlrpc_server = None
		self.thread = None
		self.ms = ms
		self.gonio = Gonio(ms)
		self.capture = Capture()

		self.camera_inf = read_camera_inf(os.path.join(os.environ["BLCONFIG"], "video", "camera.inf"))
		self.bss_config = read_bss_config(os.path.join(os.environ["BLCONFIG"], "bss", "bss.config"))
		self.coax_pulse2zoom = dict(zip(self.bss_config["zoom_pulses"], self.camera_inf["zoom_opts"]))
		self.coax_zoom2pulse = dict(zip(self.camera_inf["zoom_opts"], self.bss_config["zoom_pulses"]))
		self.coax_zoom2oshift = dict(zip(self.camera_inf["zoom_opts"], self.camera_inf["origin_shift"]))
		self.coax_zpulse2pint = {0:19985, -16000:19980, -32000:19974, -48000:20024} # zoom pulse to pint pulse
	# __init__()

	def get_axes_info(self):
		phi = "%8.2f" % self.gonio.getPhi()
		gx = "%8.4f" % self.gonio.getXmm()
		gy = "%8.4f" % self.gonio.getYmm()
		gz = "%8.4f" % self.gonio.getZmm()
		#gzz = "%8.4f" % self.gonio.getZZmm()

		return phi, gx, gy, gz
	# get_axes_info()

	def get_axes_info_float(self):
		phi =self.gonio.getPhi()
		gx = self.gonio.getXmm()
		gy = self.gonio.getYmm()
		gz = self.gonio.getZmm()
		return phi,gx,gy,gz
	# get_curr_xyz_mm(self):

	def move_gonio_abs(self, phi, gx, gy, gz):
		self.gonio.moveXYZmm(gx, gy, gz)
		self.set_gonio_phi(phi)
	# move_gonio_abs()

	def get_pixel_size(self): # returns in microns
		# X[mm] = X[px] / (C * Zoom * TvExtender)
		# C = 102.4375
		# TvExtender = 1
		#
		#	 MM2P = _MM2P * ci[GetVideoChannel()].zoom * ci[GetVideoChannel()].tvext / (GetBinning()+1);
		# #define _MM2P 102.4375
		#	 double X = ((double)px - WIDTH/2.0) / MM2P;
		# GetBinning()+1 == 4 when 4x4 bin (2 for 2x2 bin, 1 for 1x1 bin)
		"""
		zoom, tvext: see $BLCONFIG/video/camera.inf
		(for st2_coax_1_zoom pulse value, see $CLBONFIG/bss/bss.config Microscope_Zoom_Options:
		"""
		"""
				XXX Not-thread safe!... but how this happened?
		debug:: video_vdclickemu/put/3812_video_server/ok/0
		Traceback (most recent call last):
  		File "shinoda_centering_server.py", line 500, in BtnRun_onclick
			self.intr.do_centering()
  		File "shinoda_centering_server.py", line 398, in do_centering
			oneaction(20*rotate_sign, i==0)
  		File "shinoda_centering_server.py", line 385, in oneaction
			log_write("%.2d_shift= %.2f%% %.2f%% (%.2f %.2f um)"%((self.count, self.last_shift[0]*100., self.last_shift[1]*100.)+self.calc_shift_by_img_px(sx,sy, unit="um")))
  		File "shinoda_centering_server.py", line 256, in calc_shift_by_img_px
			um_per_px = self.get_pixel_size()
  		File "shinoda_centering_server.py", line 148, in get_pixel_size
			bin =  self.capture.getBinning()
  		File "/isilon/BL32XU/BLsoft/Other/Yam/yamtbx/bl32xu/centering_support/hiratalib/Capture.py", line 178, in getBinning
			return int(sp[-2])
		ValueError: invalid literal for int() with base 10: 'ok'
		video_binning/get/3812_video_server/4/0
		"""
		bin =  self.capture.getBinning()
		#print "Binning=", bin

		zoom = self.get_zoom()
		#print "Zoom=", zoom

		return 1.e3/(102.4375*zoom/bin)
	# get_pixel_size()

	def get_coax_center(self):
		zoom = self.get_zoom()
		#print "Zoom=", zoom
		origin_shift = self.coax_zoom2oshift[zoom]
		return origin_shift
	# get_coax_center()

	def get_zoom(self):
		self.ms.sendall("get/bl_32in_st2_coax_1_zoom/query")
		recbuf = self.ms.recv(8000)
		print "debug::", recbuf

		sp = recbuf.split("/")
		if len(sp) == 5:
			ret = sp[-2]
			r = re.search("(.*)_([0-9-]+)pulse", ret)
			if r:
				assert r.group(1) == "inactive"
				return self.coax_pulse2zoom[int(r.group(2))]
	# get_zoom()

	def set_zoom(self, zoom):
		if zoom not in self.coax_zoom2pulse:
			print "Possible zoom:", self.coax_zoom2pulse.keys()
			return

		zoomaxis = Zoom(self.ms)
		zoom_pulse = self.coax_zoom2pulse[zoom]
		zoomaxis.move(zoom_pulse)
		
		if zoom_pulse not in self.coax_zpulse2pint:
			print "Error. Unknown zoom pulse for pint adjustment:", zoom_pulse
			return

		pintaxis = CoaxPint(self.ms)
		pint_pulse = self.coax_zpulse2pint[zoom_pulse]
		pintaxis.move(pint_pulse)
	# set_zoom()

	def set_axes(self):
		print "set axes"
		
		# left (-), right (+)
		self.gonio.moveTrans(dist)

		# down (-), up (+)
		self.gonio.moveUpDown(dist)

		# phi
		self.gonio.rotatePhiRelative(rot_ang)
		
		# pint
		self.gonio.movePint(dist)
	# set_axes()

	def rotate(self, deltaphi):
		self.gonio.rotatePhiRelative(deltaphi)
	# rotate()

	def set_gonio_phi(self, phi):
		self.gonio.rotatePhi(phi)
	# set_gonio_phi()

	def move(self, deltax, deltay):
		# left (-), right (+)
		self.gonio.moveTrans(deltax)

		# down (-), up (+)
		self.gonio.moveUpDown(deltay)
	# move()

	# vserv control
	def set_binning(self, bin):
		if bin==1: setbin = 0
		elif bin==2: setbin = 1
		elif bin==4: setbin = 3
		else:
			print "Invalid binning size"
			return None

		self.capture.setBinning(setbin)
	# set_binning()
	
	def get_coax_image(self, imgout, convert=False):
		self.capture.capture(imgout, speed=50) # 50 seems good..

		if convert:
			print "Converting.."
			subprocess.call(["convert", imgout, "-compress", "none", imgout])
	# get_coax_image()

	def calc_shift_by_img_px(self, sx, sy, units=("um",)):
		"""
		sx,sy: x,y on videosrv's coordinate system. origin is left top.
		"""
		if sx < 0 or sy < 0:
			print "Invalid sx or sy:", sx, sy

		um_per_px = self.get_pixel_size()
		origin_shift = self.get_coax_center()
		origin_shift = map(lambda x: x/um_per_px*1.e3, origin_shift)
		w, h = 640, 480
		cen_x, cen_y = w/2+origin_shift[0], h/2-origin_shift[1]
		print "Center: ", cen_x, cen_y

		#dx, dy = (deltax-cen_x)*um_per_px, (deltay-cen_y)*um_per_px
		dx, dy = -(sx-cen_x), (sy-cen_y)

		ret = []
		for unit in units:
			if sx < 0 or sy < 0:
				ret.append((unit, (0,0)))
			elif unit == "um":
				ret.append((unit, (dx*um_per_px, dy*um_per_px)))
			elif unit == "px":
				ret.append((unit, (dx, dy)))
			elif unit == "rel":
				ret.append((unit, (dx/float(w), dy/float(h))))
			else:
				raise Exception("Unknown unit: %s"%unit)

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
			print "Invalid sx or sy:", sx, sy
			return
		dx, dy = self.calc_shift_by_img_px(sx, sy)
		print "move=", dx, dy
		self.move(dx, dy)
	# move_by_img_px()

	# Calculation goniometer coordinate from given pixel coordinate
	# gcenx, gceny, gcenz should be given in unit of "mm"
	# ph: pixel coordinate of horizontal axis
	# pv: pixel coordinate of vertical axis
	def calc_gxyz_of_pix_at(self, ph, pv, gcenx, gceny, gcenz, phi):
		if ph < 0 or pv < 0:
			print "Invalid ph or ph:", ph, pv
			return 
		# distance from center cross [um]
		dh, dv = self.calc_shift_by_img_px(ph, pv)
		# distance from center cross [mm]
		dh_mm = dh/1000.0
		dv_mm = dv/1000.0
		print "%12.4f %12.4f %12.4f"%(gcenx,gceny,gcenz)
	
		# Horizontal direction -> Gonio Y axis
		gy=gceny+dh_mm # unit [mm]

		# Vertical direction -> Gonio X/Z axes
		mm_dx,mm_dz=self.gonio.calcUpDown(dv,phi)
		gx=gcenx+mm_dx # unit [mm]
		gz=gcenz+mm_dz # unit [mm]

		print "(Xpix,Ypix,GX,GY,GZ)=%5d %5d %12.5f %12.5f %12.5f"%(ph,pv,gx,gy,gz)
		#print "GX,GY,GZ=",gx,gy,gz
		return gx,gy,gz
	# calc_gxyz_of_pix_at()

	def move_to_pix_at(self,ph,pv,gcenx,gceny,gcenz,phi):
		# Calculation of gonio xyz first
		tx,ty,tz=self.calc_gxyz_of_pix_at(ph,pv,gcenx,gceny,gcenz,phi)
		print "move to %10.4f %10.4f %10.4f"%(tx,ty,tz)
		self.gonio.moveXYZmm(tx,ty,tz)

	def let_bss_move(self, sx, sy):
		if sx < 0 or sy < 0:
			print "Invalid sx or sy:", sx, sy
			return
		
		w, h = 640, 480
		sx = w-sx
		assert 0 <= sx <= w
		assert 0 <= sy <= h
		self.capture.s.sendall("put/video_vdclickemu/%d_%d"%(sx,sy))
		print "let_bss_move::", self.capture.s.recv(8000)

		time.sleep(0.5)
		while True:
			if self.gonio.goniox.isMoved() and self.gonio.gonioy.isMoved() and self.gonio.gonioz.isMoved():
				return
			print "Waiting to stop.."
			time.sleep(0.1)
	# let_bss_move()

	def start_shinoda_centering_core(self):
		if self.running is None or not self.running.isalive():
			edir = "/isilon/BL32XU/BLsoft/Other/shinoda/loop_centering_current"
			self.running = pexpect.spawn('ssh oys09 "cd %s; ./out_simple_centering"'%edir)
	# start_shinoda_centering_core()
	
	def start_shinoda_facing_core(self):
		if self.runningf is None or not self.runningf.isalive():
			edir = "/isilon/BL32XU/BLsoft/Other/shinoda/loop_centering_current"
			self.runningf = pexpect.spawn('ssh oys09 "cd %s; ./out_simple_faceing"'%edir)
	# start_shinoda_facing_core()

	def do_centering(self):
		#log_root = "/isilon/BL32XU/BLsoft/Other/shinoda/loop_centering_current/logs"
		#edir = "/isilon/BL32XU/BLsoft/Other/shinoda/loop_centering_current"

		#log_dir = os.path.join(log_root, time.strftime("%y%m%d_%H%M%S"))
		#os.mkdir(log_dir)
		#inocclog.config(log_dir, stream=self.parent.logstream)
		#inocclog.info("Started")
		#inocclog.info("gonio_phixyz= %s %s %s %s" % self.get_axes_info())
		#start_time = time.time()
		#self.start_shinoda_centering_core()

		rotate_sign = -1 if self.gonio.getPhi() > 0 else 1

		self.count = 0
		self.ttt = None
		self.tmv = None
		self.last_shift = (0,0)
		def oneaction(phistep, isfirst=False):
			self.get_coax_image(os.path.join(edir, "tmp_img/img1.ppm"))
			self.rotate(phistep)

			if len(lines) == 2:
				sx, sy, decision = self.running.before.splitlines()[1].split()
				sx, sy = map(int, (sx, sy))
				shift = self.calc_shift_by_img_px(sx,sy, units=("um", "rel"))
		print sx,sy
	# do_centering()

if __name__ == "__main__":
	dpm=DrawPolygon()
	ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#ms.connect(("192.168.163.1", 10101))
	ms.connect(("172.24.242.41", 10101))
	crycen=crycen(ms)

	#print crycen.get_pixel_size()
	# cross center Gonio xyz values

	phi,cenx,ceny,cenz=crycen.get_axes_info_float()
	print phi,cenx,ceny,cenz
	filename="/isilon/BL32XU/BLsoft/PPPP/03.GUI/04.SACLA-KUMA/test.ppm"
	crycen.get_coax_image(filename, convert=False)
	#crycen.move_by_img_px(157,167)
	grav_x,grav_y,xylist=dpm.run(filename)
	#crycen.move_by_img_px(grav_x,grav_y)

	gxyz=[]
	for xy in xylist:
		x,y=xy
		print "PIXPLOT ",x,y
		tx,ty,tz=crycen.calc_gxyz_of_pix_at(x,y,cenx,ceny,cenz,phi)
		print "GONIOPLOT ",tx,ty,tz
		gxyz.append((tx,ty,tz))

	print xylist
	print gxyz

	"""
	for xyz in gxyz:
		x,y,z=xyz
		crycen.move_gonio_abs(phi,x,y,z)
		time.sleep(3)
	"""
	#x,y=dpm.run(filename)
	#crycen.move_by_img_px(x,y)
