import os, sys
import json
from PyQt5 import QtCore, QtWidgets, QtGui

from pysplitter.core.splits import Splits, InvalidSplitError
from pysplitter.config import keymaps


def display_error_dialog(message):
    error_dialog = QtWidgets.QMessageBox()
    error_dialog.setWindowTitle("Error: Incorrect split file.")
    error_dialog.setText(message)
    error_dialog.exec_()

def validate_split_file_name(file_name):
    if not file_name.endswith(".json"):
        display_error_dialog("Invalid split file. File is not of \".json\" extension.")
        return False
    return True

def ask_save_file_name(prompt):
    return QtWidgets.QFileDialog.getSaveFileName(parent=None,
                    caption="prompt", directory=os.getcwd())

def ask_load_file_name(prompt):
    return QtWidgets.QFileDialog.getOpenFileName(parent=None,
                    caption="prompt", directory=os.getcwd())


class PySplitButton(QtWidgets.QPushButton):
    def __init__(self, main_window, *args, **kwargs):
        self.main_window = main_window
        super().__init__(*args, **kwargs)

    def event(self, event):
        # Redirect event
        if event.type() == QtCore.QEvent.KeyPress and event.key() in keymaps.values():
            return self.main_window.keyPressEvent(event)
        return QtWidgets.QPushButton.event(self, event)


class ImportExportLayout(QtWidgets.QHBoxLayout):
    def __init__(self, main_window, set_splits, get_splits):
        super().__init__()
        self.get_splits = get_splits
        self.set_splits = set_splits

        self.load_button = PySplitButton(main_window, "Load splits")
        self.load_button.pressed.connect(self.load_splits)

        self.save_button = PySplitButton(main_window, "Save splits")
        self.save_button.pressed.connect(self.save_splits)

        self.addWidget(self.load_button)
        self.addWidget(self.save_button)


    def load_splits(self):
        keep_asking = True

        while keep_asking:
            file_path, _ = ask_load_file_name("Choose the splits file.")

            if not file_path:
                keep_asking = False
            else:
                if validate_split_file_name(file_path):
                    try:
                        splits = Splits.load_from_file(file_path)
                        self.set_splits(splits)
                        keep_asking = False

                    except InvalidSplitError as err:
                        display_error_dialog(err.message)



    def save_splits(self):
        keep_asking = True

        while keep_asking:
            file_path, _ = ask_save_file_name("Choose a file name to save the splits.")

            if not file_path:
                keep_asking = False
            else:
                if "." not in file_path:
                    file_path += ".json"

                if validate_split_file_name(file_path):
                    self.get_splits().write_to_file(file_path)
                    keep_asking = False
