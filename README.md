# repoheat

[![CI](https://github.com/edxeme/repoheat/actions/workflows/ci.yml/badge.svg)](https://github.com/edxeme/repoheat/actions/workflows/ci.yml)
[![PyPI — python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://pypi.org/project/repoheat/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-stdlib%20only-success)](#how-it-works)

Forensics for git repositories — **churn**, change **hotspots** and **bus
factor**, parsed straight from `git log`. Know where a codebase lives
dangerously before you touch it.

```sh
$ repoheat hotspots . -n 3
  score  churn   size  path
---------------------------
  21509    157    137  src/repoheat/gitlog.py
  15904    142    112  tests/test_gitlog.py
  12769    113    113  src/repoheat/cli.py
```

That is repoheat analyzing *its own history* — the fastest way to see what
it does.

## Why

Before refactoring, estimating, or onboarding onto a codebase you need to
know where the risk lives: which files change constantly (churn), which of
those are still big today (hotspots), and which of them only one person
understands (bus factor). repoheat answers all three from a single
`git log --numstat` invocation — no daemons, no indexing, no config.

## Install

```sh
pipx install repoheat        # or: pip install repoheat
```

Requires Python 3.11+ and git.

## Usage

**Churn** — per-file change volume, heaviest first:

```sh
$ repoheat churn .
path                                     commits    add    del  total        last
---------------------------------------------------------------------------------
src/repoheat/gitlog.py                         3    147     10    157  2026-09-30
tests/test_gitlog.py                           3    127     15    142  2026-09-30
src/repoheat/cli.py                            1    113      0    113  2026-09-29
```

Filter with `--since YYYY-MM-DD` — the day boundary is **inclusive** and
timezone-independent.

**Hotspots** — churn × current size; the files where defects concentrate:

```sh
$ repoheat hotspots . -n 5
  score  churn   size  path
---------------------------
  21509    157    137  src/repoheat/gitlog.py
  15904    142    112  tests/test_gitlog.py
  12769    113    113  src/repoheat/cli.py
  11448    108    106  tests/conftest.py
   6561     81     81  src/repoheat/hotspots.py
```

**Bus factor** — knowledge concentration; fewest authors first:

```sh
$ repoheat bus-factor . -n 3
authors commits main author              path
---------------------------------------------
      1       3 Edwin Martínez           src/repoheat/gitlog.py
      1       3 Edwin Martínez           tests/conftest.py
      1       3 Edwin Martínez           tests/test_gitlog.py
```

**JSON everywhere** — add `--json` when a dashboard is the real consumer.

## How it works

- **One git invocation.** `git log --numstat -M` with ASCII record/field
  separators (`%x1e`/`%x1f`) so author names and paths with spaces survive.
- **Renames resolve forward.** `{old => new}` entries land on the file's
  *new* name — where the code lives today. Binary files (`-` counts) are
  flagged, never fatal.
- **Date filtering in Python.** git's `--since` is approxidate: its cutoff
  depends on the host timezone and it excludes same-day commits (verified
  empirically). repoheat filters parsed commits instead — inclusive day
  boundary, identical on every machine.
- **Size as cheap complexity.** Hotspot score is churn × current line
  count; deleted files score zero because churn without surviving code is
  not a risk.

## Docker

The image ships git and runs an end-to-end smoke: it builds a tiny
repository with real commits, then maps it with all three commands.

```sh
docker build -t repoheat .
docker run --rm repoheat
```

## Development

```sh
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/pytest    # fixture repos are built with real git commands
```

## Roadmap

- [ ] `--format dot` — file coupling graph (files that change together)
- [ ] `--window` churn over sliding windows instead of lifetime
- [ ] Optional complexity input from AST analysis to replace size

## License

[MIT](LICENSE) — Edwin Martinez
