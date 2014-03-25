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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load CircleCraters class from file CircleCraters
    from circlecraters import CircleCraters
    return CircleCraters(iface)
