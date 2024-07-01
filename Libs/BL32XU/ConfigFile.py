import os
import sys
from MyException import *

class ConfigFile:
	def __init__(self):
		self.ourconf="/isilon/BL32XU/BLsoft/PPPP/bl32xu.conf"
		self.isReady=False

	def readFile(self):
		tmpf=open(self.ourconf,"r")
		self.oconf=tmpf.readlines()

	def checkConfig(self):
		defstart=0
		defend=0
		for x in self.oconf:
			if x.find("def"): 
				defstart+=1
			if x.find("fed"): 
				defend+=1
		if defstart!=defend:
			print " 'def' and 'fed' statement must be same!\n"
			sys.exit(1)
		return 1

	def convLine2Dic(self,linestr):
		key,data=linestr[:-1].split("=")
		tmpdic={key:data}

		return tmpdic

	def prep(self):
		self.readFile()
		self.checkConfig()
		self.storeBlock()
		self.isReady=True

	def storeBlock(self):
		self.block={}
		self.each_dict={}

		for i in range(0,len(self.oconf)):
			line=self.oconf[i]
			#print line
			if line.find("def")!=-1:
				# header string
				header=line[:-1].replace("def ","").replace(":","")
				#print "HEADER:"+header
				j=i+1
				tmpblock={}
				while(1):
					tmpline=self.oconf[j]
					if tmpline.find("fed")!=-1:
						#print "END"
						break
					tmpblock.update(self.convLine2Dic(tmpline))
					#print tmpblock
					#print tmpline
					j+=1
				#print header
				self.block.update({header:tmpblock})

		#print self.block
		#print len(self.block)

	def getCondition(self,key):
		if self.isReady!=True:
			self.prep()

		# Key check
		if key in self.block:
			return float(self.block[key])
		else :
			raise MyException("getCondition:No such a key!\n")

	def getCondition2(self,key1,key2):
		if self.isReady!=True:
			self.prep()
		# Key check
		if key1 in self.block:
			if key2 in self.block[key1]:
				return float(self.block[key1][key2])
			else :
				raise MyException("getCondition:No such a key!\n")
		else:
			raise MyException("getCondition:No such a key!\n")

if __name__=="__main__":

	conf=ConfigFile()
	#print conf.getCondition("TCS_SCAN")
	#print conf.getCondition2("TCS_SCAN","vstart")
	#print conf.getCondition2("TCS_SCAN","vend")
	#print conf.getCondition(sys.argv[1])

	try :
		tmp=conf.getCondition2(sys.argv[1],sys.argv[2])
		print tmp
        except MyException,ttt:
                print ttt.args[0]
