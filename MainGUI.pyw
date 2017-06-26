import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *


html="""
<body> Hello world </body>

"""


class Browser(QWebView):

    def __init__(self):
        QWebView.__init__(self)
        self.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        self.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

        self.loadFinished.connect(self._result_available)

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
        self.view = Browser()
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


    app.exec_()
