# Mini Investigation Agent

A local, auditable demo of an AI-investigation workflow for financial-crime alerts. It uses **only synthetic data** and runs with Python's standard library—no API key, paid account, or external service is required.

This is deliberately an investigation-assistance demo, not a system for making real compliance decisions.

## What it demonstrates

- A fixed investigation workflow: retrieve facts -> assess risk -> verify evidence -> write a memo.
- Exact evidence citations (`transaction_id`s) for every risk finding.
- A conservative `insufficient_evidence` outcome for ordinary lookalikes.
- A simple rules baseline and a small regression evaluation suite.

## Run it

Open this folder in VS Code, then run:

```bash
cd /Users/ananyabadagi/Documents/Codex/2026-11-02/i-wa/polarisk-investigation-agent
python3 -m investigator.cli seed
python3 -m investigator.cli list-cases
python3 -m investigator.cli investigate ALERT-STRUCT-001
python3 -m investigator.cli evaluate
python3 -m unittest discover -s tests -v
```

The `seed` command creates `data/polarisk_demo.db`, a local SQLite database. It is safe to delete; rerun `seed` to recreate it.

## Example output

`investigate` prints a JSON investigation packet containing:

- `risk_level` and `suspected_typology`
- cited evidence and a separate evidence-verification result
- an alternative explanation
- a human-review recommendation
- a readable memo

## Architecture

```text
Alert
  -> SQL data retrieval
  -> deterministic pattern analysis
  -> evidence verification
  -> structured investigation memo
```

In a production version, the pattern-analysis step could call an LLM with structured output. The local version is deterministic so that every decision is reproducible and easy to evaluate.

## Good next extensions

1. Add a LangGraph workflow around the existing stages.
2. Add an LLM adapter that is allowed to explain facts, but not invent evidence.
3. Add synthetic scenario generation and adversarial lookalikes.
4. Replace the CLI with a FastAPI endpoint and a review queue.
