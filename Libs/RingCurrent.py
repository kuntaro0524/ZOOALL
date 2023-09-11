import socket

class RingCurrent:
	def __init__(self,server):
		self.s=server
		self.get_current_str="get/bl_dbci_ringcurrent/present"

	def getRingCurrent(self):
		self.s.sendall(self.get_current_str)
		recbuf = self.s.recv(8000)
		strs=recbuf.split("/")
		ring_current=float(strs[len(strs)-2].replace("mA",""))
		return ring_current

	def isAborted(self):
		ring_current=self.getRingCurrent()
		if ring_current > 10.0:
			return False
		else:
			return True

if __name__=="__main__":
                host = '172.24.242.41'
                port = 10101

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host,port))

		p=RingCurrent(s)
		print(p.getRingCurrent())
		print(p.isAborted())
