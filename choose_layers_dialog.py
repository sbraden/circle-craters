# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ChooseLayersDialog
                                 A QGIS plugin
 A crater counting tool for planetary science
                             -------------------
        begin                : 2014-12-31
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Sarah E Braden
        email                : braden.sarah@gmail.com
 ***************************************************************************/
"""

import os

from PyQt5 import QtGui, QtCore, uic, QtWidgets

from .errors import CircleCraterError


ChooseLayersDialogBase, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'choose_layers_dialog_base.ui'))


class ChooseLayersDialog(QtWidgets.QDialog, ChooseLayersDialogBase):
    selected = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        """Constructor."""
        super(ChooseLayersDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.accepted.connect(self.on_accept)

    def show(self, choices):
        if not choices:
            raise CircleCraterError(
                'No choice of layers available. '
                'Please create polygon type vector layers.'
            )

        self.layer_select.clear()

        for layer in choices:
            # Add these layers to the combobox (dropdown menu)
            self.layer_select.addItem(layer.name(), layer)

        super(ChooseLayersDialog, self).show()

    def get_layer(self):
        return self.layer_select.itemData(self.layer_select.currentIndex())

    def on_accept(self):
        self.selected.emit(self.get_layer())
