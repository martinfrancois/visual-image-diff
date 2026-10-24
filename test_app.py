import os
from collections import namedtuple
from pathlib import Path

import pytest
from PIL import Image

from app import compare_images, process_folders

EXAMPLES = Path(__file__).parent / "examples"
THRESHOLD = 30
BACKGROUND = (200, 200, 200)

Pair = namedtuple("Pair", "a b out")


@pytest.fixture
def pair(tmp_path):
    return Pair(tmp_path / "a.png", tmp_path / "b.png", tmp_path / "diff.png")


def write_image(path, size=(32, 32), color=BACKGROUND, patch=None):
    img = Image.new("RGB", size, color)
    if patch is not None:
        box, patch_color = patch
        img.paste(patch_color, box)
    img.save(path)


def read_gray(path):
    return Image.open(path).convert("L")


def compare(pair, **kwargs):
    compare_images(str(pair.a), str(pair.b), str(pair.out), **kwargs)


def test_strict_mode_writes_black_pixels_where_images_differ(pair):
    write_image(pair.a)
    write_image(pair.b, patch=((4, 4, 8, 8), (0, 0, 0)))

    compare(pair)

    diff = read_gray(pair.out)
    assert diff.size == (32, 32)
    pixels = diff.tobytes()
    assert pixels.count(0) == 16
    assert pixels.count(255) == 32 * 32 - 16
    assert diff.getpixel((5, 5)) == 0
    assert diff.getpixel((0, 0)) == 255


def test_identical_images_write_no_diff(pair):
    write_image(pair.a)
    write_image(pair.b)

    compare(pair)

    assert not pair.out.exists()


def test_size_mismatch_writes_no_diff(pair):
    write_image(pair.a, size=(32, 32))
    write_image(pair.b, size=(32, 16))

    compare(pair)

    assert not pair.out.exists()


def test_unreadable_image_writes_no_diff(pair):
    write_image(pair.a)
    pair.b.write_bytes(b"not an image")

    compare(pair)

    assert not pair.out.exists()


def test_relaxed_mode_ignores_differences_below_threshold(pair):
    write_image(pair.a)
    write_image(pair.b, patch=((4, 4, 12, 12), (190, 190, 190)))

    compare(pair, threshold_value=THRESHOLD, mode="relaxed")
    assert not pair.out.exists()

    compare(pair, threshold_value=THRESHOLD, mode="strict")
    assert pair.out.exists()


@pytest.mark.parametrize("difference, marked", [(THRESHOLD, False), (THRESHOLD + 1, True)])
def test_relaxed_mode_marks_only_differences_above_threshold(pair, difference, marked):
    # An equal change in every channel gives the same grayscale difference.
    level = BACKGROUND[0] - difference
    write_image(pair.a)
    write_image(pair.b, patch=((4, 4, 12, 12), (level, level, level)))

    compare(pair, threshold_value=THRESHOLD, mode="relaxed")

    assert pair.out.exists() == marked


def test_process_folders_only_compares_files_present_in_both(tmp_path):
    ref = tmp_path / "reference"
    new = tmp_path / "new"
    out = tmp_path / "out"
    ref.mkdir()
    new.mkdir()
    write_image(ref / "changed.png")
    write_image(new / "changed.png", patch=((0, 0, 2, 2), (0, 0, 0)))
    write_image(ref / "same.png")
    write_image(new / "same.png")
    write_image(ref / "only-in-reference.png")
    (ref / "notes.txt").write_text("not an image")
    (new / "notes.txt").write_text("not an image")

    process_folders(str(ref), str(new), str(out))

    assert sorted(os.listdir(out)) == ["diff_changed.png"]


def test_readme_example_writes_one_diff_with_332_black_pixels(tmp_path):
    out = tmp_path / "diff"

    process_folders(str(EXAMPLES / "reference"), str(EXAMPLES / "new"), str(out))

    assert os.listdir(out) == ["diff_card.png"]
    diff = read_gray(out / "diff_card.png")
    assert diff.size == (96, 64)
    assert diff.tobytes().count(0) == 332
