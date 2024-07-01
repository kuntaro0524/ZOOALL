import sys,os,math,glob

root_path=sys.argv[1]
dires=["./","vscan/"]
prefix=sys.argv[2]
idx=0

comfile=open("comcom.com","w")
comfile.write("#!/bin/csh\n")
comfile.write("#$ -cwd\n")

def getBestGrid(selefile):
	#print selefile
	lines=open(selefile,"r").readlines()
	cols=lines[1].split()
	#print cols
	imgfile=cols[0]
	score=cols[5]
	#print imgfile,score
	idx=imgfile.rfind("_")
	return int(imgfile[idx+1:].replace(".img",""))

print dires
pnglist=""
for di in dires:
	filepath="%s/%s"%(root_path,di)
	#print filepath
	selelist=glob.glob("%s/_spotfinder/*selected*.dat"%filepath)
	masterlist=glob.glob("%s/*master*"%filepath)
	print "PNG file searching..."
	print "%s/_spotfinder/ "%filepath
	pngfile=glob.glob("%s/_spotfinder/*map*png"%filepath)
	pnglist+="%s "%pngfile[0]

	# Convert command

	for masterfile,selefile in zip(masterlist,selelist):
		imgnum=getBestGrid(selefile)
		outfile="check%02d.cbf"%idx
		comfile.write( "eiger2cbf %s %d:%d %s\n"%(masterfile,imgnum,imgnum,outfile))
		comfile.write( "eiger2cbf %s %d:%d %s\n"%(masterfile,imgnum,imgnum,outfile))
		jpgfile=outfile.replace(".cbf",".jpg")
		comfile.write( "adxv -sa -contrast -1 4 %s %s\n"%(outfile,jpgfile))
		idx+=1

comfile.write("montage -tile 2x2 -geometry 4000x4000 check00.jpg check01.jpg %s tmp.jpg\n\n"%pnglist)
comfile.write("sleep 5\n")
comfile.write("convert -pointsize 300 -gravity north -font Times-Roman -fill black -annotate 0 \"%s\" tmp.jpg matome.jpg"%prefix)
