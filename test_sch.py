import MultiCrystal

if __name__=="__main__":
	t=MultiCrystal.MultiCrystal()
	glist=[(0.0,0.0,1.0),(1.0,1.0,1.0)]
	sch_file="./pppp.sch"

	t.setCameraLength(200)
	t.setScanCondition(start_phi,end_phi,osc_width)
	t.setDir(dir)
	t.setAttIdx(att_idx)
	t.makeSchStr(sch_file,glist)
