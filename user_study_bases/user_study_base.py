import sys
import os
import time
import pickle
from scipy import misc
import cv2
import numpy as np
from numpy import array

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph.dockarea import *

sys.path.insert(0, '../interactions')
from gaze_supported import GazeSupported

sys.path.insert(0, '../globals')
from common_constants import *
from states import *
from arduino_communication_protocol import *
from tasks_roi import *


class UserStudyBase(GazeSupported):
    def __init__(self, screen_width_input, screen_height_input, interaction, home_directory):

        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#
        self.interaction = interaction
        self.results_home_dir = home_directory
        self.user_study_order = USER_STUDY_ORDER

        # <editor-fold desc="state variables">
        self.current_central_image_type = CentralImageType.NONE
        self.user_study_state = AbstractUserStudyState.MANUAL_PPT_TRAINING
        # </editor-fold>

        # <editor-fold desc="gui variables">
        self.current_system_state_icon = None

        # -- docks layout
        self.captured_images_dock = None
        self.parameters_dock = None
        self.instructions_dock = None
        self.timer_dock = None
        self.progress_dock = None

        # -- parameters layout
        self.parameters_widget = None
        self.parameters_layout_view_box = None
        self.parameters_label_item = None
        self.captured_images_widget = None

        # -- captured images layout
        self.captured_images_view_box = None
        self.captured_images_item = None

        # -- progress layout
        self.progress_widget = None
        self.progress_layout_view_box = None
        self.progress_text_item = None
        self.progress_label_item_text = None

        # -- timer layout
        self.timer_widget = None
        self.timer_layout_view_box = None
        self.timer_label_item = None

        # -- system state image
        self.system_state_image_view_box = None
        self.gaze_activation_image_view_box = None
        self.system_state_image_item = None
        self.gaze_image_item = None
        self.system_state_reposition_icon = None
        self.system_state_resize_icon = None
        self.gaze_icon = None
        self.is_gaze_icon_set = False

        # </editor-fold>

        # <editor-fold desc="parameters variables">
        self.depth_value = 0
        self.focus_value = 0
        self.frequency_value = 0
        self.gain_value = 0
        # </editor-fold>

        # <editor-fold desc="repetitiveness scoring variables">
        self.raw_key_input_log = []
        self.AR_log = []
        self.pre_FR_log = []
        self.LZW_compressed_log = []
        self.FR_log = []
        self.AR_score = 0
        self.FR_score = 0
        self.total_repetitiveness_score = 0

        self.raw_key_input_log_names = []
        self.AR_log_names = []
        self.pre_FR_log_names = []
        self.LZW_compressed_log_names = []
        self.FR_log_names = []

        self.prev_letter = None
        self.counted_cursor_movement = False
        self.double_press_PB = False

        self.raw_key_input_log_list = []
        self.AR_log_list = []
        self.pre_FR_log_list = []
        self.FR_log_list = []
        self.repetitiveness_scores_list = []

        self.last_cursor_sub = 0

        # </editor-fold>

        # <editor-fold desc="timer variables">
        self.current_timer = None
        self.list_times_elapsed = []
        self.counting_time = False
        self.time_limit = 0
        self.time_elapsed = 0
        # </editor-fold>

        # <editor-fold desc="POG variables">
        self.pog_log = []
        self.pog_x_y_d_time = None
        self.record_pog_flag = False
        # </editor-fold>

        # <editor-fold desc="task-related variables">
        self.user_number = 0
        self.current_task_number = 0
        self.location_header = None
        self.file_name_header = None
        self.total_number_of_tasks = 0
        # </editor-fold>

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).__init__(screen_width_input, screen_height_input)
        else:
            super(UserStudyBase, self).__init__(screen_width_input, screen_height_input)

        self.setup_parameters_widget()
        self.setup_progress_widget()
        self.setup_timer_widget()
        self.setup_captured_images_widget()
        if LOG_RESULTS_FLAG:
            self.create_experiment_logging_directories()

        self.update_progress_bar()
        self.set_user_study_state(AbstractUserStudyState.MANUAL_DEMO)

    # <editor-fold desc="gui functions">
    def setup_docks_layout(self):
        self.dock_area = DockArea()
        self.setCentralWidget(self.dock_area)

        # define docks
        self.image_dock = Dock(DOCK_NAME_CENTRAL_IMAGE, size=(1092, 700))
        self.context_dock = Dock(DOCK_NAME_CONTEXT_IMAGE, size=(364, 200))
        self.indicators_dock = Dock(DOCK_NAME_GAZE_INDICATORS, size=(728, 200))
        self.captured_images_dock = Dock(DOCK_NAME_CAPTURED_IMAGES, size=(650, 200))

        self.parameters_dock = Dock(DOCK_NAME_PARAMETERS, size=(350, 50))
        self.instructions_dock = Dock(DOCK_NAME_INSTRUCTIONS, size=(364, 50))
        self.timer_dock = Dock(DOCK_NAME_TIMER, size=(200, 50))
        self.progress_dock = Dock(DOCK_NAME_PROGRESS, size=(400, 50))

        # hide docks' title bars
        self.image_dock.hideTitleBar()
        self.context_dock.hideTitleBar()
        self.indicators_dock.hideTitleBar()
        self.captured_images_dock.hideTitleBar()
        self.parameters_dock.hideTitleBar()
        self.timer_dock.hideTitleBar()
        self.instructions_dock.hideTitleBar()
        self.progress_dock.hideTitleBar()

        # add docks
        self.dock_area.addDock(self.progress_dock, 'top')
        self.dock_area.addDock(self.image_dock, 'top', self.progress_dock)

        self.dock_area.addDock(self.context_dock, 'bottom', self.progress_dock)

        self.dock_area.addDock(self.instructions_dock, 'right', self.progress_dock)

        self.dock_area.addDock(self.timer_dock, 'right', self.instructions_dock)
        self.dock_area.addDock(self.parameters_dock, 'right', self.timer_dock)

        # self.dock_area.addDock(self.indicators_dock, 'right', self.context_dock)
        self.dock_area.addDock(self.captured_images_dock, 'right', self.context_dock)

    def setup_parameters_widget(self):
        self.parameters_widget = pg.GraphicsLayoutWidget()

        self.system_state_image_view_box = self.parameters_widget.addViewBox(row=0, col=2)
        self.gaze_activation_image_view_box = self.parameters_widget.addViewBox(row=0, col=1)
        self.parameters_layout_view_box = self.parameters_widget.addViewBox(row=0, col=0)

        self.parameters_label_item = pg.LabelItem()
        self.parameters_layout_view_box.addItem(self.parameters_label_item)
        self.parameters_label_item.setText(self.system_state, color='5d9dfc', size='80pt', bold=True, italic=False)
        # self.parameters_layout_view_box.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
        self.parameters_layout_view_box.setAspectLocked(lock=True)

        self.parameters_layout_view_box.invertY()
        self.parameters_layout_view_box.setMouseEnabled(False, False)

        self.load_system_state_icons()
        self.system_state_image_item = pg.ImageItem()
        self.system_state_image_view_box.addItem(self.system_state_image_item)
        self.system_state_image_view_box.setAspectLocked(True)
        self.system_state_image_view_box.setMouseEnabled(False, False)

        self.gaze_image_item = pg.ImageItem()
        self.gaze_activation_image_view_box.addItem(self.gaze_image_item)
        self.gaze_activation_image_view_box.setAspectLocked(True)
        self.gaze_activation_image_view_box.setMouseEnabled(False, False)

        self.update_system_state_image()

        self.parameters_dock.addWidget(self.parameters_widget)

    def load_system_state_icons(self):

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

    def setup_timer_widget(self):
        self.timer_widget = pg.GraphicsLayoutWidget()
        self.timer_layout_view_box = self.timer_widget.addViewBox(row=0, col=0)
        self.timer_label_item = pg.LabelItem()
        self.timer_layout_view_box.addItem(self.timer_label_item)
        self.timer_label_item.setText("", color='5d9dfc', size='10pt', bold=True, italic=False)
        self.timer_layout_view_box.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
        self.timer_layout_view_box.setAspectLocked(lock=True)

        self.timer_layout_view_box.invertY()
        self.timer_layout_view_box.setMouseEnabled(False, False)
        self.timer_dock.addWidget(self.timer_widget)

    def setup_progress_widget(self):

        self.progress_widget = pg.GraphicsLayoutWidget()
        self.progress_layout_view_box = self.progress_widget.addViewBox(row=0, col=0)
        self.progress_text_item = pg.LabelItem()
        self.progress_layout_view_box.addItem(self.progress_text_item)
        self.progress_layout_view_box.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
        self.progress_layout_view_box.setAspectLocked(lock=True)

        self.progress_layout_view_box.invertY()
        self.progress_layout_view_box.setMouseEnabled(False, False)
        self.progress_dock.addWidget(self.progress_widget)

        self.progress_label_item_text = "User Study Progress"

        self.progress_text_item.setText(self.progress_label_item_text, color='5d9dfc',
                                        size='20pt', bold=True, italic=False)

    # </editor-fold>

    # <editor-fold desc="values update functions">

    def update_parameters_label(self):

        zoom = "%.0f" % self.zoom_percentage_value_horizontal
        text = "[Zoom: " + str(zoom) + "%" + "] &nbsp;&nbsp;" + "[Depth: " + str(self.depth_value) + "cm" + "]<br/>" + \
               "[Gain: " + str(self.gain_value) + "] &nbsp;&nbsp;" + "[Frequency: " + \
               str(self.frequency_value) + "MHz" + "]<br/>" + \
               "[Focus: " + str(self.focus_value) + "cm" + "]"

        self.parameters_label_item.setText(text)

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

    # </editor-fold>

    # <editor-fold desc="threading functions">

    def start_threads(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).start_threads()
        else:
            super(UserStudyBase, self).start_threads()

    # </editor-fold>

    # <editor-fold desc="callback functions">

    def callback_values_update(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).callback_values_update()
        else:
            super(UserStudyBase, self).callback_values_update()

        # update image parameters
        self.update_parameters_label()
        self.update_system_state_image()

        # update time limit
        self.time_limit = SP_TASKS_TIME_LIMITS[self.current_task_number]
        try:
            self.time_elapsed = round(time.time() - self.current_timer, 1)
        except:
            pass

        # timer check
        if self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING or \
                self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:
            if self.time_elapsed >= self.time_limit:
                self.keypress_R()
                self.time_elapsed = 0

        # update task timer
        if self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING or \
                self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:
            if self.counting_time:
                self.timer_label_item.setText(str(self.time_elapsed) + "/" + str(self.time_limit))
        else:
            if self.counting_time:
                self.timer_label_item.setText(str(self.time_elapsed))

        # logging-related
        letter = "Q"
        log_flag = False

        if time.time() - self.last_cursor_move_time == 0.0:
            print "cursor move"
            log_flag = True
            self.counted_cursor_movement = True
            self.last_cursor_sub = time.time() - self.last_cursor_move_time

        if self.prev_letter == letter:
            log_flag = False

        if log_flag:
            self.raw_key_input_log.append([letter, time.time(), self.system_state])
            self.prev_letter = letter

    def callback_arduino_update(self, info):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).callback_arduino_update(info)
        else:
            super(UserStudyBase, self).callback_arduino_update(info)

        # <editor-fold desc="logging-related">
        log_flag = True

        letter = ""

        if info == HwInterface.ZOOM_PRESS:
            letter = "W"

        elif info == HwInterface.ZOOM_CW:
            letter = "A"

        elif info == HwInterface.ZOOM_CCW:
            letter = "D"

        elif info == HwInterface.CAPTURE_PRESS:
            letter = "O"
            log_flag = False

        elif info == HwInterface.TOP_PRESS:
            letter = "P"

        elif info == HwInterface.DEPTH_CW:
            letter = "Z"

        elif info == HwInterface.DEPTH_CCW:
            letter = "X"

        elif info == HwInterface.FOCUS_CW:
            letter = "C"

        elif info == HwInterface.FOCUS_CCW:
            letter = "V"

        elif info == HwInterface.FOCUS_PRESS:
            letter = "B"

        elif info == HwInterface.RIGHT_PRESS:
            letter = "S"

            # TODO enable this only if button press is engaged during gaze activation
            # if not self.double_press_PB:
            #     if self.prev_letter == "S":
            #         letter = ""
            #         log_flag = False
            #         self.double_press_PB = True
            #     else:
            #         letter = "S"
            # else:
            #     letter = "S"
            #     self.double_press_PB = False

        if letter == "A" or letter == "D" or letter == "Z" \
                or letter == "X" or letter == "C" or letter == "V":

            if self.prev_letter == letter:
                log_flag = False

        if log_flag:
            self.raw_key_input_log.append([letter, time.time()])
            self.prev_letter = letter
        # </editor-fold>

    def callback_update_POG(self, info):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).callback_update_POG(info)
        else:
            super(UserStudyBase, self).callback_update_POG(info)

        # <editor-fold desc="logging-related">
        self.pog_x_y_d_time = [self.POG.x(), self.POG.y(), self.fixation_duration, time.time(), self.valid_POG_flag]

        if self.record_pog_flag:
            self.pog_log.append([self.user_study_state, self.current_task_number, self.pog_x_y_d_time])
        # </editor-fold>

    def callback_input_held_monitor(self):
        super(UserStudyBase, self).callback_input_held_monitor()

        if self.gaze_activation_held or self.gaze_activation_pressed:
            if not self.is_gaze_icon_set:
                self.gaze_image_item.setImage(self.gaze_icon)
                self.is_gaze_icon_set = True
        else:
            if self.is_gaze_icon_set:
                self.gaze_image_item.clear()
                self.is_gaze_icon_set = False

    # </editor-fold>

    # <editor-fold desc="repetitiveness scoring functions">

    def calculate_repetitiveness_score(self):

        # Raw list
        self.raw_key_input_log_names = self.replace_letters_with_names_AR_RAW_lists(self.raw_key_input_log)

        # AR list and score
        self.AR_log, self.pre_FR_log = self.produce_AR_and_Pre_FR_logs(self.raw_key_input_log)
        self.AR_score = self.get_AR_score(self.AR_log)

        self.AR_log_names = self.replace_letters_with_names_AR_RAW_lists(self.AR_log)

        # Pre FR list
        self.pre_FR_log_names = self.replace_letters_with_names_AR_RAW_lists(self.pre_FR_log)

        # Compressed list
        self.LZW_compressed_log = [item[0] for item in self.pre_FR_log]
        self.LZW_compressed_log = self.LZW_compress(self.LZW_compressed_log)

        # FR list and score
        self.FR_log = self.count_repetitions_in_a_list([item[0] for item in self.pre_FR_log],
                                                       self.LZW_compressed_log)
        self.FR_score = sum([item[1] for item in self.FR_log])

        self.FR_log_names = self.replace_letters_with_names_FR_list(self.FR_log)

        # Total repetitiveness score
        self.total_repetitiveness_score = self.AR_score + self.FR_score

        # Save all values to list
        raw_list_item = [self.user_study_state, self.current_task_number, self.raw_key_input_log_names]
        AR_list_item = [self.user_study_state, self.current_task_number, self.AR_log_names]
        pre_FR_list_item = [self.user_study_state, self.current_task_number, self.pre_FR_log_names]
        FR_list_item = [self.user_study_state, self.current_task_number, self.FR_log_names]
        repetitiveness_scores_item = [self.user_study_state, self.current_task_number,
                                      [self.AR_score, self.FR_score, self.total_repetitiveness_score]]

        self.raw_key_input_log_list.append(raw_list_item)
        self.AR_log_list.append(AR_list_item)
        self.pre_FR_log_list.append(pre_FR_list_item)
        self.FR_log_list.append(FR_list_item)
        self.repetitiveness_scores_list.append(repetitiveness_scores_item)

    @staticmethod
    def produce_AR_and_Pre_FR_logs(input_list):

        last_letter = ""
        AR_log = []
        pre_FR_log = []

        for i in range(0, len(input_list)):

            if last_letter == input_list[i][0]:
                AR_log.append([input_list[i][0], input_list[i][1], "R"])
            else:
                AR_log.append([input_list[i][0], input_list[i][1], ""])
                pre_FR_log.append(input_list[i])

            last_letter = input_list[i][0]

        return AR_log, pre_FR_log

    @staticmethod
    def get_AR_score(input_list):

        score = 0

        for x in input_list:
            if x[2] == "R":
                score += 1

        return score

    @staticmethod
    def count_repetitions_in_a_list(input_list, unique_list):

        input_list_string = ''.join(input_list)

        output = []

        for x in unique_list:
            output.append([x, input_list_string.count(x) - 1])

        return output

    @staticmethod
    def LZW_compress(uncompressed):
        """Compress a string to a list of output symbols."""
        # Build the dictionary.
        dictionary = []

        w = ""
        for c in uncompressed:
            wc = w + c

            if wc in dictionary:
                w = wc
            else:
                # Add wc to the dictionary.
                dictionary.append(wc)
                w = c

        return dictionary

    def replace_letters_with_names_AR_RAW_lists(self, input_list):

        output_list = [item[0] for item in input_list]
        out = []
        for x in output_list:
            out.append(self.replace_letters_with_names(x))
        output_list = out

        for i in range(0, len(output_list)):
            try:
                output_list[i] = [output_list[i], input_list[i][1], input_list[i][2]]
            except:
                try:
                    output_list[i] = [output_list[i], input_list[i][1]]
                except:
                    output_list[i] = [output_list[i]]

        return output_list

    def replace_letters_with_names_FR_list(self, x):

        y = []

        for j in range(0, len(x)):
            test = x[j][0]

            out = []
            y_item = []

            for i in range(0, len(test)):
                letter = test[i]

                letter_rep = self.replace_letters_with_names(letter)

                out.append(letter_rep)

            y_item.append([out, x[j][1]])

            y.append(y_item)

        return y

    @staticmethod
    def replace_letters_with_names(letter):

        name = ""

        if letter == 'W':
            name = letter.replace('W', HwInterface.ZOOM_PRESS)
        if letter == 'A':
            name = letter.replace('A', HwInterface.ZOOM_CW)
        if letter == 'D':
            name = letter.replace('D', HwInterface.ZOOM_CCW)
        if letter == 'O':
            name = letter.replace('O', HwInterface.CAPTURE_PRESS)
        if letter == 'P':
            name = letter.replace('P', HwInterface.TOP_PRESS)
        if letter == 'G':
            name = letter.replace('G', HwInterface.CALIBRATE_PRESS)
        if letter == 'Z':
            name = letter.replace('Z', HwInterface.DEPTH_CW)
        if letter == 'X':
            name = letter.replace('X', HwInterface.DEPTH_CCW)
        if letter == 'C':
            name = letter.replace('C', HwInterface.FOCUS_CW)
        if letter == 'V':
            name = letter.replace('V', HwInterface.FOCUS_CCW)
        if letter == 'B':
            name = letter.replace('B', HwInterface.FOCUS_PRESS)
        if letter == 'S':
            name = letter.replace('S', HwInterface.RIGHT_PRESS)
        if letter == 'Q':
            name = letter.replace('Q', HwInterface.CURSOR_MOVE)

        return name

    def print_repetitiveness_scores(self):

        print "RAW list:"
        for i in range(0, len(self.raw_key_input_log_list)):
            print self.raw_key_input_log_list[i]

        print "=============================="

        print "AR list:"
        for i in range(0, len(self.AR_log_list)):
            print self.AR_log_list[i]

        print "=============================="

        print "Pre-FR list:"
        for i in range(0, len(self.pre_FR_log_list)):
            print self.pre_FR_log_list[i]

        print "=============================="

        print "FR list:"
        for i in range(0, len(self.FR_log_list)):
            print self.FR_log_list[i]

        print "=============================="

        print "Repetitiveness Scores:"
        for i in range(0, len(self.repetitiveness_scores_list)):
            print self.repetitiveness_scores_list[i]

    # </editor-fold>

    # <editor-fold desc="timer-related functions">
    def start_timer(self):
        self.current_timer = time.time()
        self.counting_time = True

    def stop_timer(self):
        time_elapsed = time.time() - self.current_timer

        time_elapsed_list_item = [self.user_study_state, self.current_task_number, time_elapsed]

        self.list_times_elapsed.append(time_elapsed_list_item)
        self.counting_time = False

    def reset_timer(self):
        self.current_timer = None
        self.timer_label_item.setText("")

    def print_elapsed_times(self):
        print "Total elapsed times:"
        for i in range(0, len(self.list_times_elapsed)):
            print self.list_times_elapsed[i]

    # </editor-fold>

    # <editor-fold desc="data logging functions">

    @staticmethod
    def save_image_to_file(image, location, file_name):

        image = np.rot90(image)
        misc.imsave(location + file_name, image)

    @staticmethod
    def log_list_to_file(input_list, directory, file_name):

        with open(directory + file_name, 'wb') as f:
            pickle.dump(input_list, f)

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
        subdirectories = [user_dir + '/' + AbstractUserStudyState.MANUAL_DEMO,
                          user_dir + '/' + AbstractUserStudyState.GAZE_DEMO,
                          user_dir + '/' + AbstractUserStudyState.MANUAL_PPT_TRAINING,
                          user_dir + '/' + AbstractUserStudyState.MANUAL_PPT_RECORDED,
                          user_dir + '/' + AbstractUserStudyState.GAZE_PPT_TRAINING,
                          user_dir + '/' + AbstractUserStudyState.GAZE_PPT_RECORDED]

        os.mkdir(user_dir)

        for i in range(0, len(subdirectories)):
            os.mkdir(subdirectories[i])
            os.mkdir(subdirectories[i] + '/' + DIR_ACCURACY_SCORES)
            os.mkdir(subdirectories[i] + '/' + DIR_AUDIO_RECORDING)
            os.mkdir(subdirectories[i] + '/' + DIR_CAPTURED_IMAGES)
            os.mkdir(subdirectories[i] + '/' + DIR_ELAPSED_TIMES)
            os.mkdir(subdirectories[i] + '/' + DIR_POG_LOGS)
            os.mkdir(subdirectories[i] + '/' + DIR_REPETITIVENESS)
            os.mkdir(subdirectories[i] + '/' + DIR_RESEARCHER_NOTES)

        self.update_save_to_file_strings()

    def update_save_to_file_strings(self):
        self.location_header = self.results_home_dir + DIR_USER + str(self.user_number) + "/" + \
                               self.user_study_state + "/"

        self.file_name_header = self.user_study_state + "_"

    def log_elapsed_times_to_file(self):
        location = self.location_header + DIR_ELAPSED_TIMES + "/"

        self.log_list_to_file(self.list_times_elapsed, location,
                              self.file_name_header + FILE_NAME_TIMES_ELAPSED_SCORES)

        print "timer score logged to " + location + self.file_name_header + FILE_NAME_TIMES_ELAPSED_SCORES

    def log_repetitiveness_scores_to_file(self):
        location = self.location_header + DIR_REPETITIVENESS + "/"

        self.log_list_to_file(self.raw_key_input_log_list, location,
                              self.file_name_header + str(self.current_task_number) + "_" +
                              FILE_NAME_RAW_REPETITIVENESS_LIST)

        self.log_list_to_file(self.AR_log_list, location,
                              self.file_name_header + str(self.current_task_number) + "_" +
                              FILE_NAME_AR_REPETITIVENESS_LIST)

        self.log_list_to_file(self.pre_FR_log_list, location,
                              self.file_name_header + str(self.current_task_number) + "_" +
                              FILE_NAME_PRE_FR_REPETITIVENESS_LIST)

        self.log_list_to_file(self.FR_log_list, location,
                              self.file_name_header + str(self.current_task_number) + "_" +
                              FILE_NAME_FR_REPETITIVENESS_LIST)

        self.log_list_to_file(self.repetitiveness_scores_list, location,
                              self.file_name_header + str(self.current_task_number) + "_" +
                              FILE_NAME_REPETITIVENESS_SCORES)

        print "repetitiveness scores logged to " + location + self.file_name_header + \
              str(self.current_task_number) + "_" + FILE_NAME_REPETITIVENESS_SCORES

    def log_fixation_data_to_file(self):
        location = self.location_header + DIR_POG_LOGS + "/"

        self.log_list_to_file(self.pog_log, location,
                              self.file_name_header + str(self.current_task_number) + "_" + FILE_NAME_POG_LOG)

        print "fixations data logged to " + location + self.file_name_header + str(self.current_task_number) + "_" + \
              FILE_NAME_POG_LOG

    def log_all_task_values_to_file(self):
        self.print_elapsed_times()
        self.log_elapsed_times_to_file()

        # self.print_repetitiveness_scores()
        self.log_repetitiveness_scores_to_file()

        self.log_fixation_data_to_file()

    # </editor-fold>

    # <editor-fold desc="task-related functions">

    def update_progress_bar(self):

        # progress_intro_text = PROGRESS_INTRODUCTION
        progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
        progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

        progress_demo_manual_text = PROGRESS_DEMO
        progress_training_manual_text = PROGRESS_PPT_TRAINING
        progress_recorded_manual_text = PROGRESS_PPT_RECORDED
        # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

        progress_demo_gaze_text = PROGRESS_DEMO
        progress_training_gaze_text = PROGRESS_PPT_TRAINING
        progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
        # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

        progress_break_text = PROGRESS_BREAK
        # progress_discussion_text = PROGRESS_DISCUSSION

        if self.user_study_state == AbstractUserStudyState.INTRODUCTION:
            # progress_intro_text = "[" + PROGRESS_INTRODUCTION + "]"
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.MANUAL_DEMO:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = "[" + PROGRESS_DEMO + "]"
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = "[" + PROGRESS_PPT_TRAINING + "]"
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = "[" + PROGRESS_PPT_RECORDED + "]"
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_EVALUATION:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = "[" + PROGRESS_PPT_EVALUATION + "]"

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.BREAK:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = "[" + PROGRESS_BREAK + "]"
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.GAZE_DEMO:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = "[" + PROGRESS_DEMO + "]"
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = "[" + PROGRESS_PPT_TRAINING + "]"
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = "[" + PROGRESS_PPT_RECORDED + "]"
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_EVALUATION:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = "[" + PROGRESS_PPT_EVALUATION + "]"

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = PROGRESS_DISCUSSION

        elif self.user_study_state == AbstractUserStudyState.DISCUSSION:
            # progress_intro_text = PROGRESS_INTRODUCTION
            progress_manual_text = PROGRESS_MANUAL_BASED_INTERFACE
            progress_gaze_text = PROGRESS_GAZE_SUPPORTED_INTERFACE

            progress_demo_manual_text = PROGRESS_DEMO
            progress_training_manual_text = PROGRESS_PPT_TRAINING
            progress_recorded_manual_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_manual_text = PROGRESS_PPT_EVALUATION

            progress_demo_gaze_text = PROGRESS_DEMO
            progress_training_gaze_text = PROGRESS_PPT_TRAINING
            progress_recorded_gaze_text = PROGRESS_PPT_RECORDED
            # progress_evaluation_gaze_text = PROGRESS_PPT_EVALUATION

            progress_break_text = PROGRESS_BREAK
            # progress_discussion_text = "[" + PROGRESS_DISCUSSION + "]"

        text = "Progress Bar"

        if self.user_study_order == UserStudyOrder.A:
            text = progress_manual_text + HTML_SPACE + \
                   progress_demo_manual_text + ", " + progress_training_manual_text + ", " + \
                   progress_recorded_manual_text + \
                   HTML_NEWLINE + progress_break_text + HTML_NEWLINE + \
                   progress_gaze_text + HTML_SPACE + \
                   progress_demo_gaze_text + ", " + progress_training_gaze_text + ", " + progress_recorded_gaze_text

        if self.user_study_order == UserStudyOrder.B:
            text = progress_gaze_text + HTML_SPACE + \
                   progress_demo_gaze_text + ", " + progress_training_gaze_text + ", " + \
                   progress_recorded_gaze_text + \
                   HTML_NEWLINE + progress_break_text + HTML_NEWLINE + \
                   progress_manual_text + HTML_SPACE + \
                   progress_demo_manual_text + ", " + progress_training_manual_text + ", " + \
                   progress_recorded_manual_text

        self.progress_text_item.setText(text)

    def update_instructions_bar(self):
        self.instructions_layout_view_box.autoRange()
        self.instructions_label_item.setText(
            INSTRUCTION_TARGET_NUMBER + str(self.current_task_number + 1) + " - " +
            INSTRUCTION_DEMO_TRAINING_RECORDED_DEFAULT)

    def clear_captured_images(self):
        for item in self.captured_images_item:
            item.clear()
        self.captured_images = []

    def clear_values_logs(self):
        # reset tasks
        self.current_task_number = 0

        # clear fixation points
        self.pog_log = []

        # clear repetitiveness logs
        self.raw_key_input_log_list = []
        self.AR_log_list = []
        self.pre_FR_log_list = []
        self.FR_log_list = []
        self.repetitiveness_scores_list = []

        # clear elapsed times
        self.list_times_elapsed = []

    def reset_all_values(self):

        # <editor-fold desc="reset system state">
        self.set_system_state(SystemState.FULLSCALE)
        # </editor-fold>

        # <editor-fold desc="reset roi">
        self.set_roi_to_default_pos_and_size()
        # </editor-fold>

        # <editor-fold desc="reset timer">
        self.reset_timer()
        # </editor-fold>

        # <editor-fold desc="reset repetitiveness logs">
        self.raw_key_input_log = []
        self.AR_log = []
        self.pre_FR_log = []
        self.LZW_compressed_log = []
        self.FR_log = []
        self.AR_score = 0
        self.FR_score = 0
        self.total_repetitiveness_score = 0

        self.raw_key_input_log_names = []
        self.AR_log_names = []
        self.pre_FR_log_names = []
        self.LZW_compressed_log_names = []
        self.FR_log_names = []

        self.prev_letter = None
        self.counted_cursor_movement = False
        self.double_press_PB = False

        self.raw_key_input_log_list = []
        self.AR_log_list = []
        self.pre_FR_log_list = []
        self.FR_log_list = []
        self.repetitiveness_scores_list = []
        # </editor-fold>

        # <editor-fold desc="reset fixation logs">
        self.pog_log = []
        # </editor-fold>

    def switch_interaction(self, interaction):

        if interaction == Interaction.MANUAL_BASED:
            if self.interaction != Interaction.MANUAL_BASED:
                self.interaction = Interaction.MANUAL_BASED
                self.input_held_monitor_timer_thread.stop()

                if self.system_state == SystemState.ZOOM_B:
                    self.set_system_state(SystemState.ZOOM_A)

                elif self.system_state == SystemState.PRE_ZOOM_B:
                    self.set_system_state(SystemState.PRE_ZOOM_A)

        elif interaction == Interaction.GAZE_SUPPORTED:
            if self.interaction != Interaction.GAZE_SUPPORTED:
                self.interaction = Interaction.GAZE_SUPPORTED
                self.input_held_monitor_timer_thread.start(.1)

                if self.system_state == SystemState.ZOOM_A:
                    self.set_system_state(SystemState.ZOOM_B)

                elif self.system_state == SystemState.PRE_ZOOM_A:
                    self.set_system_state(SystemState.PRE_ZOOM_B)

    # </editor-fold>

    # <editor-fold desc="researcher tools functions">

    def set_user_study_state(self, state):

        # clear all logs
        self.clear_values_logs()

        # then reset the values
        self.reset_all_values()

        if state == AbstractUserStudyState.INTRODUCTION:
            self.user_study_state = AbstractUserStudyState.INTRODUCTION

            self.instructions_label_item.setText(INSTRUCTIONS_INTRO)

        elif state == AbstractUserStudyState.MANUAL_DEMO:
            self.switch_interaction(Interaction.MANUAL_BASED)
            self.user_study_state = AbstractUserStudyState.MANUAL_DEMO

            self.instructions_label_item.setText(
                INSTRUCTION_TARGET_NUMBER + str(self.current_task_number + 1) + " - " +
                INSTRUCTION_DEMO_TRAINING_RECORDED_DEFAULT)

        elif state == AbstractUserStudyState.MANUAL_PPT_TRAINING:
            self.switch_interaction(Interaction.MANUAL_BASED)
            self.user_study_state = AbstractUserStudyState.MANUAL_PPT_TRAINING

            self.instructions_label_item.setText(
                INSTRUCTION_TARGET_NUMBER + str(self.current_task_number + 1) + " - " +
                INSTRUCTION_DEMO_TRAINING_RECORDED_DEFAULT)

        elif state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
            self.switch_interaction(Interaction.MANUAL_BASED)
            self.user_study_state = AbstractUserStudyState.MANUAL_PPT_RECORDED

            self.instructions_label_item.setText(
                INSTRUCTION_TARGET_NUMBER + str(self.current_task_number + 1) + " - " +
                INSTRUCTION_DEMO_TRAINING_RECORDED_DEFAULT)

        elif state == AbstractUserStudyState.MANUAL_PPT_EVALUATION:
            self.switch_interaction(Interaction.MANUAL_BASED)
            self.user_study_state = AbstractUserStudyState.MANUAL_PPT_EVALUATION

            self.instructions_label_item.setText(INSTRUCTIONS_EVALUATION)

        elif state == AbstractUserStudyState.BREAK:
            self.user_study_state = AbstractUserStudyState.BREAK

            self.instructions_label_item.setText(PROGRESS_BREAK)

        elif state == AbstractUserStudyState.GAZE_DEMO:
            self.switch_interaction(Interaction.GAZE_SUPPORTED)
            self.user_study_state = AbstractUserStudyState.GAZE_DEMO

            self.instructions_label_item.setText(
                INSTRUCTION_TARGET_NUMBER + str(self.current_task_number + 1) + " - " +
                INSTRUCTION_DEMO_TRAINING_RECORDED_DEFAULT)

        elif state == AbstractUserStudyState.GAZE_PPT_TRAINING:
            self.switch_interaction(Interaction.GAZE_SUPPORTED)
            self.user_study_state = AbstractUserStudyState.GAZE_PPT_TRAINING

            self.instructions_label_item.setText(
                INSTRUCTION_TARGET_NUMBER + str(self.current_task_number + 1) + " - " +
                INSTRUCTION_DEMO_TRAINING_RECORDED_DEFAULT)

        elif state == AbstractUserStudyState.GAZE_PPT_RECORDED:
            self.switch_interaction(Interaction.GAZE_SUPPORTED)
            self.user_study_state = AbstractUserStudyState.GAZE_PPT_RECORDED

            self.instructions_label_item.setText(
                INSTRUCTION_TARGET_NUMBER + str(self.current_task_number + 1) + " - " +
                INSTRUCTION_DEMO_TRAINING_RECORDED_DEFAULT)

        elif state == AbstractUserStudyState.GAZE_PPT_EVALUATION:
            self.switch_interaction(Interaction.GAZE_SUPPORTED)
            self.user_study_state = AbstractUserStudyState.GAZE_PPT_EVALUATION

            self.instructions_label_item.setText(INSTRUCTIONS_EVALUATION)

        elif state == AbstractUserStudyState.DISCUSSION:
            self.user_study_state = AbstractUserStudyState.DISCUSSION

            self.instructions_label_item.setText(INSTRUCTIONS_DISCUSSION)

        self.update_progress_bar()
        self.update_save_to_file_strings()
        print self.location_header
        print self.file_name_header

    def go_to_next_user_study_state(self):

        if self.user_study_order == UserStudyOrder.A:
            if self.user_study_state == AbstractUserStudyState.INTRODUCTION:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_DEMO)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_DEMO:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_TRAINING)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_RECORDED)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_EVALUATION)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_EVALUATION:
                self.set_user_study_state(AbstractUserStudyState.BREAK)

            elif self.user_study_state == AbstractUserStudyState.BREAK:
                self.set_user_study_state(AbstractUserStudyState.GAZE_DEMO)

            elif self.user_study_state == AbstractUserStudyState.GAZE_DEMO:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_TRAINING)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_RECORDED)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_EVALUATION)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_EVALUATION:
                self.set_user_study_state(AbstractUserStudyState.DISCUSSION)

        if self.user_study_order == UserStudyOrder.B:
            if self.user_study_state == AbstractUserStudyState.INTRODUCTION:
                self.set_user_study_state(AbstractUserStudyState.GAZE_DEMO)

            elif self.user_study_state == AbstractUserStudyState.GAZE_DEMO:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_TRAINING)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_RECORDED)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_EVALUATION)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_EVALUATION:
                self.set_user_study_state(AbstractUserStudyState.BREAK)

            elif self.user_study_state == AbstractUserStudyState.BREAK:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_DEMO)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_DEMO:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_TRAINING)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_RECORDED)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_EVALUATION)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_EVALUATION:
                self.set_user_study_state(AbstractUserStudyState.DISCUSSION)

        self.clear_captured_images()

    def go_to_previous_user_study_state(self):

        if self.user_study_order == UserStudyOrder.A:
            if self.user_study_state == AbstractUserStudyState.DISCUSSION:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_EVALUATION)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_EVALUATION:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_RECORDED)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_TRAINING)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:
                self.set_user_study_state(AbstractUserStudyState.GAZE_DEMO)

            elif self.user_study_state == AbstractUserStudyState.GAZE_DEMO:
                self.set_user_study_state(AbstractUserStudyState.BREAK)

            elif self.user_study_state == AbstractUserStudyState.BREAK:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_EVALUATION)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_EVALUATION:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_RECORDED)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_TRAINING)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_DEMO)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_DEMO:
                self.set_user_study_state(AbstractUserStudyState.INTRODUCTION)

        if self.user_study_order == UserStudyOrder.B:
            if self.user_study_state == AbstractUserStudyState.DISCUSSION:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_EVALUATION)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_EVALUATION:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_RECORDED)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_PPT_TRAINING)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING:
                self.set_user_study_state(AbstractUserStudyState.MANUAL_DEMO)

            elif self.user_study_state == AbstractUserStudyState.MANUAL_DEMO:
                self.set_user_study_state(AbstractUserStudyState.BREAK)

            elif self.user_study_state == AbstractUserStudyState.BREAK:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_EVALUATION)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_EVALUATION:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_RECORDED)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED:
                self.set_user_study_state(AbstractUserStudyState.GAZE_PPT_TRAINING)

            elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:
                self.set_user_study_state(AbstractUserStudyState.GAZE_DEMO)

            elif self.user_study_state == AbstractUserStudyState.GAZE_DEMO:
                self.set_user_study_state(AbstractUserStudyState.INTRODUCTION)

        self.clear_captured_images()

    def go_to_next_task(self):
        self.current_task_number += 1
        if self.current_task_number == self.total_number_of_tasks:
            self.current_task_number = 0
        self.update_instructions_bar()

    def go_to_previous_task(self):
        self.current_task_number -= 1
        if self.current_task_number < 0:
            self.current_task_number = 0
        self.update_instructions_bar()

    def start_current_task(self):
        self.start_timer()
        self.record_pog_flag = True

    def end_current_task(self):
        # stop timer to log elapsed time
        try:
            self.stop_timer()
        except:
            print "timer has not been started"

        # calculate repetitiveness for logging
        self.calculate_repetitiveness_score()

        # stop collecting fixations for logging
        self.record_pog_flag = False

        if LOG_RESULTS_FLAG:
            # log everything
            self.log_all_task_values_to_file()

        # reset
        self.reset_all_values()

    # </editor-fold>

    def keyPressEvent(self, event):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keyPressEvent(event)
        else:
            super(UserStudyBase, self).keyPressEvent(event)

        key = event.key()

        if key == QtCore.Qt.Key_1:
            self.go_to_next_user_study_state()

        if key == QtCore.Qt.Key_2:
            self.start_current_task()

        if key == QtCore.Qt.Key_3:
            self.go_to_next_task()
            self.show_current_task()

        if key == QtCore.Qt.Key_4:
            self.end_current_task()
            self.keypress_Q()
            self.keypress_Q()
            self.keypress_Q()

        if key == QtCore.Qt.Key_5:
            pass

        if key == QtCore.Qt.Key_6:
            self.go_to_previous_user_study_state()

        if key == QtCore.Qt.Key_7:
            self.go_to_previous_task()
            self.show_current_task()

    def keypress_R(self):

        if self.system_state == SystemState.PRE_ZOOM_A or self.system_state == SystemState.PRE_ZOOM_B:
            self.instructions_label_item.setText(
                INSTRUCTION_TARGET_NUMBER + str(self.current_task_number + 1) + " - " +
                INSTRUCTIONS_CONFIRM_ZOOM_MESSAGE)

        elif self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B or \
                self.system_state == SystemState.FULLSCALE:

            captured_image = self.roi.getArrayRegion(self.image, self.image_item)
            self.captured_images.append(captured_image)

            location = self.location_header + DIR_CAPTURED_IMAGES + "/"
            file_name = self.file_name_header + str(len(self.captured_images)) + EXTENSION_CAPTURED_IMAGE

            self.save_image_to_file(captured_image, location, file_name)

            self.last_action = Actions.CAPTURE

            index = len(self.captured_images) - 1
            if index < MAX_NUM_DISPLAYED_CAPTURED_IMAGES:
                self.captured_images_item[index].setImage(self.captured_images[index])
            else:
                images_to_shift = []
                for i in range(0, MAX_NUM_DISPLAYED_CAPTURED_IMAGES):
                    images_to_shift.append(self.captured_images_item[i].image)

                for i in range(0, MAX_NUM_DISPLAYED_CAPTURED_IMAGES - 1):
                    self.captured_images_item[i].setImage(images_to_shift[i + 1])
                    self.captured_images_item[i].setImage(images_to_shift[i + 1])

                self.captured_images_item[MAX_NUM_DISPLAYED_CAPTURED_IMAGES - 1].setImage(self.captured_images[index])

            if self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING or \
                    self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED or \
                    self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING or \
                    self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED:
                self.end_current_task()

        self.keypress_Q()
        self.keypress_Q()
        self.keypress_Q()

    def keypress_E(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_E()
        else:
            super(UserStudyBase, self).keypress_E()

    def keypress_W(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_W()
        else:
            super(UserStudyBase, self).keypress_W()

    def keypress_U(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_U()
        else:
            super(UserStudyBase, self).keypress_U()

    def keypress_Q(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_Q()
        else:
            super(UserStudyBase, self).keypress_Q()

    def keypress_Y(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_Y()
        else:
            super(UserStudyBase, self).keypress_Y()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPLICATION_TITLE_USER_STUDY_BASE)

    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    main = UserStudyBase(width, height, Interaction.GAZE_SUPPORTED, DIR_TEST_HOME)
    main.show()

    sys.exit(app.exec_())
