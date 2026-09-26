"""Churn aggregation tests over parsed fixture histories."""

from repoheat.churn import aggregate
from repoheat.gitlog import collect_history


def test_aggregates_across_commits(make_repo):
    repo = make_repo()
    commits = collect_history(repo)

    churn = aggregate(commits)

    core = next(c for c in churn if c.path == "src/core.py")
    assert core.commits == 2
    assert core.added == 4  # 3 + 1
    assert core.deleted == 0
    assert core.total == 4
    assert core.last_touched.isoformat().startswith("2026-09-02")


def test_sorted_by_total_churn_descending(make_repo):
    repo = make_repo()
    commits = collect_history(repo)

    churn = aggregate(commits)

    totals = [c.total for c in churn]
    assert totals == sorted(totals, reverse=True)
    assert churn[0].path == "src/core.py"  # 4 beats readme's 1


def test_since_is_inclusive_of_the_same_day(make_repo):
    repo = make_repo()
    commits = collect_history(repo)

    churn = aggregate(commits, since="2026-09-03")

    assert [c.path for c in churn] == ["docs/readme.md"]  # committed that day


def test_since_excludes_older_commits(make_repo):
    repo = make_repo()
    commits = collect_history(repo)

    churn = aggregate(commits, since="2026-09-10")

    assert churn == []


def test_aggregate_empty_history():
    assert aggregate([]) == []
