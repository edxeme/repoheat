"""Churn aggregation tests over parsed fixture histories."""

from repoheat.churn import aggregate
from repoheat.gitlog import collect_history


def test_aggregates_across_commits(make_repo):
    repo = make_repo()
    commits = collect_history(repo)

    churn = aggregate(commits)

    core = next(c for c in churn if c.path == "src/core.py")
    assert core.commits == 3
    assert core.added == 5  # 3 + 1 + 1
    assert core.deleted == 0
    assert core.total == 5
    assert core.last_touched.isoformat().startswith("2026-09-03")


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

    # both files in the same-day commit, readme first on the tie-break
    assert [c.path for c in churn] == ["docs/readme.md", "src/core.py"]


def test_since_excludes_older_commits(make_repo):
    repo = make_repo()
    commits = collect_history(repo)

    churn = aggregate(commits, since="2026-09-10")

    assert churn == []


def test_aggregate_empty_history():
    assert aggregate([]) == []
