from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
import serial

import sys
sys.path.insert(0, '../globals')
from arduino_communication_protocol import *


class ArduinoThread(QtCore.QThread, QtGui.QGraphicsView):
    data = QtCore.pyqtSignal(object)
    connected = False

    def __init__(self):
        QtCore.QThread.__init__(self)

        try:
            self.arduino = serial.Serial(ARDUINO_INTERFACE, ARDUINO_BAUD_RATE)
            self.connected = True
        except:
            self.connected = False

        self._loop = True

    def run(self):
        if self.connected:
            while self._loop:
                try:
                    string = self.arduino.readline()

                    if HwInterface.ZOOM_CW in string:
                        self.data.emit(HwInterface.ZOOM_CW)
                    # if HwInterface.FREEZE_PRESS in string:
                    #     self.data.emit(HwInterface.FREEZE_PRESS)
                    elif HwInterface.CALIBRATE_PRESS in string:
                        self.data.emit(HwInterface.CALIBRATE_PRESS)
                    elif HwInterface.ZOOM_CCW in string:
                        self.data.emit(HwInterface.ZOOM_CCW)
                    elif HwInterface.ZOOM_PRESS in string:
                        self.data.emit(HwInterface.ZOOM_PRESS)
                    elif HwInterface.RIGHT_PRESS in string:
                        self.data.emit(HwInterface.RIGHT_PRESS)
                    elif HwInterface.CAPTURE_PRESS in string:
                        self.data.emit(HwInterface.CAPTURE_PRESS)
                    elif HwInterface.TOP_PRESS in string:
                        self.data.emit(HwInterface.TOP_PRESS)
                    elif HwInterface.FREQUENCY_CW in string:
                        self.data.emit(HwInterface.FREQUENCY_CW)
                    elif HwInterface.FREQUENCY_CCW in string:
                        self.data.emit(HwInterface.FREQUENCY_CCW)
                    elif HwInterface.GAIN_CW in string:
                        self.data.emit(HwInterface.GAIN_CW)
                    elif HwInterface.GAIN_CCW in string:
                        self.data.emit(HwInterface.GAIN_CCW)
                    elif HwInterface.FOCUS_CW in string:
                        self.data.emit(HwInterface.FOCUS_CW)
                    elif HwInterface.FOCUS_CCW in string:
                        self.data.emit(HwInterface.FOCUS_CCW)
                    elif HwInterface.DEPTH_CW in string:
                        self.data.emit(HwInterface.DEPTH_CW)
                    elif HwInterface.DEPTH_CCW in string:
                        self.data.emit(HwInterface.DEPTH_CCW)

                except:
                    pass
        else:
            pass
