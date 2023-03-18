import sys
import warnings
from PyQt5 import QtCore, QtWidgets

from pysplitter.core.splitter import Splitter, TimeInformation
from pysplitter.core.records import SpeedrunRecords
from pysplitter.core.database import update_database

from pysplitter.ui.segments import SegmentsLayout
from pysplitter.ui.import_export import ImportExportLayout
from pysplitter.ui.utils import ask_yes_no_dialog
from pysplitter.config import keymaps, refresh_delay, database_directory, ask_update_database, use_database


class MainWindow(QtWidgets.QWidget):
    default_segments = ["End"]

    def __init__(self, parent=None, *args):
        super().__init__(parent)

        self.key_action = {
                keymaps["split"]:       self.split,
                keymaps["reset"]:       self.reset,
                keymaps["undo"]:        self.undo_split,
                keymaps["load records"]: self.load_records,
                keymaps["save records"]: self.save_records,
                keymaps["quit"]:        self.closeEvent
            }

        self.setGeometry(0, 0, 200, 800)
        self.setMinimumWidth(500)
        self.setStyleSheet("background-color: #292c30; color: #e8effa;")

        self._splitter = Splitter(self.default_segments)
        self.records = None

        self.main_layout = QtWidgets.QVBoxLayout()
        self.segments_layout = SegmentsLayout(
                self.default_segments, self.get_splitter, self._get_records
        )
        self.main_layout.addLayout(self.segments_layout)
        self.import_export_layout = ImportExportLayout(self, self._set_records, self._get_records)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.import_export_layout)

        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.setInterval(int(refresh_delay*1e3))
        self.refresh_timer.timeout.connect(self._refresh_display)
        self.refresh_timer.start()

        self.setLayout(self.main_layout)
        self.setWindowTitle("PySplitter")

    def get_splitter(self):
        return self._splitter

    def split(self):
        if self.records is not None and (self._splitter.is_ongoing or self._splitter.is_ready):
            self._splitter.split()
            self._refresh_display(segment_changed=True)

    def undo_split(self):
        self.segments_layout.erase_current_split()
        self._splitter.undo_split()

    def reset(self):
        if self._splitter.has_run_ended:
            self._ask_update_times()
        self._splitter.reset()
        self.segments_layout.clear_times()

    def load_records(self):
        self._ask_save_records()
        self.import_export_layout.load_records()

    def save_records(self):
        self.import_export_layout.save_records()

    def _get_records(self)->SpeedrunRecords|None:
        return self.records

    def _set_records(self, splits: SpeedrunRecords):
        self.reset()
        self.records = splits
        self._splitter = Splitter(splits.segment_names.copy())
        self.segments_layout.set_segments_names(splits.segment_names.copy())

    def _refresh_display(self, segment_changed=False):
        self.segments_layout.refresh(segment_changed)

    def _ask_update_times(self):
        times = self._splitter.get_time(TimeInformation.ALL_SEGMENTS)
        if times is not None and self.records is not None:
            segment_times, final_time = times

            if use_database:
                if not ask_update_database or (ask_update_database and ask_yes_no_dialog(self, "Add times in the database?")):
                    update_database(database_directory, self.records.name, segment_times)

            if self.records.has_new_records(segment_times, final_time) and ask_yes_no_dialog(self, "Write new record splits?"):
                self.records.update_times(segment_times, final_time)
                if self.records.file_name is None:
                    warnings.warn("Couldn't update records file: path set to None.")
                else:
                    self.records.write_to_file(self.records.file_name)

    def _ask_save_records(self):
        if self.records is not None and not self.records.records_file_up_to_date:
            if ask_yes_no_dialog(self, "Would like to save the unsaved records before closing this speedrun?"):
                self.save_records()

    def closeEvent(self, event=None):
        self._ask_save_records()
        self.close()

    def keyPressEvent(self, event):
        if event.key() in self.key_action.keys():
            self.key_action[event.key()]()
            return True
        event.accept()


def launch_main_window(args):
    app = QtWidgets.QApplication(args)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    launch_main_window(sys.argv)
