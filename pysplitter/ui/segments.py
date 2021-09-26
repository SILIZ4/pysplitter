import sys
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui


def get_title_label(text)->QtWidgets.QLabel:
    label = QtWidgets.QLabel(text)
    label.setFont(QtGui.QFont('Arial', 16))
    return label


def get_split_label(text)->QtWidgets.QLabel:
    label = QtWidgets.QLabel(text)
    label.setFont(QtGui.QFont('Arial', 13))
    return label


class SegmentsLayout(QtWidgets.QGridLayout):
    def __init__(self, segment_names):
        super().__init__()
        self.rows = 0
        self.cols = 2

        self._add_segment_row("Segment name", "Segment time", is_title=True)

        for i in range(1, self.rows):
            self._add_segment_row(segment_names[i-1], "")

    def _add_segment_row(self, *cols: str, is_title=False):
        assert(len(cols) == self.cols)

        get_label = get_title_label if is_title else get_split_label
        for col, element in enumerate(cols):
            self.addWidget(get_label(element), self.rows, col)

        self.rows += 1

    def _set_row_segment_name(self, segment_name: str, row):
        self.itemAtPosition(row, 0).widget().setText(segment_name)

    def clear_times(self):
        for i in range(self.rows):
            self.itemAtPosition(i, 1).widget().setText("")

    def set_segments_names(self, segment_names: list[str]):
        for i, segment_name in enumerate(segment_names):
            if i < self.rows:
                self._set_row_segment_name(segment_name, i)
            else:
                self._add_segment_row(segment_name, "")
