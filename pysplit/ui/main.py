import sys
from PyQt5 import QtCore, QtWidgets, QtGui

from pysplit.core.splitter import Splitter
import segments
import import_export


segment_names = ["a", "b", "c"]

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        super().__init__(*args)
        self.setGeometry(0, 0, 200, 800)

        self.splitter = Splitter(segment_names)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.segments_layout = segments.SegmentsLayout(segment_names)
        self.main_layout.addLayout(self.segments_layout)
        self.main_layout.addLayout(import_export.ImportExportLayout(segment_names, self.set_splits, self.get_splits))

        self.setLayout(self.main_layout)
        self.setWindowTitle("PySplitter")

    def set_splits(self, splits: dict):
        segment_names = list(splits.keys())
        self.splitter.set_segments(segment_names)
        self.segments_layout.set_segments_names(segment_names)

    def get_splits(self)->dict:
        return self.splitter.get_time("all")


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
