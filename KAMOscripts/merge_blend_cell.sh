#!/bin/sh
# settings
dmin=$1
anomalous=false # true or false
lstin=formerge_goodcell.lst # list of XDS_ASCII.HKL files
use_ramdisk=true # set false if there is few memory or few space in /tmp
# _______/setting

kamo.multi_merge \
        workdir=blend_${dmin}A_framecc_b+B \
        lstin=${lstin} d_min=${dmin} anomalous=${anomalous} \
        space_group=None reference.data=None \
        program=xscale xscale.reference=bmin xscale.degrees_per_batch=None \
        reject_method=framecc+lpstats rejection.lpstats.stats=em.b+bfactor \
        clustering=blend blend.min_cmpl=95 blend.min_redun=8 blend.max_LCV=None blend.max_aLCV=None \
        max_clusters=None xscale.use_tmpdir_if_available=${use_ramdisk} \
        batch.engine=sge batch.par_run=merging batch.nproc_each=8 nproc=8 batch.sge_pe_name=par
