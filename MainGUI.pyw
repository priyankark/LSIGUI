import sip
sip.setapi('QString', 2)


import sys
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *
import GUIGlobalValues
from qgis.core import *
from qgis.gui import *
from Aakash.ExtractLine import *


# The MapViewer class is used for displaying the shape file on a canvas. QGIS (Python) has been made use of for the visualization.
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


#This is the class defining the main thread which executes the different functions (Extraction, Polygonization etc)
class MainExecutionThread(QThread):
    def __init__(self,fileName,k):
        QThread.__init__(self)
        self.SHPfileName=""
        self.DXFfilename=fileName
        self.k=k

    def __del__(self):
        self.wait()

    def run(self):
        print "DXF file name is ", self.DXFfilename
        self.SHPfileName=ExtractLines(self.DXFfilename)

        #print self.SHPfileName
        GUIGlobalValues.listOfDXFFiles[self.k]["SHPFile"]=self.SHPfileName
        print GUIGlobalValues.listOfDXFFiles[self.k]["SHPFile"]+" saved" #For troubleshooting
        self.sleep(2)



#Important : Needs to be worked upon. Not used in current program
# This class shall be used for setting up a network manager to establish connection to the internet over IIIT's proxy.
class MyNetworkAccessManager(QNetworkAccessManager):
    def __init__(self):
        QNetworkAccessManager.__init__(self)
        proxy = QNetworkProxy(QNetworkProxy.HttpProxy,"http://proxy.iiit.ac.in",8080)
        self.setProxy(proxy)




#The class below is for future use
#This class helps visualize both shp and image files on the canvas (Incomplete)
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





#This class is used for taking information from the user.

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
        self.selectDXFFilesButton.clicked.connect(self.showDFXDlg)

        self.selectIMGFilesLabel=QLabel("Select .svg files:")
        self.selectIMGFilesButton=QPushButton("Select SVG files")
        self.selectIMGFilesButton.clicked.connect(self.getIMGFiles)

        #self.showSelectionButton=QPushButton("Show selections")
        #self.showSelectionButton.clicked.connect(self.showSelection)

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
        #fbox.addRow(self.selectIMGFilesLabel,self.selectIMGFilesButton)
        fbox.addRow(self.submitButton)
        fbox.setAlignment(Qt.AlignTop)
        self.setLayout(fbox)





#The dialog that shows up on clicking the 'Select DXF button'
#All the selections made are stored as a dictionary of dictionaries in GUIGlobalVariable.listOfDXFFiles
    '''
    Dictionary structure is defined as follows
 GUIGlobalValues.listOfDXFFiles={
    floor_No: {
        "dxfSelect": reference a QPushButton Object for selecting the DXF,
         "dxfSelectTextBox": for showing the location of the file selected,
         "viewButton": button for viewing the final output,
         "extractButton": for running the main execution thread for extracting the lines, generating the SHP file
    }
    }
    The GUIGlobalVariables module is used for storing the various values so that it is easy to pass these between the other modules.
    The reason the references to the various PyQt Objects are being passed to the dictionary above is because we require a dynamic GUI.
    That is, if the user selected the number of floors to be 2, we would have to show the GUI to have options only for taking two inputs
    in the SelectDXF dialog.

    Storing the various information related to a particular floor in a single dictionary with the key as the floor number and the value as
    another dictionary with different sub fields related to that particular floor, should later prove advantageous.



    '''

#Function for selecting the DXF files
    def showDFXDlg(self):
        dlg=QDialog()
        GUIGlobalValues.floors=int(self.floorsText.text())
        GUIGlobalValues.northPoint=float(self.northPointText.text())
        GUIGlobalValues.latOfVertex=float(self.latText.text())
        GUIGlobalValues.longOfVertex=float(self.longText.text())
        GUIGlobalValues.listOfSHPFiles={}
        for i in range(0,GUIGlobalValues.floors):
            GUIGlobalValues.listOfDXFFiles[i]=dict()

        mainDlgLayout=QVBoxLayout()
        mainDlgWidget=QWidget()
        for i in range(0,GUIGlobalValues.floors):
            floorInfoLayout=QHBoxLayout()
            GUIGlobalValues.listOfDXFFiles[i]["dxfSelect"]=QPushButton("Select Floor "+str(i)+" Plan")

            GUIGlobalValues.listOfDXFFiles[i]["dxfSelectTextBox"]=QLineEdit()

            GUIGlobalValues.listOfDXFFiles[i]["dxfSelect"].clicked.connect(lambda:self.getDXFFiles(GUIGlobalValues.listOfDXFFiles[i]["dxfSelectTextBox"]))
            GUIGlobalValues.listOfDXFFiles[i]["georefButton"]=QPushButton("GeoReference")
            #Ananth's code for this button
            GUIGlobalValues.listOfDXFFiles[i]["viewButton"]=QPushButton("View")
            #DFX Viewer code
            GUIGlobalValues.listOfDXFFiles[i]["extractButton"]=QPushButton("Extract")
            #Aakash+Saumya+Clean Module code
            GUIGlobalValues.listOfDXFFiles[i]["extractButton"].clicked.connect(self.handleExtract)




            floorInfoLayout.addWidget(GUIGlobalValues.listOfDXFFiles[i]["dxfSelectTextBox"])
            floorInfoLayout.addWidget(GUIGlobalValues.listOfDXFFiles[i]["dxfSelect"])
            floorInfoLayout.addWidget(GUIGlobalValues.listOfDXFFiles[i]["georefButton"])
            floorInfoLayout.addWidget(GUIGlobalValues.listOfDXFFiles[i]["viewButton"])
            floorInfoLayout.addWidget(GUIGlobalValues.listOfDXFFiles[i]["extractButton"])
            floorInfoWidget=QWidget()
            floorInfoWidget.setLayout(floorInfoLayout)
            mainDlgLayout.addWidget(floorInfoWidget)

        submit=QPushButton("Submit")
        submit.clicked.connect(self.showOutput)
        mainDlgLayout.addWidget(submit)
        dlg.setLayout(mainDlgLayout)


        dlg.exec_()

#Visualizingthe SHP files
    def showOutput(self):
        dlg=QDialog()
        grid=QVBoxLayout()
        k=0
        for i in range(0,GUIGlobalValues.floors):
            canvas = QgsMapCanvas()
            canvas.useImageToRender(False)
            print GUIGlobalValues.listOfDXFFiles[k]["SHPFile"]
            file=GUIGlobalValues.listOfDXFFiles[k]["SHPFile"]
            k=k+1
            layer = QgsVectorLayer(file,str(k),"ogr")
            if not layer.isValid():
                print "Layer failed to load"

            QgsMapLayerRegistry.instance().addMapLayer(layer)
            canvas.setExtent(layer.extent())
            cl = QgsMapCanvasLayer(layer)
            layers = [cl]
            canvas.setLayerSet(layers)

            grid.addWidget(canvas)
        dlg.setLayout(grid)


        dlg.exec_()

#Opening up the File Dilaog for selecting the DXF file
    def getDXFFiles(self,dxfSelectTextBox):
        dlg=QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setFilter("DXF Files (*.dxf)")
        sender=self.sender()
        text=sender.text()
        t=0

        #The loop below finds the floor number corresponding to the button press i.e.
        # Which floor's button for selecting the DXF was pressed?
        for key,value in GUIGlobalValues.listOfDXFFiles.items():
            if value["dxfSelect"]==sender:
                t=int(key)


        if dlg.exec_():
            filename=dlg.selectedFiles()
            GUIGlobalValues.listOfDXFFiles[t]["dxfSelectTextBox"].setText(filename[0])
            GUIGlobalValues.listOfDXFFiles[t]["DXFFileName"]=filename[0]
            print GUIGlobalValues.listOfDXFFiles[t]["DXFFileName"]

#Handling the execution of the main code
    def handleExtract(self):
        sender=self.sender()
        print sender.text()
        t=0
        for key,value in GUIGlobalValues.listOfDXFFiles.items():
            if value["extractButton"]==sender:
                t=int(key)
        print t

        print GUIGlobalValues.listOfDXFFiles[t]["DXFFileName"]
        mainExecutionThread=MainExecutionThread(GUIGlobalValues.listOfDXFFiles[t]["DXFFileName"],t)
        mainExecutionThread.start()






#For Image Files (future use, incomplete)
    def getIMGFiles(self):
        dlg=QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        dlg.setFilter("PNG Files (*.png)")

        if dlg.exec_():
            filename=dlg.selectedFiles()
            GUIGlobalValues.listOfIMGFiles=filename
            print GUIGlobalValues.listOfIMGFiles


#Handling of the submission of the form containing the main information (Number of floors etc etc)
    def handleSubmit(self):
        GUIGlobalValues.floors=int(self.floorsText.text())
        GUIGlobalValues.northPoint=float(self.northPointText.text())
        GUIGlobalValues.latOfVertex=float(self.latText.text())
        GUIGlobalValues.longOfVertex=float(self.longText.text())
        print GUIGlobalValues.floors,GUIGlobalValues.northPoint,GUIGlobalValues.latOfVertex,GUIGlobalValues.longOfVertex


#This API is defined to be able to expose Python Objects and functions to JavaScript.
#This is mainly for the webview used to display the Google Map. As soon as thye user clicks on a coordinate, takeInputDilaog() would be opened
class PythonAPI(QObject):
    @pyqtSlot(str,result=str)
    def showMessage(self,theString):
        #QMessageBox.information(None, "Info","hello")
        inputWidget=takeInputDilaog()
        inputWidget.exec_()
        #q=QDialog()
        #q.exec_()


#Class defined for the webview
class Browser(QWebView):

    def __init__(self):
        QWebView.__init__(self)
        self.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

        #proxy=QNetworkProxy()
        #proxy.setType(QNetworkProxy.HttpProxy)
        #proxy.setHostName("http://proxy.iiit.ac.in/")
        #proxy.setPort(8080)
        #proxy.setUser("priyankar.kumar98@gmail.com")
        #proxy.setPassword("5ea291f3")
        #QNetworkProxy.setApplicationProxy(proxy)


        #old_manager = self.page().networkAccessManager()
        #new_manager = MyNetworkAccessManager()
        #self.page().setNetworkAccessManager(new_manager)

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


#Class defined for the Main Application Widget
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
        #self.view.load(QUrl("/home/priyankar/Desktop/InternshipWork/GUIfinal/maps.html"))
        dir = os.path.dirname(__file__)
        filename = os.path.join(dir, 'maps.html')
        self.view.load(QUrl(filename))


        mapWidgetLayout.addWidget(self.view)
        mapWidget.setLayout(mapWidgetLayout)
        mapWidget.show()




        layout.addWidget(mapWidget)
        self.setLayout(layout)
        self.show()




if __name__ == '__main__':
    #proxy=QNetworkProxy()
    #proxy.setType(QNetworkProxy.HttpProxy)
    #proxy.setHostName("http://proxy.iiit.ac.in/")
    #proxy.setPort(8080)
    #proxy.setUser("priyankar.kumar98@gmail.com")
    #proxy.setPassword("5ea291f3")

    #QNetworkProxy.setApplicationProxy(proxy)

    app = QApplication(sys.argv)
    mainApplication=MainApplication()
    QgsApplication.setPrefixPath("/usr", True) #For loading QGIS python. This path is different for Windows.
    QgsApplication.initQgis()
    QApplication.processEvents()



    app.exec_()
