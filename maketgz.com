#!/bin/csh
pwd > pwd.log
tar cvfz $1.tgz XSCALE.INP XSCALE.LP *.log pwd.log ccp4/

echo $1
\mv -f $1.tgz /isilon/BL32XU/TMP/
chmod a+rw /isilon/BL32XU/TMP/$1.tgz
