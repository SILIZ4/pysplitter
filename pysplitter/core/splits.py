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

    def update_times(self, _segment_names, _times):
        segment_names = _segment_names.copy()
        times = _times.copy()

        if segment_names[-1] == "final":
            final_time = times.pop()
            segment_names.pop()
        else:
            final_time = None


        if segment_names != self.segment_names:
            print("Times not updated")
        else:
            if self.best_splits is None:
                self.best_splits = times
            else:
                for i, (time, best_time) in enumerate(zip(times, self.best_splits)):
                    if time < best_time:
                        self.best_splits[i] = time

            if final_time is not None:
                if self.pb is None or final_time < self.pb:
                    self.pb = final_time

                if self.wr is not None and final_time < self.wr:
                    self.wr = final_time
