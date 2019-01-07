import sys
import win32api
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from multiprocessing import Queue

sys.path.insert(0, '../components')
from gaze_tracker_comp import *
from plot_comp import *

# NOTE: there's always an offset between the actual points transmitted and the drawn rectangle on screen
# (data is ok, visual representation in this program isn't)

pog = [0, 0]


class GazeTrackerGUI(QtGui.QGraphicsView):
    def __init__(self, screen_width_input, screen_height_input):
        super(GazeTrackerGUI, self).__init__()

        self.queue = multiprocessing.Queue()

        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#
        self.screen_width = screen_width_input
        self.screen_height = screen_height_input

        self.xpos = 0
        self.ypos = 0
        self.is_valid = 0

        self.moving_tiny_rect = None

        self.gaze_tracker_process = None

        self.additional_thread = None

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#
        # PlotWindow(self.screen_width * 1.5)
        self.setup_gui()
        self.setup_moving_element()

    def setup_gui(self):
        self.setScene(QtGui.QGraphicsScene())
        self.setFixedSize(self.screen_width, self.screen_height)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def setup_moving_element(self):
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(QtCore.Qt.green))
        brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.green).darker(150))
        self.moving_tiny_rect = self.scene().addRect(0, 0, 50, 50, pen, brush)
        self.moving_tiny_rect.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

    def update_location(self):

        try:
            info = self.queue.get_nowait()
            self.xpos = float(info['FPOGX']) * self.screen_width
            self.ypos = float(info['FPOGY']) * self.screen_height

            global pog
            pog = [self.xpos, self.ypos]

            self.moving_tiny_rect.setPos(self.xpos, self.ypos)

        except:
            pass

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_A:
            self.gaze_tracker_process = GazeTrackerProcess()
            self.gaze_tracker_process.set_values([GazeTrackerDataEnableMessages.POG_FIX], self.queue)
            self.gaze_tracker_process.start()

            self.gaze_update_thread = QtCore.QTimer()
            self.connect(self.gaze_update_thread, QtCore.SIGNAL('timeout()'), self.update_location)
            self.gaze_update_thread.start(0)

        if key == QtCore.Qt.Key_1:
            self.gaze_tracker_process.show_tracker_display()

        if key == QtCore.Qt.Key_2:
            import pdb
            pdb.set_trace()

        if key == QtCore.Qt.Key_S:
            self.gaze_tracker_process.set_use_moving_average_filter(True)

        if key == QtCore.Qt.Key_D:
            self.gaze_tracker_process.set_use_moving_average_filter(False)

        if key == QtCore.Qt.Key_F:
            print "calibrate"
            self.gaze_tracker_process.start_calibration()

        if key == QtCore.Qt.Key_G:
            print "exit calibration window"
            self.gaze_tracker_process.exit_calibration()

        if key == QtCore.Qt.Key_H:
            print "show tracker display"
            self.gaze_tracker_process.show_tracker_display()

        if key == QtCore.Qt.Key_J:
            print "hide tracker display"
            self.gaze_tracker_process.hide_tracker_display()


class PlotWindow(QtGui.QMainWindow):
    def __init__(self, ylim):
        super(PlotWindow, self).__init__()

        # Define the geometry of the main window
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("my first window")

        # Create FRAME_A
        self.FRAME_A = QtGui.QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(210, 210, 235, 255).name())
        self.LAYOUT_A = QtGui.QGridLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)

        # Place the matplotlib figure
        self.myFig = CustomFigCanvas(ylim)
        self.LAYOUT_A.addWidget(self.myFig, *(0, 1))

        # Add the callbackfunc to ..
        myDataLoop = threading.Thread(name='myDataLoop', target=dataSendLoop, args=(self.addData_callbackFunc,))
        myDataLoop.setDaemon(True)
        myDataLoop.start()

        self.show()

    def addData_callbackFunc(self, value):
        # print("Add data: " + str(value))
        self.myFig.addData(value)


def dataSendLoop(addData_callbackFunc):
    # Setup the signal-slot mechanism.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)

    while True:
        time.sleep(0.1)
        mySrc.data_signal.emit(pog[0])


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPLICATION_TITLE_GAZE_TRACKER_COMPONENT_GUI)

    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    trackerGUI = GazeTrackerGUI(width, height)
    trackerGUI.show()
    app.exec_()
