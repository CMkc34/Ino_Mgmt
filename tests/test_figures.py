"""Tests for pipelines/figures.py."""

import matplotlib.pyplot as plt

from pipelines.figures import save_figure


def simple_chart():
    figure, axes = plt.subplots()
    axes.plot([2023, 2024, 2025], [10, 20, 40])
    axes.set_title("Example")
    return figure


def test_saving_the_same_chart_twice_gives_identical_files(tmp_path):
    first = save_figure(simple_chart(), "example", tmp_path).read_bytes()
    second = save_figure(simple_chart(), "example", tmp_path).read_bytes()
    assert first == second
