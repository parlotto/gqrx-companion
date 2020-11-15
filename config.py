#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 11:58:56 2020

@author: philippe
"""
VERSION='0.1'
HOST = "localhost"
RIG_PORT = 4532
GQRX_PORT = 7356
FLDIGI_PORT = 7362
TIMEOUT = 4

# mode conversion between GQRX and my TS590 :

modeRigtoGQRX = {'AM':'AM', 'CW':'CWU', 'CWR':'CWL',\
                   'USB':'USB','PKTUSB':'USB','LSB':'LSB','PKTLSB':'LSB',\
                   'FM':'FM','PKTFM':'FM', 'RTTY':'USB','RTTYR':'LSB'}

modeGQRXtoRig = {'AM':'AM', 'CWU':'CW', 'CWL':'CWR',\
                   'USB':'USB','LSB':'LSB','FM':'FM'}

# band limits
band_limits= [(100e3,150e3),(450e3,550e3),(1.6e6,2e6),(3e6,4e6),(5e6,5.5e6),\
              (6.5e6,7.5e6),(9.5e6,10.5e6),(13.5e6,14.5e6),(18.0,18.4),(20.5e6,21.6e6),\
              (24.5e6,25.5e6),(26.5e6,30.5e6),(45e6,55e6),(8.0,8.5),(12.0,12.5)]

band_memories = [138e3,472e3,1.85e6,3.55e6,5.352e6,7.025e6,10.125e6,14.025e6,18.073e6,21.025e6,\
                 24.895e6,28.025e6,50.09e6,8.1e6,12.1e6]

mode_memories = ['USB']*len(band_memories)
