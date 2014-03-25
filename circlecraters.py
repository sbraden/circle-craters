# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CircleCraters
                                 A QGIS plugin
 Tool for crater counting for planetary science. Takes three points and fits a circle. 
                              -------------------
        begin                : 2014-03-13
        copyright            : (C) 2014 by Sarah Braden
        email                : braden.sarah@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from circlecratersdialog import CircleCratersDialog
import os.path


class CircleCraters:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'circlecraters_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = CircleCratersDialog()

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/circlecraters/icon.png"),
            u"Fit a circle", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Circle Craters", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Circle Craters", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass

    def points2circle(p1, p2, p3):
        '''
        inputs: p1, p2, p3 are tuples representing points in 2D space
        returns: radius in units of ? and the center point as a tuple
        We are solving for x.
        Better algorithms:
        http://stackoverflow.com/questions/4103405/what-is-the-algorithm-for-finding-the-center-of-a-circle-from-three-points
        '''
        # define the points
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        x3, y3 = p3[0], p3[1]
        # calculate the two chord lines
        ma = (y2 - y1) / (x2 - x1)
        mb = (y3 - y2) / (x3 - x2)
        ya = ma * (x - x1) + y1
        yb = mb * (x - x2) + y2
        # The center of the circle is the intersection of the 2 lines
        # perpendicular to and passing through the midpoints of the lines 
        # p1p2 and p2p3. 
        norm_ya = (-1/ma)*(x - )
        norm_yb = (-1/mb)*

        '''
        Need to catch the following errors:

        1. (mb - ma) is only zero when the lines are parallel 
        in which case they must be coincident and 
        thus no circle results.
        2. If either line is vertical then the corresponding slope is infinite. 
        This can be solved by simply rearranging the order of the points so 
        that vertical lines do not occur. 
        '''

        return raidus, center

'''
From: http://gis.stackexchange.com/questions/45094/how-to-programatically-check-for-a-mouse-click-in-qgis
The best way to make a new tool like the Select Single Feature tool is to inherit 
from the QgsMapTool class. When your tool is active, which can be set using 
QgsMapCanvas::setMapTool, any keyboard or click events the canvas gets will be 
passed onto your custom tool.

http://www.qgis.org/api/classQgsMapTool.html
'''

class PointTool(QgsMapTool):   
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas    

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def activate(self):
        pass

    def deactivate(self):
        pass