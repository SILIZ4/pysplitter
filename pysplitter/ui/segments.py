import sys
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.colors import LinearSegmentedColormap

from pysplitter.config import timer_precision


def get_title_label(text)->QtWidgets.QLabel:
    label = QtWidgets.QLabel(text)
    label.setFont(QtGui.QFont('Arial', 18))
    label.setStyleSheet("QLabel { color : #f2f2f2; background-color: #292929; }")
    label.setAlignment(QtCore.Qt.AlignCenter)
    label.setMaximumHeight(25)
    label.setMinimumHeight(25)
    return label

def get_split_label(text)->QtWidgets.QLabel:
    label = QtWidgets.QLabel(text)
    label.setFont(QtGui.QFont('Arial', 16))
    label.setMinimumHeight(30)
    return label

def get_time_label(text)->QtWidgets.QLabel:
    label = get_split_label(text)
    label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
    return label


def clip_at_unity(x):
    if x>1:
        return 1
    elif x<-1:
        return -1
    return x


class SegmentsLayout(QtWidgets.QGridLayout):
    EMPTY_TIME = "-  "
    color_bins = 60
    delta_cmap = LinearSegmentedColormap.from_list("delta_cmap", ["#36a841", "white", "#991111"], N=color_bins)

    def __init__(self, segment_names, get_time, get_current_split, get_splits):
        super().__init__()
        self.setSpacing(0)

        self.get_current_split = get_current_split
        self.get_time = get_time
        self.get_splits = get_splits

        self.rows = 0
        self.cols = 3

        self._add_segment_row("Segment name", "Segment time", "Delta", is_title=True)
        for i in range(1, self.rows):
            self._add_segment_row(segment_names[i-1], self.EMPTY_TIME, self.EMPTY_TIME, is_title=False)
        self._add_segment_row("Total time", self.EMPTY_TIME, "")

    def _add_segment_row(self, *cols: str, is_title=False):
        assert(len(cols) == self.cols)

        for col, element in enumerate(cols):
            if is_title:
                label = get_title_label(element)
            else:
                if col == 0:
                    label = get_split_label(" "+element)
                else:
                    label = get_time_label(element)

            self.addWidget(label, self.rows, col)

        self.rows += 1

    def _get_formatted_time(self, time):
        hours, rem = divmod(time, 3600)
        mins, secs = divmod(rem, 60)
        if hours:
            return f"{int(hours):1d}:{int(mins):02d}:{secs:0{timer_precision+3}.{timer_precision}f}"
        if mins:
            return f"{int(mins):1d}:{secs:0{timer_precision+3}.{timer_precision}f}"
        return f"{secs:.{timer_precision}f}s"

    def _set_row_segment_name(self, segment_name: str, row):
        self.itemAtPosition(row, 0).widget().setText(segment_name)

    def _set_row_color(self, row, *args, **kwargs):
        for col in range(self.cols):
            self._set_element_color(row, col, *args, **kwargs)

    def _set_element_color(self, row, col, textcolor=None, background=None):
        _textcolor, _background = textcolor, background
        if textcolor is None:
            _textcolor = "#384459" if row%2==1 else "#e8effa"
        if background is None:
            _background = "#b2c0d6" if row%2==1 else "#556787"

        self.itemAtPosition(row, col).widget()\
                .setStyleSheet("QLabel { color : "+_textcolor+"; background-color: "+_background+"; }")

    def _refresh(self, change_split=False):
        current_segment = self.get_current_split()
        splits = self.get_splits()

        if change_split and current_segment > 0:
            previous_segment_time = round(self.get_time("previous"), timer_precision)
            self.itemAtPosition(current_segment, 1).widget().setText( self._get_formatted_time(previous_segment_time) )
            self._set_delta(previous_segment_time, current_segment-1)

        if 0 <= current_segment < len(splits.segment_names):
            current_segment_time = round(self.get_time("segment"), timer_precision)
            self.itemAtPosition(current_segment+1, 1).widget().setText( self._get_formatted_time(current_segment_time) )
            self.itemAtPosition(self.rows-1, 1).widget().setText( self._get_formatted_time(self.get_time("total")) )

            if splits.pb is not None:
                if current_segment < len(splits.best_splits) and current_segment_time >= splits.best_splits[current_segment]:
                    self._set_delta(current_segment_time, current_segment)

    def _set_delta(self, segment_time, segment_number):
        splits = self.get_splits()

        if splits.best_splits is None or segment_number >= len(splits.best_splits):
            delta, text_color = 0, "gold"

        else:
            if splits.pb is None or segment_number >= len(splits.pb_splits) or splits.pb_splits[segment_number] is None:
                return

            pb_time, best_split = splits.pb_splits[segment_number], splits.best_splits[segment_number]
            delta = segment_time-pb_time

            if segment_time < best_split:
                text_color = "gold"
            else:
                color = self.delta_cmap( self.color_bins*(clip_at_unity(delta)))
                text_color = "rgb(" + ",".join(list(map(lambda x: str(int(255*x)), color[:-1]))) + ")"

        self.itemAtPosition(segment_number+1, 2).widget().setText( f'{delta:+.{timer_precision}f}')
        self._set_element_color(segment_number+1, 2, textcolor=text_color)


    def _erase_row(self, row):
        for col in range(1, self.cols):
            self.itemAtPosition(row, col).widget().setText(self.EMPTY_TIME)

    def erase_current_split(self):
        current_segment = self.get_current_split()
        if current_segment > 0:
            self._erase_row(current_segment+1)
            self._set_row_color(current_segment+1)


    def clear_times(self):
        for i in range(1, self.rows):
            self._erase_row(i)
            if i < self.rows-1:
                self._set_row_color(i)

    def set_segments_names(self, segment_names: list[str]):
        segments_number = len(segment_names)
        row_number = max([segments_number+1, self.rows])

        for i in range(1, row_number):
            if i < segments_number+1:
                if i < self.rows:
                    self._set_row_segment_name(" "+segment_names[i-1], i)
                else:
                    self._add_segment_row(segment_names[i-1], self.EMPTY_TIME, self.EMPTY_TIME)
            else:
                self._set_row_segment_name("", i)
            self._set_row_color(i)

        if segments_number < self.rows-1:
            self._set_row_segment_name("Total time", self.rows-1)
        else:
            self._add_segment_row("Total time", self.EMPTY_TIME, "")
