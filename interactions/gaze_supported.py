from win32api import GetSystemMetrics
from win32api import SetCursorPos
import sys
import win32gui
from win32gui import GetForegroundWindow

from pyqtgraph.Qt import QtCore, QtGui

sys.path.insert(0, '../components')
from gaze_tracker_comp import *
from plot_comp import *

sys.path.insert(0, '../globals')
from common_constants import *
from states import *

from manual_based import ManualBased

plot_data = 0


class GazeSupported(ManualBased):
    def __init__(self, screen_width_input, screen_height_input):
        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#

        # <editor-fold desc="gaze-based zoom interaction variables">
        self.pan_the_zoom = False
        self.zoom_timeout = time.time()
        self.pan_active_rect = None
        # </editor-fold>

        # -- pan areas
        self.upper_rect = None
        self.upper_right_rect = None
        self.upper_left_rect = None
        self.lower_rect = None
        self.lower_right_rect = None
        self.lower_left_rect = None
        self.left_rect = None
        self.right_rect = None
        # </editor-fold>

        # <editor-fold desc="threads variables">
        self.input_held_monitor_timer_thread = None
        # </editor-fold>

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#
        super(GazeSupported, self).__init__(screen_width_input, screen_height_input)
        # PlotWindow(self.screen_width * 1.5)

        self.pan_active_rect = QtCore.QRect(self.image_width * 0.15, self.image_height - (self.image_height * 0.82),
                                            self.image_width - (self.image_width * 0.30),
                                            self.image_height - (self.image_height * 0.30))

    # <editor-fold desc="threading functions">

    def create_threads(self):
        super(GazeSupported, self).create_threads()
        self.input_held_monitor_timer_thread = QtCore.QTimer()
        self.connect(self.input_held_monitor_timer_thread, QtCore.SIGNAL('timeout()'), self.callback_input_held_monitor)

    def start_threads(self):
        super(GazeSupported, self).start_threads()
        self.thread_start_input_held_monitor()

    def thread_start_input_held_monitor(self):
        self.input_held_monitor_timer_thread.start(.1)

    # </editor-fold>

    # <editor-fold desc="callback functions">
    def callback_input_held_monitor(self):

        # <editor-fold desc="pan-related">
        self.gaze_activation_press_elapsed_time = time.time() - self.gaze_activation_press_start_time

        if self.gaze_activation_pressed:
            if self.gaze_activation_press_elapsed_time > 0.5:
                self.gaze_activation_held = True
        else:
            self.gaze_activation_press_start_time = 0

        if self.gaze_activation_held:
            if self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
                pass
                # self.auto_pan_using_pan_regions()
                # self.pan_to_POG()

            elif self.system_state == SystemState.PRE_ZOOM_A or self.system_state == SystemState.PRE_ZOOM_B:
                self.set_roi_in_center_of_pog()

        # </editor-fold>

        # <editor-fold desc="zoom-related">
        if time.time() - self.zoom_timeout > 0.5:
            self.zoom_timeout = time.time()
            self.pan_the_zoom = False
        else:
            if self.pan_the_zoom:
                if self.allow_gaze_pan_after_zoom:
                    self.auto_pan_using_pan_regions()
                    self.pan_to_POG()
        # </editor-fold>

    # </editor-fold>

    # <editor-fold desc="roi functions">
    def set_roi_in_center_of_pog(self):

        pos = self.image_view_box.mapSceneToView(self.POG)
        pos = QtCore.QPoint(pos.x(), pos.y())

        rect = QtCore.QRect(self.detail_view_roi.pos().x(), self.detail_view_roi.pos().y(),
                            self.detail_view_roi.size().x(), self.detail_view_roi.size().y())

        if rect.contains(pos):

            x = pos.x()
            y = pos.y()

            pos_check = self.image_view_box.mapFromViewToItem(self.image_item, pos)

            if pos_check.x() - self.roi.size().x() / 2 < 0:
                x = self.roi.size().x() / 2

            if pos_check.x() + self.roi.size().x() / 2 > self.image_width:
                x = self.image_width - self.roi.size().x() / 2

            if pos_check.y() + self.roi.size().y() / 2 > self.image_height:
                y = self.image_height - self.roi.size().y() / 2

            if pos_check.y() - self.roi.size().y() / 2 < 0:
                y = self.roi.size().y() / 2

            self.set_roi_position_in_the_center_of(x, y)

    # </editor-fold>

    # <editor-fold desc="pan functions">

    def pan_to_POG(self):

        pos = self.image_view_box.mapSceneToView(self.POG)
        pos = QtCore.QPoint(pos.x(), pos.y())

        rect = QtCore.QRect(self.detail_view_roi.pos().x(), self.detail_view_roi.pos().y(),
                            self.detail_view_roi.size().x(), self.detail_view_roi.size().y())

        if rect.contains(pos):

            mapped_pog = self.image_view_box.mapSceneToView(self.POG)

            C = QtCore.QPoint(self.roi.x() + (self.roi.size().x()/2), self.roi.y() + (self.roi.size().y()/2))

            D = math.sqrt(math.pow(C.x(), 2) + math.pow(C.y(), 2)) / 2

            d = math.sqrt((math.pow(mapped_pog.x() - C.x(), 2)) + (math.pow(mapped_pog.y() - C.y(), 2)))

            theta = math.atan2(math.fabs(mapped_pog.y() - C.y()), math.fabs(mapped_pog.x() - C.x()))

            FG = d/D

            IM_velocity_current = FG * IM_VELOCITY_MAX

            IM_velocity_current_x = IM_velocity_current * math.cos(theta)

            IM_velocity_current_y = IM_velocity_current * math.sin(theta)

            if d > PAN_CENTER_RADIUS:
                if mapped_pog.x() > C.x() and mapped_pog.y() > C.y():
                    self.translate_roi(Direction.UPPER_RIGHT, IM_velocity_current_y)

                elif mapped_pog.x() > C.x() and mapped_pog.y() < C.y():
                    self.translate_roi(Direction.LOWER_RIGHT, IM_velocity_current_y)

                elif mapped_pog.x() < C.x() and mapped_pog.y() > C.y():
                    self.translate_roi(Direction.UPPER_LEFT, IM_velocity_current_y)

                elif mapped_pog.x() < C.x() and mapped_pog.y() < C.y():
                    self.translate_roi(Direction.LOWER_LEFT, IM_velocity_current_y)

                elif mapped_pog.y() > C.y():
                    self.translate_roi(Direction.UP, IM_velocity_current_y)

                elif mapped_pog.y() < C.y():
                    self.translate_roi(Direction.DOWN, IM_velocity_current_y)

                elif mapped_pog.x() > C.x():
                    self.translate_roi(Direction.RIGHT, IM_velocity_current_x)

                elif mapped_pog.y() < C.y():
                    self.translate_roi(Direction.LEFT, IM_velocity_current_x)

            self.set_view_to_roi_and_pad()

    def define_pan_areas(self):

        image_rect = QtCore.QRect(self.detail_view_roi.pos().x(), self.detail_view_roi.pos().y(),
                                  self.detail_view_roi.size().x(), self.detail_view_roi.size().y())

        x1 = image_rect.x()
        x2 = image_rect.x() + image_rect.width() * 0.25
        x3 = image_rect.x() + image_rect.width() * 0.75

        y1 = image_rect.y() + image_rect.height() * 0.75
        y2 = image_rect.y() + image_rect.height() * 0.25
        y3 = image_rect.y()

        w25 = image_rect.width() * 0.25
        w50 = image_rect.width() * 0.50
        h25 = image_rect.height() * 0.25
        h50 = image_rect.height() * 0.50

        self.upper_left_rect = QtCore.QRect(x1 - 100, y1, w25 + 100, h25 + 100)
        self.upper_rect = QtCore.QRect(x2, y1, w50, h25 + 100)
        self.upper_right_rect = QtCore.QRect(x3, y1, w25 + 100, h25 + 100)
        self.left_rect = QtCore.QRect(x1 - 100, y2, w25 + 100, h50)
        self.lower_left_rect = QtCore.QRect(x1 - 100, y3 - 100, w25 + 100, h25 + 100)
        self.lower_rect = QtCore.QRect(x2, y3 - 100, w50, h25 + 100)
        self.lower_right_rect = QtCore.QRect(x3, y3 - 100, w25 + 100, h25 + 100)
        self.right_rect = QtCore.QRect(x3, y2, w25 + 100, h50)

    def locate_panning_direction(self, pos):
        pos = QtCore.QPoint(pos.x(), pos.y())

        if self.upper_left_rect.contains(pos):
            return Direction.UPPER_LEFT

        elif self.upper_rect.contains(pos):
            return Direction.UP

        elif self.upper_right_rect.contains(pos):
            return Direction.UPPER_RIGHT

        elif self.left_rect.contains(pos):
            return Direction.LEFT

        elif self.right_rect.contains(pos):
            return Direction.RIGHT

        elif self.lower_left_rect.contains(pos):
            return Direction.LOWER_LEFT

        elif self.lower_rect.contains(pos):
            return Direction.DOWN

        elif self.lower_right_rect.contains(pos):
            return Direction.LOWER_RIGHT

    def auto_pan_using_pan_regions(self):
        self.define_pan_areas()
        pos = self.image_view_box.mapSceneToView(self.POG)
        direction = self.locate_panning_direction(QtCore.QPoint(pos.x(), pos.y()))

        x = self.zoom_percentage_value_horizontal
        scale = (-1 * (13*(pow(x, 3))/60000000) + (47*(pow(x, 2))/200000) - ((79*x)/750) + (142/5)) / 5

        self.translate_roi(direction, scale)
        self.set_view_to_roi_and_pad()

    # </editor-fold>

    def keyPressEvent(self, event):
        super(GazeSupported, self).keyPressEvent(event)

        key = event.key()

        # if not event.isAutoRepeat():
        #     if key == QtCore.Qt.Key_M:
        #         print "gaze thread started"
        #         self.process_start_gaze_tracker()

        if key == QtCore.Qt.Key_0:
            try:
                print "input held monitor: " + str(self.input_held_monitor_timer_thread.isActive())
            except:
                print "input held monitor: False"

    def keypress_W(self):

        if self.gaze_activation_held:
            if self.system_state == SystemState.FULLSCALE:
                print "zoom in"
                self.set_roi_in_center_of_pog()

                self.zoom_in()
                self.set_system_state(SystemState.ZOOM_A)
                # self.instructions_label_item.setText(self.system_state)

            elif self.system_state == SystemState.PRE_ZOOM_B or self.system_state == SystemState.PRE_ZOOM_A:
                pass
                # self.minimize_roi_dimensions(False)

            elif self.system_state == SystemState.ZOOM_B or self.system_state == SystemState.ZOOM_A:
                print "zoom in"
                self.zoom_timeout = time.time()
                self.pan_the_zoom = True
                self.zoom_in()

                self.last_action = Actions.ZOOM_IN
        else:
            super(GazeSupported, self).keypress_W()


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
        print("Add data: " + str(value))
        self.myFig.addData(value)


def dataSendLoop(addData_callbackFunc):
    # Setup the signal-slot mechanism.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)

    while True:
        time.sleep(0.1)
        mySrc.data_signal.emit(plot_data)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPLICATION_TITLE_MANUAL_BASED)

    width, height = GetSystemMetrics(0), GetSystemMetrics(1)

    main = GazeSupported(width, height)
    main.show()

    print "Screen Dimensions = "
    print win32gui.GetWindowRect(GetForegroundWindow())

    sys.exit(app.exec_())
