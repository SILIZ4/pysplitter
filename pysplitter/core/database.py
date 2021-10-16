import os
import warnings
import numpy as np


def add_entry_in_database(database_dir, segment_names, times):
    if os.path.isfile(database_dir):
        warnings.warn("Could not update database. Database directory is a file")
        return

    if not os.path.isdir(database_dir):
        os.makedirs(database_dir)

    for segment, time in zip(segment_names, times):
        file_name = os.path.join(database_dir, segment)
        if os.path.isfile(file_name):
            database_times = np.load(file_name)
        else:
            database_times = np.array([], dtype=np.double)

        database_times = np.append(database_times, time).astype(np.double)
        np.save(file_name, database_times)
