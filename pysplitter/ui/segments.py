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
    EMPTY_TIME = "-"

    def __init__(self, segment_names, get_time, get_current_split):
        super().__init__()
        self.get_current_split = get_current_split
        self.get_time = get_time

        self.rows = 0
        self.cols = 2

        self._add_segment_row("Segment name", "Segment time", is_title=True)
        for i in range(1, self.rows):
            self._add_segment_row(segment_names[i-1], self.EMPTY_TIME)
        self._add_segment_row("Total time", self.EMPTY_TIME)

    def _add_segment_row(self, *cols: str, is_title=False):
        assert(len(cols) == self.cols)

        get_label = get_title_label if is_title else get_split_label
        for col, element in enumerate(cols):
            self.addWidget(get_label(element), self.rows, col)

        self.rows += 1

    def _set_row_segment_name(self, segment_name: str, row):
        self.itemAtPosition(row, 0).widget().setText(segment_name)

    def _refresh(self):
        current_split = self.get_current_split()
        if current_split >= 0:
            self.itemAtPosition(current_split+1, 1).widget().setText( f'{self.get_time("segment"):.1f}')
            self.itemAtPosition(self.rows-1, 1).widget().setText( f'{self.get_time("total"):.1f}')

    def _erase_current_split(self):
        current_split = self.get_current_split()
        if current_split > 0:
            self.itemAtPosition(current_split+1, 1).widget().setText(self.EMPTY_TIME)


    def clear_times(self):
        for i in range(1, self.rows):
            self.itemAtPosition(i, 1).widget().setText(self.EMPTY_TIME)

    def set_segments_names(self, segment_names: list[str]):
        segments_number = len(segment_names)
        line_number = max([segments_number+1, self.rows])

        for i in range(1, line_number):
            if i < segments_number+1:
                if i < self.rows:
                    self._set_row_segment_name(segment_names[i-1], i)
                else:
                    self._add_segment_row(segment_names[i-1], self.EMPTY_TIME)
            else:
                self._set_row_segment_name("", i)

        if segments_number < self.rows-1:
            self._set_row_segment_name("Total time", self.rows-1)
        else:
            self._add_segment_row("Total time", self.EMPTY_TIME)
