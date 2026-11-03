from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from .data import DEFAULT_DB, connect


def _row_dict(row: Any) -> dict[str, Any]:
    return dict(row)


def load_case(alert_id: str, db_path: Path = DEFAULT_DB) -> dict[str, Any]:
    with connect(db_path) as connection:
        alert = connection.execute("SELECT * FROM alerts WHERE alert_id = ?", (alert_id,)).fetchone()
        if alert is None:
            raise ValueError(f"Unknown alert: {alert_id}")
        customer = connection.execute(
            "SELECT * FROM customers WHERE customer_id = ?", (alert["customer_id"],)
        ).fetchone()
        transactions = connection.execute(
            "SELECT * FROM transactions WHERE customer_id = ? ORDER BY transaction_date, transaction_id",
            (alert["customer_id"],),
        ).fetchall()
    return {"alert": _row_dict(alert), "customer": _row_dict(customer), "transactions": [_row_dict(row) for row in transactions]}


def _days_apart(first: str, last: str) -> int:
    return (date.fromisoformat(last) - date.fromisoformat(first)).days


def analyze(case: dict[str, Any]) -> dict[str, Any]:
    transactions = case["transactions"]
    near_threshold = [
        transaction for transaction in transactions
        if transaction["direction"] == "outbound" and 8000 <= transaction["amount"] < 10000
    ]
    counterparties = {transaction["counterparty"] for transaction in near_threshold}
    if len(near_threshold) >= 3 and len(counterparties) >= 3 and _days_apart(near_threshold[0]["transaction_date"], near_threshold[-1]["transaction_date"]) <= 7:
        ids = [transaction["transaction_id"] for transaction in near_threshold]
        return {
            "typology": "structuring",
            "risk_level": "high",
            "confidence": "high",
            "evidence_ids": ids,
            "rationale": f"{len(ids)} outbound payments between $8,000 and $10,000 were sent to {len(counterparties)} counterparties within seven days.",
            "alternative_explanation": "The data does not establish the commercial purpose of the consulting payments.",
        }

    inbound = [transaction for transaction in transactions if transaction["direction"] == "inbound" and transaction["amount"] >= 20000]
    outbound = [transaction for transaction in transactions if transaction["direction"] == "outbound"]
    for credit in inbound:
        following = [
            debit for debit in outbound
            if 0 <= _days_apart(credit["transaction_date"], debit["transaction_date"]) <= 2
        ]
        total_following = sum(debit["amount"] for debit in following)
        if total_following >= credit["amount"] * 0.8 and len(following) >= 2:
            ids = [credit["transaction_id"], *[debit["transaction_id"] for debit in following]]
            return {
                "typology": "rapid_pass_through",
                "risk_level": "medium",
                "confidence": "medium",
                "evidence_ids": ids,
                "rationale": f"${total_following:,.0f} was sent onward within two days of a ${credit['amount']:,.0f} incoming payment.",
                "alternative_explanation": "The transactions may be legitimate supplier payments; invoices and beneficial-owner data should be reviewed.",
            }

    return {
        "typology": "insufficient_evidence",
        "risk_level": "low",
        "confidence": "medium",
        "evidence_ids": [transaction["transaction_id"] for transaction in transactions],
        "rationale": "The available transaction history does not meet the configured risk-pattern thresholds.",
        "alternative_explanation": "Normal activity remains plausible based on the available transaction descriptions and recurrence.",
    }


def verify_evidence(case: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    known_ids = {transaction["transaction_id"] for transaction in case["transactions"]}
    cited_ids = set(analysis["evidence_ids"])
    unsupported = sorted(cited_ids - known_ids)
    return {
        "passed": not unsupported,
        "cited_transaction_ids": sorted(cited_ids),
        "unsupported_transaction_ids": unsupported,
        "review_note": "All cited records were retrieved from the local synthetic database." if not unsupported else "Unsupported citations must be removed before review.",
    }


def write_memo(case: dict[str, Any], analysis: dict[str, Any]) -> str:
    customer = case["customer"]
    alert = case["alert"]
    evidence = ", ".join(analysis["evidence_ids"])
    return (
        f"Investigation memo for {alert['alert_id']}\n\n"
        f"Customer: {customer['name']} ({customer['customer_id']}); risk rating: {customer['risk_rating']}.\n"
        f"Alert: {alert['description']}\n\n"
        f"Assessment: {analysis['typology']} ({analysis['risk_level']} risk, {analysis['confidence']} confidence).\n"
        f"Evidence: {analysis['rationale']} Cited transactions: {evidence}.\n"
        f"Alternative explanation: {analysis['alternative_explanation']}\n\n"
        "Recommendation: Route to a human compliance reviewer. This synthetic demonstration does not make an automated filing or customer decision."
    )


def investigate(alert_id: str, db_path: Path = DEFAULT_DB) -> dict[str, Any]:
    case = load_case(alert_id, db_path)
    analysis = analyze(case)
    verification = verify_evidence(case, analysis)
    return {
        "alert_id": alert_id,
        "customer": case["customer"],
        "alert_description": case["alert"]["description"],
        "risk_level": analysis["risk_level"],
        "suspected_typology": analysis["typology"],
        "confidence": analysis["confidence"],
        "evidence": analysis["evidence_ids"],
        "evidence_verification": verification,
        "alternative_explanation": analysis["alternative_explanation"],
        "requires_human_review": True,
        "memo": write_memo(case, analysis),
    }


def evaluate(db_path: Path = DEFAULT_DB) -> dict[str, Any]:
    with connect(db_path) as connection:
        alerts = connection.execute("SELECT * FROM alerts ORDER BY alert_id").fetchall()
    results = []
    for alert in alerts:
        packet = investigate(alert["alert_id"], db_path)
        expected_evidence = set(alert["expected_evidence"].split(","))
        actual_evidence = set(packet["evidence"])
        results.append({
            "alert_id": alert["alert_id"],
            "expected_typology": alert["expected_typology"],
            "predicted_typology": packet["suspected_typology"],
            "typology_correct": alert["expected_typology"] == packet["suspected_typology"],
            "evidence_coverage": round(len(expected_evidence & actual_evidence) / len(expected_evidence), 2),
            "evidence_verified": packet["evidence_verification"]["passed"],
        })
    correct = sum(row["typology_correct"] for row in results)
    return {"cases": results, "summary": {"case_count": len(results), "typology_accuracy": round(correct / len(results), 2), "all_evidence_verified": all(row["evidence_verified"] for row in results)}}
