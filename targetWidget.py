#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from PyQt4.QtGui import *
from PyQt4 import QtCore
import subprocess
import re
import os
import sys
import socket
import MyLabel
import settings
from time import strftime


import smtplib
try:
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
except:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText


class targetWidget( QWidget ):
    
    TYPE_MAIL_DEAD = 0
    TYPE_MAIL_ALIVE = 1
    
    def __init__ ( self, target, order, parent = None ):
        QWidget.__init__( self, parent )
        setattr(self, "target", target)
        setattr(self, "targetIP", "")
        setattr(self, "targetHostname", "")
        setattr(self, "parent", parent)
        setattr(self, "order", order)
        setattr(self, "pingValue", 0)
        setattr(self, "avgValue", 0)
        setattr(self, "maxValue", 0)
        setattr(self, "minValue", 999999)
        setattr(self, "sumValue", 0)
        setattr(self, "tick", 0)
        setattr(self, "pLost", 0)
        setattr(self, "percent", 0)
        setattr(self, "unreachablePing", 0)
        setattr(self, "mailSent", False)
        self.initUI()

    def resetCounters(self):
        setattr(self, "pingValue", 0)
        setattr(self, "avgValue", 0)
        setattr(self, "maxValue", 0)
        setattr(self, "minValue", 999999)
        setattr(self, "sumValue", 0)
        setattr(self, "tick", 0)
        setattr(self, "pLost", 0)
        setattr(self, "percent", 0)
        setattr(self, "unreachablePing", 0)
        setattr(self, "mailSent", False)

    def initUI(self):
        if self.order % 2 == 0:
            self.css = "background-color : #ccdee2; color : black;"
        else:
            self.css = "background-color : #b3b8bf; color : black;"        
        #
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refreshValue)
        self.timer.start(settings.db['TIMER_PING'])
        #
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        #
        # self.lOrder = QLabel(" %05d" % self.order)
        # self.lOrder.setStyleSheet(self.css)
        #
        if self.isValidIPAddress(self.target):
            self.targetIP = self.target
            try:
                self.targetHostname = socket.gethostbyaddr(str(self.targetIP))[0]
            except:
                self.targetHostname = "unknown"
        else:
            self.targetIP = socket.gethostbyname(str(self.target))
            self.targetHostname = self.target
         
        self.lPacketsLost = QLabel()
        self.lPacketsLost.setStyleSheet(self.css)
        self.lPacketsLost.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        #
        self.lTargetIP = QLabel(self.targetIP)
        self.lTargetIP.setStyleSheet(self.css)
        myFont=QFont()
        myFont.setBold(True)
        self.lTargetIP.setFont(myFont)
        self.lTargetIP.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        #
        self.lTargetHost = MyLabel.MyLabel(self.targetHostname)
        self.lTargetHost.setStyleSheet(self.css)
        myFont=QFont()
        myFont.setBold(True)
        self.lTargetHost.setFont(myFont)
        self.lTargetHost.setFixedWidth(200)
        self.lTargetHost.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.lPingValue = QLabel(str(self.pingValue))
        self.lPingValue.setStyleSheet(self.css + " border: 2px solid grey;")
        self.lPingValue.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        
        self.lMaxValue = QLabel(str(self.maxValue))
        self.lMaxValue.setStyleSheet(self.css + " border: 2px solid grey;")
        self.lMaxValue.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        
        self.lMinValue = QLabel(str(self.minValue))
        self.lMinValue.setStyleSheet(self.css + " border: 2px solid grey;")
        self.lMinValue.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        
        self.lAvgValue = QLabel(str(self.avgValue))
        self.lAvgValue.setStyleSheet(self.css + " border: 2px solid grey;")
        self.lAvgValue.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        
        # LABEL TICKs
        self.lTick = QLabel(" %d" % self.tick)
        self.lTick.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.lTick.setStyleSheet(self.css + " border: 2px solid grey;")
        #
        self.btnClear = QPushButton()
        icon = QIcon(":/png/16x16/Trash.png")
        self.btnClear.setFixedSize(icon.availableSizes()[0])
        self.btnClear.setIcon(icon)
        self.btnClear.clicked.connect(lambda: self.parent.clearTarget(self.order))
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
        # self.layout.addStretch()
        # self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def setOrder(self, n):
        setattr(self, "order", n)
        self.refreshValue()
        
    def setInterval(self, n):
        self.timer.setInterval(n)
        self.refreshValue()
        
    def sendWarnMessage(self, typeMail):
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.db['SMTP_USER']
        msg['To'] = settings.db['SMTP_RECIPIENTS']
        if typeMail == self.TYPE_MAIL_DEAD :
            msg['Subject'] = 'Dead target detected (' + self.target + ')'
            # Create the body of the message (a plain-text and an HTML version).            
            text = """\
            Hello from Pyng,\n\n
            The following target is no more responding :\n\n
            Target IP\t{0}\n
            Target hostname\t{1}\n
            Event date\t{2}\n
            Probe source\t{3}\n\n
            Best regards,\n\n
            The Pyng Team.\n
            """.format(self.targetIP, self.targetHostname, strftime("%Y-%m-%d %H:%M:%S"), socket.gethostname())
            
            html = """\
            <html>
              <head></head>
              <body>
                <p>Hello from Pyng,<br><br>
                    The following target is no more responding :<br>
                    <center>
                    <table>
                        <tr><td>Target IP</td><td><b>{0}</b></td></tr>
                        <tr><td>Target hostname</td><td><b>{1}</b></td></tr>
                        <tr><td>Event date</td><td><b>{2}</b></td></tr>
                        <tr><td>Probe source</td><td><b>{3}</b></td></tr>
                   </table>
                   </center>
                   <br>
                   Best regards,<br><br>
                   <i>The Pyng Team.</i>
                </p>
              </body>
            </html>
            """.format(self.targetIP, self.targetHostname, strftime("%Y-%m-%d %H:%M:%S"), socket.gethostname())
        else:
            msg['Subject'] = 'Target is back to life (' + self.target + ')'
            # Create the body of the message (a plain-text and an HTML version).            
            text = """\
            Hello from Pyng,\n\n
            The following target is back to life :\n\n
            Target IP\t{0}\n
            Target hostname\t{1}\n
            Event date\t{2}\n
            Probe source\t{3}\n\n
            Best regards,\n\n
            The Pyng Team.\n
            """.format(self.targetIP, self.targetHostname, strftime("%Y-%m-%d %H:%M:%S"), socket.gethostname())
            
            html = """\
            <html>
              <head></head>
              <body>
                <p>Hello from Pyng,<br><br>
                    The following target is back to life :<br>
                    <center>
                    <table>
                        <tr><td>Target IP</td><td><b>{0}</b></td></tr>
                        <tr><td>Target hostname</td><td><b>{1}</b></td></tr>
                        <tr><td>Event date</td><td><b>{2}</b></td></tr>
                        <tr><td>Probe source</td><td><b>{3}</b></td></tr>
                   </table>
                   </center>
                   <br>
                   Best regards,<br><br>
                   <i>The Pyng Team.</i>
                </p>
              </body>
            </html>
            """.format(self.targetIP, self.targetHostname, strftime("%Y-%m-%d %H:%M:%S"), socket.gethostname())

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        mailserver = smtplib.SMTP(settings.db['SMTP_SERVER'], int(settings.db['SMTP_PORT']))
        if settings.db['SMTP_TLS']==True:
            mailserver.ehlo()
            mailserver.starttls()
        mailserver.ehlo()
        mailserver.login(settings.db['SMTP_USER'], settings.db['SMTP_PASSWORD'])
        mailserver.sendmail(settings.db['SMTP_USER'], settings.db['SMTP_RECIPIENTS'].split(";"), msg.as_string())
        mailserver.quit()
        self.parent.statusBar.showMessage("Warning mail sent", settings.db['TIMER_STATUS'])
        
    def refreshValue(self):
        if self.order % 2 == 0:
            self.css = "background-color : #ccdee2; color : black;"
        else:
            self.css = "background-color : #b3b8bf; color : black;"
        #
        if self.parent.isRunning == True:
            #
            self.lTargetIP.setStyleSheet(self.css)
            self.lTargetHost.setStyleSheet(self.css)
            #
            self.pingValue = self.pingMe()
            if self.pLost != 0:
                percent = (self.pLost / self.tick) * 100
                if percent >= self.percent:
                    self.lPacketsLost.setStyleSheet(self.css + "color : red;")
                else:
                    self.lPacketsLost.setStyleSheet(self.css + "color : green;")
                self.lPacketsLost.setText("%d" % percent)
                self.percent = percent
            else:
                self.lPacketsLost.setStyleSheet(self.css)
            # LABEL PING VALUE
            if self.pingValue == -1:
                self.lPingValue.setText("Timeout")
                self.css_status = "background-color : #CD0000; color : black;"
                self.lPingValue.setStyleSheet(self.css_status + " border: 2px solid grey;")
                #
                # MANAGE "NO DEAD TARGETS" OPTION
                #
                self.unreachablePing = self.unreachablePing + 1
                if self.unreachablePing >= settings.db['UNREACHABLE_PING']:
                    if self.parent.chkWarnDeadTargets.isChecked() and self.mailSent == False:
                        self.parent.statusBar.showMessage("Dead target %s" % self.target, settings.db['TIMER_STATUS'])
                        self.sendWarnMessage(self.TYPE_MAIL_DEAD)
                        self.mailSent = True
                    if self.parent.chkNoDeadTargets.isChecked():
                        self.parent.clearTarget(self.order)
            else:
                if self.unreachablePing >= settings.db['UNREACHABLE_PING']:
                    if self.parent.chkWarnDeadTargets.isChecked():
                        self.parent.statusBar.showMessage("Target %s is back to life" % self.target, settings.db['TIMER_STATUS'])
                        self.sendWarnMessage(self.TYPE_MAIL_ALIVE)                        
                self.mailSent = False
                self.unreachablePing = 0
                self.lPingValue.setText("%d" % self.pingValue)
                self.css_status = "background-color : #A5D496; color : black;"
                if self.pingValue > settings.db['STATUS_GREEN'] and self.pingValue <= settings.db['STATUS_YELLOW']:
                    self.css_status = "background-color : #FFAE19; color : black;"
                else:
                    if self.pingValue > settings.db['STATUS_YELLOW']:
                        self.css_status = "background-color : #CD0000; color : black;"
                self.lPingValue.setStyleSheet(self.css_status + " border: 2px solid grey;")
            # LABEL MAX VALUE
            self.lMaxValue.setText("%d" % self.maxValue)
            self.css_status = "background-color : #A5D496; color : black;"
            if self.maxValue > settings.db['STATUS_GREEN'] and self.maxValue <= settings.db['STATUS_YELLOW']:
                self.css_status = "background-color : #FFAE19; color : black;"
            else:
                if self.maxValue > settings.db['STATUS_YELLOW']:
                    self.css_status = "background-color : #CD0000; color : black;"
            self.lMaxValue.setStyleSheet(self.css_status + " border: 2px solid grey;")
            # LABEL MIN VALUE
            self.lMinValue.setText("%d" % self.minValue)
            self.css_status = "background-color : #A5D496; color : black;"
            if self.minValue > settings.db['STATUS_GREEN'] and self.minValue <= settings.db['STATUS_YELLOW']:
                self.css_status = "background-color : #FFAE19; color : black;"
            else:
                if self.minValue > settings.db['STATUS_YELLOW']:
                    self.css_status = "background-color : #CD0000; color : black;"
            self.lMinValue.setStyleSheet(self.css_status + " border: 2px solid grey;")
            # LABEL AVG VALUE
            self.lAvgValue.setText("%d" % self.avgValue)
            self.css_status = "background-color : #A5D496; color : black;"
            if self.avgValue > settings.db['STATUS_GREEN'] and self.avgValue <= settings.db['STATUS_YELLOW']:
                self.css_status = "background-color : #FFAE19; color : black;"
            else:
                if self.avgValue > settings.db['STATUS_YELLOW']:
                    self.css_status = "background-color : #CD0000; color : black;"
            self.lAvgValue.setStyleSheet(self.css_status + " border: 2px solid grey;")
            # LABEL TICKs
            self.lTick.setText("%d" % self.tick)
            self.lTick.setStyleSheet(self.css + " border: 2px solid grey;")
        
        
    def pingMe(self):
        # TODO : manage alternate ping command
        # Windows
        if os.name == "nt":
            args=['ping', '-n', '1', '-w', '1', str(self.targetIP)]
            p_ping = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, creationflags = 0x08000000)
            # save ping stdout
            p_ping_out = p_ping.communicate()[0]
            if (p_ping.wait() == 0):
                # Minimum = 19ms, Maximum = 19ms, Moyenne = 19ms
                if sys.version_info[0] < 3:
                    search = re.search(r'Minimum = (.*)ms, Maximum = (.*)ms, Moyenne = (.*)ms',p_ping_out, re.M|re.I)
                else:
                    search = re.search(r'Minimum = (.*)ms, Maximum = (.*)ms, Moyenne = (.*)ms',p_ping_out.decode('windows-1252'), re.M|re.I)
                ping_rtt = search.group(2)
        # Linux
        else:
            args=['/bin/ping', '-c', '1', '-W', '1', str(self.targetIP)]
            p_ping = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
            # save ping stdout
            p_ping_out = p_ping.communicate()[0]
            if (p_ping.wait() == 0):
                # rtt min/avg/max/mdev = 22.293/22.293/22.293/0.000 ms
                if sys.version_info[0] < 3:
                    search = re.search(r'rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms',p_ping_out, re.M|re.I)
                else:
                    search = re.search(r'rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms',p_ping_out.decode('windows-1252'), re.M|re.I)
                ping_rtt = search.group(2)        
        self.tick = self.tick + 1
        
        # FIX THIS
        try:
            self.pingValue = int(float(ping_rtt))
        except:
            self.pingValue = -1
            self.pLost = self.pLost + 1
        
        if self.pingValue != -1:
            if self.pingValue > self.maxValue:
                self.maxValue = self.pingValue
            if self.pingValue < self.minValue:
                self.minValue = self.pingValue
            self.sumValue = self.sumValue + self.pingValue
            self.avgValue = self.sumValue / self.tick            
        return self.pingValue
        
    def isValidIPAddress(self, ipAddress):
        try:
            socket.inet_aton(ipAddress)
            return True
        except:
            return False



