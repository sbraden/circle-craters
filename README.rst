===============================
circle-craters
===============================

A crater-counting python plugin for `QGIS`_.

Current Status: In Testing

Originally written for and tested on QGIS version 2.6 (Brighton). Ported to python3/QGIS version 3.16.

Features include:

* Flexibility to crater count in a GIS environment on Windows, OS X, or Linux
* Free software: BSD license
* Three-click input defines crater rims as a circle
* Projection independent

Details
-------

* This QGIS plugin is designed to offer an open source alternative to the
  `craterTools`_ plugin for `ArcGIS`_.

* `Crater counting`_ is a technique used by planetary scientists to estimate the
  age of a surface.

* Collaboration is welcome! Please see the Issues page and the CONTRIBUTING.rst
  file.

* CircleCraters was initially presented at the `2015 Lunar and Planetary Science
  Conference`_

* This plugin will be submitted to the QGIS plugin repository.

* At this time the plugin does works on QGIS 3.16

Installation
------------

1. First install QGIS.

2. Download the contents of the git repository using the git clone command or
   downloading a zipfile.

3. Use the makefile to compile and copy the files to the QGIS plugin directory
   (run make deploy). 

   On GNU/Linux systems, the QGIS plugin directory should be in 
   
      ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

   On OSX system, the QGIS plugin directory should be in
   
      ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/

4. On the command line run::

       $ make deploy

5. You may get see the following error messages::

       make: pyrcc5: Command not found.

   If you see this message install the Python Qt5 developer tools by running::

   On GNU/Linux systems::
    Debian/Ubuntu:
       $ sudo apt-get install pyqt5-dev-tools
    RHEL/CentOS/Fedora:
       $ yum groupinstall "C Development Tools and Libraries"
       $ yum install qt5-qtbase-devel
   On OSX system::

       $ brew install pyqt

   Another commmon error::

       make: sphinx-build: Command not found

   If you see this message install the python sphinx library by running::

   On GNU/Linux systems::
    Debian/Ubuntu:
       $ sudo apt-get install python3-sphinx
    RHEL/CentOS/Fedora:
       $ yum install python-sphinx
   On OSX system::

       $ brew install sphinx-doc
   
   Notice that sphinx is keg-only by default. Please make sure that sphinx has been added to system PATH.

6. Enable the plugin from the QGIS plugin manager. Go to Plugins > Manage and
   Install Plugins. This will connect you to the official QGIS plugin
   repository, but also searches the QGIS plugin directory on your machine for
   plugins. Find Circle Craters in the list and select the checkbox to the left
   of the name.

Installation Tips for QGIS
--------------------------

`Instructions on QGIS.org`_. Hopefully this encourages you to try out QGIS if
you have not used it before for planetary data!

Windows / Linux / MacOSX QGIS Installers: https://qgis.org/en/site/forusers/download.html

Contributing
------------

Feedback, issues, and contributions are always gratefully welcomed. See the
`contributing guide`_ for details.

.. _QGIS: http://www.qgis.org
.. _craterTools: http://hrscview.fu-berlin.de/software.html
.. _ArcGIS: http://www.esri.com/software/arcgis
.. _Crater counting: http://en.wikipedia.org/wiki/Crater_counting
.. _2015 Lunar and Planetary Science Conference: http://www.hou.usra.edu/meetings/lpsc2015/pdf/1816.pdf
.. _Instructions on QGIS.org: http://www2.qgis.org/en/site/forusers/download.html
.. _Homebrew: http://brew.sh/
.. _this tap: https://github.com/OSGeo/homebrew-osgeo4mac
.. _contributing guide: https://github.com/sbraden/circle-craters/blob/master/CONTRIBUTING.rst
