from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.colors import LinearSegmentedColormap

from pysplitter.config import (
        timer_precision, time_loss_color, time_gain_color,
        worst_time_loss, best_time_gain, best_split_color,
        odd_row_text_color, odd_row_bg_color, even_row_text_color, even_row_bg_color,
)
from pysplitter.core.splitter import TimeInformation


def get_title_label(text)->QtWidgets.QLabel:
    label = QtWidgets.QLabel(text)
    label.setFont(QtGui.QFont('Arial', 18))
    label.setStyleSheet("QLabel { color : #f2f2f2; background-color: #292929; }")
    label.setAlignment(QtCore.Qt.AlignCenter)
    label.setMaximumHeight(25)
    label.setMinimumHeight(25)
    return label

def get_segment_label(text)->QtWidgets.QLabel:
    label = QtWidgets.QLabel(text)
    label.setFont(QtGui.QFont('Arial', 16))
    label.setMinimumHeight(30)
    return label

def get_time_label(text)->QtWidgets.QLabel:
    label = get_segment_label(text)
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
    time_loss_cmap = LinearSegmentedColormap.from_list("delta_cmap", ["gray", time_loss_color], N=color_bins)
    time_gain_cmap = LinearSegmentedColormap.from_list("delta_cmap", ["gray", time_gain_color], N=color_bins)

    def __init__(self, segment_names, get_splitter, get_records):
        super().__init__()
        self.setSpacing(0)

        self._get_splitter = get_splitter
        self._get_records = get_records

        self.rows = 0
        self.cols = 3

        self._add_segment_row("Segment name", "Segment time", "Delta", is_title=True)
        for i in range(1, self.rows):
            self._add_segment_row(segment_names[i-1], self.EMPTY_TIME, self.EMPTY_TIME)
        self._add_segment_row("Total time", self.EMPTY_TIME, "")

    @property
    def splitter(self):
        return self._get_splitter()

    @property
    def records(self):
        return self._get_records()

    def refresh(self, segment_changed=False):
        segment_index = self.splitter.get_current_segment_index()

        if segment_changed and segment_index > 0:
            previous_segment_time = self._get_time(TimeInformation.PREVIOUS_SEGMENT)
            self._set_time(segment_index, 1, previous_segment_time)
            self._set_delta(previous_segment_time, segment_index-1)

        if 0 <= segment_index < len(self.records.segment_names):
            current_split = self._get_time(TimeInformation.CURRENT_SEGMENT)
            self._set_time(segment_index+1, 1, current_split)
            self._set_time(self.rows-1, 1, self._get_time(TimeInformation.CURRENT_TOTAL_TIME))

            if self.records.pb is not None:
                if segment_index < len(self.records.best_splits) and current_split >= self.records.best_splits[segment_index]:
                    self._set_delta(current_split, segment_index)

    def _set_time(self, segment_index, column, time):
        self.itemAtPosition(segment_index, column).widget().setText( self._get_formatted_time(time) )

    def _get_time(self, time_type: TimeInformation):
        return self.splitter.get_time(time_type)

    def erase_current_split(self):
        current_segment = self.splitter.get_current_segment_index()
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

    def _add_segment_row(self, *cols: str, is_title=False):
        assert(len(cols) == self.cols)

        for col, element in enumerate(cols):
            if is_title:
                label = get_title_label(element)
            else:
                if col == 0:
                    label = get_segment_label(" "+element)
                else:
                    label = get_time_label(element)
            self.addWidget(label, self.rows, col)

        self.rows += 1

    def _get_formatted_time(self, time):
        hours, rem = divmod(round(time, timer_precision), 3600)
        mins, secs = divmod(rem, 60)
        if hours:
            return f"{int(hours):1d}:{int(mins):02d}:{secs:0{timer_precision+3}.{timer_precision}f}"
        if mins:
            return f"{int(mins):1d}:{secs:0{timer_precision+3}.{timer_precision}f}"
        return f"{secs:.{timer_precision}f}s"

    def _set_delta(self, split, segment_index):
        if self.records.pb_splits[segment_index] is None:
            return

        pb_time, best_split = self.records.pb_splits[segment_index], self.records.best_splits[segment_index]
        delta = split-pb_time

        if split < best_split:
            text_color = best_split_color
        else:
            if delta <= 0:
                colormap = self.time_gain_cmap
                split_deviance_intensity = clip_at_unity(-delta/best_time_gain)
            else:
                colormap = self.time_loss_cmap
                split_deviance_intensity = clip_at_unity(delta/worst_time_loss)

            color = colormap( split_deviance_intensity+.5 )
            text_color = "rgb(" + ",".join(list(map(lambda x: str(int(255*x)), color[:-1]))) + ")"

        self.itemAtPosition(segment_index+1, 2).widget().setText( f'{delta:+.{timer_precision}f}')
        self._set_element_color(segment_index+1, 2, textcolor=text_color)

    def _erase_row(self, row):
        for col in range(1, self.cols):
            self.itemAtPosition(row, col).widget().setText(self.EMPTY_TIME)

    def _set_row_segment_name(self, segment_name: str, row):
        self.itemAtPosition(row, 0).widget().setText(segment_name)

    def _set_row_color(self, row, *args, **kwargs):
        for col in range(self.cols):
            self._set_element_color(row, col, *args, **kwargs)

    def _set_element_color(self, row, col, textcolor=None, background=None):
        _textcolor, _background = textcolor, background
        if textcolor is None:
            _textcolor = odd_row_text_color if row%2==1 else even_row_text_color
        if background is None:
            _background = odd_row_bg_color if row%2==1 else even_row_bg_color

        self.itemAtPosition(row, col).widget()\
                .setStyleSheet("QLabel { color : " + _textcolor + ";"
                               + "background-color: " + _background+"; }")
