# -*- coding: utf-8 -*-
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import urllib
import xml.etree.ElementTree as etree
import io
import os
import processing
from qgis.analysis import *
from pyspatialite import dbapi2 as db
from qgis import core
from qgis import *
from qgis import utils
from qgis.utils import *
import re
import random
import sys
import shutil
import tempfile
import platform
import getpass
from os.path import basename
from subprocess import call
import collections
import string
import stat
import subprocess
from subprocess import Popen
from subprocess import PIPE
from subprocess import check_output
from string import digits

def attribute_odict(QGisType):
    default_attributes_odict=None
    if QGisType==QGis.Point:
        default_attributes_odict = collections.OrderedDict()
        #Name in pdf = [default value,data type, attribute name for shp, required for polish bool]
        default_attributes_odict['id'] =[None,QVariant.Int,'id',False]
        default_attributes_odict['Img_id'] = [None,QVariant.Int,'MP_MAP_ID',False]
        default_attributes_odict['Feature_id'] =[None,QVariant.Int,'MP_FEAT_ID',False]
        default_attributes_odict['Type'] = ['0x00',QVariant.String,'MP_TYPE',True]
        default_attributes_odict['Marine'] = ['N',QVariant.String,'MP_MARINE',False]
        default_attributes_odict['City'] = ['N',QVariant.String,'MP_CITY',False]
        default_attributes_odict['Label'] = [None,QVariant.String,'MP_LBL',False]
        default_attributes_odict['EndLevel'] = [None,QVariant.Int,'MP_BIT_LVL',False]
        default_attributes_odict['DataLevel'] = [0,QVariant.Int,'MP_DTA_LVL',True]
        default_attributes_odict['StreetDesc'] = [None,QVariant.String,'MP_SDC',False]
        default_attributes_odict['HouseNumber'] = [None,QVariant.Int,'MP_HSNO',False]
        default_attributes_odict['OvernightParking'] = ['N',QVariant.String,'MP_ONPRK',False]
        default_attributes_odict['Highway'] = [None,QVariant.String,'MP_HWY',False]
        default_attributes_odict['CityName'] = [None,QVariant.String,'MP_CTYNM',False]
        default_attributes_odict['RegionName'] = [None,QVariant.String,'MP_RGNNM',False]
        default_attributes_odict['CountryName'] = [None,QVariant.String,'MP_CNTNM',False]
        default_attributes_odict['Zip'] = [None,QVariant.String,'MP_ZIP',False]
        default_attributes_odict['Exit'] = [None,QVariant.String,'MP_EXIT',False]
        
    if QGisType==QGis.Polygon:
        default_attributes_odict = collections.OrderedDict()
        default_attributes_odict['id'] =[None,QVariant.Int,'id',False]
        default_attributes_odict['Img_id'] = [None,QVariant.Int,'MP_MAP_ID',False]
        default_attributes_odict['Feature_id'] =[None,QVariant.Int,'MP_FEAT_ID',False]
        default_attributes_odict['Type'] = ['0x00',QVariant.String,'MP_TYPE',True]
        default_attributes_odict['Marine'] = ['N',QVariant.String,'MP_MARINE',False]
        default_attributes_odict['Label'] = [None,QVariant.String,'MP_LBL',False]
        default_attributes_odict['EndLevel'] = [None,QVariant.Int,'MP_BIT_LVL',False]
        default_attributes_odict['Background'] = ['N',QVariant.String,'MP_BKGRND',False]
        default_attributes_odict['DataLevel'] = [0,QVariant.Int,'MP_DTA_LVL',True]

    if QGisType==QGis.Line:
        default_attributes_odict = collections.OrderedDict()
        default_attributes_odict['id'] =[None,QVariant.Int,'id',False]
        default_attributes_odict['Img_id'] = [None,QVariant.Int,'MP_MAP_ID',False]
        default_attributes_odict['Feature_id'] =[None,QVariant.Int,'MP_FEAT_ID',False]
        default_attributes_odict['Type'] = ['0x00',QVariant.String,'MP_TYPE',True]
        default_attributes_odict['Marine'] = ['N',QVariant.String,'MP_MARINE',False]
        
        default_attributes_odict['Label'] = [None,QVariant.String,'MP_LBL',False]
        default_attributes_odict['Label2'] = [None,QVariant.String,'MP_LBL2',False]
        default_attributes_odict['EndLevel'] = [None,QVariant.Int,'MP_BIT_LVL',False]
        default_attributes_odict['DataLevel'] = [0,QVariant.Int,'MP_DTA_LVL',True]
        default_attributes_odict['StreetDesc'] = [None,QVariant.String,'MP_ST_DSC',False]
        default_attributes_odict['DirIndicator'] = [0,QVariant.Int,'MP_DIR_IND',False]
        default_attributes_odict['CityName'] = [None,QVariant.String,'MP_CTYNM',False]
        default_attributes_odict['RegionName'] = [None,QVariant.String,'MP_RGNNM',False]
        default_attributes_odict['CountryName'] = [None,QVariant.String,'MP_CNTNM',False]
        default_attributes_odict['Zip'] = [None,QVariant.String,'MP_ZIP',False]
        
        #Routing specific
        default_attributes_odict['RoadID'] = [None,QVariant.Int,'MP_ROAD_ID',False]
        for n in range(1, 60):
            default_attributes_odict['Numbers'+str(n)]= [None,QVariant.String,'MP_NUM'+str(n),False]
        default_attributes_odict['Routeparam'] = ['3,4,0,0,0,0,0,0,0,0,0,0',QVariant.String,'MP_ROUTE',False]
        default_attributes_odict['NodIDs']=[None,QVariant.String,'MP_NODES',False]#eg '1,0,1002,0|2,1,1003,0'
    if QGisType==QGis.UnknownGeometry:
        raise ValueError('Cannot build layer for UnknownGeometry',QGisType)
    
    if default_attributes_odict==None:
        raise ValueError('Unknown QGisType',QGisType)
    return default_attributes_odict
  

def WKBType_to_type(QGisWKBType):
 
    if QGisWKBType==0:#WKBUnknown
        return QGis.UnknownGeometry
    if QGisWKBType==1:#WKBPoint
        return QGis.Point
    if QGisWKBType==2:#WKBLineString 
        return QGis.Line
    if QGisWKBType==3:#WKBPolygon
        return QGis.Polygon
    if QGisWKBType==4:#WKBMultiPoint 
        return QGis.Point
    if QGisWKBType==5:#WKBMultiLineString 
        return QGis.Line
    if QGisWKBType==6:#WKBMultiPolygon 
        return QGis.Polygon
    if QGisWKBType==7:#WKBMultiPolygon 
        return QGis.NoGeometry
        
def QGisWktType_to_text(QGisWKBType):
    if QGisWKBType==0:#WKBUnknown
        return "Unknown"
    if QGisWKBType==1:#WKBPoint
        return "Point"
    if QGisWKBType==2:#WKBLineString 
        return "LineString"
    if QGisWKBType==3:#WKBPolygon
        return "Polygon"
    if QGisWKBType==4:#WKBMultiPoint 
        return "MultiPoint"
    if QGisWKBType==5:#WKBMultiLineString 
        return "MultiLineString"
    if QGisWKBType==6:#WKBMultiPolygon 
        return "MultiPolygon"
    if QGisWKBType==7:#WKBMultiPolygon 
        return "NoGeometry"
        QGisType_to_text(WKBType_to_type(QGisWKBType))
def QGisType_to_text(QGisType):
    if QGisType==0:
        return "Point"
    if QGisType==1:
        return "Line"
    if QGisType==2:
        return "Polygon"
    if QGisType==3:
        return "UnknownGeometry"
    if QGisType==4:
        return "NoGeometry"
        
def QGisType_to_URItext(QGisType):
    if QGisType==0:
        return "Point"
    if QGisType==1:
        return "LineString"
    if QGisType==2:
        return "Polygon"
    if QGisType==3:
        return "UnknownGeometry"
    if QGisType==4:
        return "NoGeometry"
        
def verbose():
    return True

def myver():
    return "0.0.2"
    
def get_cGPSmapper_path():
    return r'C:\Program Files (x86)\cGPSmapper'
    
def explode(input_layer,destination_title):
    my_WkbType = { 'WKBUnknown': 0, 'WKBPoint':1, 'WKBLineString':2, 'WKBPolygon':3, 'WKBMultiPoint':4, 'WKBMultiLineString':5, 'WKBMultiPolygon':6, 'WKBNoGeometry':7, 'WKBPoint25D':8, 'WKBLineString25D':9, 'WKBPolygon25D':10, 'WKBMultiPoint25D':11, 'WKBMultiLineString25D':12, 'WKBMultiPolygon25D':13 }
    my_rev_WkbType = {v:k for k, v in my_WkbType.items()}
    my_GeometryType = { 'Point': 0, 'Line':1, 'Polygon':2, 'UnknownGeometry':3, 'NoGeometry':4}
    my_rev_GeometryType = {v:k for k, v in my_GeometryType.items()}
    QGisWKBType=input_layer.dataProvider().geometryType()
    #multiple_type=[4,5,6,11,12,13]
    #multipart=False
    #if QGisWKBType in multiple_type:
    #    multipart=True
    EPSG_code=int(input_layer.dataProvider().crs().authid().split(":")[1])
    #Read layer directly to memory
    destination_layer=QgsVectorLayer(my_rev_WkbType[QGisWKBType][3:]+'?crs=epsg:'+str(EPSG_code)+'&index=no',destination_title,'memory')
    #Add fields to destination layer
    oldattributeList = input_layer.dataProvider().fields().toList()
    newattributeList=[]
    for attrib in oldattributeList:
        if destination_layer.fieldNameIndex(attrib.name())==-1:
            newattributeList.append(QgsField(attrib.name(),attrib.type()))
    destination_layer.dataProvider().addAttributes(newattributeList)
    destination_layer.updateFields()
    destination_layer_attribute_list = input_layer.dataProvider().fields().toList()
    #Copy feataures to new layer
    cfeatures=[]
    for feature in input_layer.getFeatures():
        #Get attributes for this feature
        cfeature_Attributes=[]
        for destination_QGSfield in destination_layer_attribute_list:
            attribute_field=destination_QGSfield.name()
            attr_still_to_append=True
            idx = input_layer.fieldNameIndex(attribute_field)
            if idx>=0:
                cfeature_Attributes.append(feature.attributes()[idx])
                attr_still_to_append=False
            if attr_still_to_append:
                cfeature_Attributes.append(None)
        #Get geometrys
        geom = feature.geometry()
        new_geoms=[]
        if geom.isMultipart():
            new_geoms=geom.asGeometryCollection()
        else:
            new_geoms.append(geom)
        #Add attributes to geometrys
        for new_geom in new_geoms:
            cfeature = QgsFeature()
            cfeature.setGeometry(new_geom)
            cfeature.setAttributes(cfeature_Attributes)
            cfeatures.append(cfeature)
    destination_layer.dataProvider().addFeatures(cfeatures)
    destination_layer.commitChanges()
    destination_layer.updateExtents()
    return destination_layer

def dice(input_layer,destination_name="diced",max_vertices=255):
    import numpy  
    from PyQt4.QtCore import *
    my_WkbType = { 'WKBUnknown': 0, 'WKBPoint':1, 'WKBLineString':2, 'WKBPolygon':3, 'WKBMultiPoint':4, 'WKBMultiLineString':5, 'WKBMultiPolygon':6, 'WKBNoGeometry':7, 'WKBPoint25D':8, 'WKBLineString25D':9, 'WKBPolygon25D':10, 'WKBMultiPoint25D':11, 'WKBMultiLineString25D':12, 'WKBMultiPolygon25D':13 }
    my_rev_WkbType = {v:k for k, v in my_WkbType.items()}
    QGisWKBType=input_layer.dataProvider().geometryType()
    dice_safe_type=False
    dice_safe_types=[1,2,3,4,5,6]
    if QGisWKBType in dice_safe_types:
        dice_safe_type=True
    if not dice_safe_type:
        raise ValueError("Invalid layer type:"+my_rev_WkbType[QGisWKBType][3:])

    layerQGisType = my_rev_WkbType[QGisWKBType][3:]
    EPSG_code=int(input_layer.dataProvider().crs().authid().split(":")[1])
    destination_layer=QgsVectorLayer(QGisType_to_URItext(WKBType_to_type(QGisWKBType))+'?crs=epsg:'+str(EPSG_code)+'&index=yes',destination_name,'memory')

    if not destination_layer.isValid():
        raise ValueError("Failed to create memory layer")
    #Add input_layer attribute fields
    input_layer_attrib_names = input_layer.dataProvider().fields()
    oldattributeList = input_layer.dataProvider().fields().toList()
    newattributeList=[]
    for attrib in oldattributeList:
        if destination_layer.fieldNameIndex(attrib.name())==-1:
            newattributeList.append(QgsField(attrib.name(),attrib.type()))
    destination_layer.dataProvider().addAttributes(newattributeList)
    destination_layer.updateFields()
    destination_layer_attribute_list=destination_layer.dataProvider().fields().toList()
    #Copy features over to the the new memory layer
    first_output_geom_type=None
    destination_layer.startEditing()
    cfeatures=[]
    xfeatures = input_layer.getFeatures()
    for xfeature in xfeatures:
        #Get attributes from feature
        cfeature_Attributes=[]
        for destination_QGSfield in destination_layer_attribute_list:
            attribute_field=destination_QGSfield.name()
            attr_still_to_append=True
            #Get old attribute value and append
            idx = input_layer.fieldNameIndex(attribute_field)
            if idx>=0:
                cfeature_Attributes.append(xfeature.attributes()[idx])
                attr_still_to_append=False
            #Append a Null into any unfound attributes
            if attr_still_to_append:
                cfeature_Attributes.append(None)
                
        gorzirras=[]
        diced=[]
        #Get geometrys from feature
        geom = xfeature.geometry()
        if geom.isMultipart():
            gorzirras=geom.asGeometryCollection()
        else:
            gorzirras.append(geom)
        while len(gorzirras)>0:
            gorzirra=gorzirras.pop()
            if gorzirra.type()==QGis.Point and QGisWKBType in [QGis.WKBPoint,QGis.WKBMultiPoint,QGis.WKBPoint25D,QGis.WKBMultiPoint25D]:
                diced.append(gorzirra)
            if gorzirra.type()==QGis.Line and QGisWKBType in [QGis.WKBLineString,QGis.WKBMultiLineString,QGis.WKBLineString25D,QGis.WKBMultiLineString25D]:
                line_as_list = gorzirra.asPolyline()
                if len(line_as_list)<=max_vertices:
                    diced.append(gorzirra)
                else:
                    diced.append(QgsGeometry.fromPolyline(line_as_list[:max_vertices]))
                    gorzirras.append(QgsGeometry.fromPolyline(line_as_list[(max_vertices-1):]))
            if gorzirra.type()==QGis.Polygon and QGisWKBType in [QGis.WKBPolygon,QGis.WKBMultiPolygon,QGis.WKBPolygon25D,QGis.WKBMultiPolygon25D]:
                xval_list=[]
                yval_list=[]
                ring_list=gorzirra.asPolygon()
                for ring in ring_list:
                    for vertex in ring:
                            xval_list.append(vertex.x())
                            yval_list.append(vertex.y())
                if len(xval_list)<=max_vertices:
                    diced.append(gorzirra)
                else:
                    #Locate longest dimension
                    bbox_rectangle=gorzirra.boundingBox()
                    xmax=bbox_rectangle.xMaximum()
                    ymax=bbox_rectangle.yMaximum()
                    xmin=bbox_rectangle.xMinimum()
                    ymin=bbox_rectangle.yMinimum()
                    dice_X=True
                    if (ymax-ymin)>(xmax-xmin):
                        dice_X=False
                    #Locate median vertex value of long dimension
                    if dice_X:
                        median_val=numpy.median(numpy.array(xval_list))
                    else:
                        median_val=numpy.median(numpy.array(yval_list))
                    #Build dice masks
                    if dice_X:
                        dice_left_geometry=QgsGeometry.fromPolygon( [ [ \
                        QgsPoint(xmin,ymin),\
                        QgsPoint(xmin,ymax), \
                        QgsPoint(median_val,ymax),\
                        QgsPoint(median_val,ymin) ] ] )
                        dice_right_geometry=QgsGeometry.fromPolygon( [ [ \
                        QgsPoint(median_val,ymin),\
                        QgsPoint(median_val,ymax), \
                        QgsPoint(xmax,ymax),\
                        QgsPoint(xmax,ymin) ] ] )
                    else:
                        dice_left_geometry=QgsGeometry.fromPolygon( [ [ \
                        QgsPoint(xmin,ymin),\
                        QgsPoint(xmin,median_val), \
                        QgsPoint(xmax,median_val),\
                        QgsPoint(xmax,ymin) ] ] )
                        dice_right_geometry=QgsGeometry.fromPolygon( [ [ \
                        QgsPoint(xmin,median_val),\
                        QgsPoint(xmin,ymax), \
                        QgsPoint(xmax,ymax),\
                        QgsPoint(xmax,median_val) ] ] )
                    #Apply dice masks
                    left_diced=(gorzirra.intersection(dice_left_geometry)).asGeometryCollection()
                    right_diced=(gorzirra.intersection(dice_right_geometry)).asGeometryCollection()
                    for unpop in left_diced+right_diced:
                        gorzirras.append(unpop)
        for dgeometry in diced:
            ngeometrys=[]
            if dgeometry.isMultipart():
                ngeometrys=dgeometry.asGeometryCollection()
            else:
                ngeometrys.append(dgeometry)
            for ngeometry in ngeometrys:
                #Add attributes to each
                cfeature = QgsFeature()
                cfeature.setGeometry(ngeometry)
                #Populate feature with attributes
                cfeature.setAttributes(cfeature_Attributes)
                cfeatures.append(cfeature)
                #            
                #        dice_this_feature=False
                #        xgeometry = xfeature.geometry()
                #        slices=1
                #        if QGisWKBType==2 or QGisWKBType==5:
                #            if xgeometry.isMultipart():
                #                list_of_geoms= xgeometry.asGeometryCollection()
                #            else:
                #                list_of_geoms=[]
                #                list_of_geoms.append(xgeometry)
                #            for geom in list_of_geoms:
                #                line_as_list = geom.asPolyline()
                #                if len(line_as_list)>max_vertices:
                #                    gorzirras.append(geom)
                #                else:
                #                   diced.append(geom)
                #                while len(gorzirras)>0:
                #                    gorzirra=gorzirras.pop()
                #                    line_as_list = gorzirra.asPolyline()
                #                    dice_left_geometry=QgsGeometry.fromPolyline(line_as_list[:max_vertices])
                #                    diced.append(dice_left_geometry)
                #                    dice_right_geometry=QgsGeometry.fromPolyline(line_as_list[(max_vertices-1):])
                #                    if len(line_as_list)-max_vertices+1>max_vertices:
                #                        gorzirras.append(dice_right_geometry)
                #                    else:
                #                        diced.append(dice_right_geometry)
                #                
                #        if QGisWKBType==3 or QGisWKBType==6:
                #            if xgeometry.isMultipart():
                #               list_of_geoms= xgeometry.asGeometryCollection()
                #            else:
                #                list_of_geoms=[]
                #                list_of_geoms.append(xgeometry)
                #            for geom in list_of_geoms:
                #                rings = geom.asPolygon()
                #                no_vertices=0
                #                for ring in rings:
                #                    no_vertices = no_vertices+len(ring)
                #                if no_vertices>max_vertices:
                #                    gorzirras.append(geom)
                #                else:
                #                    diced.append(geom)
                #                
                #                while len(gorzirras)>0:
                #                    slices+=1
                #                    gorzirra=gorzirras.pop()
                #                    #Determine longer dimension to split
                #                    bbox_rectangle=gorzirra.boundingBox()
                #                    xmax=bbox_rectangle.xMaximum()
                #                    ymax=bbox_rectangle.yMaximum()
                #                    xmin=bbox_rectangle.xMinimum()
                #                    ymin=bbox_rectangle.yMinimum()
                #                    dice_X=True
                #                    if (ymax-ymin)>(xmax-xmin):
                #                        dice_X=False
                #                    #Locate median vertex value of long dimension
                #                    ring_list=gorzirra.asPolygon()
                #                    val_list=[]
                #                    for ring in ring_list:
                #                        for vertex in ring:
                #                            if dice_X:
                #                                val_list.append(vertex.x())
                #                            else:
                #                                val_list.append(vertex.y())
                #                    median_val=numpy.median(numpy.array(val_list))
                #                    if dice_X:
                #                        dice_left_geometry=QgsGeometry.fromPolygon( [ [ \
                #                        QgsPoint(xmin,ymin),\
                #                        QgsPoint(xmin,ymax), \
                #                        QgsPoint(median_val,ymax),\
                #                        QgsPoint(median_val,ymin) ] ] )
                #                        
                #                        dice_right_geometry=QgsGeometry.fromPolygon( [ [ \
                #                        QgsPoint(median_val,ymin),\
                #                        QgsPoint(median_val,ymax), \
                #                        QgsPoint(xmax,ymax),\
                #                        QgsPoint(xmax,ymin) ] ] )
                #                    else:
                #                        dice_left_geometry=QgsGeometry.fromPolygon( [ [ \
                #                        QgsPoint(xmin,ymin),\
                #                        QgsPoint(xmin,median_val), \
                #                        QgsPoint(xmax,median_val),\
                #                        QgsPoint(xmax,ymin) ] ] )
                #                        
                #                        dice_right_geometry=QgsGeometry.fromPolygon( [ [ \
                #                        QgsPoint(xmin,median_val),\
                #                        QgsPoint(xmin,ymax), \
                #                        QgsPoint(xmax,ymax),\
                #                        QgsPoint(xmax,median_val) ] ] )
                #                    
                #                    #Carry out intersections
                #                    left_diced=(gorzirra.intersection(dice_left_geometry)).asGeometryCollection()
                #                    right_diced=(gorzirra.intersection(dice_right_geometry)).asGeometryCollection()
                #                    
                #                    diced_list=left_diced+right_diced
                #                    for diced_geometry in diced_list:
                #                        rings = diced_geometry.asPolygon()
                #                        no_vertices=0
                #                        for ring in rings:
                #                            no_vertices = no_vertices+len(ring)
                #                        if no_vertices>max_vertices:
                #                            gorzirras.append(diced_geometry)
                #                        else:
                #                            #if not diced_geometry.isGeosEmpty():
                #                            diced.append(diced_geometry)
                #        #Create destination features
                #        for pgeometry in diced:
                #            if pgeometry.isMultipart():
                #                list_of_geoms= pgeometry.asGeometryCollection()
                #            else:
                #                list_of_geoms=[]
                #                list_of_geoms.append(pgeometry)
                #            for ngeometry in list_of_geoms:
                #                ok_to_add=False
                #                if first_output_geom_type is None:
                #                    first_output_geom_type=ngeometry.type()
                #                    ok_to_add=True
                #                else:
                #                    if first_output_geom_type==ngeometry.type():
                #                        ok_to_add=True
                #                #if ngeometry.type()==0:
                #                #    ok_to_add=False
                #                if ok_to_add:
                #                    if ngeometry.isMultipart():
                #                        print "STILL MULTIPART??"
                #                    cfeature = QgsFeature()
                #                    cfeature.setGeometry(ngeometry)
                #                    #Populate feature with attributes
                #
                #                cfeature.setAttributes(cfeature_Attributes)
                #                cfeatures.append(cfeature)
    destination_layer.dataProvider().addFeatures(cfeatures)
    destination_layer.commitChanges()
    destination_layer.updateExtents()
    #QgsMapLayerRegistry.instance().addMapLayer(destination_layer)
    return destination_layer

def dehole(input_layer,destination_name="diholed"):
    import numpy  
    from PyQt4.QtCore import *
    my_WkbType = { 'WKBUnknown': 0, 'WKBPoint':1, 'WKBLineString':2, 'WKBPolygon':3, 'WKBMultiPoint':4, 'WKBMultiLineString':5, 'WKBMultiPolygon':6, 'WKBNoGeometry':7, 'WKBPoint25D':8, 'WKBLineString25D':9, 'WKBPolygon25D':10, 'WKBMultiPoint25D':11, 'WKBMultiLineString25D':12, 'WKBMultiPolygon25D':13 }
    my_rev_WkbType = {v:k for k, v in my_WkbType.items()}
    my_GeometryType = { 'Point': 0, 'Line':1, 'Polygon':2, 'UnknownGeometry':3, 'NoGeometry':4}
    my_rev_GeometryType = {v:k for k, v in my_GeometryType.items()}
    QGisWKBType=input_layer.dataProvider().geometryType()
    dice_safe_type=False
    dice_safe_types=[1,2,3,4,5,6]
    if QGisWKBType in dice_safe_types:
        dice_safe_type=True
    if not dice_safe_type:
        raise ValueError("Invalid layer type:"+my_rev_WkbType[QGisWKBType][3:])

    layerQGisType = my_rev_WkbType[QGisWKBType][3:]
    EPSG_code=int(input_layer.dataProvider().crs().authid().split(":")[1])
    destination_layer=QgsVectorLayer(QGisType_to_URItext(WKBType_to_type(QGisWKBType))+'?crs=epsg:'+str(EPSG_code)+'&index=yes',destination_name,'memory')

    if not destination_layer.isValid():
        raise ValueError("Failed to create memory layer")
    #Add input_layer attribute fields
    input_layer_attrib_names = input_layer.dataProvider().fields()
    oldattributeList = input_layer.dataProvider().fields().toList()
    newattributeList=[]
    for attrib in oldattributeList:
        if destination_layer.fieldNameIndex(attrib.name())==-1:
            newattributeList.append(QgsField(attrib.name(),attrib.type()))
    destination_layer.dataProvider().addAttributes(newattributeList)
    destination_layer.updateFields()
    destination_layer_attribute_list=destination_layer.dataProvider().fields().toList()
    #Copy features over to the the new memory layer
    first_output_geom_type=None
    destination_layer.startEditing()
    cfeatures=[]
    xfeatures = input_layer.getFeatures()
    for xfeature in xfeatures:
        #Get attributes from feature
        cfeature_Attributes=[]
        for destination_QGSfield in destination_layer_attribute_list:
            attribute_field=destination_QGSfield.name()
            attr_still_to_append=True
            #Get old attribute value and append
            idx = input_layer.fieldNameIndex(attribute_field)
            if idx>=0:
                cfeature_Attributes.append(xfeature.attributes()[idx])
                attr_still_to_append=False
            #Append a Null into any unfound attributes
            if attr_still_to_append:
                cfeature_Attributes.append(None)
                

        #Get geometrys from feature
        geom = xfeature.geometry()
        gorzirras=[]
        diced=[]
        if geom.isMultipart():
            gorzirras=geom.asGeometryCollection()
        else:
            gorzirras.append(geom)
        while len(gorzirras)>0:
            gorzirra=gorzirras.pop()
            if gorzirra.type()==QGis.Point:
                if QGisWKBType in [QGis.WKBPoint,QGis.WKBMultiPoint,QGis.WKBPoint25D,QGis.WKBMultiPoint25D]:
                    diced.append(gorzirra)
                else:
                    print "WARNING "+my_rev_GeometryType[QGis.Point]+" found for "+my_rev_WkbType[QGisWKBType][3:]+" layer"
            if gorzirra.type()==QGis.Line:
                if QGisWKBType in [QGis.WKBLineString,QGis.WKBMultiLineString,QGis.WKBLineString25D,QGis.WKBMultiLineString25D]:
                    diced.append(gorzirra)
                else:
                    print "WARNING "+my_rev_GeometryType[QGis.Line]+" found for "+my_rev_WkbType[QGisWKBType][3:]+" layer"
            if gorzirra.type()==QGis.Polygon:
                if QGisWKBType in [QGis.WKBPolygon,QGis.WKBMultiPolygon,QGis.WKBPolygon25D,QGis.WKBMultiPolygon25D]:
                    if len(gorzirra.asPolygon())<2:
                        diced.append(gorzirra)
                    else:
                        bbox_rectangle=gorzirra.boundingBox()
                        xmax=bbox_rectangle.xMaximum()
                        ymax=bbox_rectangle.yMaximum()
                        xmin=bbox_rectangle.xMinimum()
                        ymin=bbox_rectangle.yMinimum()
                        slice_X=True
                        if (ymax-ymin)>(xmax-xmin):
                            slice_X=False
                        #locate center of first island
                        gorzirra_polygon=gorzirra.asPolygon()
                        island_center=(QgsGeometry.fromPolygon([gorzirra_polygon[1]])).centroid().asPoint()
                        island_centerx=island_center.x()
                        island_centery=island_center.y()
                        if slice_X:
                            slice_left_geometry=QgsGeometry.fromPolygon( [ [ \
                            QgsPoint(xmin,ymin),\
                            QgsPoint(xmin,ymax), \
                            QgsPoint(island_centerx,ymax),\
                            QgsPoint(island_centerx,ymin) ] ] )
                            slice_right_geometry=QgsGeometry.fromPolygon( [ [ \
                            QgsPoint(island_centerx,ymin),\
                            QgsPoint(island_centerx,ymax), \
                            QgsPoint(xmax,ymax),\
                            QgsPoint(xmax,ymin) ] ] )
                        else:
                            slice_left_geometry=QgsGeometry.fromPolygon( [ [ \
                            QgsPoint(xmin,ymin),\
                            QgsPoint(xmin,island_centery), \
                            QgsPoint(xmax,island_centery),\
                            QgsPoint(xmax,ymin) ] ] )
                            slice_right_geometry=QgsGeometry.fromPolygon( [ [ \
                            QgsPoint(xmin,island_centery),\
                            QgsPoint(xmin,ymax), \
                            QgsPoint(xmax,ymax),\
                            QgsPoint(xmax,island_centery) ] ] )
                        left_sliced=(gorzirra.intersection(slice_left_geometry)).asGeometryCollection()
                        right_sliced=(gorzirra.intersection(slice_right_geometry)).asGeometryCollection()
                        sliced_list=left_sliced+right_sliced
                        for unpop in sliced_list:
                            gorzirras.append(unpop)
                else:
                    print "WARNING "+my_rev_GeometryType[QGis.Polygon]+" found for "+my_rev_WkbType[QGisWKBType][3:]+" layer"
        for dgeometry in diced:
            ngeometrys=[]
            if dgeometry.isMultipart():
                ngeometrys=dgeometry.asGeometryCollection()
            else:
                ngeometrys.append(dgeometry)
            for ngeometry in ngeometrys:
                #Add attributes to each
                cfeature = QgsFeature()
                cfeature.setGeometry(ngeometry)
                #Populate feature with attributes
                cfeature.setAttributes(cfeature_Attributes)
                cfeatures.append(cfeature)
    destination_layer.dataProvider().addFeatures(cfeatures)
    destination_layer.commitChanges()
    destination_layer.updateExtents()
    #QgsMapLayerRegistry.instance().addMapLayer(destination_layer)
    return destination_layer

def get_WINEpath():
    print "checkin wine path now"
    winePath = None
    mypathlist=os.environ["PATH"].split(":")
    for directory in mypathlist:
        testWinePath = os.path.join(directory, "wine")
        if os.path.exists(testWinePath) and os.access(testWinePath, os.R_OK | os.X_OK):
            winePath = testWinePath
            break
    return winePath

def isLinux():
    if platform.system()=='Linux':
        return True
    else:
        return False
        
def isWindows():
    if platform.system()=='Windows':
        return True
    else:
        return False
        
def bit_level(file_header_dict,bit_val):
    #returns the level# associated with a given bit level value
    BIT_LEVEL_DICT = {}
    for key in file_header_dict:
        if key.startswith("Level"):
            if key!="Levels":
                BIT_LEVEL_DICT[int(file_header_dict[key])]=int(str(key[5:]))
    rev_BIT_LEVEL_DICT = {v:k for k, v in BIT_LEVEL_DICT.items()}
    
    try:
        output=BIT_LEVEL_DICT[int(bit_val)]
    except:
        print BIT_LEVEL_DICT
        print "bit_val is:"+str(bit_val)
        print "WARNING INVALID MP_BIT_VAL SETTING DATA LEVEL 0"
        output=0
            
    return output
    
    
def rev_bit_level(file_header_dict,level_val):
    #returns the bit level associated with a given level#
    BIT_LEVEL_DICT = {}
    for key in file_header_dict:
        if key.startswith("Level"):
            if key!="Levels":
                BIT_LEVEL_DICT[file_header_dict[key]]=str(key[5:])
    rev_BIT_LEVEL_DICT = {v:k for k, v in BIT_LEVEL_DICT.items()}
    return rev_BIT_LEVEL_DICT[level_val]
    
def geomWrite(polish_file,pntsgeom,xform,DATA_LVL,compiler="cGPSmapper"):
    dp=12
    if compiler=="MapTk":
        dp=5
    Datastring=''
    firstpoint=0
    pointcount=0
    ok_to_write_data=True
    for myQgsPoint in pntsgeom:
        newQgsPoint=xform.transform(myQgsPoint)
        if firstpoint==0:
            firstpoint=1
            ok_to_write_data=True
            Datastring=Datastring+'Data'+str(DATA_LVL)+'=('+Datastring
        else:
            Datastring=Datastring+',('
        Datastring=Datastring+("{0:."+str(dp)+"f}").format(newQgsPoint.y())+','+("{0:."+str(dp)+"f}").format(newQgsPoint.x())+')'
        if False: #This code is intended to split lines into 255 length lines for MKmap
            pointcount=pointcount+1
            if False:
            #if pointcount==255:
                pointcount=0
                firstpoint=0
                polish_file.write(u''+Datastring+'\n')
                Datastring='('+("{0:."+str(dp)+"f}").format(newQgsPoint.y())+','+("{0:."+str(dp)+"f}").format(newQgsPoint.x())+')'
                ok_to_write_data=False
    if ok_to_write_data:
        polish_file.write(u''+Datastring+'\n')

#def writepolishobject(polish_file,outputtype,MP_TYPE_val,MP_NAME_val,END_LVL_val,DATA_LVL,xform,datalinesgeom):
def writepolishobject(polish_file,outputtype,Feature_attributes_odict,file_header_dict,xform,datalinesgeom,compiler="cGPSmapper"):
    #print polish_file
    #print outputtype
    #print Feature_attributes_odict
    #print file_header_dict
    #print xform
    #print datalinesgeom
    
    if outputtype == '[POI]':
        QGisType=QGis.Point
    if outputtype == '[POLYLINE]':
        QGisType=QGis.Line
    if outputtype == '[POLYGON]':
        QGisType=QGis.Polygon
   
    polish_file.write(u''+outputtype+'\n')
    #XXXXXXXXXXXXXXXXXXXXXXXNEED TO FIND A WAY TO GO ATTR BY ATTR 
    #FROM ODICT WRITING WITH CORRECT FORMAT ALONG THE WAY AND ENFORCING CORRECT FORMAT AND REQIUORED ATTRS
    for Feature_attribute in Feature_attributes_odict:
        attr_name=str(Feature_attribute)
        #print Feature_attributes_odict[attr_name]
        attr_val=Feature_attributes_odict[attr_name]
        if attr_name=="EndLevel": #Convert to level rather than bit thingy
            if attr_val is not None:
                attr_val=bit_level(file_header_dict,attr_val)
                polish_file.write(attr_name+u'='+str(attr_val)+'\n')
                attr_val=None

        if attr_name=="DataLevel": #Convert to level rather than bit thingy
            DATA_LVL=int(attr_val)
            attr_val=None
        if attr_name[:7]=='Numbers':
            pass
            #multi line output but it will go as default
        if attr_name=='NodIDs':
            pass
            #split the string on | for multi line output then set attr_val to None
            if attr_val is not None:
                nod_string_list=attr_val.split("|")
                for nod_string in nod_string_list:
                    Nod_id_string="Nod"+str(nod_string.split(",")[0])
                    Nod_val_string=",".join(nod_string.split(",")[-(len(nod_string.split(","))-1):])
                    polish_file.write(Nod_id_string+u'='+Nod_val_string+'\n')
                    attr_val=None
                
        if attr_name=='id':
            attr_val=None
        if attr_name=='Img_id':
            attr_val=None
        if attr_name=='Feature_id':
            attr_val=None
        if attr_name=='Type':
            if compiler=="cGPSmapper":
                pass
            else:
                attr_val=attr_val.lower()
        if attr_val==attribute_odict(QGisType)[attr_name][0]:
            attr_val=None
            
        if attr_val is not None:
            polish_file.write(str(Feature_attribute)+u'='+str(attr_val)+'\n')
    

    #polish_file.write(u'Type='+str(MP_TYPE_val)+'\n')                    
    #if MP_NAME_val!='':
    #    polish_file.write(u'Label='+str(MP_NAME_val)+'\n')
    #polish_file.write(u'EndLevel='+str(END_LVL_val)+'\n')
    for datalinegeom in datalinesgeom:
        geomWrite(polish_file,datalinegeom,xform,DATA_LVL,compiler)
        
    polish_file.write(u'[END]\n\n')
    
def default_mp_header():
    polishexporter_ver=myver()
    default_header = {}
    default_header['ID'] = random.randint(10000000,99999999)
    default_header['Name']='python exporter map'
    default_header['LBLcoding']=6
    default_header['Codepage']=0
    default_header['Datum']='W84'
    default_header['Transparent']='N'
    default_header['MG']='N'
    default_header['Numbering']='N'
    default_header['Routing']='N'
    default_header['ProductCode']=1
    default_header['Copyright']='map generated by polish exporter '+polishexporter_ver    
    default_header['Elevation']='M'
    default_header['POIIndex']='N'
    default_header['POINumberFirst']='Y'
    default_header['POIZipFirst']='Y'
    default_header['CountryName']=''
    default_header['RegionName']=''
    default_header['TreSize']=1500
    default_header['TreMargin']=0.00000
    default_header['RgnLimit']=1024
    default_header['SimplifyLevel']=1
    default_header['Preprocess']='F'   

    default_header['Levels']=5
    default_header['Level0']=24
    default_header['Level1']=22
    default_header['Level2']=20
    default_header['Level3']=17
    default_header['Level4']=15
    default_header['Zoom0']=0
    default_header['Zoom1']=1
    default_header['Zoom2']=2
    default_header['Zoom3']=3
    default_header['Zoom4']=4

    default_header['Preview']='N'
    default_header['DrawPriority']=25
    default_header['Marine']='N'
    default_header['LeftSideTraffic']='N'
    default_header['NT']='N' 
    default_header['PolygonEvaluate']='Y' 
    
    return default_header
    
def default_pv_header():
    preview_default_dictionary={}
    preview_default_dictionary['FileName']=os.path.join(tempfile.gettempdir(),'Output_file')
    preview_default_dictionary['MapVersion']='100'
    preview_default_dictionary['ProductCode']='1'
    preview_default_dictionary['FID']='222'
    preview_default_dictionary['ID']='1'
    preview_default_dictionary['MG']='Y'
    preview_default_dictionary['Transparent']='Y'
    preview_default_dictionary['Levels']='2'
    preview_default_dictionary['Level0']='14'
    preview_default_dictionary['Level1']='12'

    preview_default_dictionary['Zoom0']='5'
    preview_default_dictionary['Zoom1']='6'
    preview_default_dictionary['Copy1']='Copywrite line one'
    preview_default_dictionary['Copy2']='Copywrite line two'
    preview_default_dictionary['MapsourceName']='QGIS generated MapsourceName'
    preview_default_dictionary['MapSetName']='QGIS generated MapSetName'
    preview_default_dictionary['CDSetName']='QGIS generated CDSetName'
    
    preview_default_dictionary_dictionary={}
    preview_default_dictionary_dictionary['name']='6'
    preview_default_dictionary_dictionary['Level0RGN10']='000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    preview_default_dictionary_dictionary['Level1RGN10']='000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    preview_default_dictionary_dictionary['Level0RGN20']='111111111110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    preview_default_dictionary_dictionary['Level1RGN20']='111111111100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    preview_default_dictionary_dictionary['Level0RGN40']='111110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    preview_default_dictionary_dictionary['Level1RGN40']='111100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    preview_default_dictionary_dictionary['Level0RGN80']='111111111111111111111100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    preview_default_dictionary_dictionary['Level1RGN80']='111111111111111111111100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    preview_default_dictionary['preview_default_dictionary_dictionary']= preview_default_dictionary_dictionary
    return preview_default_dictionary

  
    
def build_create_layer_string(QGisWKBType,epsg_code):
    if QGisWKBType==QGis.WKBUnknown:
        raise ValueError('Cannot build layer for WKBUnknown',QGisWKBType)
    QGisType=WKBType_to_type(QGisWKBType)
    type_string=QGisWktType_to_text(QGisWKBType)
    layer_string=type_string+"?crs=epsg:"+str(epsg_code)
    try:
        default_attributes_odict=attribute_odict(QGisType)
    except ValueError as err:
        print(err.args)
    default_attributes_odict=attribute_odict(QGisType)
    for mp_attribute_name in default_attributes_odict:
        attribute_vals=default_attributes_odict[mp_attribute_name]
        type_string=''
        if attribute_vals[1]==QVariant.Int:
            type_string="integer"
        if attribute_vals[1]==QVariant.String:
            type_string="string"
        layer_attribute_name=str(attribute_vals[2])    
        layer_string=layer_string+"&field="+layer_attribute_name+":"+str(type_string)
    layer_string=layer_string+"&index=yes"
    return layer_string

def parse_object_type(ADD_layer,Polish_header_dict,QGisType,Feature_data_list):
    #This code is reusable for all feature types
    Feature_id=0
    default_layer_attributes_odict=attribute_odict(QGisType)

    for Feature_data in Feature_data_list:
        ADD_layer_provider= ADD_layer.dataProvider()
        Feature_attributes_dict=dict(default_layer_attributes_odict)
        Feature_id=Feature_id+1
        Feature_attributes_dict['Feature_id'] =[Feature_id,Feature_attributes_dict['Feature_id'][1],Feature_attributes_dict['Feature_id'][2]]
        Feature_attributes_dict['Img_id'] =[Polish_header_dict['ID'],Feature_attributes_dict['Feature_id'][1],Feature_attributes_dict['Feature_id'][2]]
        Data_objects=[]
        Data_objects_level_list=[]
        Data_levels_used_set=set()
        #Data_objects_level_dict={}
        Data_objects_dict={}
        obj_no=-1
        for read_line in Feature_data.split('\n'):
            
            if not read_line[:1]==";":
                data_pair=read_line.split('=')
                #DEBUG LINE
                if data_pair[0]=='Type':
                    pass
                    #print data_pair[1]
                    
                try:
                    if Feature_attributes_dict[data_pair[0]] is not None:
                        Feature_attributes_dict[data_pair[0]]=[(data_pair[1]).rstrip(),Feature_attributes_dict[data_pair[0]][1],Feature_attributes_dict[data_pair[0]][2]]
                    else:
                        pass
                except:
                    pass
                    #used to have data level stuff here
                        
                if read_line[:3]=='Nod':
                    NodeNo=int(data_pair[0][3:])
                    NewNodeString=str(NodeNo)+','+data_pair[1]
                    OldNodeString=Feature_attributes_dict['NodIDs'][0]
                    if len(OldNodeString)>1:
                        separator='|'
                    else:
                        separator=''
                    Feature_attributes_dict['NodIDs']=[OldNodeString+separator+NewNodeString,Feature_attributes_dict['NodIDs'][1],Feature_attributes_dict['NodIDs'][2]]
            
                if data_pair[0]=='EndLevel':
                    MP_BIT_LEVEL=Polish_header_dict['Level'+''.join(c for c in str(data_pair[1]) if c in digits)]
                    Feature_attributes_dict[data_pair[0]]=[MP_BIT_LEVEL,Feature_attributes_dict[data_pair[0]][1],Feature_attributes_dict[data_pair[0]][2]]
                
                if read_line[:4]=='Data':
                    obj_no+=1
                    #Add objects to feature
                    #Add data level
                    Data_level=int(data_pair[0][4:])
                    
                    Data_levels_used_set.add(Data_level)
                    Data_objects_level_list.append(Data_level)
                    
                    special_attribute='DataLevel'
                    Feature_attributes_dict[special_attribute]=[Data_level,Feature_attributes_dict[special_attribute][1],Feature_attributes_dict[special_attribute][2]]
                    
                    #Add points to list of points
                    Data_object_point_list=[]
                    DATA_RES_STRING='-*\d+\.*\d*,-*\d+\.*\d*'
                    DATA_REGEX_HAYSTACK=data_pair[1]
                    DATA_REGEX_STRING=re.compile(DATA_RES_STRING)
                    DATA_REGEX_MATCH = DATA_REGEX_STRING.findall(DATA_REGEX_HAYSTACK)
                    Data_object_points=[]
                    for latlonpair in DATA_REGEX_MATCH:
                        latlon=latlonpair.split(',')
                        Data_Point=QgsPoint(float(latlon[1]),float(latlon[0]))
                        Data_object_points.append(Data_Point)
                    Data_objects.append(Data_object_points)
                    Data_objects_dict[obj_no]=[Data_level,Data_object_points]
                    
                    
        #Add feature to layer
        #At this point we have all the attributes of the feature and a dictionary of objects in that feature each object being a list of latlon points
        


        if QGisType==QGis.Polygon:
            for used_level in Data_levels_used_set:
                is_outer_ring=True
                for Data_object in Data_objects_dict:
                    if Data_objects_dict[Data_object][0]==used_level:
                        if is_outer_ring:
                            is_outer_ring=False
                            feat = QgsFeature()
                            polygon_rings=[]
                            polygon_rings.append(Data_objects_dict[Data_object][1])
                        else:
                            polygon_rings.append(Data_objects_dict[Data_object][1])

                feat.setGeometry(QgsGeometry.fromPolygon(Data_objects))
                
                #for index, Data_object in enumerate(Data_objects):
                #    ring_object=[]
                #    for data_point in Data_object:
                attributes_list=[]
                for index, attribute_name in enumerate(default_layer_attributes_odict):
                    if attribute_name=='DataLevel':
                        #print "setting DataLevel to "+str(used_level)
                        attributes_list.append(used_level)
                    else:
                        #print attribute_name
                        attributes_list.append(Feature_attributes_dict[attribute_name][0])
                #print attributes_list
                feat.setAttributes(attributes_list)
                (res, outFeats) = ADD_layer.dataProvider().addFeatures( [ feat ] )
  
                    
        if QGisType==QGis.Point:       
            for index, Data_object in enumerate(Data_objects):
                Feature_attributes_dict['DataLevel'][0]=Data_objects_level_list[index]
                for Data_Point in Data_object:
                    feat = QgsFeature()
                    feat.setGeometry(QgsGeometry.fromPoint(Data_Point))
                    attributes_list=[]
                    for index, attribute_name in enumerate(default_layer_attributes_odict):
                        attributes_list.append(Feature_attributes_dict[attribute_name][0])
                    feat.setAttributes(attributes_list)
                    (res, outFeats) = ADD_layer.dataProvider().addFeatures( [ feat ] )
                    
            
        if QGisType==QGis.Line:
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromMultiPolyline(Data_objects))
            line_objects=[]
            #for index, Data_object in enumerate(Data_objects):
            #    ring_object=[]
            #    for data_point in Data_object:
            attributes_list=[]
            for index, attribute_name in enumerate(default_layer_attributes_odict):
                attributes_list.append(Feature_attributes_dict[attribute_name][0])
            feat.setAttributes(attributes_list)
            (res, outFeats) = ADD_layer.dataProvider().addFeatures( [ feat ] )
    #ADD_layer.updateExtents()
    #QgsMapLayerRegistry.instance().addMapLayer(ADD_layer)
    #qgis.utils.iface.setActiveLayer(ADD_layer)
    #qgis.utils.iface.zoomToActiveLayer()
    
    return True

def internal_reorganise(layers_list):
    diced_layers=[]
    for input_layer in layers_list:
        diced_layers.append(dice(input_layer,input_layer.name(),255))
    output_handles=[]
    for diced_layer in diced_layers:
        output_handles.append(dehole(diced_layer,diced_layer.name()))
        QgsMapLayerRegistry.instance().removeMapLayer(diced_layer.id())
    return output_handles

def export_polish(self,input_layers_list,output_file,import_dict,compiler="cGPSmapper"):
    if compiler=="MapTk":
        print "WARNING: RUNNING 'REORGANISE' FOR MapTk"
        layers_list=internal_reorganise(input_layers_list)
    else:
        layers_list=input_layers_list
    #Build DEFAULT polish header dictionary
    polishexporter_ver=myver
    default_header = default_mp_header()
    #Get template mp file
    template_file_name='template.mp'
    if os.path.exists(template_file_name):
        with open(template_file_name,'r') as f:
            output = f.read()
        headregex = re.compile('\[IMG ID\].+?\[END-IMG ID\]',re.DOTALL)
        result = headregex.match(output)
        template_header=result.group()
        #print template_header
        #read in mp parameters from template file
        #ID_regex = re.compile('ID=[0-9]{8}')
        for header_key in default_header:
            regex_str = re.compile(header_key+'=.+')
            regex_match = regex_str.search(template_header)
            #needs to be findall and capture last instance
            regex_line = regex_match.group()
            default_header[header_key]=(regex_line.split("="))[1]
            try:
                default_header[header_key]=pass_header[header_key]
            except:
                pass
        for header_key in default_header:
            pass
            #print default_header[header_key] 
            
    #Add import_dict to header info
    
    for header_key in default_header:
        for import_key in import_dict:
            if header_key==import_key:
                default_header[header_key]=import_dict[header_key]
    file_header_dict=default_header
    
    #Prepare BIT_LEVEL dictionary
    #BIT_LEVEL_DICT = {}
    #for key in default_header:
    #    if key.startswith("Level"):
    #        if key!="Levels":
    #            #print "Found",key,"=",default_header[key],"Data"+str(key[5:])
    #            BIT_LEVEL_DICT[default_header[key]]=str(key[5:])
    #            rev_BIT_LEVEL_DICT = {v:k for k, v in BIT_LEVEL_DICT.items()}
    polish_temp_file=os.path.join(tempfile.gettempdir(),"polish_temp_file.mp")
    
    with io.open(polish_temp_file, 'w',1,None,None,'\r\n') as polish_file:
        #Write header to file
        #print 'writing '+output_file
#        #polish_file.write(r';')# generated by Mr Purples pyQGIS polish exporter '+str(myver())+u'\n')
        polish_file.write(u'[IMG ID]\n')
        for header_key in default_header:
            polish_string= str(header_key)+"="+str(default_header[header_key]) 
            polish_file.write(unicode(polish_string).rstrip()+'\n')
        polish_file.write(u'[END-IMG ID]\n')
        polish_file.write(u'\n')
        #Loop through layers
        for layer in layers_list:
            layer_dp=layer.dataProvider()
            crsSrc = layer_dp.crs()
            crsDest = QgsCoordinateReferenceSystem(4326)  # WGS84
            xform = QgsCoordinateTransform(crsSrc, crsDest)
            
            #get indices for mp attributes 
            #nb the weird mp_name attribute 
            #which returns the name of the 
            #attribute to use for the name
            
            layer_dataprovider=layer.dataProvider()
            layer_attributes = layer_dataprovider.fields()
            attribute_list = layer_attributes.toList()
            MP_TYPE_idx = layer.fieldNameIndex('MP_TYPE')
            MP_BIT_LVL_idx = layer.fieldNameIndex('MP_BIT_LVL')
            MP_DTA_LVL_idx = layer.fieldNameIndex('MP_DTA_LVL')
            MP_NAME_idx = layer.fieldNameIndex('MP_NAME')
            
            myWkbType=layer.dataProvider().geometryType()
            QGisType=WKBType_to_type(myWkbType)
            mp_attr_name_list=[]
            mp_attr_idx_list=[]
            default_attributes=attribute_odict(QGisType)
            for default_attribute in default_attributes:
                mp_attr_name_list.append(default_attributes[default_attribute][2])
                mp_attr_idx_list.append(layer.fieldNameIndex(default_attributes[default_attribute][2]))
                
                
            #idx will be -1 if no field found and subsiquently filled with a default value
            iter = layer.getFeatures()
            for feature in iter:
                geom=feature.geometry()
                kind_is_point=0
                kind_is_area=0
                kind_is_line=0
                if geom:
                    #help(feature)
                    #help(geom)
                    #print "wkbtype is "+str(geom.wkbType())
                    #print "type is "+str(geom.type())
                    if geom.wkbType()==QGis.WKBMultiPoint:
                        pass
                        #print "Point: " + str(geom.asMultiPoint())
                    if geom.type() == QGis.Point:
                        outputtype='[POI]'
                        #print "POI found"
                    if geom.type() == QGis.Line:
                        outputtype='[POLYLINE]'
                        #print "LINE found"
                    if geom.type() == QGis.Polygon:
                        outputtype='[POLYGON]'
                        #print "AREA found"
                    QGisType=geom.type()
                    default_feature_attributes_odict=attribute_odict(QGisType)
                    feature_attributes_odict = collections.OrderedDict()
                    MP_NAME_SET=False
                   
                    for default_feature_attribute in default_feature_attributes_odict:
                        attribute_name=default_feature_attributes_odict[default_feature_attribute][2]
                        layer_attribute_idx=layer.fieldNameIndex(attribute_name)
                        if layer_attribute_idx>=0:
                            if str(feature.attributes()[layer_attribute_idx])=='NULL':
                                feature_attributes_odict[default_feature_attribute]=None
                                #print "NULL found"
                            else:
                                #print "Not NULL found"
                                #print str(feature.attributes()[layer_attribute_idx])
                                if feature.attributes()[layer_attribute_idx]==default_feature_attributes_odict[default_feature_attribute][0]:
                                    pass
                                feature_attributes_odict[default_feature_attribute] = feature.attributes()[layer_attribute_idx]
                        else:
                            
                            if default_feature_attributes_odict[default_feature_attribute][3]:
                                feature_attributes_odict[default_feature_attribute] = default_feature_attributes_odict[default_feature_attribute][0]
                            else:
                                feature_attributes_odict[default_feature_attribute] = None
                        MP_NAMElayer_attribute_idx=layer.fieldNameIndex("MP_NAME")
                        
                        if MP_NAMElayer_attribute_idx>=0:
                            #raise ValueError('FOUND MP_NAME ATTR')
                            MP_LBL_layer_attribute_idx=layer.fieldNameIndex("MP_LBL")
                            if MP_LBL_layer_attribute_idx<=0:
                                #raise ValueError('HAVE MP_NAME ATTR & NO MP_LBL ATTR')
                                #layer_attribute_idx=layer.fieldNameIndex("MP_NAME")
                                MP_LBL_ATTR=str(feature.attributes()[MP_NAMElayer_attribute_idx])
                                #raise ValueError('MP_LBLs contained in attribute called'+MP_LBL_ATTR)
                                if MP_LBL_ATTR =='NULL':
                                    #raise ValueError('EMPTY MP_NAME ATTR')
                                    MP_LBL_val=None
                                    MP_NAME_SET=True

                                else:
                                    
                                    MP_LBL_ATTR_idx=layer.fieldNameIndex(MP_LBL_ATTR)
                                    if MP_LBL_ATTR_idx>=0:
                                        MP_LBL_val=str(feature.attributes()[MP_LBL_ATTR_idx])
                                        MP_NAME_SET=True
                                        if MP_LBL_val=="NULL":
                                            MP_LBL_val=None
                                        else:
                                            pass
                                            #raise ValueError('FOUND ACTUAL EXTANT MP_NAME ATTR'+MP_LBL_val)
                    if MP_NAME_SET:
                        #print feature_attributes_odict
                        temp_feature_attributes_odict = collections.OrderedDict()
                        for key in feature_attributes_odict:
                            if key == "Label":
                                temp_feature_attributes_odict[key]=MP_LBL_val
                            else:
                                temp_feature_attributes_odict[key]=feature_attributes_odict[key]
                        feature_attributes_odict=temp_feature_attributes_odict
                        temp_feature_attributes_odict=None
                        #print feature_attributes_odict
                        
                    #print feature_attributes_odict[default_feature_attribute]
                    
                    geometry_wkbtype=geom.wkbType()
                    if geometry_wkbtype == QGis.WKBPoint:
                        #outputtype='[POI]'
                        datalinegeom=[]
                        datalinegeom.append(geom.asPoint())
                        datalinesgeom=[]
                        datalinesgeom.append(datalinegeom)
                        writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,datalinesgeom,compiler)
                    if geometry_wkbtype == QGis.WKBMultiPoint:
                        #outputtype='[POI]'
                        for geomprime in geom.asMultiPoint():
                            datalinegeom=[]
                            datalinegeom.append(geomprime)
                            datalinesgeom=[]
                            datalinesgeom.append(datalinegeom)
                            #print "found my code"
                            writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,datalinesgeom,compiler)
                    if geometry_wkbtype == QGis.WKBLineString:
                        #outputtype='[POLYLINE]'
                        datalinesgeom=[]
                        datalinesgeom.append(geom.asPolyline())
                        writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,datalinesgeom,compiler)
                    if geometry_wkbtype == QGis.WKBMultiLineString:
                        #outputtype='[POLYLINE]'
                        writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,geom.asMultiPolyline(),compiler)
                    if geometry_wkbtype == QGis.WKBPolygon:
                        #outputtype='[POLYGON]'
                        writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,geom.asPolygon(),compiler)
                    if geometry_wkbtype == QGis.WKBMultiPolygon:
                        #outputtype='[POLYGON]'
                        for datalinesgeom in geom.asMultiPolygon():
                            writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,datalinesgeom,compiler)
                else:
                    print "WARNING: No geometry found for feature id: "+str(feature.id())
    shutil.copy2(polish_temp_file, output_file)
    os.remove(polish_temp_file)
    print "wrote "+output_file

class Polish:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()
        if verbose(): print "WARNING: Polish class running in verbose mode"

    def initGui(self):
        # Create action that will start plugin
        self.action = QAction(QIcon(":/plugins/"), "&Polish", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("activated()"), self.Polish)

        # Add toolbar button and menu item
        self.iface.addPluginToMenu("Polish", self.action)


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("Polish",self.action)

    def testfun(self):
        print "local file function test"
        
    def list_polish_attributes(self,QGisType):
        return attribute_odict(QGisType)
        
    def build_memory_layer_string(self,QGisWKBType,epsg_code):
        return build_create_layer_string(QGisWKBType,epsg_code)
        
    def export_layers_as_polish(self,layers_list,output_file,import_dict={},compiler="cGPSmapper"):
        export_polish(self,layers_list,output_file,import_dict,compiler)
        
    def WKBtype_to_GeomType(self,QGisWKBType):
        return WKBType_to_type(QGisWKBType)
                        
    def export_files_as_polish(self,files_list,output_file,import_dict={},compiler="cGPSmapper"):
        layers_list=[]
        for file in files_list:
            if os.path.exists(file):
                layer=QgsVectorLayer(file,file, "ogr")
                if layer.isValid():
                    #iter = layer.getFeatures()
                    feature_count=layer.featureCount ()
                    #for feature in iter:
                    #    feature_count+=1
                    if feature_count>0:
                        if verbose(): print "Exporting "+file#+str(import_dict)
                        layers_list.append(layer)
                else:
                    if verbose(): print file+" not valid"
            else:
                if verbose(): print "Could not find "+file
        
        export_polish(self,layers_list,output_file,import_dict,compiler)
        
    def export_layers_as_polish(self,layers_list,output_file,import_dict={},compiler="cGPSmapper"):
        
        use_layers_list=[]
        for layer in layers_list:
            if layer.isValid():
                #iter = layer.getFeatures()
                feature_count=layer.featureCount ()
                #for feature in iter:
                #    feature_count+=1
                if feature_count>0:
                    if verbose(): print "Exporting "+layer.name()+" layer to "+output_file
                    use_layers_list.append(layer)
            else:
                if verbose(): print "layer not valid"

            
        export_polish(self,layers_list,output_file,import_dict,compiler)
    
    def get_polish_file_header(self,Polish_file):
        if os.path.exists(Polish_file):
            with open(Polish_file,'r') as f:
                read_data = f.read()
            headregex = re.compile('\[IMG ID\].+?\[END-IMG ID\]', re.MULTILINE|re.DOTALL)
            result = headregex.search(read_data)
            Polish_header_data=result.group()
            #print Polish_header_data
            Polish_header_dict={}
            default_header=default_mp_header()
            for header_key in default_header:
                regex_needle=header_key+'\s*=.*'
                regex_comp = re.compile(regex_needle)
                regex_match = regex_comp.search(Polish_header_data)
                try:
                    regex_line = regex_match.group(0)
                    Polish_header_dict[header_key]=(regex_line.split("="))[1]
                except:
                    print "Did not find "+str(header_key)+" using default value '"+str(default_header[header_key])+"'"
                    Polish_header_dict[header_key]=default_header[header_key]
            return Polish_header_dict
        else:
            raise ValueError('File not found ',Polish_file)
                        
    def import_polish_files(self,Polish_file_list):
        epsg_code=4326
        
        #Create POL layer
        layer_string=build_create_layer_string(QGis.WKBPoint,epsg_code)
        POI_layer= QgsVectorLayer(layer_string, "POI_layer", "memory")
        POI_provider = POI_layer.dataProvider()
        QgsMapLayerRegistry.instance().addMapLayer(POI_layer)

        #Create Polygon layer
        layer_string=build_create_layer_string(QGis.WKBPolygon,epsg_code)
        #print layer_string
        Polygon_layer= QgsVectorLayer(layer_string, "Polygon_layer", "memory")
        Polygon_provider = Polygon_layer.dataProvider()
        QgsMapLayerRegistry.instance().addMapLayer(Polygon_layer)

        #Create Polyline layer
        layer_string=build_create_layer_string(QGis.WKBMultiLineString,epsg_code)
        Line_layer= QgsVectorLayer(layer_string, "Line_layer", "memory")
        Line_provider = Line_layer.dataProvider()
        QgsMapLayerRegistry.instance().addMapLayer(Line_layer)
        
        layer_handles={}
        layer_handles['point']=POI_layer
        layer_handles['line']=Line_layer
        layer_handles['polygon']=Polygon_layer
        
        for Polish_file in Polish_file_list:
            if os.path.exists(Polish_file):
                with open(Polish_file,'r') as f:
                    read_data = f.read()
                    
                #Generate new spatialite table
                #try:
                #    os.remove(tempfile.gettempdir(),'newfile.sqlite')
                #except:
                #    pass
                #spatialitedb=os.path.join(tempfile.gettempdir(),'newfile.sqlite')
                #conn = db.connect(spatialitedb)
                #cur = conn.cursor()
                #cur.execute('DROP TABLE IF EXISTS header_info')
                #cur.execute('CREATE TABLE header_info (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, img_ID INTEGER, Key TEXT, key_val TEXT)')
                #cur.execute('DROP TABLE IF EXISTS POI')
                #cur.execute('CREATE TABLE POI (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, img_ID INTEGER, MP_TYPE TEXT NOT NULL, Marine TEXT DEFAULT "N", City TEXT DEFAULT "N", Label TEXT, EndLevel INTEGER DEFAULT 0, DataNo INTEGER DEFAULT 0, StreetDesc TEXT, HouseNumber INTEGER, OvernightParking TEXT DEFAULT "N", Highway TEXT, CityName TEXT, RegionName TEXT, CountryName TEXT, Zip TEXT, Exit TEXT)')
                #cur.execute("SELECT AddGeometryColumn('POI', 'location',  4326, 'POINT', 'XY')")
                #Get header data
                headregex = re.compile('\[IMG ID\].+?\[END-IMG ID\]', re.MULTILINE|re.DOTALL)
                result = headregex.search(read_data)
                Polish_header_data=result.group()
                #print Polish_header_data
                Polish_header_dict={}
                #polish_object_instance = utils.plugins['Polish']
                #default_header=polish_object_instance.get_default_mp_header()
                default_header=default_mp_header()
                for header_key in default_header:
                    regex_needle=header_key+'\s*=.*'
                    #print 'looking for '+header_key
                    regex_comp = re.compile(regex_needle)
                    regex_match = regex_comp.search(Polish_header_data)
                    try:
                        regex_line = regex_match.group(0)
                        #print 'found '+regex_line
                        header_value=((regex_line.split("="))[1])
                        #print header_value
                        Polish_header_dict[header_key]=header_value.rstrip()
                    except:
                        print "Did not find "+str(header_key)+" using default value '"+str(default_header[header_key])+"'"
                        Polish_header_dict[header_key]=default_header[header_key]
                        
                for header_key in Polish_header_dict:
                    #print str(header_key)+' = '+str(Polish_header_dict[header_key] )
                    #cur.execute("INSERT INTO header_info VALUES (NULL,"+Polish_header_dict['ID']+",'"+str(header_key)+"','"+str(Polish_header_dict[header_key] )+"'"+")")
                    pass
                #Read POIs from current file
                POIregex = re.compile('\[POI\].+?\[END\]', re.MULTILINE|re.DOTALL)
                Feature_data_list = POIregex.findall(read_data)
                for dataset in Feature_data_list:
                    pass
                    #print dataset
                parse_object_type(POI_layer,Polish_header_dict ,QGis.Point,Feature_data_list)
                
                #Read Polygons from current file
                Polygonregex = re.compile('\[POLYGON\].+?\[END\]', re.MULTILINE|re.DOTALL)
                Feature_data_list = Polygonregex.findall(read_data)
                for dataset in Feature_data_list:
                    pass
                    #print dataset
                parse_object_type(Polygon_layer, Polish_header_dict, QGis.Polygon,Feature_data_list)
                
                #Read Lines from current file
                Lineregex = re.compile('\[POLYLINE\].+?\[END\]', re.MULTILINE|re.DOTALL)
                Feature_data_list = Lineregex.findall(read_data)
                for dataset in Feature_data_list:
                    pass
                    #print dataset
                #MP_BIT_LEVEL=Polish_header_dict['Level2']
                #print MP_BIT_LEVEL
                parse_object_type(Line_layer, Polish_header_dict, QGis.Line,Feature_data_list)
                
        QgsMapLayerRegistry.instance().addMapLayer(Polygon_layer)
        QgsMapLayerRegistry.instance().addMapLayer(POI_layer)
        QgsMapLayerRegistry.instance().addMapLayer(Line_layer)
        self.iface.mapCanvas().refresh()
        return layer_handles

    def reorganise(self,input_layers_list):
        layers_list=internal_reorganise(input_layers_list)
        return layers_list
        
    def compile_preview_by_cgpsmapper(self,img_files_list,import_pv_dict,):
        cgpsmapper_path=get_cGPSmapper_path()
        #cgpsmapper_file_path=os.path.join(cgpsmapper_path,"cgpsmapper.exe")
        #cpreview_file_path=os.path.join(cgpsmapper_path,"cpreview.exe")
        cgpsmapper_file_path=cgpsmapper_path+"\\"+"cgpsmapper.exe"
        cpreview_file_path=cgpsmapper_path+"\\"+"cpreview.exe"
        if isLinux():
            if verbose(): print "Running in linux checking for WINE"
            if verbose(): print "Wine path is "+str(get_WINEpath())
            #status = call(r"wine '"+cgpsmapper_file_path+"'",shell=True)
            
        preview_default_dictionary=default_pv_header()
        preview_default_dictionary_dictionary=preview_default_dictionary['preview_default_dictionary_dictionary']

        #print "Updating preview_default_dictionary"
        for pv_key in preview_default_dictionary:
            try:
                #print "attempting to change "+pv_key+" to "+import_pv_dict[pv_key]
                preview_default_dictionary[pv_key]=import_pv_dict[pv_key]
                
            except:
                pass
        
        files_list=[]
        temp_list=[]
        
        #get output path from output filename
        new_temp_output_path=os.path.join(tempfile.gettempdir(),basename(import_pv_dict['FileName']))
        output_dir=os.path.dirname(import_pv_dict['FileName'])
        preview_default_dictionary['FileName']=new_temp_output_path
        
        for img_file in img_files_list:
            if os.path.exists(img_file):
                files_list.append(img_file)
            else:
               if verbose(): print "WARNING: Could not find "+img_file
               
        for fname in files_list:
            img_file_name=basename(fname)
            img_path=os.path.dirname(fname)
            oldfile=fname
            newfile=os.path.join(tempfile.gettempdir(),basename(fname))
            shutil.copy(oldfile,newfile)
            temp_list.append(newfile)
            
        #write pv file into temp directory
        PV_FILE_FULL_PATH=os.path.join(tempfile.gettempdir(),'PV_FILE.txt')
        with io.open(PV_FILE_FULL_PATH, 'w',1,None,None,'\r\n') as pv_file:
            pv_file.write(u''+';Temporary preview file created by the QGIS polish class library'+'\n')
            pv_file.write(u''+'[Map]'+'\n')
            for key in preview_default_dictionary:
                pv_file.write(u''+str(key)+'='+str(preview_default_dictionary[key])+'\n')
            pv_file.write(u''+'[DICTIONARY]'+'\n')
            for key in preview_default_dictionary_dictionary:
                pv_file.write(u''+str(key)+'='+str(preview_default_dictionary_dictionary[key])+'\n')
            pv_file.write(u''+'[END-DICTIONARY]'+'\n')
            pv_file.write(u''+'[End-Map]'+'\n')
            pv_file.write(u''+''+'\n')
            pv_file.write(u''+'[Files]'+'\n')
            for temp_file in temp_list:
                pv_file.write(u''+'img='+temp_file+'\n')
            pv_file.write(u''+'[END-Files]'+'\n')

        full_command=cpreview_file_path+" "+PV_FILE_FULL_PATH
        if verbose(): print full_command        
        if isLinux():
            WINE_PV_FILE_FULL_PATH="Z:"+PV_FILE_FULL_PATH
            WINE_PV_FILE_FULL_PATH=WINE_PV_FILE_FULL_PATH.replace("/","\\")
            WINE_cpreview_file_path=cpreview_file_path
            #WINE_cpreview_file_path=WINE_cpreview_file_path.replace("/","\\")
            full_command=r"wine '"+WINE_cpreview_file_path+"' '"+WINE_PV_FILE_FULL_PATH+"'"
            if verbose(): print full_command
            status = call(full_command, shell=True)
        if isWindows():
            bin_path=cpreview_file_path
            arg_string=""#NB cant seem to add arg yet??
            streaming=True
            shell_command=[bin_path, PV_FILE_FULL_PATH]
            print "Running: "+" ".join(shell_command)
            p = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE, bufsize=1)
            if streaming:
                with p.stdout:
                    for line in iter(p.stdout.readline, b''):
                        print line,
                p.wait() 
            else:
                out, err = p.communicate()
                print out
        
        suffix_list=[]
        suffix_list.append('.MDX')
        suffix_list.append('.mp')
        suffix_list.append('.reg')
        suffix_list.append('.TDB')
        for suffix in suffix_list:
            #Determine if file exists
            src = preview_default_dictionary['FileName']+suffix
            dst = os.path.join(output_dir,basename(preview_default_dictionary['FileName']))+suffix
            if os.path.isfile(src):
                shutil.copy(src,dst)
                os.remove(src)
            else:
                print "WARNING: "+src+" NOT FOUND: NOT INCLUDING IN MAPSET"
        for temp_file in temp_list:
            os.remove(temp_file)
            pass
        os.remove(PV_FILE_FULL_PATH)
        preview_file_path = os.path.join(output_dir,basename(preview_default_dictionary['FileName'])+'.mp')
        full_command=cgpsmapper_path+"\\"+"cgpsmapper.exe"+" "+preview_file_path
        
        if isLinux():
            WINE_cgpsmapper_path=cgpsmapper_path
            WINE_cgpsmapper_file_path=cgpsmapper_path+"\\"+"cgpsmapper.exe"
            #WINE_cgpsmapper_path=WINE_cgpsmapper_path.replace("/","\\")
            WINE_preview_file_path="Z:"+preview_file_path
            WINE_preview_file_path=WINE_preview_file_path.replace("/","\\")
            full_command=r"wine '"+WINE_cgpsmapper_file_path+"' '"+WINE_preview_file_path+"'"
            if verbose(): print full_command
            status = call(full_command, shell=True)
        if isWindows():
            bin_path=cgpsmapper_file_path
            arg_string=""#NB cant seem to add arg yet??
            streaming=True
            shell_command=[bin_path, preview_file_path]
            print "Running: "+" ".join(shell_command)
            p = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE, bufsize=1)
            if streaming:
                with p.stdout:
                    for line in iter(p.stdout.readline, b''):
                        print line,
                p.wait() 
            else:
                out, err = p.communicate()
                print out
            
            
    def get_default_mp_header(self):
        default_header = default_mp_header()
        return default_header
     
    def print_default_mp_header(self):
        default_header = default_mp_header()
        for header_key in default_header:
            print str(header_key)+' = '+str(default_header[header_key])
            
    def print_default_pv_file(self):
        default_header = default_pv_header()
        for header_key in default_header:
            print str(header_key)+' = '+str(default_header[header_key]  )
            
    def parallel_compile_by_cgpsmapper(self,mp_files_list,cgpsmapper_path,output_folder):
        if len(mp_files_list)>0:
            #NB needs to correctly reparse cgpsmapper path
            mp_file_list=[]
            for raw_mp_file in mp_files_list:
                output="Z:"+raw_mp_file
                output= string.replace(output, '/', '\\\\')
                mp_file_list.append(output)
            subprocess_args=[]
            i=0
            for mp_file_path in mp_file_list:
                i+=1
                command_script=os.path.join(tempfile.gettempdir(),"command_script_"+str(i)+".sh")
                try:
                    os.remove("/tmp/command_script_"+str(i)+".sh")
                except:
                    pass
                f1 = open(command_script,'w')
                f1.write("#!/bin/bash\n")
                f1.write("clickcgpsmapper.sh &\n")
                f1.write(r'wine "c:\\Program Files (x86)\\cGPSmapper\\cgpsmapper.exe" ac "'+mp_file_path+'"'+"\n")
                f1.close()
                st = os.stat(command_script)
                os.chmod(command_script, st.st_mode | stat.S_IEXEC)

            parallel_script=os.path.join(tempfile.gettempdir(),"gnu_parallel_script.sh")
            try:
                os.remove(parallel_script)
            except:
                pass
            f2 = open(parallel_script,'w')
            f2.write("#!/bin/bash\n")
            f2.write("cd "+output_folder+"\n")
            f2.write("clickcgpsmapper.sh &\n")
            f2.write("parallel "+os.path.join(tempfile.gettempdir(),"command_script_{1}.sh")+" ::: {1.."+str(i)+"}")
            f2.close()
            st = os.stat(parallel_script)
            os.chmod(parallel_script, st.st_mode | stat.S_IEXEC)
            p = Popen(parallel_script, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate(b"input data that is passed to subprocess' stdin")
            rc = p.returncode
            print output
            #os.remove(parallel_script)
            for n in range(i):
                pass
                #os.remove("/tmp/command_script_"+str(i)+".sh")

    def compile_by_cgpsmapper(self,mp_files_list,cgpsmapper_path,import_pv_dict={},compiler="cGPSmapper"):
        if isLinux():
            if compiler=="MapTk":
                print "MapTk compilation not available in Linux yet - attempting to compile with cGPSmapper at "+cgpsmapper_path
            if verbose(): print "Running in linux requires  WINE"
            if verbose(): print "Running in linux requires  cpsmapper path as WINE dos path"
            if verbose(): print "Wine located at "+str(get_WINEpath())
        if isWindows():
            print "Running in windows"
        username=getpass.getuser()
        #cgpsmapper_path=get_cGPSmapper_path()
        cgpsmapper_file_path=cgpsmapper_path+"\\"+"cgpsmapper.exe"
        cpreview_file_path=cgpsmapper_path+"\\"+"cpreview.exe"
        os_temp=tempfile.gettempdir()
        wine_temp_win="C:\\users\\"+username+ "\\Temp\\" 
        wine_temp_unix=r"/home/"+username+r"/.wine/drive_c/users/"+username+r"/Temp"
        
        files_list=[]
        for fname in mp_files_list:
            if os.path.exists(fname):
                files_list.append(fname)
                print "compiling "+ fname
                with open(fname) as f:
                    content = f.read().splitlines()
                for file_line in content:
                    RES_STRING='ID=[0-9]{8}'
                    REGEX_HAYSTACK=file_line
                    REGEX_STRING=re.compile(RES_STRING)
                    REGEX_MATCH = REGEX_STRING.match(REGEX_HAYSTACK)
                    if REGEX_MATCH:
                        match_string = REGEX_MATCH.group()
                        break
                    else:
                        pass                  
                img_ID=(match_string.split("="))[1]
                if verbose(): print img_ID
                id_file=str(img_ID)+".mp"
          
                os_id_file_path=os.path.join(tempfile.gettempdir(),id_file)
            
                Linux_full_command=""
                wine_temp_unix_bak=""
                if isLinux():
                    #shift wine temp path to os temp path
                    wine_temp_unix_bak = "/home/"+username+"/.wine/drive_c/users/"+username+"/TempBak"
                    try:
                        status = call("rm -rf " + wine_temp_unix_bak, shell=True)
                    except:
                        pass
                    status = call(r"mv " + wine_temp_unix + r" " + wine_temp_unix_bak, shell=True)
                    status = call("ln -s /tmp "+wine_temp_unix, shell=True)
                    
                    #Write Linux wine compile command
                    wine_id_file_path=r"C:/users/"+username+r"/Temp/"+id_file
                    Linux_full_command=r"wine '"+cgpsmapper_file_path+"' '"+wine_id_file_path+"'"
                    if verbose(): print Linux_full_command

                shutil.copy(fname,os_id_file_path)
            
                
                #Run cGPSmapper compile commands
                if isLinux:
                    status = call(Linux_full_command, shell=True)
                    status = call("rm -rf " + wine_temp_unix, shell=True)
                    status = call(r"mv " + wine_temp_unix_bak + r" " + wine_temp_unix, shell=True)
                
                if isWindows():
                    streaming=True
                    bin_path=cgpsmapper_path
                    polish_path=os_id_file_path
                    shell_command=[bin_path, polish_path]
                    print "Running: "+" ".join(shell_command)
                    p = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE, bufsize=1)
                    if streaming:
                        with p.stdout:
                            for line in iter(p.stdout.readline, b''):
                                print line,
                        p.wait() 
                    else:
                        out, err = p.communicate()
                        print out
                    
                #Copy compiled files to oiginal mp file path
                try:
                    shutil.copy(os.path.join(tempfile.gettempdir(),str(img_ID)+".img"),os.path.join(os.path.split(fname)[0],str(img_ID)+".img"))
                    os.remove(os.path.join(tempfile.gettempdir(),str(img_ID)+".img"))
                    pass
                except:
                    print "unable to complete compliation for "+ str(img_ID)+".img"
                
                try:
                    shutil.copy(os.path.join(tempfile.gettempdir(),str(img_ID)+".img.idx"),os.path.join(os.path.split(fname)[0],str(img_ID)+".img.idx"))
                    os.remove(os.path.join(tempfile.gettempdir(),str(img_ID)+".img.idx"))
                    pass
                except:
                    print "No idx file generated"
                
                try:
                    os.remove(os.path.join(tempfile.gettempdir(),str(img_ID)+".mp"))
                    pass
                except:
                    pass
            else:
                print "WARNING: Could not find "+fname
    # run
    def Polish(self):
        QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('Polish', "Polish"), QCoreApplication.translate('Polish', "Polish"))
        return


if __name__ == "__main__":
    pass
