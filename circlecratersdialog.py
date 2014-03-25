# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CircleCratersDialog
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

from PyQt4 import QtCore, QtGui
from ui_circlecraters import Ui_CircleCraters
# create the dialog for zoom to point


class CircleCratersDialog(QtGui.QDialog, Ui_CircleCraters):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
