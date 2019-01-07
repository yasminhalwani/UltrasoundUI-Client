class ClinicalStudyState:
    def __init__(self):
        pass

    DEMO = "DEMO"
    PHANTOM = "PHANTOM"
    PATIENT = "PATIENT"


class SoundFileAction:
    def __init__(self):
        pass

    PLAY = 1
    STOP = 2


class SoundType:
    def __init__(self):
        pass

    CAPTURE_NO_HIT = 1
    CAPTURE_HIT = 2
    GO = 3
    TIMEOUT = 4
    GAME_OVER = 5
    LEVEL_UP = 6
    TARGET_BLINK = 7
    COUNTER = 8


class GameLevel:
    def __init__(self):
        pass

    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8
    LEVEL_9 = 9
    LEVEL_10 = 10


class ShapeRegularity:
    def __init__(self):
        pass

    REGULAR = 1
    IRREGULAR = 2


class GameState:
    def __init__(self):
        pass

    IDLE = 0
    COUNTING_TO_START = 1
    TASK_RUNNING = 2
    DESTROYING_TARGET = 3
    LEVELING_UP = 4
    TIMEOUT_SCREEN = 5
    GAME_OVER_SCREEN = 6
    YOU_WIN_SCREEN = 7


class Actions:
    def __init__(self):
        pass

    NONE = 0
    ZOOM_IN = 1
    ZOOM_OUT = 2
    CONFIRM_ZOOM = 3
    RESET_ZOOM = 4
    PRE_ZOOM = 5
    INCREASE_FOCUS = 6
    DECREASE_FOCUS = 7
    INCREASE_DEPTH = 8
    DECREASE_DEPTH = 9
    PAN = 10
    RESIZE = 11
    TOGGLE = 12
    EYE = 13
    CAPTURE = 14
    CALIBRATE = 15


class UserStudyOrder:
    def __init__(self):
        pass

    A = 1
    B = 2


class AbstractUserStudyState:
    def __init__(self):
        pass

    INTRODUCTION = "INTRODUCTION"

    MANUAL_DEMO = "MANUAL_DEMO"
    MANUAL_PPT_TRAINING = "MANUAL_TRAINING"
    MANUAL_PPT_RECORDED = "MANUAL_RECORDED"
    MANUAL_PPT_EVALUATION = "MANUAL_EVALUATION"

    GAZE_DEMO = "GAZE_DEMO"
    GAZE_PPT_TRAINING = "GAZE_TRAINING"
    GAZE_PPT_RECORDED = "GAZE_RECORDED"
    GAZE_PPT_EVALUATION = "GAZE_EVALUATION"

    DISCUSSION = "DISCUSSION"

    BREAK = "BREAK"


class CentralImageType:
    def __init__(self):
        pass

    NONE = 0
    DEMO = 1
    TRAINING_1 = 2
    TRAINING_2 = 3
    RECORDED_1 = 4
    RECORDED_2 = 5
    OLD = 6


class SystemState:
    def __init__(self):
        pass

    FULLSCALE = "FullScale"
    PRE_ZOOM_A = "Pre Zoom A"
    PRE_ZOOM_B = "Pre Zoom B"
    ZOOM_A = "Zoom A"
    ZOOM_B = "Zoom B"


class DepthLevels:
    def __init__(self):
        pass

    DEPTH_LEVEL_1 = 5
    DEPTH_LEVEL_2 = 6
    DEPTH_LEVEL_3 = 7
    DEPTH_LEVEL_4 = 8
    DEPTH_LEVEL_5 = 9
    DEPTH_LEVEL_6 = 10
    DEPTH_LEVEL_7 = 11


class Interaction:
    def __init__(self):
        pass

    MANUAL_BASED = 1
    GAZE_SUPPORTED = 2


class ScrollDirection:
    def __init__(self):
        pass

    NATURAL = 1
    REVERSE = 2


class CalibrationStage:
    def __init__(self):
        pass

    NONE = 0
    SHOW_TRACKER = 1
    HIDE_TRACKER = 2
    SHOW_CALIBRATION = 3
    HIDE_CALIBRATION = 4


class ImageState:
    def __init__(self):
        pass

    ORIGINAL = 1
    ZOOMED = 2


class EyeTrackerState:
    def __init__(self):
        pass

    DISCONNECTED = 1
    PENDING = 2
    UNDETECTED = 3
    DETECTED = 4


class Direction:
    def __init__(self):
        pass

    NONE = 0
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4
    UPPER_LEFT = 5
    UPPER_RIGHT = 6
    LOWER_LEFT = 7
    LOWER_RIGHT = 8


class POGValidity:
    def __init__(self):
        pass

    VALID = 1
    INVALID_SHORT = 2
    INVALID_INTERMEDIATE = 3
    INVALID_LONG = 4


class ROIState:
    def __init__(self):
        pass

    NONE = 1
    VISIBLE = 2
    INVISIBLE = 3
    RESIZING = 4
    MOVING = 5
    HELD = 6


class PaddingType:
    def __init__(self):
        pass

    NONE = 1
    LEFT_RIGHT = 2
    UP_DOWN = 3
    INVALID = 4
