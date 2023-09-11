import socket,os

host="192.168.163.12"
port=920920

serversock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
serversock.bind((host,port))
serversock.listen(10)

program="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/tanuki"

while True: 
	clientsock,client_address=serversock.accept()
	filename=clientsock.recv(1024)
	command="%s %s"%(program,filename)
	os.system(command)
	s_msg="%s capture done"%filename
	clientsock.sendall(s_msg)
	clientsock.close()

#clientsock.close()
