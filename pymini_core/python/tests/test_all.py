import pytest
import pymini_core


def test_sum_as_string():
    assert pymini_core.sum_as_string(1, 1) == "2"
