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
import datetime

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon, QColor

from qgis.core import QgsPoint, QgsGeometry, QgsFeature, QgsMapLayerRegistry, QgsMapLayer, QgsErrorMessage, QgsField, QgsDistanceArea
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand

# Initialize Qt resources from file resources.py
import resources_rc  # noqa

from circle_craters_dialog import CircleCratersDialog
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
        # TODO: rename to export_dlg
        self.dlg = CircleCratersDialog()
        self.choose_dlg = ChooseLayersDialog()

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
            callback=self.prep_tool,
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

        circle = Circle(self.clicks[0], self.clicks[1], self.clicks[2])
        self.draw_circle(circle.center.x, circle.center.y, circle.radius)

        self.reset_clicks()

    def set_tool(self):
        """Run method that performs all the real work"""
        if self.layer:
            self.canvas.setMapTool(self.tool)
        else:
            msg = 'No crater counting layer selected. Please choose a layer.'
            self.iface.messageBar().pushMessage('User Error:', msg)

    def stop_tool(self):
        """Run method that deactivates the crater counting tool"""
        self.canvas.unsetMapTool(self.tool)
        self.layer = None

    def prep_tool(self):
        """ Run method that lets users choose layer for crater shapefile.
        Sets self.layer
        """
        self.choose_dlg.show()
        # Fetch all loaded layers
        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                # Add these layers to the combobox (dropdown menu)
                self.choose_dlg.craterLayer.addItem(layer.name(), layer)
                self.choose_dlg.areaLayer.addItem(layer.name(), layer)

        # Run the dialog event loop
        result = self.choose_dlg.exec_()

        # See if OK was pressed
        if result == 1:

            if self.choose_dlg.craterLayer.currentIndex() == -1:
                msg = 'No choice of layers available. Please create polygon type vector layers.'
                self.iface.messageBar().pushMessage('User Error', msg)
                return

            crater_index = self.choose_dlg.craterLayer.currentIndex()
            crater_layer = self.choose_dlg.craterLayer.itemData(crater_index)
            area_index = self.choose_dlg.areaLayer.currentIndex()
            area_layer = self.choose_dlg.areaLayer.itemData(area_index)
            print 'Area Layer name:', area_layer.name()

            self.layer = crater_layer
            self.set_field_attributes()

            msg = 'The layer: "{}" is set as the crater counting layer'.format(crater_layer.name())
            self.iface.messageBar().pushMessage('Info', msg)

            self.set_tool()

    def set_field_attributes(self):
        if self.layer.fieldNameIndex('diameter') == -1:
            field_attribute = [QgsField('diameter', QVariant.Double)]
            result = self.layer.dataProvider().addAttributes(field_attribute)

        if self.layer.fieldNameIndex('center_lat') == -1:
            field_attribute = [QgsField('center_lat', QVariant.Double)]
            result = self.layer.dataProvider().addAttributes(field_attribute)

        if self.layer.fieldNameIndex('center_lon') == -1:
            field_attribute = [QgsField('center_lon', QVariant.Double)]
            result = self.layer.dataProvider().addAttributes(field_attribute)

        # removes useless 'id' field,
        # could cause problems if 'id' field doesn't exist, which it wouldn't if the file has already been edited
        # self.layer.dataProvider().deleteAttributes([0])

        # print self.layer.dataProvider().attributeIndexes()
        # print self.layer.dataProvider().fields()

        self.layer.updateFields()

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
            self.crater_export_layer = self.dlg.craterLayer.itemData(crater_index)

            area_index = self.dlg.areaLayer.currentIndex()
            self.area_export_layer = self.dlg.areaLayer.itemData(area_index)

            self.write_diam_file(self.dlg.editDirectory.text(), self.dlg.editFilename.text())

    def create_diam_header(self, total_area):
        current_datetime = str(datetime.datetime.now())
        header_lines = [
            '# Diam file for Craterstats\n',
            '# Date of measurement export = ' + current_datetime + '\n',
            '#\n',
            'Area <km^2> = ' + str(total_area) + '\n',
            '#\n',
            '#diameter, fraction, lon, lat\n',
        ]
        return header_lines

    def write_diam_file(self, directory, filename):
        """Method writes crater data to a special formatted file."""
        if os.path.exists(directory):

            total_area = self.compute_area()
            print 'Area in meters squared: ', total_area
            header_lines = self.create_diam_header(total_area)
            # This is where you will check for intersection
            self.check_for_intersection()
            nested_list = self.format_diam_data()

            # table delimited datafile
            with open(os.path.join(directory, filename + '.diam'), 'w') as f:
                for line in header_lines:
                    f.write(line)
                f.writelines('\t'.join(i) + '\n' for i in nested_list)
        else:
            msg = 'The directory "{}" does not exist.'.format(directory)
            self.iface.messageBar().pushMessage('User Error', msg)

    def convert_meters_to_km(self, meters):
        return meters * 0.001

    def area(self, d, feature):
        return d.measure(feature.geometry())

    def compute_area(self):
        """Returns values are in meters resp. square meters
        http://qgis.org/api/2.6/classQgsDistanceArea.html
        use measure() takes QgsGeometry as a parameter and calculates distance or area
        """
        # Call up the CRS
        provider = self.area_export_layer.dataProvider()
        crs = provider.crs()
        d = QgsDistanceArea()
        d.setSourceCrs(crs)
        d.setEllipsoid(crs.ellipsoidAcronym())
        d.setEllipsoidalMode(crs.geographicFlag())

        features = self.area_export_layer.getFeatures()
        areas = [self.area(d, f) for f in features]
        return sum(areas)

    def check_for_intersection(self):

        features = self.area_export_layer.getFeatures()
        for f in features:
            points = self.crater_export_layer.getFeatures()
            for p in points:
                print f.geometry().intersects(p.geometry())

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

    def convert_diam_to_meters(self, feature):
        # Call up the CRS
        provider = self.layer.dataProvider()
        crs = provider.crs()
        d = QgsDistanceArea()
        d.setSourceCrs(crs)
        d.setEllipsoid(crs.ellipsoidAcronym())
        d.setEllipsoidalMode(crs.geographicFlag())

        return d.measure(feature.geometry())

    def format_diam_data(self):
        """Formats crater diameter data for export as .diam file"""
        features = self.crater_export_layer.getFeatures()
        diameter = self.crater_export_layer.fieldNameIndex('diameter')
        lat = self.crater_export_layer.fieldNameIndex('center_lat')
        lon = self.crater_export_layer.fieldNameIndex('center_lon')

        data = [self.get_fields(f, diameter, lon, lat) for f in features]
        return data

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

        # Create a line geometry to represent radius
        radius_line = [QgsPoint(0.0, 0.0), QgsPoint(0.0, r)]
        print radius_line
        radius_geometry = QgsGeometry.fromPolyline(radius_line)
        line = QgsFeature()
        line.setGeometry(radius_geometry)

        radius_in_meters = self.convert_diam_to_meters(line)
        print 'Radius in meters:', radius_in_meters

        # feature.id() is NULL right now
        feature.setAttributes([feature.id(), radius_in_meters * 2, x, y])

        self.layer.startEditing()

        (result, feat_list) = self.layer.dataProvider().addFeatures([feature])
        self.rb.setToGeometry(geometry, None)

        # commit to stop editing the layer
        self.layer.commitChanges()
        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        self.layer.updateExtents()
