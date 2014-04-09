Polish
======

A plugin for handling polish format files in QGIS. Originally envisioned by Mr Purple.

Premise
=======

Polish format map files (suffix .mp) are a useful human readable and well documented file format for mapping. Its particularly useful for the preparation of maps for GARMIN compatible GPSr units. The aim of this plugin is therefore to provide functions for reading from and writing to files in the polish format within an installation of QGIS.

A long term goal is to also handle the pv file format for managing sets of map tiles or (mapsets)

A further long term goal is to incorporate the use of cross platform map and mapset compilers such as gmaptool and mkgmap or maptk

Function objectives
===================

Export to Polish format
=======================
This function is now working:

how to export files or layers as a polish format file:

Polish format files contain objects with zoom level attributes in order to set these attributes you need to add attributes to the layers an populate the attributes for the featurews in those layers yourself

MP_BIT_LVL containing an integer representing the bit level at which the feature should be displayed when zooming in from infinity

MP_NAME containing NOT THE LABEL OF THE FEATURE but the name of the attribute which contains the lable you wish to display for that feature

MP_DTA_LVL contains an integer representing the bit level at which the feature should cease to display when zooming in from infinity

MP_TYPE containing a string of the polish type code to use in the output file

Usage:
------
To use this function from the console:

from qgis import utils
Polish_object_instance = utils.plugins['Polish']
files_list=[]
files_list.append("filename1.shp")
files_list.append("filename2.shp")
Polish_object_instance.export_files_as_polish(files_list,'output.mp')



Import from Polish format
-------------------------
The second function is to import a selection of polish format files into a spatialite database. The use of a spatialite database allows for retention of the routing and turn restriction information that would otherwise be lost.

The resulting spatialite file will be routable using spatialite.

Installation
============
First install QGIS

This plugin is installable by downloading and extracting the Polish folder into
<QGIS installation folder>\apps\qgis\python\plugins
and then activating it by going to "plugins/manage and install plugins" then select "Polish"

Access the functions from the console using

from qgis import utils

Polish = utils.plugins['Polish']

Polish.functionname()
