#!/bin/csh

# ssh -X vserv2
python back_cam_server.py
