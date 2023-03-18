import os, pathlib
from PyQt5.QtCore import Qt


absolute_path_to_file = pathlib.Path(__file__).parent.resolve()


keymaps = {
        "split":        Qt.Key.Key_Space,
        "reset":        Qt.Key.Key_R,
        "undo":         Qt.Key.Key_Backspace,
        "load records": Qt.Key.Key_L,
        "save records": Qt.Key.Key_E,
        "quit":         Qt.Key.Key_Q,
    }

database_directory = os.path.join(absolute_path_to_file, "database")

timer_precision = 1  # in decimals
refresh_delay = 0.05  # in seconds, should be smaller than timer precision for correct rendering
use_database = True
ask_update_database = False

# CSS format: e.g. "rgb(R, G, B)", "color name"
best_split_color = "gold"
odd_row_text_color = "#384459"
odd_row_bg_color ="#b2c0d6"
even_row_text_color = "#e8effa"
even_row_bg_color = "#556787"

# Can be any color name supported by matplotlib
time_loss_color = "#991111"
time_gain_color = "#08C421"
# Delta gradient range
worst_time_loss = 30 # in seconds
best_time_gain = 30 # in seconds
