# <editor-fold desc="Serial Communication Parameters">
# ARDUINO_INTERFACE = 'COM3' #  old box
ARDUINO_INTERFACE = 'COM6'
ARDUINO_BAUD_RATE = 9600
# </editor-fold>


# <editor-fold desc="Communication Messages">
class HwInterface:
    def __init__(self):
        pass

    ZOOM_CW = "ZOOM_CLOCKWISE"
    ZOOM_CCW = "ZOOM_COUNTER"
    ZOOM_PRESS = "ZOOM_PRESS"

    DEPTH_CW = "DEPTH_CLOCKWISE"
    DEPTH_CCW = "DEPTH_COUNTER"
    DEPTH_PRESS = "DEPTH_PRESS"

    FOCUS_CW = "FOCUS_CLOCKWISE"
    FOCUS_CCW = "FOCUS_COUNTER"
    FOCUS_PRESS = "FOCUS_PRESS"

    FREQUENCY_CW = "FREQUENCY_CLOCKWISE"
    FREQUENCY_CCW = "FREQUENCY_COUNTER"
    FREQUENCY_PRESS = "FREQUENCY_PRESS"

    GAIN_CW = "GAIN_CLOCKWISE"
    GAIN_CCW = "GAIN_COUNTER"
    GAIN_PRESS = "GAIN_PRESS"

    RIGHT_PRESS = "RIGHT_PRESS"
    TOP_PRESS = "TOP_PRESS"
    CAPTURE_PRESS = "CAPTURE_PRESS"
    FREEZE_PRESS = "FREEZE_PRESS"

    CALIBRATE_PRESS = "CALIBRATE_PRESS"

    CURSOR_MOVE = "CURSOR_MOVE"
# </editor-fold>
