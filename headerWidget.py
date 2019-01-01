#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4 import QtCore

import mainwindow as mw
import icons

class headerWidget( QWidget ):
    def __init__ ( self, parent = None ):
        QWidget.__init__( self, parent )
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.font=QFont()
        self.font.setBold(True)
        self.css = "background-color : #6992c2; color : black;"
        #
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        # LABEL PACKETS LOST
        self.lPacketsLost = QLabel("Lost (%)")
        self.lPacketsLost.setFont(self.font)
        self.lPacketsLost.setStyleSheet(self.css)
        self.lPacketsLost.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)        
        # LABEL HOSTNAME
        self.lTargetHost = QLabel("Hostname")
        self.lTargetHost.setFont(self.font)
        self.lTargetHost.setStyleSheet(self.css)
        self.lTargetHost.setFixedWidth(200)
        self.lTargetHost.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # LABEL TARGET IP
        self.lTargetIP = QLabel("IP Address")
        self.lTargetIP.setFont(self.font)
        self.lTargetIP.setStyleSheet(self.css)
        self.lTargetIP.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # LABEL PING VALUE
        self.lPingValue = QLabel("Ping (ms)")
        self.lPingValue.setFont(self.font)
        self.lPingValue.setStyleSheet(self.css)
        self.lPingValue.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # LABEL MAX VALUE
        self.lMaxValue = QLabel("Max (ms)")
        self.lMaxValue.setFont(self.font)
        self.lMaxValue.setStyleSheet(self.css)
        self.lMaxValue.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # LABEL MIN VALUE
        self.lMinValue = QLabel("Min (ms)")
        self.lMinValue.setFont(self.font)
        self.lMinValue.setStyleSheet(self.css)
        self.lMinValue.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # LABEL AVG VALUE
        self.lAvgValue = QLabel("Average (ms)")
        self.lAvgValue.setFont(self.font)
        self.lAvgValue.setStyleSheet(self.css)
        self.lAvgValue.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # LABEL TICKs
        self.lTick = QLabel("Requests")
        self.lTick.setFont(self.font)
        self.lTick.setStyleSheet(self.css)
        self.lTick.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        #
        self.btnClear = QPushButton()
        icon = QIcon(":/png/16x16/Trash.png")
        self.btnClear.setFixedSize(icon.availableSizes()[0])
        self.btnClear.setIcon(icon)
        self.btnClear.clicked.connect(self.parent.clearTargets)
        #
        self.layout.addWidget(self.lPacketsLost)
        self.layout.addWidget(self.lTargetHost)
        self.layout.addWidget(self.lTargetIP)
        self.layout.addWidget(self.lPingValue)
        self.layout.addWidget(self.lAvgValue)
        self.layout.addWidget(self.lMinValue)
        self.layout.addWidget(self.lMaxValue)                
        self.layout.addWidget(self.lTick)
        self.layout.addWidget(self.btnClear)
