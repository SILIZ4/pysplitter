import argparse
import json
import os
import numpy as np
from matplotlib import pyplot as plt

from pysplitter.config import database_directory


parser = argparse.ArgumentParser()
parser.add_argument(metavar="split file name", dest="split_filename")
args = parser.parse_args()

if not os.path.isfile(args.split_filename):
    raise ValueError("Given file name does not exist.")
elif not args.split_filename.endswith(".json"):
    raise ValueError("Split file must be given in \".json\" format.")

with open(args.split_filename, "r") as file_stream:
    split_file_content = json.load(file_stream)
    if "name" not in split_file_content.keys():
        raise ValueError("Invalid split file. Entry \"name\" is missing.")

    database_directory = os.path.join("..", database_directory, split_file_content["name"])

if not os.path.isdir(database_directory):
    print("No data acquired for this run.")
    exit()


file_number = len(os.listdir(database_directory))
collected_data, labels = [], []

for filename in os.listdir(database_directory):
    collected_data.append( np.load(os.path.join(database_directory, filename)) )
    labels.append(filename.rstrip(".npy"))

plt.hist(collected_data, label=labels)
plt.xlabel("Time [s]")
plt.legend()
plt.tight_layout()
plt.show()
