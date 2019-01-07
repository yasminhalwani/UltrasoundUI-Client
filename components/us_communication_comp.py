from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
import socket
import sys
from PIL import Image
import numpy as np

sys.path.insert(0, '../globals')
from us_machine_comm_protocol import *


class USCommunicationThread(QtCore.QThread, QtGui.QGraphicsView):
    data = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QThread.__init__(self)

        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#
        # <editor-fold description="tcp connection variables">
        self.sonix_address = SERVER_ADDRESS
        self.tcp_commands_port = SERVER_PARAM_PORT
        self.tcp_image_stream_port = SERVER_IMAGE_PORT

        self.client_tcp_commands_socket = None
        self.tcp_commands_socket_last_received_data = None
        self.client_tcp_images_socket = None
        self.are_tcp_connections_established = False
        # </editor-fold>

        # <editor-fold description="received image variables">
        self.received_image_data = None
        self.image_update_timer = None
        self.previous_ultrasound_image = None
        self.image = None
        # </editor-fold>

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#
        self.setup_tcp_commands_connection()

    def run(self):
        while True:
            try:
                if self.are_tcp_connections_established:

                    # We use a timer to limit how many images we request from the server each second:
                    if self.image_update_timer < 1:
                        try:
                            # Create a socket connection for connecting to the server:
                            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            client_socket.connect((self.sonix_address, SERVER_IMAGE_PORT))

                            # Receive data from the server:
                            self.received_image_data = client_socket.recv(SERIALIZED_IMAGE_SIZE)
                            self.image = self.received_image_data

                            # Set the timer back to original value:
                            self.image_update_timer = 1
                        except:
                            print "could not connect to server"
                            self.are_tcp_connections_established = False
                    else:
                        # Count down the timer:
                        self.image_update_timer -= 1

                    # We store the previous received image in case the client fails to
                    # receive all of the data for the new image:
                    self.previous_ultrasound_image = self.image
                    try:

                        self.image = Image.fromstring("L", (OPTIMAL_IMAGE_WIDTH, OPTIMAL_IMAGE_HEIGHT), self.image)

                        self.image = np.array(self.image)
                        self.image = self.image.astype('int16')
                        self.image = np.rot90(self.image)
                        self.image = np.rot90(self.image)
                        self.image = np.rot90(self.image)

                        self.data.emit(self.image)
                    except:
                        # If we failed to receive a new image we display the last image we received:
                        self.image = self.previous_ultrasound_image
            except:
                pass

    def setup_tcp_commands_connection(self):
        self.client_tcp_commands_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_tcp_commands_socket.connect((self.sonix_address, self.tcp_commands_port))

        self.client_tcp_commands_socket.send(CONNECT_TO_SERVER)
        self.tcp_commands_socket_last_received_data = self.client_tcp_commands_socket.recv(64)

        if self.tcp_commands_socket_last_received_data == ACK_CONNECT_TO_SERVER:
            self.client_tcp_commands_socket.send(CONNECT_TO_ULTRASONIX)
            self.tcp_commands_socket_last_received_data = self.client_tcp_commands_socket.recv(64)
            print "received: " + self.tcp_commands_socket_last_received_data

            if self.tcp_commands_socket_last_received_data == ACK_CONNECT_TO_ULTRASONIX:
                self.client_tcp_commands_socket.send(INITIALIZE_IMAGE_ACQUISITION)
                self.tcp_commands_socket_last_received_data = self.client_tcp_commands_socket.recv(64)
                print "received: " + self.tcp_commands_socket_last_received_data

                if self.tcp_commands_socket_last_received_data == ACK_INITIALIZE_IMAGE_ACQUISITION:
                    self.client_tcp_commands_socket.send(START_IMAGE_STREAMING)
                    self.tcp_commands_socket_last_received_data = self.client_tcp_commands_socket.recv(64)
                    print "received: " + self.tcp_commands_socket_last_received_data

                    if self.tcp_commands_socket_last_received_data == ACK_START_IMAGE_STREAMING:
                        self.client_tcp_images_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.client_tcp_images_socket.connect((self.sonix_address, self.tcp_image_stream_port))
                        self.client_tcp_images_socket.send(START_IMAGE_STREAMING)
                        self.are_tcp_connections_established = True

    def param_command_increase_depth(self):
        self.client_tcp_commands_socket.send(PARAM_INC_DEPTH)

    def param_command_decrease_depth(self):
        self.client_tcp_commands_socket.send(PARAM_DEC_DEPTH)

    def param_command_get_depth(self):
        self.client_tcp_commands_socket.send(PARAM_GET_DEPTH)
        value = self.client_tcp_commands_socket.recv(64)
        print value
        return value

    def param_command_increase_gain(self):
        self.client_tcp_commands_socket.send(PARAM_INC_GAIN)

    def param_command_decrease_gain(self):
        self.client_tcp_commands_socket.send(PARAM_DEC_GAIN)

    def param_command_get_gain(self):
        self.client_tcp_commands_socket.send(PARAM_GET_GAIN)
        value = self.client_tcp_commands_socket.recv(64)
        print value
        return value

    def param_command_increase_frequency(self):
        self.client_tcp_commands_socket.send(PARAM_INC_FREQ)

    def param_command_decrease_frequency(self):
        self.client_tcp_commands_socket.send(PARAM_DEC_FREQ)

    def param_command_get_frequency(self):
        self.client_tcp_commands_socket.send(PARAM_GET_FREQ)
        value = self.client_tcp_commands_socket.recv(64)
        print value
        return value

    def param_command_increase_focus(self):
        self.client_tcp_commands_socket.send(PARAM_INC_FOCUS)

    def param_command_decrease_focus(self):
        self.client_tcp_commands_socket.send(PARAM_DEC_FOCUS)

    def param_command_get_focus(self):
        self.client_tcp_commands_socket.send(PARAM_GET_FOCUS)
        value = self.client_tcp_commands_socket.recv(64)
        print value
        return value

    def param_command_toggle_freeze(self):
        self.client_tcp_commands_socket.send(PARAM_TOGGLE_FREEZE)
