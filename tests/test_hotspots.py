"""Hotspot and bus-factor tests over real fixture histories."""

from repoheat.gitlog import collect_history
from repoheat.hotspots import bus_factor, hotspots


def test_hotspots_score_is_churn_times_current_size(make_repo):
    repo = make_repo()
    history = collect_history(repo)

    ranked = hotspots(repo, history)

    core = next(h for h in ranked if h.path == "src/core.py")
    assert core.churn == 5
    assert core.size == 5  # file exists today with 5 lines
    assert core.score == 25


def test_hotspots_rank_by_score_descending(make_repo):
    repo = make_repo()
    history = collect_history(repo)

    ranked = hotspots(repo, history)

    scores = [h.score for h in ranked]
    assert scores == sorted(scores, reverse=True)


def test_hotspots_missing_files_score_zero(make_repo):
    repo = make_repo()
    history = collect_history(repo)
    (repo / "src" / "core.py").unlink()  # deleted after all those commits

    ranked = hotspots(repo, history)

    core = next(h for h in ranked if h.path == "src/core.py")
    assert core.size == 0
    assert core.score == 0  # churn without current size is not a hotspot


def test_top_limits_the_ranking(make_repo):
    repo = make_repo()
    history = collect_history(repo)

    assert len(hotspots(repo, history, top=1)) == 1


def test_bus_factor_counts_distinct_authors(make_repo):
    repo = make_repo()
    history = collect_history(repo)

    rows = bus_factor(history)

    core = next(r for r in rows if r.path == "src/core.py")
    assert core.authors == 2  # Ada + Linus
    assert core.main_author == "Ada Lovelace"  # 2 of 3 commits
    readme = next(r for r in rows if r.path == "docs/readme.md")
    assert readme.authors == 1
    assert readme.main_author == "Ada Lovelace"


def test_bus_factor_fewest_authors_first(make_repo):
    repo = make_repo()
    history = collect_history(repo)

    rows = bus_factor(history)

    authors = [r.authors for r in rows]
    assert authors == sorted(authors)
    assert rows[0].authors == 1  # the fragile files come first


def test_bus_factor_ties_break_by_most_commits(make_repo):
    repo = make_repo()
    history = collect_history(repo)

    rows = bus_factor(history)

    single_author = [r for r in rows if r.authors == 1]
    assert single_author[0].commits >= single_author[-1].commits
