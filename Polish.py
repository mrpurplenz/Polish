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


def attribute_odict(QGisType):
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
        default_attributes_odict['Background'] = ['N',QVariant.String,'MP_MARINE',False]
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
        default_attributes_odict['NodIDs']=['',QVariant.String,'MP_NODES',False]#eg '1,0,1002,0|2,1,1003,0'
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

        
def verbose():
    return True

def myver():
    return "0.0.1"
    
def get_cGPSmapper_path():
    return r'C:\Program Files (x86)\cGPSmapper'


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
        
def bit_level(file_header_dict,bit_val):
    #returns the level# associated with a given bit level value
    BIT_LEVEL_DICT = {}
    for key in file_header_dict:
        if key.startswith("Level"):
            if key!="Levels":
                BIT_LEVEL_DICT[file_header_dict[key]]=str(key[5:])
    rev_BIT_LEVEL_DICT = {v:k for k, v in BIT_LEVEL_DICT.items()}
    return BIT_LEVEL_DICT[int(bit_val)]
    
def rev_bit_level(file_header_dict,level_val):
    #returns the bit level associated with a given level#
    BIT_LEVEL_DICT = {}
    for key in file_header_dict:
        if key.startswith("Level"):
            if key!="Levels":
                BIT_LEVEL_DICT[file_header_dict[key]]=str(key[5:])
    rev_BIT_LEVEL_DICT = {v:k for k, v in BIT_LEVEL_DICT.items()}
    return rev_BIT_LEVEL_DICT[level_val]
    
def geomWrite(polish_file,pntsgeom,xform,DATA_LVL):
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
        Datastring=Datastring+str(newQgsPoint.y())+','+str(newQgsPoint.x())+')'
        if False: #This code is intended to split lines into 255 length lines for MKmap
            pointcount=pointcount+1
            if False:
            #if pointcount==255:
                pointcount=0
                firstpoint=0
                polish_file.write(u''+Datastring+'\n')
                Datastring='('+str(newQgsPoint.y())+','+str(newQgsPoint.x())+')'
                ok_to_write_data=False
    if ok_to_write_data:
        polish_file.write(u''+Datastring+'\n')

#def writepolishobject(polish_file,outputtype,MP_TYPE_val,MP_NAME_val,END_LVL_val,DATA_LVL,xform,datalinesgeom):
def writepolishobject(polish_file,outputtype,Feature_attributes_odict,file_header_dict,xform,datalinesgeom):
    
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
            
        if attr_val==attribute_odict(QGisType)[attr_name][0]:
            attr_val=None
            
        if attr_val is not None:
            polish_file.write(str(Feature_attribute)+u'='+str(Feature_attributes_odict[attr_name])+'\n')
    

    #polish_file.write(u'Type='+str(MP_TYPE_val)+'\n')                    
    #if MP_NAME_val!='':
    #    polish_file.write(u'Label='+str(MP_NAME_val)+'\n')
    #polish_file.write(u'EndLevel='+str(END_LVL_val)+'\n')
    for datalinegeom in datalinesgeom:
        geomWrite(polish_file,datalinegeom,xform,DATA_LVL)
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
    QGisType=WKBType_to_type(QGisWKBType)
    type_string=QGisWktType_to_text(QGisWKBType)
    layer_string=type_string+"?crs=epsg:"+str(epsg_code)
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
    #This code is reusable fo all feature types
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
        for read_line in Feature_data.split('\n'):
            
            if not read_line[:1]==";":
                data_pair=read_line.split('=')
                #DEBUG LINE
                if data_pair[0]=='Type':
                    pass
                    #print data_pair[1]
                try:
                    if Feature_attributes_dict[data_pair[0]] is not None:
                        Feature_attributes_dict[data_pair[0]]=[data_pair[1],Feature_attributes_dict[data_pair[0]][1],Feature_attributes_dict[data_pair[0]][2]]
                    else:
                        pass
                except:    
                    if read_line[:4]=='Data':
                        
                        #Add objects to feature
                        #Add data level
                        Data_level=data_pair[0][5:]
                        Data_objects_level_list.append(Data_level)
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
                    if read_line[:3]=='Nod':
                        NodeNo=int(data_pair[0][3:])
                        NewNodeString=str(NodeNo)+','+data_pair[1]
                        OldNodeString=Feature_attributes_dict['NodIDs'][0]
                        if len(OldNodeString)>1:
                            separator='|'
                        else:
                            separator=''
                        Feature_attributes_dict['NodIDs']=[OldNodeString+separator+NewNodeString,Feature_attributes_dict['NodIDs'][1],Feature_attributes_dict['NodIDs'][2]]

        #Add feature to layer
        #At this point we have all the attributes of the feature and a list of objects in htat feature each object being a list of latlon points
        
        if QGisType==QGis.Polygon:
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromPolygon(Data_objects))
                ring_objects=[]
                #for index, Data_object in enumerate(Data_objects):
                #    ring_object=[]
                #    for data_point in Data_object:
                attributes_list=[]
                for index, attribute_name in enumerate(default_layer_attributes_odict):
                    attributes_list.append(Feature_attributes_dict[attribute_name][0])
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



def export_polish(self,layers_list,output_file,import_dict):

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
            print default_header[header_key] 
            
    #Add import_dict to header info
    
    for header_key in default_header:
        try:
            default_header[header_key]=import_dict[header_key]
        except:
            pass
    
    file_header_dict=default_header
    
    #Prepare BIT_LEVEL dictionary
    #BIT_LEVEL_DICT = {}
    #for key in default_header:
    #    if key.startswith("Level"):
    #        if key!="Levels":
    #            #print "Found",key,"=",default_header[key],"Data"+str(key[5:])
    #            BIT_LEVEL_DICT[default_header[key]]=str(key[5:])
    #            rev_BIT_LEVEL_DICT = {v:k for k, v in BIT_LEVEL_DICT.items()}

    with io.open(output_file, 'w',1,None,None,'\r\n') as polish_file:
        #Write header to file
        print 'writing to file'
#        #polish_file.write(r';')# generated by Mr Purples pyQGIS polish exporter '+str(myver())+u'\n')
        polish_file.write(u'[IMG ID]\n')
        for header_key in default_header:
            polish_string= str(header_key)+"="+str(default_header[header_key]) 
            polish_file.write(unicode(polish_string)+'\n')
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
                #print feature_attributes_odict[default_feature_attribute]
                #get mp attribs or set to default
                #attrs = feature.attributes()
                #if MP_TYPE_idx >=0:
                #    MP_TYPE_val=(attrs[MP_TYPE_idx])
                #    #print MP_TYPE_val
                #else:
                #    MP_TYPE_val="0x00"
                    
                #if MP_BIT_LVL_idx >=0:
                #    MP_BIT_LVL_val=(attrs[MP_BIT_LVL_idx])
                #else:
                #    MP_BIT_LVL_val=24
                #try:
                #    END_LVL_val=BIT_LEVEL_DICT[MP_BIT_LVL_val]
                #except:
                #    print "No value found for MP_BIT_LVL attribute id reported as "+str(MP_BIT_LVL_idx)+". MP_TYPE for this feature was reported to be "+str(MP_TYPE_val)
                #    print "attributes are:"
                #    i=0
                #    for attribute in attribute_list:
                #        print "id "+str(i)+" is "+str(attribute.name())+" and has a value of "+str(attrs[i])
                #        i=i+1
                #    END_LVL_val=1
                #    print "level set to "+str(END_LVL_val)
                    
                #MP_DTA_LVL_val=0
                #try:
                #    if MP_DTA_LVL_idx >=0:
                #        MP_DTA_LVL_val=(attrs[MP_DTA_LVL_idx])
                #    else:
                #        MP_DTA_LVL_val=0
                #except:
                #    pass
                #DATA_LVL=BIT_LEVEL_DICT[MP_DTA_LVL_val]
                #DATA_LVL=MP_DTA_LVL_val
    
                #MP_NAME_field_name=''
                #if MP_NAME_idx>=0:
                #    MP_NAME_field_name=(attrs[MP_NAME_idx])
                #    LOCAL_NAME_idx = layer.fieldNameIndex(str(MP_NAME_field_name))
                #    MP_NAME_val=''
                #    if LOCAL_NAME_idx>=0:
                #        MP_NAME_val=(attrs[LOCAL_NAME_idx])
                #    else:
                #        MP_NAME_val=''
                #else:
                #    MP_NAME_val=''

                #try:
                #    if MP_NAME_val.isNull():
                #        MP_NAME_val=''
                #except:
                #    pass
                
                #print "MP_TYPE is "+str(MP_TYPE_val)
                #print "MP_BIT_LVL is "+str(MP_BIT_LVL_val) 
                #print "NAME is "+str(NAME_val)
                geometry_wkbtype=geom.wkbType()
                if geometry_wkbtype == QGis.WKBPoint:
                    #outputtype='[POI]'
                    datalinegeom=[]
                    datalinegeom.append(geom.asPoint())
                    datalinesgeom=[]
                    datalinesgeom.append(datalinegeom)
                    writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,datalinesgeom)
                if geometry_wkbtype == QGis.WKBMultiPoint:
                    #outputtype='[POI]'
                    for geomprime in geom.asPoint():
                        datalinegeom=[]
                        datalinegeom.append(geomprime)
                        datalinesgeom=[]
                        datalinesgeom.append(datalinegeom)
                        writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,datalinesgeom)
                if geometry_wkbtype == QGis.WKBLineString:
                    #outputtype='[POLYLINE]'
                    datalinesgeom=[]
                    datalinesgeom.append(geom.asPolyline())
                    writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,datalinesgeom)
                if geometry_wkbtype == QGis.WKBMultiLineString:
                    #outputtype='[POLYLINE]'
                    writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,geom.asMultiPolyline())
                if geometry_wkbtype == QGis.WKBPolygon:
                    #outputtype='[POLYGON]'
                    writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,geom.asPolygon())
                if geometry_wkbtype == QGis.WKBMultiPolygon:
                    #outputtype='[POLYGON]'
                    for datalinesgeom in geom.asMultiPolygon():
                        writepolishobject(polish_file,outputtype,feature_attributes_odict,file_header_dict,xform,datalinesgeom)
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
        
    def export_layers_as_polish(self,layers_list,output_file,import_dict={}):
        export_polish(self,layers_list,output_file,import_dict)
        
    def WKBtype_to_GeomType(self,QGisWKBType):
        return WKBType_to_type(QGisWKBType)
                        
    def export_files_as_polish(self,files_list,output_file,import_dict={}):
        layers_list=[]
        for file in files_list:
            if os.path.exists(file):
                layer=QgsVectorLayer(file,file, "ogr")
                if layer.isValid():
                    iter = layer.getFeatures()
                    feature_count=0
                    for feature in iter:
                        feature_count+=1
                    if feature_count>0:
                        if verbose(): print "Exporting "+file
                        layers_list.append(layer)
                else:
                    if verbose(): print file+" not valid"
            else:
                if verbose(): print "Could not find "+file
        export_polish(self,layers_list,output_file,import_dict)
        
    def import_polish_files(self,Polish_file_list):
        epsg_code=4326
        
        #Create POL layer
        layer_string=build_create_layer_string(QGis.WKBPoint,epsg_code)
        POI_layer= QgsVectorLayer(layer_string, "POI_layer", "memory")
        POI_provider = POI_layer.dataProvider()
        QgsMapLayerRegistry.instance().addMapLayer(POI_layer)

        #Create Polygon layer
        layer_string=build_create_layer_string(QGis.WKBPolygon,epsg_code)
        Polygon_layer= QgsVectorLayer(layer_string, "Polygon_layer", "memory")
        Polygon_provider = Polygon_layer.dataProvider()
        QgsMapLayerRegistry.instance().addMapLayer(Polygon_layer)

        #Create Polyline layer
        layer_string=build_create_layer_string(QGis.WKBMultiLineString,epsg_code)
        Line_layer= QgsVectorLayer(layer_string, "Line_layer", "memory")
        Line_provider = Line_layer.dataProvider()
        QgsMapLayerRegistry.instance().addMapLayer(Line_layer)
        
        layer_handles=[]
        layer_handles.append(POI_layer)
        layer_handles.append(Polygon_layer)
        layer_handles.append(Line_layer)
        
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
                        Polish_header_dict[header_key]=(regex_line.split("="))[1]
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
                parse_object_type(Line_layer, Polish_header_dict, QGis.Line,Feature_data_list)
                
        QgsMapLayerRegistry.instance().addMapLayer(Polygon_layer)
        QgsMapLayerRegistry.instance().addMapLayer(POI_layer)
        QgsMapLayerRegistry.instance().addMapLayer(Line_layer)
        self.iface.mapCanvas().refresh()
        return layer_handles

    def compile_preview_by_cgpsmapper(self,img_files_list,import_pv_dict):
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
               if verbose(): print "Could not find "+img_file
               
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
        else:
            if verbose(): print full_command
        status = call(full_command, shell=True)
        suffix_list=[]
        suffix_list.append('.MDX')
        suffix_list.append('.mp')
        suffix_list.append('.reg')
        suffix_list.append('.TDB')
        for suffix in suffix_list:
            shutil.copy(preview_default_dictionary['FileName']+suffix,os.path.join(output_dir,basename(preview_default_dictionary['FileName']))+suffix)
            os.remove(preview_default_dictionary['FileName']+suffix)
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
        
    def compile_by_cgpsmapper(self,mp_files_list,cgpsmapper_path,import_pv_dict={}):
        if isLinux():
            if verbose(): print "Running in linux checking for WINE"
            if verbose(): print "Wine path is "+str(get_WINEpath())
        username=getpass.getuser()    
        cgpsmapper_path=get_cGPSmapper_path()
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
                    else:
                        pass                  
                img_ID=(match_string.split("="))[1]
                if verbose(): print img_ID
                id_file=str(img_ID)+".mp"
          
                os_id_file_path=os.path.join(tempfile.gettempdir(),id_file)
            
            
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
                else:
                    win_full_command=cgpsmapper_file_path+" "+os_id_file_path
                    if verbose(): print win_full_command
                
                shutil.copy(fname,os_id_file_path)
            
                
                #Run cGPSmapper compile commands
                if isLinux:
                    status = call(Linux_full_command, shell=True)
                    status = call("rm -rf " + wine_temp_unix, shell=True)
                    status = call(r"mv " + wine_temp_unix_bak + r" " + wine_temp_unix, shell=True)
                else:
                    status = call(win_full_command, shell=True)
                
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
