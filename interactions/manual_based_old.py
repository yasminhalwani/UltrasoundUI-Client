import win32api
import cv2
from win32api import GetSystemMetrics
import sys

import pyqtgraph as pg
from PIL import Image
from numpy import array
import numpy as np
import time
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *

sys.path.insert(0, '../components')
from arduino_comp import *
from gaze_tracker_comp import *
from cursor_comp import *

sys.path.insert(0, '../globals')
from common_constants import *
from states import *


class ManualBased(QtGui.QMainWindow):
    def __init__(self, screen_width_input, screen_height_input):
        super(ManualBased, self).__init__()

        self.fps = None
        self.lastTime = 0.0

        self.cursor_monitor_timer = 0

        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#

        # <editor-fold desc="state variables">
        self.interface = Interaction.MANUAL_BASED
        self.system_state = SystemState.FULLSCALE
        self.roi_state = ROIState.NONE
        self.padding_state = PaddingType.NONE
        self.current_central_image_type = CentralImageType.TRAINING_2
        self.last_action = Actions.NONE
        self.indicators_state = POGValidity.VALID
        self.indicators_state_prev = POGValidity.INVALID_LONG
        self.calibration_stage = CalibrationStage.NONE
        # </editor-fold>

        # <editor-fold desc="counter and flags variables">
        self.gaze_activation_press_elapsed_time = 0
        self.gaze_activation_press_start_time = 0
        self.no_gaze_counter = 0
        self.cursor_moved_after_state_change_flag = False
        self.latch_flag = False
        # </editor-fold>

        # <editor-fold desc="gaze variables">
        self.POG = QtCore.QPoint(0, 0)
        self.converted_cursor_pos = QtCore.QPoint(0, 0)
        self.unfiltered_POG = QtCore.QPoint(0, 0)
        self.fixation_duration = 0
        self.valid_POG_flag = False
        self.allow_gaze_pan_after_zoom = False
        # self.pog_queue = multiprocessing.Queue()
        # </editor-fold>

        # <editor-fold desc="window variables">
        self.screen_width = screen_width_input
        self.screen_height = screen_height_input
        # </editor-fold>

        # <editor-fold desc="image variables">
        self.image = None
        self.image_width = 0
        self.image_height = 0
        self.captured_images = None
        # </editor-fold>

        # <editor-fold desc="mouse variables">
        self.mouse_pos_history = None
        self.mouse_pos_history_max_size = None
        self.current_trackball_x = 0
        self.current_trackball_y = 0
        self.prev_trackball_x = 0
        self.prev_trackball_y = 0
        self.last_cursor_move_time = 0
        self.time_since_last_cursor_movement = 0
        self.prev_time_since_last_cursor_movement = 0
        self.continuous_cursor_movement_counter = 0

        self.t = 0
        # </editor-fold>

        # <editor-fold desc="hardware interface variables">
        self.gaze_activation_pressed = False
        self.gaze_activation_held = False
        self.last_action = None
        # </editor-fold>

        # <editor-fold desc="image parameters variables">
        self.depth_level = None
        self.max_roi_size = None
        self.zoom_percentage_value_horizontal = 0
        self.zoom_percentage_value_vertical = 0
        self.max_zoom_percentage_horizontal = 0
        self.max_zoom_percentage_vertical = 0
        # </editor-fold>

        # # <editor-fold desc="gui variables">
        # GUI variables
        # -- docks
        self.dock_area = None
        self.image_dock = None
        self.context_dock = None
        self.instructions_dock = None
        self.indicators_dock = None

        # -- image layout
        self.central_image_file_name = None
        self.central_image_file_location = None
        self.image_layout_widget = None
        self.image_view_box = None
        self.image_item = None
        self.roi = None
        self.min_roi_width = None
        self.min_roi_height = None
        self.default_roi_height = None
        self.default_roi_width = None
        self.last_roi_before_reset = None
        self.detail_view_roi = None
        self.roi_pen_current = None
        self.roi_signal_timer = None
        self.roi_pen_normal = None
        self.roi_pen_signal = None

        # -- context image layout
        self.context_image_layout_widget = None
        self.context_image_view_box = None
        self.context_image_item = None
        self.context_roi = None

        # -- indicators graphics and layout
        self.indicators_widget = None
        self.indicators_view_box = None
        self.indicators_graph_item = None
        self.indicators_pen = None
        self.indicators_brush_valid = None
        self.indicators_brush_invalid_1 = None
        self.indicators_brush_invalid_2 = None
        self.indicators_brush_invalid_3 = None
        self.indicators_pos = None
        self.indicators_adj = None
        self.indicators_symbols = None

        # -- instructions dock layout
        self.instructions_widget = None
        self.instructions_layout_view_box = None
        self.instructions_label_item = None

        # -- padding layout
        self.padding_view_box = None
        self.padding_image = None
        self.left_padding = None
        self.right_padding = None
        self.top_padding = None
        self.bottom_padding = None
        self.left_padding_id = None
        self.up_padding_id = None

        # -- max panning signal layout
        self.max_pan_signal_image = None
        self.max_pan_signal_view_box = None
        self.max_pan_signal_item = None
        self.max_pan_signal_id = None
        self.max_pan_signal_width = None
        self.max_pan_timer = None

        # </editor-fold>

        # <editor-fold desc="threads variables">
        # Threads

        # Image update thread
        self.values_update_thread = None

        # Cursor monitor thread
        self.trackball_thread = None

        # Arduino interface thread
        self.arduino_interface_thread = None

        # Gaze tracker thread
        self.gaze_tracker_process = None
        # </editor-fold>

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#
        self.load_default_image_parameters()
        self.load_central_image()
        self.setup_gui()
        self.setup_gaze_indicators()
        self.create_threads()
        self.start_threads()

    def load_default_image_parameters(self):
        if self.current_central_image_type == CentralImageType.DEMO:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_DEMO

        elif self.current_central_image_type == CentralImageType.OLD:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_OLD

        elif self.current_central_image_type == CentralImageType.TRAINING_1:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_TRAINING_1

        elif self.current_central_image_type == CentralImageType.TRAINING_2:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_TRAINING_2

        elif self.current_central_image_type == CentralImageType.RECORDED_1:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_RECORDED_1

        elif self.current_central_image_type == CentralImageType.RECORDED_2:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_RECORDED_2

        self.central_image_file_name = STATIC_IMAGE_DEPTH_LEVEL_1

        self.depth_level = DepthLevels.DEPTH_LEVEL_7

        self.captured_images = []

    # <editor-fold desc="gui functions">

    def update_central_image(self):
        self.image_item.setImage(self.image)
        self.image_item.setRect(QtCore.QRectF(0.0, 0.0, self.image_width, self.image_height))
        self.context_image_item.setImage(self.image)
        self.image_view_box.autoRange(padding=0)

        if self.system_state == SystemState.FULLSCALE or self.system_state == SystemState.ZOOM_A \
                or self.system_state == SystemState.ZOOM_B:
            self.set_view_to_roi_and_pad()

    def load_central_image(self):

        # <editor-fold desc="depth settings">
        if self.depth_level is DepthLevels.DEPTH_LEVEL_1:
            self.central_image_file_name = STATIC_IMAGE_DEPTH_LEVEL_1

        if self.depth_level is DepthLevels.DEPTH_LEVEL_2:
            self.central_image_file_name = STATIC_IMAGE_DEPTH_LEVEL_2

        if self.depth_level is DepthLevels.DEPTH_LEVEL_3:
            self.central_image_file_name = STATIC_IMAGE_DEPTH_LEVEL_3

        if self.depth_level is DepthLevels.DEPTH_LEVEL_4:
            self.central_image_file_name = STATIC_IMAGE_DEPTH_LEVEL_4

        if self.depth_level is DepthLevels.DEPTH_LEVEL_5:
            self.central_image_file_name = STATIC_IMAGE_DEPTH_LEVEL_5

        if self.depth_level is DepthLevels.DEPTH_LEVEL_6:
            self.central_image_file_name = STATIC_IMAGE_DEPTH_LEVEL_6

        if self.depth_level is DepthLevels.DEPTH_LEVEL_7:
            self.central_image_file_name = STATIC_IMAGE_DEPTH_LEVEL_7
        # </editor-fold>

        # <editor-fold desc="load image">
        if self.current_central_image_type == CentralImageType.DEMO:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_DEMO

        elif self.current_central_image_type == CentralImageType.OLD:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_OLD

        elif self.current_central_image_type == CentralImageType.TRAINING_1:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_TRAINING_1

        elif self.current_central_image_type == CentralImageType.TRAINING_2:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_TRAINING_2

        elif self.current_central_image_type == CentralImageType.RECORDED_1:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_RECORDED_1

        elif self.current_central_image_type == CentralImageType.RECORDED_2:
            self.central_image_file_location = CENTRAL_IMAGE_LOCATION_RECORDED_2

        image = cv2.imread(self.central_image_file_location + self.central_image_file_name, flags=0)
        # import pdb; pdb.set_trace()

        print self.central_image_file_location + self.central_image_file_name

        # h = image.shape[0]
        # w = image.shape[1]
        # </editor-fold>

        image = array(image)
        image = image.astype(np.int16)
        image = np.rot90(image)
        image = np.rot90(image)
        image = np.rot90(image)

        self.image = image

        self.image_width = self.image.shape[0]
        self.image_height = self.image.shape[1]

    def setup_gaze_indicators(self):
        # -- setup widgets and containers
        self.indicators_widget = pg.GraphicsLayoutWidget()
        self.indicators_view_box = self.indicators_widget.addViewBox(row=1, col=1)
        self.indicators_view_box.setAspectLocked()
        self.indicators_graph_item = pg.GraphItem()
        self.indicators_view_box.addItem(self.indicators_graph_item)
        self.indicators_view_box.setMouseEnabled(False, False)
        # -- manage graphics
        color = QtGui.QColor(QtCore.Qt.darkRed)
        self.indicators_pen = QtGui.QPen()
        self.indicators_brush_valid = QtGui.QBrush()
        self.indicators_brush_invalid_1 = QtGui.QBrush(color.darker(150))
        self.indicators_brush_invalid_2 = QtGui.QBrush(color.darker(100))
        self.indicators_brush_invalid_3 = QtGui.QBrush(color.darker(50))
        self.indicators_pos = np.array([[0, 0], [5, 0]])
        self.indicators_adj = np.array([[0, 1], [1, 0]])
        self.indicators_symbols = ['o', 'o']
        self.indicators_graph_item.setData(pos=self.indicators_pos,
                                           adj=self.indicators_adj,
                                           size=1,
                                           symbol=self.indicators_symbols,
                                           pxMode=False,
                                           symbolBrush=self.indicators_brush_invalid_1,
                                           symbolPen=self.indicators_pen)
        self.indicators_dock.addWidget(self.indicators_widget)
        self.indicators_graph_item.hide()

    def load_padding_image(self):
        self.padding_image = Image.open(PADDING_BLANK_IMAGE_LOCATION)
        self.padding_image = array(self.padding_image)
        self.padding_image = self.padding_image.astype(np.int8)

    def load_max_pan_signal_image(self):
        self.max_pan_signal_image = Image.open(MAX_PAN_SIGNAL_IMAGE_LOCATION)
        self.max_pan_signal_image = array(self.max_pan_signal_image)
        self.max_pan_signal_image = self.max_pan_signal_image.astype(np.int16)

    def get_image_center_wrt_scene(self):
        x = self.image_width / 2
        y = self.image_height / 2
        pos = QtCore.QPoint(x, y)
        pos = self.image_item.mapToScene(pos.x(), pos.y())
        return pos

    def get_roi_center_wrt_scene(self):
        size = self.roi.size()
        pos = self.roi.pos()
        center = QtCore.QPoint(pos.x() + size.x() / 2, pos.y() + size.y() / 2)
        x = center.x()
        y = center.y()
        pos = QtCore.QPoint(x, y)
        pos = self.roi.mapToScene(pos.x(), pos.y())
        return pos

    def get_image_center_wrt_view(self):
        x = self.image_width / 2
        y = self.image_height / 2
        pos = QtCore.QPoint(x, y)
        pos = self.image_view_box.mapFromItemToView(self.image_item, QtCore.QPoint(pos.x(), pos.y()))
        return pos

    def get_roi_center_wrt_view(self):
        size = self.roi.size()
        pos = self.roi.pos()
        center = QtCore.QPoint(pos.x() + size.x() / 2, pos.y() + size.y() / 2)
        x = center.x()
        y = center.y()
        pos = QtCore.QPoint(x, y)
        pos = self.image_view_box.mapFromItemToView(self.image_item, QtCore.QPoint(pos.x(), pos.y()))
        return pos

    def setup_gui(self):
        self.showFullScreen()
        win32api.ShowCursor(False)

        self.setup_docks_layout()
        self.setup_image_layout()
        self.setup_roi_layout()
        self.setup_detail_view_roi()
        self.setup_context_image_layout()
        self.setup_instructions_widget()
        self.setup_padding_base_layout()
        self.setup_max_pan_signal_base_layout()
        self.reset_roi()
        self.set_view_to_roi_and_pad()

        self.image_view_box.sigRangeChanged.connect(self.callback_image_view_box)
        self.mouse_pos_history = []
        self.mouse_pos_history_max_size = CURSOR_POSITION_HISTORY_MAX_SIZE
        self.max_roi_size = self.roi.size()

        self.max_zoom_percentage_horizontal = (self.max_roi_size.x() / self.min_roi_width) * 100
        self.max_zoom_percentage_vertical = (self.max_roi_size.y() / self.min_roi_height) * 100

    def setup_docks_layout(self):
        self.dock_area = DockArea()
        self.setCentralWidget(self.dock_area)

        # define docks
        self.image_dock = Dock(DOCK_NAME_CENTRAL_IMAGE, size=(1092, 700))
        self.context_dock = Dock(DOCK_NAME_CONTEXT_IMAGE, size=(364, 200))
        self.instructions_dock = Dock(DOCK_NAME_INSTRUCTIONS, size=(364, 200))
        self.indicators_dock = Dock(DOCK_NAME_GAZE_INDICATORS, size=(728, 200))

        # hide docks' title bars
        self.image_dock.hideTitleBar()
        self.context_dock.hideTitleBar()
        self.instructions_dock.hideTitleBar()
        self.indicators_dock.hideTitleBar()

        # add docks
        self.dock_area.addDock(self.image_dock, 'top')
        self.dock_area.addDock(self.context_dock, 'bottom', self.image_dock)
        self.dock_area.addDock(self.instructions_dock, 'right', self.context_dock)
        self.dock_area.addDock(self.indicators_dock, 'left', self.instructions_dock)

    def setup_image_layout(self):
        self.image_layout_widget = pg.GraphicsLayoutWidget()
        self.image_view_box = self.image_layout_widget.addViewBox(row=1, col=1)
        self.image_item = pg.ImageItem()

        self.image_view_box.addItem(self.image_item)
        self.image_item.setImage(self.image)
        self.image_item.setRect(QtCore.QRectF(0.0, 0.0, self.image_width, self.image_height))
        self.image_view_box.setAspectLocked(True)

        self.image_dock.addWidget(self.image_layout_widget)
        self.image_view_box.setMouseMode(pg.ViewBox.PanMode)

        self.image_view_box.autoRange(padding=0)
        self.image_view_box.setMouseEnabled(False, False)

    def setup_roi_layout(self):
        # self.min_roi_width = self.image_width * 0.125
        # self.min_roi_height = self.image_height * 0.125

        self.min_roi_width = self.image_width * 0.08
        self.min_roi_height = self.image_height * 0.08

        self.default_roi_height = self.image_height * 0.45
        # self.default_roi_width = self.image_width * 0.45
        self.default_roi_width = self.image_height * 0.45

        self.roi = pg.RectROI([0, 0], [self.default_roi_width, self.default_roi_height], movable=False,
                              maxBounds=QtCore.QRectF(0, 0, self.image_width, self.image_height))
        self.image_view_box.addItem(self.roi)

        self.roi_pen_normal = pg.mkPen('y', width=1, style=QtCore.Qt.SolidLine)
        self.roi_pen_signal = pg.mkPen('r', width=1, style=QtCore.Qt.SolidLine)
        self.roi_pen_current = self.roi_pen_normal

        self.roi.setPen(self.roi_pen_current)
        self.roi_signal_timer = time.time()

        self.roi.removeHandle(0)
        self.roi.hide()

    def setup_detail_view_roi(self):
        self.detail_view_roi = pg.RectROI([0, 0], [self.image_width, self.image_height], movable=False,
                                          maxBounds=QtCore.QRectF(0, 0, self.image_width, self.image_height))
        self.detail_view_roi.setPen(pg.mkPen('r', width=2, style=QtCore.Qt.SolidLine))
        self.image_view_box.addItem(self.detail_view_roi)

    def setup_context_image_layout(self):
        self.context_image_layout_widget = pg.GraphicsLayoutWidget()
        self.context_image_view_box = self.context_image_layout_widget.addViewBox(row=1, col=1)
        self.context_image_item = pg.ImageItem()

        self.context_image_view_box.addItem(self.context_image_item)
        self.context_image_item.setImage(self.image)
        self.context_image_item.setRect(QtCore.QRectF(0.0, 0.0, self.image_width, self.image_height))
        self.context_image_view_box.setAspectLocked(True)
        self.context_image_view_box.setMouseEnabled(False, False)

        self.context_dock.addWidget(self.context_image_layout_widget)

        # -- manage ROI displayed over the context image
        self.context_roi = pg.RectROI([0, 0], [self.default_roi_width, self.default_roi_height], pen=(0, 5),
                                      maxBounds=QtCore.QRectF(0, 0, self.image_width, self.image_height))
        self.context_image_view_box.addItem(self.context_roi)

        if self.system_state == SystemState.FULLSCALE:
            # self.context_image_item.hide()
            pass

    def setup_instructions_widget(self):
        self.instructions_widget = pg.GraphicsLayoutWidget()
        self.instructions_layout_view_box = self.instructions_widget.addViewBox(row=1, col=1)
        self.instructions_label_item = pg.LabelItem()
        self.instructions_layout_view_box.addItem(self.instructions_label_item)
        self.instructions_label_item.setText(self.system_state, color='CCFF00', size='4pt', bold=True, italic=False)
        self.instructions_layout_view_box.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
        self.instructions_layout_view_box.setAspectLocked(lock=True)

        self.instructions_layout_view_box.invertY()
        self.instructions_layout_view_box.setMouseEnabled(False, False)

        self.instructions_dock.addWidget(self.instructions_widget)

    def setup_padding_base_layout(self):
        image = Image.open(TRANSPARENT_BASE_IMAGE_LOCATION)
        image = array(image)
        image = image.astype(np.int8)

        self.padding_view_box = self.image_layout_widget.addViewBox(row=1, col=1)
        transparent_background = pg.ImageItem()

        self.padding_view_box.addItem(transparent_background)
        transparent_background.setImage(image, opacity=0.0)
        transparent_background.setRect(QtCore.QRectF(0.0, 0.0, self.image_width, self.image_height))
        self.padding_view_box.setAspectLocked(True)
        self.padding_view_box.setMouseEnabled(False, False)

        self.load_padding_image()
        self.padding_view_box.autoRange(padding=0)

    def setup_max_pan_signal_base_layout(self):
        image = Image.open(TRANSPARENT_BASE_IMAGE_LOCATION)
        image = array(image)
        image = image.astype(np.int8)

        self.max_pan_signal_view_box = self.image_layout_widget.addViewBox(row=1, col=1)
        transparent_background = pg.ImageItem()

        self.max_pan_signal_view_box.addItem(transparent_background)
        transparent_background.setImage(image, opacity=0.0)
        transparent_background.setRect(QtCore.QRectF(0.0, 0.0, self.image_width, self.image_height))
        self.max_pan_signal_view_box.setAspectLocked(True)
        self.max_pan_signal_view_box.setMouseEnabled(False, False)

        self.load_max_pan_signal_image()
        self.max_pan_signal_view_box.autoRange(padding=0)

        self.max_pan_signal_width = 1
        self.max_pan_timer = time.time()

    # </editor-fold>

    # <editor-fold desc="callback functions">

    def callback_update_POG(self, info):

        try:
            # info = self.pog_queue.get_nowait()

            # receive data from gaze thread
            xpos = float(info['FPOGX']) * self.screen_width
            ypos = float(info['FPOGY']) * self.screen_height
            is_valid = int(info['FPOGV'])

            self.fixation_duration = info['FPOGD']

            if is_valid:

                # filter out the spikes
                d = math.sqrt(
                    (math.pow(self.unfiltered_POG.x() - xpos, 2)) + (math.pow(self.unfiltered_POG.y() - ypos, 2)))
                if d < 600:
                    self.POG = QtCore.QPoint(xpos, ypos)
                self.unfiltered_POG = QtCore.QPoint(xpos, ypos)

                self.valid_POG_flag = True
            else:
                self.valid_POG_flag = False
        except:
            pass

        # update eye gaze validity indicators
        # self.update_validity_indicators(is_valid)

    def callback_arduino_update(self, info):

        event = None
        key = None
        if info == HwInterface.ZOOM_PRESS:
            key = QtCore.Qt.Key_Q

        elif info == HwInterface.ZOOM_CW:
            key = QtCore.Qt.Key_W

        elif info == HwInterface.ZOOM_CCW:
            key = QtCore.Qt.Key_E

        elif info == HwInterface.CAPTURE_PRESS:
            key = QtCore.Qt.Key_R

        elif info == HwInterface.TOP_PRESS:
            if not self.gaze_activation_pressed:
                self.gaze_activation_pressed = True
                self.gaze_activation_press_start_time = time.time()
            else:
                self.gaze_activation_pressed = False
                if not self.gaze_activation_held:
                    key = QtCore.Qt.Key_T
                else:
                    self.gaze_activation_held = False

        elif info == HwInterface.CALIBRATE_PRESS:
            key = QtCore.Qt.Key_Y

        elif info == HwInterface.RIGHT_PRESS:
            key = QtCore.Qt.Key_U

        elif info == HwInterface.DEPTH_CW:
            key = QtCore.Qt.Key_Z

        elif info == HwInterface.DEPTH_CCW:
            key = QtCore.Qt.Key_X

        elif info == HwInterface.DEPTH_PRESS:
            key = QtCore.Qt.Key_C

        elif info == HwInterface.GAIN_CW:
            key = QtCore.Qt.Key_V

        elif info == HwInterface.GAIN_CCW:
            key = QtCore.Qt.Key_B

        elif info == HwInterface.GAIN_PRESS:
            key = QtCore.Qt.Key_N

        elif info == HwInterface.FREQUENCY_CW:
            key = QtCore.Qt.Key_M

        elif info == HwInterface.FREQUENCY_CCW:
            key = QtCore.Qt.Key_L

        elif info == HwInterface.FREQUENCY_PRESS:
            key = QtCore.Qt.Key_K

        elif info == HwInterface.FOCUS_CW:
            key = QtCore.Qt.Key_J

        elif info == HwInterface.FOCUS_CCW:
            key = QtCore.Qt.Key_H

        elif info == HwInterface.FOCUS_PRESS:
            key = QtCore.Qt.Key_G

        elif info == HwInterface.FREEZE_PRESS:
            key = QtCore.Qt.Key_F

        if key is not None:
            event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, key, QtCore.Qt.KeyboardModifiers())

        if event is not None:
            self.keyPressEvent(event)

    def callback_main_timer_thread(self):

        # self.callback_update_POG()

        self.callback_cursor_monitor()

        self.callback_values_update()

    def callback_cursor_monitor(self):

        if APPLY_CURSOR_LAG:
            if time.time() - self.cursor_monitor_timer >= CURSOR_LAG:
                run_script = True
            else:
                run_script = False
        else:
            run_script = True

        if run_script:
            roi_translation_scale = DEFAULT_ROI_TRANSLATION_SCALE
            direction = Direction.NONE
            direction_set_flag = False

            has_performed_action = False

            right_edge = self.screen_width - 50
            left_edge = 50
            upper_edge = 50
            lower_edge = self.screen_height - 50

            if self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B or \
                    self.system_state == SystemState.PRE_ZOOM_A or self.system_state == SystemState.PRE_ZOOM_B:

                # (x, y) = info

                flags, hcursor, (x, y) = win32gui.GetCursorInfo()

                self.current_trackball_x = x
                self.current_trackball_y = y

                if self.current_trackball_y != self.prev_trackball_y or \
                        self.current_trackball_x != self.prev_trackball_x:

                    self.last_cursor_move_time = time.time()

                    # <editor-fold desc="detect hitting edge of screen">
                    # if x <= left_edge and y <= upper_edge:  # up left
                    #
                    #     win32api.SetCursorPos((int(right_edge), int(lower_edge)))
                    #     self.mouse_pos_history = []
                    #     direction = Direction.UPPER_LEFT
                    #     direction_set_flag = True
                    #
                    # elif x >= right_edge and y <= upper_edge:  # up right
                    #
                    #     win32api.SetCursorPos((int(left_edge), int(lower_edge)))
                    #     self.mouse_pos_history = []
                    #     direction = Direction.UPPER_RIGHT
                    #     direction_set_flag = True
                    #
                    # elif x <= left_edge and y >= lower_edge:  # down left
                    #
                    #     win32api.SetCursorPos((int(right_edge), int(upper_edge)))
                    #     self.mouse_pos_history = []
                    #     direction = Direction.LOWER_LEFT
                    #     direction_set_flag = True
                    #
                    # elif x >= right_edge and y >= lower_edge:  # down right
                    #
                    #     win32api.SetCursorPos((int(left_edge), int(upper_edge)))
                    #     self.mouse_pos_history = []
                    #     direction = Direction.LOWER_RIGHT
                    #     direction_set_flag = True

                    if x > right_edge:  # right

                        direction = Direction.RIGHT
                        self.perform_translation_or_resize(direction, roi_translation_scale)
                        has_performed_action = True
                        win32api.SetCursorPos((int(left_edge), int(y)))
                        self.mouse_pos_history = []
                        direction_set_flag = True

                    elif x < left_edge:  # left

                        direction = Direction.LEFT
                        self.perform_translation_or_resize(direction, roi_translation_scale)
                        has_performed_action = True
                        win32api.SetCursorPos((int(right_edge), int(y)))
                        self.mouse_pos_history = []
                        direction_set_flag = True

                    elif y > lower_edge:  # down

                        direction = Direction.DOWN
                        self.perform_translation_or_resize(direction, roi_translation_scale)
                        has_performed_action = True
                        win32api.SetCursorPos((int(x), int(upper_edge)))
                        self.mouse_pos_history = []
                        direction_set_flag = True

                    elif y < upper_edge:  # up

                        direction = Direction.UP
                        self.perform_translation_or_resize(direction, roi_translation_scale)
                        has_performed_action = True
                        win32api.SetCursorPos((int(x), int(lower_edge)))
                        self.mouse_pos_history = []
                        direction_set_flag = True

                    # </editor-fold>

                    # <editor-fold desc="detect movement direction">
                    if not direction_set_flag and not has_performed_action:
                        flags, hcursor, (x, y) = win32gui.GetCursorInfo()

                        self.current_trackball_x = x
                        self.current_trackball_y = y

                        if x > self.prev_trackball_x and y == self.prev_trackball_y:
                            direction = Direction.RIGHT
                            direction_set_flag = True

                        elif x < self.prev_trackball_x and y == self.prev_trackball_y:
                            direction = Direction.LEFT
                            direction_set_flag = True

                        elif y > self.prev_trackball_y and x == self.prev_trackball_x:
                            direction = Direction.DOWN
                            direction_set_flag = True

                        elif y < self.prev_trackball_y and x == self.prev_trackball_x:
                            direction = Direction.UP
                            direction_set_flag = True

                        self.prev_trackball_y = self.current_trackball_y
                        self.prev_trackball_x = self.current_trackball_x
                        self.perform_translation_or_resize(direction, roi_translation_scale)

                    # </editor-fold>

                    self.mouse_pos_history.append((x, y))
                    if len(self.mouse_pos_history) > self.mouse_pos_history_max_size:
                        self.mouse_pos_history.pop(0)

                else:
                    self.time_since_last_cursor_movement = time.time() - self.last_cursor_move_time

            self.prev_time_since_last_cursor_movement = self.time_since_last_cursor_movement

            if APPLY_CURSOR_LAG:
                self.cursor_monitor_timer = time.time()

    def perform_translation_or_resize(self, direction, roi_translation_scale):
        # <editor-fold desc="perform reposition/resize action">
        if self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
            if self.system_state == SystemState.ZOOM_A:
                self.translate_roi(direction, roi_translation_scale)

            elif self.system_state == SystemState.ZOOM_B:
                self.resize_roi(direction)

            self.set_view_to_roi_and_pad()

        elif self.system_state == SystemState.PRE_ZOOM_A:
            self.translate_roi(direction, roi_translation_scale)

        elif self.system_state == SystemState.PRE_ZOOM_B:
            self.resize_roi(direction)

        # </editor-fold>

    def callback_image_view_box(self):
        self.context_roi.setPos(self.roi.pos())
        self.context_roi.setSize(self.roi.size())

    def callback_values_update(self):

        # set the color of roi to normal after 0.2 s if changed
        if self.roi_pen_current is self.roi_pen_signal:
            if time.time() - self.roi_signal_timer >= 0.2:
                self.roi_pen_current = self.roi_pen_normal

                self.update_roi_color()

        # update max pan signal
        if time.time() - self.max_pan_timer >= 0.2:
            self.remove_max_pan_signal()

        # update the zoom percentage value
        self.zoom_percentage_value_horizontal = (self.max_roi_size.x() / self.detail_view_roi.size().x()) * 100
        self.zoom_percentage_value_vertical = (self.max_roi_size.y() / self.detail_view_roi.size().y()) * 100

    # </editor-fold>

    # <editor-fold desc="threading functions">

    def create_threads(self):
        self.trackball_thread = QtCore.QTimer()
        self.connect(self.trackball_thread, QtCore.SIGNAL('timeout()'), self.callback_main_timer_thread)

        self.arduino_interface_thread = ArduinoThread()
        self.arduino_interface_thread.data.connect(self.callback_arduino_update)

    def start_threads(self):
        self.thread_start_cursor_monitor()
        self.thread_start_arduino_interface()

    def process_start_gaze_tracker(self):
        # self.gaze_tracker_process = GazeTrackerProcess()
        # self.gaze_tracker_process.set_values([GazeTrackerDataEnableMessages.POG_FIX], self.pog_queue)
        # self.gaze_tracker_process.start()
        self.gaze_tracker_process = GazeTrackerThread([GazeTrackerDataEnableMessages.POG_FIX,
                                                      GazeTrackerDataEnableMessages.CURSOR])
        self.gaze_tracker_process.pog.connect(self.callback_update_POG)
        self.gaze_tracker_process.start()

    def thread_start_cursor_monitor(self):
        self.trackball_thread.start(0)
        self.cursor_monitor_timer = time.time()

    def thread_start_arduino_interface(self):
        self.arduino_interface_thread.start(QtCore.QThread.TimeCriticalPriority)

    def thread_start_values_update(self):
        self.values_update_thread.start(0)

    # </editor-fold>

    # <editor-fold desc="feedback functions">
    def update_validity_indicators(self, is_valid):
        if not is_valid:
            self.no_gaze_counter += 1
            if INDICATORS_THRESHOLD_1 < self.no_gaze_counter <= INDICATORS_THRESHOLD_2 - 1:
                self.indicators_state = POGValidity.INVALID_SHORT
            elif INDICATORS_THRESHOLD_2 < self.no_gaze_counter <= INDICATORS_THRESHOLD_3 - 1:
                self.indicators_state = POGValidity.INVALID_INTERMEDIATE
            elif self.no_gaze_counter > INDICATORS_THRESHOLD_3:
                self.indicators_state = POGValidity.INVALID_LONG
        else:
            self.no_gaze_counter = 0
            self.indicators_state = POGValidity.VALID
        if self.indicators_state != self.indicators_state_prev:
            self.indicators_state_prev = self.indicators_state
            if self.indicators_state == POGValidity.VALID:
                self.indicators_graph_item.setData(pos=self.indicators_pos,
                                                   adj=self.indicators_adj,
                                                   size=1,
                                                   symbol=self.indicators_symbols,
                                                   pxMode=False,
                                                   symbolBrush=self.indicators_brush_valid,
                                                   symbolPen=self.indicators_pen)
                self.indicators_graph_item.hide()
            elif self.indicators_state == POGValidity.INVALID_SHORT:
                self.indicators_graph_item.setData(pos=self.indicators_pos,
                                                   adj=self.indicators_adj,
                                                   size=1,
                                                   symbol=self.indicators_symbols,
                                                   pxMode=False,
                                                   symbolBrush=self.indicators_brush_invalid_1,
                                                   symbolPen=self.indicators_pen)
                self.indicators_graph_item.show()
            elif self.indicators_state == POGValidity.INVALID_INTERMEDIATE:
                self.indicators_graph_item.setData(pos=self.indicators_pos,
                                                   adj=self.indicators_adj,
                                                   size=1,
                                                   symbol=self.indicators_symbols,
                                                   pxMode=False,
                                                   symbolBrush=self.indicators_brush_invalid_2,
                                                   symbolPen=self.indicators_pen)
                self.indicators_graph_item.show()
            elif self.indicators_state == POGValidity.INVALID_LONG:
                self.indicators_graph_item.setData(pos=self.indicators_pos,
                                                   adj=self.indicators_adj,
                                                   size=1,
                                                   symbol=self.indicators_symbols,
                                                   pxMode=False,
                                                   symbolBrush=self.indicators_brush_invalid_3,
                                                   symbolPen=self.indicators_pen)
                self.indicators_graph_item.show()

    # </editor-fold>

    # <editor-fold desc="depth functions">

    def increase_depth(self):

        if self.depth_level == DepthLevels.DEPTH_LEVEL_1:
            self.depth_level = DepthLevels.DEPTH_LEVEL_2

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_2:
            self.depth_level = DepthLevels.DEPTH_LEVEL_3

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_3:
            self.depth_level = DepthLevels.DEPTH_LEVEL_4

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_4:
            self.depth_level = DepthLevels.DEPTH_LEVEL_5

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_5:
            self.depth_level = DepthLevels.DEPTH_LEVEL_6

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_6:
            self.depth_level = DepthLevels.DEPTH_LEVEL_7

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_7:
            print "maximum depth level reached"

        self.load_central_image()
        self.update_central_image()

    def decrease_depth(self):

        if self.depth_level == DepthLevels.DEPTH_LEVEL_7:
            self.depth_level = DepthLevels.DEPTH_LEVEL_6

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_6:
            self.depth_level = DepthLevels.DEPTH_LEVEL_5

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_5:
            self.depth_level = DepthLevels.DEPTH_LEVEL_4

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_4:
            self.depth_level = DepthLevels.DEPTH_LEVEL_3

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_3:
            self.depth_level = DepthLevels.DEPTH_LEVEL_2

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_2:
            self.depth_level = DepthLevels.DEPTH_LEVEL_1

        elif self.depth_level == DepthLevels.DEPTH_LEVEL_1:
            print "minimum depth level reached"

        self.load_central_image()
        self.update_central_image()

    # </editor-fold>

    # <editor-fold desc="zoom functions">

    def go_to_pre_zoom(self):

        if self.last_roi_before_reset is not None:
            if self.system_state == SystemState.FULLSCALE:
                self.roi.setPos((self.last_roi_before_reset.x(), self.last_roi_before_reset.y()))
                self.roi.setSize((self.last_roi_before_reset.size().x(), self.last_roi_before_reset.size().y()))
                self.context_roi.setPos((self.last_roi_before_reset.x(), self.last_roi_before_reset.y()))
                self.context_roi.setSize((self.last_roi_before_reset.size().x(), self.last_roi_before_reset.size().y()))
        else:
            self.set_roi_to_default_pos_and_size()

        self.roi.show()
        self.context_roi.hide()

    def set_roi_to_default_pos_and_size(self):
        x = self.image_width / 2
        y = self.image_height / 2
        center_pos = QtCore.QPoint(int(x), int(y))
        center_pos = self.image_view_box.mapFromItemToView(self.image_item, center_pos)
        self.roi.setSize((self.default_roi_width, self.default_roi_height))
        self.set_roi_position_in_the_center_of(center_pos.x(), center_pos.y())

        self.last_roi_before_reset = self.roi

    def zoom_in(self):
        self.minimize_roi_dimensions(True)

    def minimize_roi_dimensions(self, confirm_zoom_flag):

        if self.roi.size().x() == self.image_width and self.roi.size().y() == self.image_height:
            if self.image_width >= self.image_height:
                new_width = self.image_height * ZOOM_RATIO
                new_height = self.image_height * ZOOM_RATIO
            else:
                new_width = self.image_width * ZOOM_RATIO
                new_height = self.image_width * ZOOM_RATIO
        else:
            new_width = self.roi.size().x() * ZOOM_RATIO
            new_height = self.roi.size().y() * ZOOM_RATIO

        x_shift = (new_width - self.roi.size().x()) / 2
        y_shift = (new_height - self.roi.size().y()) / 2

        if new_width > self.min_roi_width and new_height > self.min_roi_height:
            self.roi.setSize((new_width, new_height))
            self.roi.setPos((self.roi.pos().x() - x_shift, self.roi.pos().y() - y_shift))
            if confirm_zoom_flag:
                self.set_view_to_roi_and_pad()
            self.allow_gaze_pan_after_zoom = True
        else:
            print "max zoom reached"
            self.allow_gaze_pan_after_zoom = False

    def zoom_in_to_roi(self):
        # this function is typically used to zoom into a pre-set roi (from pre-zoom)
        if self.roi.size().x() > self.min_roi_width and self.roi.size().y() > self.min_roi_height:
            self.set_view_to_roi_and_pad()
            self.last_roi_before_reset = pg.RectROI([self.roi.pos().x(), self.roi.pos().y()],
                                                    [self.roi.size().x(), self.roi.size().y()])

    def zoom_out(self):
        self.maximize_roi_dimensions(True)

    def maximize_roi_dimensions(self, confirm_zoom_flag):
        new_width = self.roi.size().x() * 1 / ZOOM_RATIO
        new_height = self.roi.size().y() * 1 / ZOOM_RATIO

        x_shift = (new_width - self.roi.size().x()) / 2
        y_shift = (new_height - self.roi.size().y()) / 2

        new_x = self.roi.pos().x() - x_shift
        new_y = self.roi.pos().y() - y_shift

        if new_x < 0:
            new_x = 0

        if new_y < 0:
            new_y = 0

        if new_x + new_width > self.image_width:
            new_x = self.image_width - new_width

        if new_y + new_height > self.image_height:
            new_y = self.image_height - new_height

        if new_width < self.image_width or new_height < self.image_height:
            if new_x >= 0 and new_y >= 0:
                self.roi.setSize((new_width, new_height))
                self.roi.setPos((new_x, new_y))
                if confirm_zoom_flag:
                    self.set_view_to_roi_and_pad()
            else:
                if new_y >= 0:
                    self.roi.setSize((self.image_width, new_height))
                    self.roi.setPos((0, new_y))
                if new_x >= 0:
                    self.roi.setSize((new_width, self.image_height))
                    self.roi.setPos((new_x, 0))
                if confirm_zoom_flag:
                    self.set_view_to_roi_and_pad()
        else:
            self.reset_zoom()
            self.set_view_to_roi_and_pad()

        if self.last_action != Actions.ZOOM_OUT:

            if self.roi.size().x() < self.image_width * 0.75 and \
                        self.roi.size().y() < self.image_height * 0.75:
                self.last_roi_before_reset = pg.RectROI([self.roi.pos().x(), self.roi.pos().y()],
                                                        [self.roi.size().x(), self.roi.size().y()])

    def reset_zoom(self):
        if self.roi.size().x() < self.image_width * 0.75 and \
                        self.roi.size().y() < self.image_height * 0.75:
            self.last_roi_before_reset = pg.RectROI([self.roi.pos().x(), self.roi.pos().y()],
                                                    [self.roi.size().x(), self.roi.size().y()])

        self.reset_roi()
        self.image_view_box.autoRange(padding=0)

    # </editor-fold>

    # <editor-fold desc="max pan signal functions">

    def add_max_pan_signal(self, direction):

        # first, remove any existing signal
        self.remove_max_pan_signal()

        # then add a new one
        max_pan_signal_view_range = self.max_pan_signal_view_box.viewRange()
        view_range_width = max_pan_signal_view_range[0][1] - max_pan_signal_view_range[0][0]
        view_range_height = max_pan_signal_view_range[1][1] - max_pan_signal_view_range[1][0]

        self.max_pan_signal_item = pg.ImageItem()
        self.max_pan_signal_view_box.addItem(self.max_pan_signal_item)
        self.max_pan_signal_item.setImage(self.max_pan_signal_image)
        self.max_pan_signal_item.hide()

        if direction == Direction.UP:
            self.max_pan_signal_width = self.max_pan_signal_view_box.mapFromItemToView(self.detail_view_roi,
                                                                                       self.detail_view_roi.size()).x()

            self.max_pan_signal_width /= self.max_pan_signal_item.width() * 1

            self.max_pan_signal_item.scale(self.max_pan_signal_width, 1)

            self.max_pan_signal_item.setPos(max_pan_signal_view_range[0][0] +
                                            view_range_width / 2 -
                                            self.max_pan_signal_item.width() * self.max_pan_signal_width / 2,
                                            max_pan_signal_view_range[1][1] - self.max_pan_signal_item.height())

        elif direction == Direction.DOWN:
            self.max_pan_signal_width = self.max_pan_signal_view_box.mapFromItemToView(self.detail_view_roi,
                                                                                       self.detail_view_roi.size()).x()

            self.max_pan_signal_width /= self.max_pan_signal_item.width() * 1

            self.max_pan_signal_item.scale(self.max_pan_signal_width, 1)

            self.max_pan_signal_item.setPos(max_pan_signal_view_range[0][0] +
                                            view_range_width / 2 -
                                            self.max_pan_signal_item.width() * self.max_pan_signal_width / 2,
                                            max_pan_signal_view_range[1][0])

        elif direction == Direction.LEFT:

            self.max_pan_signal_width = self.max_pan_signal_view_box.mapFromItemToView(self.detail_view_roi,
                                                                                       self.detail_view_roi.size()).y()

            self.max_pan_signal_width /= self.max_pan_signal_item.height() * 1

            self.max_pan_signal_item.scale(1, self.max_pan_signal_width)

            self.max_pan_signal_item.setPos(max_pan_signal_view_range[0][0],
                                            max_pan_signal_view_range[1][0] +
                                            view_range_height / 2 -
                                            self.max_pan_signal_item.height() * self.max_pan_signal_width / 2)

        elif direction == Direction.RIGHT:
            self.max_pan_signal_width = self.max_pan_signal_view_box.mapFromItemToView(self.detail_view_roi,
                                                                                       self.detail_view_roi.size()).y()

            self.max_pan_signal_width /= self.max_pan_signal_item.height() * 1

            self.max_pan_signal_item.scale(1, self.max_pan_signal_width)

            self.max_pan_signal_item.setPos(max_pan_signal_view_range[0][1] - self.max_pan_signal_item.width(),
                                            max_pan_signal_view_range[1][0] +
                                            view_range_height / 2 -
                                            self.max_pan_signal_item.height() * self.max_pan_signal_width / 2)

        self.max_pan_signal_item.show()
        self.max_pan_signal_id = id(self.max_pan_signal_item)
        self.max_pan_timer = time.time()

    def remove_max_pan_signal(self):
        ids = []
        for i in self.max_pan_signal_view_box.addedItems[:]:
            ids.append(id(i))

        if self.max_pan_signal_id in ids:
            self.max_pan_signal_view_box.removeItem(self.max_pan_signal_item)

    # </editor-fold>

    # <editor-fold desc="padding functions">

    def set_view_to_roi_and_pad(self):

        # setting view to ROI
        rect = QtCore.QRectF(self.roi.pos().x(), self.roi.pos().y(), self.roi.size().x(), self.roi.size().y())
        self.image_view_box.setRange(rect, padding=0)
        self.padding_view_box.setRange(rect, padding=0)

        # adding the red border around the detail view
        self.detail_view_roi.setPos((rect.x(), rect.y()))
        self.detail_view_roi.setSize((rect.width(), rect.height()))

        # adding the padding if needed
        padding_type, view_range_width, view_range_height = self.check_for_padding_requirement()
        self.padding_state = padding_type

        if padding_type is not PaddingType.NONE and padding_type is not PaddingType.INVALID:
            self.add_padding(padding_type, view_range_width, view_range_height)

        # manage the visibility of the context view
        if self.roi.size().x() == self.image_width and self.roi.size().y() == self.image_height:
            self.detail_view_roi.hide()
            self.context_roi.hide()
        else:
            self.detail_view_roi.show()
            self.context_roi.show()

    def check_for_padding_requirement(self):
        view_range = self.image_view_box.viewRange()
        view_range_width = view_range[0][1] - view_range[0][0]
        view_range_height = view_range[1][1] - view_range[1][0]

        equal_heights = False
        equal_widths = False
        padding_type = PaddingType.NONE

        if int(self.roi.size().y()) == int(view_range_height):
            equal_heights = True
        if int(self.roi.size().x()) == int(view_range_width):
            equal_widths = True

        if equal_widths and not equal_heights:
            padding_type = PaddingType.UP_DOWN

        if equal_heights and not equal_widths:
            padding_type = PaddingType.LEFT_RIGHT

        if equal_heights and equal_widths:
            padding_type = PaddingType.NONE

        if not equal_heights and not equal_widths:
            padding_type = PaddingType.INVALID

        return padding_type, view_range_width, view_range_height

    def remove_existing_padding(self):
        direction = self.get_existing_padding_directions()

        if direction == Direction.LEFT:
            self.padding_view_box.removeItem(self.left_padding)
            self.padding_view_box.removeItem(self.right_padding)

        if direction == Direction.UP:
            self.padding_view_box.removeItem(self.top_padding)
            self.padding_view_box.removeItem(self.bottom_padding)

    def get_existing_padding_directions(self):

        ids = []
        for i in self.padding_view_box.addedItems[:]:
            ids.append(id(i))

        if self.left_padding_id in ids:
            return Direction.LEFT

        if self.up_padding_id in ids:
            return Direction.UP

        return Direction.NONE

    def add_padding(self, padding_type, view_range_width, view_range_height):

        self.remove_existing_padding()

        # then add the new one
        padding_view_range = self.padding_view_box.viewRange()

        if padding_type == PaddingType.LEFT_RIGHT:
            padding_width = (view_range_width - self.roi.size().x()) / 2

            self.right_padding = pg.ImageItem()
            self.padding_view_box.addItem(self.right_padding)
            self.right_padding.setImage(self.padding_image, opacity=PADDING_OPACITY)
            self.right_padding.setPos(self.roi.pos().x() + self.roi.size().x(), self.roi.pos().y())
            self.right_padding.scale(padding_width, view_range_height)
            self.right_padding.show()

            self.left_padding = pg.ImageItem()
            self.padding_view_box.addItem(self.left_padding)
            self.left_padding.setImage(self.padding_image, opacity=PADDING_OPACITY)
            self.left_padding.setPos(padding_view_range[0][0], padding_view_range[1][0])
            self.left_padding.scale(padding_width, view_range_height)
            self.left_padding.show()

            self.left_padding_id = id(self.left_padding)

        elif padding_type == PaddingType.UP_DOWN:
            padding_height = (view_range_height - self.roi.size().y()) / 2

            self.top_padding = pg.ImageItem()
            self.padding_view_box.addItem(self.top_padding)
            self.top_padding.setImage(self.padding_image, opacity=PADDING_OPACITY)
            self.top_padding.setPos(self.roi.pos().x(), self.roi.pos().y() + self.roi.size().y())
            self.top_padding.scale(view_range_width, padding_height)
            self.top_padding.show()

            self.bottom_padding = pg.ImageItem()
            self.padding_view_box.addItem(self.bottom_padding)
            self.bottom_padding.setImage(self.padding_image, opacity=PADDING_OPACITY)
            self.bottom_padding.setPos(padding_view_range[0][0], padding_view_range[1][0])
            self.bottom_padding.scale(view_range_width, padding_height)
            self.bottom_padding.show()

            self.up_padding_id = id(self.top_padding)

        elif padding_type == PaddingType.NONE:
            print MESSAGE_NO_PADDING_REQUIRED

        elif padding_type == PaddingType.INVALID:
            print MESSAGE_INVALID_PADDING

    # </editor-fold>

    # <editor-fold desc="roi functions">

    def update_roi_color(self):
        # update the color of roi, context_roi and detail_view_roi
        self.roi.setPen(self.roi_pen_current)
        self.context_roi.setPen(self.roi_pen_current)
        self.detail_view_roi.setPen(self.roi_pen_current)

    def signal_roi_max_or_min_size_reached(self):

        if self.roi_pen_current is self.roi_pen_normal:
            self.roi_signal_timer = time.time()
            self.roi_pen_current = self.roi_pen_signal

        self.roi.setPen(self.roi_pen_current)
        self.context_roi.setPen(self.roi_pen_current)
        self.detail_view_roi.setPen(self.roi_pen_current)

    def translate_roi(self, direction, scale):

        if direction != Direction.NONE:

            if self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
                if SCROLL_DIRECTION == ScrollDirection.NATURAL:
                    if direction == Direction.UP:
                        direction = Direction.DOWN
                    elif direction == Direction.DOWN:
                        direction = Direction.UP
                    elif direction == Direction.LEFT:
                        direction = Direction.RIGHT
                    elif direction == Direction.RIGHT:
                        direction = Direction.LEFT
                    elif direction == Direction.UPPER_LEFT:
                        direction = Direction.LOWER_RIGHT
                    elif direction == Direction.UPPER_RIGHT:
                        direction = Direction.LOWER_LEFT
                    elif direction == Direction.LOWER_LEFT:
                        direction = Direction.UPPER_RIGHT
                    elif direction == Direction.LOWER_RIGHT:
                        direction = Direction.UPPER_LEFT

            if direction == Direction.UP:
                if self.roi.pos().y() + self.roi.size().y() < self.image_height:
                    self.roi.setPos((self.roi.pos().x(), self.roi.pos().y() + DEFAULT_TRANSLATION_PX * scale))
                    self.remove_max_pan_signal()
                else:
                    self.roi.setPos((self.roi.pos().x(), self.image_height - self.roi.size().y()))
                    if self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
                        self.add_max_pan_signal(direction)

            elif direction == Direction.DOWN:
                if self.roi.pos().y() > 0:
                    self.roi.setPos((self.roi.pos().x(), self.roi.pos().y() - DEFAULT_TRANSLATION_PX * scale))
                    self.remove_max_pan_signal()
                else:
                    self.roi.setPos((self.roi.pos().x(), 0))
                    if self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
                        self.add_max_pan_signal(direction)

            elif direction == Direction.LEFT:
                if self.roi.pos().x() > 0:
                    self.roi.setPos((self.roi.pos().x() - DEFAULT_TRANSLATION_PX * scale, self.roi.pos().y()))
                    self.remove_max_pan_signal()
                else:
                    self.roi.setPos((0, self.roi.pos().y()))
                    if self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
                        self.add_max_pan_signal(direction)

            elif direction == Direction.RIGHT:
                if self.roi.pos().x() + self.roi.size().x() < self.image_width:
                    self.roi.setPos((self.roi.pos().x() + DEFAULT_TRANSLATION_PX * scale, self.roi.pos().y()))
                    self.remove_max_pan_signal()
                else:
                    self.roi.setPos((self.image_width - self.roi.size().x(), self.roi.pos().y()))
                    if self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
                        self.add_max_pan_signal(direction)

            elif direction == Direction.UPPER_LEFT:
                if self.roi.pos().y() + self.roi.size().y() < self.image_height:
                    if self.roi.pos().x() > 0:
                        self.roi.setPos((self.roi.pos().x() - DEFAULT_TRANSLATION_PX * scale,
                                         self.roi.pos().y() + DEFAULT_TRANSLATION_PX * scale))
                    else:
                        self.roi.setPos((0, self.roi.pos().y()))
                else:
                    self.roi.setPos((self.roi.pos().x(), self.image_height - self.roi.size().y()))

            elif direction == Direction.UPPER_RIGHT:
                if self.roi.pos().y() + self.roi.size().y() < self.image_height:
                    if self.roi.pos().x() + self.roi.size().x() < self.image_width:
                        self.roi.setPos((self.roi.pos().x() + DEFAULT_TRANSLATION_PX * scale,
                                         self.roi.pos().y() + DEFAULT_TRANSLATION_PX * scale))
                    else:
                        self.roi.setPos((self.image_width - self.roi.size().x(), self.roi.pos().y()))
                else:
                    self.roi.setPos((self.roi.pos().x(), self.image_height - self.roi.size().y()))

            elif direction == Direction.LOWER_LEFT:
                if self.roi.pos().y() > 0:
                    if self.roi.pos().x() > 0:
                        self.roi.setPos((self.roi.pos().x() - DEFAULT_TRANSLATION_PX * scale,
                                         self.roi.pos().y() - DEFAULT_TRANSLATION_PX * scale))
                    else:
                        self.roi.setPos((0, self.roi.pos().y()))
                else:
                    self.roi.setPos((self.roi.pos().x(), 0))

            elif direction == Direction.LOWER_RIGHT:
                if self.roi.pos().y() > 0:
                    if self.roi.pos().x() + self.roi.size().x() < self.image_width:
                        self.roi.setPos((self.roi.pos().x() + DEFAULT_TRANSLATION_PX * scale,
                                         self.roi.pos().y() - DEFAULT_TRANSLATION_PX * scale))
                    else:
                        self.roi.setPos((self.image_width - self.roi.size().x(), self.roi.pos().y()))
                else:
                    self.roi.setPos((self.roi.pos().x(), 0))

            self.context_roi.setPos((self.roi.pos().x(), self.roi.pos().y()))
            self.context_roi.setSize((self.roi.size().x(), self.roi.size().y()))

    def resize_roi(self, direction):

        resize_px = RESIZE_PX_MAX

        # resize_px_horizontal = \
        #     ((resize_px * self.detail_view_roi.size().x()) / self.max_roi_size.x())
        # resize_px_vertical = \
        #     (resize_px * self.detail_view_roi.size().y()) / self.max_roi_size.y()

        resize_px_horizontal = resize_px
        resize_px_vertical = resize_px

        new_height_up = self.roi.size().y() + resize_px_vertical
        new_y_up = self.roi.pos().y() - resize_px_vertical / 2

        new_height_down = self.roi.size().y() - resize_px_vertical
        new_y_down = self.roi.pos().y() + resize_px_vertical / 2

        new_width_left = self.roi.size().x() - resize_px_horizontal
        new_x_left = self.roi.pos().x() + resize_px_horizontal / 2

        new_width_right = self.roi.size().x() + resize_px_horizontal
        new_x_right = self.roi.pos().x() - resize_px_horizontal / 2

        if new_height_up + self.roi.pos().y() >= self.image_height:
            resize_px_vertical = self.image_height - (self.roi.size().y() + self.roi.pos().y())
            new_height_up = self.roi.size().y() + resize_px_vertical
            new_y_up = self.roi.pos().y() - resize_px_vertical / 2

        if new_y_up <= 0:
            resize_px_vertical = self.roi.pos().y()
            new_height_up = self.roi.size().y() + resize_px_vertical
            new_y_up = self.roi.pos().y() - resize_px_vertical / 2

        if new_width_right + self.roi.pos().x() >= self.image_width:
            resize_px_horizontal = self.image_width - (self.roi.size().x() + self.roi.pos().x())
            new_width_right = self.roi.size().x() + resize_px_horizontal
            new_x_right = self.roi.pos().x() - resize_px_horizontal / 2

        if new_x_right <= 0:
            resize_px_horizontal = self.roi.pos().x()
            new_width_right = self.roi.size().x() + resize_px_horizontal
            new_x_right = self.roi.pos().x() - resize_px_horizontal / 2

        if new_width_left <= self.min_roi_width:
            resize_px_horizontal = self.roi.size().x() - self.min_roi_width
            new_width_left = self.roi.size().x() - resize_px_horizontal
            new_x_left = self.roi.pos().x() + resize_px_horizontal / 2

        if new_height_down <= self.min_roi_height:
            resize_px_vertical = self.roi.size().y() - self.min_roi_height

            new_height_down = self.roi.size().y() - resize_px_vertical
            new_y_down = self.roi.pos().y() + resize_px_vertical / 2

        if direction != Direction.NONE:

            if direction == Direction.UP:

                if new_height_up <= self.image_height and \
                        new_y_up >= 0 and \
                        new_y_up + new_height_up < self.image_height and \
                        int(new_y_up) != int(self.roi.pos().y()):

                    self.roi.setSize((self.roi.size().x(), new_height_up))
                    self.roi.setPos((self.roi.pos().x(), new_y_up))
                else:
                    self.signal_roi_max_or_min_size_reached()

            elif direction == Direction.DOWN:

                if new_height_down > self.min_roi_height and self.roi.pos().y() >= 0:

                    self.roi.setSize((self.roi.size().x(), new_height_down))
                    self.roi.setPos((self.roi.pos().x(), new_y_down))
                else:
                    self.signal_roi_max_or_min_size_reached()

            if direction == Direction.LEFT:

                if new_width_left > self.min_roi_width and self.roi.pos().x() >= 0:

                        self.roi.setSize((new_width_left, self.roi.size().y()))
                        self.roi.setPos((new_x_left, self.roi.pos().y()))
                else:
                    self.signal_roi_max_or_min_size_reached()

            elif direction == Direction.RIGHT:
                if new_width_right <= self.image_width and \
                        new_x_right >= 0 and \
                        new_x_right + new_width_right < self.image_width and \
                        int(new_x_right) != int(self.roi.pos().x()):

                    self.roi.setSize((new_width_right, self.roi.size().y()))
                    self.roi.setPos((new_x_right, self.roi.pos().y()))
                else:
                    self.signal_roi_max_or_min_size_reached()

            elif direction == Direction.UPPER_LEFT:

                # up conditions
                if new_height_up <= self.image_height and \
                                new_y_up >= 0 and \
                                new_y_up + new_height_up < self.image_height and \
                                int(new_y_up) != int(self.roi.pos().y()):

                    # left conditions
                    if new_width_left > self.min_roi_width and self.roi.pos().x() >= 0:

                        self.roi.setSize((new_width_left, new_height_up))
                        self.roi.setPos((new_x_left, new_y_up))

            elif direction == Direction.UPPER_RIGHT:

                # up conditions
                if new_height_up <= self.image_height and \
                                new_y_up >= 0 and \
                                new_y_up + new_height_up < self.image_height and \
                                int(new_y_up) != int(self.roi.pos().y()):

                    # right conditions
                    if new_width_right <= self.image_width and \
                                    new_x_right >= 0 and \
                                    new_x_right + new_width_right < self.image_width and \
                                    int(new_x_right) != int(self.roi.pos().x()):

                        self.roi.setSize((new_width_right, new_height_up))
                        self.roi.setPos((new_x_right, new_y_up))

            elif direction == Direction.LOWER_LEFT:

                # down conditions
                if new_height_down > self.min_roi_height and self.roi.pos().y() >= 0:

                    # left conditions
                    if new_width_left > self.min_roi_width and self.roi.pos().x() >= 0:

                        self.roi.setSize((new_width_left, new_height_down))
                        self.roi.setPos((new_x_left, new_y_down))

            elif direction == Direction.LOWER_RIGHT:

                # down conditions
                if new_height_down > self.min_roi_height and self.roi.pos().y() >= 0:

                    # right conditions
                    if new_width_right <= self.image_width and \
                                    new_x_right >= 0 and \
                                    new_x_right + new_width_right < self.image_width and \
                                    int(new_x_right) != int(self.roi.pos().x()):

                        self.roi.setSize((new_width_right, new_height_down))
                        self.roi.setPos((new_x_right, new_y_down))

            if self.roi.size().y() + resize_px_vertical >= self.image_height \
                    and self.roi.size().x() + resize_px_horizontal >= self.image_width:
                self.keypress_Q()

            self.context_roi.setPos((self.roi.pos().x(), self.roi.pos().y()))
            self.context_roi.setSize((self.roi.size().x(), self.roi.size().y()))

    def set_roi_position_in_the_center_of(self, x, y):
        size = self.roi.size()
        new_x = x - (size.x() / 2)
        new_y = y - (size.y() / 2)

        self.roi.setPos([new_x, new_y])
        self.context_roi.setPos((self.roi.pos().x(), self.roi.pos().y()))
        self.context_roi.setSize((self.roi.size().x(), self.roi.size().y()))

    def reset_roi(self):
        x = self.image_width / 2
        y = self.image_height / 2
        center_pos = QtCore.QPoint(int(x), int(y))
        center_pos = self.image_view_box.mapFromItemToView(self.image_item, center_pos)
        self.roi.setSize((self.image_width, self.image_height))
        # self.roi.setSize((self.image_height, self.image_height))
        self.set_roi_position_in_the_center_of(center_pos.x(), center_pos.y())

        self.context_roi.setPos((self.roi.pos().x(), self.roi.pos().y()))
        self.context_roi.setSize((self.roi.size().x(), self.roi.size().y()))

    # </editor-fold>

    # <editor-fold desc="state functions">
    def set_system_state(self, state):
        self.system_state = state

        if state == SystemState.FULLSCALE:
            self.system_state = SystemState.FULLSCALE

        elif state == SystemState.PRE_ZOOM_A:
            self.system_state = SystemState.PRE_ZOOM_A

        elif state == SystemState.PRE_ZOOM_B:
            self.system_state = SystemState.PRE_ZOOM_B

        elif state == SystemState.ZOOM_A:
            self.system_state = SystemState.ZOOM_A

        elif state == SystemState.ZOOM_B:
            self.system_state = SystemState.ZOOM_B

    # </editor-fold>

    def keypress_W(self):

        if self.system_state == SystemState.FULLSCALE:
            print "zoom in"
            self.zoom_in()
            self.set_system_state(SystemState.ZOOM_A)
            # self.instructions_label_item.setText(self.system_state)

            self.last_action = Actions.ZOOM_IN

        elif self.system_state == SystemState.PRE_ZOOM_A or self.system_state == SystemState.PRE_ZOOM_B:
            self.minimize_roi_dimensions(False)

        elif self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
            print "zoom in"
            self.zoom_in()

            self.last_action = Actions.ZOOM_IN

    def keypress_Q(self):

        if self.system_state == SystemState.FULLSCALE:
            print "go to pre-zoom"
            self.go_to_pre_zoom()
            self.set_system_state(SystemState.PRE_ZOOM_A)
            # self.instructions_label_item.setText(self.system_state)

            self.last_action = Actions.PRE_ZOOM

        elif self.system_state == SystemState.PRE_ZOOM_A or self.system_state == SystemState.PRE_ZOOM_B:
            print "confirm zoom"
            self.zoom_in_to_roi()
            self.set_system_state(SystemState.ZOOM_A)
            # self.instructions_label_item.setText(self.system_state)
            self.roi.hide()
            self.context_roi.show()

            self.last_action = Actions.CONFIRM_ZOOM

        elif self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
            print "reset zoom"
            self.remove_max_pan_signal()
            self.reset_zoom()
            self.reset_roi()
            self.set_view_to_roi_and_pad()
            self.remove_existing_padding()
            self.set_system_state(SystemState.FULLSCALE)
            # self.instructions_label_item.setText(self.system_state)

            self.last_action = Actions.RESET_ZOOM

    def keypress_U(self):
        if self.system_state == SystemState.PRE_ZOOM_A or self.system_state == SystemState.PRE_ZOOM_B:
            print "toggle"
            if self.system_state == SystemState.PRE_ZOOM_A:
                self.set_system_state(SystemState.PRE_ZOOM_B)
            elif self.system_state == SystemState.PRE_ZOOM_B:
                self.set_system_state(SystemState.PRE_ZOOM_A)

            # self.instructions_label_item.setText(self.system_state)

            self.last_action = Actions.TOGGLE

        elif self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
            print "toggle"
            if self.system_state == SystemState.ZOOM_A:
                self.set_system_state(SystemState.ZOOM_B)
            elif self.system_state == SystemState.ZOOM_B:
                self.set_system_state(SystemState.ZOOM_A)
            # self.instructions_label_item.setText(self.system_state)

            self.last_action = Actions.TOGGLE

    def keypress_E(self):
        if self.system_state == SystemState.FULLSCALE:
            pass
        elif self.system_state == SystemState.PRE_ZOOM_A or self.system_state == SystemState.PRE_ZOOM_B:
            self.maximize_roi_dimensions(False)
        elif self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
            print "zoom out"
            self.zoom_out()
            if self.roi.size().x() == self.image_width and self.roi.size().y() == self.image_height:
                self.set_system_state(SystemState.FULLSCALE)
                # self.instructions_label_item.setText(self.system_state)

                self.last_action = Actions.ZOOM_OUT

    def keypress_R(self):
        print "capture: capture is saved only dusing user study runs"

    def keypress_Y(self):
        print "calibrate"

        if self.calibration_stage == CalibrationStage.NONE \
                or self.calibration_stage == CalibrationStage.HIDE_CALIBRATION:

            if self.calibration_stage == CalibrationStage.NONE:
                print "gaze thread started"
                self.process_start_gaze_tracker()

            self.gaze_tracker_process.show_tracker_display()
            self.calibration_stage = CalibrationStage.SHOW_TRACKER

        elif self.calibration_stage == CalibrationStage.SHOW_TRACKER:
            self.gaze_tracker_process.hide_tracker_display()
            self.calibration_stage = CalibrationStage.HIDE_TRACKER

        elif self.calibration_stage == CalibrationStage.HIDE_TRACKER:
            self.gaze_tracker_process.start_calibration()
            self.calibration_stage = CalibrationStage.SHOW_CALIBRATION

        elif self.calibration_stage == CalibrationStage.SHOW_CALIBRATION:
            self.gaze_tracker_process.exit_calibration()
            self.calibration_stage = CalibrationStage.HIDE_CALIBRATION

        self.last_action = Actions.CALIBRATE

    def keypress_T(self):
        print "eye"
        self.last_action = Actions.EYE

    def keypress_Z(self):
        print "increase depth"
        # TODO activate depth changing
        # self.increase_depth()
        self.last_action = Actions.INCREASE_DEPTH

    def keypress_X(self):
        print "decrease depth"
        # TODO activate depth changing
        # self.decrease_depth()
        self.last_action = Actions.DECREASE_DEPTH

    def keypress_J(self):
        print "increase focus depth"
        self.last_action = Actions.INCREASE_FOCUS

    def keypress_H(self):
        print "decrease focus depth"
        self.last_action = Actions.DECREASE_FOCUS

    def keyPressEvent(self, event):

        key = event.key()

        if key == QtCore.Qt.Key_9:
            self.reset_roi()

        if key == QtCore.Qt.Key_0:
            print "======================================"
            # print threading.activeC

            # self.create_threads()
            # self.start_threads()
            # print threading.activeCount()
            # print threading.currentThread()
            # print threading.enumerate()

            try:
                print "values update: " + str(self.values_update_thread.isActive())
            except:
                print "values update: False"

            try:
                print "trackball: " + str(self.trackball_thread.isActive())
            except:
                print "trackball: False"

            try:
                print "gaze tracker: " + str(self.gaze_tracker_process.isRunning())
            except:
                print "gaze tracker: False"

            try:
                print "arduino: " + str(self.arduino_interface_thread.isRunning())
            except:
                print "arduino: False"

        if key == QtCore.Qt.Key_T:
            self.keypress_T()

        if key == QtCore.Qt.Key_R:
            self.keypress_R()

        if key == QtCore.Qt.Key_Y:
            self.keypress_Y()

        if key == QtCore.Qt.Key_Z:
            self.keypress_Z()

        if key == QtCore.Qt.Key_X:
            self.keypress_X()

        if key == QtCore.Qt.Key_J:
            self.keypress_J()

        if key == QtCore.Qt.Key_H:
            self.keypress_H()

        if key == QtCore.Qt.Key_W:
            self.keypress_W()

        if key == QtCore.Qt.Key_Q:
            self.keypress_Q()

        if key == QtCore.Qt.Key_U:
            self.keypress_U()

        if key == QtCore.Qt.Key_E:
            self.keypress_E()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPLICATION_TITLE_MANUAL_BASED)

    width, height = GetSystemMetrics(0), GetSystemMetrics(1)

    main = ManualBased(width, height)
    main.show()

    sys.exit(app.exec_())
