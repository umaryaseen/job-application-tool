"""TASK-014 / A20: reviewed requirement corrections and immutable versions.

Synthetic postings only (reserved example data); every store is a temporary
private root.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from job_application_engine.cli import main
from job_application_engine.domain.requirement_review import (
    RequirementCorrection,
    RequirementReviewRevision,
    ReviewedRequirement,
)
from job_application_engine.extraction.review import (
    ConcurrentReviewError,
    ReviewError,
    StaleReviewError,
    hard_gates,
)
from job_application_engine.ingestion.text import ingest_job
from job_application_engine.snapshots import requirements as store
from job_application_engine.snapshots.requirements import (
    apply_correction,
    load_review,
    read_correction,
)
from job_application_engine.verification.support import canonical_json, model_digest

SOURCE = (
    "Requirements\n- Python or Java is required.\n- 3+ years of experience with SQL.\n"
    "- German is not required.\n- Experience with Kubernetes would be a plus.\n"
    "- Strong knowledge of Spark, Flink and similar tools.\n"
    "- No travel, not even occasionally.\nPreferred:\n- Docker.\n"
    "Nice to have\n- Terraform experience.\nBenefits\n- Free coffee.\n"
)
T0 = datetime(2026, 11, 15, 12, tzinfo=UTC)


@pytest.fixture
def root(tmp_path: Path) -> Path:
    ingest_job(SOURCE.encode(), job_id="synthetic-role", locale="en", data_root=tmp_path)
    return tmp_path


def rows_by_quote(state) -> dict[str, ReviewedRequirement]:
    return {row.span.quote: row for row in state.view.rows}


def correction(state, *operations: dict, **overrides: object) -> RequirementCorrection:
    payload = {
        "job_id": state.job.job_id,
        "job_revision": state.job.revision,
        "job_record_digest": state.job.record_digest,
        "raw_sha256": state.job.raw_sha256,
        "base_review_revision": state.view.review_revision,
        "base_view_digest": state.view.view_digest,
        "operations": list(operations),
    }
    payload.update(overrides)
    return RequirementCorrection.model_validate_json(json.dumps(payload))


def accept(row: ReviewedRequirement) -> dict:
    """Explicit acceptance naming every displayed draft uncertainty of the row."""
    return {
        "op": "accept",
        "candidate_id": row.candidate_id,
        "acknowledged_reasons": row.review_reasons,
    }


def priority(row: ReviewedRequirement, value: str) -> dict:
    return {"op": "set_priority", "candidate_id": row.candidate_id, "priority": value}


RAW = "jobs/synthetic-role/revisions/r000001/job_description.raw.txt"


def span(text: str, quote: str, start_at: int = 0) -> dict:
    start = text.index(quote, start_at)
    return {"start": start, "end": start + len(quote), "quote": quote}


def apply(
    root: Path, fix: RequirementCorrection, *, minutes: int = 0, reviewer: str = "reviewer-a"
):
    return apply_correction(
        fix, reviewer_id=reviewer, reviewed_at=T0 + timedelta(minutes=minutes), data_root=root
    )


def test_display_shows_quotes_priority_groups_and_uncertainty_all_unreviewed(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    rows = rows_by_quote(state)
    python = rows["Python or Java is required."]
    assert (python.priority, python.condition.node, python.gate) == (
        "mandatory",
        "any",
        "unreviewed",
    )
    assert [c.span.quote for c in python.condition.children] == ["Python", "Java"]
    sql = rows["3+ years of experience with SQL."]
    assert [(t.measure, t.operator, t.value) for t in sql.thresholds] == [("duration", "gte", 3)]
    spark = rows["Strong knowledge of Spark, Flink and similar tools."]
    assert spark.needs_review and spark.review_reasons == [
        "no_supported_condition", "unparsed_conjunction", "unsupported_grouping"
    ]  # fmt: skip
    assert rows["Free coffee."].gate == "not_a_requirement"
    assert all(row.review_state == "draft" for row in state.view.rows)
    assert hard_gates(state.view) == [] and state.view.review_revision == 0
    for row in state.view.rows:
        assert SOURCE[row.span.start : row.span.end] == row.span.quote


def test_edit_priority_and_accept_is_preserved_and_replayed(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    k8s = rows_by_quote(state)["Experience with Kubernetes would be a plus."].candidate_id
    record, path = apply(
        root,
        correction(
            state,
            {"op": "set_priority", "candidate_id": k8s, "priority": "mandatory"},
            {"op": "accept", "candidate_id": k8s, "acknowledged_reasons": []},
        ),
    )
    assert path.name == "v000001.json" and record.reviewer_id == "reviewer-a"
    assert record.reviewed_at == T0 and record.job_record_digest == state.job.record_digest
    again = load_review("synthetic-role", data_root=root)
    row = next(r for r in again.view.rows if r.candidate_id == k8s)
    assert (row.priority, row.edited_fields, row.review_state) == (
        "mandatory", ["priority"], "reviewed"
    )  # fmt: skip
    assert (row.reviewed_by, row.reviewed_in) == ("reviewer-a", 1)
    assert row.gate == "hard_gate" and [r.candidate_id for r in hard_gates(again.view)] == [k8s]
    # Replay against the same source reproduces the exact recorded view.
    assert again.view.view_digest == record.result_view_digest
    assert load_review("synthetic-role", data_root=root).view == again.view
    # The raw posting is untouched.
    raw = root / "jobs/synthetic-role/revisions/r000001/job_description.raw.txt"
    assert raw.read_text(encoding="utf-8") == SOURCE


def test_edit_group_with_verified_spans(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    row = rows_by_quote(state)["Python or Java is required."]
    start = row.span.start
    clause = SOURCE[start : row.span.end]
    group = {
        "node": "all",
        "span": span(SOURCE, "Python or Java", start),
        "connectives": [span(SOURCE, "or", start + clause.index("or"))],
        "children": [
            {"node": "term", "term_kind": "technology", "span": span(SOURCE, "Python", start)},
            {"node": "term", "term_kind": "technology", "span": span(SOURCE, "Java", start)},
        ],
    }
    fix = correction(
        state,
        {"op": "set_condition", "candidate_id": row.candidate_id, "condition": group},
        {"op": "accept", "candidate_id": row.candidate_id, "acknowledged_reasons": []},
    )
    apply(root, fix)
    after = rows_by_quote(load_review("synthetic-role", data_root=root))[row.span.quote]
    assert after.condition.node == "all" and after.edited_fields == ["condition"]
    assert after.gate == "hard_gate"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda s: {**s, "quote": "Pyth0n"},  # quote differs from the raw text
        lambda s: {**s, "start": s["start"] + 1, "end": s["end"] + 1},  # shifted offsets
        lambda s: {"start": 0, "end": 12, "quote": "Requirements"},  # outside the clause
        lambda s: {"start": 10**5, "end": 10**5 + 6, "quote": "Python"},  # beyond the text
    ],
)
def test_invalid_quote_or_offsets_are_rejected_and_nothing_is_stored(root: Path, mutate) -> None:
    state = load_review("synthetic-role", data_root=root)
    row = rows_by_quote(state)["Python or Java is required."]
    term = {
        "node": "term",
        "term_kind": "technology",
        "span": mutate(span(SOURCE, "Python", row.span.start)),
    }
    fix = correction(
        state, {"op": "set_condition", "candidate_id": row.candidate_id, "condition": term}
    )
    with pytest.raises(ReviewError):
        apply(root, fix)
    assert not (root / "jobs/synthetic-role/requirement-reviews/r000001/v000001.json").exists()


def test_connective_outside_its_group_is_rejected(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    row = rows_by_quote(state)["Python or Java is required."]
    start = row.span.start
    group = {
        "node": "any",
        "span": span(SOURCE, "Python or Java", start),
        "connectives": [span(SOURCE, "is", start)],  # inside the clause, outside the group
        "children": [
            {"node": "term", "term_kind": "technology", "span": span(SOURCE, "Python", start)},
            {"node": "term", "term_kind": "technology", "span": span(SOURCE, "Java", start)},
        ],
    }
    with pytest.raises(ReviewError, match="connective"):
        apply(
            root,
            correction(
                state, {"op": "set_condition", "candidate_id": row.candidate_id, "condition": group}
            ),
        )


def test_invalid_threshold_span_is_rejected(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    row = rows_by_quote(state)["3+ years of experience with SQL."]
    bad = {"measure": "duration", "operator": "gte", "value": 5, "unit": "years",
           "span": {"start": row.span.start, "end": row.span.start + 2, "quote": "5+"}}  # fmt: skip
    with pytest.raises(ReviewError):
        apply(
            root,
            correction(
                state,
                {"op": "set_thresholds", "candidate_id": row.candidate_id, "thresholds": [bad]},
            ),
        )


def test_stale_jd_digest_is_rejected(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    row = state.view.rows[0]
    for field in ("job_record_digest", "raw_sha256"):
        fix = correction(
            state, {"op": "reopen", "candidate_id": row.candidate_id}, **{field: "0" * 64}
        )
        with pytest.raises(StaleReviewError):
            apply(root, fix)


def test_concurrent_reviews_from_the_same_base_cannot_both_land(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    row = rows_by_quote(state)["Docker."]
    first = correction(
        state, {"op": "accept", "candidate_id": row.candidate_id, "acknowledged_reasons": []}
    )
    second = correction(
        state, {"op": "set_priority", "candidate_id": row.candidate_id, "priority": "mandatory"}
    )
    apply(root, first, reviewer="reviewer-a")
    with pytest.raises(ConcurrentReviewError):
        apply(root, second, minutes=1, reviewer="reviewer-b")
    assert load_review("synthetic-role", data_root=root).view.review_revision == 1


def test_racing_writer_loses_at_the_exclusive_link(root: Path, monkeypatch) -> None:
    state = load_review("synthetic-role", data_root=root)
    row = rows_by_quote(state)["Docker."]
    fix = correction(
        state, {"op": "accept", "candidate_id": row.candidate_id, "acknowledged_reasons": []}
    )
    original = store._publish

    def racing(folder: Path, number: int, record: RequirementReviewRevision) -> Path:
        # Another reviewer publishes the same revision number first.
        original(folder, number, record.model_copy(update={"reviewer_id": "reviewer-b"}))
        return original(folder, number, record)

    monkeypatch.setattr(store, "_publish", racing)
    with pytest.raises(ConcurrentReviewError):
        apply(root, fix)
    folder = root / "jobs/synthetic-role/requirement-reviews/r000001"
    assert sorted(p.name for p in folder.iterdir()) == ["v000001.json"]


def test_changed_jd_invalidates_prior_review(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    docker = rows_by_quote(state)["Docker."]
    apply(
        root,
        correction(
            state, {"op": "accept", "candidate_id": docker.candidate_id, "acknowledged_reasons": []}
        ),
    )
    reviewed = load_review("synthetic-role", data_root=root)
    edited = SOURCE.replace("3+ years", "5+ years")
    ingest_job(edited.encode(), job_id="synthetic-role", data_root=root)
    latest = load_review("synthetic-role", data_root=root)
    assert latest.job.revision == 2 and latest.view.review_revision == 0
    assert all(row.review_state == "draft" for row in latest.view.rows)
    assert hard_gates(latest.view) == []
    # The earlier review is historical: still verifiable, but superseded.
    old = load_review("synthetic-role", revision=1, data_root=root)
    assert old.view == reviewed.view and old.latest_job_revision == 2
    with pytest.raises(StaleReviewError, match="newer revision"):
        apply(
            root, correction(old, {"op": "reopen", "candidate_id": docker.candidate_id}), minutes=1
        )
    # A correction prepared against revision 1 cannot be pointed at revision 2.
    retargeted = correction(
        old, {"op": "reopen", "candidate_id": docker.candidate_id}, job_revision=2
    )
    with pytest.raises(StaleReviewError):
        apply(root, retargeted, minutes=1)


def _stored(root: Path, number: int = 1) -> Path:
    return root / f"jobs/synthetic-role/requirement-reviews/r000001/v{number:06d}.json"


def _accept_docker_then_terraform(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    rows = rows_by_quote(state)
    apply(
        root,
        correction(
            state,
            {
                "op": "accept",
                "candidate_id": rows["Docker."].candidate_id,
                "acknowledged_reasons": [],
            },
        ),
    )
    state = load_review("synthetic-role", data_root=root)
    apply(
        root,
        correction(
            state,
            {
                "op": "accept",
                "candidate_id": rows["Terraform experience."].candidate_id,
                "acknowledged_reasons": rows["Terraform experience."].review_reasons,
            },
        ),
        minutes=1,
    )


def _resign(path: Path, **changes: object) -> None:
    record = RequirementReviewRevision.model_validate_json(path.read_text(encoding="utf-8"))
    record = record.model_copy(update=changes)
    record = record.model_copy(
        update={"revision_digest": model_digest(record, exclude={"revision_digest"})}
    )
    os.chmod(path, 0o600)
    path.write_text(canonical_json(record) + "\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("tamper", "error"),
    [
        (lambda root: _stored(root).write_text(_stored(root).read_text().replace("-a", "-z")),
         ReviewError),
        (lambda root: _stored(root).unlink(), ReviewError),  # gap: v000002 without v000001
        (lambda root: _stored(root, 2).rename(_stored(root, 3)), ReviewError),
        (lambda root: (_stored(root).parent / "notes.txt").write_text("x"), ReviewError),
        (lambda root: _resign(_stored(root), classification_digest="1" * 64), StaleReviewError),
        (lambda root: _resign(_stored(root, 2), base_revision_digest="2" * 64), ReviewError),
        (lambda root: _resign(_stored(root, 2), reviewed_at=T0 - timedelta(days=1)), ReviewError),
        # A re-signed actor change no longer reproduces the recorded result digest.
        (lambda root: _resign(_stored(root), reviewer_id="reviewer-z"), ReviewError),
        (lambda root: (root / RAW).write_text(SOURCE.replace("Python", "Pascal")), ValueError),
    ],
)  # fmt: skip
def test_replay_rejects_tampered_or_incomplete_history(root: Path, tamper, error) -> None:
    _accept_docker_then_terraform(root)
    tamper(root)
    with pytest.raises(error):
        load_review("synthetic-role", data_root=root)


def test_interrupted_write_leaves_no_revision(root: Path) -> None:
    _accept_docker_then_terraform(root)
    folder = _stored(root).parent
    (folder / ".review-0123456789abcdef").write_text("partial")
    assert load_review("synthetic-role", data_root=root).view.review_revision == 2


def test_ambiguous_clause_needs_explicit_acknowledged_review(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    spark = rows_by_quote(state)["Strong knowledge of Spark, Flink and similar tools."]
    # Accepting without naming every uncertainty is refused.
    for reasons in ([], ["unsupported_grouping"]):
        fix = correction(
            state,
            {"op": "accept", "candidate_id": spark.candidate_id, "acknowledged_reasons": reasons},
        )
        with pytest.raises(ReviewError, match="acknowledge"):
            apply(root, fix)
    # Even an acknowledged, mandatory but unstructured clause is only a manual check.
    apply(root, correction(
        state,
        priority(spark, "mandatory"),
        accept(spark),
    ))  # fmt: skip
    after = load_review("synthetic-role", data_root=root)
    row = rows_by_quote(after)[spark.span.quote]
    assert (row.review_state, row.gate) == ("reviewed", "manual_check")
    assert hard_gates(after.view) == []


def test_negated_rows_and_unsupported_negation_never_gate(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    rows = rows_by_quote(state)
    german = rows["German is not required."]
    travel = rows["No travel, not even occasionally."]
    apply(root, correction(
        state,
        priority(german, "mandatory"),
        accept(german),
        priority(travel, "mandatory"),
        accept(travel),
    ))  # fmt: skip
    after = rows_by_quote(load_review("synthetic-role", data_root=root))
    assert after[german.span.quote].gate == "not_required"
    assert after[travel.span.quote].gate == "manual_check"


def test_edit_after_accept_returns_row_to_unreviewed(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    python = rows_by_quote(state)["Python or Java is required."]
    apply(
        root,
        correction(
            state, {"op": "accept", "candidate_id": python.candidate_id, "acknowledged_reasons": []}
        ),
    )
    state = load_review("synthetic-role", data_root=root)
    assert [r.candidate_id for r in hard_gates(state.view)] == [python.candidate_id]
    apply(
        root,
        correction(
            state,
            {"op": "set_priority", "candidate_id": python.candidate_id, "priority": "preferred"},
        ),
        minutes=1,
    )
    row = rows_by_quote(load_review("synthetic-role", data_root=root))[python.span.quote]
    assert (row.review_state, row.reviewed_by, row.gate) == ("draft", None, "unreviewed")


def test_role_changes_and_marker_rows(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    rows = rows_by_quote(state)
    marker = rows["Nice to have"]
    assert marker.role == "priority_marker"
    with pytest.raises(ReviewError, match="marker"):
        apply(
            root,
            correction(
                state,
                {
                    "op": "set_priority",
                    "candidate_id": marker.candidate_id,
                    "priority": "mandatory",
                },
            ),
        )
    coffee = rows["Free coffee."]
    with pytest.raises(ReviewError, match="only requirement rows"):
        apply(
            root,
            correction(
                state,
                {
                    "op": "set_priority",
                    "candidate_id": coffee.candidate_id,
                    "priority": "mandatory",
                },
            ),
        )
    with pytest.raises(ReviewError, match="already"):
        apply(
            root,
            correction(
                state,
                {"op": "set_role", "candidate_id": coffee.candidate_id, "role": "non_requirement"},
            ),
        )
    docker = rows["Docker."]
    apply(root, correction(
        state,
        {"op": "set_role", "candidate_id": docker.candidate_id, "role": "non_requirement"},
        {"op": "accept", "candidate_id": docker.candidate_id, "acknowledged_reasons": []},
        {"op": "accept", "candidate_id": marker.candidate_id, "acknowledged_reasons": []},
    ))  # fmt: skip
    after = rows_by_quote(load_review("synthetic-role", data_root=root))
    assert (after["Docker."].role, after["Docker."].condition, after["Docker."].gate) == (
        "non_requirement", None, "not_a_requirement"
    )  # fmt: skip
    assert after["Nice to have"].review_state == "reviewed"


def test_unknown_row_operation_shapes_and_bad_reviewer(root: Path) -> None:
    state = load_review("synthetic-role", data_root=root)
    with pytest.raises(ReviewError, match="unknown"):
        apply(root, correction(state, {"op": "reopen", "candidate_id": "req-missing"}))
    for bad in (
        {"op": "delete", "candidate_id": "req-x"},
        {"op": "reopen", "candidate_id": "req-x", "extra": 1},
    ):
        with pytest.raises(ValidationError):
            correction(state, bad)
    with pytest.raises(ValidationError):
        correction(state)  # an empty patch is not a review
    row = state.view.rows[0]
    with pytest.raises(ReviewError, match="reviewer"):
        apply(
            root,
            correction(state, {"op": "reopen", "candidate_id": row.candidate_id}),
            reviewer="Bad Reviewer",
        )


def test_review_time_must_not_go_backwards(root: Path) -> None:
    _accept_docker_then_terraform(root)
    state = load_review("synthetic-role", data_root=root)
    row = state.view.rows[0]
    with pytest.raises(ReviewError, match="precedes"):
        apply(
            root, correction(state, {"op": "reopen", "candidate_id": row.candidate_id}), minutes=-5
        )


def test_correction_file_must_be_private_bounded_and_unique_keyed(
    root: Path, tmp_path_factory
) -> None:
    state = load_review("synthetic-role", data_root=root)
    fix = correction(state, {"op": "reopen", "candidate_id": state.view.rows[0].candidate_id})
    inside = root / "corrections" / "fix.json"
    inside.parent.mkdir()
    inside.write_text(fix.model_dump_json(), encoding="utf-8")
    assert read_correction(Path("corrections/fix.json"), data_root=root) == fix
    outside = tmp_path_factory.mktemp("outside") / "fix.json"
    outside.write_text(fix.model_dump_json(), encoding="utf-8")
    with pytest.raises(ValueError):
        read_correction(outside, data_root=root)
    inside.write_text('{"job_id": "a", "job_id": "b"}', encoding="utf-8")
    with pytest.raises(ReviewError, match="duplicate"):
        read_correction(Path("corrections/fix.json"), data_root=root)
    inside.write_text(" " * (store.MAX_CORRECTION_BYTES + 1), encoding="utf-8")
    with pytest.raises(ReviewError, match="size"):
        read_correction(Path("corrections/fix.json"), data_root=root)


def test_cli_shows_review_and_applies_a_private_correction(root: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("JAE_DATA_DIR", str(root))
    assert main(["job-review", "--job-id", "synthetic-role"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["superseded"] is False and shown["hard_gate_ids"] == []
    rows = {row["span"]["quote"]: row for row in shown["view"]["rows"]}
    python = rows["Python or Java is required."]
    assert python["priority"] == "mandatory" and python["condition"]["node"] == "any"
    payload = {
        "job_id": "synthetic-role",
        "job_revision": 1,
        "job_record_digest": shown["view"]["job_record_digest"],
        "raw_sha256": shown["view"]["raw_sha256"],
        "base_review_revision": 0,
        "base_view_digest": shown["view"]["view_digest"],
        "operations": [
            {"op": "accept", "candidate_id": python["candidate_id"], "acknowledged_reasons": []}
        ],
    }
    (root / "fix.json").write_text(json.dumps(payload), encoding="utf-8")
    assert (
        main(["job-review-apply", "--correction", "fix.json", "--reviewer-id", "reviewer-a"]) == 0
    )
    assert json.loads(capsys.readouterr().out)["review_revision"] == 1
    assert (
        main(["job-review-apply", "--correction", "fix.json", "--reviewer-id", "reviewer-a"]) == 2
    )
    assert "reload and retry" in capsys.readouterr().err
    assert main(["job-review", "--job-id", "synthetic-role"]) == 0
    assert json.loads(capsys.readouterr().out)["hard_gate_ids"] == [python["candidate_id"]]
