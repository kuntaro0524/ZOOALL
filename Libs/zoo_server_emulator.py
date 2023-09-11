# -*- coding:utf-8 -*-
import socket

host = "127.0.0.1" 
port = 9203 

serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversock.bind((host,port)) 
serversock.listen(10) 

print('Waiting for connections...')
clientsock, client_address = serversock.accept() 

while True:
    rcvmsg = clientsock.recv(1024)
    print('Received -> %s' % (rcvmsg))
    if rcvmsg == '':
      break
    print('Type message...')
    s_msg = input()
    if s_msg == '':
      break
    print('Wait...')

    clientsock.sendall(s_msg) 
clientsock.close()
