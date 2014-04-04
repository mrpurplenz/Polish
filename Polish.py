# -*- coding: utf-8 -*-
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *


class Polish:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def initGui(self):
        # Create action that will start plugin
        self.action = QAction(QIcon(":/plugins/"), "&Polish", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("activated()"), self.Polish)

        # Add toolbar button and menu item
        self.iface.addPluginToMenu("Polish", self.action)


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("Polish",self.action)

    def testfun(self):
        print "local file function test"

    # run
    def Polish(self):
        QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('Polish', "Polish"), QCoreApplication.translate('Polish', "Polish"))
        return




if __name__ == "__main__":
    pass
