import socket,os,sys,datetime,cv2
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import Gonio

host="192.168.163.12"
port=920920

blanc = '172.24.242.41'
b_blanc = 10101
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((blanc,b_blanc))

print("OKAY")

def anaim(pinfile,backfile,prefix):
	print("Start calcEdge")
	im = cv2.imread(pinfile)
	bk = cv2.imread(backfile)

	# GRAY SCALE First this is modified from BL32XU version
	gim = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
	gbk = cv2.cvtColor(bk,cv2.COLOR_BGR2GRAY)
	
	dimg=cv2.absdiff(gim,gbk)
	cv2.imwrite("./diff.jpg",dimg)
	
	# Gaussian blur
	blur = cv2.GaussianBlur(dimg,(3,3),0)
	
	# 2 valuize
	th = cv2.threshold(blur,20,150,0)[1]
	cv2.imwrite("./%s.jpg"%prefix,th)
	
	print("Image subtraction in calcEdge finished")

gonio=Gonio.Gonio(s)

starttime=datetime.datetime.now()
for phi in [0,45,90]:
	gonio.rotatePhi(phi)
	client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	client.connect((host,port))

	client.send("from nadechin")
	response=client.recv(4096)
	dt=datetime.datetime.now()
	print(dt,response)
	
	pinimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/large.jpg"
	backimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/large_empty.jpg"
	prefix="%f.jpg"%phi
	anaim(pinimg,backimg,prefix)

endtime=datetime.datetime.now()

print(starttime)
print(endtime)
