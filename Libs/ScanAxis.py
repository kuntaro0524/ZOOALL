from MyException import *

class ScanAxis:

	def __init__(self):
		self.scan_start=0
		self.scan_end=0
		self.scan_step=0

	def setStart(self,start):
		self.scan_start=start

	def setEnd(self,end):
		self.scan_end=end

	def setStep(self,step):
		self.scan_step=step

	def checkScanCondition(self):
		self.nscan=float(self.scan_end-self.scan_start)/float(self.scan_step)
		if self.nscan<=0:
			raise MyException("Scanning conidtion is not correct!!\n")
		else:
			pass

	def setRelStart(self,curr,width): # note: the same [unit]
		self.scan_start=curr-width
		print self.scan_start

	def setRelEnd(self,curr,width): # note: the same [unit]
		self.scan_end=curr+width
		print self.scan_end

if __name__=="__main__":

	k=ScanAxis()

	k.setStart(-10)
	k.setEnd(10)
	k.setStep(-2)

	try:
		k.checkScanCondition()
	except MyException,ttt:
		print ttt.args[0]
		
