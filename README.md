# visual-image-diff

Install dependencies with Python 3.10 or newer:

```bash
python3 -m pip install -r requirements.txt
```

Run:

```bash
python3 app.py images-reference images-new images-diff
```

Use `--mode relaxed --threshold 30` to ignore small differences. `--help` lists the options. The tool compares matching filenames in the top level of each folder and writes black-on-white diff images. Missing pairs and unequal dimensions are skipped. Alpha channels and tiny red or blue changes are not detected. OpenCV uses its headless package, so no display libraries are needed.

The synthetic example is `python3 app.py examples/reference examples/new output/diff`. It writes `diff_card.png`. Install `requirements-test.txt` and run `python3 -m pytest` to test.

MIT, see [LICENSE](LICENSE).
