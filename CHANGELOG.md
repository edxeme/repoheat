# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] — 2026-10-02

### Added

- Docker image with an end-to-end smoke run: builds a tiny repo with real
  git commits, then maps it with all three commands.
- GitHub Actions CI: pytest across Python 3.11–3.13 plus a self-analysis
  smoke step.
- Full documentation with real self-analysis output.

## [0.1.1] — 2026-09-30

### Fixed

- numstat rename entries (`{old => new}`, `old => new`,
  `prefix/{old => new}/suffix`) now resolve to the file's new name instead
  of landing on ghost paths; binary files (`-` counts) are flagged with
  zero counts instead of crashing the parse with a ValueError.
- Regression tests build a real repository with `git mv` and a binary blob,
  pinning git's attribution semantics.

## [0.1.0] — 2026-09-29

### Added

- `repoheat churn PATH [--since DATE] [--json]` — per-file change volume,
  heaviest first; inclusive day boundary, timezone-independent.
- `repoheat hotspots PATH [-n N] [--json]` — churn × current size ranking;
  deleted files score zero.
- `repoheat bus-factor PATH [-n N] [--json]` — distinct authors per file,
  fewest first, with the main author per file.
- `git log --numstat -M` parsed with ASCII record/field separators; git
  failures surface as `GitHistoryError`, never raw tracebacks.
- Fixture repositories built with real `git init`/`add`/`commit` commands
  for end-to-end parser verification.
