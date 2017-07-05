from qgis.core import *
from qgis.gui import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys,os


class MapViewer(QMainWindow):
    def __init__(self,shapefile):
        QMainWindow.__init__(self)
        self.setWindowTitle("Map Viewer")

        canvas=QgsMapCanvas()
        canvas.useImageToRender(False)
        canvas.setCanvasColor(Qt.white)
        canvas.show()

        layer=QgsVectorLayer(shapefile,"large","ogr")
        if not layer.isValid():
            return IOError("Invalid Shapefile")

        QgsMapLayerRegistry.instance().addMapLayer(layer)
        canvas.setExtent(layer.extent())
        canvas.setLayerSet([QgsMapCanvasLayer(layer)])

        self.setCentralWidget(canvas)



app=QApplication(sys.argv)
QgsApplication.setPrefixPath("/usr", True)
QgsApplication.initQgis()

viewer=MapViewer("/home/priyankar/Desktop/FeattRy/TM_WORLD_BORDERS-0.3.shp")
viewer.show()
app.exec_()


QgsApplication.exitQgis()
