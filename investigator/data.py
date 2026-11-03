from __future__ import annotations

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = PROJECT_ROOT / "data" / "polarisk_demo.db"


CASES = [
    {
        "alert_id": "ALERT-STRUCT-001",
        "customer_id": "CUST-100",
        "description": "Five near-threshold international wires in three days.",
        "expected_typology": "structuring",
        "expected_evidence": "TX-1001,TX-1002,TX-1003,TX-1004,TX-1005",
    },
    {
        "alert_id": "ALERT-LAYER-001",
        "customer_id": "CUST-200",
        "description": "Large incoming payment followed by rapid international dispersal.",
        "expected_typology": "rapid_pass_through",
        "expected_evidence": "TX-2001,TX-2002,TX-2003",
    },
    {
        "alert_id": "ALERT-SALARY-001",
        "customer_id": "CUST-300",
        "description": "Large regular salary payment that looks unusual in isolation.",
        "expected_typology": "insufficient_evidence",
        "expected_evidence": "TX-3001,TX-3002,TX-3003",
    },
    {
        "alert_id": "ALERT-TUITION-001",
        "customer_id": "CUST-400",
        "description": "Cross-border tuition payment supported by a known education payee.",
        "expected_typology": "insufficient_evidence",
        "expected_evidence": "TX-4001,TX-4002",
    },
]


CUSTOMERS = [
    ("CUST-100", "Ravi Mehta", "India", "individual", "Medium", "Retail importer"),
    ("CUST-200", "Northstar Trading Ltd", "Singapore", "business", "High", "General trading"),
    ("CUST-300", "Aisha Khan", "India", "individual", "Low", "Software engineer"),
    ("CUST-400", "Nisha Rao", "India", "individual", "Low", "Graduate student"),
]


TRANSACTIONS = [
    ("TX-1001", "CUST-100", "2026-09-01", "outbound", 9500.00, "USD", "Orchid Consulting", "AE", "Consulting fee"),
    ("TX-1002", "CUST-100", "2026-09-02", "outbound", 9400.00, "USD", "Delta Imports", "SG", "Consulting fee"),
    ("TX-1003", "CUST-100", "2026-09-02", "outbound", 9600.00, "USD", "Bluewave Services", "HK", "Consulting fee"),
    ("TX-1004", "CUST-100", "2026-09-03", "outbound", 9300.00, "USD", "Nile Trading", "AE", "Consulting fee"),
    ("TX-1005", "CUST-100", "2026-09-03", "outbound", 9700.00, "USD", "Arcadia Logistics", "SG", "Consulting fee"),
    ("TX-2001", "CUST-200", "2026-08-10", "inbound", 80000.00, "USD", "Baltic Metals", "DE", "Invoice settlement"),
    ("TX-2002", "CUST-200", "2026-08-11", "outbound", 42000.00, "USD", "Sunrise Ventures", "AE", "Supplier payment"),
    ("TX-2003", "CUST-200", "2026-08-12", "outbound", 35000.00, "USD", "Pacific Link", "HK", "Supplier payment"),
    ("TX-3001", "CUST-300", "2026-07-31", "inbound", 18000.00, "USD", "Acme Software Payroll", "US", "Monthly salary"),
    ("TX-3002", "CUST-300", "2026-08-31", "inbound", 18000.00, "USD", "Acme Software Payroll", "US", "Monthly salary"),
    ("TX-3003", "CUST-300", "2026-09-30", "inbound", 18000.00, "USD", "Acme Software Payroll", "US", "Monthly salary"),
    ("TX-4001", "CUST-400", "2026-08-15", "outbound", 24000.00, "USD", "University of Glasgow", "GB", "Tuition - fall term"),
    ("TX-4002", "CUST-400", "2026-08-16", "outbound", 1200.00, "USD", "University of Glasgow", "GB", "Student accommodation deposit"),
]


def connect(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def seed_database(db_path: Path = DEFAULT_DB) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    with connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY, name TEXT, country TEXT, customer_type TEXT,
                risk_rating TEXT, occupation TEXT
            );
            CREATE TABLE transactions (
                transaction_id TEXT PRIMARY KEY, customer_id TEXT, transaction_date TEXT,
                direction TEXT, amount REAL, currency TEXT, counterparty TEXT,
                counterparty_country TEXT, description TEXT
            );
            CREATE TABLE alerts (
                alert_id TEXT PRIMARY KEY, customer_id TEXT, description TEXT,
                expected_typology TEXT, expected_evidence TEXT
            );
            """
        )
        connection.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)", CUSTOMERS)
        connection.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", TRANSACTIONS)
        connection.executemany("INSERT INTO alerts VALUES (?, ?, ?, ?, ?)", [tuple(case.values()) for case in CASES])
    return db_path
