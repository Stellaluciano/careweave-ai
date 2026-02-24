from packages.eval.run_eval import run_eval


def test_eval_runs_small_subset() -> None:
    report = run_eval(n=2)
    assert "aggregate" in report
    assert report["aggregate"]["citation_coverage"] >= 0
