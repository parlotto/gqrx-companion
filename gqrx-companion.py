#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 10:06:05 2020

@author: philippe
to update ui run : pyuic5 mainwindow.ui -x -o gui.py

"""

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import gui  # import du fichier gui.py généré par pyuic5
import sys
from PyQt5.QtCore import QThread
from config import VERSION
import trx_control

# steps in kHz
stepsList = ['5','8.33','9','10','12.5','25','50','100']



class MyWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = gui.Ui_MainWindow()
        self.ui.setupUi(self)
      
        self.options={'freq':14e6,'mode':'USB','round':False,'sync':False,'step':1000.0,\
                      'vfo':'A','band':-1}
        self.setWindowTitle("Gqrx-companion "+VERSION)
        
        self.ui.pushButtonVfoAB.clicked.connect(self.changeVFO)

        self.ui.checkBoxRoundToStep.clicked.connect(self.roundToStep_clicked)
        self.ui.comboBoxStepList.currentIndexChanged.connect(self.on_step_changed)
        self.ui.checkBoxSyncHamlib.clicked.connect(self.on_syncHamlibClicked)
        self.ui.pushButton138.clicked.connect(lambda:self.changeBand(0))
        self.ui.pushButton472.clicked.connect(lambda:self.changeBand(1))
        self.ui.pushButton1M8.clicked.connect(lambda:self.changeBand(2))
        self.ui.pushButton3M5.clicked.connect(lambda:self.changeBand(3))
        self.ui.pushButton5.clicked.connect(lambda:self.changeBand(4))
        self.ui.pushButton7.clicked.connect(lambda:self.changeBand(5))
        self.ui.pushButton10.clicked.connect(lambda:self.changeBand(6))
        self.ui.pushButton14.clicked.connect(lambda:self.changeBand(7))
        self.ui.pushButton18.clicked.connect(lambda:self.changeBand(8))
        self.ui.pushButton21.clicked.connect(lambda:self.changeBand(9))
        self.ui.pushButton24.clicked.connect(lambda:self.changeBand(10))
        self.ui.pushButton28.clicked.connect(lambda:self.changeBand(11))
        self.ui.pushButton50.clicked.connect(lambda:self.changeBand(12))
        self.ui.pushButtonG1.clicked.connect(lambda:self.changeBand(13))
        self.ui.pushButtonG2.clicked.connect(lambda:self.changeBand(14))
        
        self.step = 1e3
        for step in stepsList:
            self.ui.comboBoxStepList.addItem(step)
#        # un clic sur un élément de la liste appellera la méthode 'on_item_changed'
#        self.ui.listWidget.currentItemChanged.connect(self.on_item_changed)

        # on affiche un texte en bas de la fenêtre (status bar)
        # 1 - create Worker and Thread inside the Form

        self.obj = trx_control.TrxControl()  # no parent!
        self.thread = QThread()  # no parent!
        
#        self.options={'freq':121e6,'step':self.step,'round':True}
        self.obj.setOptions(self.options)
       # 2 - Connect Worker`s Signals to Form method slots to post data.
        self.obj.freqReady.connect(self.onFreqReady)

       # 3 - Move the Worker object to the Thread object
        self.obj.moveToThread(self.thread)

       # 4 - Connect Worker Signals to the Thread slots
        self.obj.finished.connect(self.thread.quit)

       # 5 - Connect Thread started signal to Worker operational slot method
        self.thread.started.connect(self.obj.mainProcess)

       # * - Thread finished signal will close the app if you want!
       #self.thread.finished.connect(app.exit)

       # 6 - Start the thread
        self.thread.start()


        self.ui.statusbar.showMessage("init done")
        
        
    def onFreqReady(self, freq):
        self.ui.statusbar.showMessage("thread "+str(freq))
        self.ui.doubleSpinBoxFreq.setValue(freq/1e3)

    def roundToStep_clicked(self):
        self.options['round'] = self.ui.checkBoxRoundToStep.isChecked()
        #print('options=',self.options) 
        self.on_step_changed()
        self.obj.setOptions(self.options)
        self.obj.upDateFreq()
        
    def changeVFO(self):
        if self.options['vfo']=='A':
            self.options['vfo']='B'
        else :
            self.options['vfo']='A'
        self.obj.setOptions(self.options)
        self.obj.upDateFreq()
        
    def changeBand(self,band_number):
        print('test',band_number)
        self.options['band']=band_number
        self.obj.setOptions(self.options)
        
        
    def on_step_changed(self):
        print('current item in list',self.ui.comboBoxStepList.currentText())
        if self.ui.checkBoxRoundToStep.isChecked() :
            if stepsList[self.ui.comboBoxStepList.currentIndex()]=='8.33' :
                self.step = 25e3/3
            else :
                self.step = 1e3*float(stepsList[self.ui.comboBoxStepList.currentIndex()])
        else :
           self.step=1e3
        self.ui.doubleSpinBoxFreq.setSingleStep(self.step/1e3)
        self.options['step']=self.step
        self.obj.setOptions(self.options)
        print('current step',self.step)
        print('options=',self.options)
        self.obj.upDateFreq()

    def on_syncHamlibClicked(self):
         self.options['sync']= self.ui.checkBoxSyncHamlib.isChecked()
         self.obj.setOptions(self.options)
         print('options=',self.options)
    
    def closeEvent(self, event):
        print('close')
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close gqrx-companion ?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.obj.stop()
            event.accept()
            print('Window closed')
        else:
            event.ignore()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
