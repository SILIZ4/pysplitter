import os, pathlib
from PyQt5.QtCore import Qt
from numpy import absolute


absolute_path_to_file = pathlib.Path(__file__).parent.resolve()


keymaps = {
        "split":       Qt.Key.Key_Space,
        "reset":       Qt.Key.Key_R,
        "undo":        Qt.Key.Key_Backspace,
        "load splits": Qt.Key.Key_L,
        "save splits": Qt.Key.Key_E,
        "quit":        Qt.Key.Key_Q,
    }

database_directory = os.path.join(absolute_path_to_file, "database")

refresh_delay = 0.1  # in seconds
timer_precision = 1  # in decimals
