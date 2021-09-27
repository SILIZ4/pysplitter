import os, sys
import json
from PyQt5 import QtCore, QtWidgets, QtGui

from pysplitter.core.splits import Splits


def ask_save_file_name(prompt):
    return QtWidgets.QFileDialog.getSaveFileName(parent=None,
                    caption="prompt", directory=os.getcwd())

def ask_load_file_name(prompt):
    return QtWidgets.QFileDialog.getOpenFileName(parent=None,
                    caption="prompt", directory=os.getcwd())


class ImportExportLayout(QtWidgets.QHBoxLayout):
    def __init__(self, segment_names, set_splits, get_splits):
        super().__init__()
        self.get_splits = get_splits
        self.set_splits = set_splits

        self.load_button = QtWidgets.QPushButton("Load splits")
        self.load_button.pressed.connect(self.load_splits)

        self.save_button = QtWidgets.QPushButton("Save splits")
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
