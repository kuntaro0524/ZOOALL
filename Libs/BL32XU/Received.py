class Received:

	def __init__(self,rtnmsg):
		self.rtnmsg=rtnmsg.split('/')
		#print self.rtnmsg

	def get(self,num):
		return(self.rtnmsg[num])

	def getN(self):
		print len(self.rtnmsg)
		return(len(self.rtnmsg))

	def checkQuery(self):
		if self.rtnmsg[3].find("inactive")!=-1:
			return(1)
		elif self.rtnmsg[3].find("ok")!=-1:
			return(1)
		else:
			return(0)

	def readQuery(self):
		ppp=self.rtnmsg[3].rfind("_")+1
		#print ppp
		return self.rtnmsg[3][ppp:]
		#print iii[ppp:]
		#return self.rtnmsg[3].[ppp:]

