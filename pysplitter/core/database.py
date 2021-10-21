import os
import warnings
import numpy as np

def _add_value_in_file(file_name, value):
    if os.path.isfile(file_name+".npy"):
        database_times = np.load(file_name+".npy")
    else:
        database_times = np.array([], dtype=np.double)

    database_times = np.append(database_times, value)
    np.save(file_name, database_times.astype(np.double))


def add_entry_in_database(database_dir, segment_names, times, final_time=None):
    if os.path.isfile(database_dir):
        warnings.warn("Could not update database. Database directory is a file")
        return

    if not os.path.isdir(database_dir):
        os.makedirs(database_dir)

    for segment, time in zip(segment_names, times):
        file_name = os.path.join(database_dir, segment)
        _add_value_in_file(file_name, time)

    if final_time is not None:
        file_name = os.path.join(database_dir, "__final_time")
        _add_value_in_file(file_name, final_time)
