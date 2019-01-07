import sys
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
import pyqtgraph as pg
import cv2
import numpy as np
from numpy import array
import time
import pickle
import os
import math
from scipy import misc

sys.path.insert(0, '../interactions')
from gaze_supported import GazeSupported

sys.path.insert(0, '../globals')
from common_constants import *
from us_machine_comm_protocol import *

sys.path.insert(0, '../components')
from us_communication_comp import USCommunicationThread
1

class USMachineClientInterface(GazeSupported):
    def __init__(self, screen_width_input, screen_height_input, interaction, home_directory):

        self.stream_image = STREAM_IMAGE

        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#

        self.results_home_dir = home_directory
        self.current_system_state_icon = None
        self.interaction = interaction

        # <editor-fold desc="user study variables">
        self.user_study_state = ClinicalStudyState.DEMO
        self.is_task_running = False
        self.task_time_counter = None
        self.task_pog_log = []
        self.total_logs = []
        self.total_number_of_started_tasks = 0
        self.user_number = 0
        self.time_elapsed = 0
        self.key_logs = []

        self.location_header = None
        self.file_name_header = None

        # </editor-fold>

        # <editor-fold desc="gui variables">
        self.is_gaze_icon_set = False

        self.tools_dock = None
        self.captured_images_dock = None
        self.task_state_dock = None

        self.task_state_widget = None
        self.captured_images_widget = None
        self.tools_widget = None

        self.task_state_view_box = None
        self.captured_images_view_box = None
        self.system_state_image_view_box = None
        self.gaze_activation_image_view_box = None
        self.system_state_image_item = None

        self.task_state_image_item = None
        self.captured_images_item = None
        self.gaze_image_item = None

        self.task_running_image = None
        self.system_state_resize_icon = None
        self.system_state_reposition_icon = None
        self.gaze_icon = None

        # </editor-fold>

        # <editor-fold desc="parameters variables">
        self.gain_value = 0
        self.frequency_value = 0
        self.focus_value = 0
        self.freeze_state = 0
        self.depth_value = 0
        # </editor-fold>

        # <editor-fold desc="threading variables">
        self.us_image_thread = None
        # </editor-fold>

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#
        super(USMachineClientInterface, self).__init__(screen_width_input, screen_height_input)
        if self.stream_image:
            self.read_parameters()
        self.setup_captured_images_widget()
        self.setup_task_state_widget()
        self.load_tools_icons()
        self.setup_tools_widget()

        if LOG_RESULTS_FLAG:
            self.create_experiment_logging_directories()

    # <editor-fold desc="GUI functions">
    def setup_docks_layout(self):
        self.dock_area = DockArea()
        self.setCentralWidget(self.dock_area)

        # define docks
        self.image_dock = Dock(DOCK_NAME_CENTRAL_IMAGE, size=(1092, 700))
        self.context_dock = Dock(DOCK_NAME_CONTEXT_IMAGE, size=(200, 200))
        self.tools_dock = Dock(DOCK_NAME_TOOLS, size=(200, 200))
        self.captured_images_dock = Dock(DOCK_NAME_CAPTURED_IMAGES, size=(700, 200))
        self.task_state_dock = Dock(DOCK_NAME_TASK_STATE, size=(50, 200))

        # hide docks' title bars
        self.image_dock.hideTitleBar()
        self.context_dock.hideTitleBar()
        self.tools_dock.hideTitleBar()
        self.captured_images_dock.hideTitleBar()
        self.task_state_dock.hideTitleBar()

        # add docks
        self.dock_area.addDock(self.image_dock, 'top')
        self.dock_area.addDock(self.context_dock, 'bottom', self.image_dock)
        self.dock_area.addDock(self.captured_images_dock, 'right', self.context_dock)
        self.dock_area.addDock(self.task_state_dock, 'right', self.captured_images_dock)
        self.dock_area.addDock(self.tools_dock, 'right', self.task_state_dock)

    def setup_task_state_widget(self):
        self.task_state_widget = pg.GraphicsLayoutWidget()

        self.task_state_view_box = self.task_state_widget.addViewBox(row=0, col=0)
        self.task_state_image_item = pg.ImageItem()

        self.task_running_image = cv2.imread(OTHER_IMAGE_LOCATION + TASK_RUNNING_IMAGE)
        self.task_running_image = array(self.task_running_image)
        self.task_running_image = self.task_running_image.astype('float64')

        self.task_state_image_item.setImage(self.task_running_image, opacity=0)
        self.task_state_view_box.addItem(self.task_state_image_item)
        self.task_state_dock.addWidget(self.task_state_widget)

    def setup_instructions_widget(self):
        pass

    def setup_gaze_indicators(self):
        pass

    def setup_captured_images_widget(self):
        self.captured_images_widget = pg.GraphicsLayoutWidget()
        self.captured_images_view_box = []
        self.captured_images_item = []

        for i in range(0, 2):
            for j in range(0, 4):
                self.captured_images_view_box.append(self.captured_images_widget.addViewBox(row=i, col=j))
                self.captured_images_item.append(pg.ImageItem())

        for index in range(0, MAX_NUM_DISPLAYED_CAPTURED_IMAGES):
            self.captured_images_view_box[index].addItem(self.captured_images_item[index])
            self.captured_images_view_box[index].setMouseEnabled(False, False)
            self.captured_images_view_box[index].setAspectLocked(True)

        self.captured_images_dock.addWidget(self.captured_images_widget)

    # </editor-fold>

    # <editor-fold desc="values setup functions">
    def read_parameters(self):
        if self.stream_image:
            self.depth_value = self.us_image_thread.param_command_get_depth()
            self.gain_value = self.us_image_thread.param_command_get_gain()
            self.focus_value = self.us_image_thread.param_command_get_focus()
            self.frequency_value = self.us_image_thread.param_command_get_frequency()

    def setup_tools_widget(self):
        self.tools_widget = pg.GraphicsLayoutWidget()

        self.system_state_image_view_box = self.tools_widget.addViewBox(row=0, col=0)
        self.gaze_activation_image_view_box = self.tools_widget.addViewBox(row=1, col=0)

        self.load_tools_icons()
        self.system_state_image_item = pg.ImageItem()
        self.system_state_image_view_box.addItem(self.system_state_image_item)
        self.system_state_image_view_box.setAspectLocked(True)
        self.system_state_image_view_box.setMouseEnabled(False, False)

        self.gaze_image_item = pg.ImageItem()
        self.gaze_activation_image_view_box.addItem(self.gaze_image_item)
        self.gaze_activation_image_view_box.setAspectLocked(True)
        self.gaze_activation_image_view_box.setMouseEnabled(False, False)

        self.update_system_state_image()

        self.tools_dock.addWidget(self.tools_widget)

    def update_system_state_image(self):
        if self.system_state == SystemState.FULLSCALE:
            if self.current_system_state_icon != SystemState.FULLSCALE:
                self.system_state_image_item.clear()
                self.current_system_state_icon = SystemState.FULLSCALE
        elif self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.PRE_ZOOM_A:
            if self.current_system_state_icon != SystemState.ZOOM_A:
                self.system_state_image_item.setImage(self.system_state_reposition_icon)
                self.current_system_state_icon = SystemState.ZOOM_A
        elif self.system_state == SystemState.ZOOM_B or self.system_state == SystemState.PRE_ZOOM_B:
            if self.current_system_state_icon != SystemState.ZOOM_B:
                self.system_state_image_item.setImage(self.system_state_resize_icon)
                self.current_system_state_icon = SystemState.ZOOM_B

    def load_tools_icons(self):

        self.system_state_resize_icon = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + SYSTEM_STATE_RESIZE_ICON_IMAGE)
        self.system_state_resize_icon = cv2.cvtColor(self.system_state_resize_icon, cv2.COLOR_BGR2RGB)
        self.system_state_resize_icon = array(self.system_state_resize_icon)
        self.system_state_resize_icon = self.system_state_resize_icon.astype('float64')
        self.system_state_resize_icon = np.rot90(self.system_state_resize_icon)
        self.system_state_resize_icon = np.rot90(self.system_state_resize_icon)
        self.system_state_resize_icon = np.rot90(self.system_state_resize_icon)

        self.system_state_reposition_icon = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION +
                                                       SYSTEM_STATE_REPOSITION_ICON_IMAGE)
        self.system_state_reposition_icon = cv2.cvtColor(self.system_state_reposition_icon, cv2.COLOR_BGR2RGB)
        self.system_state_reposition_icon = array(self.system_state_reposition_icon)
        self.system_state_reposition_icon = self.system_state_reposition_icon.astype('float64')
        self.system_state_reposition_icon = np.rot90(self.system_state_reposition_icon)
        self.system_state_reposition_icon = np.rot90(self.system_state_reposition_icon)
        self.system_state_reposition_icon = np.rot90(self.system_state_reposition_icon)

        self.gaze_icon = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + EYE_GAZE_ICON_IMAGE)
        self.gaze_icon = cv2.cvtColor(self.gaze_icon, cv2.COLOR_BGR2RGB)
        self.gaze_icon = array(self.gaze_icon)
        self.gaze_icon = self.gaze_icon.astype('float64')
        self.gaze_icon = np.rot90(self.gaze_icon)
        self.gaze_icon = np.rot90(self.gaze_icon)
        self.gaze_icon = np.rot90(self.gaze_icon)

    # </editor-fold>

    # <editor-fold desc="threading functions">

    def create_threads(self):
        super(USMachineClientInterface, self).create_threads()

        if self.stream_image:
            self.us_image_thread = USCommunicationThread()
            self.us_image_thread.data.connect(self.callback_us_image_receive)

    def start_threads(self):
        super(USMachineClientInterface, self).start_threads()
        if self.stream_image:
            self.thread_start_us_image_receive()

    def thread_start_us_image_receive(self):
        self.us_image_thread.start()

    # </editor-fold>

    # <editor-fold desc="callback functions">

    def callback_arduino_update(self, info):
        super(USMachineClientInterface, self).callback_arduino_update(info)

        if self.is_task_running:
            self.key_logs.append((info, time.time() - self.task_time_counter))

    def callback_us_image_receive(self, info):

        try:
            self.image = info

            self.image_width = self.image.shape[0]
            self.image_height = self.image.shape[1]

            self.image_item.setImage(self.image, autoDownsample=True)
            self.image_item.setRect(QtCore.QRectF(0.0, 0.0, self.image_width, self.image_height))
            self.context_image_item.setImage(self.image, autoDownsample=True)
        except:
            pass

    def callback_values_update(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).callback_values_update()
        else:
            super(USMachineClientInterface, self).callback_values_update()

        # <editor-fold desc="update UI">
        self.update_system_state_image()
        # </editor-fold>

    def callback_input_held_monitor(self):
        super(USMachineClientInterface, self).callback_input_held_monitor()

        if self.gaze_activation_held or self.gaze_activation_pressed:
            if not self.is_gaze_icon_set:
                self.gaze_image_item.setImage(self.gaze_icon)
                self.is_gaze_icon_set = True
        else:
            if self.is_gaze_icon_set:
                self.gaze_image_item.clear()
                self.is_gaze_icon_set = False

    def callback_update_POG(self, info):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).callback_update_POG(info)
        else:
            super(USMachineClientInterface, self).callback_update_POG(info)

        # <editor-fold desc="logging-related">

        gaze_point = self.image_view_box.mapSceneToView(self.POG)
        center_roi = QtCore.QPoint(self.roi.pos().x() + (self.roi.size().x() / 2),
                                   self.roi.pos().y() + (self.roi.size().y() / 2))

        distance_from_gaze_to_roi_center = math.sqrt(math.pow((gaze_point.x() - center_roi.x()), 2) +
                                                     math.pow(gaze_point.y() - center_roi.y(), 2))

        if self.is_task_running:
            pog_x_y_d_t_v_dist = [self.POG.x(), self.POG.y(), self.fixation_duration,
                                  time.time() - self.task_time_counter,
                                  self.valid_POG_flag, distance_from_gaze_to_roi_center]
            self.task_pog_log.append(pog_x_y_d_t_v_dist)

        # </editor-fold>

    # </editor-fold>

    # <editor-fold desc="user study functions">
    def set_user_study_state(self, state):

        if state == ClinicalStudyState.DEMO:
            self.user_study_state = ClinicalStudyState.DEMO

        elif state == ClinicalStudyState.PHANTOM:
            self.user_study_state = ClinicalStudyState.PHANTOM

        elif state == ClinicalStudyState.PATIENT:
            self.user_study_state = ClinicalStudyState.PATIENT

        self.total_logs = []
        self.total_number_of_started_tasks = 0
        self.update_save_to_file_strings()

        print "User study state: " + self.user_study_state

    def go_to_next_user_study_state(self):

        if self.user_study_state == ClinicalStudyState.DEMO:
            self.set_user_study_state(ClinicalStudyState.PHANTOM)

        elif self.user_study_state == ClinicalStudyState.PHANTOM:
            self.set_user_study_state(ClinicalStudyState.PATIENT)

    def go_to_prev_user_study_state(self):

        if self.user_study_state == ClinicalStudyState.PATIENT:
            self.set_user_study_state(ClinicalStudyState.PHANTOM)

        elif self.user_study_state == ClinicalStudyState.PHANTOM:
            self.set_user_study_state(ClinicalStudyState.DEMO)

    def start_task(self):
        self.task_state_image_item.setImage(self.task_running_image, opacity=1)
        self.is_task_running = True
        self.task_time_counter = time.time()
        self.total_number_of_started_tasks += 1
        self.task_pog_log = []
        self.key_logs = []
        self.set_roi_to_default_pos_and_size()

        print "task started"

    def end_task(self):
        self.task_state_image_item.setImage(self.task_running_image, opacity=0)
        self.is_task_running = False
        self.time_elapsed = time.time() - self.task_time_counter

        self.read_parameters()

        if LOG_RESULTS_FLAG:
            self.log_data()

        self.task_pog_log = []
        self.key_logs = []

        print "task ended"

    def log_data(self):
        location = self.location_header + "/"

        log_item = {'user study state': self.user_study_state,
                    'time elapsed': self.time_elapsed,
                    'task number': self.total_number_of_started_tasks,
                    'roi': QtCore.QRect(self.roi.pos().x(), self.roi.pos().y(),
                                        self.roi.size().x(), self.roi.size().y()),
                    'key logs': self.key_logs,
                    'image parameters': (self.depth_value, self.gain_value, self.focus_value, self.frequency_value)
                    }

        print log_item
        self.total_logs.append(log_item)

        self.log_list_to_file(self.total_logs, location, self.file_name_header + FILE_NAME_TOTAL_LOGS)

        self.log_list_to_file(self.task_pog_log, location,
                              self.file_name_header + str(self.total_number_of_started_tasks) + "_" + FILE_NAME_POG_LOG)

        image_file_name = self.file_name_header + str(len(self.captured_images)) + EXTENSION_CAPTURED_IMAGE

        captured_image = self.roi.getArrayRegion(self.image, self.image_item)
        self.save_image_to_file(captured_image, location, image_file_name)

    def create_experiment_logging_directories(self):
        directories = os.listdir(self.results_home_dir)

        i = 0
        while True:
            if DIR_USER + str(i) in directories:
                i += 1
                self.user_number = i
            else:
                break

        user_dir = self.results_home_dir + DIR_USER + str(i)
        subdirectories = [user_dir + '/' + ClinicalStudyState.DEMO,
                          user_dir + '/' + ClinicalStudyState.PHANTOM,
                          user_dir + '/' + ClinicalStudyState.PATIENT]

        os.mkdir(user_dir)

        for i in range(0, len(subdirectories)):
            os.mkdir(subdirectories[i])

        self.update_save_to_file_strings()

    def update_save_to_file_strings(self):
        self.location_header = self.results_home_dir + DIR_USER + str(self.user_number) + "/" + \
                               self.user_study_state + "/"

        self.file_name_header = self.user_study_state + "_"

    @staticmethod
    def log_list_to_file(input_list, directory, file_name):

        with open(directory + file_name, 'wb') as f:
            pickle.dump(input_list, f)

    @staticmethod
    def save_image_to_file(image, location, file_name):
        image = np.rot90(image)
        misc.imsave(location + file_name, image)

    # </editor-fold>

    def keypress_R(self):
        self.last_action = Actions.CAPTURE

        if self.is_task_running:
            self.end_task()

        # <editor-fold desc="display captured image">
        captured_image = self.roi.getArrayRegion(self.image, self.image_item)
        self.captured_images.append(captured_image)

        index = len(self.captured_images) - 1
        if index < MAX_NUM_DISPLAYED_CAPTURED_IMAGES:
            self.captured_images_item[index].setImage(self.captured_images[index])
        else:
            images_to_shift = []
            for i in range(0, MAX_NUM_DISPLAYED_CAPTURED_IMAGES):
                images_to_shift.append(self.captured_images_item[i].image)

            for i in range(0, MAX_NUM_DISPLAYED_CAPTURED_IMAGES - 1):
                self.captured_images_item[i].setImage(images_to_shift[i + 1])

            self.captured_images_item[MAX_NUM_DISPLAYED_CAPTURED_IMAGES - 1].setImage(self.captured_images[index])
        # </editor-fold>

        self.keypress_Q()

        # start next task automatically
        self.start_task()

    def keyPressEvent(self, event):
        super(USMachineClientInterface, self).keyPressEvent(event)

        key = event.key()

        if key == QtCore.Qt.Key_0:
            print "gaze active: " + str(self.is_gaze_active_in_fullscale_and_zoom_modes)

        if key == QtCore.Qt.Key_1:
            self.start_task()

        if key == QtCore.Qt.Key_2:
            self.end_task()

        if key == QtCore.Qt.Key_8:
            self.go_to_next_user_study_state()

        if key == QtCore.Qt.Key_9:
            self.go_to_prev_user_study_state()

        if key == QtCore.Qt.Key_Z:
            self.us_image_thread.param_command_increase_depth()
            # self.depth_value = self.us_image_thread.param_command_get_depth()

        if key == QtCore.Qt.Key_X:
            self.us_image_thread.param_command_decrease_depth()
            # self.depth_value = self.us_image_thread.param_command_get_depth()

        if key == QtCore.Qt.Key_C:
            self.us_image_thread.param_command_get_depth()

        if key == QtCore.Qt.Key_V:
            self.us_image_thread.param_command_increase_gain()
            # self.gain_value = self.us_image_thread.param_command_get_gain()

        if key == QtCore.Qt.Key_B:
            self.us_image_thread.param_command_decrease_gain()
            # self.gain_value = self.us_image_thread.param_command_get_gain()

        if key == QtCore.Qt.Key_N:
            self.us_image_thread.param_command_get_gain()

        if key == QtCore.Qt.Key_M:
            self.us_image_thread.param_command_increase_frequency()
            # self.frequency_value = self.us_image_thread.param_command_get_frequency()

        if key == QtCore.Qt.Key_L:
            self.us_image_thread.param_command_decrease_frequency()
            # self.frequency_value = self.us_image_thread.param_command_get_frequency()

        if key == QtCore.Qt.Key_K:
            self.us_image_thread.param_command_get_frequency()

        if key == QtCore.Qt.Key_J:
            self.us_image_thread.param_command_increase_focus()
            # self.focus_value = self.us_image_thread.param_command_get_focus()

        if key == QtCore.Qt.Key_H:
            self.us_image_thread.param_command_decrease_focus()
            # self.focus_value = self.us_image_thread.param_command_get_focus()

        if key == QtCore.Qt.Key_G:
            self.us_image_thread.param_command_get_focus()

        if key == QtCore.Qt.Key_F:
            self.us_image_thread.param_command_toggle_freeze()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPLICATION_TITLE_US_MACHINE_CLIENT_INTERFACE)

    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    main = USMachineClientInterface(width, height, Interaction.GAZE_SUPPORTED, DIR_CLINICAL_STUDY_HOME)
    main.show()

    sys.exit(app.exec_())
