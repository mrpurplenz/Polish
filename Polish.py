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
from qgis.utils import *
import re
import random
import sys
import shutil
import tempfile

from os.path import basename
from subprocess import call

def geomWrite(polish_file,pntsgeom,xform,DATA_LVL,isline):
    Datastring=''
    firstpoint=0
    pointcount=0
    ok_to_write_data=True
    for myQgsPoint in pntsgeom:
        newQgsPoint=xform.transform(myQgsPoint)
        if firstpoint==0:
            firstpoint=1
            ok_to_write_data=True
            Datastring=Datastring+'Data'+DATA_LVL+'=('+Datastring
        else:
            Datastring=Datastring+',('
        Datastring=Datastring+str(newQgsPoint.y())+','+str(newQgsPoint.x())+')'
        if isline:
            pointcount=pointcount+1
            if pointcount=255:
                pointcount=0
                firstpoint=0
                polish_file.write(u''+Datastring+'\n')
                Datastring='('+str(newQgsPoint.y())+','+str(newQgsPoint.x())+')'
                ok_to_write_data=False
    if ok_to_write_data:
        polish_file.write(u''+Datastring+'\n')

def writepolishobject(polish_file,outputtype,MP_TYPE_val,MP_NAME_val,END_LVL_val,DATA_LVL,xform,datalinesgeom):
    if outputtype='[POLYLINE]':
    	isline=True
    polish_file.write(u''+outputtype+'\n')
    polish_file.write(u'Type='+str(MP_TYPE_val)+'\n')                    
    if MP_NAME_val!='':
        polish_file.write(u'Label='+str(MP_NAME_val)+'\n')
    polish_file.write(u'EndLevel='+str(END_LVL_val)+'\n')
    for datalinegeom in datalinesgeom:
        geomWrite(polish_file,datalinegeom,xform,DATA_LVL,isline)
    polish_file.write(u'[END]\n\n')
    
def export_polish(self,layers_list,output_file,import_dict):
   
    
    #Build PASS polish header dictionary
    pass_header = {}
    pass_header['Name']='Map name'

    #Build DEFAULT polish header dictionary
    polishexporter_ver="0.0.1"
    default_header = {}
    default_header['ID'] = random.randint(10000000,99999999)
    default_header['Name']='python map'
    default_header['Elevation']='M'
    default_header['Preprocess']='F'
    default_header['TreSize']=1500
    default_header['TreMargin']=0.00000
    default_header['RgnLimit']=1024
    default_header['POIIndex']='Y'
    default_header['POINumberFirst']='Y'
    default_header['POIZipFirst']='Y'
    default_header['MG']='Y'
    default_header['Numbering']='N'
    default_header['Routing']='N'
    default_header['LeftSideTraffic']='Y'
    default_header['Copyright']='map generated by polish exporter '+polishexporter_ver
    default_header['PolygonEvaluate']='Y'
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
    
    #Prepare BIT_LEVEL dictionary
    BIT_LEVEL_DICT = {}
    for key in default_header:
        if key.startswith("Level"):
            if key!="Levels":
                #print "Found",key,"=",default_header[key],"Data"+str(key[5:])
                BIT_LEVEL_DICT[default_header[key]]=str(key[5:])

    with io.open(output_file, 'w',1,None,None,'\r\n') as polish_file:
        #Write header to file
        polish_file.write(u'; generated by Mr Purple\'s pyQGIS polish exporter '+polishexporter_ver+'\n')
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
            iter = layer.getFeatures()
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
            
            #idx will be -1 if no field found and subsiquently filled with a default value
            for feature in iter:
                geom=feature.geometry()
                kind_is_point=0
                kind_is_area=0
                kind_is_line=0
                if geom.type() == QGis.Point:
                    pass
                    #print "POI found"
                if geom.type() == QGis.Line:
                    pass
                    #print "LINE found"
                if geom.type() == QGis.Polygon:
                    pass
                    #print "AREA found"
                #get mp attribs or set to default
                attrs = feature.attributes()
                if MP_TYPE_idx >=0:
                    MP_TYPE_val=(attrs[MP_TYPE_idx])
                    #print MP_TYPE_val
                else:
                    MP_TYPE_val="0x00"
                    
                if MP_BIT_LVL_idx >=0:
                    MP_BIT_LVL_val=(attrs[MP_BIT_LVL_idx])
                else:
                    MP_BIT_LVL_val=24
                try:
                    END_LVL_val=BIT_LEVEL_DICT[MP_BIT_LVL_val]
                except:
                    print "No value found for MP_BIT_LVL attribute id reported as "+str(MP_BIT_LVL_idx)+". MP_TYPE for this feature was reported to be "+str(MP_TYPE_val)
                    print "attributes are:"
                    i=0
                    for attribute in attribute_list:
                        print "id "+str(i)+" is "+str(attribute.name())+" and has a value of "+str(attrs[i])
                        i=i+1
                    END_LVL_val=1
                    print "level set to "+str(END_LVL_val)
                    
                    
                if MP_DTA_LVL_idx >=0:
                    MP_DTA_LVL_val=(attrs[MP_DTA_LVL_idx])
                else:
                    MP_DTA_LVL_val=24
                DATA_LVL=BIT_LEVEL_DICT[MP_DTA_LVL_val]

                MP_NAME_field_name=''    
                if MP_NAME_idx>=0:
                    MP_NAME_field_name=(attrs[MP_NAME_idx])
                    LOCAL_NAME_idx = layer.fieldNameIndex(str(MP_NAME_field_name))
                    MP_NAME_val=''
                    if LOCAL_NAME_idx>=0:
                        MP_NAME_val=(attrs[LOCAL_NAME_idx])
                    else:
                        MP_NAME_val=''
                else:
                    MP_NAME_val=''

                try:
                    if MP_NAME_val.isNull():
                        MP_NAME_val=''
                except:
                    pass
                #print "MP_TYPE is "+str(MP_TYPE_val)
                #print "MP_BIT_LVL is "+str(MP_BIT_LVL_val) 
                #print "NAME is "+str(NAME_val)
                geometry_wkbtype=geom.wkbType()
                if geometry_wkbtype == QGis.WKBPoint:
                    outputtype='[POI]'
                    datalinegeom=[]
                    datalinegeom.append(geom.asPoint())
                    datalinesgeom=[]
                    datalinesgeom.append(datalinegeom)
                    writepolishobject(polish_file,outputtype,MP_TYPE_val,MP_NAME_val,END_LVL_val,DATA_LVL,xform,datalinesgeom)
                if geometry_wkbtype == QGis.WKBMultiPoint:
                    outputtype='[POI]'
                    for geomprime in geom.asPoint():
                        datalinegeom=[]
                        datalinegeom.append(geomprime)
                        datalinesgeom=[]
                        datalinesgeom.append(datalinegeom)
                        writepolishobject(polish_file,outputtype,MP_TYPE_val,MP_NAME_val,END_LVL_val,DATA_LVL,xform,datalinesgeom)
                if geometry_wkbtype == QGis.WKBLineString:
                    outputtype='[POLYLINE]'
                    datalinesgeom=[]
                    datalinesgeom.append(geom.asPolyline())
                    writepolishobject(polish_file,outputtype,MP_TYPE_val,MP_NAME_val,END_LVL_val,DATA_LVL,xform,datalinesgeom)
                if geometry_wkbtype == QGis.WKBMultiLineString:
                    outputtype='[POLYLINE]'
                    writepolishobject(polish_file,outputtype,MP_TYPE_val,MP_NAME_val,END_LVL_val,DATA_LVL,xform,geom.asMultiPolyline())
                if geometry_wkbtype == QGis.WKBPolygon:
                    outputtype='[POLYGON]'
                    writepolishobject(polish_file,outputtype,MP_TYPE_val,MP_NAME_val,END_LVL_val,DATA_LVL,xform,geom.asPolygon())
                if geometry_wkbtype == QGis.WKBMultiPolygon:
                    outputtype='[POLYGON]'
                    for datalinesgeom in geom.asMultiPolygon():
                        writepolishobject(polish_file,outputtype,MP_TYPE_val,MP_NAME_val,END_LVL_val,DATA_LVL,xform,datalinesgeom)
    print "wrote "+output_file
class Polish:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()

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
        
    def export_layers_as_polish(self,layers_list,output_file,import_dict={}):
        export_polish(self,layers_list,output_file,import_dict)
                        
    def export_files_as_polish(self,files_list,output_file,import_dict={}):
        layers_list=[]
        for file in files_list:
            if os.path.exists(file):
                layer=QgsVectorLayer(file,file, "ogr")
                if layer.isValid():
                    layers_list.append(layer)
        export_polish(self,layers_list,output_file,import_dict)
        

    def compile_preview_by_cgpsmapper(self,img_files_list,import_pv_dict):
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
        preview_default_dictionary['FileName']=new_temp_output_path
        output_dir=os.path.dirname(import_pv_dict['FileName'])
        for img_file in img_files_list:
            if os.path.exists(img_file):
                files_list.append(img_file)
            else:
               print "Could not find "+img_file
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
            
        cpreview_path='C:\\cgpsmapper\\'
        cpreview_file_path=cpreview_path+r"cpreview.exe"
        full_command=cpreview_file_path+" "+PV_FILE_FULL_PATH
        status = call(cpreview_file_path+" "+PV_FILE_FULL_PATH, shell=0)
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
        os.remove(PV_FILE_FULL_PATH)
        preview_file_path = os.path.join(output_dir,basename(preview_default_dictionary['FileName'])+'.mp')
        cgpsmapper_path='C:\\cgpsmapper\\'
        cgpsmapper_file_path=cgpsmapper_path+r"cgpsmapper.exe"
        full_command=os.path.join(cgpsmapper_path,"cgpsmapper.exe")+" "+preview_file_path
        print full_command
        status = call(cgpsmapper_file_path+" "+preview_file_path, shell=0)
        
        
    def compile_by_cgpsmapper(self,mp_files_list,cgpsmapper_path,import_pv_dict={}):
        from subprocess import call
        files_list=[]
        for fname in mp_files_list:
            if os.path.exists(fname):
                files_list.append(fname)
                print "compiling "+ fname
                #Get mp id
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
                print img_ID
            id_file=str(img_ID)+".mp"
            id_file_path=tempfile.gettempdir()+'\\'+id_file
            shutil.copy(fname,id_file_path)
            print id_file_path
            cgpsmapper_file_path=os.path.join(cgpsmapper_path,"cgpsmapper.exe")
            full_command=cgpsmapper_path+r"\cgpsmapper.exe "+id_file_path
            print full_command
            status = call(cgpsmapper_file_path+" "+id_file_path, shell=0)
            try:
                shutil.copy(os.path.join(tempfile.gettempdir(),str(img_ID)+".img"),os.path.join(os.path.split(fname)[0],str(img_ID)+".img"))
            except:
                print "unable to complete compliation for "+ str(img_ID)+".img"
            os.remove(id_file_path)
            os.remove(os.path.join(tempfile.gettempdir(),str(img_ID)+".img"))
        
    # run
    def Polish(self):
        QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('Polish', "Polish"), QCoreApplication.translate('Polish', "Polish"))
        return




if __name__ == "__main__":
    pass
