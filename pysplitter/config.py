from PyQt5.QtCore import Qt


keymaps = {
        "split":       Qt.Key.Key_Space,
        "reset":       Qt.Key.Key_R,
        "undo":        Qt.Key.Key_Backspace,
        "load splits": Qt.Key.Key_L,
        "save splits": Qt.Key.Key_E,
        "quit":        Qt.Key.Key_Q,
    }

refresh_delay = 0.1  # in seconds
timer_precision = 1  # in decimals
