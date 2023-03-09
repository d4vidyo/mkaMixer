import os
import sys
from PySide2 import QtWidgets, QtGui
import time
import threading

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, NAME, function, settings, parent=None):
        self.settings = settings
        self.function = function
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(NAME)
        self.menu = QtWidgets.QMenu(parent)
         
        self.open_app = self.menu.addAction("Settings")
        self.open_app.triggered.connect(self.openWindow)
        self.open_app.setIcon(QtGui.QIcon("Images\windowIcon.png"))

        self.exit_ = self.menu.addAction("Exit")
        self.exit_.triggered.connect(lambda: os._exit(0))
        self.exit_.setIcon(QtGui.QIcon("Images\exitIcon.png"))

        self.menu.addSeparator()
        self.setContextMenu(self.menu)
        self.activated.connect(self.onTrayIconActivated)

    def onTrayIconActivated(self, reason):
        if reason == self.DoubleClick:
            self.openWindow()

    def openWindow(self):    
        self.function(self.settings)

class handler():
    def start(self):
        app = QtWidgets.QApplication(sys.argv)
        w = QtWidgets.QWidget()
        tray_icon = SystemTrayIcon(QtGui.QIcon("Images/trayIcon.png"), self.NAME, self.function, self.settings, w)
        tray_icon.show()
        sys.exit(app.exec_())

    def __init__(self, NAME, function, settings):
       self.NAME = NAME
       self.function = function
       self.settings = settings