"""
DealGraph AI — Synthetic Relationship Intelligence Dataset Generator (v2)

Purpose:
  Generate a richer private-capital CRM dataset for RAG, graph retrieval,
  metadata filtering, reranking, contextual compression, and evaluation.

Outputs under data/synthetic_seed/:
  companies.json
  contacts.json
  deals.json
  interactions.json
  relationship_edges.json
  documents.jsonl
  eval_questions.jsonl
  schema.md
"""

from __future__ import annotations

import argparse
import json
import random
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from faker import Faker


fake = Faker()


SECTORS = [
    "Fintech", "HealthTech", "Climate Tech", "Enterprise SaaS",
    "Consumer Tech", "Cybersecurity", "Deep Tech", "EdTech",
    "PropTech", "Logistics Tech", "AI Infrastructure", "Developer Tools",
]

COMPANY_STAGES = ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Growth"]
DEAL_STAGES = ["Lead", "Qualified", "Due Diligence", "Partner Meeting", "Term Sheet", "Closed Won", "Closed Lost", "Passed"]
DEAL_TYPES = ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Growth Equity"]
INTERACTION_TYPES = ["email", "meeting", "call", "linkedin_message", "event"]
RELATIONSHIP_STRENGTHS = ["weak", "moderate", "strong", "champion"]
VISIBILITY_GROUPS = ["team_alpha", "team_beta", "investment_committee", "restricted_partner_notes"]

TITLES = [
    "CEO", "CTO", "CFO", "COO", "VP Engineering", "VP Product",
    "Head of Growth", "Founder", "Co-Founder", "Partner",
    "Managing Director", "Principal", "Associate", "Director of Sales",
    "Chief Revenue Officer", "Head of Partnerships",
]

TEAM_MEMBERS = [
    {"id": "usr_001", "name": "Priya Mehta", "email": "priya@dealgraphvc.com", "team": "team_alpha"},
    {"id": "usr_002", "name": "James Okafor", "email": "james@dealgraphvc.com", "team": "team_alpha"},
    {"id": "usr_003", "name": "Sarah Chen", "email": "sarah@dealgraphvc.com", "team": "team_beta"},
    {"id": "usr_004", "name": "Marcus Webb", "email": "marcus@dealgraphvc.com", "team": "team_beta"},
    {"id": "usr_005", "name": "Leila Nazari", "email": "leila@dealgraphvc.com", "team": "investment_committee"},
]

TOPICS = [
    "ARR growth", "product roadmap", "team expansion", "GTM strategy",
    "technical architecture", "competitive landscape", "customer traction",
    "fundraising timeline", "board composition", "unit economics",
    "security review", "data room readiness", "enterprise adoption",
    "compliance workflow", "strategic partnerships",
]

NEXT_STEPS = [
    "Schedule follow-up in 2 weeks.",
    "Send term sheet draft by Friday.",
    "Intro to portfolio company for reference check.",
    "Review data room materials.",
    "Loop in technical partner for deep dive.",
    "Check back after Series B closes.",
    "Request updated financial model.",
    "Connect with reference customers.",
    "Share relevant portfolio operator.",
    "Prepare memo for investment committee.",
    "Ask founder for latest cohort retention numbers.",
]

QUESTION_TEMPLATES = [
    {
        "intent": "relationship_lookup",
        "question": "Who has the strongest relationship with {contact_name} at {company_name}?",
    },
    {
        "intent": "meeting_prep",
        "question": "Prep me for a meeting with {company_name}.",
    },
    {
        "intent": "deal_summary",
        "question": "Summarize the current status of the {deal_name} deal.",
    },
    {
        "intent": "follow_up_risk",
        "question": "Which recent follow-up is still open for {company_name}?",
    },
    {
        "intent": "sector_search",
        "question": "Find active {sector} deals with warm relationships.",
    },
]


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def rand_date(start_days_ago: int = 730, end_days_ago: int = 0) -> str:
    delta = random.randint(end_days_ago, start_days_ago)
    return (now_utc() - timedelta(days=delta)).date().isoformat()


def rand_datetime(start_days_ago: int = 730, end_days_ago: int = 0) -> str:
    delta = random.randint(end_days_ago, start_days_ago)
    dt = now_utc() - timedelta(
        days=delta,
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    return dt.replace(microsecond=0).isoformat()


def weighted_choice(items: list[tuple[Any, float]]) -> Any:
    values, weights = zip(*items)
    return random.choices(values, weights=weights, k=1)[0]


def generate_companies(n_companies: int) -> list[dict]:
    companies = []
    for _ in range(n_companies):
        sector = random.choice(SECTORS)
        company_name = f"{fake.company().replace(',', '').replace('.', '')} {random.choice(['AI', 'Labs', 'Tech', 'Systems', ''])}".strip()

        companies.append({
            "company_id": make_id("co"),
            "name": company_name,
            "sector": sector,
            "stage": random.choice(COMPANY_STAGES),
            "founded_year": random.randint(2010, 2024),
            "hq_city": fake.city(),
            "hq_country": weighted_choice([
                ("USA", 0.45), ("Canada", 0.15), ("UK", 0.10), ("Germany", 0.08),
                ("France", 0.05), ("Israel", 0.07), ("India", 0.05), ("Singapore", 0.05),
            ]),
            "headcount": random.choice([5, 12, 25, 50, 100, 200, 500, 1000]),
            "website": f"https://www.{fake.domain_name()}",
            "description": f"{sector} company building {fake.bs()}.",
            "linkedin_url": f"https://linkedin.com/company/{fake.slug()}",
            "last_interaction": rand_date(365, 0),
            "relationship_strength": weighted_choice([
                ("weak", 0.20), ("moderate", 0.35), ("strong", 0.30), ("champion", 0.15)
            ]),
            "tags": random.sample(
                ["portfolio", "prospect", "passed", "warm intro", "cold outreach", "referral", "strategic"],
                k=random.randint(1, 3),
            ),
            "created_at": rand_date(800, 300),
            "updated_at": rand_date(90, 0),
        })
    return companies


def generate_contacts(companies: list[dict], n_contacts: int) -> list[dict]:
    contacts = []
    company_ids = [c["company_id"] for c in companies]

    # Ensure every company has at least one contact.
    base_assignments = company_ids[:]
    while len(base_assignments) < n_contacts:
        base_assignments.append(random.choice(company_ids))
    random.shuffle(base_assignments)

    for company_id in base_assignments[:n_contacts]:
        first = fake.first_name()
        last = fake.last_name()
        owner = random.choice(TEAM_MEMBERS)
        contacts.append({
            "contact_id": make_id("ct"),
            "first_name": first,
            "last_name": last,
            "full_name": f"{first} {last}",
            "email": fake.email(),
            "linkedin_url": f"https://linkedin.com/in/{fake.slug()}",
            "title": random.choice(TITLES),
            "company_id": company_id,
            "location": f"{fake.city()}, {fake.country_code()}",
            "relationship_owner": owner["id"],
            "owner_team": owner["team"],
            "relationship_strength": weighted_choice([
                ("weak", 0.25), ("moderate", 0.35), ("strong", 0.25), ("champion", 0.15)
            ]),
            "last_interaction": rand_date(365, 0),
            "interaction_count": random.randint(1, 40),
            "notes": fake.paragraph(nb_sentences=2),
            "tags": random.sample(
                ["decision maker", "champion", "technical", "gatekeeper", "influencer", "warm", "operator", "investor"],
                k=random.randint(1, 3),
            ),
            "created_at": rand_date(800, 300),
            "updated_at": rand_date(90, 0),
        })
    return contacts


def generate_deals(companies: list[dict], contacts: list[dict], n_deals: int) -> list[dict]:
    contacts_by_company = defaultdict(list)
    for c in contacts:
        contacts_by_company[c["company_id"]].append(c["contact_id"])

    deals = []
    for _ in range(n_deals):
        company = random.choice(companies)
        stage = weighted_choice([
            ("Lead", 0.20), ("Qualified", 0.18), ("Due Diligence", 0.18),
            ("Partner Meeting", 0.12), ("Term Sheet", 0.08),
            ("Closed Won", 0.08), ("Closed Lost", 0.06), ("Passed", 0.10),
        ])
        deal_type = random.choice(DEAL_TYPES)
        deal_team = random.sample([t["id"] for t in TEAM_MEMBERS], k=random.randint(1, 3))
        company_contacts = contacts_by_company.get(company["company_id"], [])

        deals.append({
            "deal_id": make_id("dl"),
            "name": f"{company['name']} — {deal_type}",
            "company_id": company["company_id"],
            "deal_type": deal_type,
            "stage": stage,
            "amount_usd": random.choice([
                500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000,
                25_000_000, 50_000_000, 100_000_000,
            ]),
            "currency": "USD",
            "lead_partner": random.choice(deal_team),
            "deal_team": deal_team,
            "key_contacts": random.sample(
                company_contacts, k=min(len(company_contacts), random.randint(1, 3))
            ) if company_contacts else [],
            "created_at": rand_date(650, 30),
            "updated_at": rand_date(45, 0),
            "close_date": rand_date(180, 0) if stage in ["Closed Won", "Closed Lost"] else None,
            "sector": company["sector"],
            "priority": weighted_choice([("Low", 0.20), ("Medium", 0.45), ("High", 0.30), ("Critical", 0.05)]),
            "tags": random.sample(
                ["high priority", "founder led", "competitive", "exclusive", "warm intro", "board seat", "needs diligence"],
                k=random.randint(1, 3),
            ),
            "memo_url": f"https://drive.google.com/file/{uuid.uuid4().hex[:12]}",
        })
    return deals


def summarize_company(company: dict) -> str:
    return (
        f"{company['name']} is a {company['stage']} {company['sector']} company "
        f"headquartered in {company['hq_city']}, {company['hq_country']} with roughly "
        f"{company['headcount']} employees. {company['description']}"
    )


def fill_interaction_body(contact: dict, company: dict, deal: dict | None, itype: str) -> tuple[str, str]:
    topic = random.choice(TOPICS)
    summary = random.choice([
        f"They are seeing strong traction in {company['sector']} with {random.randint(20, 200)}% YoY growth.",
        f"The team is expanding rapidly and now has about {company['headcount']} employees.",
        f"Product is live with {random.randint(10, 500)} customers and {random.randint(60, 95)}% net revenue retention.",
        f"The founder has deep domain expertise and a prior leadership role at {fake.company()}.",
        f"The moat is based on proprietary workflow data, integrations, and customer switching costs.",
        f"Burn is approximately ${random.randint(200, 900)}K per month with {random.randint(9, 36)} months of runway.",
        f"They signed {random.randint(3, 20)} LOIs last quarter and have a strong enterprise pipeline.",
        f"The technical differentiation is meaningful, but the team still needs stronger security documentation.",
        f"NPS is {random.randint(45, 85)} and churn is below {random.randint(2, 9)}%.",
        f"The buyer persona is clear, but go-to-market motion still needs more proof.",
    ])
    next_step = random.choice(NEXT_STEPS)
    deal_context = f" This relates to {deal['name']} currently in {deal['stage']}." if deal else ""

    templates = {
        "meeting": [
            "Met with {contact} ({title}) at {company}. {summary}{deal_context} Next steps: {next_step}",
            "Partner meeting with {contact} from {company}. Discussed {topic}. {summary}{deal_context} Action item: {next_step}",
            "Diligence meeting at {company}. {contact} walked through {topic}. {summary}{deal_context}",
        ],
        "email": [
            "Email thread with {contact} about {topic}. {summary}{deal_context} Next: {next_step}",
            "Received update from {contact} at {company}. {summary}{deal_context}",
            "Follow-up email from {contact}. Asked for support on {topic}. {summary}{deal_context}",
        ],
        "call": [
            "Call with {contact} ({company}). {summary}{deal_context} Will reconnect after the next milestone.",
            "Reference call with {contact}. Discussed {topic}. {summary}{deal_context}",
        ],
        "linkedin_message": [
            "LinkedIn message from {contact} at {company}. {summary} They asked whether there is interest in {topic}.",
        ],
        "event": [
            "Met {contact} from {company} at an industry event. Discussed {topic}. {summary} Follow-up: {next_step}",
        ],
    }

    body = random.choice(templates.get(itype, templates["meeting"])).format(
        contact=contact["full_name"],
        title=contact["title"],
        company=company["name"],
        summary=summary,
        topic=topic,
        next_step=next_step,
        deal_context=deal_context,
    )
    return topic, body


def generate_interactions(companies: list[dict], contacts: list[dict], deals: list[dict], n_interactions: int) -> list[dict]:
    company_map = {c["company_id"]: c for c in companies}
    contacts_by_company = defaultdict(list)
    deals_by_company = defaultdict(list)

    for c in contacts:
        contacts_by_company[c["company_id"]].append(c)
    for d in deals:
        deals_by_company[d["company_id"]].append(d)

    interactions = []
    for _ in range(n_interactions):
        company = random.choice(companies)
        company_contacts = contacts_by_company[company["company_id"]]
        contact = random.choice(company_contacts)
        deal = random.choice(deals_by_company.get(company["company_id"], [None]))
        itype = random.choice(INTERACTION_TYPES)
        logged_by = random.choice(TEAM_MEMBERS)
        visibility = weighted_choice([
            ("team_alpha", 0.40), ("team_beta", 0.30),
            ("investment_committee", 0.20), ("restricted_partner_notes", 0.10),
        ])
        topic, body = fill_interaction_body(contact, company, deal, itype)

        participants = [contact["contact_id"]]
        if len(company_contacts) > 1 and random.random() > 0.65:
            participants.append(random.choice(company_contacts)["contact_id"])

        interactions.append({
            "interaction_id": make_id("ix"),
            "type": itype,
            "date": rand_datetime(540, 0),
            "company_id": company["company_id"],
            "contact_ids": list(dict.fromkeys(participants)),
            "deal_id": deal["deal_id"] if deal else None,
            "logged_by": logged_by["id"],
            "team_members_cc": random.sample([t["id"] for t in TEAM_MEMBERS], k=random.randint(0, 2)),
            "subject": f"{itype.replace('_', ' ').title()}: {company['name']} — {topic}",
            "body": body,
            "sentiment": weighted_choice([("positive", 0.55), ("neutral", 0.30), ("negative", 0.15)]),
            "tags": random.sample(
                ["diligence", "portfolio", "intro", "follow-up", "reference", "update", "fundraising", "meeting-prep"],
                k=random.randint(1, 3),
            ),
            "source_type": itype,
            "visibility": visibility,
            "created_at": rand_datetime(540, 0),
        })

    interactions.sort(key=lambda x: x["date"], reverse=True)
    return interactions


def strength_to_score(label: str) -> float:
    return {"weak": 0.25, "moderate": 0.50, "strong": 0.75, "champion": 0.95}.get(label, 0.40)


def generate_relationship_edges(contacts: list[dict], interactions: list[dict]) -> list[dict]:
    # Internal user -> contact edges
    edges = []
    seen = set()

    interaction_counts = defaultdict(int)
    last_dates = {}

    for ix in interactions:
        for contact_id in ix["contact_ids"]:
            key = (ix["logged_by"], contact_id)
            interaction_counts[key] += 1
            last_dates[key] = max(last_dates.get(key, ix["date"]), ix["date"])

    for contact in contacts:
        owner = contact["relationship_owner"]
        key = (owner, contact["contact_id"])
        count = max(contact["interaction_count"], interaction_counts.get(key, 0))
        score = min(0.99, strength_to_score(contact["relationship_strength"]) + min(count, 30) / 100)

        edge_key = (owner, contact["contact_id"], "owns_relationship")
        if edge_key in seen:
            continue
        seen.add(edge_key)
        edges.append({
            "edge_id": make_id("ed"),
            "from_id": owner,
            "from_type": "team_member",
            "to_id": contact["contact_id"],
            "to_type": "contact",
            "relationship_type": "owns_relationship",
            "strength_score": round(score, 3),
            "interaction_count": count,
            "last_interaction": last_dates.get(key, contact["last_interaction"]),
        })

    # Contact -> contact edges based on co-participation in interactions
    co_counts = defaultdict(int)
    co_last_dates = {}
    for ix in interactions:
        ids = ix["contact_ids"]
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                pair = tuple(sorted([ids[i], ids[j]]))
                co_counts[pair] += 1
                co_last_dates[pair] = max(co_last_dates.get(pair, ix["date"]), ix["date"])

    for (a, b), count in co_counts.items():
        edges.append({
            "edge_id": make_id("ed"),
            "from_id": a,
            "from_type": "contact",
            "to_id": b,
            "to_type": "contact",
            "relationship_type": "co_interaction",
            "strength_score": round(min(0.95, 0.30 + count * 0.08), 3),
            "interaction_count": count,
            "last_interaction": co_last_dates[(a, b)],
        })

    return edges


def generate_documents(companies: list[dict], contacts: list[dict], deals: list[dict], interactions: list[dict]) -> list[dict]:
    company_map = {c["company_id"]: c for c in companies}
    contact_map = {c["contact_id"]: c for c in contacts}
    deal_map = {d["deal_id"]: d for d in deals}

    docs = []

    # Company profile docs
    for company in companies:
        docs.append({
            "doc_id": make_id("doc"),
            "doc_type": "company_profile",
            "date": company["updated_at"],
            "company_id": company["company_id"],
            "deal_id": None,
            "contact_ids": [],
            "visibility": "team_alpha",
            "title": f"Company profile: {company['name']}",
            "text": summarize_company(company),
            "metadata": {
                "sector": company["sector"],
                "stage": company["stage"],
                "source": "crm_company",
            },
        })

    # Interaction docs, the primary RAG corpus.
    for ix in interactions:
        company = company_map[ix["company_id"]]
        names = [contact_map[cid]["full_name"] for cid in ix["contact_ids"] if cid in contact_map]
        deal = deal_map.get(ix["deal_id"]) if ix.get("deal_id") else None

        docs.append({
            "doc_id": make_id("doc"),
            "doc_type": ix["source_type"],
            "date": ix["date"],
            "company_id": ix["company_id"],
            "deal_id": ix["deal_id"],
            "contact_ids": ix["contact_ids"],
            "visibility": ix["visibility"],
            "title": ix["subject"],
            "text": ix["body"],
            "metadata": {
                "company_name": company["name"],
                "contact_names": names,
                "deal_name": deal["name"] if deal else None,
                "sector": company["sector"],
                "source": "interaction",
                "sentiment": ix["sentiment"],
                "tags": ix["tags"],
                "logged_by": ix["logged_by"],
            },
        })

    return docs


def generate_eval_questions(companies: list[dict], contacts: list[dict], deals: list[dict]) -> list[dict]:
    contacts_by_company = defaultdict(list)
    deals_by_company = defaultdict(list)
    for c in contacts:
        contacts_by_company[c["company_id"]].append(c)
    for d in deals:
        deals_by_company[d["company_id"]].append(d)

    eval_items = []
    for company in random.sample(companies, k=min(30, len(companies))):
        company_contacts = contacts_by_company.get(company["company_id"], [])
        company_deals = deals_by_company.get(company["company_id"], [])
        contact = random.choice(company_contacts) if company_contacts else None
        deal = random.choice(company_deals) if company_deals else None

        template = random.choice(QUESTION_TEMPLATES)
        question = template["question"].format(
            contact_name=contact["full_name"] if contact else "the key contact",
            company_name=company["name"],
            deal_name=deal["name"] if deal else f"{company['name']} opportunity",
            sector=company["sector"],
        )

        expected_sources = []
        if deal:
            expected_sources.append({"type": "deal", "id": deal["deal_id"]})
        if contact:
            expected_sources.append({"type": "contact", "id": contact["contact_id"]})
        expected_sources.append({"type": "company", "id": company["company_id"]})

        eval_items.append({
            "question_id": make_id("q"),
            "intent": template["intent"],
            "question": question,
            "expected_entities": expected_sources,
            "metadata_filters": {
                "company_id": company["company_id"],
                "sector": company["sector"],
                "deal_id": deal["deal_id"] if deal else None,
            },
        })
    return eval_items


SCHEMA_MD = """# DealGraph AI — Synthetic Data Model

## Purpose

This dataset is built to test senior-level RAG system design, not just a chatbot demo.

It supports:

- structured CRM lookup
- unstructured interaction retrieval
- metadata filtering
- vector search
- graph relationship search
- reranking
- contextual compression
- permission-aware retrieval
- evaluation with expected entities

## Entities

| File | Description |
|---|---|
| companies.json | CRM company records |
| contacts.json | People connected to each company |
| deals.json | Investment opportunities |
| interactions.json | Email, meeting, call, LinkedIn, and event records |
| relationship_edges.json | Graph edges between team members and contacts |
| documents.jsonl | RAG-ready document corpus |
| eval_questions.jsonl | Evaluation questions with expected entities |

## Important Retrieval Metadata

- company_id
- deal_id
- contact_ids
- sector
- source_type/doc_type
- date
- visibility
- logged_by
- sentiment
- tags

## Why These Fields Matter

A production RAG system should not rely on vector similarity alone. In private-capital CRM search, users often ask entity-specific and permission-sensitive questions. Metadata filters reduce the search space before vector search, making answers more relevant, safer, and faster.
"""


def write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row) + "\n")


def dataset_summary(companies: list[dict], contacts: list[dict], deals: list[dict], interactions: list[dict], edges: list[dict], docs: list[dict], eval_items: list[dict]) -> None:
    print("\n── Dataset Summary ──────────────────────────────")
    print(f"  Companies:           {len(companies)}")
    print(f"  Contacts:            {len(contacts)}")
    print(f"  Deals:               {len(deals)}")
    print(f"  Interactions:        {len(interactions)}")
    print(f"  Relationship edges:  {len(edges)}")
    print(f"  RAG documents:       {len(docs)}")
    print(f"  Eval questions:      {len(eval_items)}")
    print(f"  Total RAG text chars: {sum(len(d['text']) for d in docs):,}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/synthetic_seed")
    parser.add_argument("--companies", type=int, default=50)
    parser.add_argument("--contacts", type=int, default=200)
    parser.add_argument("--deals", type=int, default=150)
    parser.add_argument("--interactions", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    Faker.seed(args.seed)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating DealGraph AI synthetic dataset...")

    companies = generate_companies(args.companies)
    contacts = generate_contacts(companies, args.contacts)
    deals = generate_deals(companies, contacts, args.deals)
    interactions = generate_interactions(companies, contacts, deals, args.interactions)
    edges = generate_relationship_edges(contacts, interactions)
    docs = generate_documents(companies, contacts, deals, interactions)
    eval_items = generate_eval_questions(companies, contacts, deals)

    write_json(output_dir / "companies.json", companies)
    write_json(output_dir / "contacts.json", contacts)
    write_json(output_dir / "deals.json", deals)
    write_json(output_dir / "interactions.json", interactions)
    write_json(output_dir / "relationship_edges.json", edges)
    write_jsonl(output_dir / "documents.jsonl", docs)
    write_jsonl(output_dir / "eval_questions.jsonl", eval_items)
    (output_dir / "schema.md").write_text(SCHEMA_MD, encoding="utf-8")

    dataset_summary(companies, contacts, deals, interactions, edges, docs, eval_items)
    print("\n✅ Dataset generation complete.")


if __name__ == "__main__":
    main()
