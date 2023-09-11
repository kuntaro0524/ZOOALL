import time
import socket
import MyException

class SocketCom():
    def __init__(self, serv_address, serv_port):
        self.serv_address=serv_address
        self.serv_port = serv_port
        self.isConnect=False

    # String to bytes
    def communicate(self, comstr):
        sending_command = comstr.encode()
        print(sending_command)
        if self.isConnect==False:
            print("Connection first!")
            return False
        else:
            self.bssr.sendall(sending_command)
            recstr=self.bssr.recv(8000)

        return repr(recstr)

    def connect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for i in range(0,20):
            try:
                self.server.connect((self.serv_address, self.serv_port))
                self.isConnect=True
                return True
            except MyException as ttt:
                print("connect: failed. %s"%ttt.args[0])
                time.sleep(20.0)
        return False

    def disconnect(self):
        time.sleep(3.0)
        if self.isConnect:
            command="put/bss/disconnect"
            recstr=self.communicate(command)
            print(recstr)
            self.serv.close()
        return True

    def disconnectServers(self):
        query_com="put/device_server/disconnect"
        if self.isConnect==False:
            print("Connection first!")
            return False
        else:
            recstr=self.communicate(query_com)
            print(recstr)

    def connectServers(self):
        query_com="put/device_server/connect"
        if self.isConnect==False:
            print("Connection first!")
            return False
        else:
            recstr=self.communicate(query_com)
            return repr(recstr)