import socket,os

host="192.168.163.12"
port=9203

serversock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
serversock.bind((host,port))
serversock.listen(10)

program="python /isilon/BL32XU/BLsoft/PPPP/10.Zoo/back_cam_cap.py"

print("waiting..")

while True: 
	clientsock,client_address=serversock.accept()
	rcvmsg=clientsock.recv(1024)
	print("Writing filename -> %s"%rcvmsg)
	if rcvmsg=="":
		break
	command="%s %s"%(program,rcvmsg)
	os.system(command)
	s_msg="Capture done"
	clientsock.sendall(s_msg)
	clientsock.close()

#clientsock.close()
