import socket,os,sys,datetime,cv2,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")

class IboINOCC:
	def __init__(self,gonio):
		self.capture_host="192.168.163.12"
		self.capture_port=920920
		self.gonio=gonio
		self.pinimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/large.jpg"
		self.backimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/large_empty.jpg"

		self.roi_x0=205
		self.roi_x1=349
		self.roi_y0=250
		self.roi_y1=370
		self.ysize=self.roi_y1-self.roi_y0

	def anaim(self,prefix):
		print "Start calcEdge"
		im = cv2.imread(self.pinimg)
		bk = cv2.imread(self.backimg)
	
		# GRAY SCALE First this is modified from BL32XU version
		gim = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
		gbk = cv2.cvtColor(bk,cv2.COLOR_BGR2GRAY)
		
		dimg=cv2.absdiff(gim,gbk)
		cv2.imwrite("./diff.jpg",dimg)
		
		# Gaussian blur
		blur = cv2.GaussianBlur(dimg,(5,5),0)
		
		# 2 valuize
		th = cv2.threshold(blur,20,150,0)[1]
		cv2.imwrite("./%s.jpg"%prefix,th)

		#ROI
		print im.shape
		#roi=th[self.roi_x0:self.roi_x1,self.roi_y0:self.roi_y1]
		self.roi=th[self.roi_y0:self.roi_y1,self.roi_x0:self.roi_x1]
		cv2.imwrite("%s_roi.jpg"%(prefix),self.roi)
		
		print "Image subtraction in calcEdge finished"

	# This analyzes x line for detecting line bunch 
	def lineAnalysis(self,x_line):
		#print "###################"
		#print x_line
		#print "###################"
		index=0
		n_found=0
                none_x=150
		find_flag=False

		y_len_max_each=0
		for value in x_line:
			y_cen_max=0.0
			#print value
                        if value > 100 and find_flag==False:
                                #print "START",index
                                find_flag=True
                                ok_y_start=index
                                ok_y_end=index
                        elif value < 100 and find_flag==True:
                                #print "END",index
                                find_flag=False
                                ylength=ok_y_end-ok_y_start
				#print "YLENGTH=",ylength
                                ycenter=(ok_y_end+ok_y_start)/2.0
                                if ylength > 10 and ylength > y_len_max_each:
                                        y_len_max_each=ylength
					y_cen_max_each=ycenter
                                        n_found+=1
                                        #print "FIND!",y_len_max_each
                        elif value > 100 and find_flag==True:
                                ok_y_end=index
                        else:
                                continue
			index+=1
                # edge made OK no baai
                if find_flag==True:
                        ycenter=(index+ok_y_start)/2.0
                        ylength=index-ok_y_start
                        if ylength > 10 and ylength > y_len_max_each:
                                y_len_max_each=ylength
				n_max_each=ycenter
                                n_found+=1
                                print "FIND!",y_len_max_each

		if n_found==0:
			y_cen_max_each=-99.9999

		#print "BEFORE RETURN",y_len_max_each
		return y_len_max_each,y_cen_max_each,n_found

        # for the quick alignment for rotation
        def anaROI2(self,phi):
                #print self.roi.shape
		ok_data=[]
		self.gonio.rotatePhi(phi)
		self.getImage()
		prefix="phi_%03f"%phi
		self.anaim(prefix)
		y_len_max_all=0.0
		y_len_max_cen=0.0
		none_x=150

		print "STARTING PHI=",phi
                for xline in [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140]:
			#print "XLINE=",xline
                        find_flag=False
                        ok_line=0
			y_len_max_each,max_y_cen,n_found=self.lineAnalysis(self.roi[:,xline])
			#print "N_FOUND=",n_found,max_y_cen
			if n_found > 0:
				ok_data.append((xline,y_len_max_each,max_y_cen))
                        	if y_len_max_each > y_len_max_all:
                                	y_len_max_all=y_len_max_each
                                	y_len_max_x=xline
                                	y_len_max_cen=max_y_cen

                	# Line not found
                	elif n_found==0:
                        	if none_x > xline:
					print "NOT FOUND",xline,none_x
                                	none_x=xline

		print "NONE X=",none_x
		#good_index=none_x-20
		hashi_index1=none_x-20
		hashi_index2=none_x-10
		ofile=open("phi.dat","a")
		edge_sum=0.0
		for x,y,cen in ok_data:
			if x==hashi_index1 or x==hashi_index2:
				edge_sum+=cen
			if x==hashi_index2:
				cen=edge_sum/2.0
				ofile.write("PHI,y,max_cen,edge_cen,diff= %8.5f %8.5f %8.5f %8.5f %8.5f\n"%(phi,y_len_max_all,cen,y_len_max_cen,y_len_max_cen-cen))

		return y_len_max_all

	def getImage(self):
		client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		client.connect((self.capture_host,self.capture_port))
		client.send("from nadechin")
		response=client.recv(4096)
		print response
		return True

	def captureROI(self,phi):
		self.gonio.rotate(phi)
		self.getImage()

	def testCapture(self):
		starttime=datetime.datetime.now()
		#for phi in [0,45,90]:
		for phi in [45]:
			self.gonio.rotatePhi(phi)
			self.getImage()
		
			prefix="%f"%phi
			self.anaim(prefix)
		
		endtime=datetime.datetime.now()
		print starttime,endtime
	
if __name__ == "__main__":
	import Gonio
	blanc = '172.24.242.41'
	b_blanc = 10101
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((blanc,b_blanc))
	
	gonio=Gonio.Gonio(s)
	inocc=IboINOCC(gonio)

	"""
	phi=120.0
	ylen_max=inocc.anaROI2(phi)
	print "(PHI,YLEN)=",phi,ylen_max
	if ylen_max < 30.0:
		phi=phi+90.0
		print phi
	elif ylen_max < 60.0:
		phi=phi+50.0
		print phi
	elif ylen_max < 70.0:
		phi=phi+30.0
		print phi
	elif ylen_max < 80.0:
		phi=phi+10.0
		print phi
	gonio.rotatePhi(phi)
	"""
	#inocc.testCapture()
	for phi in range(0,360,20):
		ylen_max=inocc.anaROI2(phi)
