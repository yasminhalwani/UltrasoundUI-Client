from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QThread, SIGNAL
from PyQt4.QtCore import *
import win32gui


class CursorThread(QtCore.QThread, QtGui.QGraphicsView):
    # xy = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        while True:
            try:
                flags, hcursor, (x, y) = win32gui.GetCursorInfo()
                # self.xy.emit((x, y))

                self.emit(SIGNAL('xy(PyQt_PyObject)'), (x, y))

            except:
                pass
