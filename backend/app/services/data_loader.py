from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "backend" / "data" / "synthetic_seed"


class DataFileNotFoundError(FileNotFoundError):
    """Raised when an expected synthetic data file is missing."""


def _ensure_data_dir_exists() -> None:
    if not DATA_DIR.exists():
        raise DataFileNotFoundError(
            f"Data directory not found: {DATA_DIR}. "
            "Run `python scripts/generate_data.py` from the project root first."
        )


def _load_json(filename: str) -> list[dict[str, Any]]:
    _ensure_data_dir_exists()

    path = DATA_DIR / filename

    if not path.exists():
        raise DataFileNotFoundError(
            f"Missing data file: {path}. "
            "Run `python scripts/generate_data.py` from the project root."
        )

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Expected {filename} to contain a JSON list.")

    return data


def _load_jsonl(filename: str) -> list[dict[str, Any]]:
    _ensure_data_dir_exists()

    path = DATA_DIR / filename

    if not path.exists():
        raise DataFileNotFoundError(
            f"Missing data file: {path}. "
            "Run `python scripts/generate_data.py` from the project root."
        )

    records: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSONL in {filename} at line {line_number}: {exc}"
                ) from exc

            if not isinstance(record, dict):
                raise ValueError(
                    f"Expected each JSONL line in {filename} to be an object. "
                    f"Line {line_number} was {type(record).__name__}."
                )

            records.append(record)

    return records


def load_companies() -> list[dict[str, Any]]:
    return _load_json("companies.json")


def load_contacts() -> list[dict[str, Any]]:
    return _load_json("contacts.json")


def load_deals() -> list[dict[str, Any]]:
    return _load_json("deals.json")


def load_interactions() -> list[dict[str, Any]]:
    return _load_json("interactions.json")


def load_relationship_edges() -> list[dict[str, Any]]:
    return _load_json("relationship_edges.json")


def load_documents() -> list[dict[str, Any]]:
    return _load_jsonl("documents.jsonl")


def load_eval_questions() -> list[dict[str, Any]]:
    return _load_jsonl("eval_questions.jsonl")


def load_schema_markdown() -> str:
    _ensure_data_dir_exists()

    path = DATA_DIR / "schema.md"

    if not path.exists():
        raise DataFileNotFoundError(
            f"Missing schema file: {path}. "
            "Run `python scripts/generate_data.py` from the project root."
        )

    return path.read_text(encoding="utf-8")


def load_dataset_summary() -> dict[str, Any]:
    companies = load_companies()
    contacts = load_contacts()
    deals = load_deals()
    interactions = load_interactions()
    relationships = load_relationship_edges()
    documents = load_documents()
    eval_questions = load_eval_questions()

    return {
        "data_dir": str(DATA_DIR),
        "counts": {
            "companies": len(companies),
            "contacts": len(contacts),
            "deals": len(deals),
            "interactions": len(interactions),
            "relationship_edges": len(relationships),
            "documents": len(documents),
            "eval_questions": len(eval_questions),
        },
        "sample_ids": {
            "company_id": companies[0].get("company_id") if companies else None,
            "contact_id": contacts[0].get("contact_id") if contacts else None,
            "deal_id": deals[0].get("deal_id") if deals else None,
            "interaction_id": interactions[0].get("interaction_id") if interactions else None,
            "doc_id": documents[0].get("doc_id") if documents else None,
        },
    }