#!/bin/sh
# settings
dmin=4.0 # resolution
clustering_dmin=7.0
anomalous=false # true or false
lstin=formerge_goodcell.lst # list of XDS_ASCII.HKL files
use_ramdisk=true # set false if there is few memory or few space in /tmp
max_cluster=50
min_comp=95
min_red=8
# _______/setting

kamo.multi_merge \
        workdir=ccc_${dmin}A_framecc_b+B_1deg \
        lstin=${lstin} d_min=${dmin} anomalous=${anomalous} \
        space_group=None reference.data=None \
        program=xscale xscale.reference=bmin xscale.degrees_per_batch=1.0 \
        reject_method=framecc+lpstats rejection.lpstats.stats=em.b+bfactor \
        clustering=cc cc_clustering.d_min=${clustering_dmin} cc_clustering.b_scale=false cc_clustering.use_normalized=false \
        cc_clustering.min_cmpl=${min_comp} cc_clustering.min_redun=${min_red} \
        max_clusters=${max_cluster} xscale.use_tmpdir_if_available=${use_ramdisk} \
        batch.engine=sge batch.par_run=merging batch.nproc_each=8 nproc=8 batch.sge_pe_name=par &


kamo.multi_merge \
        workdir=ccc_${dmin}A_framecc_b+B \
        lstin=${lstin} d_min=${dmin} anomalous=${anomalous} \
        space_group=None reference.data=None \
        program=xscale xscale.reference=bmin xscale.degrees_per_batch=none \
        reject_method=framecc+lpstats rejection.lpstats.stats=em.b+bfactor \
        clustering=cc cc_clustering.d_min=${clustering_dmin} cc_clustering.b_scale=false cc_clustering.use_normalized=false \
        cc_clustering.min_cmpl=${min_comp} cc_clustering.min_redun=${min_red} \
        max_clusters=${max_cluster} xscale.use_tmpdir_if_available=${use_ramdisk} \
        batch.engine=sge batch.par_run=merging batch.nproc_each=8 nproc=8 batch.sge_pe_name=par &


kamo.multi_merge \
        workdir=ccc_${dmin}A_framecc_b+B_1deg_normalized \
        lstin=${lstin} d_min=${dmin} anomalous=${anomalous} \
        space_group=None reference.data=None \
        program=xscale xscale.reference=bmin xscale.degrees_per_batch=1.0 \
        reject_method=framecc+lpstats rejection.lpstats.stats=em.b+bfactor \
        clustering=cc cc_clustering.d_min=${clustering_dmin} cc_clustering.b_scale=false cc_clustering.use_normalized=true \
        cc_clustering.min_cmpl=${min_comp} cc_clustering.min_redun=${min_red} \
        max_clusters=${max_cluster} xscale.use_tmpdir_if_available=${use_ramdisk} \
        batch.engine=sge batch.par_run=merging batch.nproc_each=8 nproc=8 batch.sge_pe_name=par &

kamo.multi_merge \
        workdir=blend_${dmin}A_framecc_b+B_normal \
        lstin=${lstin} d_min=${dmin} anomalous=${anomalous} \
        space_group=None reference.data=None \
        program=xscale xscale.reference=bmin xscale.degrees_per_batch=None \
        reject_method=framecc+lpstats rejection.lpstats.stats=em.b+bfactor \
        clustering=blend blend.min_cmpl=$min_comp blend.min_redun=$min_red blend.max_LCV=None blend.max_aLCV=None \
        max_clusters=None xscale.use_tmpdir_if_available=${use_ramdisk} \
        batch.engine=sge batch.par_run=merging batch.nproc_each=8 nproc=8 batch.sge_pe_name=par &

kamo.multi_merge \
        workdir=blend_${dmin}A_framecc_b+B_1deg \
        lstin=${lstin} d_min=${dmin} anomalous=${anomalous} \
        space_group=None reference.data=None \
        program=xscale xscale.reference=bmin xscale.degrees_per_batch=1.0 \
        reject_method=framecc+lpstats rejection.lpstats.stats=em.b+bfactor \
        clustering=blend blend.min_cmpl=$min_comp blend.min_redun=$min_red blend.max_LCV=None blend.max_aLCV=None \
        max_clusters=None xscale.use_tmpdir_if_available=${use_ramdisk} \
        batch.engine=sge batch.par_run=merging batch.nproc_each=8 nproc=8 batch.sge_pe_name=par &
