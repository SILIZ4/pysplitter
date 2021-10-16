import os, sys
import json
from PyQt5 import QtCore, QtWidgets, QtGui

from pysplitter.core.splits import Splits
from pysplitter.config import keymaps


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
        file_path, _ = ask_load_file_name("Choose the splits file")
        if file_path:
            self.set_splits(Splits.load_from_file(file_path))

    def save_splits(self):
        file_path, _ = ask_save_file_name("Choose a file name to save the splits")
        if file_path:
            self.get_splits().write_to_file(file_path)
