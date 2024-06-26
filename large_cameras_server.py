import socket,os

host="192.168.163.11"
port=9203

serversock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
serversock.bind((host,port))
serversock.listen(10)

#back
cap0="/home/bladmin/bin/video0_cap"
#side
cap1="/home/bladmin/bin/video1_cap -g 60"

print "waiting.."

while True: 
	clientsock,client_address=serversock.accept()
	rcvmsg=clientsock.recv(1024)
	print "Received -> %s"%rcvmsg
	if rcvmsg=="":
		break
	# Command interpreter
	cols=rcvmsg.split(",")
	# command for capture
	# "back" or "side"
	print cols
	view=cols[0]
	filename=cols[1]
	binning=int(cols[2])
	exptime=int(cols[3])

	# Side camera
	if view=="side":
		s_msg="side camera capturing"
		command="%s -f %s -b %d -e %d"%(cap1,filename,binning,exptime)
		os.system(command)
	elif view=="naname":
		s_msg="naname camera capturing"
		if binning!=1:
			command="%s -f %s -b %d"%(cap0,filename,binning)
		else:
			command="%s -e 300 -f %s -b %d"%(cap0,filename,binning)
		os.system(command)

	clientsock.sendall(s_msg)
	clientsock.close()

#clientsock.close()
