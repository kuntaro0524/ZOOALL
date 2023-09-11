#CCC
kamo.auto_multi_merge \
  csv=data_proc.csv \
  workdir=$PWD \
  prefix=merge_cc_ \
  cell_method=reindex \
  merge.max_clusters=50 \
  merge.d_min_start=2.0 \
  merge.clustering=cc \
  merge.cc_clustering.min_acmpl=95 \
  merge.cc_clustering.min_aredun=16 \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \ &
#  unit_cell="63     48    342     90     90.65  90.00" space_group=p2


# BLEND
kamo.auto_multi_merge \
  csv=data_proc.csv \
  workdir=$PWD \
  prefix=merge_blend_ \
  cell_method=reindex \
  merge.max_clusters=50 \
  merge.d_min_start=2.0 \
  merge.clustering=blend \
  merge.cc_clustering.min_acmpl=95 \
  merge.cc_clustering.min_aredun=16 \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \ &
#  unit_cell="63     48    342     90     90.65  90.00" space_group=p2
