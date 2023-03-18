import sys, pathlib

abolute_path_to_file = pathlib.Path(__file__).parent.resolve()
sys.path.append(f"{abolute_path_to_file}/pysplitter/ui")
from main import launch_main_window
launch_main_window(sys.argv)
