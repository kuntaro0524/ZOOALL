import *

heatmap=SHIKAhm.readSummaryDat(raster_path)

# For Multi
crystal_list=SHIKAhm.getCrystals(mode="multi",dist_thresh=0.015)

# For helical 
crystal_list=SHIKAhm.getCrystals(mode="bunch",dist_thresh=0.015)

def getCrystals(self,mode,dist_thresh):
	# For multiple crystals in the loop
	# dist_thresh is used as 'NG' distance for neighbor one
	if mode=="multi":
		crystals=self.analyzeMulti(self.heatmap,dist_thresh)

	# For detecting bunch of pixels -> one crystal
	# dist_thresh is used as 'OK' distance for successive crystal region
	elif mode=="bunch":
		crystals=self.analyzeBunch(self.heatmap,dist_thresh)

def getHeatMap(self,diffscanlog,summary_dat):
