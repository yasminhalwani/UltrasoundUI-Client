import sys

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

sys.path.insert(0, '../user_study_bases')
from user_study_base import UserStudyBase

sys.path.insert(0, '../globals')
from common_constants import *
from states import *
from tasks_roi import *


class GraphicalImageInterface(UserStudyBase):
    def __init__(self, screen_width_input, screen_height_input, interaction, home_directory):
        super(GraphicalImageInterface, self).__init__(screen_width_input, screen_height_input,
                                                      interaction, home_directory)

        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#

        # <editor-fold desc="state variables">
        self.current_central_image_type = CentralImageType.NONE
        # </editor-fold>

        # <editor-fold desc="accuracy-related variables">
        self.roi_pen_target_zero = None
        self.roi_pen_target_quarter = None
        self.roi_pen_target_half = None
        self.roi_pen_target_full = None
        self.accuracy_score = None
        self.accuracy_score_log = []
        self.accuracy_score_half_flag = False
        self.accuracy_score_quarter_flag = False
        self.accuracy_score_full_flag = False
        # </editor-fold>

        # <editor-fold desc="task-related variables">
        self.current_task_roi = None
        self.task_rect_and_depth = None
        # </editor-fold>

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#
        self.initialize_extra_gui_elements()
        self.initialize_task_variables()

    # <editor-fold desc="gui functions">
    def initialize_extra_gui_elements(self):
        self.roi_pen_target_zero = pg.mkPen(color="r", width=25, style=QtCore.Qt.SolidLine)
        self.roi_pen_target_quarter = pg.mkPen(color="#cc6200", width=25, style=QtCore.Qt.SolidLine)
        self.roi_pen_target_half = pg.mkPen(color="#f7f304", width=25, style=QtCore.Qt.SolidLine)
        self.roi_pen_target_full = pg.mkPen(color="#006600", width=25, style=QtCore.Qt.SolidLine)
    # </editor-fold>

    # <editor-fold desc="callback functions">

    def callback_values_update(self):
        call_load = False
        if self.user_study_state == AbstractUserStudyState.INTRODUCTION or self.user_study_state == AbstractUserStudyState.MANUAL_DEMO \
                or self.user_study_state == AbstractUserStudyState.GAZE_DEMO:
            if not self.current_central_image_type == CentralImageType.DEMO:
                self.current_central_image_type = CentralImageType.DEMO
                call_load = True

        elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_TRAINING:
            if not self.current_central_image_type == CentralImageType.TRAINING_1:
                self.current_central_image_type = CentralImageType.TRAINING_1
                call_load = True

        elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_TRAINING:
            if not self.current_central_image_type == CentralImageType.TRAINING_2:
                self.current_central_image_type = CentralImageType.TRAINING_2
                call_load = True

        elif self.user_study_state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
            if not self.current_central_image_type == CentralImageType.RECORDED_1:
                self.current_central_image_type = CentralImageType.RECORDED_1
                call_load = True

        elif self.user_study_state == AbstractUserStudyState.GAZE_PPT_RECORDED:
            if not self.current_central_image_type == CentralImageType.RECORDED_2:
                self.current_central_image_type = CentralImageType.RECORDED_2
                call_load = True

        if call_load:
            self.load_central_image()
            self.update_central_image()

        super(GraphicalImageInterface, self).callback_values_update()

        self.check_for_sufficient_target_framing()

    # </editor-fold>

    # <editor-fold desc="accuracy score functions">

    def print_accuracy_scores(self):
        print "Accuracy scores:"
        for i in range(0, len(self.accuracy_score_log)):
            print self.accuracy_score_log[i]

    def calculate_accuracy_score(self):
        self.accuracy_score = 0

        if self.accuracy_score_full_flag:
            self.accuracy_score = 1.0

        elif self.accuracy_score_half_flag:
            self.accuracy_score = 0.5

        elif self.accuracy_score_quarter_flag:
            self.accuracy_score = 0.25

        accuracy_score_list_item = [self.user_study_state, self.current_task_number, self.accuracy_score]

        self.accuracy_score_log.append(accuracy_score_list_item)

    def check_for_sufficient_target_framing(self):

        detail_view_rect = QtCore.QRect(self.detail_view_roi.pos().x(), self.detail_view_roi.pos().y(),
                                        self.detail_view_roi.size().x(), self.detail_view_roi.size().y())

        target_rect = QtCore.QRect(self.current_task_roi.pos().x(), self.current_task_roi.pos().y(),
                                   self.current_task_roi.size().x(), self.current_task_roi.size().y())

        if detail_view_rect.intersects(target_rect):

            intersection = detail_view_rect.intersected(target_rect)

            if (intersection.width() * 1.0 / target_rect.width() * 1.0) * 100 >= MIN_INTERSECTION_PERCENTAGE:
                if MIN_INTERSECTION_PERCENTAGE <= (intersection.height() * 1.0 / target_rect.height() * 1.0) * 100:

                    if round((self.current_task_roi.size().x() / self.detail_view_roi.size().x()), 2) * 100 \
                            >= MIN_ZOOM_PERCENTAGE \
                            and round((self.current_task_roi.size().y() / self.detail_view_roi.size().y()), 2) * 100 \
                            >= MIN_ZOOM_PERCENTAGE:

                        if detail_view_rect.contains(target_rect):
                            self.detail_view_roi.setPen(self.roi_pen_target_full)
                            self.accuracy_score_full_flag = True
                            self.accuracy_score_half_flag = False
                            self.accuracy_score_quarter_flag = False
                        else:
                            self.detail_view_roi.setPen(self.roi_pen_target_half)
                            self.accuracy_score_full_flag = False
                            self.accuracy_score_half_flag = True
                            self.accuracy_score_quarter_flag = False

                    else:
                        if detail_view_rect.contains(target_rect):
                            self.detail_view_roi.setPen(self.roi_pen_target_quarter)
                            self.accuracy_score_full_flag = False
                            self.accuracy_score_half_flag = False
                            self.accuracy_score_quarter_flag = True
                        else:
                            self.detail_view_roi.setPen(self.roi_pen_current)
                            self.accuracy_score_full_flag = False
                            self.accuracy_score_half_flag = False
                            self.accuracy_score_quarter_flag = False
        else:
            self.detail_view_roi.setPen(self.roi_pen_current)
            self.accuracy_score_full_flag = False
            self.accuracy_score_half_flag = False
            self.accuracy_score_quarter_flag = False

    # </editor-fold>

    # <editor-fold desc="data logging functions">
    def log_accuracy_scores_to_file(self):
        location = self.location_header + DIR_ACCURACY_SCORES + "/"

        self.log_list_to_file(self.accuracy_score_log, location,
                              self.file_name_header + FILE_NAME_ACCURACY_SCORES_LIST)

        print "accuracy scores logged to " + location + self.file_name_header + FILE_NAME_ACCURACY_SCORES_LIST

    def log_all_task_values_to_file(self):

        self.print_accuracy_scores()
        self.log_accuracy_scores_to_file()

        super(GraphicalImageInterface, self).log_all_task_values_to_file()

    # </editor-fold>

    # <editor-fold desc="researcher tools functions">

    def start_current_task(self):
        self.current_task_roi.hide()
        super(GraphicalImageInterface, self).start_current_task()

    def end_current_task(self):

        # calculate accuracy for logging
        self.calculate_accuracy_score()

        super(GraphicalImageInterface, self).end_current_task()

    def set_user_study_state(self, state):
        super(GraphicalImageInterface, self).set_user_study_state(state)

        if state == AbstractUserStudyState.MANUAL_DEMO or \
                state == AbstractUserStudyState.MANUAL_PPT_EVALUATION or state == AbstractUserStudyState.BREAK or \
                state == AbstractUserStudyState.GAZE_DEMO or state == AbstractUserStudyState.GAZE_PPT_EVALUATION or \
                state == AbstractUserStudyState.DISCUSSION:
            self.current_task_roi.hide()

        if state == AbstractUserStudyState.MANUAL_PPT_TRAINING:
            self.task_rect_and_depth = training_1_task_rect_and_depth
            self.total_number_of_tasks = TOTAL_NUMBER_OF_TASKS_TRAINING_1
            self.show_current_task()

        elif state == AbstractUserStudyState.MANUAL_PPT_RECORDED:
            self.task_rect_and_depth = recorded_1_task_rect_and_depth
            self.total_number_of_tasks = TOTAL_NUMBER_OF_TASKS_RECORDED_1
            self.show_current_task()

        elif state == AbstractUserStudyState.GAZE_PPT_TRAINING:
            self.task_rect_and_depth = training_2_task_rect_and_depth
            self.total_number_of_tasks = TOTAL_NUMBER_OF_TASKS_TRAINING_2
            self.show_current_task()

        elif state == AbstractUserStudyState.GAZE_PPT_RECORDED:
            self.task_rect_and_depth = recorded_1_task_rect_and_depth
            self.total_number_of_tasks = TOTAL_NUMBER_OF_TASKS_RECORDED_2
            self.show_current_task()

    def go_to_next_task(self):
        super(GraphicalImageInterface, self).go_to_next_task()

        self.show_current_task()

    def go_to_previous_task(self):
        super(GraphicalImageInterface, self).go_to_previous_task()

        self.show_current_task()

    # </editor-fold>

    # <editor-fold desc="task-related functions">

    def initialize_task_variables(self):

        self.last_cursor_move_time = 0

        self.current_task_number = 0

        self.current_task_roi = pg.RectROI([0, 0], [self.default_roi_width, self.default_roi_height], movable=True,
                                           maxBounds=QtCore.QRectF(0, 0, self.image_width, self.image_height))
        self.current_task_roi.hide()
        self.image_view_box.addItem(self.current_task_roi)

        self.task_rect_and_depth = old_task_rect_and_depth

    def show_current_task(self):

        self.current_task_roi.show()

        rect = self.task_rect_and_depth[self.current_task_number]
        self.current_task_roi.setPos(QtCore.QPoint(rect[self.depth_level - BASE_DEPTH_LEVEL][0].x(),
                                                   rect[self.depth_level - BASE_DEPTH_LEVEL][0].y()))
        self.current_task_roi.setSize(QtCore.QPoint(rect[self.depth_level - BASE_DEPTH_LEVEL][0].width(),
                                                    rect[self.depth_level - BASE_DEPTH_LEVEL][0].height()))

    def clear_values_logs(self):

        # clear accuracy scores
        self.accuracy_score_log = []

        super(GraphicalImageInterface, self).clear_values_logs()

    def reset_all_values(self):

        # <editor-fold desc="reset accuracy score">
        self.accuracy_score = 0
        # </editor-fold>

        super(GraphicalImageInterface, self).reset_all_values()

    # </editor-fold>

    def keyPressEvent(self, event):
        super(GraphicalImageInterface, self).keyPressEvent(event)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPLICATION_TITLE_GRAPHICAL_IMAGE_INTERFACE)

    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    main = GraphicalImageInterface(width, height, Interaction.MANUAL_BASED, DIR_TEST_HOME)
    main.show()

    sys.exit(app.exec_())
