import socket,os
import v4l2
import cv2
import numpy as np
from fcntl import ioctl

host="192.168.163.13"
port=1192

def capture(filename):
    fd=open('/dev/video0', 'rw')
    ioctl(fd, v4l2.VIDIOC_S_INPUT, v4l2.c_int(2))

    cap = cv2.VideoCapture(0)
    ret,frame=cap.read()
    cv2.imwrite(filename,frame)
    cap.release()

serversock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
serversock.bind((host,port))
serversock.listen(10)

print("OKAY")
print(host,port)

while True: 
	clientsock,client_address=serversock.accept()
	filename=clientsock.recv(1024)
        capture(filename)
	s_msg="%s capture done"%filename
	clientsock.sendall(s_msg)
	print(s_msg)
	clientsock.close()

#clientsock.close()
