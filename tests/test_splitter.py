import pysplit.core.splitter
import pytest
from time import sleep


segment_names = ["a", "b", "c", "d"]
segment_times = [0.2, 0.4, 0.4, 0.3]
timer_precision = 5e-3


def test_gettime_segment_correctTime():
    splitter = pysplit.core.splitter.Splitter(segment_names)
    splitter.start()

    sleep(.3)
    assert pytest.approx(splitter.get_time("segment"), timer_precision) == .3
    splitter.split()

    sleep(.5)
    assert pytest.approx(splitter.get_time("segment"), timer_precision) == .5


def test_gettime_total_correctTime():
    splitter = pysplit.core.splitter.Splitter(segment_names)
    splitter.start()

    for i in range(3):
        sleep(0.33)
        splitter.split()

    assert pytest.approx(splitter.get_time("total"), timer_precision) == .99


def test_gettime_all_correctTimes():
    splitter = pysplit.core.splitter.Splitter(segment_names)
    splitter.start()

    expected_times = {}
    for segment_name, split_time in zip(segment_names, segment_times):
        expected_times[segment_name] = split_time
        sleep(split_time)
        splitter.split()

    expected_times["final"] = sum(segment_times)
    actual_times = splitter.get_time("all")
    print(actual_times)

    for segment_name, split_time in zip(segment_names, segment_times):
        assert pytest.approx(actual_times[segment_name], timer_precision) == split_time
