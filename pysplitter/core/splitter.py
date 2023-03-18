from typing import OrderedDict
import warnings
from time import perf_counter_ns
from enum import Enum


class TimeInformation(Enum):
    CURRENT_SEGMENT = 0
    PREVIOUS_SEGMENT = 1
    CURRENT_TOTAL_TIME = 2
    ALL_SEGMENTS = 3


class RunState(Enum):
    READY = 0
    ONGOING = 1
    ENDED = 2


class Splitter:
    def __init__(self, segment_names: list[str]):
        assert(len(segment_names)>0)
        self._segment_names = segment_names
        self._segment_times = []
        self._final_time = None
        self._run_state = RunState.READY

    def split(self):
        if self.is_ready:
            self._start()

        elif self.is_ongoing:
            self._add_split_time()
            if len(self._segment_times) == len(self._segment_names)+1:
                self._end()

    def reset(self):
        self._segment_times = []
        self._final_time = None
        self._run_state = RunState.READY

    def undo_split(self):
        if len(self._segment_times)>1:
            self._segment_times.pop()

    def get_current_segment_index(self)->int:
        return len(self._segment_times)-1

    def get_time(self, time_information: TimeInformation):
        if self._segment_times == []:
            return None

        current_time = self._segment_times[-1] if self.has_run_ended else perf_counter_ns()

        match time_information:
            case TimeInformation.CURRENT_SEGMENT:
                return self._convert_time(current_time - self._segment_times[-1])
            case TimeInformation.CURRENT_TOTAL_TIME:
                return self._convert_time(current_time - self._segment_times[0])
            case TimeInformation.PREVIOUS_SEGMENT:
                return self._convert_time(self._segment_times[-1] - self._segment_times[-2])
            case TimeInformation.ALL_SEGMENTS:
                segment_times = OrderedDict( (name, None) for name in self._segment_names )
                for name, start, end in zip(self._segment_names, self._segment_times, self._segment_times[1:]):
                    segment_times[name] = self._convert_time(end-start)

                return segment_times, self._final_time

    @property
    def is_ready(self) -> bool:
        return self._run_state == RunState.READY

    @property
    def is_ongoing(self) -> bool:
        return self._run_state == RunState.ONGOING

    @property
    def has_run_ended(self) -> bool:
        return self._run_state == RunState.ENDED

    def _start(self):
        if len(self._segment_names)==0:
            warnings.warn("Could not start run: no segments.")
            return
        self._run_state = RunState.ONGOING
        self._add_split_time()

    def _end(self):
        self._final_time = self._convert_time(self._segment_times[-1] - self._segment_times[0])
        self._run_state = RunState.ENDED

    def _convert_time(self, time: int)->float:
        return time/1e9

    def _add_split_time(self):
        self._segment_times.append(perf_counter_ns())
