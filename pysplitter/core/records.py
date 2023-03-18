import warnings
import json


def is_correct_type(value, types):
    if not isinstance(value, types[0]):
        return False
    else:
        if len(types) > 1:
            for el in value:
                if not is_correct_type(el, [t for t in types[1:]]):
                    return False
    return True


class InvalidRecordsError(Exception):
    def __init__(self, message):
        self.message = message


class SpeedrunRecords:
    information_types = {
                "segment_names": [list, str],
                "pb": [float],
                "pb_splits": [list, float],
                "best_splits": [list, float],
                "wr": [float],
                "name": [str],
                "run_count": [int],
            }
    information_names = set(information_types.keys())

    def __init__(self, name, segment_names, file_name=None, pb_splits=None, pb=None, best_splits=None, wr=None, run_count=None):
        self.name = name
        self.segment_names = segment_names
        self.pb_splits = pb_splits
        self.pb = pb
        self.best_splits = best_splits
        self.wr = wr
        self.run_count = run_count if run_count is not None else 0
        self.file_name = file_name

        self.records_file_up_to_date = True

        if self.best_splits is None or len(self.best_splits) != len(self.segment_names):
            self.best_splits = [None for i in range(len(self.segment_names))]
        if self.pb_splits is None or len(self.pb_splits) != len(self.segment_names):
            self.pb_splits = [None for i in range(len(self.segment_names))]

    @staticmethod
    def load_from_file(file_name):
        try:
            with open(file_name, "r") as file_stream:
                file_content = json.load(file_stream)
        except json.decoder.JSONDecodeError:
            raise InvalidRecordsError("Invalid json file. Empty file or incorrect formatting.")

        SpeedrunRecords.validate_records_file_content(file_content)

        speedrun_information = {}
        unused_informations = []
        for key, value in file_content.items():
            if key in SpeedrunRecords.information_names:
                speedrun_information[key]=value
            else:
                unused_informations.append(key)

        if unused_informations:
            warnings.warn(f"Entries \"{', '.join(unused_informations)}\" in records file \"{file_name}\" were ignored.")

        return SpeedrunRecords(file_name=file_name, **speedrun_information)

    @staticmethod
    def validate_records_file_content(file_content):
        if "segment_names" not in file_content.keys():
            raise InvalidRecordsError("Invalid records file. The \"segment_names\" entry is missing.")

        if "name" not in file_content.keys():
            raise InvalidRecordsError("Invalid records file. The \"name\" entry is missing.")

        for information, expected_types in SpeedrunRecords.information_types.items():
            if information in file_content.keys():
                if not is_correct_type(file_content[information], expected_types):
                    raise InvalidRecordsError(f"Invalid records file. The entry \"{information}\" is not of type {expected_types}.")

        if file_content["segment_names"] == []:
            raise InvalidRecordsError("Invalid records file. The \"segment_names\" entry is empty.")

        if file_content["name"] == "":
            raise InvalidRecordsError("Invalid records file. The \"name\" entry is empty.")

    def write_to_file(self, file_name):
        available_information = {"name": self.name, "segment_names": self.segment_names}
        for information in ["pb", "pb_splits", "best_splits", "wr", "run_count"]:
            if self.__dict__[information] is not None:
                available_information[information] = self.__dict__[information]

        with open(file_name, "w") as file_stream:
            json.dump(available_information, file_stream, indent=4)
        self.records_file_up_to_date = True

    def has_new_records(self, segment_times, final_time):
        new_best_splits = len(self._find_new_best_splits(segment_times.values()))>0
        new_pb = self.pb is None or final_time < self.pb
        return new_pb or new_best_splits

    def _find_new_best_splits(self, splits):
        def is_better_time(current_time, new_time):
            if new_time is None:
                return False
            if current_time is None:
                return True
            return new_time < current_time

        return [index for index, (current_time, new_time) in enumerate(zip(self.best_splits, splits))
                    if is_better_time(current_time, new_time)]

    def update_times(self, segment_times, final_time=None):
        if list(segment_times.keys()) != self.segment_names:
            warnings.warn("Times not updated. Segment names don't match.")
            return

        self.records_file_up_to_date = self.records_file_up_to_date or self.has_new_records(segment_times, final_time)

        splits = list(segment_times.values())
        self._update_best_splits(splits)
        self._update_pb(splits, final_time)
        self.run_count += 1

    def _update_best_splits(self, splits):
        for better_split in self._find_new_best_splits(splits):
            self.best_splits[better_split] = splits[better_split]

    def _update_pb(self, splits, final_time) -> bool:
        if final_time is None:
            return False

        if self.pb is None or final_time < self.pb:
            self.pb = final_time
            self.pb_splits = splits.copy()
            return True
        return False
