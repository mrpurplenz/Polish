Polish
======

A plugin for handling polish format files in QGIS

Premise
=======

Polish format map files (suffix .mp) are a useful human readable and well documented file format for mapping. Its particularly useful for the preparation of maps for GARMIN compatible GPSr units. The aim of this plugin is therefore to provide functions for reading from and writing to files in the polish format within an installation of QGIS.

A long term goal is to also handle the pv file format for managing sets of map tiles or (mapsets)

A further long term goal is to incorporate the use of cross platform map and mapset compilers such as gmaptool and mkgmap or maptk

Function objectives
===================

Export to Polish format
-----------------------
The first function to write is the export_to_polish function which will take a list of QGIS map layers and output a polish format file.

This will be acheived by reading in each feature of each layer and generating the text output into an output .mp file

The header data of the output file will have default values which can be modified through teh use of a template file or by passing a dictionary of header key:value combinations.

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
