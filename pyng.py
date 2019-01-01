#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

# import PyQt4 QtCore and QtGui modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import mainwindow as mw
import const
import settings

if __name__ == '__main__':
    # create application
    app = QApplication(sys.argv)
    app.setOrganizationName(const.ORGANIZATION_NAME)
    app.setOrganizationDomain(const.ORGANIZATION_DOMAIN)    
    app.setApplicationName(const.APPLICATION_NAME)
    #
    icon = QIcon(":/png/16x16/Light.png")
    app.setWindowIcon(icon)    
    # create widget
    mWindow = mw.MainWindow()
    mWindow.setWindowTitle('Pyng')
    mWindow.statusBar.showMessage("Welcome", settings.db['TIMER_STATUS'])
    mWindow.show()
    # connection
    QObject.connect(app, SIGNAL('lastWindowClosed()'), app, SLOT('quit()'))
    # execute application
    sys.exit(app.exec_())
