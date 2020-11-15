#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 10:36:00 2020

@author: philippe
"""

# worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time
import telnetlib

from config import *

class TrxControl(QObject):
    

    print('begin')
    finished = pyqtSignal()
    freqReady = pyqtSignal(float)

    @pyqtSlot()
    def mainProcess(self): # A slot takes no params
        self.upDate = False
        self.timeout= 4
        self.run = True
        print(self.options)
        try :
            tnGqrx = telnetlib.Telnet(HOST,GQRX_PORT)
        except ConnectionRefusedError:
            print('ConnectionRefusedError: Activate remote control in GQRX')
            #self.ui.statusbar.showMessage('ConnectionRefusedError: Activate remote control in GQRX')
            return
        try :
            tnRig = telnetlib.Telnet(HOST,RIG_PORT)
        except ConnectionRefusedError:
            tnRig = None
            print('ConnectionRefusedError: make sure rigctld is running')

        # set initial frequency
        self.setFreq(tnGqrx,self.options['freq'])
        self.old_freq=self.options['freq']
        self.old_gqrx_freq = self.options['freq']
        self.old_rig_freq = self.options['freq']
        self.old_vfo = self.options['vfo']
        self.old_band = self.options['band']
        self.changeBand = False
        # set old modes
        self.old_rig_mode = 0
        self.old_gqrx_mode = 0
        self.changeMode = False
        # main loop 
        while self.run :
            self.upDateFreqs(tnRig,tnGqrx)
            self.upDateModes(tnRig,tnGqrx)
            self.upDateVFO(tnRig)
            self.upDateFreqMemories()
            time.sleep(0.1)
            
        self.finished.emit()
        
    def getFreq(self,tn) :
     tn.write(b'f\n')
     data=tn.read_until( b'\n',TIMEOUT)
     return int(data.decode('ASCII'))
 
    def setFreq(self,tn, freq) :
        build_msg = 'F ' + str(freq) + '\n'
        MESSAGE = bytes(build_msg, 'utf-8')
        tn.write(MESSAGE)
        data=tn.read_until( b'\n', TIMEOUT)
        return data
    
    def getMode(self,tn):
        tn.write(b'm\n')
        mode=tn.read_until( b'\n', self.timeout )
        width = tn.read_until( b'\n', self.timeout )
        return mode,width

    def setMode(self,tn, mode) :
        build_msg = 'M ' + str(mode) + ' 0\n'
        MESSAGE = bytes(build_msg, 'utf-8')
        tn.write(MESSAGE)
        data=tn.read_until( b'\n', self.timeout)
        return data
    
    def setVFO(self,tn,vfo):
        build_msg = 'V' + 'VFO' + vfo + '\n'
        MESSAGE = bytes(build_msg, 'utf-8')
        tn.write(MESSAGE)
        data=tn.read_until( b'\n', self.timeout)
        return data
    
    def setOptions(self,options):
        self.options=options
    
    def stop(self) :
        self.run = False 
        
    def upDateFreq(self):
        self.update = True 

    def roundToStep(self,doRound,freq,old_freq,step) :
        if not doRound or (freq != old_freq) :
            return freq
        print(doRound,freq,old_freq,step)
        n=freq/step
        n=round(n)
        print('initial',freq,n)
        if abs (freq - old_freq) >=step :
            print('>step',freq,n,int(n*step))
            return int(n*step)
        if freq > old_freq :
            print('>>',freq,n+1,int(n*step))
            return int((n+1)*step)
        elif freq < old_freq :
            print('<<',freq,n-1,int(n*step))
            return int((n-1)*step)
        print('rounded',int(n*step))
        return float(n*step)

        
        
    
    def upDateFreqs(self,tnRig,tnGqrx):
#        print('upDateFreqs')
#        if tnRig!=None :
            rnd = self.options['round']
            step = self.options['step']
            sync = self.options['sync']
                     
            if self.changeBand :
                gqrx_freq = self.options['freq']
                #set gqrx to new fequency
                rc = self.setFreq(tnGqrx, gqrx_freq)
                print('Return Code from GQRX: {0}'.format(rc))
                self.changeBand = False
            else :
                gqrx_freq = self.getFreq(tnGqrx)
                self.options['freq']=gqrx_freq
#                gqrx_freq = self.roundToStep(rnd,float(gqrx_freq),self.old_gqrx_freq,step)
#                if rnd :
#                    rc = self.setFreq(tnGqrx, gqrx_freq)
#                    self.old_gqrx_freq = gqrx_freq
#                    self.options['freq']=gqrx_freq
#                    if sync :
#                        self.upDate = True
#                    print('Return Code from GQRX: {0}'.format(rc))
            
            if (gqrx_freq != self.old_gqrx_freq and sync) or self.upDate :
                self.upDate = False
                
                print('gqrx_freq =',gqrx_freq)
                # set Hamlib to gqrx frequency
                try :
                        rc = self.setFreq(tnRig, float(gqrx_freq))
                        print('Return Code from Hamlib: {0}'.format(rc))
                        self.old_gqrx_freq = gqrx_freq
                        self.old_rig_freq = gqrx_freq
                        self.options['freq']=gqrx_freq
                except ValueError:
                     print('ValueError :',gqrx_freq)
            
            rig_freq = self.getFreq(tnRig)
           # print('rig_freq =',rig_freq, end=' ')

            if (rig_freq != self.old_rig_freq) and sync :
                # set gqrx to Hamlib frequency
                print('rig_freq =',rig_freq, end=' ')
                try :
                     if rnd :
                         rig_freq = self.roundToStep(rig_freq,step)
                     rc = self.setFreq(tnGqrx, float(rig_freq))
                     
                     print('Return Code from GQRX: {0}'.format(rc))
                     self.old_rig_freq = rig_freq
                     self.old_gqrx_freq = rig_freq
                     self.options['freq']=rig_freq
                except ValueError:
                     print('ValueError :',rig_freq)
                     
            self.freqReady.emit(gqrx_freq)
            
    def upDateModes(self,tnRig,tnGqrx): 
        if self.changeMode :
            self.setMode(tnGqrx,self.options['mode'])
            self.changeMode = False
        
        gqrx_mode,gqrx_width = self.getMode(tnGqrx)
        gqrx_mode= gqrx_mode.decode('ASCII').strip()
        self.gqrx_mode = gqrx_mode
        
        sync = self.options['sync']
        if not sync :
            return
        # sync modes 
        rig_mode,rig_width = self.getMode(tnRig)
        rig_mode = rig_mode.decode('ASCII').strip()
        self.rig_mode = rig_mode

            
        
        # mode rig -> gqrx
        if self.rig_mode != self.old_rig_mode :
            print('RIG mode :',rig_mode,'GQRX mode :', gqrx_mode)
            try :
                if modeRigtoGQRX[rig_mode] != gqrx_mode :
                    self.setMode(tnGqrx,modeRigtoGQRX[rig_mode])
                    print("RIG Mode --> GQRX mode")
                    self.gqrx_mode=self.old_gqrx_mode = modeRigtoGQRX[rig_mode]
            except KeyError:
                print('KeyError :',rig_mode)
            self.old_rig_mode = rig_mode


#        # mode gqrx -> rig
        if self.gqrx_mode != self.old_gqrx_mode :
            if self.gqrx_mode in modeGQRXtoRig :
                 self.setMode(tnRig,modeGQRXtoRig[gqrx_mode])
                 print("GQRX Mode --> RIG mode")
                 self.old_gqrx_mode = self.gqrx_mode
            self.old_rig_mode = rig_mode
            
    def upDateVFO(self,tnRig):
        if self.old_vfo != self.options['vfo']:
            self.setVFO(tnRig,self.options['vfo'])
            self.old_vfo = self.options['vfo']
            self.update = True
            
    def upDateFreqMemories(self):
       freq = self.options['freq']
       for band,limit in enumerate(band_limits) :
           if freq >= limit[0] and freq <=limit[1] :
               band_memories[band]=freq
               mode_memories[band]=self.gqrx_mode
               break
       current_band = self.options['band']
       if self.old_band != current_band :
           self.options['freq']= band_memories[current_band]
           self.options['mode']= mode_memories[current_band]
           self.old_band = current_band
           self.changeBand = True
           self.changeMode = True
           print(self.options)
