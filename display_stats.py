import argparse
import json
import os
import numpy as np
from scipy.stats import gaussian_kde
from matplotlib import pyplot as plt
from matplotlib import rcParams
from cycler import cycler

from pysplitter.config import database_directory


midblack ="#3d3d3d"
lightgray = "#ababab"

rcParams["axes.labelsize"] = 15
rcParams["axes.facecolor"] = "white"
rcParams["axes.grid"] = False
rcParams["axes.edgecolor"] = lightgray
rcParams['axes.spines.right'] = False
rcParams['axes.spines.top'] = False

rcParams["xtick.labelsize"] = 14
rcParams["ytick.labelsize"] = 14
rcParams["xtick.color"] = midblack
rcParams["ytick.color"] = midblack

rcParams["legend.edgecolor"] = "white"
rcParams["legend.fontsize"] = 13
rcParams["text.color"] = midblack


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


pdfs, labels = [], []
min, max = None, -1
final_times = False

for filename in os.listdir(database_directory):
    collected_data = np.load(os.path.join(database_directory, filename))
    if collected_data.shape[0] <= 1:
        continue

    if filename == "__final_time.npy":
        final_times = True

    pdfs.append(gaussian_kde(collected_data, bw_method=0.2))

    data_min, data_max = np.min(collected_data), np.max(collected_data)
    if min is None or min > data_min:
        min = data_min

    if max < data_max:
        max = data_max
    labels.append(filename[:-4])


if final_times:
    fig, axes = plt.subplots(2)
else:
    fig, axes = [plt.subplots(1)]

xvalues = np.linspace(min, max, 300)
if final_times:
    final_time_index = labels.index("__final_time")
    axes[1].plot(xvalues, pdfs[final_time_index].evaluate(xvalues), label="Final time")

    pdfs.pop(final_time_index)
    labels.pop(final_time_index)

for pdf, label in zip(pdfs, labels):
    axes[0].plot(xvalues, pdf.evaluate(xvalues), label=label)

for ax in axes:
    ax.set_xlabel("Time [s]")
    ax.legend()

plt.tight_layout()
plt.show()
