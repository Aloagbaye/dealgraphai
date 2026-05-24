from app.services.data_loader import (
    load_companies,
    load_contacts,
    load_deals,
    load_interactions,
    load_relationship_edges,
    load_documents,
    load_eval_questions,
    load_dataset_summary,
)


def main() -> None:
    print("Running data loader smoke test...")

    companies = load_companies()
    contacts = load_contacts()
    deals = load_deals()
    interactions = load_interactions()
    relationships = load_relationship_edges()
    documents = load_documents()
    eval_questions = load_eval_questions()
    summary = load_dataset_summary()

    assert len(companies) > 0, "No companies loaded"
    assert len(contacts) > 0, "No contacts loaded"
    assert len(deals) > 0, "No deals loaded"
    assert len(interactions) > 0, "No interactions loaded"
    assert len(relationships) > 0, "No relationship edges loaded"
    assert len(documents) > 0, "No documents loaded"
    assert len(eval_questions) > 0, "No eval questions loaded"

    print("Dataset summary:")
    print(summary)
    print("✅ Data loader smoke test passed.")


if __name__ == "__main__":
    main()