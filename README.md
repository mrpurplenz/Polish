Polish
======

A plugin for handling polish format files in QGIS. Originally envisioned by Mr Purple.

Premise
=======

Polish format map files (suffix .mp) are a useful human readable and well documented file format for mapping. Its particularly useful for the preparation of maps for GARMIN compatible GPSr units. The aim of this plugin is therefore to provide functions for reading from and writing to files in the polish format within an installation of QGIS.

A long term goal is to also handle the pv file format for managing sets of map tiles or (mapsets)

A further long term goal is to incorporate the use of cross platform map and mapset compilers such as gmaptool and mkgmap or maptk

Function objectives:
====================

Export to Polish format
-----------------------
Import from Polish format
-------------------------
Compile Polish file to img
-------------------------
Compile list of Polish files to mapset
--------------------------------------


Installation
============
First install QGIS

This plugin is installable by downloading and extracting the Polish folder into
<QGIS installation folder>\apps\qgis\python\plugins
and then activating it by going to "plugins/manage and install plugins" then select "Polish"

The functions can be accessed from the console as follows
First display the console by clicking "plugins/python console"

Then in the console you can run the functions with:

	from qgis import utils
	Polish = utils.plugins['Polish']
	Polish.functionname()

Usage:
------

Import from Polish format
-------------------------
The main import code is complete you can import a 'list' of polish format files into QGIS from the consol with the command

	from qgis import utils
	Polish = utils.plugins['Polish']
	polish_file_list=[]
	polish_file_list.append('path/to/polish/format/file1.mp')
	polish_file_list.append('path/to/polish/format/file2.mp')
	list_of_layer_handles=Polish.import_polish_files(polish_file_list)


I've still to write the code to pull the routing information from the attributes into a working routing graph

Export to Polish format
-------------------------
To use this function from the console:

	from qgis import utils
	Polish_object_instance = utils.plugins['Polish']
	shape_file_list=[]
	shape_file_list.append("path/to/shapefile1.shp")
	shape_file_list.append("path/to/shapefile2.shp")
	Polish_object_instance.export_files_as_polish(shape_file_list,'output.mp')

In order to get attributes such as object name into the output file you need to create some specifically named fields for example

MP_BIT_LVL containing an integer representing the bit level at which the feature should be displayed when zooming in from infinity

MP_NAME containing NOT THE LABEL OF THE FEATURE but the name of the attribute which contains the lable you wish to display for that feature or MP_LABEL containing the name of the feature (not yet implimented)

MP_DTA_LVL contains an integer representing the bit level at which the feature should cease to display when zooming in from infinity

MP_TYPE containing a string of the polish type code to use in the output file

At some point I will add a print_available_attrs function so you can see what attributes will be parsed by the plugin. At this stage only those attributes given above will be parsed and output to polish format.

Compile to img file
-------------------

This function while available has yet to have instructions written for it


Compile to mapset
-----------------

This function while available has yet to have instructions written for it.

