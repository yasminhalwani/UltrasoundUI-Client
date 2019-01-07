from states import UserStudyOrder, ScrollDirection, GameLevel

USER_STUDY_ORDER = UserStudyOrder.A
SCROLL_DIRECTION = ScrollDirection.REVERSE
LOG_RESULTS_FLAG = True
STREAM_IMAGE = True
GRAPHICAL_EXPERIMENT = 2

# <editor-fold desc="Manual-based Interface">
APPLY_CURSOR_LAG = False
CURSOR_LAG = 0.03
DEFAULT_TRANSLATION_PX = 5
# RESIZE_PX_MAX = 25
RESIZE_PX_MAX = 20

MAX_ROI_TRANSLATION_SCALE = 15
DEFAULT_ROI_TRANSLATION_SCALE = 3
ROI_TRANSLATION_SCALE_ZOOM_MODE = 8
ROI_TRANSLATION_SCALE_PRE_ZOOM_MODE = 4
DOUBLE_ROI_TRANSLATION_THRESHOLD = 50

CURSOR_POSITION_HISTORY_MAX_SIZE = 2
CURSOR_MOVE_TIME_BUFFER_SIZE = 10
ZOOM_RATIO = 0.94
FOCUS_HEIGHT_RATIO = 0.2
FOCUS_MOVE_PX = 15
BASE_DEPTH_LEVEL = 5
PAN_CENTER_RADIUS = 10
MIN_ZOOM_PERCENTAGE = 65.0
MIN_INTERSECTION_PERCENTAGE = 97.0
PADDING_OPACITY = 0.6
MAX_NUM_DISPLAYED_CAPTURED_IMAGES = 8
# </editor-fold>

THREAD_TIMEOUT = 1000

# <editor-fold desc="Gaze-supported Interface">
INDICATORS_THRESHOLD_1 = 35
INDICATORS_THRESHOLD_2 = 80
INDICATORS_THRESHOLD_3 = 120

IM_VELOCITY_MAX = 7
# </editor-fold>

# <editor-fold desc="Tasks">
TOTAL_NUMBER_OF_TASKS_OLD = 14
TOTAL_NUMBER_OF_TASKS_TRAINING_1 = 17
TOTAL_NUMBER_OF_TASKS_TRAINING_2 = 17
TOTAL_NUMBER_OF_TASKS_RECORDED_1 = 17
TOTAL_NUMBER_OF_TASKS_RECORDED_2 = 17
# </editor-fold>

# <editor-fold desc="Instructions">
INSTRUCTIONS_INTRO = "Hi! :) Let's first calibrate the eye tracker."
INSTRUCTION_DEMO_TRAINING_RECORDED_DEFAULT = "Please locate, frame and capture <br /> the indicated target."
INSTRUCTION_DEMO_TRAINING_RECORDED_DEPTH_MESSAGE = "Please increase the depth <br /> to show the next target."
INSTRUCTION_TARGET_NUMBER = "Target # "
INSTRUCTIONS_EVALUATION = "Thank you for completing the tasks. <br />Please evaluate the interaction design."
INSTRUCTIONS_DISCUSSION = "Thank you for taking part <br />in the experiment!"
INSTRUCTIONS_CONFIRM_ZOOM_MESSAGE = "Please confirm zoom before capture."
# </editor-fold>

# <editor-fold desc="Progress Bar Strings">
PROGRESS_INTRODUCTION = "Introduction"

PROGRESS_MANUAL_BASED_INTERFACE = "Session 1"
PROGRESS_GAZE_SUPPORTED_INTERFACE = "Session 2"
PROGRESS_BREAK = "Break time!"

PROGRESS_DEMO = "Demo"
PROGRESS_PPT_TRAINING = "Try it yourself"
PROGRESS_PPT_RECORDED = "Let's go!"
PROGRESS_PPT_EVALUATION = "Questionnaire"

PROGRESS_DISCUSSION = "Discussion"
# </editor-fold>

# <editor-fold desc="Timer Strings">
SS_TIMER_TEXT = "Task Started"
SP_TASKS_TIME_LIMITS = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 60, 60, 20, 60, 60, 20]
# </editor-fold>

# <editor-fold desc="Gamification Variables">
MAX_NUMBER_OF_TIMEOUTS_PER_TRAINING_LEVEL = 14
MAX_NUMBER_OF_TIMEOUTS_PER_RECORDED_LEVEL = 14
TOTAL_NUMBER_OF_RECORDED_TASKS = 14
TOTAL_NUMBER_OF_REQUIRED_CONSECUTIVE_CORRECT_TASKS = 6
LEVEL1_TIME_LIMIT_REGULAR = 20
LEVEL1_TIME_LIMIT_IRREGULAR = 100
MAXIMUM_NUMBER_OF_LEVELS = GameLevel.LEVEL_10

if GRAPHICAL_EXPERIMENT == 1:
    TARGET_1_IMAGE = "target_1.png"
    TARGET_1_SELECTED_IMAGE = "target_1_selected.png"
    TARGET_2_IMAGE = "target_2.png"
    TARGET_2_SELECTED_IMAGE = "target_2_selected.png"
    TARGET_3_IMAGE = "target_3.png"
    TARGET_3_SELECTED_IMAGE = "target_3_selected.png"
    TARGET_4_IMAGE = "target_4.png"
    TARGET_4_SELECTED_IMAGE = "target_4_selected.png"
    TARGET_DESTROYED_IMAGE = "target_destroyed.png"
elif GRAPHICAL_EXPERIMENT == 2:
    TARGET_2_IMAGE = "target_1.png"
    TARGET_2_SELECTED_IMAGE = "target_1_selected.png"
    TARGET_1_IMAGE = "target_2.png"
    TARGET_1_SELECTED_IMAGE = "target_2_selected.png"
    TARGET_4_IMAGE = "target_3.png"
    TARGET_4_SELECTED_IMAGE = "target_3_selected.png"
    TARGET_3_IMAGE = "target_4.png"
    TARGET_3_SELECTED_IMAGE = "target_4_selected.png"
    TARGET_DESTROYED_IMAGE = "target_destroyed.png"

LIFE_IMAGE = "life.png"

SPACE_BACKGROUND_IMAGE = "space.jpg"
COUNTER_BACKGROUND_1_IMAGE = "space_counter_1.jpg"
COUNTER_BACKGROUND_2_IMAGE = "space_counter_2.jpg"
COUNTER_BACKGROUND_3_IMAGE = "space_counter_3.jpg"
COUNTER_BACKGROUND_GO_IMAGE = "space_counter_go.jpg"
BACKGROUND_LEVEL_UP_IMAGE = "space_level_up.jpg"
TIMEOUT_BACKGROUND_IMAGE = "timeout.jpg"
GAME_OVER_BACKGROUND_IMAGE = "game_over.jpg"
YOU_WIN_BACKGROUND_IMAGE = "you_win.jpg"

# </editor-fold>

# <editor-fold desc="Images locations">
CENTRAL_IMAGE_LOCATION_OLD = "../resources/old/"
CENTRAL_IMAGE_LOCATION_DEMO = "../resources/demo/"
CENTRAL_IMAGE_LOCATION_TRAINING_1 = "../resources/training_1/"
CENTRAL_IMAGE_LOCATION_TRAINING_2 = "../resources/training_2/"
CENTRAL_IMAGE_LOCATION_RECORDED_1 = "../resources/recorded_1/"
# CENTRAL_IMAGE_LOCATION_RECORDED_2 = "../resources/recorded_2/"
CENTRAL_IMAGE_LOCATION_RECORDED_2 = "../resources/recorded_1/"

SYSTEM_STATE_IMAGE_LOCATION = "../resources/icons/"
OTHER_IMAGE_LOCATION = "../resources/"
SOUNDS_LOCATION = "../resources/sounds/"
SOUND_CAPTURE_NO_HIT = "capture_no_hit.wav"
SOUND_CAPTURE_HIT = "capture_hit.wav"
SOUND_GO = "go.wav"
SOUND_TIMEOUT = "timeout.wav"
SOUND_GAME_OVER = "game_over.wav"
SOUND_LEVEL_UP = "level_up.wav"
SOUND_TARGET_BLINK = "target_blink.wav"
SOUND_COUNTER = "counter.wav"
SOUND_TRAINING_BACKGROUND_MUSIC = "training_background.wav"
SOUND_RECORDED_BACKGROUND_MUSIC = "recorded_background.wav"
SOUND_NAME_TRAINING_BACKGROUND_MUSIC = "training_background"
SOUND_NAME_RECORDED_BACKGROUND_MUSIC = "recorded_background"

SYSTEM_STATE_RESIZE_ICON_IMAGE = "resize_icon.png"
SYSTEM_STATE_REPOSITION_ICON_IMAGE = "reposition_icon.png"
TASK_RUNNING_IMAGE = "dot_maroon.jpg"
# EYE_GAZE_ICON_IMAGE = "eye_icon.png"
EYE_GAZE_ICON_IMAGE = "eye_icon_pixelated.png"
MODE_FULLSCALE_SELECTED_ICON_IMAGE = "fullscale_selected.png"
MODE_FULLSCALE_DESELECTED_ICON_IMAGE = "fullscale_deselected.png"
MODE_PREZOOM_SELECTED_ICON_IMAGE = "prezoom_selected.png"
MODE_PREZOOM_DESELECTED_ICON_IMAGE = "prezoom_deselected.png"
MODE_ZOOM_SELECTED_ICON_IMAGE = "zoom_selected.png"
MODE_ZOOM_DESELECTED_ICON_IMAGE = "zoom_deselected.png"
LEVEL_1_ICON = "level_1.png"
LEVEL_2_ICON = "level_2.png"
LEVEL_3_ICON = "level_3.png"
LEVEL_4_ICON = "level_4.png"
LEVEL_5_ICON = "level_5.png"
LEVEL_6_ICON = "level_6.png"
LEVEL_7_ICON = "level_7.png"
LEVEL_8_ICON = "level_8.png"
LEVEL_9_ICON = "level_9.png"
LEVEL_10_ICON = "level_10.png"


STATIC_IMAGE_DEPTH_LEVEL_1 = "level_1.jpg"
STATIC_IMAGE_DEPTH_LEVEL_2 = "level_2.jpg"
STATIC_IMAGE_DEPTH_LEVEL_3 = "level_3.jpg"
STATIC_IMAGE_DEPTH_LEVEL_4 = "level_4.jpg"
STATIC_IMAGE_DEPTH_LEVEL_5 = "level_5.jpg"
STATIC_IMAGE_DEPTH_LEVEL_6 = "level_6.jpg"
STATIC_IMAGE_DEPTH_LEVEL_7 = "level_7.jpg"
PADDING_BLANK_IMAGE_LOCATION = "../resources/dot.jpg"
TRANSPARENT_BASE_IMAGE_LOCATION = "../resources/black.jpg"
MAX_PAN_SIGNAL_IMAGE_LOCATION = "../resources/dot_maroon.png"
# </editor-fold>


# <editor-fold desc="GUI Strings">
DOCK_NAME_CENTRAL_IMAGE = "Central Image"
DOCK_NAME_GAZE_INDICATORS = "Eye Gaze Indicators"
DOCK_NAME_CONTEXT_IMAGE = "Image Context"
DOCK_NAME_CAPTURED_IMAGES = "Captured Images"
DOCK_NAME_PARAMETERS = "Parameters"
DOCK_NAME_INSTRUCTIONS = "Instructions"
DOCK_NAME_TIMER = "Timer"
DOCK_NAME_PROGRESS = "Progress"
DOCK_NAME_TIMER_PROGRESS_BAR = "Timer Progress Bar"
DOCK_NAME_LEVEL_NUMBER = "Level Number"
DOCK_NAME_LEVEL_PROGRESS_BAR = "Level Progress Bar"
DOCK_NAME_TOOLS = "Tools"
DOCK_NAME_HP = "HP"
DOCK_NAME_TASK_STATE = "Task State"
HTML_NEWLINE = "<br/>"
HTML_SPACE = "&nbsp; - &nbsp; "
HTML_CENTER_DIV = '<div style="margin:0 auto;">'
HTML_HIGHLIGHT_DIV = '<div style="text-decoration: underline; color:#ff4d4d">'
HTML_SUB_HIGHLIGHT_DIV = '<div style="color:#b32400">'
HTML_DIV_END = '</div>'
HTML_BOLD_START = "<b>"
HTML_BOLD_END = "</b>"
# </editor-fold>

# <editor-fold desc="Application Title Strings">
APPLICATION_TITLE_MANUAL_BASED = "Manual-based Interface"
APPLICATION_TITLE_GAZE_SUPPORTED = "Gaze-supported Interface"
APPLICATION_TITLE_USER_STUDY_BASE = "User Study Base Interface"
APPLICATION_TITLE_GRAPHICAL_IMAGE_INTERFACE = "Graphical Image Interface"
APPLICATION_TITLE_US_MACHINE_CLIENT_INTERFACE = "Ultrasound Machine Client Interface"
APPLICATION_TITLE_SS = "Software Test - Static Image"
APPLICATION_TITLE_SP = "Software Test - Phantom Image"
APPLICATION_TITLE_GNOB_FZ = "Graphics - No Bimanual - Fast Zoom"
APPLICATION_TITLE_GNOB_DZ = "Graphics - No Bimanual - Detailed Zoom"


APPLICATION_TITLE_GAMIFIED_USER_STUDY_BASE = "Gamified User Study Base Interface"
# </editor-fold>


# <editor-fold desc="Error/Info Messages Strings">
MESSAGE_NO_PADDING_REQUIRED = "no padding required"
MESSAGE_INVALID_PADDING = "invalid padding"
# </editor-fold>

# <editor-fold desc="User Study Directories And File Names">

DIR_USER = 'user_'

DIR_ACCURACY_SCORES = 'accuracy_scores'
DIR_AUDIO_RECORDING = 'audio_recording'
DIR_CAPTURED_IMAGES = 'captured_images'
DIR_ELAPSED_TIMES = 'elapsed_times'
DIR_POG_LOGS = 'pog_logs'
DIR_REPETITIVENESS = 'repetitiveness'
DIR_RESEARCHER_NOTES = 'researcher_notes'

FILE_NAME_TIMES_ELAPSED_SCORES = "times_elapsed.txt"
FILE_NAME_TOTAL_LOGS = "total_logs.txt"

FILE_NAME_REPETITIVENESS_SCORES = "repetitiveness_scores.txt"
FILE_NAME_RAW_REPETITIVENESS_LIST = "RAW.txt"
FILE_NAME_AR_REPETITIVENESS_LIST = "AR_list.txt"
FILE_NAME_PRE_FR_REPETITIVENESS_LIST = "pre_FR_list.txt"
FILE_NAME_FR_REPETITIVENESS_LIST = "FR_list.txt"
FILE_NAME_POG_LOG = "pog_log.txt"
FILE_NAME_ACCURACY_SCORES_LIST = "accuracy_scores.txt"

EXTENSION_CAPTURED_IMAGE = ".jpg"

DIR_TEST_HOME = '../../TEST_Results/'
DIR_SS_HOME = '../../SS_Results/'
DIR_SP_HOME = '../../SP_Results/'
DIR_GAMIFIED_FAST_ZOOM_HOME = '../../Gamified_FastZoom_Results/'
DIR_GAMIFIED_DETAILED_ZOOM_HOME = '../../Gamified_DetailedZoom_Results/'
DIR_CLINICAL_STUDY_HOME = '../../Clinical_Study_Results/'
# </editor-fold>
