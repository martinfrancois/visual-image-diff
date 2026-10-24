# visual-image-diff

Compare two folders of images and write a black-on-white diff image for every pair that differs.

## What it does

The tool looks for files with the same name in both folders and compares each
pair pixel by pixel. Where the two images differ it writes `diff_<name>` into
the output folder: a grayscale image with a white background and black pixels
at every position that changed. Pairs with no difference produce no file.

Two modes:

- `strict` (default) marks every pixel whose value differs at all.
- `relaxed` marks only pixels whose grayscale difference is at or above
  `--threshold` (default 30), then removes isolated marks with a 3x3
  morphological opening.

## Requirements

Python 3.10 or newer. OpenCV is installed from the headless wheel, so no
display libraries are needed.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -e .
```

This adds the `visual-image-diff` command to the virtualenv. Without
installing, `python3 app.py` takes the same arguments.

## Usage

```bash
visual-image-diff /path/to/reference /path/to/new /path/to/diff-output
visual-image-diff /path/to/reference /path/to/new /path/to/diff-output --mode relaxed --threshold 30
```

The output folder is created if it does not exist. Files are matched by name
only, in the top level of each folder. Only files with the extensions `.png`,
`.jpg`, `.jpeg`, `.bmp`, `.gif` and `.tiff` are considered.

## Example

`examples/` holds generated images. `card.png` has a red circle that moved
eight pixels to the right in `new`. `unchanged.png` is the same in both
folders. `banner.png` is 120x40 in `reference` and 100x40 in `new`.
`only-in-reference.png` has no counterpart in `new`.

```bash
visual-image-diff examples/reference examples/new output/diff
```

Output, in varying order:

```
Skipping examples/reference/banner.png and examples/new/banner.png due to different dimensions.
No differences found in unchanged.png; skipping diff image.
Diff saved to output/diff/diff_card.png
```

`output/diff/diff_card.png` is a 96x64 image with 332 black pixels where the
circle was and where it is now, and white everywhere else.
`only-in-reference.png` produces no message.

To run the tests, install the test dependencies and run pytest:

```bash
python -m pip install -r requirements-test.txt
python -m pytest
```

The tests generate small images with Pillow in a temporary folder and check
the diff output.

## Behavior for missing files and size mismatches

- A file present in only one folder is ignored without a message.
- A pair with different pixel dimensions prints
  `Skipping <path1> and <path2> due to different dimensions.` and writes
  nothing. The images are not resized.
- A file OpenCV cannot decode prints `Error loading image: <path>` and the
  pair is skipped. This applies to `.gif` files: the extension is accepted
  but `cv2.imread` cannot read GIF, so every GIF pair reports this error.
- If no file name occurs in both folders, the tool prints
  `No common image files found between folders.` and exits with status 0.
- If an input folder does not exist, the tool creates the output folder and
  then fails with a `FileNotFoundError` traceback.

## Limitations

- Images are compared at identical size and position. A shift of one pixel
  marks the whole shifted area as different.
- Color images are diffed per channel, then the difference is converted to
  grayscale before thresholding. A change of one level in the red or blue
  channel alone rounds to zero gray and is missed even in strict mode.
- Alpha channels are ignored: images are loaded as three-channel BGR.
- Subfolders are not searched.

## License

MIT, see `LICENSE`.
