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
import datetime

from PyQt4.QtCore import (
    QCoreApplication,
    QSettings,
    QTranslator,
    QVariant,
    qVersion,
)

from PyQt4.QtGui import (
    QAction,
    QIcon,
)

from qgis.core import (
    QgsDistanceArea,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPoint,
)

from qgis.gui import (
    QgsMapToolEmitPoint,
    QgsMessageBar,
)

# Initialize Qt resources from file resources.py
import resources_rc  # noqa

from export_dialog import ExportDialog
from choose_layers_dialog import ChooseLayersDialog

from shapes import Point, Circle

# TODO: Handle intersection of crater centers and area layers
# TODO: total area must be in km^2 for the .diam file

# TODO: Test conversion between CRS
# TODO: test area and distance measurements for accuracy
# TODO: Flatten git repos: Tests and Makefile should be in the top directory
# TODO: get new icons


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
        self.export_dlg = ExportDialog()
        self.export_dlg.accepted.connect(self.export)

        self.choose_dlg = ChooseLayersDialog()
        self.choose_dlg.selected.connect(self.on_layer_select)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Circle Craters')

        self.toolbar = self.iface.addToolBar(u'CircleCraters')
        self.toolbar.setObjectName(u'CircleCraters')

        self.tool = QgsMapToolEmitPoint(self.canvas)
        self.tool.canvasClicked.connect(self.handle_click)
        self.tool.deactivated.connect(self.reset_clicks)
        self.clicks = []

        self.layer = None

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

    def show_error(self, message, title='Error', **kwargs):
        self.iface.messageBar().pushMessage(
            title, message, level=QgsMessageBar.CRITICAL, **kwargs)

    def show_info(self, message, **kwargs):
        self.iface.messageBar().pushMessage(
            message, level=QgsMessageBar.INFO, **kwargs)

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

        self.add_action(
            ':/plugins/CircleCraters/start.png',
            text=self.tr(u'Select Layers for Crater Counting'),
            callback=self.show_layer_select,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            ':/plugins/CircleCraters/stop.png',
            text=self.tr(u'Stop Crater Counting'),
            callback=self.stop_tool,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            ':/plugins/CircleCraters/3points.png',
            text=self.tr(u'Circle Craters'),
            callback=self.set_tool,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            ':/plugins/CircleCraters/export.png',
            text=self.tr(u'Export Data'),
            callback=self.show_export_dialog,
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

        self.draw_circle(Circle(*self.clicks))
        self.reset_clicks()

    def set_tool(self):
        """Run method that performs all the real work"""
        if not self.layer:
            error = 'No crater counting layer selected. Please choose a layer.'
            self.show_error(error)
        self.canvas.setMapTool(self.tool)

    def stop_tool(self):
        """Run method that deactivates the crater counting tool"""
        self.canvas.unsetMapTool(self.tool)
        self.layer = None

    def show_layer_select(self):
        """ Run method that lets users choose layer for crater shapefile.
        Sets self.layer
        """
        try:
            self.choose_dlg.show()
        except Exception as error:
            self.show_error(error.message)

    def on_layer_select(self, layer):
        self.layer = layer
        self.set_field_attributes()

        msg = 'The layer "{!s}" is set as the crater counting layer'
        self.show_info(msg.format(layer.name()))

        self.set_tool()

    def set_field_attributes(self):
        if self.layer.fieldNameIndex('diameter') == -1:
            field_attribute = [QgsField('diameter', QVariant.Double)]
            self.layer.dataProvider().addAttributes(field_attribute)

        if self.layer.fieldNameIndex('center_lat') == -1:
            field_attribute = [QgsField('center_lat', QVariant.Double)]
            self.layer.dataProvider().addAttributes(field_attribute)

        if self.layer.fieldNameIndex('center_lon') == -1:
            field_attribute = [QgsField('center_lon', QVariant.Double)]
            self.layer.dataProvider().addAttributes(field_attribute)

        # TODO: decide what to do with useless useless 'id' field.
        # self.layer.dataProvider().deleteAttributes([0])
        # print self.layer.dataProvider().attributeIndexes()
        # print self.layer.dataProvider().fields()

        self.layer.updateFields()

    def show_export_dialog(self):
        """ Run method that exports data to a file"""
        try:
            self.export_dlg.show()
        except Exception as error:
            self.show_error(error.message)

    def export(self, crater_layer, area_layer, filename):
        try:
            self.write_diam_file(crater_layer, area_layer, filename)
        except Exception as error:
            self.show_error(error.message)

    def create_diam_header(self, total_area):
        current_datetime = str(datetime.datetime.now())
        header = [
            '# Diam file for Craterstats',
            '# Date of measurement export = {}'.format(current_datetime),
            '#',
            'Area <km^2> = {}'.format(total_area),
            '#',
            '#diameter, fraction, lon, lat',
            '',
        ]
        return '\n'.join(header)

    def write_diam_file(self, crater_layer, area_layer, filename):
        """Method writes crater data to a special formatted file."""
        total_area = self.compute_area(area_layer)
        print 'Area in meters squared: ', total_area

        header = self.create_diam_header(total_area)
        nested_list = self.format_diam_data()

        # tab delimited datafile
        with open(filename, 'w') as fp:
            fp.write(header)
            fp.writelines('\t'.join(i) + '\n' for i in nested_list)

    def get_distance_area(self, layer):
        # Call up the CRS
        crs = layer.dataProvider().crs()
        distance_area = QgsDistanceArea()
        distance_area.setSourceCrs(crs)
        distance_area.setEllipsoid(crs.ellipsoidAcronym())
        distance_area.setEllipsoidalMode(crs.geographicFlag())
        return distance_area

    def convert_meters_to_km(self, meters):
        return meters * 0.001

    def measure(self, layer, geometry):
        return self.get_distance_area(layer).measure(geometry)

    def compute_area(self, layer):
        """Returns values are in meters resp. square meters
        http://qgis.org/api/2.6/classQgsDistanceArea.html
        use measure() takes QgsGeometry as a parameter and calculates distance
        or area
        """
        distance_area = self.get_distance_area(layer)
        features = layer.getFeatures()
        return sum([distance_area.measure(f.geometry()) for f in features])

    def get_fields(self, feature, diameter, lon, lat):
        """Retrieves fields from the attribute table in the order required
        for .diam file: diameter, fraction, lon, lat
        And casts as strings"""
        # diameter is in units of km
        attributes = feature.attributes()
        # fraction is always 1
        fraction = 1
        # refer to an attribute by its index
        field_list = [
            str(self.convert_meters_to_km(attributes[diameter])),
            str(fraction),
            str(attributes[lon]),
            str(attributes[lat]),
        ]
        return field_list

    def pixels_to_meters(self, layer, pixels):
        line = [QgsPoint(0.0, 0.0), QgsPoint(0.0, pixels)]
        geometry = QgsGeometry.fromPolyline(line)
        return self.measure(layer, geometry)

    def intersects(self, crater, areas):
        geometry = crater.geometry()
        return any(geometry.intersects(area.geometry()) for area in areas)

    def format_diam_data(self, crater_layer, area_layer):
        """Formats crater diameter data for export as .diam file
        Checks to see if craters intersect with area polygons in area layer
        """
        diameter = crater_layer.fieldNameIndex('diameter')
        lat = crater_layer.fieldNameIndex('center_lat')
        lon = crater_layer.fieldNameIndex('center_lon')

        craters = list(crater_layer.getFeatures())
        areas = list(area_layer.getFeatures())

        craters = [c for c in craters if self.intersects(c, areas)]
        return [self.get_fields(c, diameter, lon, lat) for c in craters]

    def draw_circle(self, circle):
        polygon = [QgsPoint(*point) for point in circle.to_polygon()]
        geometry = QgsGeometry.fromPolygon([polygon])

        feature = QgsFeature()
        feature.setGeometry(geometry)

        # Create a line geometry to represent radius
        diameter = self.pixels_to_meters(self.layer, circle.diameter)

        # circle_feature.id() is NULL right now
        feature.setAttributes([
            feature.id(),
            diameter,
            circle.center.x,
            circle.center.y,
        ])

        self.layer.startEditing()
        self.layer.dataProvider().addFeatures([feature])
        self.layer.commitChanges()

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        self.layer.updateExtents()
