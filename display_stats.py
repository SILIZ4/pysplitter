import argparse
from copy import deepcopy
import json
import numpy as np
import os, time

from matplotlib import pyplot as plt
from matplotlib import rcParams, ticker
from scipy.stats import gaussian_kde
import pandas as pd

from pysplitter.config import database_directory


midblack ="#3d3d3d"
lightgray = "#ababab"

rcParams["axes.labelsize"] = 15
rcParams["axes.facecolor"] = "white"
rcParams["axes.grid"] = False
rcParams["axes.edgecolor"] = lightgray
rcParams['axes.spines.left'] = False
rcParams['axes.spines.right'] = False
rcParams['axes.spines.top'] = False

rcParams["xtick.labelsize"] = 9
rcParams["ytick.labelsize"] = 9
rcParams["xtick.color"] = midblack
rcParams["ytick.color"] = midblack

rcParams["legend.edgecolor"] = "white"
rcParams["legend.fontsize"] = 10
rcParams["text.color"] = midblack


valid_sorting = ["temporal", "mean", "name"]
parser = argparse.ArgumentParser()
parser.add_argument(metavar="split file name", dest="split_filename")
parser.add_argument("-o", metavar="oredering type", dest="sorting", default="mean",
                    help="One of "+str(valid_sorting))
parser.add_argument("-s", metavar="segments", nargs="+",
                    help="One of "+str(valid_sorting))
args = parser.parse_args()

if not os.path.isfile(args.split_filename):
    raise ValueError("Given file name does not exist.")
elif not args.split_filename.endswith(".json"):
    raise ValueError("Split file must be given in \".json\" format.")

with open(args.split_filename, "r") as file_stream:
    split_file_content = json.load(file_stream)
    if "name" not in split_file_content.keys():
        raise ValueError("Invalid split file. Entry \"name\" is missing.")

    segment_names = args.s if args.s else split_file_content["segment_names"]

    database_directory = os.path.join("..", database_directory, split_file_content["name"])

if not os.path.isdir(database_directory):
    print("No data acquired for this run.")
    exit()

if args.sorting not in valid_sorting:
    raise ValueError(f'Sorting "{args.sorting}" invalid.')


segments_data = []
final_times_set = False

# Collect and sort statistics

segment_names.append("__final_time")
found_segments = []
for segment_name in segment_names:
    file_path = os.path.join(database_directory, segment_name+".npy")
    if not os.path.isfile(file_path):
        print(f'Skipping segment "{segment_name}". Data not found.')
        continue

    collected_data = np.load(file_path)
    if collected_data.shape[0] <= 1:
        continue

    if segment_name == "__final_time":
        final_times_set = True

    segment = {}
    segment["min"] = np.min(collected_data)
    segment["max"] = np.max(collected_data)
    segment["mean"] = np.mean(collected_data)
    segment["std"] = np.std(collected_data)
    segment["rel std"] = segment["std"]/segment["mean"]
    segment["pdf"] = gaussian_kde(collected_data, bw_method=0.5)

    segments_data.append(segment)
    found_segments.append(segment_name)

segments_data = pd.DataFrame(segments_data, index=found_segments)

if args.sorting == "mean":
    segments_data.sort_values("mean", ascending=False, inplace=True)
elif args.sorting == "name":
    segments_data.sort_index(ascending=False, inplace=True)


# Print out largest relative variance
print("Most consistent:")
segments_no_final = segments_data.drop("__final_time")
print(segments_no_final.sort_values("rel std", ascending=True).head(5)[["std"]])

print("Most inconsistent:")
print(segments_no_final.sort_values("rel std", ascending=False).head(5)[["std"]])


# Plot

group_size = 5
group_number = int(np.ceil((segments_data.shape[0]-final_times_set)/group_size) + final_times_set)

fig, axes = plt.subplots(
                group_number,
                figsize=(6, (2*group_number)+1)
            )

if group_number == 1:
    axes = [axes]

colors = [
        "#50514f",
        "#f25f5c",
        "#FDBF61",
        "#247ba0",
        "#70c1b3",
    ]

def plot_distribution(ax, row, label=None, color=colors[0]):
    min, max = row["min"], row["max"]
    xvalues = min if max==min else np.linspace(min, max, 300)
    yvalues = row["pdf"].evaluate(xvalues)

    ax.plot(xvalues, yvalues, label=label, color=color)
    ax.fill_between(xvalues, yvalues, color=color, alpha=0.3)


group_index = 0
current_group_index = 0
for (index, row), segment_name in zip(segments_data.iterrows(), segments_data.index):
    if segment_name == "__final_time":
        plot_distribution(axes[-1], row, "Final time", colors[0])
        continue

    if current_group_index == group_size:
        current_group_index = 0
        group_index += 1

    plot_distribution(axes[group_index], row, segment_name, colors[current_group_index])

    current_group_index += 1

def time_formatter(seconds, _):
    formatted_string = ""
    element_number = 0

    if seconds>=3600:
        formatted_string += f"{int(seconds//3600)}h "
        seconds = seconds % 3600
        element_number += 1

    if seconds>=60 or element_number > 1:
        formatted_string += f"{int(seconds//60)}m "
        seconds = seconds % 60
        element_number += 1

    if not element_number == 2 and (seconds >=0 or element_number<2):
        formatted_string += f"{int(seconds)}s "
        seconds = seconds % 1
        element_number += 1

    if not element_number == 2 and (seconds >=0 or element_number<2):
        formatted_string += f"{int(seconds*1000)}ms "

    return formatted_string

for ax in axes:
    ax.set_yticks([])
    ax.xaxis.set_major_formatter(time_formatter)
    ax.legend()

axes[-1].set_xlabel("Time [s]")

fig.tight_layout()
plt.show()
