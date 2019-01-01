#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys
import struct
import socket
import os
from netaddr import IPAddress

class DlgTargetInput (QDialog):
    """DlgTargetInput inherits QDialog"""
    cidr = 24
    ip = "127.0.0.1"
    targets = []

    def __init__ ( self, parent = None ):
        QDialog.__init__( self, parent )
        uic.loadUi(resource_path('DlgTargetInput.ui'), self)
        self.setFixedSize(self.size())
        #
        self.btnOK.clicked.connect(self.accept)
        self.btnCancel.clicked.connect(self.reject)
        self.btnGenerate.clicked.connect(self.generateIP)
        #
        regexp = QRegExp('^([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])$')
        validator = QRegExpValidator(regexp)
        #
        self.txtIP1.textChanged.connect(self.check_state)
        self.txtIP1.textChanged.emit(self.txtIP1.text())        
        self.txtIP1.setValidator(validator)
        #
        self.txtIP2.textChanged.connect(self.check_state)
        self.txtIP2.textChanged.emit(self.txtIP2.text())
        self.txtIP2.setValidator(validator)
        #
        self.txtIP3.textChanged.connect(self.check_state)
        self.txtIP3.textChanged.emit(self.txtIP3.text())
        self.txtIP3.setValidator(validator)
        #
        self.txtIP4.textChanged.connect(self.check_state)
        self.txtIP4.textChanged.emit(self.txtIP4.text())
        self.txtIP4.setValidator(validator)
        #
        self.txtNM1.textChanged.connect(self.check_state)
        self.txtNM1.textChanged.emit(self.txtNM1.text())        
        self.txtNM1.setValidator(validator)
        #
        self.txtNM2.textChanged.connect(self.check_state)
        self.txtNM2.textChanged.emit(self.txtNM2.text())
        self.txtNM2.setValidator(validator)
        #
        self.txtNM3.textChanged.connect(self.check_state)
        self.txtNM3.textChanged.emit(self.txtNM3.text())
        self.txtNM3.setValidator(validator)
        #
        self.txtNM4.textChanged.connect(self.check_state)
        self.txtNM4.textChanged.emit(self.txtNM4.text())
        self.txtNM4.setValidator(validator)
        #
        self.radRange.toggled.connect(self.swapModeRange)
        self.radSubnet.toggled.connect(self.swapModeSubnet)
        self.rangeMode()

    def __del__ (self):
        self.ui = None
    
    def swapModeRange(self, enabled):
        if enabled:
            self.rangeMode()
        else:
            self.subnetMode()
    
    def swapModeSubnet(self, enabled):
        if enabled:
            self.subnetMode()
        else:
            self.rangeMode()
 
    def rangeMode(self):
        self.lblTargets.setText("0")
        self.btnOK.setEnabled(False)
        self.txtCIDR.hide()
        self.lblCIDR.hide()
        self.txtIP1.setText("192")
        self.txtIP2.setText("168")
        self.txtIP3.setText("1")
        self.txtIP4.setText("1")
        self.txtNM1.setText("192")
        self.txtNM2.setText("168")
        self.txtNM3.setText("1")
        self.txtNM4.setText("10")
        self.lblAddress.setText("<html><head/><body><p>&#8227; From address</p></body></html>")
        self.lblNetmask.setText("<html><head/><body><p>&#8227; To address</p></body></html>")

    def subnetMode(self):
        self.lblTargets.setText("0")
        self.btnOK.setEnabled(False)
        self.txtCIDR.show()
        self.lblCIDR.show()
        self.txtIP1.setText("192")
        self.txtIP2.setText("168")
        self.txtIP3.setText("1")
        self.txtIP4.setText("0")
        self.txtNM1.setText("255")
        self.txtNM2.setText("255")
        self.txtNM3.setText("255")
        self.txtNM4.setText("0")
        self.lblAddress.setText("<html><head/><body><p>&#8227; IP address</p></body></html>")
        self.lblNetmask.setText("<html><head/><body><p>&#8227; Netmask</p></body></html>")

    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
    
    def generateIP(self):
        if self.radRange.isChecked():
            self.genAddressesFromRange()
        else:
            self.computeCIDR()
            self.getIPAddressesFromCIDR()
        if int(self.lblTargets.text()) > 0:
            self.btnOK.setEnabled(True)
        else:
            self.btnOK.setEnabled(False)
            
    def computeCIDR(self):
        netmask = str(self.txtNM1.text()) + "." + str(self.txtNM2.text()) + "." + str(self.txtNM3.text()) + "." + str(self.txtNM4.text())
        self.cidr = IPAddress(netmask).netmask_bits()        
        self.txtCIDR.setText(str(self.cidr))

    def genAddressesFromRange(self):
        ipStart = str(self.txtIP1.text() + "." + self.txtIP2.text() + "." + self.txtIP3.text() + "." + self.txtIP4.text())
        ipEnd = str(self.txtNM1.text() + "." + self.txtNM2.text() + "." + self.txtNM3.text() + "." + self.txtNM4.text())
        start = struct.unpack('>I', socket.inet_aton(ipStart))[0]
        end = struct.unpack('>I', socket.inet_aton(ipEnd))[0]        
        self.targets = [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end + 1)]
        self.lblTargets.setText(str(len(self.targets)))

    def getIPAddressesFromCIDR(self):
        self.ip = str(self.txtIP1.text() + "." + self.txtIP2.text() + "." + self.txtIP3.text() + "." + self.txtIP4.text())
        host_bits = 32 - self.cidr
        i = struct.unpack('>I', socket.inet_aton(self.ip))[0] # note the endianness
        start = (i >> host_bits) << host_bits # clear the host bits
        end = start | ((1 << host_bits) - 1)
        self.lblTargets.setText(str(end - start - 2))

        # excludes the first and last address in the subnet
        self.targets = []
        for i in range(start + 1, end - 1):
            self.targets.append(socket.inet_ntoa(struct.pack('>I',i)))
            # print(socket.inet_ntoa(struct.pack('>I',i)))

def getTargets(parent = None):
    dialog = DlgTargetInput(parent)
    result = dialog.exec_()
    return (dialog.targets, result == QDialog.Accepted)
    

# Define function to import external files when using PyInstaller.
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
