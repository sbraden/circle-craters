# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ExportDialog
                                 A QGIS plugin
 A crater counting tool for planetary science
                             -------------------
        begin                : 2014-12-31
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Sarah E Braden
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

import os

from PyQt4 import QtGui, uic

ExportDialogBase, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'export_dialog_base.ui'))


class ExportDialog(QtGui.QDialog, ExportDialogBase):
    def __init__(self, parent=None):
        """Constructor."""
        super(ExportDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.accepted = self.button_box.accepted
