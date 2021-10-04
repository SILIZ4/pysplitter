import sys
import json
from PyQt5 import QtCore, QtWidgets, QtGui

from pysplitter.core.splitter import Splitter
from pysplitter.core.splits import Splits

from pysplitter.ui.segments import SegmentsLayout
from pysplitter.ui.import_export import ImportExportLayout
from pysplitter.config import keymaps, refresh_delay


class MainWindow(QtWidgets.QWidget):
    default_segments = ["End"]

    def __init__(self, parent=None, *args):
        super().__init__(*args)
        self.setGeometry(0, 0, 200, 800)
        self.setMinimumWidth(500)
        self.setStyleSheet("background-color: #c9c9c9;")

        self.splitter = Splitter(self.default_segments)
        self.splits = None

        self.main_layout = QtWidgets.QVBoxLayout()
        self.segments_layout = SegmentsLayout(self.default_segments, self.splitter.get_time, self.splitter.get_current_segment, self.get_splits)
        self.main_layout.addLayout(self.segments_layout)
        self.main_layout.addLayout(ImportExportLayout(self.default_segments, self.set_splits, self.get_splits))

        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.setInterval(int(refresh_delay*1e3))
        self.refresh_timer.timeout.connect(self._refresh_display)
        self.refresh_timer.start()

        self.setLayout(self.main_layout)
        self.setWindowTitle("PySplitter")

        self.key_action = {
                keymaps["split"]: self.split,
                keymaps["reset"]: self.reset,
                keymaps["undo"] : self.undo_split,
            }

    def set_splits(self, splits: Splits):
        self.splits = splits
        self.splitter.set_segments(splits.segment_names.copy())
        self.segments_layout.clear_times()
        self.segments_layout.set_segments_names(splits.segment_names.copy())

    def get_splits(self)->Splits:
        return self.splits

    def split(self):
        if self.splits is not None and not self.splitter.is_run_finished():
            self.splitter.split()
            self._refresh_display(True)
            if self.splitter.is_run_finished():
                self.end_run()

    def _refresh_display(self, changed_split=False):
        self.segments_layout._refresh(changed_split)

    def undo_split(self):
        self.segments_layout._erase_current_split()
        self.splitter.undo_split()

    def reset(self):
        self.splitter.reset()
        self.segments_layout.clear_times()

    def end_run(self):
        self.splits.update_times(*self.splitter.get_time("all"))

    def keyPressEvent(self, event):
        if event.key() in self.key_action.keys():
            self.key_action[event.key()]()
        event.accept()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
