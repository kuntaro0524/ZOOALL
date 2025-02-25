import csv
import sys,os

fff=open(sys.argv[1],"ru")
reader=csv.reader(fff)
header=next(reader)

blend_csv_list=[]

for row in reader:
	blend_path="%s-blend"%row[3]
	row[3]=blend_path
	blend_csv_list.append(row)

fff=open(sys.argv[1],"ru")
reader=csv.reader(fff)
header=next(reader)

cc_csv_list=[]
for row in reader:
	cc_path="%s-cc"%row[3]
	row[3]=cc_path
	cc_csv_list.append(row)

# For BLEND clustering CSV
prefix=sys.argv[1].replace(".csv","")
newfile="%s.blend.csv"%prefix
ofile=open(newfile,"w")
writer=csv.writer(ofile,lineterminator="\n")
writer.writerow(header)
writer.writerows(blend_csv_list)

# Prep for blend auto merge
cwd=os.getcwd()
bfile=open("00_blend_auto.sh","w")
bfile.write("/oys/xtal/cctbx/snapshots/upstream/build/bin/kamo.auto_multi_merge \\\n")
bfile.write("csv=%s \\\n"%newfile)
bfile.write("workdir=$PWD \\\n")
bfile.write("prefix=merge_ \\\n")
bfile.write("datadir=%s \\\n"%cwd)
bfile.write("postrefine=False \\\n")
bfile.write("merge.max_clusters=10 \\\n")
bfile.write("merge.d_min_start=3.0 \\\n")
bfile.write("merge.clustering=blend \\\n")
bfile.write("merge.blend.min_acmpl=90 \\\n")
bfile.write("merge.blend.min_aredun=2 \\\n")
bfile.write("batch.engine=sge \\\n")
bfile.write("merge.batch.engine=sge \\\n")
bfile.write("merge.batch.par_run=merging \\\n")

ofile.close()

# for CC clustering CSV
newfile="%s.cc.csv"%prefix
ofile=open(newfile,"w")
writer=csv.writer(ofile,lineterminator="\n")
writer.writerow(header)
writer.writerows(cc_csv_list)

# Prep for cc clustering
cwd=os.getcwd()
bfile=open("01_cc_auto.sh","w")
bfile.write("/oys/xtal/cctbx/snapshots/upstream/build/bin/kamo.auto_multi_merge \\\n")
bfile.write("csv=%s \\\n"%newfile)
bfile.write("workdir=$PWD \\\n")
bfile.write("prefix=merge_ \\\n")
bfile.write("datadir=%s \\\n"%cwd)
bfile.write("postrefine=False \\\n")
bfile.write("merge.max_clusters=10 \\\n")
bfile.write("merge.d_min_start=3.0 \\\n")
bfile.write("merge.clustering=cc \\\n")
bfile.write("merge.cc_clustering.min_acmpl=90 \\\n")
bfile.write("merge.cc_clustering.min_aredun=2 \\\n")
bfile.write("batch.engine=sge \\\n")
bfile.write("merge.batch.engine=sge \\\n")
bfile.write("merge.batch.par_run=merging \\\n")

ofile.close()
