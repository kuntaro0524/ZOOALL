#!/bin/env python 
import sys, os, socket
import Gonio

if __name__ == "__main__":
    # host = '192.168.163.1'
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    gonio = Gonio.Gonio(s)

    while (1):
        gonio.rotatePhi(0)
        gonio.rotatePhi(360)

    s.close()
