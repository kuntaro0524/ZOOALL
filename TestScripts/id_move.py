import sys
import socket
import time
from ID import *

if __name__=="__main__":
	host = '172.24.242.41'
	port = 10101
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))
	
	id=ID(s)
	id.move(float(input()))

	s.close()
