from pysplitter.core.splitter import Splitter, TimeInformation
import pytest
from time import sleep


segment_names = ["a", "b", "c", "d"]
splits = [0.02, 0.04, 0.07, 0.01]
timer_precision = 1e-3 # seconds


def compare_time(time1, time2, abs=timer_precision, **kwargs):
    assert pytest.approx(time1, abs=abs, **kwargs) == time2


def test_initial_flags():
    splitter = Splitter(segment_names)
    assert splitter.is_ready == True
    assert splitter.is_ongoing == False
    assert splitter.has_run_ended == False


def test_runstarted_flags():
    splitter = Splitter(segment_names)
    splitter.split()

    for split in splits:
        assert splitter.is_ready == False
        assert splitter.is_ongoing == True
        assert splitter.has_run_ended == False
        splitter.split()


def test_runended_flags():
    splitter = Splitter(segment_names)
    splitter.split()

    for split in splits:
        splitter.split()

    assert splitter.is_ready == False
    assert splitter.is_ongoing == False
    assert splitter.has_run_ended == True


def test_finishedrunreset_flags():
    splitter = Splitter(segment_names)
    splitter.split()

    for split in splits:
        splitter.split()
    splitter.reset()

    assert splitter.is_ready == True
    assert splitter.is_ongoing == False
    assert splitter.has_run_ended == False


def test_unfinishedrunreset_flags():
    splitter = Splitter(segment_names)
    splitter.split()
    splitter.split()
    splitter.reset()

    assert splitter.is_ready == True
    assert splitter.is_ongoing == False
    assert splitter.has_run_ended == False


def test_gettime_segment():
    splitter = Splitter(segment_names)
    splitter.split()

    for split in splits:
        sleep(split)
        compare_time(splitter.get_time(TimeInformation.CURRENT_SEGMENT), split)
        splitter.split()


def test_gettime_total():
    splitter = Splitter(segment_names)
    splitter.split()

    for split in splits:
        sleep(split)
        splitter.split()

    compare_time(splitter.get_time(TimeInformation.CURRENT_TOTAL_TIME), sum(splits))


def test_gettime_allsegments():
    splitter = Splitter(segment_names)
    splitter.split()

    for split in splits:
        sleep(split)
        splitter.split()
    segment_times, final_time = splitter.get_time(TimeInformation.ALL_SEGMENTS)

    compare_time(final_time, sum(splits))
    for expected_time, actual_time in zip(splits, segment_times.values()):
        compare_time(expected_time, actual_time)


def test_timesfixed_afterended():
    splitter = Splitter(segment_names)
    splitter.split()

    for split in splits:
        sleep(split)
        splitter.split()
    sleep(0.1)

    segment_times, final_time = splitter.get_time(TimeInformation.ALL_SEGMENTS)
    compare_time(final_time, sum(splits))
    for expected_time, actual_time in zip(splits, segment_times.values()):
        compare_time(expected_time, actual_time)
