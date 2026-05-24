# DealGraph AI — Synthetic Data Model

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
