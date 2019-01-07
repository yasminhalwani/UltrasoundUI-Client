import select
import socket
import sys
import threading
from xml.dom import minidom

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
import numpy as np
import math
import pylab as plt

import Queue

sys.path.insert(0, '../globals')
from gaze_tracker_comm_protocol import *


class GazeTrackerThread(QThread, QtGui.QGraphicsView):
    pog = QtCore.pyqtSignal(object)

    def __init__(self, data_types):
        QtCore.QThread.__init__(self)
        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#

        self.data_types = data_types

        # <editor-fold desc="network variables">
        self.gaze_tracker_address = None
        self.gaze_tracker_socket = None
        # </editor-fold>

        # <editor-fold desc="data variables">
        self.raw_data_queue = Queue.Queue(4)
        self.xml_data_string = None
        self.unprocessed_data_records = None
        self.validated_data_records = None
        self.filtered_data_records = None

        self.processed_data_queue = Queue.Queue(4)
        self.parsed_reply = None
        self.reply = None
        # </editor-fold>

        # <editor-fold desc="threading variables">
        self.gaze_data_thread = None
        self.data_transmission_thread_started = False
        # </editor-fold>

        # <editor-fold desc="moving average filter variables">
        self.use_moving_average_filter = False
        self.last_valid_data_records = None
        self.history_size = 0
        self.d_history_size = 0
        self.moving_average_d_threshold = 0

        self.POG_FIX_history = {}
        self.POG_LEFT_history = {}
        self.POG_RIGHT_history = {}
        self.POG_BEST_history = {}
        self.PUPIL_LEFT_history = {}
        self.PUPIL_RIGHT_history = {}
        self.EYE_LEFT_history = {}
        self.EYE_RIGHT_history = {}
        self.CURSOR_history = {}
        # </editor-fold>

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#
        self.initialize_moving_average_filter_parameters()
        self.initialize_gaze_tracker_connection()

        self.send_enable_send_data_messages()

    # <editor-fold desc="gaze tracker connection functions">
    def initialize_gaze_tracker_connection(self):

        while True:
            self.connect_gaze_tracker_socket()
            if self.reply == ACK_ENABLE_SEND_DATA:
                break
            self.disconnect_gaze_tracker_socket()

        self.initialize_data_transmission_thread()

    def connect_gaze_tracker_socket(self):
        self.gaze_tracker_address = GAZE_TRACKER_IP_ADDRESS
        self.parsed_reply = ''
        self.reply = ''

        self.gaze_tracker_socket = GazeTrackerClient()

        try:
            self.gaze_tracker_socket.connect(self.gaze_tracker_address, GAZE_TRACKER_PORT)
            self.gaze_tracker_socket.sock.settimeout(TIMEOUT_INITIAL)

        except socket.error as socket_error:
            print(SOCKET_ERROR_MESSAGE, socket_error)

        else:
            print SOCKET_CONNECTED
            self.gaze_tracker_socket.set_timeout(TIMEOUT_ERROR)

        if self.gaze_tracker_socket.is_socket_client_opened:
            self.initialize_data_transmission()

    def disconnect_gaze_tracker_socket(self):
        if self.gaze_tracker_socket.is_socket_client_opened:

            try:
                self.gaze_tracker_socket.disconnect()

            except socket.error as socket_error:
                print(SOCKET_ERROR_MESSAGE, socket_error)
            else:
                print SOCKET_DISCONNECTED

    # </editor-fold>

    # <editor-fold desc="data transmission initialization functions">
    def initialize_data_transmission(self):

        # (1) Send enable data transmission
        message = SET_ENABLE_SEND_DATA
        self.gaze_tracker_socket.send_message(message)
        print message

        # (2) Receive ack for data transmission
        try:
            self.reply = self.gaze_tracker_socket.receive_message(len(message))
            print self.reply

        except:
            print MESSAGE_ERROR

    def initialize_data_transmission_thread(self):
        self.gaze_data_thread = GazeDataThread(self.gaze_tracker_socket, self.raw_data_queue)
        self.gaze_data_thread.set_message_length(REPLY_MESSAGE_LENGTH)
        self.gaze_data_thread.daemon = True
        self.gaze_data_thread.start()
        self.data_transmission_thread_started = True

    def send_enable_send_data_messages(self):

        for data_type in self.data_types:
            message = data_type
            self.reply = self.send_and_receive_from_gaze_tracker(message)

    def send_and_receive_from_gaze_tracker(self, message):

        reply = ""

        # (1) Send enable transmission
        self.gaze_tracker_socket.send_message(message)
        print "sending to tracker: " + message

        # (2) Receive ack for enable transmission
        try:
            reply = self.gaze_tracker_socket.receive_message(len(message))

        except:
            print MESSAGE_ERROR

        return reply

    # </editor-fold>

    # <editor-fold desc="other gaze tracker functions">

    def start_calibration(self):

        message = SET_CALIBRATE_SHOW_1
        reply1 = self.send_and_receive_from_gaze_tracker(message)

        message = SET_CALIBRATE_START
        reply2 = self.send_and_receive_from_gaze_tracker(message)

        return reply1 + " " + reply2

    def exit_calibration(self):

        message = SET_CALIBRATE_SHOW_0
        reply = self.send_and_receive_from_gaze_tracker(message)

        return reply

    def show_tracker_display(self):

        message = SET_TRACKER_DISPLAY_1
        reply = self.send_and_receive_from_gaze_tracker(message)

        return reply

    def hide_tracker_display(self):

        message = SET_TRACKER_DISPLAY_0
        reply = self.send_and_receive_from_gaze_tracker(message)

        return reply

    # </editor-fold>

    # <editor-fold desc="data processing functions">
    def get_processed_data(self):

        if self.data_transmission_thread_started and not self.raw_data_queue.empty():
            # (1) parse raw string to produce xml data string
            self.xml_data_string = self.parse_raw_string(self.raw_data_queue.get_nowait())

            if self.xml_data_string != "":

                # (2) parse xml string to produce unprocessed data records
                self.unprocessed_data_records = self.parse_xml_string(self.xml_data_string)

                # (3) validate data records
                self.validated_data_records = self.validate_parsed_data(self.unprocessed_data_records)

                output_data = self.validated_data_records

                # (4) filter data records
                if self.use_moving_average_filter:
                    self.filtered_data_records = \
                        self.filter_data_records_with_customized_moving_average(self.validated_data_records)

                    output_data = self.filtered_data_records

                try:
                    self.processed_data_queue.put_nowait(output_data)
                except Queue.Full:
                    self.processed_data_queue.get_nowait()

        return self.processed_data_queue.get_nowait()

    def parse_raw_string(self, input_string):

        reply_string = input_string
        if reply_string.find("<") and reply_string.find(">") >= 0:

            reply_string_1 = reply_string.split(">")[0]
            reply_string_2 = reply_string.split(">")[1]
            self.parsed_reply = self.parsed_reply + reply_string_1

            output = self.parsed_reply + ">"
            self.parsed_reply = reply_string_2

        elif reply_string.find("<") >= 0:
            self.parsed_reply = reply_string
            output = ""
        elif reply_string.find(">") >= 0:
            self.parsed_reply = self.parsed_reply + reply_string
            output = self.parsed_reply + ">"
        else:
            self.parsed_reply = self.parsed_reply + reply_string
            output = ""

        return output

    def validate_parsed_data(self, input_data_records):

        if self.last_valid_data_records is None:
            self.last_valid_data_records = input_data_records

        # COUNTER, TIME, TIME_TICK, USER, CURSOR
        if GazeTrackerDataEnableMessages.COUNTER in self.data_types:
            self.last_valid_data_records['CNT'] = input_data_records['CNT']

        if GazeTrackerDataEnableMessages.TIME in self.data_types:
            self.last_valid_data_records['TIME'] = input_data_records['TIME']

        if GazeTrackerDataEnableMessages.TIME_TICK in self.data_types:
            self.last_valid_data_records['TIME_TICK'] = input_data_records['TIME_TICK']

        if GazeTrackerDataEnableMessages.USER_DATA in self.data_types:
            self.last_valid_data_records['USER'] = input_data_records['USER']

        if GazeTrackerDataEnableMessages.CURSOR in self.data_types:
            self.last_valid_data_records['CX'] = input_data_records['CX']
            self.last_valid_data_records['CY'] = input_data_records['CY']
            self.last_valid_data_records['CS'] = input_data_records['CS']

        # POG FIX
        if GazeTrackerDataEnableMessages.POG_FIX in self.data_types:
            if input_data_records['FPOGV'] == 1.0 and \
                    (input_data_records['FPOGX'] >= 0.0 and input_data_records['FPOGY'] >= 0.0):
                self.last_valid_data_records['FPOGX'] = input_data_records['FPOGX']
                self.last_valid_data_records['FPOGY'] = input_data_records['FPOGY']
                self.last_valid_data_records['FPOGD'] = input_data_records['FPOGD']
                self.last_valid_data_records['FPOGID'] = input_data_records['FPOGID']
                self.last_valid_data_records['FPOGV'] = input_data_records['FPOGV']
            else:
                self.last_valid_data_records['FPOGV'] = 0.0

        # POG_LEFT
        if GazeTrackerDataEnableMessages.POG_LEFT in self.data_types:
            if input_data_records['LPOGV'] == 1.0 and \
                    (input_data_records['LPOGX'] >= 0.0 and input_data_records['LPOGY'] >= 0.0):
                self.last_valid_data_records['LPOGX'] = input_data_records['LPOGX']
                self.last_valid_data_records['LPOGY'] = input_data_records['LPOGY']
                self.last_valid_data_records['LPOGV'] = input_data_records['LPOGV']
            else:
                self.last_valid_data_records['LPOGV'] = 0.0

        # POG_RIGHT
        if GazeTrackerDataEnableMessages.POG_RIGHT in self.data_types:
            if input_data_records['RPOGV'] == 1.0 and \
                    (input_data_records['RPOGX'] >= 0.0 and input_data_records['RPOGY'] >= 0.0):
                self.last_valid_data_records['RPOGX'] = input_data_records['RPOGX']
                self.last_valid_data_records['RPOGY'] = input_data_records['RPOGY']
                self.last_valid_data_records['RPOGV'] = input_data_records['RPOGV']
            else:
                self.last_valid_data_records['RPOGV'] = 0.0

        # POG_BEST
        if GazeTrackerDataEnableMessages.POG_BEST in self.data_types:
            if input_data_records['BPOGV'] == 1.0 and \
                    (input_data_records['BPOGX'] >= 0.0 and input_data_records['BPOGY'] >= 0.0):
                self.last_valid_data_records['BPOGX'] = input_data_records['BPOGX']
                self.last_valid_data_records['BPOGY'] = input_data_records['BPOGY']
                self.last_valid_data_records['BPOGV'] = input_data_records['BPOGV']
            else:
                self.last_valid_data_records['BPOGV'] = 0.0

        # PUPIL_LEFT
        if GazeTrackerDataEnableMessages.PUPIL_LEFT in self.data_types:
            if input_data_records['LPV'] == 1.0 and \
                    (input_data_records['LPCX'] >= 0.0 and input_data_records['LPCY'] >= 0.0):
                self.last_valid_data_records['LPCX'] = input_data_records['LPCX']
                self.last_valid_data_records['LPCY'] = input_data_records['LPCY']
                self.last_valid_data_records['LPD'] = input_data_records['LPD']
                self.last_valid_data_records['LPS'] = input_data_records['LPS']
                self.last_valid_data_records['LPV'] = input_data_records['LPV']
            else:
                self.last_valid_data_records['LPV'] = 0.0

        # PUPIL_RIGHT
        if GazeTrackerDataEnableMessages.PUPIL_RIGHT in self.data_types:
            if input_data_records['RPV'] == 1.0 and \
                    (input_data_records['RPCX'] >= 0.0 and input_data_records['RPCY'] >= 0.0):
                self.last_valid_data_records['RPCX'] = input_data_records['RPCX']
                self.last_valid_data_records['RPCY'] = input_data_records['RPCY']
                self.last_valid_data_records['RPD'] = input_data_records['RPD']
                self.last_valid_data_records['RPS'] = input_data_records['RPS']
                self.last_valid_data_records['RPV'] = input_data_records['RPV']
            else:
                self.last_valid_data_records['RPV'] = 0.0

        # EYE_LEFT
        if GazeTrackerDataEnableMessages.EYE_LEFT in self.data_types:
            if input_data_records['LPUPILV'] == 1.0 and \
                    (input_data_records['LEYEX'] >= 0.0 and input_data_records['LEYEY'] >= 0.0):
                self.last_valid_data_records['LEYEX'] = input_data_records['LEYEX']
                self.last_valid_data_records['LEYEY'] = input_data_records['LEYEY']
                self.last_valid_data_records['LEYEZ'] = input_data_records['LEYEZ']
                self.last_valid_data_records['LPUPILD'] = input_data_records['LPUPILD']
                self.last_valid_data_records['LPUPILV'] = input_data_records['LPUPILV']
            else:
                self.last_valid_data_records['LPUPILV'] = 0

        # EYE_LEFT
        if GazeTrackerDataEnableMessages.EYE_RIGHT in self.data_types:
            if input_data_records['RPUPILV'] == 1.0 and \
                    (input_data_records['REYEX'] >= 0.0 and input_data_records['REYEY'] >= 0.0):
                self.last_valid_data_records['REYEX'] = input_data_records['REYEX']
                self.last_valid_data_records['REYEY'] = input_data_records['REYEY']
                self.last_valid_data_records['REYEZ'] = input_data_records['REYEZ']
                self.last_valid_data_records['RPUPILD'] = input_data_records['RPUPILD']
                self.last_valid_data_records['RPUPILV'] = input_data_records['RPUPILV']
            else:
                self.last_valid_data_records['RPUPILV'] = 0

        return self.last_valid_data_records

    @staticmethod
    def parse_xml_string(raw_xml):
        data_records = {}

        xmldoc = minidom.parseString(raw_xml)
        item_list = xmldoc.getElementsByTagName('REC')

        for _ in range(len(GazeTrackerDataEnableMessages.DATA_RECORDS_TYPES)):

            try:
                data_records['CNT'] = float(item_list[0].attributes['CNT'].value)
            except:
                pass

            try:
                data_records['TIME'] = float(item_list[0].attributes['TIME'].value)
            except:
                pass

            try:
                data_records['TIME_TICK'] = float(item_list[0].attributes['TIME_TICK'].value)
            except:
                pass

            try:
                data_records['FPOGX'] = float(item_list[0].attributes['FPOGX'].value)
            except:
                pass

            try:
                data_records['FPOGY'] = float(item_list[0].attributes['FPOGY'].value)
            except:
                pass

            try:
                data_records['FPOGS'] = float(item_list[0].attributes['FPOGS'].value)
            except:
                pass

            try:
                data_records['FPOGD'] = float(item_list[0].attributes['FPOGD'].value)
            except:
                pass

            try:
                data_records['FPOGID'] = float(item_list[0].attributes['FPOGID'].value)
            except:
                pass

            try:
                data_records['FPOGV'] = float(item_list[0].attributes['FPOGV'].value)
            except:
                pass

            try:
                data_records['LPOGX'] = float(item_list[0].attributes['LPOGX'].value)
            except:
                pass

            try:
                data_records['LPOGY'] = float(item_list[0].attributes['LPOGY'].value)
            except:
                pass

            try:
                data_records['LPOGV'] = float(item_list[0].attributes['LPOGV'].value)
            except:
                pass

            try:
                data_records['RPOGX'] = float(item_list[0].attributes['RPOGX'].value)
            except:
                pass

            try:
                data_records['RPOGY'] = float(item_list[0].attributes['RPOGY'].value)
            except:
                pass

            try:
                data_records['RPOGV'] = float(item_list[0].attributes['RPOGV'].value)
            except:
                pass

            try:
                data_records['BPOGX'] = float(item_list[0].attributes['BPOGX'].value)
            except:
                pass

            try:
                data_records['BPOGY'] = float(item_list[0].attributes['BPOGY'].value)
            except:
                pass

            try:
                data_records['BPOGV'] = float(item_list[0].attributes['BPOGV'].value)
            except:
                pass

            try:
                data_records['LPCX'] = float(item_list[0].attributes['LPCX'].value)
            except:
                pass

            try:
                data_records['LPCY'] = float(item_list[0].attributes['LPCY'].value)
            except:
                pass

            try:
                data_records['LPD'] = float(item_list[0].attributes['LPD'].value)
            except:
                pass

            try:
                data_records['LPS'] = float(item_list[0].attributes['LPS'].value)
            except:
                pass

            try:
                data_records['LPV'] = float(item_list[0].attributes['LPV'].value)
            except:
                pass

            try:
                data_records['RPCX'] = float(item_list[0].attributes['RPCX'].value)
            except:
                pass

            try:
                data_records['RPCY'] = float(item_list[0].attributes['RPCY'].value)
            except:
                pass

            try:
                data_records['RPD'] = float(item_list[0].attributes['RPD'].value)
            except:
                pass

            try:
                data_records['RPS'] = float(item_list[0].attributes['RPS'].value)
            except:
                pass

            try:
                data_records['RPV'] = float(item_list[0].attributes['RPV'].value)
            except:
                pass

            try:
                data_records['LEYEX'] = float(item_list[0].attributes['LEYEX'].value)
            except:
                pass

            try:
                data_records['LEYEY'] = float(item_list[0].attributes['LEYEY'].value)
            except:
                pass

            try:
                data_records['LEYEZ'] = float(item_list[0].attributes['LEYEZ'].value)
            except:
                pass

            try:
                data_records['LPUPILD'] = float(item_list[0].attributes['LPUPILD'].value)
            except:
                pass

            try:
                data_records['LPUPILV'] = float(item_list[0].attributes['LPUPILV'].value)
            except:
                pass

            try:
                data_records['REYEX'] = float(item_list[0].attributes['REYEX'].value)
            except:
                pass

            try:
                data_records['REYEY'] = float(item_list[0].attributes['REYEY'].value)
            except:
                pass

            try:
                data_records['REYEZ'] = float(item_list[0].attributes['REYEZ'].value)
            except:
                pass

            try:
                data_records['RPUPILD'] = float(item_list[0].attributes['RPUPILD'].value)
            except:
                pass

            try:
                data_records['RPUPILV'] = float(item_list[0].attributes['RPUPILV'].value)
            except:
                pass

            try:
                data_records['CX'] = float(item_list[0].attributes['CX'].value)
            except:
                pass

            try:
                data_records['CY'] = float(item_list[0].attributes['CY'].value)
            except:
                pass

            try:
                data_records['CS'] = float(item_list[0].attributes['CS'].value)
            except:
                pass

            try:
                data_records['USER'] = str(item_list[0].attributes['USER'].value)
            except:
                pass

        return data_records

    # </editor-fold>

    # <editor-fold desc="moving average filtering functions">
    def initialize_moving_average_filter_parameters(self):
        self.use_moving_average_filter = USE_MOVING_AVERAGE_FILTER
        self.history_size = GAZE_DATA_HISTORY_SIZE
        self.d_history_size = GAZE_DATA_D_HISTORY_SIZE
        self.moving_average_d_threshold = GAZE_DATA_MOVING_AVERAGE_D_THRESHOLD

        self.POG_FIX_history['x'] = Queue.Queue(self.history_size)
        self.POG_FIX_history['y'] = Queue.Queue(self.history_size)
        self.POG_FIX_history['d'] = Queue.Queue(self.d_history_size)
        self.POG_FIX_history['c'] = 0

        self.POG_LEFT_history['x'] = Queue.Queue(self.history_size)
        self.POG_LEFT_history['y'] = Queue.Queue(self.history_size)
        self.POG_LEFT_history['d'] = Queue.Queue(self.d_history_size)
        self.POG_LEFT_history['c'] = 0

        self.POG_RIGHT_history['x'] = Queue.Queue(self.history_size)
        self.POG_RIGHT_history['y'] = Queue.Queue(self.history_size)
        self.POG_RIGHT_history['d'] = Queue.Queue(self.d_history_size)
        self.POG_RIGHT_history['c'] = 0

        self.POG_BEST_history['x'] = Queue.Queue(self.history_size)
        self.POG_BEST_history['y'] = Queue.Queue(self.history_size)
        self.POG_BEST_history['d'] = Queue.Queue(self.d_history_size)
        self.POG_BEST_history['c'] = 0

        self.PUPIL_LEFT_history['x'] = Queue.Queue(self.history_size)
        self.PUPIL_LEFT_history['y'] = Queue.Queue(self.history_size)
        self.PUPIL_LEFT_history['d'] = Queue.Queue(self.d_history_size)
        self.PUPIL_LEFT_history['c'] = 0

        self.PUPIL_RIGHT_history['x'] = Queue.Queue(self.history_size)
        self.PUPIL_RIGHT_history['y'] = Queue.Queue(self.history_size)
        self.PUPIL_RIGHT_history['d'] = Queue.Queue(self.d_history_size)
        self.PUPIL_RIGHT_history['c'] = 0

        self.EYE_LEFT_history['x'] = Queue.Queue(self.history_size)
        self.EYE_LEFT_history['y'] = Queue.Queue(self.history_size)
        self.EYE_LEFT_history['d'] = Queue.Queue(self.d_history_size)
        self.EYE_LEFT_history['c'] = 0

        self.EYE_RIGHT_history['x'] = Queue.Queue(self.history_size)
        self.EYE_RIGHT_history['y'] = Queue.Queue(self.history_size)
        self.EYE_RIGHT_history['d'] = Queue.Queue(self.d_history_size)
        self.EYE_RIGHT_history['c'] = 0

        self.CURSOR_history['x'] = Queue.Queue(self.history_size)
        self.CURSOR_history['y'] = Queue.Queue(self.history_size)
        self.CURSOR_history['d'] = Queue.Queue(self.d_history_size)
        self.CURSOR_history['c'] = 0

        for x in range(0, self.history_size):
            self.POG_FIX_history['x'].put_nowait(0)
            self.POG_FIX_history['y'].put_nowait(0)

            self.POG_LEFT_history['x'].put_nowait(0)
            self.POG_LEFT_history['y'].put_nowait(0)

            self.POG_RIGHT_history['x'].put_nowait(0)
            self.POG_RIGHT_history['y'].put_nowait(0)

            self.POG_BEST_history['x'].put_nowait(0)
            self.POG_BEST_history['y'].put_nowait(0)

            self.PUPIL_LEFT_history['x'].put_nowait(0)
            self.PUPIL_LEFT_history['y'].put_nowait(0)

            self.PUPIL_RIGHT_history['x'].put_nowait(0)
            self.PUPIL_RIGHT_history['y'].put_nowait(0)

            self.EYE_LEFT_history['x'].put_nowait(0)
            self.EYE_LEFT_history['y'].put_nowait(0)

            self.EYE_RIGHT_history['x'].put_nowait(0)
            self.EYE_RIGHT_history['y'].put_nowait(0)

            self.CURSOR_history['x'].put_nowait(0)
            self.CURSOR_history['y'].put_nowait(0)

        for x in range(0, self.d_history_size):
            self.POG_FIX_history['d'].put_nowait(0)
            self.POG_LEFT_history['d'].put_nowait(0)
            self.POG_RIGHT_history['d'].put_nowait(0)
            self.POG_BEST_history['d'].put_nowait(0)
            self.PUPIL_LEFT_history['d'].put_nowait(0)
            self.PUPIL_RIGHT_history['d'].put_nowait(0)
            self.EYE_LEFT_history['d'].put_nowait(0)
            self.EYE_RIGHT_history['d'].put_nowait(0)
            self.CURSOR_history['d'].put_nowait(0)

    def filter_data_records_with_customized_moving_average(self, validated_data_records):

        filtered_data_records = validated_data_records

        if GazeTrackerDataEnableMessages.POG_FIX in self.data_types:
            history_x = self.POG_FIX_history['x']
            history_y = self.POG_FIX_history['y']
            history_d = self.POG_FIX_history['d']
            history_c = self.POG_FIX_history['c']

            [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
                validated_data_records['FPOGX'],
                validated_data_records['FPOGY'],
                history_x, history_y, history_d, history_c)

            self.POG_FIX_history['x'] = h_x
            self.POG_FIX_history['y'] = h_y
            self.POG_FIX_history['d'] = h_d
            self.POG_FIX_history['c'] = h_c

            filtered_data_records['FPOGX'] = x
            filtered_data_records['FPOGY'] = y

        if GazeTrackerDataEnableMessages.POG_LEFT in self.data_types:
            history_x = self.POG_LEFT_history['x']
            history_y = self.POG_LEFT_history['y']
            history_d = self.POG_LEFT_history['d']
            history_c = self.POG_LEFT_history['c']

            [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
                validated_data_records['LPOGX'],
                validated_data_records['LPOGY'],
                history_x, history_y, history_d, history_c)

            self.POG_LEFT_history['x'] = h_x
            self.POG_LEFT_history['y'] = h_y
            self.POG_LEFT_history['d'] = h_d
            self.POG_LEFT_history['c'] = h_c

            filtered_data_records['LPOGX'] = x
            filtered_data_records['LPOGY'] = y

        if GazeTrackerDataEnableMessages.POG_RIGHT in self.data_types:
            history_x = self.POG_RIGHT_history['x']
            history_y = self.POG_RIGHT_history['y']
            history_d = self.POG_RIGHT_history['d']
            history_c = self.POG_RIGHT_history['c']

            [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
                validated_data_records['RPOGX'],
                validated_data_records['RPOGY'],
                history_x, history_y, history_d, history_c)

            self.POG_RIGHT_history['x'] = h_x
            self.POG_RIGHT_history['y'] = h_y
            self.POG_RIGHT_history['d'] = h_d
            self.POG_RIGHT_history['c'] = h_c

            filtered_data_records['RPOGX'] = x
            filtered_data_records['RPOGY'] = y

        if GazeTrackerDataEnableMessages.POG_BEST in self.data_types:
            history_x = self.POG_BEST_history['x']
            history_y = self.POG_BEST_history['y']
            history_d = self.POG_BEST_history['d']
            history_c = self.POG_BEST_history['c']

            [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
                validated_data_records['BPOGX'],
                validated_data_records['BPOGY'],
                history_x, history_y, history_d, history_c)

            self.POG_BEST_history['x'] = h_x
            self.POG_BEST_history['y'] = h_y
            self.POG_BEST_history['d'] = h_d
            self.POG_BEST_history['c'] = h_c

            filtered_data_records['BPOGX'] = x
            filtered_data_records['BPOGY'] = y

        if GazeTrackerDataEnableMessages.PUPIL_LEFT in self.data_types:
            history_x = self.PUPIL_LEFT_history['x']
            history_y = self.PUPIL_LEFT_history['y']
            history_d = self.PUPIL_LEFT_history['d']
            history_c = self.PUPIL_LEFT_history['c']

            [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
                validated_data_records['LPCX'],
                validated_data_records['LPCY'],
                history_x, history_y, history_d, history_c)

            self.PUPIL_LEFT_history['x'] = h_x
            self.PUPIL_LEFT_history['y'] = h_y
            self.PUPIL_LEFT_history['d'] = h_d
            self.PUPIL_LEFT_history['c'] = h_c

            filtered_data_records['LPCX'] = x
            filtered_data_records['LPCY'] = y

        if GazeTrackerDataEnableMessages.PUPIL_RIGHT in self.data_types:
            history_x = self.PUPIL_RIGHT_history['x']
            history_y = self.PUPIL_RIGHT_history['y']
            history_d = self.PUPIL_RIGHT_history['d']
            history_c = self.PUPIL_RIGHT_history['c']

            [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
                validated_data_records['RPCX'],
                validated_data_records['RPCY'],
                history_x, history_y, history_d, history_c)

            self.PUPIL_RIGHT_history['x'] = h_x
            self.PUPIL_RIGHT_history['y'] = h_y
            self.PUPIL_RIGHT_history['d'] = h_d
            self.PUPIL_RIGHT_history['c'] = h_c

            filtered_data_records['RPCX'] = x
            filtered_data_records['RPCY'] = y

        if GazeTrackerDataEnableMessages.EYE_LEFT in self.data_types:
            history_x = self.EYE_LEFT_history['x']
            history_y = self.EYE_LEFT_history['y']
            history_d = self.EYE_LEFT_history['d']
            history_c = self.EYE_LEFT_history['c']

            [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
                validated_data_records['LEYEX'],
                validated_data_records['LEYEY'],
                history_x, history_y, history_d, history_c)

            self.EYE_LEFT_history['x'] = h_x
            self.EYE_LEFT_history['y'] = h_y
            self.EYE_LEFT_history['d'] = h_d
            self.EYE_LEFT_history['c'] = h_c

            filtered_data_records['LEYEX'] = x
            filtered_data_records['LEYEY'] = y

        if GazeTrackerDataEnableMessages.EYE_RIGHT in self.data_types:
            history_x = self.EYE_RIGHT_history['x']
            history_y = self.EYE_RIGHT_history['y']
            history_d = self.EYE_RIGHT_history['d']
            history_c = self.EYE_RIGHT_history['c']

            [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
                validated_data_records['REYEX'],
                validated_data_records['REYEY'],
                history_x, history_y, history_d, history_c)

            self.EYE_RIGHT_history['x'] = h_x
            self.EYE_RIGHT_history['y'] = h_y
            self.EYE_RIGHT_history['d'] = h_d
            self.EYE_RIGHT_history['c'] = h_c

            filtered_data_records['REYEX'] = x
            filtered_data_records['REYEY'] = y

        if GazeTrackerDataEnableMessages.CURSOR in self.data_types:
            history_x = self.CURSOR_history['x']
            history_y = self.CURSOR_history['y']
            history_d = self.CURSOR_history['d']
            history_c = self.CURSOR_history['c']

            [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
                validated_data_records['CX'],
                validated_data_records['CY'],
                history_x, history_y, history_d, history_c)

            self.CURSOR_history['x'] = h_x
            self.CURSOR_history['y'] = h_y
            self.CURSOR_history['d'] = h_d
            self.CURSOR_history['c'] = h_c

            filtered_data_records['CX'] = x
            filtered_data_records['CY'] = y

        return filtered_data_records

    def filter_data_points_with_customized_moving_average(self, x_input, y_input,
                                                          history_x, history_y, history_d, history_c):

        # update filter history

        xpos = x_input
        ypos = y_input

        history_x.get_nowait()
        history_x.put_nowait(xpos)

        history_y.get_nowait()
        history_y.put_nowait(ypos)

        # apply filter

        x = xpos
        y = ypos

        x_list = []
        for elem in list(history_x.queue):
            x_list.append(elem)

        y_list = []
        for elem in list(history_y.queue):
            y_list.append(elem)

        old_x = x_list[self.history_size - 2]
        new_x = x_list[self.history_size - 1]

        old_y = y_list[self.history_size - 2]
        new_y = y_list[self.history_size - 2]

        if x_list[0:10] == [0] * 10 and y_list[0:10] == [0] * 10:
            just_started = True
        else:
            just_started = False

        if just_started is False:
            d = math.sqrt((old_x - new_x) ** 2 + (old_y - new_y) ** 2)
            history_d.get_nowait()
            history_d.put_nowait(d)

            d_list = []
            for elem in list(history_d.queue):
                d_list.append(elem)

            d_average = sum(d_list) / self.d_history_size

            if d_average < self.moving_average_d_threshold:

                if history_c < self.history_size:
                    history_c += 1
                else:
                    history_c = self.history_size

                # reversing the list of points so that it will only average the recent ones
                x_list_reversed = x_list
                x_list_reversed.reverse()
                y_list_reversed = y_list
                y_list_reversed.reverse()
                x_average = sum(x_list_reversed[0:history_c]) / history_c
                y_average = sum(y_list_reversed[0:history_c]) / history_c

                x = x_average
                y = y_average

            else:
                history_c = 0
                x = new_x
                y = new_y

        return [x, y, history_x, history_y, history_d, history_c]

    def set_use_moving_average_filter(self, use_moving_average_filter):
        self.use_moving_average_filter = use_moving_average_filter

    # </editor-fold>

    def run(self):
        while True:
            try:
                pass
                output_data = self.get_processed_data()
                self.pog.emit(output_data)

            except:
                pass



class GazeDataThread(threading.Thread):
    def __init__(self, gaze_tracker_socket, queue):
        threading.Thread.__init__(self)
        self.socket = gaze_tracker_socket
        self.queue = queue
        self._loop = True
        self.message_length = 0
        self.reply = ''
        self.setName("GazeDataThread")

    def run(self):
        while True:
            try:
                read = [self.socket.sock]
                while read:
                    read, write, error = select.select([self.socket.sock], [], [], 0.0)
                    self.reply = self.socket.receive_message(self.message_length)
                    self.queue.put_nowait(self.reply)

            except socket.timeout:
                pass

            except Queue.Full:
                self.queue.get_nowait()

    def set_message_length(self, length):
        self.message_length = length


class GazeTrackerClient(object):
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.is_socket_client_opened = False

    def connect(self, host, port):
        self.sock.connect((host, port))
        self.is_socket_client_opened = True

    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def set_timeout(self, timeout):
        self.sock.settimeout(timeout)

    def send_message(self, content):
        total_sent = 0
        while total_sent < len(content):
            sent = self.sock.send(content[total_sent:])
            if sent == 0:
                raise RunTimeError("socket connection broken")
            total_sent = total_sent + sent

    def receive_message(self, message_length):
        chunks = []
        bytes_received = 0
        while bytes_received < message_length:
            chunk = self.sock.recv(min(message_length - bytes_received, 2048))

            if chunk == '':
                raise RuntimeError("socket connection broken")

            chunks.append(chunk)
            bytes_received += len(chunk)

        message = ''.join(chunks)
        return message


# import select
# import socket
# import sys
# import threading
# import multiprocessing
# from xml.dom import minidom
# import math
# import Queue
#
# sys.path.insert(0, '../globals')
# from gaze_tracker_comm_protocol import *
#
#
# class GazeTrackerProcess(multiprocessing.Process):
#
#     def set_values(self, data_types, queue):
#         self.data_types = data_types
#         self.queue = queue
#
#     def init(self):
#         # ---------------------------#
#         #     VARIABLES              #
#         # ---------------------------#
#
#         # self.data_types = data_types
#
#         # <editor-fold desc="network variables">
#         self.gaze_tracker_address = None
#         self.gaze_tracker_socket = None
#         # </editor-fold>
#
#         # <editor-fold desc="data variables">
#         self.raw_data_queue = Queue.Queue(4)
#         self.xml_data_string = None
#         self.unprocessed_data_records = None
#         self.validated_data_records = None
#         self.filtered_data_records = None
#
#         self.processed_data_queue = Queue.Queue(4)
#         self.parsed_reply = None
#         self.reply = None
#         # </editor-fold>
#
#         # <editor-fold desc="threading variables">
#         self.gaze_data_thread = None
#         self.data_transmission_thread_started = False
#         # </editor-fold>
#
#         # <editor-fold desc="moving average filter variables">
#         self.use_moving_average_filter = False
#         self.last_valid_data_records = None
#         self.history_size = 0
#         self.d_history_size = 0
#         self.moving_average_d_threshold = 0
#
#         self.POG_FIX_history = {}
#         self.POG_LEFT_history = {}
#         self.POG_RIGHT_history = {}
#         self.POG_BEST_history = {}
#         self.PUPIL_LEFT_history = {}
#         self.PUPIL_RIGHT_history = {}
#         self.EYE_LEFT_history = {}
#         self.EYE_RIGHT_history = {}
#         self.CURSOR_history = {}
#         # </editor-fold>
#
#         # ---------------------------#
#         #     METHOD CALLS           #
#         # ---------------------------#
#         self.initialize_moving_average_filter_parameters()
#         self.initialize_gaze_tracker_connection()
#         self.send_enable_send_data_messages()
#
#         print "init ended"
#
#     # <editor-fold desc="gaze tracker connection functions">
#     def initialize_gaze_tracker_connection(self):
#
#         while True:
#             self.connect_gaze_tracker_socket()
#             if self.reply == ACK_ENABLE_SEND_DATA:
#                 break
#             self.disconnect_gaze_tracker_socket()
#
#         self.initialize_data_transmission_thread()
#
#     def connect_gaze_tracker_socket(self):
#         print "CONNNECTED TO GAZE TRACKER SOCKET"
#         self.gaze_tracker_address = GAZE_TRACKER_IP_ADDRESS
#         self.parsed_reply = ''
#         self.reply = ''
#
#         self.gaze_tracker_socket = GazeTrackerClient()
#
#         try:
#             self.gaze_tracker_socket.connect(self.gaze_tracker_address, GAZE_TRACKER_PORT)
#             self.gaze_tracker_socket.sock.settimeout(TIMEOUT_INITIAL)
#
#         except socket.error as socket_error:
#             print(SOCKET_ERROR_MESSAGE, socket_error)
#
#         else:
#             print SOCKET_CONNECTED
#             self.gaze_tracker_socket.set_timeout(TIMEOUT_ERROR)
#
#         if self.gaze_tracker_socket.is_socket_client_opened:
#             self.initialize_data_transmission()
#
#     def disconnect_gaze_tracker_socket(self):
#         if self.gaze_tracker_socket.is_socket_client_opened:
#
#             try:
#                 self.gaze_tracker_socket.disconnect()
#
#             except socket.error as socket_error:
#                 print(SOCKET_ERROR_MESSAGE, socket_error)
#             else:
#                 print SOCKET_DISCONNECTED
#
#     # </editor-fold>
#
#     # <editor-fold desc="data transmission initialization functions">
#     def initialize_data_transmission(self):
#
#         # (1) Send enable data transmission
#         message = SET_ENABLE_SEND_DATA
#         self.gaze_tracker_socket.send_message(message)
#         print message
#
#         # (2) Receive ack for data transmission
#         try:
#             self.reply = self.gaze_tracker_socket.receive_message(len(message))
#             print self.reply
#
#         except:
#             print MESSAGE_ERROR
#
#     def initialize_data_transmission_thread(self):
#         self.gaze_data_thread = GazeDataThread(self.gaze_tracker_socket, self.raw_data_queue)
#         self.gaze_data_thread.set_message_length(REPLY_MESSAGE_LENGTH)
#         self.gaze_data_thread.daemon = True
#         self.gaze_data_thread.start()
#         self.data_transmission_thread_started = True
#
#     def send_enable_send_data_messages(self):
#
#         for data_type in self.data_types:
#             message = data_type
#             self.reply = self.send_and_receive_from_gaze_tracker(message)
#
#     def send_and_receive_from_gaze_tracker(self, message):
#
#         reply = ""
#
#         # (1) Send enable transmission
#         self.gaze_tracker_socket.send_message(message)
#         print "sending to tracker: " + message
#
#         # (2) Receive ack for enable transmission
#         try:
#             reply = self.gaze_tracker_socket.receive_message(len(message))
#
#         except:
#             print MESSAGE_ERROR
#
#         return reply
#
#     # </editor-fold>
#
#     # <editor-fold desc="other gaze tracker functions">
#
#     def start_calibration(self):
#
#         self.connect_gaze_tracker_socket()
#
#         message = SET_CALIBRATE_SHOW_1
#         reply1 = self.send_and_receive_from_gaze_tracker(message)
#
#         message = SET_CALIBRATE_START
#         reply2 = self.send_and_receive_from_gaze_tracker(message)
#
#         return reply1 + " " + reply2
#
#     def exit_calibration(self):
#
#         self.connect_gaze_tracker_socket()
#
#         message = SET_CALIBRATE_SHOW_0
#         reply = self.send_and_receive_from_gaze_tracker(message)
#
#         return reply
#
#     def show_tracker_display(self):
#
#         self.connect_gaze_tracker_socket()
#
#         message = SET_TRACKER_DISPLAY_1
#         reply = self.send_and_receive_from_gaze_tracker(message)
#
#         return reply
#
#     def hide_tracker_display(self):
#
#         self.connect_gaze_tracker_socket()
#
#         message = SET_TRACKER_DISPLAY_0
#         reply = self.send_and_receive_from_gaze_tracker(message)
#
#         return reply
#
#     # </editor-fold>
#
#     # <editor-fold desc="data processing functions">
#     def get_processed_data(self):
#
#         if self.data_transmission_thread_started and not self.raw_data_queue.empty():
#             # (1) parse raw string to produce xml data string
#             self.xml_data_string = self.parse_raw_string(self.raw_data_queue.get_nowait())
#
#             if self.xml_data_string != "":
#
#                 # (2) parse xml string to produce unprocessed data records
#                 self.unprocessed_data_records = self.parse_xml_string(self.xml_data_string)
#
#                 # (3) validate data records
#                 self.validated_data_records = self.validate_parsed_data(self.unprocessed_data_records)
#
#                 output_data = self.validated_data_records
#
#                 # (4) filter data records
#                 if self.use_moving_average_filter:
#                     self.filtered_data_records = \
#                         self.filter_data_records_with_customized_moving_average(self.validated_data_records)
#
#                     output_data = self.filtered_data_records
#
#                 try:
#                     self.processed_data_queue.put_nowait(output_data)
#                 except Queue.Full:
#                     self.processed_data_queue.get_nowait()
#
#         return self.processed_data_queue.get_nowait()
#
#     def parse_raw_string(self, input_string):
#
#         reply_string = input_string
#         if reply_string.find("<") and reply_string.find(">") >= 0:
#
#             reply_string_1 = reply_string.split(">")[0]
#             reply_string_2 = reply_string.split(">")[1]
#             self.parsed_reply = self.parsed_reply + reply_string_1
#
#             output = self.parsed_reply + ">"
#             self.parsed_reply = reply_string_2
#
#         elif reply_string.find("<") >= 0:
#             self.parsed_reply = reply_string
#             output = ""
#         elif reply_string.find(">") >= 0:
#             self.parsed_reply = self.parsed_reply + reply_string
#             output = self.parsed_reply + ">"
#         else:
#             self.parsed_reply = self.parsed_reply + reply_string
#             output = ""
#
#         return output
#
#     def validate_parsed_data(self, input_data_records):
#
#         if self.last_valid_data_records is None:
#             self.last_valid_data_records = input_data_records
#
#         # COUNTER, TIME, TIME_TICK, USER, CURSOR
#         if GazeTrackerDataEnableMessages.COUNTER in self.data_types:
#             self.last_valid_data_records['CNT'] = input_data_records['CNT']
#
#         if GazeTrackerDataEnableMessages.TIME in self.data_types:
#             self.last_valid_data_records['TIME'] = input_data_records['TIME']
#
#         if GazeTrackerDataEnableMessages.TIME_TICK in self.data_types:
#             self.last_valid_data_records['TIME_TICK'] = input_data_records['TIME_TICK']
#
#         if GazeTrackerDataEnableMessages.USER_DATA in self.data_types:
#             self.last_valid_data_records['USER'] = input_data_records['USER']
#
#         if GazeTrackerDataEnableMessages.CURSOR in self.data_types:
#             self.last_valid_data_records['CX'] = input_data_records['CX']
#             self.last_valid_data_records['CY'] = input_data_records['CY']
#             self.last_valid_data_records['CS'] = input_data_records['CS']
#
#         # POG FIX
#         if GazeTrackerDataEnableMessages.POG_FIX in self.data_types:
#             if input_data_records['FPOGV'] == 1.0 and \
#                     (input_data_records['FPOGX'] >= 0.0 and input_data_records['FPOGY'] >= 0.0):
#                 self.last_valid_data_records['FPOGX'] = input_data_records['FPOGX']
#                 self.last_valid_data_records['FPOGY'] = input_data_records['FPOGY']
#                 self.last_valid_data_records['FPOGD'] = input_data_records['FPOGD']
#                 self.last_valid_data_records['FPOGID'] = input_data_records['FPOGID']
#                 self.last_valid_data_records['FPOGV'] = input_data_records['FPOGV']
#             else:
#                 self.last_valid_data_records['FPOGV'] = 0.0
#
#         # POG_LEFT
#         if GazeTrackerDataEnableMessages.POG_LEFT in self.data_types:
#             if input_data_records['LPOGV'] == 1.0 and \
#                     (input_data_records['LPOGX'] >= 0.0 and input_data_records['LPOGY'] >= 0.0):
#                 self.last_valid_data_records['LPOGX'] = input_data_records['LPOGX']
#                 self.last_valid_data_records['LPOGY'] = input_data_records['LPOGY']
#                 self.last_valid_data_records['LPOGV'] = input_data_records['LPOGV']
#             else:
#                 self.last_valid_data_records['LPOGV'] = 0.0
#
#         # POG_RIGHT
#         if GazeTrackerDataEnableMessages.POG_RIGHT in self.data_types:
#             if input_data_records['RPOGV'] == 1.0 and \
#                     (input_data_records['RPOGX'] >= 0.0 and input_data_records['RPOGY'] >= 0.0):
#                 self.last_valid_data_records['RPOGX'] = input_data_records['RPOGX']
#                 self.last_valid_data_records['RPOGY'] = input_data_records['RPOGY']
#                 self.last_valid_data_records['RPOGV'] = input_data_records['RPOGV']
#             else:
#                 self.last_valid_data_records['RPOGV'] = 0.0
#
#         # POG_BEST
#         if GazeTrackerDataEnableMessages.POG_BEST in self.data_types:
#             if input_data_records['BPOGV'] == 1.0 and \
#                     (input_data_records['BPOGX'] >= 0.0 and input_data_records['BPOGY'] >= 0.0):
#                 self.last_valid_data_records['BPOGX'] = input_data_records['BPOGX']
#                 self.last_valid_data_records['BPOGY'] = input_data_records['BPOGY']
#                 self.last_valid_data_records['BPOGV'] = input_data_records['BPOGV']
#             else:
#                 self.last_valid_data_records['BPOGV'] = 0.0
#
#         # PUPIL_LEFT
#         if GazeTrackerDataEnableMessages.PUPIL_LEFT in self.data_types:
#             if input_data_records['LPV'] == 1.0 and \
#                     (input_data_records['LPCX'] >= 0.0 and input_data_records['LPCY'] >= 0.0):
#                 self.last_valid_data_records['LPCX'] = input_data_records['LPCX']
#                 self.last_valid_data_records['LPCY'] = input_data_records['LPCY']
#                 self.last_valid_data_records['LPD'] = input_data_records['LPD']
#                 self.last_valid_data_records['LPS'] = input_data_records['LPS']
#                 self.last_valid_data_records['LPV'] = input_data_records['LPV']
#             else:
#                 self.last_valid_data_records['LPV'] = 0.0
#
#         # PUPIL_RIGHT
#         if GazeTrackerDataEnableMessages.PUPIL_RIGHT in self.data_types:
#             if input_data_records['RPV'] == 1.0 and \
#                     (input_data_records['RPCX'] >= 0.0 and input_data_records['RPCY'] >= 0.0):
#                 self.last_valid_data_records['RPCX'] = input_data_records['RPCX']
#                 self.last_valid_data_records['RPCY'] = input_data_records['RPCY']
#                 self.last_valid_data_records['RPD'] = input_data_records['RPD']
#                 self.last_valid_data_records['RPS'] = input_data_records['RPS']
#                 self.last_valid_data_records['RPV'] = input_data_records['RPV']
#             else:
#                 self.last_valid_data_records['RPV'] = 0.0
#
#         # EYE_LEFT
#         if GazeTrackerDataEnableMessages.EYE_LEFT in self.data_types:
#             if input_data_records['LPUPILV'] == 1.0 and \
#                     (input_data_records['LEYEX'] >= 0.0 and input_data_records['LEYEY'] >= 0.0):
#                 self.last_valid_data_records['LEYEX'] = input_data_records['LEYEX']
#                 self.last_valid_data_records['LEYEY'] = input_data_records['LEYEY']
#                 self.last_valid_data_records['LEYEZ'] = input_data_records['LEYEZ']
#                 self.last_valid_data_records['LPUPILD'] = input_data_records['LPUPILD']
#                 self.last_valid_data_records['LPUPILV'] = input_data_records['LPUPILV']
#             else:
#                 self.last_valid_data_records['LPUPILV'] = 0
#
#         # EYE_LEFT
#         if GazeTrackerDataEnableMessages.EYE_RIGHT in self.data_types:
#             if input_data_records['RPUPILV'] == 1.0 and \
#                     (input_data_records['REYEX'] >= 0.0 and input_data_records['REYEY'] >= 0.0):
#                 self.last_valid_data_records['REYEX'] = input_data_records['REYEX']
#                 self.last_valid_data_records['REYEY'] = input_data_records['REYEY']
#                 self.last_valid_data_records['REYEZ'] = input_data_records['REYEZ']
#                 self.last_valid_data_records['RPUPILD'] = input_data_records['RPUPILD']
#                 self.last_valid_data_records['RPUPILV'] = input_data_records['RPUPILV']
#             else:
#                 self.last_valid_data_records['RPUPILV'] = 0
#
#         return self.last_valid_data_records
#
#     @staticmethod
#     def parse_xml_string(raw_xml):
#         data_records = {}
#
#         xmldoc = minidom.parseString(raw_xml)
#         item_list = xmldoc.getElementsByTagName('REC')
#
#         for _ in range(len(GazeTrackerDataEnableMessages.DATA_RECORDS_TYPES)):
#
#             try:
#                 data_records['CNT'] = float(item_list[0].attributes['CNT'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['TIME'] = float(item_list[0].attributes['TIME'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['TIME_TICK'] = float(item_list[0].attributes['TIME_TICK'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['FPOGX'] = float(item_list[0].attributes['FPOGX'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['FPOGY'] = float(item_list[0].attributes['FPOGY'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['FPOGS'] = float(item_list[0].attributes['FPOGS'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['FPOGD'] = float(item_list[0].attributes['FPOGD'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['FPOGID'] = float(item_list[0].attributes['FPOGID'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['FPOGV'] = float(item_list[0].attributes['FPOGV'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPOGX'] = float(item_list[0].attributes['LPOGX'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPOGY'] = float(item_list[0].attributes['LPOGY'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPOGV'] = float(item_list[0].attributes['LPOGV'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPOGX'] = float(item_list[0].attributes['RPOGX'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPOGY'] = float(item_list[0].attributes['RPOGY'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPOGV'] = float(item_list[0].attributes['RPOGV'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['BPOGX'] = float(item_list[0].attributes['BPOGX'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['BPOGY'] = float(item_list[0].attributes['BPOGY'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['BPOGV'] = float(item_list[0].attributes['BPOGV'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPCX'] = float(item_list[0].attributes['LPCX'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPCY'] = float(item_list[0].attributes['LPCY'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPD'] = float(item_list[0].attributes['LPD'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPS'] = float(item_list[0].attributes['LPS'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPV'] = float(item_list[0].attributes['LPV'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPCX'] = float(item_list[0].attributes['RPCX'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPCY'] = float(item_list[0].attributes['RPCY'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPD'] = float(item_list[0].attributes['RPD'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPS'] = float(item_list[0].attributes['RPS'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPV'] = float(item_list[0].attributes['RPV'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LEYEX'] = float(item_list[0].attributes['LEYEX'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LEYEY'] = float(item_list[0].attributes['LEYEY'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LEYEZ'] = float(item_list[0].attributes['LEYEZ'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPUPILD'] = float(item_list[0].attributes['LPUPILD'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['LPUPILV'] = float(item_list[0].attributes['LPUPILV'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['REYEX'] = float(item_list[0].attributes['REYEX'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['REYEY'] = float(item_list[0].attributes['REYEY'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['REYEZ'] = float(item_list[0].attributes['REYEZ'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPUPILD'] = float(item_list[0].attributes['RPUPILD'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['RPUPILV'] = float(item_list[0].attributes['RPUPILV'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['CX'] = float(item_list[0].attributes['CX'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['CY'] = float(item_list[0].attributes['CY'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['CS'] = float(item_list[0].attributes['CS'].value)
#             except:
#                 pass
#
#             try:
#                 data_records['USER'] = str(item_list[0].attributes['USER'].value)
#             except:
#                 pass
#
#         return data_records
#
#     # </editor-fold>
#
#     # <editor-fold desc="moving average filtering functions">
#     def initialize_moving_average_filter_parameters(self):
#         self.use_moving_average_filter = USE_MOVING_AVERAGE_FILTER
#         self.history_size = GAZE_DATA_HISTORY_SIZE
#         self.d_history_size = GAZE_DATA_D_HISTORY_SIZE
#         self.moving_average_d_threshold = GAZE_DATA_MOVING_AVERAGE_D_THRESHOLD
#
#         self.POG_FIX_history['x'] = Queue.Queue(self.history_size)
#         self.POG_FIX_history['y'] = Queue.Queue(self.history_size)
#         self.POG_FIX_history['d'] = Queue.Queue(self.d_history_size)
#         self.POG_FIX_history['c'] = 0
#
#         self.POG_LEFT_history['x'] = Queue.Queue(self.history_size)
#         self.POG_LEFT_history['y'] = Queue.Queue(self.history_size)
#         self.POG_LEFT_history['d'] = Queue.Queue(self.d_history_size)
#         self.POG_LEFT_history['c'] = 0
#
#         self.POG_RIGHT_history['x'] = Queue.Queue(self.history_size)
#         self.POG_RIGHT_history['y'] = Queue.Queue(self.history_size)
#         self.POG_RIGHT_history['d'] = Queue.Queue(self.d_history_size)
#         self.POG_RIGHT_history['c'] = 0
#
#         self.POG_BEST_history['x'] = Queue.Queue(self.history_size)
#         self.POG_BEST_history['y'] = Queue.Queue(self.history_size)
#         self.POG_BEST_history['d'] = Queue.Queue(self.d_history_size)
#         self.POG_BEST_history['c'] = 0
#
#         self.PUPIL_LEFT_history['x'] = Queue.Queue(self.history_size)
#         self.PUPIL_LEFT_history['y'] = Queue.Queue(self.history_size)
#         self.PUPIL_LEFT_history['d'] = Queue.Queue(self.d_history_size)
#         self.PUPIL_LEFT_history['c'] = 0
#
#         self.PUPIL_RIGHT_history['x'] = Queue.Queue(self.history_size)
#         self.PUPIL_RIGHT_history['y'] = Queue.Queue(self.history_size)
#         self.PUPIL_RIGHT_history['d'] = Queue.Queue(self.d_history_size)
#         self.PUPIL_RIGHT_history['c'] = 0
#
#         self.EYE_LEFT_history['x'] = Queue.Queue(self.history_size)
#         self.EYE_LEFT_history['y'] = Queue.Queue(self.history_size)
#         self.EYE_LEFT_history['d'] = Queue.Queue(self.d_history_size)
#         self.EYE_LEFT_history['c'] = 0
#
#         self.EYE_RIGHT_history['x'] = Queue.Queue(self.history_size)
#         self.EYE_RIGHT_history['y'] = Queue.Queue(self.history_size)
#         self.EYE_RIGHT_history['d'] = Queue.Queue(self.d_history_size)
#         self.EYE_RIGHT_history['c'] = 0
#
#         self.CURSOR_history['x'] = Queue.Queue(self.history_size)
#         self.CURSOR_history['y'] = Queue.Queue(self.history_size)
#         self.CURSOR_history['d'] = Queue.Queue(self.d_history_size)
#         self.CURSOR_history['c'] = 0
#
#         for x in range(0, self.history_size):
#             self.POG_FIX_history['x'].put_nowait(0)
#             self.POG_FIX_history['y'].put_nowait(0)
#
#             self.POG_LEFT_history['x'].put_nowait(0)
#             self.POG_LEFT_history['y'].put_nowait(0)
#
#             self.POG_RIGHT_history['x'].put_nowait(0)
#             self.POG_RIGHT_history['y'].put_nowait(0)
#
#             self.POG_BEST_history['x'].put_nowait(0)
#             self.POG_BEST_history['y'].put_nowait(0)
#
#             self.PUPIL_LEFT_history['x'].put_nowait(0)
#             self.PUPIL_LEFT_history['y'].put_nowait(0)
#
#             self.PUPIL_RIGHT_history['x'].put_nowait(0)
#             self.PUPIL_RIGHT_history['y'].put_nowait(0)
#
#             self.EYE_LEFT_history['x'].put_nowait(0)
#             self.EYE_LEFT_history['y'].put_nowait(0)
#
#             self.EYE_RIGHT_history['x'].put_nowait(0)
#             self.EYE_RIGHT_history['y'].put_nowait(0)
#
#             self.CURSOR_history['x'].put_nowait(0)
#             self.CURSOR_history['y'].put_nowait(0)
#
#         for x in range(0, self.d_history_size):
#             self.POG_FIX_history['d'].put_nowait(0)
#             self.POG_LEFT_history['d'].put_nowait(0)
#             self.POG_RIGHT_history['d'].put_nowait(0)
#             self.POG_BEST_history['d'].put_nowait(0)
#             self.PUPIL_LEFT_history['d'].put_nowait(0)
#             self.PUPIL_RIGHT_history['d'].put_nowait(0)
#             self.EYE_LEFT_history['d'].put_nowait(0)
#             self.EYE_RIGHT_history['d'].put_nowait(0)
#             self.CURSOR_history['d'].put_nowait(0)
#
#     def filter_data_records_with_customized_moving_average(self, validated_data_records):
#
#         filtered_data_records = validated_data_records
#
#         if GazeTrackerDataEnableMessages.POG_FIX in self.data_types:
#             history_x = self.POG_FIX_history['x']
#             history_y = self.POG_FIX_history['y']
#             history_d = self.POG_FIX_history['d']
#             history_c = self.POG_FIX_history['c']
#
#             [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
#                 validated_data_records['FPOGX'],
#                 validated_data_records['FPOGY'],
#                 history_x, history_y, history_d, history_c)
#
#             self.POG_FIX_history['x'] = h_x
#             self.POG_FIX_history['y'] = h_y
#             self.POG_FIX_history['d'] = h_d
#             self.POG_FIX_history['c'] = h_c
#
#             filtered_data_records['FPOGX'] = x
#             filtered_data_records['FPOGY'] = y
#
#         if GazeTrackerDataEnableMessages.POG_LEFT in self.data_types:
#             history_x = self.POG_LEFT_history['x']
#             history_y = self.POG_LEFT_history['y']
#             history_d = self.POG_LEFT_history['d']
#             history_c = self.POG_LEFT_history['c']
#
#             [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
#                 validated_data_records['LPOGX'],
#                 validated_data_records['LPOGY'],
#                 history_x, history_y, history_d, history_c)
#
#             self.POG_LEFT_history['x'] = h_x
#             self.POG_LEFT_history['y'] = h_y
#             self.POG_LEFT_history['d'] = h_d
#             self.POG_LEFT_history['c'] = h_c
#
#             filtered_data_records['LPOGX'] = x
#             filtered_data_records['LPOGY'] = y
#
#         if GazeTrackerDataEnableMessages.POG_RIGHT in self.data_types:
#             history_x = self.POG_RIGHT_history['x']
#             history_y = self.POG_RIGHT_history['y']
#             history_d = self.POG_RIGHT_history['d']
#             history_c = self.POG_RIGHT_history['c']
#
#             [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
#                 validated_data_records['RPOGX'],
#                 validated_data_records['RPOGY'],
#                 history_x, history_y, history_d, history_c)
#
#             self.POG_RIGHT_history['x'] = h_x
#             self.POG_RIGHT_history['y'] = h_y
#             self.POG_RIGHT_history['d'] = h_d
#             self.POG_RIGHT_history['c'] = h_c
#
#             filtered_data_records['RPOGX'] = x
#             filtered_data_records['RPOGY'] = y
#
#         if GazeTrackerDataEnableMessages.POG_BEST in self.data_types:
#             history_x = self.POG_BEST_history['x']
#             history_y = self.POG_BEST_history['y']
#             history_d = self.POG_BEST_history['d']
#             history_c = self.POG_BEST_history['c']
#
#             [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
#                 validated_data_records['BPOGX'],
#                 validated_data_records['BPOGY'],
#                 history_x, history_y, history_d, history_c)
#
#             self.POG_BEST_history['x'] = h_x
#             self.POG_BEST_history['y'] = h_y
#             self.POG_BEST_history['d'] = h_d
#             self.POG_BEST_history['c'] = h_c
#
#             filtered_data_records['BPOGX'] = x
#             filtered_data_records['BPOGY'] = y
#
#         if GazeTrackerDataEnableMessages.PUPIL_LEFT in self.data_types:
#             history_x = self.PUPIL_LEFT_history['x']
#             history_y = self.PUPIL_LEFT_history['y']
#             history_d = self.PUPIL_LEFT_history['d']
#             history_c = self.PUPIL_LEFT_history['c']
#
#             [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
#                 validated_data_records['LPCX'],
#                 validated_data_records['LPCY'],
#                 history_x, history_y, history_d, history_c)
#
#             self.PUPIL_LEFT_history['x'] = h_x
#             self.PUPIL_LEFT_history['y'] = h_y
#             self.PUPIL_LEFT_history['d'] = h_d
#             self.PUPIL_LEFT_history['c'] = h_c
#
#             filtered_data_records['LPCX'] = x
#             filtered_data_records['LPCY'] = y
#
#         if GazeTrackerDataEnableMessages.PUPIL_RIGHT in self.data_types:
#             history_x = self.PUPIL_RIGHT_history['x']
#             history_y = self.PUPIL_RIGHT_history['y']
#             history_d = self.PUPIL_RIGHT_history['d']
#             history_c = self.PUPIL_RIGHT_history['c']
#
#             [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
#                 validated_data_records['RPCX'],
#                 validated_data_records['RPCY'],
#                 history_x, history_y, history_d, history_c)
#
#             self.PUPIL_RIGHT_history['x'] = h_x
#             self.PUPIL_RIGHT_history['y'] = h_y
#             self.PUPIL_RIGHT_history['d'] = h_d
#             self.PUPIL_RIGHT_history['c'] = h_c
#
#             filtered_data_records['RPCX'] = x
#             filtered_data_records['RPCY'] = y
#
#         if GazeTrackerDataEnableMessages.EYE_LEFT in self.data_types:
#             history_x = self.EYE_LEFT_history['x']
#             history_y = self.EYE_LEFT_history['y']
#             history_d = self.EYE_LEFT_history['d']
#             history_c = self.EYE_LEFT_history['c']
#
#             [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
#                 validated_data_records['LEYEX'],
#                 validated_data_records['LEYEY'],
#                 history_x, history_y, history_d, history_c)
#
#             self.EYE_LEFT_history['x'] = h_x
#             self.EYE_LEFT_history['y'] = h_y
#             self.EYE_LEFT_history['d'] = h_d
#             self.EYE_LEFT_history['c'] = h_c
#
#             filtered_data_records['LEYEX'] = x
#             filtered_data_records['LEYEY'] = y
#
#         if GazeTrackerDataEnableMessages.EYE_RIGHT in self.data_types:
#             history_x = self.EYE_RIGHT_history['x']
#             history_y = self.EYE_RIGHT_history['y']
#             history_d = self.EYE_RIGHT_history['d']
#             history_c = self.EYE_RIGHT_history['c']
#
#             [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
#                 validated_data_records['REYEX'],
#                 validated_data_records['REYEY'],
#                 history_x, history_y, history_d, history_c)
#
#             self.EYE_RIGHT_history['x'] = h_x
#             self.EYE_RIGHT_history['y'] = h_y
#             self.EYE_RIGHT_history['d'] = h_d
#             self.EYE_RIGHT_history['c'] = h_c
#
#             filtered_data_records['REYEX'] = x
#             filtered_data_records['REYEY'] = y
#
#         if GazeTrackerDataEnableMessages.CURSOR in self.data_types:
#             history_x = self.CURSOR_history['x']
#             history_y = self.CURSOR_history['y']
#             history_d = self.CURSOR_history['d']
#             history_c = self.CURSOR_history['c']
#
#             [x, y, h_x, h_y, h_d, h_c] = self.filter_data_points_with_customized_moving_average(
#                 validated_data_records['CX'],
#                 validated_data_records['CY'],
#                 history_x, history_y, history_d, history_c)
#
#             self.CURSOR_history['x'] = h_x
#             self.CURSOR_history['y'] = h_y
#             self.CURSOR_history['d'] = h_d
#             self.CURSOR_history['c'] = h_c
#
#             filtered_data_records['CX'] = x
#             filtered_data_records['CY'] = y
#
#         return filtered_data_records
#
#     def filter_data_points_with_customized_moving_average(self, x_input, y_input,
#                                                           history_x, history_y, history_d, history_c):
#
#         # update filter history
#
#         xpos = x_input
#         ypos = y_input
#
#         history_x.get_nowait()
#         history_x.put_nowait(xpos)
#
#         history_y.get_nowait()
#         history_y.put_nowait(ypos)
#
#         # apply filter
#
#         x = xpos
#         y = ypos
#
#         x_list = []
#         for elem in list(history_x.queue):
#             x_list.append(elem)
#
#         y_list = []
#         for elem in list(history_y.queue):
#             y_list.append(elem)
#
#         old_x = x_list[self.history_size - 2]
#         new_x = x_list[self.history_size - 1]
#
#         old_y = y_list[self.history_size - 2]
#         new_y = y_list[self.history_size - 2]
#
#         if x_list[0:10] == [0] * 10 and y_list[0:10] == [0] * 10:
#             just_started = True
#         else:
#             just_started = False
#
#         if just_started is False:
#             d = math.sqrt((old_x - new_x) ** 2 + (old_y - new_y) ** 2)
#             history_d.get_nowait()
#             history_d.put_nowait(d)
#
#             d_list = []
#             for elem in list(history_d.queue):
#                 d_list.append(elem)
#
#             d_average = sum(d_list) / self.d_history_size
#
#             if d_average < self.moving_average_d_threshold:
#
#                 if history_c < self.history_size:
#                     history_c += 1
#                 else:
#                     history_c = self.history_size
#
#                 # reversing the list of points so that it will only average the recent ones
#                 x_list_reversed = x_list
#                 x_list_reversed.reverse()
#                 y_list_reversed = y_list
#                 y_list_reversed.reverse()
#                 x_average = sum(x_list_reversed[0:history_c]) / history_c
#                 y_average = sum(y_list_reversed[0:history_c]) / history_c
#
#                 x = x_average
#                 y = y_average
#
#             else:
#                 history_c = 0
#                 x = new_x
#                 y = new_y
#
#         return [x, y, history_x, history_y, history_d, history_c]
#
#     def set_use_moving_average_filter(self, use_moving_average_filter):
#         self.use_moving_average_filter = use_moving_average_filter
#
#     # </editor-fold>
#
#     def run(self):
#         self.init()
#
#         while True:
#             try:
#                 output_data = self.get_processed_data()
#                 self.queue.put_nowait(output_data)
#
#             except:
#                 pass
#
#
# class GazeDataThread(threading.Thread):
#     def __init__(self, gaze_tracker_socket, queue):
#         threading.Thread.__init__(self)
#         self.socket = gaze_tracker_socket
#         self.queue = queue
#         self._loop = True
#         self.message_length = 0
#         self.reply = ''
#         self.setName("GazeDataThread")
#
#     def run(self):
#         while True:
#             try:
#                 read = [self.socket.sock]
#                 while read:
#                     read, write, error = select.select([self.socket.sock], [], [], 0.0)
#                     self.reply = self.socket.receive_message(self.message_length)
#                     self.queue.put_nowait(self.reply)
#
#             except socket.timeout:
#                 pass
#
#             except Queue.Full:
#                 self.queue.get_nowait()
#
#     def set_message_length(self, length):
#         self.message_length = length
#
#
# class GazeTrackerClient(object):
#     def __init__(self, sock=None):
#         if sock is None:
#             self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         else:
#             self.sock = sock
#
#         self.is_socket_client_opened = False
#
#     def connect(self, host, port):
#         self.sock.connect((host, port))
#         self.is_socket_client_opened = True
#
#     def disconnect(self):
#         self.sock.shutdown(socket.SHUT_RDWR)
#         self.sock.close()
#
#     def set_timeout(self, timeout):
#         self.sock.settimeout(timeout)
#
#     def send_message(self, content):
#         total_sent = 0
#         while total_sent < len(content):
#             sent = self.sock.send(content[total_sent:])
#             if sent == 0:
#                 raise RunTimeError("socket connection broken")
#             total_sent = total_sent + sent
#
#     def receive_message(self, message_length):
#         chunks = []
#         bytes_received = 0
#         while bytes_received < message_length:
#             chunk = self.sock.recv(min(message_length - bytes_received, 2048))
#
#             if chunk == '':
#                 raise RuntimeError("socket connection broken")
#
#             chunks.append(chunk)
#             bytes_received += len(chunk)
#
#         message = ''.join(chunks)
#         return message
