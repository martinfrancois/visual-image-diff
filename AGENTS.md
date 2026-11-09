# AGENTS

visual-image-diff compares two folders of images and writes a black-on-white diff image for every pair that differs. README.md has the usage.

## Checks

Run these before committing, with Python 3.10 or newer. CI runs the same steps on Python 3.12 and the tests on 3.10 as well (`.github/workflows/ci.yml`):

```bash
python3 -m pip install -r requirements-test.txt
python3 app.py --help
python3 -m pytest
python3 app.py examples/reference examples/new output/diff
```

The last command should write only `output/diff/diff_card.png`.

## Contributing for Someone Else

martinfrancois's rule for outside contributions, and for any agent working for an outside contributor: contributors shouldn't spend time on pull requests that collide with someone else's work or that he wouldn't accept. So a contribution takes one of three paths (see "Three ways to contribute" in CONTRIBUTING.md):

- Small fix (bug fix, typo, docs improvement or similar): open a pull request directly, no issue needed. If an issue for it exists, claim it first as below.
- Existing issue: check its assignees and linked pull requests, post `/take` on the issue, and start only once the assignment comes back. Never open a pull request for an issue that isn't assigned to the contributor you work for, and don't start on one that someone else holds or that an open pull request already addresses.
- New feature: open a thread in the Ideas category of GitHub Discussions. Wait until martinfrancois approves it and opens an issue, then claim that issue with `/take`. Never open a feature pull request without an approved issue assigned to your contributor.
