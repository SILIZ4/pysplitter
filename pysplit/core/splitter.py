from time import perf_counter_ns


class Splitter:
    def __init__(self, segment_names: list[str]):
        assert(len(segment_names)>0)
        self.segment_names = segment_names
        self.final_time = None
        self.segment_times = []

    def set_segments(self, segment_names: list[str]):
        assert(len(segment_names)>0)
        assert(self.is_run_finished())
        self.segment_names = segment_names


    def start(self):
        self.final_time = -1
        self.segment_times = [perf_counter_ns()]

    def split(self):
        self.segment_times.append(perf_counter_ns())
        if len(self.segment_times) > len(self.segment_names):
            self._end()

    def _end(self):
        self.final_time = perf_counter_ns() - self.segment_times[-1]

    def is_run_finished(self)->bool:
        return self.final_time != -1


    def convert_time(self, time: int)->float:
        return time/1e9

    def get_time(self, type: str):
        assert(len(self.segment_times)>0)

        if type == "segment":
            return self.convert_time(perf_counter_ns() - self.segment_times[-1])

        elif type == "previous":
            return self.convert_time(self.segment_times[-1] - self.segment_times[-2])

        elif type == "total":
            return self.convert_time(perf_counter_ns() - self.segment_times[0])

        elif type == "all":
            segment_times = {key: self.convert_time(end-start) for key, start, end in zip(self.segment_names, self.segment_times, self.segment_times[1:])}
            if self.is_run_finished():
                segment_times["final"] = self.final_time

            return segment_times
