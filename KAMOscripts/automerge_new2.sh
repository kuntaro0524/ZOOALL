#Currently, use automerge_new.sh please
kamo.auto_multi_merge \
  csv=sample2.csv \
  workdir=$PWD \
  prefix=merge2h_ \
  cell_method=reindex \
  merge.max_clusters=15 \
  merge.d_min_start=1.4 \
  merge.clustering=cc \
  merge.cc_clustering.min_acmpl=90 \
  merge.cc_clustering.min_aredun=2 \
  batch.engine=sge \
  merge.batch.engine=sge \
  merge.batch.par_run=merging \
#  unit_cell="63     48    342     90     90.65  90.00" space_group=p2

