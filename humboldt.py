
# 'Humboldt' - A program to teach geography/topography.
#
# See also http://kartograph.org/docs/kartograph.py/ and http://www.naturalearthdata.com/
#
# Software by Michiel Overtoom, motoom@xs4all.nl

from PyQt4 import QtGui, QtCore
import svgreader

solid_pen =  QtGui.QPen(QtGui.QColor("black"))
no_brush= QtGui.QBrush(QtCore.Qt.NoBrush)
        
class MyPolygonGraphicsItem(QtGui.QGraphicsPolygonItem):
    def __init__(self, frame, name, *args, **kwargs):
            QtGui.QGraphicsPolygonItem.__init__(self, *args, **kwargs)
            self.frame=frame
            self.name = name
            self.setAcceptHoverEvents(True)
            self.setPen(solid_pen)
            self.setBrush(no_brush)
            
    def hoverEnterEvent(self, event):
        self.frame.label.setText(self.name)

    def hoverLeaveEvent(self, event):
        self.frame.label.setText("")

    def mousePressEvent(self, event):
        pass


            
class MainFrame(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.setWindowTitle("Humboldt - Learn topography")
        self.setMinimumSize(200, 120)
        self.resize(1024, 600)
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
        self.label.setMinimumWidth(400)
        self.label.setMinimumHeight(50)
        self.label.setMargin(8)
        self.label.setFont(QtGui.QFont("Helvetica", 24))
        
        view = QtGui.QGraphicsView()
        bkbrush = QtGui.QBrush(self.palette().color(QtGui.QPalette.Window))
        view.setBackgroundBrush(bkbrush)
        toptobottom.addWidget(view)
        # view.setFrameStyle(QtGui.QFrame.NoFrame) # Geen border om kaart heen.

        self.scene = QtGui.QGraphicsScene()
        view.setScene(self.scene)

        meta, background, regions = svgreader.readfile("usa-states.svg")
        errors = meta[3]
        if errors: print errors
        for region in regions:
            title, coords = region
            polyf = QtGui.QPolygonF([QtCore.QPointF(x,y) for (x,y) in coords])
            item = MyPolygonGraphicsItem(self, title, polyf)
            self.scene.addItem(item)

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
