#!/bin/bash
# 171114 changed
echo "\n\n" | /usr/local/bss/bss --server --console  --admin

# After BSS shutdown
sleep 1
##ssh 192.168.163.6 "killall $VIDEOSRV"    # for ARTRAY
killall $VIDEOSRV      # for DFK72 YK@190315
sleep 1
killall bss

END:
