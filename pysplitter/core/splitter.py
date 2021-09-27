from time import perf_counter_ns


class Splitter:
    def __init__(self, segment_names: list[str]):
        assert(len(segment_names)>0)
        self.segment_names = segment_names
        self.final_time = None
        self.segment_times = []

    def set_segments(self, segment_names: list[str]):
        assert(len(segment_names)>0)
        assert(not self.is_run_started())
        self.segment_names = segment_names


    def start(self):
        self.final_time = -1
        self.segment_times = [perf_counter_ns()]

    def split(self):
        if not self.is_run_started():
            self.start()

        else:
            self.segment_times.append(perf_counter_ns())
            if self.is_run_finished():
                self._end()

    def reset(self):
        self.final_time = -2
        self.segment_times = []

    def undo_split(self):
        if len(self.segment_times)>1:
            self.segment_times.pop()

    def _end(self):
        self.final_time = self.convert_time(self.segment_times[-1] - self.segment_times[0])

    def is_run_finished(self)->bool:
        return len(self.segment_times) > len(self.segment_names)

    def is_run_started(self)->bool:
        return len(self.segment_times) > 0 and self.final_time == -1

    def convert_time(self, time: int)->float:
        return time/1e9

    def get_current_segment(self)->int:
        return len(self.segment_times)-1

    def get_time(self, type: str):
        assert(len(self.segment_times)>0)
        current_time = self.segment_times[-1] if self.is_run_finished() else perf_counter_ns()

        if type == "segment":
            return self.convert_time(current_time - self.segment_times[-1])

        elif type == "total":
            return self.convert_time(current_time - self.segment_times[0])

        elif type == "previous":
            return self.convert_time(self.segment_times[-1] - self.segment_times[-2])

        elif type == "all":
            segment_times = [self.convert_time(end-start) for start, end in zip(self.segment_times, self.segment_times[1:])]
            segment_names = self.segment_names.copy()

            if self.is_run_finished():
                segment_names.append("final")
                segment_times.append(self.final_time)

            return (segment_names, segment_times)

        else:
            raise ValueError(f"Unknown time type \"{type}\"")
