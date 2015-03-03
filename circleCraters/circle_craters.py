# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CircleCraters
                                 A QGIS plugin
 A crater counting tool for planetary science
                              -------------------
        begin                : 2015-01-28
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Sarah E Braden
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
import os.path
import math
import collections

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QColor

from qgis.core import QgsPoint, QgsGeometry, QgsFeature, QgsVectorLayer, QgsMapLayerRegistry, QgsMapLayer, QgsErrorMessage
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand, QgsMessageBar

# Initialize Qt resources from file resources.py
import resources  # noqa

# Import the code for the dialog
from circle_craters_dialog import CircleCratersDialog


Point = collections.namedtuple('Point', ['x', 'y'])


class Circle(object):
    """ A cicle is defined by three distinct non-colinear points."""

    def __init__(self, points):
        """Input: a list of tuples
        """
        self.a, self.b, self.c = points
        print repr(self)
        self.compute_deltas()
        self.points_too_close()
        self.compute_line_slopes()
        self.check_if_colinear()

    def compute_deltas(self):
        # TODO: If the points are colinear, x_delta_a will be zero and
        # compute_line_slopes will throw an ZeroDivisionError
        self.y_delta_a = self.b.y - self.a.y
        self.x_delta_a = self.b.x - self.a.x
        self.y_delta_b = self.c.y - self.b.y
        self.x_delta_b = self.c.x - self.b.x

    def compute_line_slopes(self):
        self.a_slope = self.y_delta_a / self.x_delta_a
        self.b_slope = self.y_delta_b / self.x_delta_b

    def check_if_colinear(self):
        if abs(self.a_slope - self.b_slope) <= 0.000000001:
            # TODO: this should be printed as a message to the user in QGIS
            QgsErrorMessage('The three points are colinear. Cannot compute circle.\n')
            # TODO: clear the 3 points

    def points_too_close(self):
        if self.is_small(self.x_delta_a) & self.is_small(self.y_delta_b):
            # TODO: this should be printed as a message to the user in QGIS
            QgsErrorMessage('The points are too close together. Cannot compute circle.\n')
            # TODO: clear the 3 points

    def is_small(self, value):
        return abs(value) <= 0.000000001

    def radius(self):
        return self.distance(self.center, self.a)

    def diameter(self):
        return self.radius() * 2

    def distance(self, point_1, point_2):
        part_1 = math.pow((point_1.x - point_2.x), 2)
        part_2 = math.pow((point_1.y - point_2.y), 2)
        return math.sqrt(part_1 + part_2)

    def get_center(self):
        # TODO: this function is too long

        part_1 = self.a_slope * self.b_slope * (self.a.y - self.c.y)
        part_2 = self.b_slope * (self.a.x + self.b.x)
        part_3 = self.a_slope * (self.b.x + self.c.x)

        center_x = (part_1 + part_2 - part_3) / (2 * (self.b_slope - self.a_slope))
        a_b_midpoint = Point((self.a.x + self.b.x) / 2, (self.a.y + self.b.y) / 2)
        center_y = -1 * (center_x - a_b_midpoint.x) / self.a_slope + a_b_midpoint.y

        self.center = Point(center_x, center_y)
        return self.center

    def __repr__(self):
        return 'Point(%r, %r, %r)' % (self.a, self.b, self.c)


class CircleCraters(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CircleCraters_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = CircleCratersDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Circle Craters')

        self.toolbar = self.iface.addToolBar(u'CircleCraters')
        self.toolbar.setObjectName(u'CircleCraters')

        self.tool = QgsMapToolEmitPoint(self.canvas)
        self.tool.canvasClicked.connect(self.handle_click)
        self.tool.deactivated.connect(self.reset_clicks)
        self.clicks = []

        self.rb = QgsRubberBand(self.canvas, True)
        self.rb.setBorderColor(QColor(255, 0, 0))
        self.rb.setFillColor(QColor(0, 0, 0, 0))
        self.rb.setWidth(1)

        # TODO: We are going to let the user set this up in a future iteration
        # This is where the layer is being created
        self.layer = QgsVectorLayer('polygon', 'layer', 'memory')
        QgsMapLayerRegistry.instance().addMapLayer(self.layer)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CircleCraters', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):  # noqa
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/CircleCraters/3points.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Circle Craters'),
            callback=self.set_tool,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            ':/plugins/CircleCraters/export.png',
            text=self.tr(u'Export Data'),
            callback=self.export_tool,
            parent=self.iface.mainWindow(),
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Circle Craters'),
                action)
            self.iface.removeToolBarIcon(action)

    def reset_clicks(self):
        self.clicks = []

    def handle_click(self, point, button):
        self.clicks.append(Point(point.x(), point.y()))

        if len(self.clicks) != 3:
            return

        circle = Circle(self.clicks)

        # must be called in this order
        center = circle.get_center()
        radius = circle.radius()

        # radius is set to 50
        self.draw_circle(center.x, center.y, radius)

        msg = "clicks: {}".format(self.clicks)
        self.iface.messageBar().pushMessage("Info", msg)
        self.canvas.unsetMapTool(self.tool)

    def set_tool(self):
        """Run method that performs all the real work"""
        self.canvas.setMapTool(self.tool)

    def write_file(self, directory, filename):
        if os.path.exists(directory):
            print 'YAY'

    def export_tool(self):
        """ Run method that exports data to a file"""
        self.dlg.show()
        # Fetch all loaded layers
        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                # Add these layers to the combobox (dropdown menu)
                self.dlg.craterLayer.addItem(layer.name(), layer)
                self.dlg.areaLayer.addItem(layer.name(), layer)

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            crater_index = self.dlg.craterLayer.currentIndex()
            crater_layer = self.dlg.craterLayer.itemData(crater_index)
            area_index = self.dlg.areaLayer.currentIndex()
            area_layer = self.dlg.areaLayer.itemData(area_index)
            self.write_file(self.dlg.editDirectory.text(), self.dlg.editFilename.text())
            print 'Crater Layer name:', crater_layer.name()
            print 'Area Layer name:', area_layer.name()

    def get_area(self):
        return NotImplementedError

    def generate_circle(self, x, y, r):
        segments = 64
        thetas = [(2 * math.pi) / segments * i for i in xrange(segments)]
        points = [Point(r * math.cos(t), r * math.sin(t)) for t in thetas]
        polygon = [QgsPoint(p.x + x, p.y + y) for p in points]
        return QgsGeometry.fromPolygon([polygon])

    def draw_circle(self, x, y, r):
        geometry = self.generate_circle(x, y, r)

        feature = QgsFeature()
        feature.setGeometry(geometry)

        self.layer.addFeature(feature)
        self.rb.setToGeometry(geometry, None)
        print 'Circle should be there.'
