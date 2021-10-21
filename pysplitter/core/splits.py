import warnings
import json
from copy import deepcopy


def is_correct_type(value, types):
    if not isinstance(value, types[0]):
        return False
    else:
        if len(types) > 1:
            for el in value:
                if not is_correct_type(el, [t for t in types[1:]]):
                    return False
    return True


class InvalidSplitError(Exception):
    def __init__(self, message):
        self.message = message


class Splits:
    information_types = {
                "segment_names": (list, str),
                "pb": (float),
                "pb_splits": (list, float),
                "best_splits": (list, float),
                "wr": (float),
                "name": (str)
            }
    information_names = set(information_types.keys())

    def __init__(self, name, segment_names, pb_splits=None, pb=None, best_splits=None, wr=None):
        self.name = name
        self.segment_names = segment_names
        self.pb_splits = pb_splits
        self.pb = pb
        self.best_splits = best_splits
        self.wr = wr

        self.new_records_set = False

    @staticmethod
    def load_from_file(file_name):
        try:
            with open(file_name, "r") as file_stream:
                file_content = json.load(file_stream)
        except json.decoder.JSONDecodeError:
            raise InvalidSplitError("Invalid json file. Empty file or incorrect formatting.")

        Splits.validate_split_file_content(file_content)

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

    @staticmethod
    def validate_split_file_content(file_content):
        if "segment_names" not in file_content.keys():
            raise InvalidSplitError("Invalid split file. The \"segment_names\" entry is missing.")

        if "name" not in file_content.keys():
            raise InvalidSplitError("Invalid split file. The \"name\" entry is missing.")

        for information, expected_types in Splits.information_types.items():
            if information in file_content.keys():
                if not is_correct_type(file_content[information], expected_types):
                    raise InvalidSplitError(f"Invalid split file. The entry \"{information}\" is not of type {expected_types}.")


        if file_content["split_names"]:
            raise InvalidSplitError("Invalid split file. The \"split_names\" entry is empty.")

        if file_content["name"] == "":
            raise InvalidSplitError("Invalid split file. The \"name\" entry is empty.")


    def write_to_file(self, file_name):
        available_information = {"name": self.name, "segment_names": self.segment_names}
        for information in ["pb", "pb_splits", "best_splits", "wr"]:
            if self.__dict__[information] is not None:
                available_information[information] = self.__dict__[information]

        with open(file_name, "w") as file_stream:
            json.dump(available_information, file_stream, indent=4)

    def are_new_records(self, _segment_names, _times, final_time=None):
        if self.best_splits is None or len(_times) > len(self.best_splits):
            return True

        for time, best_time in zip(_times, self.best_splits):
            if best_time is None or time < best_time:
                return True

        if final_time is not None:
            if self.pb_splits is None or final_time < self.pb:
                return True

        return False

    def update_times(self, _segment_names, _times, final_time=None):
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
                        if self.best_splits[i] is None or time < self.best_splits[i]:
                            self.best_splits[i] = time
                    else:
                        self.best_splits.append(time)

            if final_time is not None:
                if self.pb is None or final_time < self.pb:
                    self.pb = final_time
                    self.pb_splits = times.copy()

                if self.wr is not None and final_time < self.wr:
                    self.wr = final_time


            if previous_times == self.__dict__.values():
                self.new_records_set = True
