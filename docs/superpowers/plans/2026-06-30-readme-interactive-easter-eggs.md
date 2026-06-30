# README Interactive Easter Eggs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a "random commit" badge and a hidden click counter to the `morphqdd/morphqdd` profile README; the header gif swaps based on the click count's divisibility by 5/3/2.

**Architecture:** Two static GitHub Pages (`docs/roulette.html`, `docs/secret.html`) handle the two click targets client-side. A shared public counter (Abacus API) tracks clicks. A scheduled GitHub Action reads the counter, computes which gif tier applies via a small pure Python function, and rewrites the README's header `<img>` tag when it changes.

**Tech Stack:** Static HTML/JS (no build step), Python 3 (stdlib only, for the Action's logic + tests), GitHub Actions, GitHub Pages.

## Global Constraints

- No paid services. No new secrets — the Action uses the default `GITHUB_TOKEN` only, same as `.github/workflows/snake.yml`.
- Counter: Abacus API, namespace `morphqdd-readme`, key `secret-clicks`. Hit (increment+read): `GET https://abacus.jasoncameron.dev/hit/morphqdd-readme/secret-clicks`. Read-only: `GET https://abacus.jasoncameron.dev/get/morphqdd-readme/secret-clicks`.
- Gif tier priority when count matches multiple divisors: 5 wins over 3 wins over 2. `count == 0` or matching none → default.
- `gif-rules.json` lives at repo root; all four URLs start as the existing header gif (`https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif`) as a working placeholder the owner swaps later.
- Repo default branch is `main`. Pages will serve from `main` / `docs`.

---

## File Structure

- Create: `gif-rules.json` — per-tier gif URL config.
- Create: `scripts/select_gif.py` — pure function mapping (count, rules) → URL, plus CLI entrypoint.
- Create: `scripts/test_select_gif.py` — unit tests for the above.
- Create: `scripts/update_readme_gif.py` — rewrites README's header `<img>` `src` in place, plus CLI entrypoint.
- Create: `scripts/test_update_readme_gif.py` — unit tests for the above.
- Create: `docs/secret.html` — click target, increments counter, shows count.
- Create: `docs/roulette.html` — click target, redirects to a random commit.
- Modify: `README.md` — add roulette badge (after the Telegram badge block) and a small secret link (at the end of the file).
- Create: `.github/workflows/update-header-gif.yml` — scheduled Action wiring it together.

---

### Task 1: Gif tier config

**Files:**
- Create: `gif-rules.json`

**Interfaces:**
- Produces: a JSON object with keys `default`, `div2`, `div3`, `div5`, each a gif URL string. Consumed by `scripts/select_gif.py` (Task 2) and read directly by anyone wanting to swap artwork later.

- [ ] **Step 1: Create the file**

```json
{
  "default": "https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif",
  "div2": "https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif",
  "div3": "https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif",
  "div5": "https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif"
}
```

- [ ] **Step 2: Validate it's well-formed JSON**

Run: `python3 -m json.tool gif-rules.json`
Expected: pretty-printed JSON echoed back, no error.

- [ ] **Step 3: Commit**

```bash
git add gif-rules.json
git commit -m "feat: add gif tier config for header easter egg"
```

---

### Task 2: Gif tier selection logic (TDD)

**Files:**
- Create: `scripts/select_gif.py`
- Test: `scripts/test_select_gif.py`

**Interfaces:**
- Consumes: `gif-rules.json` schema from Task 1 (keys `default`, `div2`, `div3`, `div5`).
- Produces: `select_gif(count: int, rules: dict) -> str` importable from `scripts/select_gif.py`. Consumed by Task 7 (the Action workflow) via the script's CLI: `python3 scripts/select_gif.py <count> <rules_path>` prints the chosen URL to stdout.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_select_gif.py`:

```python
import unittest

from select_gif import select_gif


RULES = {
    "default": "default.gif",
    "div2": "two.gif",
    "div3": "three.gif",
    "div5": "five.gif",
}


class SelectGifTests(unittest.TestCase):
    def test_zero_is_default(self):
        self.assertEqual(select_gif(0, RULES), RULES["default"])

    def test_one_is_default(self):
        self.assertEqual(select_gif(1, RULES), RULES["default"])

    def test_two_is_div2(self):
        self.assertEqual(select_gif(2, RULES), RULES["div2"])

    def test_three_is_div3(self):
        self.assertEqual(select_gif(3, RULES), RULES["div3"])

    def test_five_is_div5(self):
        self.assertEqual(select_gif(5, RULES), RULES["div5"])

    def test_six_div2_and_div3_picks_div3(self):
        self.assertEqual(select_gif(6, RULES), RULES["div3"])

    def test_ten_div2_and_div5_picks_div5(self):
        self.assertEqual(select_gif(10, RULES), RULES["div5"])

    def test_fifteen_div3_and_div5_picks_div5(self):
        self.assertEqual(select_gif(15, RULES), RULES["div5"])

    def test_thirty_div2_div3_div5_picks_div5(self):
        self.assertEqual(select_gif(30, RULES), RULES["div5"])

    def test_seven_is_default(self):
        self.assertEqual(select_gif(7, RULES), RULES["default"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s scripts -p "test_*.py" -v`
Expected: `ModuleNotFoundError: No module named 'select_gif'` (or import error) — fails because `select_gif.py` doesn't exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/select_gif.py`:

```python
import json
import sys


def select_gif(count: int, rules: dict) -> str:
    if count > 0 and count % 5 == 0:
        return rules["div5"]
    if count > 0 and count % 3 == 0:
        return rules["div3"]
    if count > 0 and count % 2 == 0:
        return rules["div2"]
    return rules["default"]


def main() -> None:
    count = int(sys.argv[1])
    rules_path = sys.argv[2]
    with open(rules_path, encoding="utf-8") as f:
        rules = json.load(f)
    print(select_gif(count, rules))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s scripts -p "test_*.py" -v`
Expected: 10 tests, all `ok`, final line `OK`.

- [ ] **Step 5: Verify the CLI entrypoint manually**

Run: `python3 scripts/select_gif.py 10 gif-rules.json`
Expected: prints `https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif` (the placeholder div5 URL from Task 1).

- [ ] **Step 6: Commit**

```bash
git add scripts/select_gif.py scripts/test_select_gif.py
git commit -m "feat: add gif tier selection logic with tests"
```

---

### Task 3: README header gif rewrite (TDD)

**Files:**
- Create: `scripts/update_readme_gif.py`
- Test: `scripts/test_update_readme_gif.py`

**Interfaces:**
- Consumes: README.md's current header format — first `<img>` tag, exact pattern `<img height="" src="...">` followed by two spaces and `/>` (matches `README.md:2` as it exists today).
- Produces: `update_readme_gif(text: str, new_url: str) -> str` — takes README content, returns new content with the header `src` replaced; raises `ValueError` if no header `<img>` tag is found. Consumed by Task 7 (the Action workflow) via CLI: `python3 scripts/update_readme_gif.py <new_url> [readme_path]` (default `README.md`), which rewrites the file in place.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_update_readme_gif.py`:

```python
import unittest

from update_readme_gif import update_readme_gif


SAMPLE = (
    '<div align="center">\n'
    '  <img height="" src="https://example.com/old.gif"  />\n'
    '</div>\n'
)


class UpdateReadmeGifTests(unittest.TestCase):
    def test_replaces_header_src(self):
        result = update_readme_gif(SAMPLE, "https://example.com/new.gif")
        self.assertIn('src="https://example.com/new.gif"', result)
        self.assertNotIn("old.gif", result)

    def test_preserves_surrounding_markup(self):
        result = update_readme_gif(SAMPLE, "https://example.com/new.gif")
        self.assertTrue(result.startswith('<div align="center">\n'))
        self.assertIn('</div>\n', result)

    def test_same_url_is_noop_but_valid(self):
        result = update_readme_gif(SAMPLE, "https://example.com/old.gif")
        self.assertEqual(result, SAMPLE)

    def test_only_replaces_first_img(self):
        text = SAMPLE + '<img height="" src="https://example.com/second.gif"  />\n'
        result = update_readme_gif(text, "https://example.com/new.gif")
        self.assertIn('src="https://example.com/new.gif"', result)
        self.assertIn('src="https://example.com/second.gif"', result)

    def test_raises_when_no_header_img(self):
        with self.assertRaises(ValueError):
            update_readme_gif("<div>no image here</div>\n", "https://example.com/new.gif")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s scripts -p "test_*.py" -v`
Expected: `test_update_readme_gif.py` tests fail with `ModuleNotFoundError: No module named 'update_readme_gif'`. The Task 2 tests (`test_select_gif.py`) still pass.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/update_readme_gif.py`:

```python
import re
import sys

HEADER_IMG_PATTERN = re.compile(r'(<img height="" src=")[^"]+("\s*/>)')


def update_readme_gif(text: str, new_url: str) -> str:
    new_text, count = HEADER_IMG_PATTERN.subn(
        lambda m: m.group(1) + new_url + m.group(2), text, count=1
    )
    if count == 0:
        raise ValueError("header <img> tag not found")
    return new_text


def main() -> None:
    new_url = sys.argv[1]
    readme_path = sys.argv[2] if len(sys.argv) > 2 else "README.md"
    with open(readme_path, encoding="utf-8") as f:
        text = f.read()
    updated = update_readme_gif(text, new_url)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s scripts -p "test_*.py" -v`
Expected: 15 tests total (10 from Task 2 + 5 here), all `ok`, final line `OK`.

- [ ] **Step 5: Verify the CLI entrypoint against the real README (read-only check)**

Run: `python3 scripts/update_readme_gif.py "https://example.com/test.gif" /tmp/readme-check.md` against a copy first so the real file isn't touched:

```bash
cp README.md /tmp/readme-check.md
python3 scripts/update_readme_gif.py "https://example.com/test.gif" /tmp/readme-check.md
head -3 /tmp/readme-check.md
rm /tmp/readme-check.md
```

Expected: second line of output shows `src="https://example.com/test.gif"`.

- [ ] **Step 6: Commit**

```bash
git add scripts/update_readme_gif.py scripts/test_update_readme_gif.py
git commit -m "feat: add README header gif rewrite logic with tests"
```

---

### Task 4: Secret click page

**Files:**
- Create: `docs/secret.html`

**Interfaces:**
- Consumes: Abacus hit endpoint `https://abacus.jasoncameron.dev/hit/morphqdd-readme/secret-clicks` (returns JSON `{"value": <int>}`).
- Produces: a publicly servable page at `https://morphqdd.github.io/morphqdd/secret.html` once Pages is enabled (Task 8). Linked from `README.md` in Task 6.

- [ ] **Step 1: Create the page**

Create `docs/secret.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>🕯️</title>
  <style>
    body {
      background: #0b0b12;
      color: #d9d4e8;
      font-family: monospace;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
    }
    #msg { font-size: 1.2rem; text-align: center; }
  </style>
</head>
<body>
  <div id="msg">registering click...</div>
  <script>
    fetch("https://abacus.jasoncameron.dev/hit/morphqdd-readme/secret-clicks")
      .then((res) => res.json())
      .then((data) => {
        document.getElementById("msg").textContent =
          "👁️ click registered — " + data.value + " total";
      })
      .catch(() => {
        document.getElementById("msg").textContent =
          "couldn't reach the counter, try again later";
      });
  </script>
</body>
</html>
```

- [ ] **Step 2: Verify it locally**

Run, from the repo root:

```bash
cd docs && python3 -m http.server 8123 &
sleep 1
curl -s http://localhost:8123/secret.html | grep -c "abacus.jasoncameron.dev/hit/morphqdd-readme/secret-clicks"
kill %1
cd ..
```

Expected: `1` printed (the fetch URL is present in the served HTML), then the background server is killed.

- [ ] **Step 3: Commit**

```bash
git add docs/secret.html
git commit -m "feat: add secret click counter page"
```

---

### Task 5: Random commit roulette page

**Files:**
- Create: `docs/roulette.html`

**Interfaces:**
- Consumes: public GitHub REST API, unauthenticated — `GET https://api.github.com/users/morphqdd/repos?per_page=100&type=owner` and `GET https://api.github.com/repos/morphqdd/{repo}/commits?per_page=100`.
- Produces: a publicly servable page at `https://morphqdd.github.io/morphqdd/roulette.html` once Pages is enabled (Task 8). Linked from `README.md` in Task 6.

- [ ] **Step 1: Create the page**

Create `docs/roulette.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>🎲</title>
  <style>
    body {
      background: #0b0b12;
      color: #d9d4e8;
      font-family: monospace;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
      text-align: center;
      padding: 0 1rem;
    }
  </style>
</head>
<body>
  <div id="msg">rolling the dice...</div>
  <script>
    const OWNER = "morphqdd";
    const MAX_ATTEMPTS = 5;

    async function fetchJson(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error("GitHub API error: " + res.status);
      return res.json();
    }

    async function pickRandomCommitUrl() {
      const repos = await fetchJson(
        "https://api.github.com/users/" + OWNER + "/repos?per_page=100&type=owner"
      );
      if (!repos.length) throw new Error("no public repos found");

      for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
        const repo = repos[Math.floor(Math.random() * repos.length)];
        const commits = await fetchJson(
          "https://api.github.com/repos/" + OWNER + "/" + repo.name + "/commits?per_page=100"
        );
        if (commits.length) {
          const commit = commits[Math.floor(Math.random() * commits.length)];
          return commit.html_url;
        }
      }
      throw new Error("couldn't find a repo with commits after " + MAX_ATTEMPTS + " tries");
    }

    pickRandomCommitUrl()
      .then((url) => {
        window.location.href = url;
      })
      .catch((err) => {
        document.getElementById("msg").textContent =
          "couldn't roll the dice: " + err.message;
      });
  </script>
</body>
</html>
```

- [ ] **Step 2: Verify it locally**

```bash
cd docs && python3 -m http.server 8124 &
sleep 1
curl -s http://localhost:8124/roulette.html | grep -c "api.github.com/users/morphqdd/repos"
kill %1
cd ..
```

Expected: `1` printed.

- [ ] **Step 3: Manually verify the redirect works in a real browser**

Open `https://morphqdd.github.io/morphqdd/roulette.html` (after Task 8 enables Pages) and confirm it redirects to a real commit on a `morphqdd` repo within a couple seconds. (If Pages isn't live yet, this check moves to Task 8's end-to-end verification instead.)

- [ ] **Step 4: Commit**

```bash
git add docs/roulette.html
git commit -m "feat: add random commit roulette page"
```

---

### Task 6: README links

**Files:**
- Modify: `README.md:37-41` (insert roulette badge after this block) and end of file (append secret link).

**Interfaces:**
- Consumes: page URLs from Tasks 4 and 5 (`https://morphqdd.github.io/morphqdd/secret.html`, `https://morphqdd.github.io/morphqdd/roulette.html`).

- [ ] **Step 1: Add the roulette badge after the Telegram badge block**

In `README.md`, the Telegram block currently reads (lines 37-41):

```html
<div align="center">
  <a href="https://t.me/WayToInsomnia" target="_blank">
    <img src="https://img.shields.io/static/v1?message=Telegram&logo=telegram&label=&color=2CA5E0&logoColor=white&labelColor=&style=for-the-badge" height="20" alt="telegram logo"  />
  </a>
</div>
```

Insert immediately after it (before the following `###`):

```html

<div align="center">
  <a href="https://morphqdd.github.io/morphqdd/roulette.html" target="_blank">
    <img src="https://img.shields.io/static/v1?message=Random%20Commit&logo=dice&label=%F0%9F%8E%B2&color=DEA584&logoColor=white&labelColor=&style=for-the-badge" height="20" alt="random commit roulette"  />
  </a>
</div>
```

- [ ] **Step 2: Append the secret link at the end of the file**

Append to the end of `README.md`:

```html

<div align="center">
  <a href="https://morphqdd.github.io/morphqdd/secret.html">🕯️</a>
</div>
```

- [ ] **Step 3: Verify the file is still valid by eye**

Run: `cat README.md`
Expected: both new blocks present, no broken HTML (every `<div>` has a matching `</div>`).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "feat: link random commit roulette and secret click page from README"
```

---

### Task 7: Scheduled Action to sync header gif

**Files:**
- Create: `.github/workflows/update-header-gif.yml`

**Interfaces:**
- Consumes: `scripts/select_gif.py` CLI (Task 2), `scripts/update_readme_gif.py` CLI (Task 3), Abacus read-only endpoint.
- Produces: commits to `main` updating `README.md`'s header `<img src>` when the computed tier changes.

- [ ] **Step 1: Create the workflow**

Create `.github/workflows/update-header-gif.yml`:

```yaml
name: Update header gif

on:
  schedule:
    - cron: "*/15 * * * *"
  workflow_dispatch:

jobs:
  update:
    permissions:
      contents: write
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - uses: actions/checkout@v4

      - name: Read click counter
        id: counter
        run: |
          COUNT=$(curl -s https://abacus.jasoncameron.dev/get/morphqdd-readme/secret-clicks | jq -r '.value // 0')
          echo "count=$COUNT" >> "$GITHUB_OUTPUT"

      - name: Compute target gif
        id: gif
        run: |
          URL=$(python3 scripts/select_gif.py "${{ steps.counter.outputs.count }}" gif-rules.json)
          echo "url=$URL" >> "$GITHUB_OUTPUT"

      - name: Update README header gif
        run: |
          python3 scripts/update_readme_gif.py "${{ steps.gif.outputs.url }}"

      - name: Commit and push if changed
        run: |
          if ! git diff --quiet README.md; then
            git config user.name "github-actions[bot]"
            git config user.email "github-actions[bot]@users.noreply.github.com"
            git add README.md
            git commit -m "chore: sync header gif to click-count tier"
            git push
          fi
```

- [ ] **Step 2: Validate the YAML is well-formed**

Run: `python3 -c "import yaml, sys; yaml.safe_load(open('.github/workflows/update-header-gif.yml'))" 2>&1 || python3 -c "import json,sys; print('install pyyaml or just eyeball it')"`

If `pyyaml` isn't installed, instead just visually confirm indentation matches the block above exactly (2-space, consistent) — this is the same style as the existing `.github/workflows/snake.yml`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/update-header-gif.yml
git commit -m "feat: add scheduled Action to sync header gif with click tier"
```

- [ ] **Step 4: Push and trigger a manual run to verify end-to-end**

```bash
git push
gh workflow run "Update header gif"
sleep 15
gh run list --workflow="Update header gif" --limit 1
```

Expected: the listed run has status `completed` and conclusion `success`. Since the counter starts at 0 (or whatever it currently is) and the placeholder gif URLs are all identical, expect **no new commit** from this run (no-op) — that's correct, not a failure.

---

### Task 8: Enable GitHub Pages and verify end-to-end

**Files:** none (repo settings + manual verification only).

- [ ] **Step 1: Enable Pages via the GitHub CLI**

```bash
gh api -X POST repos/morphqdd/morphqdd/pages -f "source[branch]=main" -f "source[path]=/docs" 2>&1 || \
gh api -X PUT repos/morphqdd/morphqdd/pages -f "source[branch]=main" -f "source[path]=/docs"
```

If both fail with a permissions error, enable manually: GitHub → repo Settings → Pages → Source: Deploy from a branch → Branch: `main`, folder: `/docs`.

- [ ] **Step 2: Wait for the Pages deployment**

```bash
gh api repos/morphqdd/morphqdd/pages/builds/latest 2>&1
```

Expected: eventually shows `"status": "built"` (may take a minute or two after first enabling).

- [ ] **Step 3: Verify the secret page live**

```bash
curl -s https://morphqdd.github.io/morphqdd/secret.html | grep -c "abacus.jasoncameron.dev"
```

Expected: `1`.

- [ ] **Step 4: Verify the roulette page live and redirects**

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://morphqdd.github.io/morphqdd/roulette.html
```

Expected: `200`. Then open the URL in an actual browser and confirm it lands on a real commit page within a few seconds.

- [ ] **Step 5: Click the secret link once and confirm the counter advances**

```bash
curl -s https://abacus.jasoncameron.dev/get/morphqdd-readme/secret-clicks
curl -s https://morphqdd.github.io/morphqdd/secret.html > /dev/null  # does NOT hit it (no JS execution in curl)
```

Note: `curl` won't execute the page's JS fetch. To actually register a click, open `https://morphqdd.github.io/morphqdd/secret.html` in a real browser once, then re-run:

```bash
curl -s https://abacus.jasoncameron.dev/get/morphqdd-readme/secret-clicks
```

Expected: the `value` increased by 1 compared to the first read.

- [ ] **Step 6: Manually re-run the gif-sync Action and confirm correct tier behavior**

```bash
gh workflow run "Update header gif"
sleep 15
gh run list --workflow="Update header gif" --limit 1
git log --oneline -3
```

Expected: if the new counter value matches a divisor (2, 3, or 5), and the placeholder gif URLs were left identical, there is still no new commit (since all four URLs in `gif-rules.json` are the same value) — this is expected given Task 1's placeholder config, not a bug. To see an actual swap, edit `gif-rules.json` with distinct URLs per tier first, then repeat this step.
