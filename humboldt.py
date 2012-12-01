
# 'Humboldt' - A program to teach geography/topography.
#
# See also http://kartograph.org/docs/kartograph.py/ and http://www.naturalearthdata.com/
#
# Software by Michiel Overtoom, motoom@xs4all.nl

# TODO: use Qt::PointingHandCursor


from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
import svgreader
import random

no_pen = QtGui.QPen(QtCore.Qt.NoPen)

no_brush= QtGui.QBrush(QtCore.Qt.NoBrush)
hover_brush = QtGui.QBrush(QtGui.QColor(255,255,200, 80))
select_brush= QtGui.QBrush(QtGui.QColor(255,255,200, 210))
flash0_brush = QtGui.QBrush(QtGui.QColor(255,255,255, 200))
flash1_brush = QtGui.QBrush(QtGui.QColor(255,255,255, 130))

class Region(QtGui.QGraphicsPolygonItem):
    def __init__(self, frame, name, polyf):
            super(QtGui.QGraphicsPolygonItem, self).__init__(polyf)
            self.frame=frame
            self.name = name
            self.setAcceptHoverEvents(True)
            self.setPen(no_pen)
            self.setBrush(no_brush)
            
    def hoverEnterEvent(self, event):
        self.frame.label.setText(self.name)
        self.setBrush(hover_brush)
        
    def hoverLeaveEvent(self, event):
        self.frame.label.setText("")
        self.setBrush(no_brush)

    def mousePressEvent(self, event):
        self.setBrush(select_brush)
        

class MyView(QtGui.QGraphicsView):
    def resizeEvent(self, ev):
        super(QtGui.QGraphicsView, self).resizeEvent(ev)
        scene = self.scene()
        self.fitInView(0,0,scene.width(),scene.height(), QtCore.Qt.KeepAspectRatio)


class MainFrame(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.setWindowTitle("Humboldt - Learn topography")
        self.setMinimumSize(640, 400)
        self.resize(800, 600)
        self.statusBar().showMessage("Ready")

        central = QtGui.QWidget(self)
        self.setCentralWidget(central)

        toptobottom = QtGui.QVBoxLayout()
        central.setLayout(toptobottom)
        upperframe = QtGui.QFrame()
        upperframe.setFrameStyle(6)
        upperframe.setFixedHeight(80)
        toptobottom.addWidget(upperframe)

        '''
        self.listbox = QtGui.QListWidget(upperframe)
        self.connect(self.listbox, QtCore.SIGNAL("itemSelectionChanged()"), self.on_select)
        self.listbox.clear()
        entries = (("Aap", {1: 2, 3: 4}), ("Noot", 78), ("Mies", [5,6,7]), ("Teun", 8.4), ("Vuur", "hoi"))
        for entry in entries:
            name, obj = entry
            item = QtGui.QListWidgetItem(name, self.listbox)
            item.setData(QtCore.Qt.UserRole, obj)
        '''

        self.label = QtGui.QLabel(upperframe)
        self.label.setMinimumWidth(640)
        self.label.setMinimumHeight(60)
        self.label.setMargin(8)
        self.label.setFont(QtGui.QFont("Helvetica", 24))
        self.label.setText("Humboldt")
        
        view = MyView()
        bkbrush = QtGui.QBrush(self.palette().color(QtGui.QPalette.Window))
        view.setBackgroundBrush(bkbrush)
        toptobottom.addWidget(view)
        view.setFrameStyle(QtGui.QFrame.NoFrame) # Geen border om kaart heen.

        self.scene = QtGui.QGraphicsScene()
        view.setScene(self.scene)
        
        # Read the data file.
        self.regions = []
        meta, background, regions = svgreader.readfile("usa-states.svg")
        errors = meta[3]
        if errors:
            print errors

        # Backdrop map.
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(background.img)
        item = QtGui.QGraphicsPixmapItem(pixmap)
        self.scene.addItem(item)

        # States/countries.
        for region in regions:
            title, coords = region
            polyf = QtGui.QPolygonF([QtCore.QPointF(x,y) for (x,y) in coords])
            item = Region(self, title, polyf)
            self.regions.append(item)
            self.scene.addItem(item)

        self.regiontimer = QtCore.QTimer()
        self.regiontimer.timeout.connect(self.regiontimeevent)
        self.regiontimer.setInterval(1000)
        self.regiontimer.start()
        
        self.pulsetimer = QtCore.QTimer()
        self.pulsetimer.timeout.connect(self.pulsetimeevent)
        self.pulsetimer.setInterval(120)

    def regiontimeevent(self):
        self.pulseregion = random.choice(self.regions)
        self.label.setText(self.pulseregion.name)
        self.pulsecount = 7
        self.pulsetimer.start()
        
    def pulsetimeevent(self):
        self.pulsecount -= 1
        if self.pulsecount == 0:
            self.pulsetimer.stop()
            self.pulseregion.setBrush(no_brush)            
        elif self.pulsecount & 1:
            self.pulseregion.setBrush(flash1_brush)
        else:
            self.pulseregion.setBrush(flash0_brush)
        
    def on_select(self):
        item = self.listbox.selectedItems()[0]
        name =  item.text()
        obj = item.data(QtCore.Qt.UserRole).toPyObject()
        s = "You clicked %s. userdata is %r" % (item.text(), obj)
        self.statusBar().showMessage(s)

        
if __name__ == "__main__":
    app = QtGui.QApplication([])
    frame = MainFrame()
    frame.show()
    app.exec_()
