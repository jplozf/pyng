from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import os
import settings
import smtplib

import subprocess
import re
import sys
import socket

import platform
import const

try:
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
except:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

class DlgSettings ( QDialog ):
    """DlgSettings inherits QDialog"""

    def __init__ ( self, parent = None ):
        QDialog.__init__( self, parent )
        setattr(self, "parent", parent)
        uic.loadUi(resource_path('DlgSettings.ui'), self)
        
        self.spbTimerPing.setMinimum(0)
        self.spbTimerPing.setMaximum(settings.db['TIMER_PING'] * 1000)       
        self.spbTimerPing.setValue(settings.db['TIMER_PING'])
        
        self.spbTimerStatus.setMinimum(0)
        self.spbTimerStatus.setMaximum(settings.db['TIMER_STATUS'] * 1000)
        self.spbTimerStatus.setValue(settings.db['TIMER_STATUS'])
        
        self.spbUnreachablePing.setMinimum(0)
        self.spbUnreachablePing.setMaximum(settings.db['UNREACHABLE_PING'] * 1000)
        self.spbUnreachablePing.setValue(settings.db['UNREACHABLE_PING'])
    
        self.spbGreenStatus.setMinimum(0)
        self.spbGreenStatus.setMaximum(settings.db['STATUS_GREEN'] * 1000)
        self.spbGreenStatus.setValue(settings.db['STATUS_GREEN'])
        
        self.spbYellowStatus.setMinimum(0)
        self.spbYellowStatus.setMaximum(settings.db['STATUS_YELLOW'] * 1000)
        self.spbYellowStatus.setValue(settings.db['STATUS_YELLOW'])
        
        self.spbGreenStatus.valueChanged.connect(self.greenValueChanged)
        self.spbYellowStatus.valueChanged.connect(self.yellowValueChanged)
        
        self.txtSMTPServer.setText(settings.db['SMTP_SERVER'])
        self.txtSMTPPort.setText(str(settings.db['SMTP_PORT']))
        self.chkSMTPTLS.setChecked(settings.db['SMTP_TLS'])
        self.txtSMTPUser.setText(settings.db['SMTP_USER'])
        self.txtSMTPPassword.setText(settings.db['SMTP_PASSWORD'])
        self.txtSMTPRecipients.setText(settings.db['SMTP_RECIPIENTS'])
        
        self.txtAlternateCommand.setText(settings.db['ALT_PING_COMMAND'])
        self.txtAlternateRegex.setText(settings.db['ALT_PING_REGEX'])
        self.txtAlternateGroup.setText(str(settings.db['ALT_REGEX_GROUP']))
        self.txtAlternateCodepage.setText(settings.db['ALT_PING_CODEPAGE'])
        self.chkEnableAlternate.setChecked(settings.db['ALT_PING_ENABLED'])
        self.txtTestTarget.setText("8.8.8.8")
        
        self.btnTestMail.clicked.connect(self.testMail)
        self.btnOK.clicked.connect(self.saveSettingsClose)
        self.btnCancel.clicked.connect(self.reject)
        self.btnTestAlternate.clicked.connect(self.testAlternate)
        self.btnClearOutput.clicked.connect(self.clearOutput)

        infoHost = "<center><table cellpadding='0' cellspacing='5'>"

        infoHost = infoHost + "<tr bgcolor='#6992c2'><td colspan = 2><center><b>" + const.APPLICATION_NAME + "</b></center></td></tr>"

        infoHost = infoHost + "<tr><td colspan = 2><center><i>" + const.BLAHBLAH_01 + "</i></center></td></tr>"
        infoHost = infoHost + "<tr><td colspan = 2><center><i>" + const.BLAHBLAH_02 + "</i></center></td></tr>"
        infoHost = infoHost + "<tr><td colspan = 2><center><i>" + const.BLAHBLAH_03 + "</i></center></td></tr>"
        infoHost = infoHost + "<tr><td colspan = 2><center><i>" + const.BLAHBLAH_04 + "</i></center></td></tr>"
        infoHost = infoHost + "<tr><td colspan = 2><center><i>" + const.BLAHBLAH_05 + "</i></center></td></tr>"
        infoHost = infoHost + "<tr><td colspan = 2>&nbsp;</td></tr>"
        
        infoHost = infoHost + "<tr><td><b>Author</b></td><td>" + const.AUTHOR + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>Copyright</b></td><td>" + const.COPYRIGHT + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>License</b></td><td>" + const.LICENSE + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>Version</b></td><td>" + const.VERSION + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>Email</b></td><td>" + const.EMAIL + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>Organization Name</b></td><td>" + const.ORGANIZATION_NAME + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>Organization Domain</b></td><td>" + const.ORGANIZATION_DOMAIN + "</td></tr>"        
        infoHost = infoHost + "<tr><td colspan = 2>&nbsp;</td></tr>"
        
        infoHost = infoHost + "<tr bgcolor='#6992c2'><td colspan = 2><center><b>Host</b></center></td></tr>"
        
        infoHost = infoHost + "<tr><td><b>Hostname</b></td><td>" + socket.gethostname() + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>Machine</b></td><td>" + platform.machine() + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>Version</b></td><td>" + platform.version() + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>Platform</b></td><td>" + platform.platform() + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>System</b></td><td>" + platform.system() + "</td></tr>"
        infoHost = infoHost + "<tr><td><b>Processor</b></td><td>" + platform.processor() + "</td></tr>"
        infoHost = infoHost + "<tr><td colspan = 2>&nbsp;</td></tr>"
        infoHost = infoHost + "<tr><td><b>Python version</b></td><td>" + sys.version + "</td></tr>"
        infoHost = infoHost + "<tr><td colspan = 2>&nbsp;</td></tr>"       
        
        infoHost = infoHost + "</table></center>"
        self.txtAbout.setText(infoHost)

        self.btnSaveTemplates.clicked.connect(self.saveTemplates)
        self.dirtyFlag = False
        parent.checkTemplatesFile()
        with open(const.TEMPLATES_FILE) as xmlFile:
            self.txtEditTemplates.setPlainText(str(xmlFile.read()))
        self.txtEditTemplates.textChanged.connect(self.changedText)
        self.txtEditTemplates.cursorPositionChanged.connect(self.cursorPosition)
        
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), const.HELP_FILE))
        local_url = QUrl.fromLocalFile(file_path)
        self.webHelp.load(local_url)
        self.webHelp.show() 

    def __del__ ( self ):
        self.ui = None
    
    def saveTemplates(self):
        with open(const.TEMPLATES_FILE, 'w') as xmlFile:
            xmlFile.write(str(self.txtEditTemplates.toPlainText()))
        self.dirtyFlag = False
        self.lblDirtyFlag.setText("")
        self.lblStatusXML.setText(self.parent.populateTemplatesList())
        
    def changedText(self):
        self.dirtyFlag = True
        self.lblDirtyFlag.setText("*modified*")
    
    def cursorPosition(self):
        line = self.txtEditTemplates.textCursor().blockNumber() + 1
        col = self.txtEditTemplates.textCursor().columnNumber() + 1
        self.lblLineCursor.setText("Line : %d" % line)
        self.lblColumnCursor.setText("Column : %d" % col)
    
    def greenValueChanged(self):
        if self.spbGreenStatus.value() >= self.spbYellowStatus.value():
            self.spbYellowStatus.setValue(self.spbGreenStatus.value() + 1)
    
    def yellowValueChanged(self):
        if self.spbYellowStatus.value() <= self.spbGreenStatus.value():
            self.spbGreenStatus.setValue(self.spbYellowStatus.value() - 1)

    def saveSettingsClose(self):
        self.saveSettings()
        self.accept()
        
    def saveSettings(self):
        settings.db['STATUS_GREEN'] = self.spbGreenStatus.value()
        settings.db['STATUS_YELLOW'] = self.spbYellowStatus.value()
        settings.db['TIMER_PING'] = self.spbTimerPing.value()
        settings.db['TIMER_STATUS'] = self.spbTimerStatus.value()
        settings.db['UNREACHABLE_PING'] = self.spbUnreachablePing.value()

        settings.db['SMTP_SERVER'] = str(self.txtSMTPServer.text())
        settings.db['SMTP_PORT'] = int(self.txtSMTPPort.text())
        settings.db['SMTP_TLS'] = self.chkSMTPTLS.isChecked()
        settings.db['SMTP_USER'] = str(self.txtSMTPUser.text())
        settings.db['SMTP_PASSWORD'] = str(self.txtSMTPPassword.text())
        settings.db['SMTP_RECIPIENTS'] = str(self.txtSMTPRecipients.toPlainText())

        settings.db['ALT_PING_COMMAND'] = str(self.txtAlternateCommand.text())
        settings.db['ALT_PING_REGEX'] = str(self.txtAlternateRegex.text())
        settings.db['ALT_REGEX_GROUP'] = str(self.txtAlternateGroup.text())
        settings.db['ALT_PING_CODEPAGE'] = str(self.txtAlternateCodepage.text())
        settings.db['ALT_PING_ENABLED'] = self.chkEnableAlternate.isChecked()

        settings.db.sync()

    def testMail(self):
        self.saveSettings()
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.db['SMTP_USER']
        msg['To'] = settings.db['SMTP_RECIPIENTS']
        msg['Subject'] = 'Pyng Test Message'
        
        # Create the body of the message (a plain-text and an HTML version).            
        text = """\
        Hello from Pyng,\n\n
        This is a test message.\n\n
        Best regards,\n\n
        The Pyng Team.\n
        """
        
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hello from Pyng,<br><br>
                This is a test message.<br><br>
               Best regards,<br><br>
               <i>The Pyng Team.</i>
            </p>
          </body>
        </html>
        """

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # print(settings.db['SMTP_SERVER'], int(settings.db['SMTP_PORT']))
        mailserver = smtplib.SMTP(settings.db['SMTP_SERVER'], int(settings.db['SMTP_PORT']))
        if settings.db['SMTP_TLS']==True:
            mailserver.ehlo()
            mailserver.starttls()
        mailserver.ehlo()
        # mailserver.login(settings.db['SMTP_USER'], 'xhltaqimdngaiagk')
        mailserver.login(settings.db['SMTP_USER'], settings.db['SMTP_PASSWORD'])
        mailserver.sendmail(settings.db['SMTP_USER'], settings.db['SMTP_RECIPIENTS'].split(";"), msg.as_string())
        mailserver.quit()
        
        popup = QMessageBox()
        popup.setIcon(QMessageBox.Information)
        popup.setWindowTitle("Test mail sent")
        popup.setText("A test mail has been sent.")
        popup.setInformativeText("Please, check your mail box.")
        popup.setStandardButtons(QMessageBox.Ok)
        popup.exec_()

    def str_to_raw(self, s):
        _dRawMap = {8:r'\b', 7:r'\a', 12:r'\f', 10:r'\n', 13:r'\r', 9:r'\t', 11:r'\v'}
        return r''.join( [ _dRawMap.get( ord(c), c ) for c in s ] )

    def testAlternate(self):
        tick = 0
        minValue = 99999
        maxValue = 0
        sumValue = 0
        avgValue = 0
        pLost = 0
        for i in range(0, 10):
            args = str(self.txtAlternateCommand.text()).split(" ")
            args.append(self.txtTestTarget.text())
            # Windows
            if os.name == "nt":
                p_ping = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, creationflags = 0x08000000)
            # Linux
            else:
                p_ping = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
                
            # save ping stdout
            try:
                p_ping_out = p_ping.communicate()[0]
                if self.txtAlternateCodepage.text() == "":
                    self.txtOutput.append(p_ping_out)
                else:
                    self.txtOutput.append(p_ping_out.decode(str(self.txtAlternateCodepage.text())))
                if (p_ping.wait() == 0):
                    if self.txtAlternateCodepage.text() == "":
                        search = re.search(self.str_to_raw(str(self.txtAlternateRegex.text())),p_ping_out, re.M|re.I)
                    else:
                        search = re.search(self.str_to_raw(str(self.txtAlternateRegex.text())),p_ping_out.decode(str(self.txtAlternateCodepage.text())), re.M|re.I)
                    ping_rtt = search.group(int(str(self.txtAlternateGroup.text())))
                tick = tick + 1
                try:
                    pingValue = int(float(ping_rtt))
                except:
                    pingValue = -1
                    pLost = pLost + 1
                
                if pingValue != -1:
                    if pingValue > maxValue:
                        maxValue = pingValue
                    if pingValue < minValue:
                        minValue = pingValue
                    sumValue = sumValue + pingValue
                    avgValue = sumValue / tick        
                
                self.txtOutput.append("---------------------------")
                self.txtOutput.append("Here is what I understood :")
                self.txtOutput.append("Request # %d\n" % tick)
                self.txtOutput.append("PING VALUE IS %d" % pingValue)
                self.txtOutput.append("---------------------------")
            
            except Exception as e:
                self.txtOutput.append(str(e))
                
        self.txtOutput.append("      S U M M A R Y        ")
        self.txtOutput.append("---------------------------")
        self.txtOutput.append("Requests %d\n" % tick)
        self.txtOutput.append("MIN : %d\nAVG : %d\nMAX : %d" % (minValue, avgValue, maxValue))
        self.txtOutput.append("---------------------------")

    def clearOutput(self):
        self.txtOutput.setText("")

# Define function to import external files when using PyInstaller.
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


"""
from PyQt4 import uic
import MainWindow

( Ui_VarsFileEditor, QWidget ) = uic.loadUiType( 'VarsFileEditor.ui' )

class VarsFileEditor ( QWidget ):
    # VarsFileEditor inherits QWidget

    def __init__ ( self, parent = None):
        QWidget.__init__( self, parent )
        self.ui = Ui_VarsFileEditor()
        self.ui.setupUi( self )
        self.parent = parent
        #
        self.ui.btnSaveFile.clicked.connect(self.saveFile)
        self.ui.txtEdit.textChanged.connect(self.changedText)
        #
        self.dirtyFlag = False
        with open(MainWindow.VARS_XML_FILE) as xmlFile:
            self.ui.txtEdit.setPlainText(str(xmlFile.read()))

    def setIndex(self, index):
        self.index = index
        
    def __del__ ( self ):
        self.ui = None

    def saveFile(self):
        if self.dirtyFlag == True:
            self.parent.tabWidget.setTabText(self.index, self.parent.tabWidget.tabText(self.index)[:-1])
            with open(MainWindow.VARS_XML_FILE, "w") as xmlFile:
                xmlFile.write(str(self.ui.txtEdit.toPlainText()))
            self.parent.loadVars()
            self.dirtyFlag = False
    
    def changedText(self):
        if hasattr(self, 'index'):
            if self.dirtyFlag == False:
                self.parent.tabWidget.setTabText(self.index, self.parent.tabWidget.tabText(self.index) + "*")
                self.dirtyFlag = True
"""