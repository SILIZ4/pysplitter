import os
from PyQt5 import QtCore, QtWidgets

from pysplitter.core.records import SpeedrunRecords, InvalidRecordsError
from pysplitter.config import keymaps
from pysplitter.ui.utils import display_error_dialog


def ask_save_file_name(prompt):
    return QtWidgets.QFileDialog.getSaveFileName(
            parent=None, caption=prompt, directory=os.getcwd()
    )

def ask_load_file_name(prompt):
    return QtWidgets.QFileDialog.getOpenFileName(
        parent=None, caption=prompt, directory=os.getcwd()
    )


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
    def __init__(self, main_window, set_records, get_records):
        super().__init__()
        self._get_records = get_records
        self._set_records = set_records

        self.load_button = PySplitButton(main_window, "Load records")
        self.load_button.pressed.connect(self.load_records)

        self.save_button = PySplitButton(main_window, "Save records")
        self.save_button.pressed.connect(self.save_records)

        self.addWidget(self.load_button)
        self.addWidget(self.save_button)


    def load_records(self):
        while True:
            file_path, _ = ask_load_file_name("Choose the records file.")
            if not file_path:
                return
            try:
                records = SpeedrunRecords.load_from_file(file_path)
                self._set_records(records)
                return
            except InvalidRecordsError as error:
                display_error_dialog(error.message)

    def save_records(self):
        while True:
            file_path, _ = ask_save_file_name("Choose a file name to save the records.")

            if not file_path:
                return
            try:
                self._get_records().write_to_file(file_path)
                return
            except OSError as error:
                display_error_dialog("Couldn't write records file: " + error.strerror)
