# GAZE TRACKER XML MESSAGES #
SET_ENABLE_SEND_DATA = '<SET ID="ENABLE_SEND_DATA" STATE="1" />\r\n'
ACK_ENABLE_SEND_DATA = '<ACK ID="ENABLE_SEND_DATA" STATE="1" />\r\n'

GET_CALIBRATE_START = '<GET ID="CALIBRATE_START" />\r\n'
SET_CALIBRATE_START = '<SET ID="CALIBRATE_START" STATE="1" />\r\n'
ACK_CALIBRATE_START = '<ACK ID="CALIBRATE_START" STATE="1" />\r\n'

GET_CALIBRATE_SHOW = '<GET ID="CALIBRATE_SHOW" />\r\n'
SET_CALIBRATE_SHOW_1 = '<SET ID="CALIBRATE_SHOW" STATE="1" />\r\n'
SET_CALIBRATE_SHOW_0 = '<SET ID="CALIBRATE_SHOW" STATE="0" />\r\n'
ACK_CALIBRATE_SHOW = '<ACK ID="CALIBRATE_SHOW" STATE="1" />\r\n'

GET_TRACKER_DISPLAY = '<GET ID="TRACKER_DISPLAY" />\r\n'
SET_TRACKER_DISPLAY_1 = '<SET ID="TRACKER_DISPLAY" STATE="1" />\r\n'
SET_TRACKER_DISPLAY_0 = '<SET ID="TRACKER_DISPLAY" STATE="0" />\r\n'
ACK_TRACKER_DISPLAY = '<ACK ID="TRACKER_DISPLAY" STATE="1" />\r\n'

# GAZE TRACKER COMMUNICATION PARAMETERS #
GAZE_TRACKER_IP_ADDRESS = "127.0.0.1"
GAZE_TRACKER_PORT = 4242
TIMEOUT_INITIAL = 0.5
TIMEOUT_ERROR = 0.1
REPLY_MESSAGE_LENGTH = 40
APPLICATION_TITLE_GAZE_TRACKER_COMPONENT_GUI = "Gaze Tracker Component Test GUI"

# ERROR/INFO MESSAGES #
SOCKET_ERROR_MESSAGE = "Error Connecting to Gazepoint Socket"
SOCKET_CONNECTED = "Socket connection to gaze tracker successful"
SOCKET_DISCONNECTED = "Socket disconnection from gaze tracker successful"
MESSAGE_ERROR = "Failed to receive data from gaze tracker"


# GAZE TRACKER DATA PROCESSING PARAMETERS #
USE_MOVING_AVERAGE_FILTER = True
GAZE_DATA_HISTORY_SIZE = 100
# GAZE_DATA_D_HISTORY_SIZE = 10
GAZE_DATA_D_HISTORY_SIZE = 10
GAZE_DATA_MOVING_AVERAGE_D_THRESHOLD = 0.004
# GAZE_DATA_MOVING_AVERAGE_D_THRESHOLD = 0.01


# GAZE TRACKER DATA ENABLE MESSAGES #
class GazeTrackerDataEnableMessages:
    def __init__(self):
        pass

    COUNTER = '<SET ID="ENABLE_SEND_COUNTER" STATE="1" />\r\n'
    TIME = '<SET ID="ENABLE_SEND_TIME" STATE="1" />\r\n'
    TIME_TICK = '<SET ID="ENABLE_SEND_TIME_TICK" STATE="1" />\r\n'
    POG_FIX = '<SET ID="ENABLE_SEND_POG_FIX" STATE="1" />\r\n'
    POG_LEFT = '<SET ID="ENABLE_SEND_POG_LEFT" STATE="1" />\r\n'
    POG_RIGHT = '<SET ID="ENABLE_SEND_POG_RIGHT" STATE="1" />\r\n'
    POG_BEST = '<SET ID="ENABLE_SEND_POG_BEST" STATE="1" />\r\n'
    PUPIL_LEFT = '<SET ID="ENABLE_SEND_PUPIL_LEFT" STATE="1" />\r\n'
    PUPIL_RIGHT = '<SET ID="ENABLE_SEND_PUPIL_RIGHT" STATE="1" />\r\n'
    EYE_LEFT = '<SET ID="ENABLE_SEND_EYE_LEFT" STATE="1" />\r\n'
    EYE_RIGHT = '<SET ID="ENABLE_SEND_EYE_RIGHT" STATE="1" />\r\n'
    CURSOR = '<SET ID="ENABLE_SEND_CURSOR" STATE="1" />\r\n'
    USER_DATA = '<SET ID="ENABLE_SEND_USER_DATA" STATE="1" />\r\n'

    COUNTER_ACK = '<ACK ID="ENABLE_SEND_COUNTER" STATE="1" />\r\n'
    TIME_ACK = '<ACK ID="ENABLE_SEND_TIME" STATE="1" />\r\n'
    TIME_TICK_ACK = '<ACK ID="ENABLE_SEND_TIME_TICK" STATE="1" />\r\n'
    POG_FIX_ACK = '<ACK ID="ENABLE_SEND_POG_FIX" STATE="1" />\r\n'
    POG_LEFT_ACK = '<ACK ID="ENABLE_SEND_POG_LEFT" STATE="1" />\r\n'
    POG_RIGHT_ACK = '<ACK ID="ENABLE_SEND_POG_RIGHT" STATE="1" />\r\n'
    POG_BEST_ACK = '<ACK ID="ENABLE_SEND_POG_BEST" STATE="1" />\r\n'
    PUPIL_LEFT_ACK = '<ACK ID="ENABLE_SEND_PUPIL_LEFT" STATE="1" />\r\n'
    PUPIL_RIGHT_ACK = '<ACK ID="ENABLE_SEND_PUPIL_RIGHT" STATE="1" />\r\n'
    EYE_LEFT_ACK = '<ACK ID="ENABLE_SEND_EYE_LEFT" STATE="1" />\r\n'
    EYE_RIGHT_ACK = '<ACK ID="ENABLE_SEND_EYE_RIGHT" STATE="1" />\r\n'
    CURSOR_ACK = '<ACK ID="ENABLE_SEND_CURSOR" STATE="1" />\r\n'
    USER_DATA_ACK = '<ACK ID="ENABLE_SEND_USER_DATA" STATE="1" />\r\n'

    DATA_RECORDS_TYPES = {
            'CNT',
            'TIME',
            'TIME_TICK',
            'FPOGX',
            'FPOGY',
            'FPOGS',
            'FPOGD',
            'FPOGID',
            'FPOGV',
            'LPOGX',
            'LPOGY',
            'LPOGV',
            'RPOGX',
            'RPOGY',
            'RPOGV',
            'BPOGX',
            'BPOGY',
            'BPOGV',
            'LPCX',
            'LPCY',
            'LPD',
            'LPS',
            'LPV',
            'RPCX',
            'RPCY',
            'RPD',
            'RPS',
            'RPV',
            'LEYEX',
            'LEYEY',
            'LEYEZ',
            'LPUPILD',
            'LPUPILV',
            'REYEX',
            'REYEY',
            'REYEZ',
            'RPUPILD',
            'RPUPILV',
            'CX',
            'CY',
            'CS',
            'USER',
    }
