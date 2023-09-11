#!/bin/csh

set dmin=2.5
set dmin_cc=3.5

Rscript ~/PPPP/10.Zoo/filter_cell.R

cp ~/PPPP/10.Zoo/merge_blend_cell.sh .
cp ~/PPPP/10.Zoo/merge_ccc_cell.sh .

echo $dmin $dmin_cc
sh merge_blend_cell.sh $dmin
sh merge_ccc_cell.sh $dmin $dmin_cc
