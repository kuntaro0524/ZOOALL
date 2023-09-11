#!/bin/csh
a2ps $1 -l 110 -M A4 -o tmp.ps
ps2pdf -sPAPERSIZE=a4 tmp.ps
mv -f tmp.pdf $2
