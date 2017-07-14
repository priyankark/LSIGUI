'''
import sys
import time
import datetime
import os
from getpass import getuser

# Qgis modules and environment
from qgis.core import *
import qgis.utils
from PyQt4.QtCore import QFileInfo, QSettings

from PyQt4.QtGui import QApplication
app = QApplication([])

QgsApplication.setPrefixPath("/usr", True)
QgsApplication.initQgis()

# Prepare processing framework
sys.path.append('/usr/share/qgis/python/plugins')
#from processing.core.Processing import Processing
import processing

def cleanSHP():
    processing.runalg('qgis:explodelines','/home/priyankar/Desktop/InternshipWork/GUIfinal/Vindhya algo testDXF_segmentedCenterLines.shp','/home/priyankar/Desktop/InternshipWork/GUIfinal/temp.shp')


processing.Processing.initialize()
processing.Processing.updateAlgsList()


cleanSHP()

'''

from osgeo import ogr
import sys
import math
import os

file=r'/home/priyankar/Desktop/InternshipWork/GUIfinal/Vindhya algo testDXF_segmentedCenterLines.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
dataSource = driver.Open(file, 0)

featDict=[]
lyr=dataSource.GetLayer()
for i in range(lyr.GetFeatureCount()):
    feat=lyr.GetFeature(i)
    geom=feat.GetGeometryRef()
    firstpoint=geom.GetPoint(0)
    lastpoint=geom.GetPoint(geom.GetPointCount()-1)
    id=feat.GetField('id')
    geom=feat.geometry()
    x1=firstpoint[0]
    y1=firstpoint[1]
    x2=lastpoint[0]
    y2=lastpoint[1]
    try:
        rx1=round(x1,4)
        ry1=round(y1,4)
        rx2=round(x2,4)
        ry2=round(y2,4)
        slope=((ry2-ry1)/(rx2-rx1))
    except ZeroDivisionError:
        slope="infinity"
    length=(math.sqrt(pow(x2-x1,2)+pow(y2-y1,2)))
    if slope != "infinity":
        c=round((y2-(slope*x2)),4)
    else:
        c=rx1

    featDict.append({"id":id,"x1":x1,"y1":y1,"x2":x2,"y2":y2,"length":length,"slope":slope,"c":c,"geometry":geom,"rx1":rx1,"ry1":ry1,"rx2":rx2,"ry2":ry2})
    print id,firstpoint[0],firstpoint[1],lastpoint[0],lastpoint[1],length,"slope",slope,rx1==rx2,c #X,Y,X,Y

featDictCopy=list(featDict)
commonLineArray=[]

for i in range(0,len(featDict)):
    lst=[]
    lst.append(featDict[i]["id"])
    for j in range(i+1,len(featDict)):
        flat_list = [item for sublist in commonLineArray for item in sublist]
        if featDict[i]["slope"]==featDict[j]["slope"] and featDict[i]["c"]==featDict[j]["c"] and featDict[j]["id"] not in (flat_list):      #and featDict[j]["length"]<featDict[i]["length"]:
            lst.append(featDict[j]["id"])


    commonLineArray.append(lst)

'''
for i in range(0,len(commonLineArray)):
    for j in range(i+1,len(commonLineArray)):
        if len(set(commonLineArray[i])&set(commonLineArray[j]))>1:
            commonLineArray[i]=list(set(commonLineArray[i])&set(commonLineArray[j]))
'''



    #print featDict[i]["id"]
cleanData=[]

for item in commonLineArray:
    if len(item)>1:
        cleanData.append(item)

print cleanData

largestLineArray=[]


#Delete the largest element
#delFromCleanDataArray=[]
for i in cleanData:
    pos=0
    longest=featDict[i[pos]]["length"]
    value=i[0]
    for j in range(0,len(i)):
        if featDict[i[j]]["length"]>=longest:
            longest=featDict[i[j]]["length"]
            pos=j
            value=i[j]
    delAr=[]
    for j in range(0,len(i)):
        if i[j]==value:
            continue
        else:
            if ((featDict[i[j]]["rx1"]<featDict[i[pos]]["rx1"]) and (featDict[i[j]]["rx2"]<=featDict[i[pos]]["rx1"])) or ((featDict[i[j]]["rx1"]>=featDict[i[pos]]["rx2"]) and (featDict[i[j]]["rx2"]>featDict[i[pos]]["rx2"])) :
                delAr.append((i[j]))
    delAr.append(i[pos])
    #delFromCleanDataArray.append(delAr)
    print "i before",i
    print "delAr",delAr
    cleanData[cleanData.index(i)]=list(set(i).difference(set(delAr)))
    print "i after",i

print cleanData






indices = [item for sublist in cleanData for item in sublist] #Contains ids of lines to remove

print indices

for index in sorted(indices, reverse=True):
    del featDict[index]


for i in featDict:
    print i


#Make the shapefile
driver = ogr.GetDriverByName('ESRI Shapefile')
shapefile_name="cleanedSHP.shp"
if os.path.exists(shapefile_name):
    os.remove(shapefile_name)

out_data_source = driver.CreateDataSource(shapefile_name)

out_layer = out_data_source.CreateLayer('cleaned', geom_type=ogr.wkbLineString)


out_layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
out_layer_defn = out_layer.GetLayerDefn()

for feat in featDict:
    line = ogr.Geometry(ogr.wkbLineString)
    line.AddPoint(feat["x1"],feat["y1"])
    line.AddPoint(feat["x2"],feat["y2"])
    feature = ogr.Feature(out_layer_defn)
    feature.SetField('id',feat["id"])
    feature.SetGeometry(line)
    out_layer.CreateFeature(feature)
    feature.Destroy()

out_data_source.Destroy()





















