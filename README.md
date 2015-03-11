circle-craters
==============

A crater-counting python plugin for [QGIS](http://www.qgis.org).
Circle, circle, dot, dot now you've got your craters.

Current Status: In Testing

Written for and tested on QGIS version 2.6 (Brighton).

##Details

* This QGIS plugin is designed to offer an open source alternative to the [craterTools](http://hrscview.fu-berlin.de/software.html) plugin for [ArcGIS](http://www.esri.com/software/arcgis).

* [Crater counting](http://en.wikipedia.org/wiki/Crater_counting) is a technique used by planetary scientists to estimate the age of a surface.

* I do not endeavour to replace all the functionality of ArcGIS craterTools, but start from the basics and work up.

* Collaboration is welcome! Please see the Issues page.

* CircleCraters was initially presented at the [2015 Lunar and Planetary Science Conference](http://www.hou.usra.edu/meetings/lpsc2015/pdf/1816.pdf)

* This plugin will be submitted to the QGIS plugin repository.

* At this time the plugin does not work properly on QGIS 2.8 (Wien)

##How to install circle-craters

1. First install QGIS.

2. Download the contents of the git repository using the git clone command or downloading a zipfile.

3. Use the makefile to compile and copy the files to the QGIS plugin directory (run make deploy). The QGIS plugin directory should be in ~/.qgis2/python/plugins.

4. You may get see the following error messages when running make deploy:

    make: pyrcc4: Command not found.

    If you see this message install the Python Qt4 developer tools by running:

    sudo apt-get install pyqt4-dev-tool.

    make: sphinx-build: Command not found

    If you see this message install the python sphinx library by running:

    sudo apt-get install python-sphinx

4. Enable the plugin by enabling it in the QGIS plugin manager. Go to Plugins > Manage and Install Plugins. This will connect you to the official QGIS plugin repository, but also searches the QGIS plugin directory on your machine for plugins. Find Circle Craters in the list and select the checkbox to the left of the name.

##How to install QGIS

[Instructions on QGIS.org](http://www2.qgis.org/en/site/forusers/download.html). Hopefully this encourages you to try out QGIS if you have not used it before for planetary data!

###Alternate Install For Mac OSX

The QGIS website links to a set of Mac OS X installers for QGIS. An alternative is to use Homebrew.

1. Install [Homebrew](http://brew.sh/)

2. Install GDAL with home brew

3. Install Qt with home brew (remember to link, QGIS uses version 4.8 at this time)

4. Install Pyqt with home brew

5. Install Numpy with home brew

6. Install Matplotlib with home brew

7. Install QGIS. Note: The brew/science tap is not the most stable tap for QGIS. It is recommended to use [this tap](https://github.com/OSGeo/homebrew-osgeo4mac).


