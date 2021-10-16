import warnings
import json


class Splits:

    def __init__(self, segment_names, pb=None, best_splits=None, wr=None):
        self.segment_names = segment_names
        self.pb = pb
        self.best_splits = best_splits
        self.wr = wr

    @staticmethod
    def load_from_file(file_name):
        with open(file_name, "r") as file_stream:
            file_content = json.load(file_stream)

        return Splits(**file_content)

    def write_to_file(self, file_name):
        available_information = {"segment_names": self.segment_names}
        for information in ["pb", "best_splits", "wr"]:
            if self.__dict__[information] is not None:
                available_information[information] = self.__dict__[information]

        with open(file_name, "w") as file_stream:
            json.dump(available_information, file_stream)

    def get_new_best_splits(self, _segment_names, _times):

        if self.best_splits is None:
            new_best_segments = _segment_names.copy()
        else:
            new_best_segments = []
            for i, (current_best, time) in enumerate(zip(self.best_splits, _times)):
                if time < current_best:
                    new_best_segments.append(_segment_names[i])

        return new_best_segments

    def update_times(self, _segment_names, _times):
        segment_names = _segment_names.copy()
        times = _times.copy()


        if segment_names != self.segment_names:
            warnings.warn("Times not updated. Segment names don't match.")
        else:
            if self.best_splits is None:
                self.best_splits = times.copy()
            else:
                for i, (time, best_time) in enumerate(zip(times, self.best_splits)):
                    if time < best_time:
                        self.best_splits[i] = time

            if len(times) == len(segment_names):
                final_time = sum(times)

                if self.pb is None or final_time < sum(self.pb):
                    self.pb = times.copy()

                if self.wr is not None and final_time < self.wr:
                    self.wr = final_time
