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

from PyQt5 import QtGui, QtCore, uic, QtWidgets

from .errors import CircleCraterError


ExportDialogBase, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'export_dialog_base.ui'))


class ExportDialog(QtWidgets.QDialog, ExportDialogBase):
    selected = QtCore.pyqtSignal(object, object, str)

    def __init__(self, parent=None):
        """Constructor."""
        super(ExportDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.accepted.connect(self.on_accept)
        self.filename_choose_button.clicked.connect(self.choose_file)

    def choose_file(self):
        self.filename_input.setText(QtWidgets.QFileDialog.getSaveFileName()[0])

    def show(self, choices):
        if not choices:
            raise CircleCraterError(
                'No choice of layers available. '
                'Please create polygon type vector layers.'
            )

        self.crater_layer_select.clear()
        self.area_layer_select.clear()

        for layer in choices:
            # Add these layers to the combobox (dropdown menu)
            self.crater_layer_select.addItem(layer.name(), layer)
            self.area_layer_select.addItem(layer.name(), layer)

        super(ExportDialog, self).show()

    def _get_layer(self, selector):
        return selector.itemData(selector.currentIndex())

    def get_crater_layer(self):
        return self._get_layer(self.crater_layer_select)

    def get_area_layer(self):
        return self._get_layer(self.area_layer_select)

    def get_filename(self):
        return self.filename_input.text()

    def on_accept(self):
        self.selected.emit(
            self.get_crater_layer(),
            self.get_area_layer(),
            self.get_filename(),
        )
