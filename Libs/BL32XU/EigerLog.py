import sys,os,math,datetime
import os,re,urllib,urlparse

class EigerLog:

	def __init__(self):
		self.eiger_site='http://192.168.163.204'
		self.eiger_logsite="%s/logs/"%self.eiger_site
		self.outdir="/isilon/BL32XU/BLsoft/PPPP/Logs/"

	def setDLdire(self,dire):
		self.outdir=dire

	def saveLogs(self):
		try:
  			os.mkdir(self.outdir) 
		except OSError:
  			pass

		t=urllib.urlopen(self.eiger_logsite)
		txt=t.read()
		print txt
		p = re.compile('href.*?log\"') 
		m=p.findall(txt)
		for f in m:
  			File=urlparse.urljoin(self.eiger_logsite,f[6:-1])
			print File
  			Savename=os.path.join(self.outdir,os.path.basename(File)) 
  			urllib.urlretrieve(File,Savename)

	def saveStreamLog(self):
  		File=urlparse.urljoin(self.eiger_logsite,"stream_api.log")
		print File
  		Savename=os.path.join(self.outdir,os.path.basename(File)) 
  		urllib.urlretrieve(File,Savename)

	def countDrops(self):
		self.saveStreamLog()
		api_log="%s/stream_api.log"%self.outdir
		lines=open(api_log,"r").readlines()

		iline=0
		self.drop_line=[]
		self.time_line=[]
		for line in lines:
			if line.rfind("drop")!=-1 and line.rfind("ERROR")!=-1:
				self.drop_line.append(iline)
				self.time_line.append(time_stamp)
				#print line
			if line.rfind("[")!=-1:
				istart=line.rfind("[")+1
				iend=line.rfind("]")
				time_stamp=line[istart:iend]
			iline+=1

		self.time_stamps=[]
		self.all_frames=[]
		self.acq_frames=[]
		self.suc_rate=[]
		for iline,oc_time in zip(self.drop_line,self.time_line):
			#print lines[iline]
			cols=lines[iline].split()
			expected_num=float(cols[4])
			all_num=float(cols[6])
			acquisition_rate=expected_num/all_num
			# For logging
			self.acq_frames.append(expected_num)
			self.all_frames.append(all_num)
			self.suc_rate.append(acquisition_rate)
			self.time_stamps.append(datetime.datetime.strptime(oc_time, '%Y-%m-%d %H:%M:%S'))
			logstr="%30s %s %6.4f"%(oc_time,lines[iline].strip(),acquisition_rate)

			if acquisition_rate < 0.90:
				print "Severe!!",logstr
				
			else:
				print logstr

	# Start time
	def checkDropDuring(self,starttime,endtime):
		self.countDrops()
		chk_start = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
		chk_end = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')

		total_frame=0
		total_acquired=0
		for timestamp,suc_rate,acq_frame,all_frame in zip(self.time_stamps,self.suc_rate,self.acq_frames,self.all_frames):
			if timestamp < chk_end and timestamp > chk_start:
				total_acquired+=acq_frame
				total_frame+=all_frame

		if total_frame!=0:
			acq_rate_final=float(total_acquired)/float(total_frame)
		else:	
			acq_rate_final=1.0
		print "Total in this time: %6d/%6d (dropped=%5d)"%(int(total_acquired),int(total_frame),int(total_frame-total_acquired))
		if total_acquired==0 and total_frame==0:
			return acq_rate_final
		else:
			return acq_rate_final

if __name__=="__main__":
	el=EigerLog()
	#el.saveLogs()
	#el.saveStreamLog()
	#el.countDrops()
	acq= el.checkDropDuring("2016-06-23 19:21:00","2016-06-23 19:24:00")
	print acq
