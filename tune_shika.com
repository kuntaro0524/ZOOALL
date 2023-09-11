/oys/xtal/cheetah/eiger-zmq/bin/cheetah.local_singles $1 --nproc=64 --min-pixcount=2 --min-snr=3 --local-bgradius=3 --adc-threshold=10

  #--nproc=NPROC         
  #--cut-roi             
  #--output=OUTPUT       
  #--gen-adx             
  #--dmin=D_MIN          
  #--dmax=D_MAX          
  #--adc-threshold=ADCTHRESH
  #--min-snr=MINSNR      
  #--min-pixcount=MINPIXCOUNT
  #--max-pixcount=MAXPIXCOUNT
  #--local-bgradius=LOCALBGRADIUS
  #--min-peaksep=MINPEAKSEPARATION
  #--algorithm=ALGORITHM
  #--binning=BINNING     
