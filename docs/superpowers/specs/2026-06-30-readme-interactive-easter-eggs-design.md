# README interactive easter eggs: commit roulette + click-driven header gif

Date: 2026-06-30
Status: approved

## Goal

Add two interactive elements to the `morphqdd/morphqdd` profile README, fitting
the existing night/insomnia theme:

- **G — Random Commit Roulette**: a visible badge that sends a visitor to a
  random commit from one of the owner's public repos.
- **H — Secret click counter**: a small, easy-to-miss link that, when clicked,
  increments a public counter. The header gif at the top of the README is
  swapped based on which divisor (5, 3, or 2) the current total click count
  satisfies, with 5 taking priority over 3 over 2, and a default gif when none
  apply.

No paid services, no secrets beyond the repo's existing default
`GITHUB_TOKEN`.

## Components

### 1. GitHub Pages site (`docs/` on `main`)

Served at `https://morphqdd.github.io/morphqdd/`. Two static pages, no build
step, no server:

- `docs/roulette.html` — on load, calls the public GitHub REST API
  (unauthenticated) to list the owner's public repos, picks one at random
  (retrying if it has zero commits), fetches its commit list, picks one
  commit at random, and redirects (`window.location.href`) to that commit's
  `html_url`. Shows a one-line loading message while this happens, and a
  plain-text error message if the GitHub API call fails (e.g. rate limited).
- `docs/secret.html` — on load, calls the Abacus counter API's hit endpoint
  (see below) to increment the shared counter, then displays the new total
  count with a short acknowledgement message ("👁️ click registered — N total").
  No redirect.

### 2. Click counter (Abacus)

Uses `abacus.jasoncameron.dev`, a free, unauthenticated counter API:

- Increment + read: `GET https://abacus.jasoncameron.dev/hit/morphqdd-readme/secret-clicks`
- Read-only (no increment): `GET https://abacus.jasoncameron.dev/get/morphqdd-readme/secret-clicks`

`secret.html` calls the hit endpoint. The GitHub Action (below) calls the
read-only endpoint so checking for an update never itself counts as a click.

### 3. GitHub Action: `update-header-gif.yml`

Runs on a schedule (`*/15 * * * *`) and on `workflow_dispatch`.

Steps:
1. `curl` the Abacus read-only endpoint, parse the integer count.
2. Determine the target gif by priority: `count % 5 == 0` → gif for 5,
   else `count % 3 == 0` → gif for 3, else `count % 2 == 0` → gif for 2,
   else the default gif. (`count == 0` uses the default gif.)
3. Look up the corresponding URL in `gif-rules.json` (new file at repo root).
4. If the README's header `<img src="...">` (first `<img>` tag in the file)
   does not already match the target URL, replace it in place.
5. If the file changed, commit and push to `main` using the default
   `GITHUB_TOKEN` (`contents: write` permission), mirroring the existing
   pattern in `.github/workflows/snake.yml`.

### 4. `gif-rules.json` (repo root, new file)

```json
{
  "default": "https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif",
  "div2": "https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif",
  "div3": "https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif",
  "div5": "https://i.pinimg.com/originals/3c/31/c8/3c31c8503d9e31400e96d4b90b93c141.gif"
}
```

All four entries start out pointing at the current header gif as a
placeholder value (a valid, working URL — not a TBD). The owner edits this
file directly any time to swap in real artwork per tier; no code changes
needed.

### 5. README changes

- Add a visible badge near the existing badge row, linking to
  `https://morphqdd.github.io/morphqdd/roulette.html`:
  `🎲 Random Commit` (shields.io static badge styled to match existing
  Rust-themed badges).
- Add one small, unlabeled emoji link (🕯️) near the bottom of the README,
  sized small (`height="20"` or plain text emoji, no badge styling) and not
  called out in surrounding text, linking to
  `https://morphqdd.github.io/morphqdd/secret.html`.

## Data flow

```
visitor clicks 🕯️ → secret.html → Abacus /hit (counter++) → display count
                                            |
                                            v
update-header-gif.yml (every 15 min) → Abacus /get (read) → compute tier
                                            → gif-rules.json lookup
                                            → README.md header <img> rewrite
                                            → commit + push (if changed)

visitor clicks 🎲 Random Commit badge → roulette.html → GitHub REST API
                                            → random repo → random commit
                                            → redirect to commit URL
```

## Error handling

- `roulette.html`: GitHub API failure or rate limit → show plain error text
  on the page, no redirect, no crash.
- `roulette.html`: a selected repo has zero commits → silently retry with
  another repo (bounded retries, e.g. up to 5 attempts) before giving up
  with an error message.
- `update-header-gif.yml`: Abacus read failure → step fails loudly (job
  fails), no partial/garbage commit. Next scheduled run retries.
- Idempotent commits: Action only commits when the computed target URL
  differs from what's currently in README.md, so a healthy run with no
  count change is a no-op (no empty commits).

## Out of scope

- No analytics/tracking beyond the single Abacus counter value.
- No authentication, no rate-limit handling beyond basic retry for roulette.
- No visual "X clicks until next tier" progress indicator in the README
  (count itself isn't shown in the main README, only on `secret.html`).
- Picking final artwork for the 3 tiers + default is left to the owner via
  `gif-rules.json`.
