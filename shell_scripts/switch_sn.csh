#!/bin/csh

# Membrane protein (LCP crystal)
#set SN="sn5.5"

# soluble protein
#set SN="sn4"

# Others
#set SN="sn6"
#set SN="sn8"
set SN="sn7"

ssh admin45@192.168.231.7 << EOC
ls /oys/xtal/cheetah/eiger-zmq/boost_python/config*
ln -sf /oys/xtal/cheetah/eiger-zmq/boost_python/config_manager.py.$SN /oys/xtal/cheetah/eiger-zmq/boost_python/config_manager.py
EOC

ssh admin45@192.168.231.11 << EOC
ls /oys/xtal/cheetah/eiger-zmq/boost_python/config*
ln -sf /oys/xtal/cheetah/eiger-zmq/boost_python/config_manager.py.$SN /oys/xtal/cheetah/eiger-zmq/boost_python/config_manager.py
EOC

/usr/local/bss/startcheetah.sh
