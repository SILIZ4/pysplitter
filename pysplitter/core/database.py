import os
import json
import warnings


def _create_or_append_time_to_database(database, segment_name, time):
    if database.get(segment_name) is None:
        database[segment_name] = [time]
    else:
        database[segment_name].append(time)


def _append_times_to_database(database, segment_times, final_time=None):
    for segment, time in segment_times.items():
        _create_or_append_time_to_database(database, segment, time)

    if final_time is not None:
        _create_or_append_time_to_database(database, "__final_time", final_time)


def _load_database(file_name):
    if not os.path.isfile(file_name):
        return {}

    with open(file_name, "r") as file_stream:
        return json.load(file_stream)


def _write_database(database, file_name):
    with open(file_name, "w") as file_stream:
        database = json.dump(database, file_stream)


def update_database(database_dir, speedrun_name, segment_times, final_time=None):
    if not os.path.isdir(database_dir):
        warnings.warn(f'Could not update database. Database directory "{database_dir}" does not exist.')
        return

    file_name = os.path.join(database_dir, speedrun_name+".json")

    database = _load_database(file_name)
    _append_times_to_database(database, segment_times, final_time)
    _write_database(database, file_name)
