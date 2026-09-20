import os

from PIL import Image

from app import compare_images, process_folders


def write_image(path, size=(32, 32), color=(200, 200, 200), patch=None):
    img = Image.new("RGB", size, color)
    if patch is not None:
        box, patch_color = patch
        img.paste(patch_color, box)
    img.save(path)


def read_gray(path):
    return Image.open(path).convert("L")


def test_strict_mode_writes_black_pixels_where_images_differ(tmp_path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    out = tmp_path / "diff.png"
    write_image(a)
    write_image(b, patch=((4, 4, 8, 8), (0, 0, 0)))

    compare_images(str(a), str(b), str(out))

    diff = read_gray(out)
    assert diff.size == (32, 32)
    pixels = diff.tobytes()
    assert pixels.count(0) == 16
    assert pixels.count(255) == 32 * 32 - 16
    assert diff.getpixel((5, 5)) == 0
    assert diff.getpixel((0, 0)) == 255


def test_identical_images_write_no_diff(tmp_path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    out = tmp_path / "diff.png"
    write_image(a)
    write_image(b)

    compare_images(str(a), str(b), str(out))

    assert not out.exists()


def test_size_mismatch_writes_no_diff(tmp_path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    out = tmp_path / "diff.png"
    write_image(a, size=(32, 32))
    write_image(b, size=(32, 16))

    compare_images(str(a), str(b), str(out))

    assert not out.exists()


def test_unreadable_image_writes_no_diff(tmp_path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    out = tmp_path / "diff.png"
    write_image(a)
    b.write_bytes(b"not an image")

    compare_images(str(a), str(b), str(out))

    assert not out.exists()


def test_relaxed_mode_ignores_differences_below_threshold(tmp_path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    out = tmp_path / "diff.png"
    write_image(a, color=(200, 200, 200))
    write_image(b, color=(200, 200, 200), patch=((4, 4, 12, 12), (190, 190, 190)))

    compare_images(str(a), str(b), str(out), threshold_value=30, mode="relaxed")
    assert not out.exists()

    compare_images(str(a), str(b), str(out), threshold_value=30, mode="strict")
    assert out.exists()


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
