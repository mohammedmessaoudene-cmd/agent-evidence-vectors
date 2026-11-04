"""Billing evidence never becomes effect-owner reconciliation (issue #435)."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("billing_case_generator", ROOT / "gen_vectors.py")
assert spec and spec.loader
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)
from agent_evidence_vectors import uncertaineffect as reader  # noqa: E402

EXPECTED = {
    "billing-final-invoice-does-not-authorize-retry": ("deny", "retry_after_unknown"),
    "allow-billing-final-invoice-owner-absent-before-retry": ("allow", "effect_held"),
    "billing-zero-invoice-does-not-establish-no-effect":
        ("deny", "outcome_settled_without_authority"),
    "allow-billing-zero-invoice-keeps-outcome-unknown": ("allow", "effect_held"),
}


def records() -> dict[str, dict]:  # type: ignore[type-arg]
    all_cases = {case[0]: case for case in generator.cases()}
    assert set(EXPECTED) <= set(all_cases)
    return {name: all_cases[name][1] for name in EXPECTED}


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_billing_cases_match_unchanged_reader(name: str) -> None:
    record = records()[name]
    reason = reader._first_failure(record, frozenset())
    actual = ("deny", reason) if reason else ("allow", reader.ALLOWED_REASON)
    assert actual == EXPECTED[name]
    assert record["billingObservations"][0]["kind"] == "final_invoice"


def test_retry_pair_differs_only_in_owner_reconciliation_and_identity() -> None:
    data = records()
    refused = copy.deepcopy(data["billing-final-invoice-does-not-authorize-retry"])
    allowed = copy.deepcopy(data["allow-billing-final-invoice-owner-absent-before-retry"])
    assert refused.pop("reconciliations") == []
    assert allowed.pop("reconciliations") == [generator.lookup(30, "absent")]
    refused.pop("recordId")
    allowed.pop("recordId")
    assert refused == allowed


def test_zero_invoice_pair_differs_only_in_reported_outcome_and_identity() -> None:
    data = records()
    refused = copy.deepcopy(data["billing-zero-invoice-does-not-establish-no-effect"])
    allowed = copy.deepcopy(data["allow-billing-zero-invoice-keeps-outcome-unknown"])
    assert refused.pop("reported") == {"outcome": "not_run"}
    assert allowed.pop("reported") == {"outcome": "unknown"}
    refused.pop("recordId")
    allowed.pop("recordId")
    assert refused == allowed


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_invoice_annotation_cannot_change_authoritative_reading(name: str) -> None:
    record = records()[name]
    before = (reader.settled_outcome(record), reader._first_failure(record, frozenset()))
    del record["billingObservations"]
    assert (reader.settled_outcome(record), reader._first_failure(record, frozenset())) == before


@pytest.mark.parametrize("name", [name for name in EXPECTED if EXPECTED[name][0] == "deny"])
def test_each_new_denial_forces_its_existing_rule(name: str) -> None:
    record = records()[name]
    reason = EXPECTED[name][1]
    assert reader._first_failure(record, frozenset({reason})) is None


def test_billing_is_not_a_new_effect_capacity_release_rule() -> None:
    data = records()
    for record in data.values():
        assert record["reservation"]["charged"] is True
    for name in ("billing-zero-invoice-does-not-establish-no-effect",
                 "allow-billing-zero-invoice-keeps-outcome-unknown"):
        assert data[name]["billingObservations"][0]["amountMicrousd"] == 0
        assert reader.settled_outcome(data[name]) == "unknown"
