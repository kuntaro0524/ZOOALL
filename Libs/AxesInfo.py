import time
import socket
import sys

#import Motor as Motor
from File import *
from Motor import *

class AxesInfo:
	def __init__(self,server):
		self.s=server
		self.isStore=-1

	def all(self,ofname):
    		d=datetime.datetime.today()

		ofile=open(ofname,"w")
		ofile.write("### %s ####\n"%d)
    		ofile.write( "##### ID #####\n")
    		ofile.write( "ID gap\t:%12s%7s\n" % Motor(self.s,"bl_32in_id_gap","mm").getPosition())
    		ofile.write( "##### Front End ####\n")
    		ofile.write( "vert\t:%12s%7s\n" % Motor(self.s,"bl_32in_fe_slit_1_vertical","mm").getPosition())
    		ofile.write( "hori\t:%12s%7s\n" % Motor(self.s,"bl_32in_fe_slit_1_horizontal","mm").getPosition())
    		ofile.write( "height\t:%12s%7s\n" % Motor(self.s,"bl_32in_fe_slit_1_height","mm").getApert()) 
		ofile.write( "width\t:%12s%7s\n" % Motor(self.s,"bl_32in_fe_slit_1_width","mm").getApert())
    		ofile.write( "##### Monochromator ####\n")
    		ofile.write( "Energy\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1","pulse").getEnergy())
    		ofile.write( "Angle\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1","pulse").getAngle())
    		ofile.write( "Wavelength\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1","pulse").getRamda())
    		ofile.write( "Theta\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_theta","pulse").getPosition())
    		ofile.write( "Y1\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_y1","pulse").getPosition())
    		ofile.write( "Z1\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_z1","pulse").getPosition())
    		ofile.write( "Dth1\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_dtheta1","pulse").getPosition())
    		ofile.write( "Ty1\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_thetay1","pulse").getPosition())
    		ofile.write( "Z2\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_z2","pulse").getPosition())
    		ofile.write( "Tx2\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_thetax2","pulse").getPosition())
    		ofile.write( "Ty2\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_thetay2","pulse").getPosition())
    		ofile.write( "Xt\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_xt","pulse").getPosition())
    		ofile.write( "Zt\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_zt","pulse").getPosition())
    		ofile.write( "##### TC slit ####\n")
    		ofile.write( "height\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_slit_1_height","mm").getApert())
    		ofile.write( "width\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_slit_1_width","mm").getApert())
    		ofile.write( "vert\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_slit_1_vertical","mm").getPosition())
    		ofile.write( "hori\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_slit_1_horizontal","mm").getPosition())
    		ofile.write( "##### Mirror ####\n")
    		ofile.write( "VFM-y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mv_1_y","pulse").getPosition())
    		ofile.write( "VFM-z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mv_1_z","pulse").getPosition())
    		ofile.write( "VFM-tx\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mv_1_tx","pulse").getPosition())
    		ofile.write( "VFM-ty\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mv_1_ty","pulse").getPosition())
    		ofile.write( "HFM-y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mh_1_y","pulse").getPosition())
    		ofile.write( "HFM-z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mh_1_z","pulse").getPosition())
    		ofile.write( "HFM-tz\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mh_1_tz","pulse").getPosition())
		ofile.write("##### Stage ####\n")
		ofile.write("Stage-y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_stage_1_y","pulse").getPosition())
		ofile.write("Stage-z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_stage_1_z","pulse").getPosition())
		ofile.write("Coax-x\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_coax_1_x","pulse").getPosition())
		ofile.write("Coax-y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_slit_2_ring","pulse").getPosition())
		ofile.write("Coax-z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_slit_2_hall","pulse").getPosition())
		ofile.write("Gonio phi\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_phi","pulse").getPosition())
		ofile.write("Gonio x\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_x","pulse").getPosition())
		ofile.write("Gonio y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_y","pulse").getPosition())
		ofile.write("Gonio z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_z","pulse").getPosition())
		ofile.write("Gonio zz\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_zz","pulse").getPosition())

		ofile.close()
		return 1

	def getLeastInfo(self):
		time.sleep(1)
		try :
    			gap=Motor(self.s,"bl_32in_id_gap","mm").getPosition()[0]
    			fesv=Motor(self.s,"bl_32in_fe_slit_1_vertical","mm").getPosition()[0]
    			fesh=Motor(self.s,"bl_32in_fe_slit_1_horizontal","mm").getPosition()[0]
    			fesheight=Motor(self.s,"bl_32in_fe_slit_1_height","mm").getApert()[0]
    			feswidth=Motor(self.s,"bl_32in_fe_slit_1_width","mm").getApert()[0]
			energy=Motor(self.s,"bl_32in_tc1_stmono_1","pulse").getEnergy()[0]
                	tcs_height=Motor(self.s,"bl_32in_tc1_slit_1_height","mm").getApert()[0]
                	tcs_width=Motor(self.s,"bl_32in_tc1_slit_1_width","mm").getApert()[0]
                	tcs_vert=Motor(self.s,"bl_32in_tc1_slit_1_vertical","mm").getPosition()[0]
                	tcs_hori=Motor(self.s,"bl_32in_tc1_slit_1_horizontal","mm").getPosition()[0]

		except :
			print sys.exc_info()[0]
			sys.exit(1)

		cm1="Gap %8.3fmm\nFES[mm]: (He,Wi)=(%6.4f,%6.4f)\nFES[mm]:(V,H)=(%6.4f,%6.4f)\nEnergy=%12.4fkeV\n"%(gap,fesheight,feswidth,fesv,fesh,energy)
		cm2="TCS(He,Wi)=(%6.4f,%6.4f)[mm]\nTCS(Vert,Hori)=(%6.4f,%6.4f)[mm]\n"%(tcs_height,tcs_width,tcs_vert,tcs_hori)
		cm3="[Date:%s]\n"%(datetime.datetime.today())
		
		#print cm1+cm2
		return cm3+cm1+cm2

	def getInfoStr(self):
    		d=datetime.datetime.today()

		tmpstr=("### %s ####\n"%d)
    		tmpstr=tmpstr+("##### ID #####\n")
    		tmpstr=tmpstr+( "ID gap\t:%12s%7s\n" % Motor(self.s,"bl_32in_id_gap","mm").getPosition())
    		tmpstr=tmpstr+( "##### Front End ####\n")
    		tmpstr=tmpstr+( "vert\t:%12s%7s\n" % Motor(self.s,"bl_32in_fe_slit_1_vertical","mm").getPosition())
    		tmpstr=tmpstr+( "hori\t:%12s%7s\n" % Motor(self.s,"bl_32in_fe_slit_1_horizontal","mm").getPosition())
    		tmpstr=tmpstr+( "height\t:%12s%7s\n" % Motor(self.s,"bl_32in_fe_slit_1_height","mm").getApert())
    		tmpstr=tmpstr+( "width\t:%12s%7s\n" % Motor(self.s,"bl_32in_fe_slit_1_width","mm").getApert())
    		tmpstr=tmpstr+( "##### Monochromator ####\n")
    		tmpstr=tmpstr+( "Energy\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1","pulse").getEnergy())
    		tmpstr=tmpstr+( "Angle\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1","pulse").getAngle())
    		tmpstr=tmpstr+( "Wavelength\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1","pulse").getRamda())
    		tmpstr=tmpstr+( "Theta\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_theta","pulse").getPosition())
    		tmpstr=tmpstr+( "Y1\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_y1","pulse").getPosition())
    		tmpstr=tmpstr+( "Z1\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_z1","pulse").getPosition())
    		tmpstr=tmpstr+( "Dth1\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_dtheta1","pulse").getPosition())
    		tmpstr=tmpstr+( "Ty1\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_thetay1","pulse").getPosition())
    		tmpstr=tmpstr+( "Z2\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_z2","pulse").getPosition())
    		tmpstr=tmpstr+( "Tx2\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_thetax2","pulse").getPosition())
    		tmpstr=tmpstr+( "Ty2\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_thetay2","pulse").getPosition())
    		tmpstr=tmpstr+( "Xt\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_xt","pulse").getPosition())
    		tmpstr=tmpstr+( "Zt\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_stmono_1_zt","pulse").getPosition())
    		tmpstr=tmpstr+( "##### TC slit ####\n")
    		tmpstr=tmpstr+( "height\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_slit_1_height","mm").getApert())
    		tmpstr=tmpstr+( "width\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_slit_1_width","mm").getApert())
    		tmpstr=tmpstr+( "vert\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_slit_1_vertical","mm").getPosition())
    		tmpstr=tmpstr+( "hori\t:%12s%7s\n" % Motor(self.s,"bl_32in_tc1_slit_1_horizontal","mm").getPosition())
    		tmpstr=tmpstr+( "##### Mirror ####\n")
    		tmpstr=tmpstr+( "VFM-y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mv_1_y","pulse").getPosition())
    		tmpstr=tmpstr+( "VFM-z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mv_1_z","pulse").getPosition())
    		tmpstr=tmpstr+( "VFM-tx\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mv_1_tx","pulse").getPosition())
    		tmpstr=tmpstr+( "VFM-ty\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mv_1_ty","pulse").getPosition())
    		tmpstr=tmpstr+( "HFM-y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mh_1_y","pulse").getPosition())
    		tmpstr=tmpstr+( "HFM-z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mh_1_z","pulse").getPosition())
    		tmpstr=tmpstr+( "HFM-tz\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_mh_1_tz","pulse").getPosition())
		tmpstr=tmpstr+("##### Stage ####\n")
		tmpstr=tmpstr+("Stage-y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_stage_1_y","pulse").getPosition())
		tmpstr=tmpstr+("Stage-z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_stage_1_z","pulse").getPosition())
		tmpstr=tmpstr+("Gonio phi\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_phi","pulse").getPosition())
		tmpsrt=tmpstr+("Coax-x\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_coax_1_x","pulse").getPosition())
		tmpsrt=tmpstr+("Coax-y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_slit_2_ring","pulse").getPosition())
		tmpsrt=tmpstr+("Coax-z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_slit_2_hall","pulse").getPosition())
		tmpstr=tmpstr+("Gonio x\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_x","pulse").getPosition())
		tmpstr=tmpstr+("Gonio y\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_y","pulse").getPosition())
		tmpstr=tmpstr+("Gonio z\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_z","pulse").getPosition())
		tmpstr=tmpstr+("Gonio zz\t:%12s%7s\n" % Motor(self.s,"bl_32in_st2_gonio_1_zz","pulse").getPosition())

		return tmpstr

if __name__=="__main__":
	#host = '192.168.163.1'
	host = '172.24.242.41'
	port = 10101
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))

	f=File("./")
    	prefix="%03d"%f.getNewIdx3()
	ax=AxesInfo(s)

    	ofile=prefix+"_axes.dat"   #hashi 100615
	ax.all(ofile)              #hashi 100615
	#print ax.getLeastInfo() 
	
