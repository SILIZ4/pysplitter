import warnings
import json
from copy import deepcopy


class Splits:
    information_names = {"segment_names", "pb", "best_splits", "wr"}

    def __init__(self, segment_names, pb=None, best_splits=None, wr=None):
        self.segment_names = segment_names
        self.pb = pb
        self.best_splits = best_splits
        self.wr = wr

        self.new_records_set = False

    @staticmethod
    def load_from_file(file_name):
        with open(file_name, "r") as file_stream:
            file_content = json.load(file_stream)

        if "segment_names" not in file_content.keys():
            return

        split_informations = {}
        unused_informations = []
        for key, value in file_content.items():
            if key in Splits.information_names:
                split_informations[key]=value
            else:
                unused_informations.append(key)

        if unused_informations:
            warnings.warn(f"Entries \"{', '.join(unused_informations)}\" in split file \"{file_name}\" were ignored.")

        return Splits(**split_informations)

    def write_to_file(self, file_name):
        available_information = {"segment_names": self.segment_names}
        for information in ["pb", "best_splits", "wr"]:
            if self.__dict__[information] is not None:
                available_information[information] = self.__dict__[information]

        with open(file_name, "w") as file_stream:
            json.dump(available_information, file_stream)

    def are_new_records(self, _segment_names, _times):
        if self.best_splits is None or len(_times) > len(self.best_splits):
            return True

        for time, best_time in zip(_times, self.best_splits):
            if time < best_time:
                return True

        if len(_times) == len(_segment_names):
            if self.pb is None or sum(_times) < sum(self.pb):
                return True

        return False

    def update_times(self, _segment_names, _times):
        segment_names = _segment_names.copy()
        times = _times.copy()
        previous_times = deepcopy(self.__dict__).values()

        if segment_names != self.segment_names:
            warnings.warn("Times not updated. Segment names don't match.")
        else:
            if self.best_splits is None:
                self.best_splits = times.copy()
            else:
                for i, time in enumerate(times):
                    if i < len(self.best_splits):
                        if time < self.best_splits[i]:
                            self.best_splits[i] = time
                    else:
                        self.best_splits.append(time)

            if len(times) == len(segment_names):
                final_time = sum(times)

                if self.pb is None or final_time < sum(self.pb):
                    self.pb = times.copy()

                if self.wr is not None and final_time < self.wr:
                    self.wr = final_time


            if previous_times == self.__dict__.values():
                self.new_records_set = True
