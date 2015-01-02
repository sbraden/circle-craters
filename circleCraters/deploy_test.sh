#!/bin/bash

# QGIS plugin directory
destination=/Users/sbraden/.qgis2/python/plugins/circle-craters
source_dir=/Users/sbraden/workspace/circle-craters
# copy files in repo workspace to qgis plugin folder
# cp -r /Users/sbraden/workspace/circle-craters/ $destination/
cp $source_dir/Makefile $destination/Makefile
cp $source_dir/README.md $destination/README.md
cp $source_dir/__init__.py $destination/__init__.py
cp $source_dir/circle_craters.py $destination/circle_craters.py
cp $source_dir/circle_craters_dialog.py $destination/circle_craters_dialog.py
cp $source_dir/icon.png $destination/icon.png
cp $source_dir/metadata.txt $destination/metadata.txt
cp $source_dir/resources.qrc $destination/resources.qrc
cp $source_dir/circle_craters_dialog_base.ui $destination/circle_craters_dialog_base.ui

cp $source_dir/rectangle_example.py $destination/rectangle_example.py
# Compile the ui file using pyuic4
pyuic4 $destination/ui_circlecraters.ui> $destination/ui_circlecraters.py
#Compile the resources file using pyrcc4
pyrcc4 $destination/resources.qrc > $destination/resources.py

echo "Deploy Successful"
