import sys
from pyqtgraph.Qt import QtCore, QtGui


sys.path.insert(0, '../user_study_bases')
from us_machine_client_interface import USMachineClientInterface

sys.path.insert(0, '../globals')
from common_constants import *
from states import *


class SoftwarePhantom(USMachineClientInterface):
    def __init__(self, screen_width_input, screen_height_input, interaction):
        super(SoftwarePhantom, self).__init__(screen_width_input, screen_height_input, interaction, DIR_SP_HOME)

        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#

    def keyPressEvent(self, event):
        super(SoftwarePhantom, self).keyPressEvent(event)

        key = event.key()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPLICATION_TITLE_SP)

    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    main = SoftwarePhantom(width, height, Interaction.GAZE_SUPPORTED)
    main.show()

    sys.exit(app.exec_())
