#!/bin/bash

# QGIS plugin directory
destination=/Users/sbraden/.qgis2/python/plugins/circle-craters

source_dir=/Users/sbraden/workspace/circle-craters/circleCraters

# copy files in repo workspace to qgis plugin folder
cp -r $source_dir/ $destination/

# Compile the ui file using pyuic4
pyuic4 $destination/ui_circlecraters.ui> $destination/ui_circlecraters.py

#Compile the resources file using pyrcc4
pyrcc4 $destination/resources.qrc > $destination/resources.py

echo "Deploy Successful"
