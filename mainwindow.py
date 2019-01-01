from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import os
import sys
import targetWidget
import headerWidget
import datetime
import pickle
import DlgTargetInput
import xml.etree.ElementTree as ET
import DlgSettings
import const
import settings
import time
import threading
from datetime import datetime
from dateutil.relativedelta import relativedelta


# Define function to import external files when using PyInstaller.
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow ( QMainWindow ):
    """MainWindow inherits QMainWindow"""  
    appDir = ""
    isRunning = False
    nOrder = 1
    
    DATE, HOUR, TARGET = range(3)

    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        uic.loadUi(resource_path('mainwindow.ui'), self)
        # settings.openDB()
        
        self.action_Quit.triggered.connect(self.close)
        self.action_Settings.triggered.connect(self.displaySettings)
        
        self.btnReset.clicked.connect(self.resetCounters)
        self.btnEditTemplates.clicked.connect(self.editTemplates)
        
        self.btnAddTarget.clicked.connect(self.addTarget)
        self.btnAddTargets.clicked.connect(self.addTargets)
        self.btnRun.clicked.connect(self.runPing)
        self.btnDeleteTemplate.clicked.connect(self.deleteTemplate)
        self.btnSaveAsTemplate.clicked.connect(self.saveAsTemplate)
        self.btnSaveTemplate.clicked.connect(self.saveTemplate)
        self.connect(self.lstTemplates, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.addTargetsFromTemplate)
        self.tvwHistory.doubleClicked.connect(self.addTargetFromHistory)
        self.tvwHistory.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.lTargets = QLabel("")
        self.lTargets.setFrameShape(QFrame.Panel)
        self.lTargets.setFrameShadow(QFrame.Sunken)
        self.lTargets.setLineWidth(1)
        self.statusBar.addPermanentWidget(self.lTargets)
        self.displayTargets()
        
        self.lcdElapsed.display("00:00:00")
        self.lcdInterval.display(settings.db['TIMER_PING'])
        self.sldInterval.setMinimum(settings.db['TIMER_PING'] / 10)
        self.sldInterval.setMaximum(settings.db['TIMER_PING'] * 10)
        self.sldInterval.setValue(settings.db['TIMER_PING'])
        self.sldInterval.valueChanged.connect(self.changeInterval)
        
        self.lblLED = QLabel()
        self.lblLED.setPixmap(QPixmap("16x16/led_green.png"))
        self.statusBar.addPermanentWidget(self.lblLED)
        self.repaint()
        
        self.lblGreen.setText("%d-%d ms" % (0, settings.db['STATUS_GREEN']))
        self.lblYellow.setText("%d-%d ms" % (settings.db['STATUS_GREEN'] + 1, settings.db['STATUS_YELLOW']))
        self.lblRed.setText(" %d ms and up" % (settings.db['STATUS_YELLOW'] + 1))
        
        self.vLayout.addStretch()

        self.appDir = os.path.join(os.path.expanduser("~"), const.APP_FOLDER)
        if not os.path.exists(self.appDir):
            os.makedirs(self.appDir)
        
        self.createHistoryView(self)
        self.cbxTarget.lineEdit().returnPressed.connect(self.addTarget)
        #
        # SETTINGS RESTORE
        #
        """
        try:
            with open(HISTORY_FILE, "rb") as fp:
                self.aCommands = pickle.load(fp)
                self.iCommands = len(self.aCommands)
        except:
            pass
        """
        #
        mySettings = QSettings()
        size = mySettings.value('MainWindow/Size', QSize(600,500))
        try:
            self.resize(size)
        except:
            self.resize(size.toSize())
        position = mySettings.value('MainWindow/Position', QPoint(0,0))
        try:
            self.move(position)
        except:
            self.move(position.toPoint())
        
        try:
            self.restoreState(mySettings.value("MainWindow/WindowState", b"", type='QByteArray'))
            splitterSettings = mySettings.value("MainWindow/SplitterSettings")
        except:
            splitterSettings = None

        """
        try:
            settings.TIMER_PING = mySettings.value("MainWindow/TimerPing", 500).toInt()[0]
            settings.TIMER_STATUS = mySettings.value("MainWindow/TimerStatus", 3000).toInt()[0]
            settings.UNREACHABLE_PING = mySettings.value("MainWindow/UnreachablePing", 10).toInt()[0]
        except:
            pass
        """
        
        if splitterSettings:
            try:
                self.splitter.restoreState(splitterSettings)
            except:
                try:
                    self.splitter.restoreState(splitterSettings.toPyObject())
                except:
                    pass
        """
        try:
            global COLOR_LINE_1
            COLOR_LINE_1 = mySettings.value("MainWindow/ColorLine1","#ccdee2").toString()
            global COLOR_LINE_2
            COLOR_LINE_2 = mySettings.value("MainWindow/ColorLine2","#b3b8bf").toString()
        except:
            pass
        """
        #
        lastItem = self.vLayout.itemAt(self.vLayout.count() - 1)
        self.vLayout.removeItem(lastItem)
        hWidget = headerWidget.headerWidget(self)
        self.vLayout.addWidget(hWidget)
        self.vLayout.addStretch()
        #
        self.checkTemplatesFile()
        self.populateTemplatesList()

    def __del__ ( self ):
        self.ui = None
    
    def resetCounters(self):
        for i in range(self.vLayout.count()):
            wWidget = self.vLayout.itemAt(i).widget()
            if type(wWidget) is targetWidget.targetWidget:
                wWidget.resetCounters()
        self.startTime = datetime.now()
        self.lcdElapsed.display("00:00:00")
    
    def editTemplates(self):
        self.wDlgSettings= DlgSettings.DlgSettings(self)
        self.wDlgSettings.setWindowTitle('Pyng Settings')
        self.wDlgSettings.tabWidget.setCurrentIndex(3)
        self.wDlgSettings.exec_()
        self.refreshUI()
        
    def displaySettings(self):
        self.wDlgSettings= DlgSettings.DlgSettings(self)
        self.wDlgSettings.setWindowTitle('Pyng Settings')
        self.wDlgSettings.exec_()
        self.refreshUI()

    def refreshUI(self):
        self.lblGreen.setText("%d-%d ms" % (0, settings.db['STATUS_GREEN']))
        self.lblYellow.setText("%d-%d ms" % (settings.db['STATUS_GREEN'] + 1, settings.db['STATUS_YELLOW']))
        self.lblRed.setText(" %d ms and up" % (settings.db['STATUS_YELLOW'] + 1))
        
        self.lcdInterval.display(settings.db['TIMER_PING'])
        self.sldInterval.setMinimum(settings.db['TIMER_PING'] / 10)
        self.sldInterval.setMaximum(settings.db['TIMER_PING'] * 10)
        self.sldInterval.setValue(settings.db['TIMER_PING'])
        
    def addExplicitTarget(self, target):
        # remove ending stretch
        lastItem = self.vLayout.itemAt(self.vLayout.count() - 1)
        self.vLayout.removeItem(lastItem)
        # add ping widget to right panel with current target
        tWidget = targetWidget.targetWidget(target, self.nOrder, self)
        self.vLayout.addWidget(tWidget)
        # add target to history
        now = datetime.now()
        self.mdlHistory.insertRow(0)
        self.mdlHistory.setData(self.mdlHistory.index(0, self.DATE), now.strftime("%d/%m/%Y"))
        self.mdlHistory.setData(self.mdlHistory.index(0, self.HOUR), now.strftime("%H:%M:%S"))
        self.mdlHistory.setData(self.mdlHistory.index(0, self.TARGET), target)        
        # increment nOrder variable
        self.nOrder = self.nOrder + 1
        #
        self.displayTargets()
        # add the ending stretch
        self.vLayout.addStretch()

    def addTargets(self):
        targets, rc = DlgTargetInput.getTargets(self)
        if rc == True:
            for target in targets:
                self.addExplicitTarget(target)
            # done !
            self.statusBar.showMessage("%d target(s) added" % len(targets), settings.db['TIMER_STATUS'])
        else:
            self.statusBar.showMessage("Cancelled", settings.db['TIMER_STATUS'])
        
    def addTarget(self):
        # add target to combo list if not already present in it
        if self.cbxTarget.currentText() not in [self.cbxTarget.itemText(i) for i in range(self.cbxTarget.count())]:
                self.cbxTarget.addItem(self.cbxTarget.currentText())
        self.addExplicitTarget(self.cbxTarget.currentText())
        # done !
        self.statusBar.showMessage("Target added", settings.db['TIMER_STATUS'])

    def displayTime(self, arg):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            delta = relativedelta(datetime.now(), self.startTime)
            self.lcdElapsed.display('{:02d}:{:02d}:{:02d}'.format(delta.hours, delta.minutes, delta.seconds))        
    
    def runPing(self):
        if self.isRunning == True:
            self.isRunning = False            
            self.btnRun.setIcon(QIcon("16x16/Player Play.png"))
            self.statusBar.showMessage("Ping is stopped", settings.db['TIMER_STATUS'])
            self.lblLED.setPixmap(QPixmap("16x16/led_green.png"))
            self.lblLED2.setPixmap(QPixmap("16x16/led_green.png"))
            self.threadDisplayTime.do_run = False
            self.threadDisplayTime.join()
            self.repaint()
        else:
            self.isRunning = True
            self.btnRun.setIcon(QIcon("16x16/Player Pause.png"))
            self.statusBar.showMessage("Ping is running", settings.db['TIMER_STATUS'])
            self.lblLED.setPixmap(QPixmap("16x16/led_red.png"))
            self.lblLED2.setPixmap(QPixmap("16x16/led_red.png"))
            #
            self.startTime = datetime.now()
            #
            self.threadDisplayTime = threading.Thread(target=self.displayTime, args=("task",))
            self.threadDisplayTime.start()
            #
            self.repaint()
    
    def changeInterval(self):
        newInterval = self.sldInterval.value()
        self.lcdInterval.display(newInterval)
        self.updateTimer(newInterval)
        
    def updateTimer(self, n):
        for i in range(self.vLayout.count()):
            wWidget = self.vLayout.itemAt(i).widget()
            if type(wWidget) is targetWidget.targetWidget:
                wWidget.setInterval(n)
    
    def clearTargets(self):
        # first, remove the ending stretch
        lastItem = self.vLayout.itemAt(self.vLayout.count() - 1)
        self.vLayout.removeItem(lastItem)
        # then, remove the widgets
        for i in reversed(range(self.vLayout.count())): 
            self.vLayout.itemAt(i).widget().deleteLater()       
        # reset the nOrder variable
        self.nOrder = 1
        # add the ending stretch
        self.vLayout.addStretch()
        # done !
        lastItem = self.vLayout.itemAt(self.vLayout.count() - 1)
        self.vLayout.removeItem(lastItem)
        hWidget = headerWidget.headerWidget(self)
        self.vLayout.addWidget(hWidget)
        self.vLayout.addStretch()        
        #
        self.displayTargets()
        self.statusBar.showMessage("Targets list cleared", settings.db['TIMER_STATUS'])
        
    def displayTargets(self):
        self.lTargets.setText(" Targets : %5d " % (self.nOrder - 1))
        
    def clearTarget(self, order):
        #
        thisItem = self.vLayout.itemAt(order)
        self.vLayout.itemAt(order).widget().deleteLater()
        self.vLayout.removeItem(thisItem)
        self.nOrder = self.nOrder - 1
        #
        for i in range(self.vLayout.count()):
            wWidget = self.vLayout.itemAt(i).widget()
            if type(wWidget) is targetWidget.targetWidget:
                wWidget.setOrder(i)
            
        self.displayTargets()
        self.statusBar.showMessage("Target #%d cleared" % order, settings.db['TIMER_STATUS'])        
        
    def deleteTemplate(self):
        # TODO : manage delete template option
        pass
    
    def saveAsTemplate(self):
        # TODO : manage save as template option
        pass

    def saveTemplate(self):
        # TODO : manage save template option
        text, ok = QInputDialog.getText(self, 'Template saving', "Template's name:")		
        if ok:
            self.statusBar.showMessage("Template '%s' saved" % text, settings.db['TIMER_STATUS'])
        else:
            self.statusBar.showMessage("Cancelled", settings.db['TIMER_STATUS'])

    def closeEvent(self, event):
        result = QMessageBox.question(self,"Confirm Exit","Are you sure you want to quit ?",QMessageBox.Yes| QMessageBox.No)        
        if result == QMessageBox.Yes:
            #
            # STOP TIME DISPLAY THREAD
            #
            if hasattr(self, "threadDisplayTime"):
                self.threadDisplayTime.do_run = False
                self.threadDisplayTime.join()
            #
            # SETTINGS BACKUP
            #
            self.saveHistory()
            """
            with open(HISTORY_FILE, "wb") as fp:
                pickle.dump(self.aCommands, fp)
            """
            #
            mySettings = QSettings()
            mySettings.setValue("MainWindow/Size", self.size())
            mySettings.setValue("MainWindow/Position", self.pos())
            mySettings.setValue("MainWindow/WindowState", self.saveState())
            """
            mySettings.setValue("MainWindow/TimerBeat", settings.db['TIMER_PING'])
            mySettings.setValue("MainWindow/TimerStatus", settings.db['TIMER_STATUS'])
            mySettings.setValue("MainWindow/UnreachablePing", settings.db['UNREACHABLE_PING'])
            mySettings.setValue("MainWindow/StatusYellow", settings.db['STATUS_YELLOW'])
            mySettings.setValue("MainWindow/StatusGreen", settings.db['STATUS_GREEN'])
            # mySettings.setValue("MainWindow/ColorLine1", COLOR_LINE_1)
            # mySettings.setValue("MainWindow/ColorLine2", COLOR_LINE_2)
            """
            splitterSettings = self.splitter.saveState()
            if splitterSettings:
                mySettings.setValue("MainWindow/SplitterSettings", self.splitter.saveState())           
            event.accept()
        else:
            event.ignore()
            
    def createHistoryView(self, parent):
        self.mdlHistory = QStandardItemModel(0, 3, parent)
        self.mdlHistory.setHeaderData(self.DATE, Qt.Horizontal, "Date")
        self.mdlHistory.setHeaderData(self.HOUR, Qt.Horizontal, "Hour")
        self.mdlHistory.setHeaderData(self.TARGET, Qt.Horizontal, "Target")
        
        self.tvwHistory.setRootIsDecorated(False)
        self.tvwHistory.setAlternatingRowColors(True)
        self.tvwHistory.setModel(self.mdlHistory)
        
        self.loadHistory()

    def saveHistory(self):
        file = open(os.path.join(self.appDir, const.HISTORY_FILE), 'wb')
        for iRow in range(0,self.mdlHistory.rowCount()):
            for iCol in range(0,self.mdlHistory.columnCount()):
                cell = str(self.mdlHistory.item(iRow, iCol).text())
                # print(cell)
                pickle.dump(cell, file)
        file.close()

    def loadHistory(self):
        objects = []
        okLoad = True
        with (open(os.path.join(self.appDir, const.HISTORY_FILE), 'rb')) as file:
            while True:
                try:
                    objects.append(pickle.load(file))
                except EOFError:
                    break
                except ValueError:
                    """
                    Pickle in Python 3.x is not compatible with pickle in Python 2.x
                    """
                    okLoad = False
        if okLoad == True:
            for i in range(0, len(objects), 3):
                self.mdlHistory.insertRow(0)
                self.mdlHistory.setData(self.mdlHistory.index(0, self.DATE), objects[i + 0])
                self.mdlHistory.setData(self.mdlHistory.index(0, self.HOUR), objects[i + 1])
                self.mdlHistory.setData(self.mdlHistory.index(0, self.TARGET), objects[i + 2])        
        file.close()
    
    def checkTemplatesFile(self):
        try:
            xmlFile = open(const.TEMPLATES_FILE, 'r')
        except:
            xmlFile = open(const.TEMPLATES_FILE, 'w+')
            xmlFile.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            xmlFile.write("\t<templates>\n")
            xmlFile.write("\t\t<template name='Public DNS'>\n")
            xmlFile.write("\t\t\t<target>8.8.8.8</target>\n")
            xmlFile.write("\t\t\t<target>8.8.4.4</target>\n")
            xmlFile.write("\t\t\t<target>1.1.1.1</target>\n")
            xmlFile.write("\t\t\t<target>1.0.0.1</target>\n")            
            xmlFile.write("\t\t</template>\n")
            xmlFile.write("\t</templates>\n")
        xmlFile.close()

    def populateTemplatesList(self):
        self.lstTemplates.clear()
        try:
            tree = ET.parse(const.TEMPLATES_FILE)
            templates = tree.getroot()
            for template in templates:
                self.lstTemplates.addItem(template.attrib.get("name"))
        except:
            self.statusBar.showMessage("ERROR : Templates file not well-formed", settings.db['TIMER_STATUS'])

    def addTargetsFromTemplate(self, item):
        tree = ET.parse(const.TEMPLATES_FILE)
        templates = tree.getroot()
        self.lblTemplate.setText(item.text())
        for template in templates:
            if item.text() == template.attrib.get("name"):
                for target in template:
                    self.addExplicitTarget(target.text)
                self.statusBar.showMessage("Template's targets added", settings.db['TIMER_STATUS'])

    def addTargetFromHistory(self, index):
        mySel = []
        for ix in self.tvwHistory.selectedIndexes():
            if sys.version_info[0] < 3:
                # Python 2.x
                mySel.append(ix.data().toString())
            else:
                # Python 3.x
                mySel.append(ix.data())
        self.addExplicitTarget(mySel[2])
        self.statusBar.showMessage("Target %s added from history" % mySel[2], settings.db['TIMER_STATUS'])

    """
    use pickle :

    import pickle
    dict = {'one': 1, 'two': 2}
    file = open('dump.txt', 'w')
    pickle.dump(dict, file)
    file.close()

    and to read it again :

    file = open('dump.txt', 'r')
    dict = pickle.load(file)
    
    
    
    import xml.etree.ElementTree as ET

tree = ET.parse("/media/jpl/JPL003/Projets/Python/Pyng/templates.xml")
templates = tree.getroot()
for template in templates:
    # print(template.tag, template.attrib)
    print(template.attrib.get('name'))
    for target in template:
        print(target.text)

    """
