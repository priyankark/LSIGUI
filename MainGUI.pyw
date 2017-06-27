import sip
sip.setapi('QString', 2)


import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
import GUIGlobalValues
from qgis.core import *
from qgis.gui import *


class SHPCanvas(QDialog):
   def __init__(self):
       QDialog.__init__(self)

       grid=QGridLayout()
       k=0
       for i in range(int(GUIGlobalValues.floors/2)):
           for j in range(int(GUIGlobalValues.floors/2)):
               canvas = QgsMapCanvas()
               canvas.useImageToRender(False)
               file=GUIGlobalValues.listOfSHPFiles[k]
               k=k+1
               layer = QgsVectorLayer(file,str(k),"ogr")
               if not layer.isValid():
                   print "Layer failed to load"

               QgsMapLayerRegistry.instance().addMapLayer(layer);
               canvas.setExtent(layer.extent())
               cl = QgsMapCanvasLayer(layer)
               layers = [cl]
               canvas.setLayerSet(layers)

               grid.addWidget(canvas,i,j)
       self.setLayout(grid)

class ShowSelectionsCanvas(QDialog):
   def __init__(self):
       QDialog.__init__(self)
       layout=QVBoxLayout()
       showDXFFilesWidget=QWidget()
       layoutDXF=QVBoxLayout()
       for i in GUIGlobalValues.listOfDXFFiles:
           l=QLabel()
           l.setText(i)
           layoutDXF.addWidget(l)
       showDXFFilesWidget.setLayout(layoutDXF)
       layout.addWidget(showDXFFilesWidget)

       imageCanvasWidget=QWidget()
       grid=QGridLayout()
       k=0
       for i in range(len(GUIGlobalValues.listOfIMGFiles)/2):
           for j in range(len(GUIGlobalValues.listOfIMGFiles)/2):
               pic=QLabel()
               pic.setPixmap(QPixmap(GUIGlobalValues.listOfIMGFiles[k]))
               k+=1
               pic.show()

               grid.addWidget(pic,i,j)
       imageCanvasWidget.setLayout(grid)
       layout.addWidget(imageCanvasWidget)
       #layout.addWidget(imageCanvasWidget)
       self.setLayout(layout)








class takeInputDilaog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.floorsLabel=QLabel("Number of floors:")
        self.floorsText=QLineEdit()

        self.northPointLabel=QLabel("North Point:")
        self.northPointText=QLineEdit()

        self.latOfVertexLabel=QLabel("Latitude of Vertex")
        self.latText=QLineEdit()

        self.longOfVertexLabel=QLabel("Longitude of Vertex")
        self.longText=QLineEdit()

        self.selectDXFFilesLabel=QLabel("Select .dxf files:")
        self.selectDXFFilesButton=QPushButton("Select DXF files")
        self.selectDXFFilesButton.clicked.connect(self.getDXFFiles)

        self.selectIMGFilesLabel=QLabel("Select .svg files:")
        self.selectIMGFilesButton=QPushButton("Select SVG files")
        self.selectIMGFilesButton.clicked.connect(self.getIMGFiles)

        self.showSelectionButton=QPushButton("Show selections")
        self.showSelectionButton.clicked.connect(self.showSelection)

        self.submitButton=QPushButton("Submit")
        self.submitButton.clicked.connect(self.handleSubmit)

        fbox=QFormLayout()
        fbox.addRow(self.floorsLabel,self.floorsText)
        fbox.addRow(self.northPointLabel,self.northPointText)
        fbox.addRow(self.floorsLabel,self.floorsText)
        fbox.addRow(self.northPointLabel,self.northPointText)
        fbox.addRow(self.latOfVertexLabel,self.latText)
        fbox.addRow(self.longOfVertexLabel,self.longText)
        fbox.addRow(self.selectDXFFilesLabel,self.selectDXFFilesButton)
        fbox.addRow(self.selectIMGFilesLabel,self.selectIMGFilesButton)
        fbox.addRow(self.showSelectionButton,self.submitButton)
        fbox.setAlignment(Qt.AlignTop)
        self.setLayout(fbox)

    def getDXFFiles(self):
        dlg=QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        dlg.setFilter("DXF Files (*.dxf)")


        if dlg.exec_():
            filename=dlg.selectedFiles()
            GUIGlobalValues.listOfDXFFiles=filename
            print GUIGlobalValues.listOfDXFFiles

    def getIMGFiles(self):
        dlg=QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        dlg.setFilter("PNG Files (*.png)")

        if dlg.exec_():
            filename=dlg.selectedFiles()
            GUIGlobalValues.listOfIMGFiles=filename
            print GUIGlobalValues.listOfIMGFiles

    def handleSubmit(self):
        GUIGlobalValues.floors=int(self.floorsText.text())
        GUIGlobalValues.northPoint=float(self.northPointText.text())
        GUIGlobalValues.latOfVertex=float(self.latText.text())
        GUIGlobalValues.longOfVertex=float(self.longText.text())
        print GUIGlobalValues.floors,GUIGlobalValues.northPoint,GUIGlobalValues.latOfVertex,GUIGlobalValues.longOfVertex

    def showSelection(self):
        GUIGlobalValues.floors=int(self.floorsText.text())
        GUIGlobalValues.northPoint=float(self.northPointText.text())
        GUIGlobalValues.latOfVertex=float(self.latText.text())
        GUIGlobalValues.longOfVertex=float(self.longText.text())
        dlg=ShowSelectionsCanvas()
        dlg.exec_()



class PythonAPI(QObject):
    @pyqtSlot(str,result=str)
    def showMessage(self,theString):
        #QMessageBox.information(None, "Info","hello")
        inputWidget=takeInputDilaog()
        inputWidget.exec_()
        #q=QDialog()
        #q.exec_()



class Browser(QWebView):

    def __init__(self):
        QWebView.__init__(self)
        self.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.api=PythonAPI()
        self.frame = self.page().mainFrame()
        self.frame.javaScriptWindowObjectCleared.connect(self.load_api)
        self.loadFinished.connect(self._result_available)

    def load_api(self):
        # add pyapi to javascript window object
        # slots can be accessed in either of the following ways -
        #   1.  var obj = window.pyapi.json_decode(json);
        #   2.  var obj = pyapi.json_decode(json)
        self.frame.addToJavaScriptWindowObject('pyapi', self.api)

    def _result_available(self, ok):
        frame = self.page().mainFrame()

        print unicode(frame.toHtml()).encode('utf-8')

class MainApplication(QWidget):
    def __init__(self,parent=None):
        super(MainApplication,self).__init__(parent)
        layout=QHBoxLayout()

        #file=bar.addMenu("File")

        #tools=bar.addMenu("Tools")
        #help=bar.addMenu("Help")
        #info=bar.addMenu("Information")

        mapWidget=QWidget()
        mapWidgetLayout=QHBoxLayout()
        #myObj = StupidClass()
        self.view = Browser()
        #self.view.page().mainFrame().addToJavaScriptWindowObject("pyObj", myObj)
        self.view.load(QUrl("/home/priyankar/Desktop/GUIfinal/maps.html"))

        mapWidgetLayout.addWidget(self.view)
        mapWidget.setLayout(mapWidgetLayout)
        mapWidget.show()




        layout.addWidget(mapWidget)
        self.setLayout(layout)
        self.show()








if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainApplication=MainApplication()
    QgsApplication.setPrefixPath("/usr", True)
    QgsApplication.initQgis()
    QApplication.processEvents()


    app.exec_()
