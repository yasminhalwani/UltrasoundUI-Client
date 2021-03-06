import sys
from pyqtgraph.Qt import QtCore, QtGui

sys.path.insert(0, '../user_study_bases')
from gamified_user_study_base_FZ import GamifiedUserStudyBase

sys.path.insert(0, '../globals')
from common_constants import *
from states import *


class GNoB_FZ(GamifiedUserStudyBase):
    def __init__(self, screen_width_input, screen_height_input, interaction):
        super(GNoB_FZ, self).__init__(screen_width_input, screen_height_input,
                                      interaction, DIR_GAMIFIED_FAST_ZOOM_HOME)

        # ---------------------------#
        #     VARIABLES              #
        # ---------------------------#

        # ---------------------------#
        #     METHOD CALLS           #
        # ---------------------------#

    def keyPressEvent(self, event):
        super(GNoB_FZ, self).keyPressEvent(event)

        key = event.key()

        if key == QtCore.Qt.Key_0:
            pass


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName(APPLICATION_TITLE_GNOB_FZ)

    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    main = GNoB_FZ(width, height, Interaction.GAZE_SUPPORTED)
    main.show()

    sys.exit(app.exec_())
