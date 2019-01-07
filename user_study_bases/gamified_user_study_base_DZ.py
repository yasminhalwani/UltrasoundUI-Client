import sys
import os
import time
import pickle
import random
import cv2
import numpy as np
from numpy import array
import win32gui
import win32api

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph.dockarea import *

sys.path.insert(0, '../interactions')
from gaze_supported import GazeSupported

sys.path.insert(0, '../globals')
from common_constants import *
from states import *
from tasks_roi import *

sys.path.insert(0, '../components')
from arduino_comp import *


class GamifiedUserStudyBase(GazeSupported):
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
        self.current_game_level = GameLevel.LEVEL_1
        self.current_target_shape = ShapeRegularity.REGULAR
        self.current_game_state = GameState.IDLE
        # </editor-fold>

        # <editor-fold desc="game variables">
        self.counting_to_start_timer = None
        self.blinking_target_timer = None
        self.destroying_target_timer = None
        self.leveling_up_timer = None
        self.timeout_screen_timer = None

        self.total_number_of_started_tasks = 0
        self.required_number_of_consecutive_tasks_per_level = 0
        self.total_level_score = 0
        self.maximum_number_of_levels = 0

        self.target_captured = False
        self.task_timed_out = False
        self.leveled_up = False

        self.current_task_roi = None
        self.target_selected_flag = False

        self.counter_1_flag = False
        self.counter_2_flag = False
        self.counter_3_flag = False
        self.counter_go_flag = False

        self.target_blink_on_flag = False
        self.target_blink_off_flag = False

        self.highest_passed_training_level = GameLevel.LEVEL_1

        # </editor-fold>

        # <editor-fold desc="gui variables">

        # -- image widget
        self.space_background_image = None
        self.counter_background_image_3 = None
        self.counter_background_image_2 = None
        self.counter_background_image_1 = None
        self.counter_background_image_go = None
        self.counter_background_image_level_up = None
        self.timeout_background_image = None
        self.game_over_background_image = None
        self.you_win_background_image = None
        self.life_image = None

        # -- targets
        self.target_1_image = None
        self.target_2_image = None
        self.target_3_image = None
        self.target_4_image = None
        self.target_1_selected_image = None
        self.target_2_selected_image = None
        self.target_3_selected_image = None
        self.target_4_selected_image = None
        self.destroyed_target_image = None
        self.target_image_item = None
        self.context_target_image_item = None
        self.current_target_shape = None

        self.target_image = None
        self.selected_target_image = None

        # -- docks layout
        self.timer_progress_bar_dock = None
        self.level_number_dock = None
        self.level_progress_bar_dock = None
        self.tools_dock = None
        self.hp_dock = None

        # -- tools images
        self.tools_widget = None
        self.system_state_image_view_box = None
        self.gaze_activation_image_view_box = None
        self.system_state_image_item = None
        self.gaze_image_item = None
        self.system_state_reposition_icon = None
        self.system_state_resize_icon = None
        self.gaze_icon = None
        self.is_gaze_icon_set = False
        self.current_system_state_icon = None

        # -- timer progress bar
        self.timer_progress_bar_style = None
        self.task_timer_progress_bar_widget = None

        # -- level progress bar
        self.level_progress_bar_style = None
        self.level_progress_bar_widget = None

        # -- hp images
        self.hp_widget = None
        self.life_view_boxes = []
        self.life_image_items = []
        self.life_icon = None
        self.remaining_lives = 0

        # -- level images
        self.level_number_widget = None
        self.level_icon_view_box = None
        self.level_icon_image_item = None

        self.level_1_icon = None
        self.level_2_icon = None
        self.level_3_icon = None
        self.level_4_icon = None
        self.level_5_icon = None
        self.level_6_icon = None
        self.level_7_icon = None
        self.level_8_icon = None
        self.level_9_icon = None
        self.level_10_icon = None

        self.current_level_icon = None

        # </editor-fold>

        # <editor-fold desc="timer variables">
        self.current_task_timer = None
        self.list_task_times_elapsed = []
        self.counting_time_on_task = False
        self.task_time_limit = 0
        self.task_time_elapsed = 0
        self.total_logs = []
        # </editor-fold>

        # <editor-fold desc="POG variables">
        self.pog_log = []
        self.pog_x_y_d_time = None
        self.record_pog_flag = False
        # </editor-fold>

        # <editor-fold desc="logging-related variables">
        self.user_number = 0
        self.location_header = None
        self.file_name_header = None
        self.key_logs = []
        self.current_cursor_x = 0
        self.current_cursor_y = 0
        self.prev_cursor_x = 0
        self.prev_cursor_y = 0

        self.prev_roi = None
        self.roi_logs = []
        # </editor-fold>

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).__init__(screen_width_input, screen_height_input)
        else:
            super(GamifiedUserStudyBase, self).__init__(screen_width_input, screen_height_input)

        # <editor-fold desc="function calls">
        self.load_tools_icons()
        self.load_hp_icon()
        self.load_level_icons()
        self.load_targets_images()
        self.setup_timer_progress_bar_widget()
        self.setup_level_number_widget()
        self.setup_tools_widget()
        self.setup_hp_widget()
        self.setup_level_progress_bar_widget()
        self.setup_game_variables()

        if LOG_RESULTS_FLAG:
            self.create_experiment_logging_directories()

        self.set_user_study_state(AbstractUserStudyState.INTRODUCTION)
        # </editor-fold>

    # <editor-fold desc="gui functions">

    def setup_image_layout(self):
        super(GamifiedUserStudyBase, self).setup_image_layout()

        self.image = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + SPACE_BACKGROUND_IMAGE)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.image = array(self.image)
        self.image = self.image.astype('float64')
        self.image = np.rot90(self.image)
        self.image = np.rot90(self.image)
        self.image = np.rot90(self.image)

        self.counter_background_image_3 = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + COUNTER_BACKGROUND_3_IMAGE)
        self.counter_background_image_3 = cv2.cvtColor(self.counter_background_image_3, cv2.COLOR_BGR2RGB)
        self.counter_background_image_3 = array(self.counter_background_image_3)
        self.counter_background_image_3 = self.counter_background_image_3.astype('float64')
        self.counter_background_image_3 = np.rot90(self.counter_background_image_3)
        self.counter_background_image_3 = np.rot90(self.counter_background_image_3)
        self.counter_background_image_3 = np.rot90(self.counter_background_image_3)

        self.counter_background_image_2 = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + COUNTER_BACKGROUND_2_IMAGE)
        self.counter_background_image_2 = cv2.cvtColor(self.counter_background_image_2, cv2.COLOR_BGR2RGB)
        self.counter_background_image_2 = array(self.counter_background_image_2)
        self.counter_background_image_2 = self.counter_background_image_2.astype('float64')
        self.counter_background_image_2 = np.rot90(self.counter_background_image_2)
        self.counter_background_image_2 = np.rot90(self.counter_background_image_2)
        self.counter_background_image_2 = np.rot90(self.counter_background_image_2)

        self.counter_background_image_1 = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + COUNTER_BACKGROUND_1_IMAGE)
        self.counter_background_image_1 = cv2.cvtColor(self.counter_background_image_1, cv2.COLOR_BGR2RGB)
        self.counter_background_image_1 = array(self.counter_background_image_1)
        self.counter_background_image_1 = self.counter_background_image_1.astype('float64')
        self.counter_background_image_1 = np.rot90(self.counter_background_image_1)
        self.counter_background_image_1 = np.rot90(self.counter_background_image_1)
        self.counter_background_image_1 = np.rot90(self.counter_background_image_1)

        self.counter_background_image_go = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + COUNTER_BACKGROUND_GO_IMAGE)
        self.counter_background_image_go = cv2.cvtColor(self.counter_background_image_go, cv2.COLOR_BGR2RGB)
        self.counter_background_image_go = array(self.counter_background_image_go)
        self.counter_background_image_go = self.counter_background_image_go.astype('float64')
        self.counter_background_image_go = np.rot90(self.counter_background_image_go)
        self.counter_background_image_go = np.rot90(self.counter_background_image_go)
        self.counter_background_image_go = np.rot90(self.counter_background_image_go)

        self.counter_background_image_level_up = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + BACKGROUND_LEVEL_UP_IMAGE)
        self.counter_background_image_level_up = cv2.cvtColor(self.counter_background_image_level_up, cv2.COLOR_BGR2RGB)
        self.counter_background_image_level_up = array(self.counter_background_image_level_up)
        self.counter_background_image_level_up = self.counter_background_image_level_up.astype('float64')
        self.counter_background_image_level_up = np.rot90(self.counter_background_image_level_up)
        self.counter_background_image_level_up = np.rot90(self.counter_background_image_level_up)
        self.counter_background_image_level_up = np.rot90(self.counter_background_image_level_up)

        self.timeout_background_image = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + TIMEOUT_BACKGROUND_IMAGE)
        self.timeout_background_image = cv2.cvtColor(self.timeout_background_image, cv2.COLOR_BGR2RGB)
        self.timeout_background_image = array(self.timeout_background_image)
        self.timeout_background_image = self.timeout_background_image.astype('float64')
        self.timeout_background_image = np.rot90(self.timeout_background_image)
        self.timeout_background_image = np.rot90(self.timeout_background_image)
        self.timeout_background_image = np.rot90(self.timeout_background_image)

        self.game_over_background_image = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + GAME_OVER_BACKGROUND_IMAGE)
        self.game_over_background_image = cv2.cvtColor(self.game_over_background_image, cv2.COLOR_BGR2RGB)
        self.game_over_background_image = array(self.game_over_background_image)
        self.game_over_background_image = self.game_over_background_image.astype('float64')
        self.game_over_background_image = np.rot90(self.game_over_background_image)
        self.game_over_background_image = np.rot90(self.game_over_background_image)
        self.game_over_background_image = np.rot90(self.game_over_background_image)

        self.you_win_background_image = cv2.imread(SYSTEM_STATE_IMAGE_LOCATION + YOU_WIN_BACKGROUND_IMAGE)
        self.you_win_background_image = cv2.cvtColor(self.you_win_background_image, cv2.COLOR_BGR2RGB)
        self.you_win_background_image = array(self.you_win_background_image)
        self.you_win_background_image = self.you_win_background_image.astype('float64')
        self.you_win_background_image = np.rot90(self.you_win_background_image)
        self.you_win_background_image = np.rot90(self.you_win_background_image)
        self.you_win_background_image = np.rot90(self.you_win_background_image)

        self.image_item.setImage(self.image)

    def setup_docks_layout(self):
        self.dock_area = DockArea()
        self.setCentralWidget(self.dock_area)

        # define docks
        self.image_dock = Dock(DOCK_NAME_CENTRAL_IMAGE, size=(1092, 700))
        self.context_dock = Dock(DOCK_NAME_CONTEXT_IMAGE, size=(200, 200))
        self.timer_progress_bar_dock = Dock(DOCK_NAME_TIMER_PROGRESS_BAR, size=(546, 30))
        self.hp_dock = Dock(DOCK_NAME_HP, size=(300, 200))
        self.level_progress_bar_dock = Dock(DOCK_NAME_LEVEL_PROGRESS_BAR, size=(30, 200))
        self.level_number_dock = Dock(DOCK_NAME_LEVEL_NUMBER, size=(300, 200))
        self.tools_dock = Dock(DOCK_NAME_TOOLS, size=(500, 200))

        # hide docks' title bars
        self.image_dock.hideTitleBar()
        self.context_dock.hideTitleBar()
        self.timer_progress_bar_dock.hideTitleBar()
        self.hp_dock.hideTitleBar()
        self.level_number_dock.hideTitleBar()
        self.tools_dock.hideTitleBar()
        self.level_progress_bar_dock.hideTitleBar()

        # add docks
        self.dock_area.addDock(self.context_dock, 'top')
        self.dock_area.addDock(self.timer_progress_bar_dock, 'top', self.context_dock)
        self.dock_area.addDock(self.image_dock, 'top', self.timer_progress_bar_dock)
        self.dock_area.addDock(self.hp_dock, 'right', self.context_dock)
        self.dock_area.addDock(self.level_progress_bar_dock, 'right', self.hp_dock)
        self.dock_area.addDock(self.level_number_dock, 'right', self.level_progress_bar_dock)
        self.dock_area.addDock(self.tools_dock, 'right', self.level_number_dock)

    def setup_timer_progress_bar_widget(self):

        self.task_timer_progress_bar_widget = QtGui.QProgressBar(self)
        self.task_timer_progress_bar_widget.setGeometry(200, 80, 250, 20)
        self.task_timer_progress_bar_widget.setRange(0, 100)
        # self.timer_progress_bar_widget.setOrientation(QtCore.Qt.Vertical)

        self.timer_progress_bar_style = """
        QProgressBar{
            border: 8px solid black;
            border-radius: 5px;
            text-align: center;
            background: black;
        }

        QProgressBar::chunk {
            background-color: blue;
            width: 10px;
            margin: 1px;
        }
        """
        self.task_timer_progress_bar_widget.setStyleSheet(self.timer_progress_bar_style)
        self.timer_progress_bar_dock.addWidget(self.task_timer_progress_bar_widget)

    def setup_hp_widget(self):
        self.hp_widget = pg.GraphicsLayoutWidget()

        self.remaining_lives = MAX_NUMBER_OF_TIMEOUTS_PER_TRAINING_LEVEL

        for i in range(0, MAX_NUMBER_OF_TIMEOUTS_PER_TRAINING_LEVEL / 2):
            self.life_view_boxes.append(self.hp_widget.addViewBox(row=0, col=i))

        for i in range(0, MAX_NUMBER_OF_TIMEOUTS_PER_TRAINING_LEVEL / 2):
            self.life_view_boxes.append(self.hp_widget.addViewBox(row=1, col=i))

        self.load_hp_icon()

        for i in self.life_view_boxes:
            self.life_image_items.append(pg.ImageItem(self.life_icon))
            i.addItem(self.life_image_items[len(self.life_image_items) - 1])
            i.setAspectLocked(True)
            i.setMouseEnabled(False, False)

        # self.life_1_image_item = pg.ImageItem(self.life_icon)
        # self.life_1_view_box.addItem(self.life_1_image_item)
        # self.life_1_view_box.setAspectLocked(True)
        # self.life_1_view_box.setMouseEnabled(False, False)
        #
        # self.life_2_image_item = pg.ImageItem(self.life_icon)
        # self.life_2_view_box.addItem(self.life_2_image_item)
        # self.life_2_view_box.setAspectLocked(True)
        # self.life_2_view_box.setMouseEnabled(False, False)
        #
        # self.life_3_image_item = pg.ImageItem(self.life_icon)
        # self.life_3_view_box.addItem(self.life_3_image_item)
        # self.life_3_view_box.setAspectLocked(True)
        # self.life_3_view_box.setMouseEnabled(False, False)

        self.hp_dock.addWidget(self.hp_widget)

    def setup_level_progress_bar_widget(self):
        self.level_progress_bar_widget = QtGui.QProgressBar(self)
        self.level_progress_bar_widget.setRange(0, 100)
        self.level_progress_bar_widget.setValue(0)
        self.level_progress_bar_widget.setOrientation(QtCore.Qt.Vertical)

        self.level_progress_bar_style = """
                QProgressBar{
                    border: 8px solid black;
                    border-radius: 5px;
                    text-align: center;
                    background: black;
                }

                QProgressBar::chunk {
                    background-color: red;
                    height: 10px;
                    margin: 1px;
                }
                """
        self.level_progress_bar_widget.setStyleSheet(self.level_progress_bar_style)
        self.level_progress_bar_dock.addWidget(self.level_progress_bar_widget)

    def setup_level_number_widget(self):
        self.level_number_widget = pg.GraphicsLayoutWidget()

        self.level_icon_view_box = self.level_number_widget.addViewBox(row=0, col=0)

        self.load_level_icons()

        self.level_icon_image_item = pg.ImageItem()
        self.level_icon_view_box.addItem(self.level_icon_image_item)
        self.level_icon_view_box.setAspectLocked(True)
        self.level_icon_view_box.setMouseEnabled(False, False)

        self.update_level_number_icon()

        self.level_number_dock.addWidget(self.level_number_widget)

    def setup_tools_widget(self):
        self.tools_widget = pg.GraphicsLayoutWidget()

        self.system_state_image_view_box = self.tools_widget.addViewBox(row=0, col=1)
        self.gaze_activation_image_view_box = self.tools_widget.addViewBox(row=0, col=0)

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

    def setup_instructions_widget(self):
        pass

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

    def load_hp_icon(self):

        self.life_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LIFE_IMAGE)
        self.life_icon = cv2.cvtColor(self.life_icon, cv2.COLOR_BGR2RGB)
        self.life_icon = array(self.life_icon)
        self.life_icon = self.life_icon.astype('float64')
        self.life_icon = np.rot90(self.life_icon)
        self.life_icon = np.rot90(self.life_icon)
        self.life_icon = np.rot90(self.life_icon)

    def load_level_icons(self):
        self.level_1_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_1_ICON)
        self.level_1_icon = cv2.cvtColor(self.level_1_icon, cv2.COLOR_BGR2RGB)
        self.level_1_icon = array(self.level_1_icon)
        self.level_1_icon = self.level_1_icon.astype('float64')
        self.level_1_icon = np.rot90(self.level_1_icon)
        self.level_1_icon = np.rot90(self.level_1_icon)
        self.level_1_icon = np.rot90(self.level_1_icon)

        self.level_2_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_2_ICON)
        self.level_2_icon = cv2.cvtColor(self.level_2_icon, cv2.COLOR_BGR2RGB)
        self.level_2_icon = array(self.level_2_icon)
        self.level_2_icon = self.level_2_icon.astype('float64')
        self.level_2_icon = np.rot90(self.level_2_icon)
        self.level_2_icon = np.rot90(self.level_2_icon)
        self.level_2_icon = np.rot90(self.level_2_icon)

        self.level_3_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_3_ICON)
        self.level_3_icon = cv2.cvtColor(self.level_3_icon, cv2.COLOR_BGR2RGB)
        self.level_3_icon = array(self.level_3_icon)
        self.level_3_icon = self.level_3_icon.astype('float64')
        self.level_3_icon = np.rot90(self.level_3_icon)
        self.level_3_icon = np.rot90(self.level_3_icon)
        self.level_3_icon = np.rot90(self.level_3_icon)

        self.level_4_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_4_ICON)
        self.level_4_icon = cv2.cvtColor(self.level_4_icon, cv2.COLOR_BGR2RGB)
        self.level_4_icon = array(self.level_4_icon)
        self.level_4_icon = self.level_4_icon.astype('float64')
        self.level_4_icon = np.rot90(self.level_4_icon)
        self.level_4_icon = np.rot90(self.level_4_icon)
        self.level_4_icon = np.rot90(self.level_4_icon)

        self.level_5_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_5_ICON)
        self.level_5_icon = cv2.cvtColor(self.level_5_icon, cv2.COLOR_BGR2RGB)
        self.level_5_icon = array(self.level_5_icon)
        self.level_5_icon = self.level_5_icon.astype('float64')
        self.level_5_icon = np.rot90(self.level_5_icon)
        self.level_5_icon = np.rot90(self.level_5_icon)
        self.level_5_icon = np.rot90(self.level_5_icon)

        self.level_6_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_6_ICON)
        self.level_6_icon = cv2.cvtColor(self.level_6_icon, cv2.COLOR_BGR2RGB)
        self.level_6_icon = array(self.level_6_icon)
        self.level_6_icon = self.level_6_icon.astype('float64')
        self.level_6_icon = np.rot90(self.level_6_icon)
        self.level_6_icon = np.rot90(self.level_6_icon)
        self.level_6_icon = np.rot90(self.level_6_icon)

        self.level_7_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_7_ICON)
        self.level_7_icon = cv2.cvtColor(self.level_7_icon, cv2.COLOR_BGR2RGB)
        self.level_7_icon = array(self.level_7_icon)
        self.level_7_icon = self.level_7_icon.astype('float64')
        self.level_7_icon = np.rot90(self.level_7_icon)
        self.level_7_icon = np.rot90(self.level_7_icon)
        self.level_7_icon = np.rot90(self.level_7_icon)

        self.level_8_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_8_ICON)
        self.level_8_icon = cv2.cvtColor(self.level_8_icon, cv2.COLOR_BGR2RGB)
        self.level_8_icon = array(self.level_8_icon)
        self.level_8_icon = self.level_8_icon.astype('float64')
        self.level_8_icon = np.rot90(self.level_8_icon)
        self.level_8_icon = np.rot90(self.level_8_icon)
        self.level_8_icon = np.rot90(self.level_8_icon)

        self.level_9_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_9_ICON)
        self.level_9_icon = cv2.cvtColor(self.level_9_icon, cv2.COLOR_BGR2RGB)
        self.level_9_icon = array(self.level_9_icon)
        self.level_9_icon = self.level_9_icon.astype('float64')
        self.level_9_icon = np.rot90(self.level_9_icon)
        self.level_9_icon = np.rot90(self.level_9_icon)
        self.level_9_icon = np.rot90(self.level_9_icon)

        self.level_10_icon = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + LEVEL_10_ICON)
        self.level_10_icon = cv2.cvtColor(self.level_10_icon, cv2.COLOR_BGR2RGB)
        self.level_10_icon = array(self.level_10_icon)
        self.level_10_icon = self.level_10_icon.astype('float64')
        self.level_10_icon = np.rot90(self.level_10_icon)
        self.level_10_icon = np.rot90(self.level_10_icon)
        self.level_10_icon = np.rot90(self.level_10_icon)

    def load_targets_images(self):
        self.target_1_image = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + TARGET_1_IMAGE)
        self.target_1_image = cv2.cvtColor(self.target_1_image, cv2.COLOR_BGR2RGB)
        self.target_1_image = array(self.target_1_image)
        self.target_1_image = self.target_1_image.astype('float64')
        self.target_1_image = np.rot90(self.target_1_image)
        self.target_1_image = np.rot90(self.target_1_image)
        self.target_1_image = np.rot90(self.target_1_image)

        self.target_1_selected_image = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + TARGET_1_SELECTED_IMAGE)
        self.target_1_selected_image = array(self.target_1_selected_image)
        self.target_1_selected_image = self.target_1_selected_image.astype('float64')
        self.target_1_selected_image = np.rot90(self.target_1_selected_image)
        self.target_1_selected_image = np.rot90(self.target_1_selected_image)
        self.target_1_selected_image = np.rot90(self.target_1_selected_image)

        self.target_2_image = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + TARGET_2_IMAGE)
        self.target_2_image = array(self.target_2_image)
        self.target_2_image = self.target_2_image.astype('float64')
        self.target_2_image = np.rot90(self.target_2_image)
        self.target_2_image = np.rot90(self.target_2_image)
        self.target_2_image = np.rot90(self.target_2_image)

        self.target_2_selected_image = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + TARGET_2_SELECTED_IMAGE)
        self.target_2_selected_image = array(self.target_2_selected_image)
        self.target_2_selected_image = self.target_2_selected_image.astype('float64')
        self.target_2_selected_image = np.rot90(self.target_2_selected_image)
        self.target_2_selected_image = np.rot90(self.target_2_selected_image)
        self.target_2_selected_image = np.rot90(self.target_2_selected_image)

        self.target_3_image = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + TARGET_3_IMAGE)
        self.target_3_image = array(self.target_3_image)
        self.target_3_image = self.target_3_image.astype('float64')
        self.target_3_image = np.rot90(self.target_3_image)
        self.target_3_image = np.rot90(self.target_3_image)
        self.target_3_image = np.rot90(self.target_3_image)

        self.target_3_selected_image = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + TARGET_3_SELECTED_IMAGE)
        self.target_3_selected_image = array(self.target_3_selected_image)
        self.target_3_selected_image = self.target_3_selected_image.astype('float64')
        self.target_3_selected_image = np.rot90(self.target_3_selected_image)
        self.target_3_selected_image = np.rot90(self.target_3_selected_image)
        self.target_3_selected_image = np.rot90(self.target_3_selected_image)

        self.target_4_image = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + TARGET_4_IMAGE)
        self.target_4_image = array(self.target_4_image)
        self.target_4_image = self.target_4_image.astype('float64')
        self.target_4_image = np.rot90(self.target_4_image)
        self.target_4_image = np.rot90(self.target_4_image)
        self.target_4_image = np.rot90(self.target_4_image)

        self.target_4_selected_image = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + TARGET_4_SELECTED_IMAGE)
        self.target_4_selected_image = array(self.target_4_selected_image)
        self.target_4_selected_image = self.target_4_selected_image.astype('float64')
        self.target_4_selected_image = np.rot90(self.target_4_selected_image)
        self.target_4_selected_image = np.rot90(self.target_4_selected_image)
        self.target_4_selected_image = np.rot90(self.target_4_selected_image)

        self.destroyed_target_image = cv2.imread(
            SYSTEM_STATE_IMAGE_LOCATION + TARGET_DESTROYED_IMAGE)
        self.destroyed_target_image = array(self.destroyed_target_image)
        self.destroyed_target_image = self.destroyed_target_image.astype('float64')
        self.destroyed_target_image = np.rot90(self.destroyed_target_image)
        self.destroyed_target_image = np.rot90(self.destroyed_target_image)
        self.destroyed_target_image = np.rot90(self.destroyed_target_image)

        self.target_image_item = pg.ImageItem()
        self.context_target_image_item = pg.ImageItem()
        self.image_view_box.addItem(self.target_image_item)
        self.context_image_view_box.addItem(self.context_target_image_item)

    def setup_gaze_indicators(self):
        pass

    # </editor-fold>

    # <editor-fold desc="game gui functions">
    def show_counter_to_start_game_screen(self):
        count_to_start_time_elapsed = int(round(time.time() - self.counting_to_start_timer, 1))

        if count_to_start_time_elapsed == 0:
            if not self.counter_1_flag:
                self.image_item.setImage(self.counter_background_image_3)
                self.play_sound(SoundType.COUNTER)
                self.counter_1_flag = True
                self.counter_2_flag = False
                self.counter_3_flag = False
                self.counter_go_flag = False

        if count_to_start_time_elapsed == 1:
            if not self.counter_2_flag:
                self.image_item.setImage(self.counter_background_image_2)
                self.play_sound(SoundType.COUNTER)
                self.counter_1_flag = False
                self.counter_2_flag = True
                self.counter_3_flag = False
                self.counter_go_flag = False

        if count_to_start_time_elapsed == 2:
            if not self.counter_3_flag:
                self.image_item.setImage(self.counter_background_image_1)
                self.play_sound(SoundType.COUNTER)
                self.counter_1_flag = False
                self.counter_2_flag = False
                self.counter_3_flag = True
                self.counter_go_flag = False

        if count_to_start_time_elapsed == 3:
            if not self.counter_go_flag:
                self.image_item.setImage(self.counter_background_image_go)
                self.play_sound(SoundType.GO)
                self.counter_1_flag = False
                self.counter_2_flag = False
                self.counter_3_flag = False
                self.counter_go_flag = True

        if count_to_start_time_elapsed == 4:
            self.counting_to_start_timer = None
            self.counter_1_flag = False
            self.counter_2_flag = False
            self.counter_3_flag = False
            self.counter_go_flag = False

    def generate_and_display_new_target(self):
        self.target_image_item.clear()
        self.context_target_image_item.clear()

        x_threshold = self.image_width * 0.15
        y_threshold = self.image_height * 0.15

        target = random.randrange(0, 2)

        if target == 1:
            self.target_image = self.target_1_image
            self.selected_target_image = self.target_1_selected_image
            self.current_target_shape = TARGET_1_IMAGE
        else:
            self.target_image = self.target_4_image
            self.selected_target_image = self.target_4_selected_image
            self.current_target_shape = TARGET_4_IMAGE

        if GRAPHICAL_EXPERIMENT == 1:
            w_h = random.randrange(100, 300)
            x = random.randrange(int(x_threshold), int(self.image_width - w_h - x_threshold))
            y = random.randrange(int(y_threshold), int(self.image_height - w_h - y_threshold))
            rect = QtCore.QRect(x, y, w_h, w_h)

        elif GRAPHICAL_EXPERIMENT == 2:
            random_dimension = random.randrange(300, 400)

            if self.current_target_shape == TARGET_1_IMAGE:
                h = random_dimension
                w = h / 3.5752

            elif self.current_target_shape == TARGET_4_IMAGE:
                w = random_dimension
                h = w / 3.5752

            x = random.randrange(int(x_threshold), int(self.image_width - w - x_threshold))
            y = random.randrange(int(y_threshold), int(self.image_height - h - y_threshold))
            rect = QtCore.QRect(x, y, w, h)

            self.current_task_roi.setPos(QtCore.QPoint(x, y))
            self.current_task_roi.setSize(QtCore.QPoint(w, h))

        self.target_image_item.setImage(self.target_image, opacity=1)
        self.context_target_image_item.setImage(self.selected_target_image, opacity=1)

        self.target_image_item.setRect(rect)
        self.context_target_image_item.setRect(rect)

    def update_level_number_icon(self):

        if self.current_game_level == GameLevel.LEVEL_1:
            if self.current_level_icon != GameLevel.LEVEL_1:
                self.level_icon_image_item.setImage(self.level_1_icon)
                self.current_level_icon = GameLevel.LEVEL_1

        elif self.current_game_level == GameLevel.LEVEL_2:
            if self.current_level_icon != GameLevel.LEVEL_2:
                self.level_icon_image_item.setImage(self.level_2_icon)
                self.current_level_icon = GameLevel.LEVEL_2

        elif self.current_game_level == GameLevel.LEVEL_3:
            if self.current_level_icon != GameLevel.LEVEL_3:
                self.level_icon_image_item.setImage(self.level_3_icon)
                self.current_level_icon = GameLevel.LEVEL_3

        elif self.current_game_level == GameLevel.LEVEL_4:
            if self.current_level_icon != GameLevel.LEVEL_4:
                self.level_icon_image_item.setImage(self.level_4_icon)
                self.current_level_icon = GameLevel.LEVEL_4

        elif self.current_game_level == GameLevel.LEVEL_5:
            if self.current_level_icon != GameLevel.LEVEL_5:
                self.level_icon_image_item.setImage(self.level_5_icon)
                self.current_level_icon = GameLevel.LEVEL_5

        elif self.current_game_level == GameLevel.LEVEL_6:
            if self.current_level_icon != GameLevel.LEVEL_6:
                self.level_icon_image_item.setImage(self.level_6_icon)
                self.current_level_icon = GameLevel.LEVEL_6

        elif self.current_game_level == GameLevel.LEVEL_7:
            if self.current_level_icon != GameLevel.LEVEL_7:
                self.level_icon_image_item.setImage(self.level_7_icon)
                self.current_level_icon = GameLevel.LEVEL_7

        elif self.current_game_level == GameLevel.LEVEL_8:
            if self.current_level_icon != GameLevel.LEVEL_8:
                self.level_icon_image_item.setImage(self.level_8_icon)
                self.current_level_icon = GameLevel.LEVEL_8

        elif self.current_game_level == GameLevel.LEVEL_9:
            if self.current_level_icon != GameLevel.LEVEL_9:
                self.level_icon_image_item.setImage(self.level_9_icon)
                self.current_level_icon = GameLevel.LEVEL_9

        elif self.current_game_level == GameLevel.LEVEL_10:
            if self.current_level_icon != GameLevel.LEVEL_10:
                self.level_icon_image_item.setImage(self.level_10_icon)
                self.current_level_icon = GameLevel.LEVEL_10

    def blink_existing_target(self):
        try:
            target_time_elapsed = round(time.time() - self.blinking_target_timer, 1)

            if target_time_elapsed == 0.0:
                if self.target_selected_flag:
                    self.target_image_item.setImage(self.selected_target_image, opacity=1)
                    self.context_target_image_item.setImage(self.selected_target_image, opacity=1)
                else:
                    self.target_image_item.setImage(self.target_image, opacity=1)
                    self.context_target_image_item.setImage(self.target_image, opacity=1)

            if target_time_elapsed == 0.5:
                if self.target_selected_flag:
                    self.target_image_item.setImage(self.selected_target_image, opacity=0.7)
                    self.context_target_image_item.setImage(self.selected_target_image, opacity=0.7)
                else:
                    self.target_image_item.setImage(self.target_image, opacity=1)
                    self.context_target_image_item.setImage(self.target_image, opacity=1)

            if target_time_elapsed == 1.0:
                if self.target_selected_flag:
                    self.target_image_item.setImage(self.selected_target_image, opacity=1)
                    self.context_target_image_item.setImage(self.selected_target_image, opacity=1)
                else:
                    self.target_image_item.setImage(self.target_image, opacity=1)
                    self.context_target_image_item.setImage(self.target_image, opacity=1)

            if target_time_elapsed == 1.5:
                if self.target_selected_flag:
                    self.target_image_item.setImage(self.selected_target_image, opacity=0.7)
                    self.context_target_image_item.setImage(self.selected_target_image, opacity=0.7)
                else:
                    self.target_image_item.setImage(self.target_image, opacity=1)
                    self.context_target_image_item.setImage(self.target_image, opacity=1)

            if target_time_elapsed == 2.0:
                if self.target_selected_flag:
                    self.target_image_item.setImage(self.selected_target_image, opacity=1)
                    self.context_target_image_item.setImage(self.selected_target_image, opacity=1)
                else:
                    self.target_image_item.setImage(self.target_image, opacity=0)
                    self.context_target_image_item.setImage(self.target_image, opacity=0)

            if target_time_elapsed == 2.5:
                if self.target_selected_flag:
                    self.target_image_item.setImage(self.selected_target_image, opacity=0.7)
                    self.context_target_image_item.setImage(self.selected_target_image, opacity=0.7)
                else:
                    if not self.target_blink_on_flag:
                        self.play_sound(SoundType.TARGET_BLINK)
                        self.target_image_item.setImage(self.target_image, opacity=1)
                        self.context_target_image_item.setImage(self.target_image, opacity=1)
                        self.target_blink_on_flag = True

            if target_time_elapsed == 3.0:
                if self.target_selected_flag:
                    self.target_image_item.setImage(self.selected_target_image, opacity=1)
                    self.context_target_image_item.setImage(self.selected_target_image, opacity=1)
                else:
                    self.target_image_item.setImage(self.target_image, opacity=0)
                    self.context_target_image_item.setImage(self.target_image, opacity=0)
                self.blinking_target_timer = time.time()
                self.target_blink_on_flag = False
        except:
            pass

    def show_target_being_destroyed(self):
        target_destroyed_time_elapsed = time.time() - self.destroying_target_timer
        self.target_image_item.setImage(self.destroyed_target_image, opacity=1)
        self.context_target_image_item.setImage(self.destroyed_target_image, opacity=1)

        if target_destroyed_time_elapsed >= 0.5:
            self.target_image_item.clear()
            self.context_target_image_item.clear()
            self.destroying_target_timer = None

    def show_level_up_screen(self):
        message_time_elapsed = int(round(time.time() - self.leveling_up_timer, 1))
        self.image_item.setImage(self.counter_background_image_level_up)
        self.level_progress_bar_widget.setValue(self.required_number_of_consecutive_tasks_per_level)
        if message_time_elapsed == 1:
            self.leveling_up_timer = None

    def show_timeout_screen(self):
        self.target_image_item.clear()
        self.context_target_image_item.clear()
        message_time_out = int(round(time.time() - self.timeout_screen_timer, 1))
        self.image_item.setImage(self.timeout_background_image)
        self.task_timer_progress_bar_widget.setValue(self.task_time_limit)
        if message_time_out == 1:
            self.timeout_screen_timer = None

    def show_game_over_screen(self):
        self.image_item.setImage(self.game_over_background_image)

    def show_you_win_screen(self):
        self.image_item.setImage(self.you_win_background_image)

    def set_game_state(self, state):

        if state == GameState.IDLE:
            self.current_game_state = GameState.IDLE

        elif state == GameState.COUNTING_TO_START:
            self.current_game_state = GameState.COUNTING_TO_START
            self.counting_to_start_timer = time.time()
            if self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING or \
                            self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING or \
                            self.user_study_state == AbstractUserStudyState.MANUAL_DEMO or \
                            self.user_study_state == AbstractUserStudyState.GAZE_DEMO:
                self.total_level_score = 0
                self.level_progress_bar_widget.setValue(self.total_level_score)
            self.task_timer_progress_bar_widget.setValue(0)

        elif state == GameState.TASK_RUNNING:
            self.current_game_state = GameState.TASK_RUNNING
            self.blinking_target_timer = time.time()
            self.go_to_next_task()
            self.image_item.setImage(self.image)

        elif state == GameState.DESTROYING_TARGET:
            self.play_sound(SoundType.CAPTURE_HIT)
            self.current_game_state = GameState.DESTROYING_TARGET
            self.destroying_target_timer = time.time()

        elif state == GameState.LEVELING_UP:
            self.highest_passed_training_level = self.current_game_level
            self.play_sound(SoundType.LEVEL_UP)
            self.current_game_state = GameState.LEVELING_UP
            self.leveling_up_timer = time.time()
            self.restore_hp_points()

        elif state == GameState.TIMEOUT_SCREEN:
            self.play_sound(SoundType.TIMEOUT)
            self.current_game_state = GameState.TIMEOUT_SCREEN
            self.timeout_screen_timer = time.time()

            self.reset_all_values()
            self.keypress_Q()
            self.keypress_Q()
            self.keypress_Q()

        elif state == GameState.GAME_OVER_SCREEN:
            self.play_sound(SoundType.GAME_OVER)
            self.current_game_state = GameState.GAME_OVER_SCREEN

        elif state == GameState.YOU_WIN_SCREEN:
            self.play_sound(SoundType.LEVEL_UP)
            self.current_game_state = GameState.YOU_WIN_SCREEN

    def remove_hp_point(self):

        if self.remaining_lives > 0:
            self.remaining_lives -= 1
            try:
                self.life_image_items[self.remaining_lives].setImage(self.life_image, opacity=0)
            except:
                pass

        print "remaining lives:" + str(self.remaining_lives)

    def restore_hp_points(self):
        for i in self.life_image_items:
            i.setImage(self.life_image, opacity=1)

        if self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING or \
                        self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:
            self.remaining_lives = MAX_NUMBER_OF_TIMEOUTS_PER_TRAINING_LEVEL

        elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED or \
                        self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
            self.remaining_lives = MAX_NUMBER_OF_TIMEOUTS_PER_RECORDED_LEVEL

        else:
            self.remaining_lives = 5

    # </editor-fold>

    # <editor-fold desc="game logic functions">

    def calculate_new_time_limit(self):

        if self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED or \
                        self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED:
            level_reference = self.highest_passed_training_level - 1
        else:
            level_reference = self.highest_passed_training_level

        level = None
        calculate_from_training_session = False

        if self.current_game_level == GameLevel.LEVEL_1:
            calculate_from_training_session = True
        elif self.current_game_level == GameLevel.LEVEL_2:
            level = GameLevel.LEVEL_1
        elif self.current_game_level == GameLevel.LEVEL_3:
            level = GameLevel.LEVEL_2
        elif self.current_game_level == GameLevel.LEVEL_4:
            level = GameLevel.LEVEL_3
        elif self.current_game_level == GameLevel.LEVEL_5:
            level = GameLevel.LEVEL_4
        elif self.current_game_level == GameLevel.LEVEL_6:
            level = GameLevel.LEVEL_5
        elif self.current_game_level == GameLevel.LEVEL_7:
            level = GameLevel.LEVEL_6
        elif self.current_game_level == GameLevel.LEVEL_8:
            level = GameLevel.LEVEL_7
        elif self.current_game_level == GameLevel.LEVEL_9:
            level = GameLevel.LEVEL_8
        elif self.current_game_level == GameLevel.LEVEL_10:
            level = GameLevel.LEVEL_9

        total = 0
        count = 0
        if level is not None:
            for i in self.total_logs:
                if i['level'] == level:
                    if i['user study state'] == self.user_study_state:
                        total += i['time elapsed']
                        count += 1

        else:
            if calculate_from_training_session:
                for i in self.total_logs:
                    if i['level'] == level_reference:
                        if self.interaction == Interaction.GAZE_SUPPORTED:
                            if i['user study state'] == AbstractUserStudyState.GAZE_PPT_TRAINING:
                                total += i['time elapsed']
                                count += 1
                        elif self.interaction == Interaction.MANUAL_BASED:
                            if i['user study state'] == AbstractUserStudyState.MANUAL_PPT_TRAINING:
                                total += i['time elapsed']
                                count += 1
                print "calculated new timing from training level #" + str(level_reference)

        if count == 0:
            if GRAPHICAL_EXPERIMENT == 1:
                self.task_time_limit = LEVEL1_TIME_LIMIT_REGULAR
            elif GRAPHICAL_EXPERIMENT == 2:
                self.task_time_limit = LEVEL1_TIME_LIMIT_IRREGULAR
        else:
            self.task_time_limit = total / count

        print "task time limit = " + str(self.task_time_limit)

    def setup_game_variables(self):
        if GRAPHICAL_EXPERIMENT == 1:
            self.task_time_limit = LEVEL1_TIME_LIMIT_REGULAR
        elif GRAPHICAL_EXPERIMENT == 2:
            self.task_time_limit = LEVEL1_TIME_LIMIT_IRREGULAR

        self.maximum_number_of_levels = MAXIMUM_NUMBER_OF_LEVELS

        self.task_timer_progress_bar_widget.setRange(0, self.task_time_limit)

        self.current_task_roi = pg.RectROI([0, 0], [self.default_roi_width, self.default_roi_height], movable=True,
                                           maxBounds=QtCore.QRectF(0, 0, self.image_width, self.image_height))

        self.image_view_box.addItem(self.current_task_roi)
        self.current_task_roi.hide()

    def start_game(self):
        self.reset_all_values()
        self.update_level_number_icon()

        if self.total_number_of_started_tasks == 0:
            self.restore_hp_points()

        if self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING or \
                        self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:

            self.required_number_of_consecutive_tasks_per_level = TOTAL_NUMBER_OF_REQUIRED_CONSECUTIVE_CORRECT_TASKS
            self.level_progress_bar_widget.setRange(0, self.required_number_of_consecutive_tasks_per_level)

        elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED or \
                        self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED:

            self.required_number_of_consecutive_tasks_per_level = TOTAL_NUMBER_OF_RECORDED_TASKS
            self.level_progress_bar_widget.setRange(0, TOTAL_NUMBER_OF_RECORDED_TASKS)

        else:
            self.required_number_of_consecutive_tasks_per_level = 3
            self.level_progress_bar_widget.setRange(0, self.required_number_of_consecutive_tasks_per_level)

        if self.current_game_level <= self.maximum_number_of_levels and self.remaining_lives > 0:
            self.calculate_new_time_limit()
            self.task_timer_progress_bar_widget.setRange(0, self.task_time_limit)
            print "task number: " + str(self.total_number_of_started_tasks)
            self.set_game_state(GameState.COUNTING_TO_START)
        else:
            self.end_game()

    def end_game(self):
        self.set_game_state(GameState.GAME_OVER_SCREEN)

    def set_game_level(self, level):
        self.current_game_level = level

        self.calculate_new_time_limit()

        self.task_timer_progress_bar_widget.setRange(0, self.task_time_limit)

    def terminate_level(self):
        self.reset_all_values()
        self.end_current_task()
        if self.leveled_up:
            self.leveled_up = False
        self.start_game()

    def go_to_next_game_level(self):

        if self.current_game_level == GameLevel.LEVEL_1:
            if self.maximum_number_of_levels == 1:
                self.end_game()
            else:
                self.set_game_level(GameLevel.LEVEL_2)

        elif self.current_game_level == GameLevel.LEVEL_2:
            if self.maximum_number_of_levels == 2:
                self.end_game()
            else:
                self.set_game_level(GameLevel.LEVEL_3)

        elif self.current_game_level == GameLevel.LEVEL_3:
            if self.maximum_number_of_levels == 3:
                self.end_game()
            else:
                self.set_game_level(GameLevel.LEVEL_4)

        elif self.current_game_level == GameLevel.LEVEL_4:
            if self.maximum_number_of_levels == 4:
                self.end_game()
            else:
                self.set_game_level(GameLevel.LEVEL_5)

        elif self.current_game_level == GameLevel.LEVEL_5:
            if self.maximum_number_of_levels == 5:
                self.end_game()
            else:
                self.set_game_level(GameLevel.LEVEL_6)

        elif self.current_game_level == GameLevel.LEVEL_6:
            if self.maximum_number_of_levels == 6:
                self.end_game()
            else:
                self.set_game_level(GameLevel.LEVEL_7)

        elif self.current_game_level == GameLevel.LEVEL_7:
            if self.maximum_number_of_levels == 7:
                self.end_game()
            else:
                self.set_game_level(GameLevel.LEVEL_8)

        elif self.current_game_level == GameLevel.LEVEL_8:
            if self.maximum_number_of_levels == 8:
                self.end_game()
            else:
                self.set_game_level(GameLevel.LEVEL_9)

        elif self.current_game_level == GameLevel.LEVEL_9:
            if self.maximum_number_of_levels == 9:
                self.end_game()
            else:
                self.set_game_level(GameLevel.LEVEL_10)

        elif self.current_game_level == GameLevel.LEVEL_10:
            if self.maximum_number_of_levels == 10:
                self.end_game()

        self.total_number_of_started_tasks = 0

    def check_for_sufficient_target_framing(self):

        self.containing_rect = QtCore.QRect(self.detail_view_roi.pos().x(), self.detail_view_roi.pos().y(),
                                       self.detail_view_roi.size().x(), self.detail_view_roi.size().y())

        self.target_rect = QtCore.QRect(self.current_task_roi.pos().x(), self.current_task_roi.pos().y(),
                                   self.current_task_roi.size().x(), self.current_task_roi.size().y())

        if GRAPHICAL_EXPERIMENT == 1:

            if self.containing_rect.intersects(self.target_rect):

                intersection = self.containing_rect.intersected(self.target_rect)

                intersection_area = intersection.width() * intersection.height()
                target_rect_area = self.target_rect.width() * self.target_rect.height()

                if (intersection_area * 1.0 / target_rect_area * 1.0) * 100 >= MIN_INTERSECTION_PERCENTAGE:

                    if round((self.current_task_roi.size().x() / self.detail_view_roi.size().x()), 2) * 100 \
                            >= MIN_ZOOM_PERCENTAGE \
                            and round((self.current_task_roi.size().y() / self.detail_view_roi.size().y()), 2) * 100 \
                                    >= MIN_ZOOM_PERCENTAGE:

                        self.target_selected_flag = True

                    else:
                        self.target_selected_flag = False
                else:
                    self.target_selected_flag = False
            else:
                self.target_selected_flag = False

        elif GRAPHICAL_EXPERIMENT == 2:

                # intersection = containing_rect.intersected(target_rect)

                # intersection_area = intersection.width() * intersection.height()
                # target_rect_area = target_rect.width() * target_rect.height()

                # if (intersection_area * 1.0 / target_rect_area * 1.0) * 100 >= MIN_INTERSECTION_PERCENTAGE:

                if self.containing_rect.contains(self.target_rect):

                    if round((self.target_rect.width() * 1.0 / self.containing_rect.width() * 1.0), 2) * 100 \
                            >= 50.0 \
                            and round((self.target_rect.height() * 1.0 / self.containing_rect.height() * 1.0), 2) * 100 \
                            >= 50.0:

                        self.target_selected_flag = True
                    else:
                        self.target_selected_flag = False
                else:
                    self.target_selected_flag = False



    @staticmethod
    def play_sound(sound_type):
        if sound_type == SoundType.CAPTURE_NO_HIT:
            QtGui.QSound.play(SOUNDS_LOCATION + SOUND_CAPTURE_NO_HIT)

        if sound_type == SoundType.CAPTURE_HIT:
            QtGui.QSound.play(SOUNDS_LOCATION + SOUND_CAPTURE_HIT)

        if sound_type == SoundType.GO:
            QtGui.QSound.play(SOUNDS_LOCATION + SOUND_GO)

        if sound_type == SoundType.TIMEOUT:
            QtGui.QSound.play(SOUNDS_LOCATION + SOUND_TIMEOUT)

        if sound_type == SoundType.GAME_OVER:
            QtGui.QSound.play(SOUNDS_LOCATION + SOUND_GAME_OVER)

        if sound_type == SoundType.LEVEL_UP:
            QtGui.QSound.play(SOUNDS_LOCATION + SOUND_LEVEL_UP)

        if sound_type == SoundType.TARGET_BLINK:
            # QtGui.QSound.play(SOUNDS_LOCATION + SOUND_TARGET_BLINK)
            pass

        if sound_type == SoundType.COUNTER:
            QtGui.QSound.play(SOUNDS_LOCATION + SOUND_COUNTER)

    # </editor-fold>

    # <editor-fold desc="values update functions">

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
            super(GamifiedUserStudyBase, self).start_threads()

    # </editor-fold>

    # <editor-fold desc="callback functions">

    def callback_arduino_update(self, info):
        super(GamifiedUserStudyBase, self).callback_arduino_update(info)

        self.key_logs.append((info, time.time()))

    def callback_values_update(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).callback_values_update()
        else:
            super(GamifiedUserStudyBase, self).callback_values_update()

        if self.prev_roi is None or (self.prev_roi[0]) != (self.roi.pos().x())\
                or (self.prev_roi[1]) != (self.roi.pos().y()):

            self.prev_roi = (self.roi.pos().x(), self.roi.pos().y(), self.roi.size().x(), self.roi.size().y())
            self.roi_logs.append((self.prev_roi, self.task_time_elapsed))

        # <editor-fold desc="update UI">
        self.update_system_state_image()
        # </editor-fold>

        # <editor-fold desc="update cursor key log">
        if len(self.key_logs) > 0:

            flags, hcursor, (x, y) = win32gui.GetCursorInfo()

            self.current_cursor_x = x
            self.current_cursor_y = y

            if self.current_cursor_y != self.prev_cursor_y or self.current_cursor_x != self.prev_cursor_x:

                cursor_log = ("Cursor", time.time())

                prev_log = self.key_logs[len(self.key_logs) - 1][0]

                if prev_log != cursor_log[0]:
                    self.key_logs.append(cursor_log)
                    print cursor_log[0]

                self.prev_cursor_y = self.current_cursor_y
                self.prev_cursor_x = self.current_cursor_x
        # </editor-fold>

        # <editor-fold desc="game-related updates">
        if self.current_game_state == GameState.COUNTING_TO_START:
            self.show_counter_to_start_game_screen()
            if self.counting_to_start_timer is None:
                self.reset_all_values()
                self.keypress_Q()
                self.keypress_Q()
                self.keypress_Q()
                self.set_game_state(GameState.TASK_RUNNING)

        elif self.current_game_state == GameState.TASK_RUNNING:
            if self.counting_time_on_task:
                self.blink_existing_target()
                self.check_for_sufficient_target_framing()

                self.task_time_elapsed = round(time.time() - self.current_task_timer, 1)
                # update task timer gui
                if self.counting_time_on_task:
                    self.task_timer_progress_bar_widget.setValue(self.task_time_elapsed)

                # timer check for timeout
                if self.task_time_elapsed >= self.task_time_limit:
                    self.target_selected_flag = True
                    self.keypress_R()
                    self.target_selected_flag = False
                    self.task_timed_out = True

                if self.target_captured:
                    if self.task_timed_out:
                        self.end_current_task()
                        self.task_timer_progress_bar_widget.setValue(0)
                        self.set_game_state(GameState.TIMEOUT_SCREEN)
                        self.remove_hp_point()
                    else:
                        self.total_level_score += 1
                        self.level_progress_bar_widget.setValue(self.total_level_score)

                        self.set_game_state(GameState.DESTROYING_TARGET)

                        self.end_current_task()
                        self.task_timer_progress_bar_widget.setValue(0)
            else:
                if not self.target_captured:
                    self.start_current_task()
                    self.generate_and_display_new_target()
                    self.blinking_target_timer = time.time()

        elif self.current_game_state == GameState.TIMEOUT_SCREEN:
            if self.timeout_screen_timer is not None:
                self.show_timeout_screen()
            else:
                self.terminate_level()

        elif self.current_game_state == GameState.DESTROYING_TARGET:
            if self.destroying_target_timer is not None:
                self.show_target_being_destroyed()
            else:
                self.reset_all_values()
                self.keypress_Q()
                self.keypress_Q()
                self.keypress_Q()

                if self.total_level_score == self.required_number_of_consecutive_tasks_per_level:
                    self.terminate_level()
                    self.set_game_state(GameState.LEVELING_UP)
                else:
                    self.set_game_state(GameState.TASK_RUNNING)

        elif self.current_game_state == GameState.LEVELING_UP:
            if self.leveling_up_timer is not None:
                if not self.leveled_up:
                    self.go_to_next_game_level()
                    self.update_level_number_icon()
                    self.leveled_up = True
                else:
                    self.show_level_up_screen()
            else:
                self.terminate_level()

        elif self.current_game_state == GameState.GAME_OVER_SCREEN:
            self.show_game_over_screen()

        elif self.current_game_state == GameState.YOU_WIN_SCREEN:
            self.show_you_win_screen()
            # </editor-fold>

    def callback_update_POG(self, info):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).callback_update_POG(info)
        else:
            super(GamifiedUserStudyBase, self).callback_update_POG(info)

        # <editor-fold desc="logging-related">
        self.pog_x_y_d_time = [self.POG.x(), self.POG.y(), self.fixation_duration, time.time(), self.valid_POG_flag]

        if self.record_pog_flag:
            self.pog_log.append([self.user_study_state, self.total_number_of_started_tasks, self.pog_x_y_d_time])
            # </editor-fold>

    def callback_input_held_monitor(self):
        super(GamifiedUserStudyBase, self).callback_input_held_monitor()

        if self.gaze_activation_held or self.gaze_activation_pressed:
            if not self.is_gaze_icon_set:
                self.gaze_image_item.setImage(self.gaze_icon)
                self.is_gaze_icon_set = True
        else:
            if self.is_gaze_icon_set:
                self.gaze_image_item.clear()
                self.is_gaze_icon_set = False
                pos = self.roi.pos()
                pos = self.image_view_box.mapViewToScene(pos)
                win32api.SetCursorPos((int(pos.x()), int(pos.y())))

    # </editor-fold>

    # <editor-fold desc="timer-related functions">
    def start_timer(self):
        self.current_task_timer = time.time()
        self.counting_time_on_task = True

        self.key_logs = []
        self.roi_logs = []

    def stop_timer(self):
        time_elapsed = time.time() - self.current_task_timer
        time_elapsed_list_item = [self.user_study_state, self.total_number_of_started_tasks, time_elapsed]
        self.list_task_times_elapsed.append(time_elapsed_list_item)

        target_rect = QtCore.QRect(self.current_task_roi.pos().x() + self.current_task_roi.size().x() / 2,
                                   self.current_task_roi.pos().y() + self.current_task_roi.size().y() / 2,
                                   self.current_task_roi.size().x(), self.current_task_roi.size().y())

        log_item = {'user study state': self.user_study_state,
                    'level': self.current_game_level,
                    'level score': self.total_level_score,
                    'time elapsed': time_elapsed,
                    'total tasks started this level': self.total_number_of_started_tasks,
                    'remaining lives': self.remaining_lives,
                    'timeout': self.task_timed_out,
                    'target rect': target_rect,
                    'target shape': self.current_target_shape,
                    'key logs': self.key_logs,
                    'roi logs': self.roi_logs
                    }
        print log_item
        self.total_logs.append(log_item)
        self.counting_time_on_task = False

    def reset_task_timer(self):
        self.current_task_timer = None

    def print_elapsed_times(self):
        print "Total elapsed times:"
        for i in range(0, len(self.list_task_times_elapsed)):
            print self.list_task_times_elapsed[i]

    # </editor-fold>

    # <editor-fold desc="data logging functions">

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

    @staticmethod
    def log_list_to_file(input_list, directory, file_name):

        with open(directory + file_name, 'wb') as f:
            pickle.dump(input_list, f)

    def log_elapsed_times_to_file(self):
        location = self.location_header + DIR_ELAPSED_TIMES + "/"

        self.log_list_to_file(self.list_task_times_elapsed, location,
                              self.file_name_header + FILE_NAME_TIMES_ELAPSED_SCORES)

        self.log_list_to_file(self.total_logs, location, self.file_name_header + FILE_NAME_TOTAL_LOGS)

        print "timer score logged to " + location + self.file_name_header + FILE_NAME_TIMES_ELAPSED_SCORES

    def log_fixation_data_to_file(self):
        location = self.location_header + DIR_POG_LOGS + "/"

        self.log_list_to_file(self.pog_log, location,
                              self.file_name_header + str(self.total_number_of_started_tasks) + "_" + FILE_NAME_POG_LOG)

        print "fixations data logged to " + location + self.file_name_header + \
              str(self.total_number_of_started_tasks) + "_" + \
              FILE_NAME_POG_LOG

    def log_all_task_values_to_file(self):
        self.print_elapsed_times()
        self.log_elapsed_times_to_file()

        self.log_fixation_data_to_file()

    # </editor-fold>

    # <editor-fold desc="researcher tools functions">

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

    def clear_values_logs(self):
        # reset tasks
        self.total_number_of_started_tasks = 0

        # clear fixation points
        self.pog_log = []

        # clear elapsed times
        self.list_task_times_elapsed = []

    def reset_all_values(self):

        # <editor-fold desc="reset system state">
        self.set_system_state(SystemState.FULLSCALE)
        # </editor-fold>

        # <editor-fold desc="reset roi">
        self.set_roi_to_default_pos_and_size()
        # </editor-fold>

        # <editor-fold desc="reset timer">
        self.reset_task_timer()
        # </editor-fold>

        # <editor-fold desc="reset fixation logs">
        self.pog_log = []
        # </editor-fold>

        # <editor-fold desc="reset task values">
        self.target_captured = False
        self.task_timed_out = False
        # </editor-fold>

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

    def go_to_next_task(self):

        self.total_number_of_started_tasks += 1

    def go_to_previous_task(self):

        self.total_number_of_started_tasks -= 1
        if self.total_number_of_started_tasks < 0:
            self.total_number_of_started_tasks = 0

    def start_current_task(self):
        self.start_timer()
        self.record_pog_flag = True

    def end_current_task(self):
        # stop timer to log elapsed time
        try:
            self.stop_timer()
        except:
            print "timer has not been started"

        # stop collecting fixations for logging
        self.record_pog_flag = False

        if LOG_RESULTS_FLAG:
            # log everything
            self.log_all_task_values_to_file()

    def set_user_study_state(self, state):

        # clear all logs
        self.clear_values_logs()

        # then reset the values
        self.reset_all_values()

        # reset level
        self.current_game_level = GameLevel.LEVEL_1

        if state == AbstractUserStudyState.INTRODUCTION:
            self.user_study_state = AbstractUserStudyState.INTRODUCTION

        elif state == AbstractUserStudyState.MANUAL_DEMO:
            self.switch_interaction(Interaction.MANUAL_BASED)
            self.user_study_state = AbstractUserStudyState.MANUAL_DEMO

        elif state == AbstractUserStudyState.MANUAL_PPT_TRAINING:
            self.switch_interaction(Interaction.MANUAL_BASED)
            self.user_study_state = AbstractUserStudyState.MANUAL_PPT_TRAINING

            self.maximum_number_of_levels = MAXIMUM_NUMBER_OF_LEVELS

        elif state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
            self.switch_interaction(Interaction.MANUAL_BASED)
            self.user_study_state = AbstractUserStudyState.MANUAL_PPT_RECORDED

            self.maximum_number_of_levels = 1

        elif state == AbstractUserStudyState.MANUAL_PPT_EVALUATION:
            self.switch_interaction(Interaction.MANUAL_BASED)
            self.user_study_state = AbstractUserStudyState.MANUAL_PPT_EVALUATION

        elif state == AbstractUserStudyState.BREAK:
            self.user_study_state = AbstractUserStudyState.BREAK

        elif state == AbstractUserStudyState.GAZE_DEMO:
            self.switch_interaction(Interaction.GAZE_SUPPORTED)
            self.user_study_state = AbstractUserStudyState.GAZE_DEMO

        elif state == AbstractUserStudyState.GAZE_PPT_TRAINING:
            self.switch_interaction(Interaction.GAZE_SUPPORTED)
            self.user_study_state = AbstractUserStudyState.GAZE_PPT_TRAINING

            self.maximum_number_of_levels = MAXIMUM_NUMBER_OF_LEVELS

        elif state == AbstractUserStudyState.GAZE_PPT_RECORDED:
            self.switch_interaction(Interaction.GAZE_SUPPORTED)
            self.user_study_state = AbstractUserStudyState.GAZE_PPT_RECORDED

            self.maximum_number_of_levels = 1

        elif state == AbstractUserStudyState.GAZE_PPT_EVALUATION:
            self.switch_interaction(Interaction.GAZE_SUPPORTED)
            self.user_study_state = AbstractUserStudyState.GAZE_PPT_EVALUATION

        elif state == AbstractUserStudyState.DISCUSSION:
            self.user_study_state = AbstractUserStudyState.DISCUSSION

        self.update_save_to_file_strings()
        print self.location_header
        print self.file_name_header

    # </editor-fold>

    def keyPressEvent(self, event):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keyPressEvent(event)
        else:
            super(GamifiedUserStudyBase, self).keyPressEvent(event)

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
            self.reset_all_values()
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

        if key == QtCore.Qt.Key_0:
            print self.user_study_state
            import pdb
            pdb.set_trace()

        if key == QtCore.Qt.Key_8:
            self.start_game()

        if key == QtCore.Qt.Key_9:
            self.end_game()

    def keypress_R(self):

        self.play_sound(SoundType.CAPTURE_NO_HIT)
        if self.target_selected_flag:
            self.target_captured = True

        if self.system_state == SystemState.PRE_ZOOM_A or self.system_state == SystemState.PRE_ZOOM_B or \
                        self.system_state == SystemState.FULLSCALE:
            pass

        elif self.system_state == SystemState.ZOOM_A or self.system_state == SystemState.ZOOM_B:
            self.last_action = Actions.CAPTURE

    def keypress_E(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_E()
        else:
            super(GamifiedUserStudyBase, self).keypress_E()

    def keypress_W(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_W()
        else:
            super(GamifiedUserStudyBase, self).keypress_W()

    def keypress_U(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_U()
        else:
            super(GamifiedUserStudyBase, self).keypress_U()

    def keypress_Q(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_Q()
        else:
            super(GamifiedUserStudyBase, self).keypress_Q()

    def keypress_Y(self):
        if self.interaction is Interaction.MANUAL_BASED:
            super(GazeSupported, self).keypress_Y()
        else:
            super(GamifiedUserStudyBase, self).keypress_Y()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPLICATION_TITLE_GAMIFIED_USER_STUDY_BASE)

    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    main = GamifiedUserStudyBase(width, height, Interaction.GAZE_SUPPORTED, DIR_TEST_HOME)
    main.show()

    sys.exit(app.exec_())
