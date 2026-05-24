# DealGraph AI

DealGraph AI is a portfolio-grade AI engineering project that demonstrates how to build a relationship-intelligence RAG system for private capital CRM workflows.

The system combines structured CRM data, unstructured meeting and email notes, vector search, graph-style relationship reasoning, reranking, contextual compression, and LLM agents.

## Problem

Private capital teams work across emails, meetings, deal notes, company records, and relationship networks. The challenge is not only storing that information, but retrieving the right context at the right time.

Deal teams often need to answer questions like:

- Who has the strongest relationship with this investor or founder?
- What happened in our last few meetings with this company?
- Which deals have gone cold?
- Who can provide a warm introduction?
- What should I know before tomorrow's meeting?

## Solution

DealGraph AI helps users ask natural language questions over CRM records, meeting notes, email summaries, and relationship data.

The system returns grounded answers with citations, relationship context, and recommended next actions.

## Core Features

- Hybrid RAG over CRM records, emails, and meeting notes
- Metadata-aware retrieval
- Relationship graph search
- Warm introduction path finder
- Meeting prep agent
- CRM writeback agent with confirmation
- Reranking and contextual compression
- Evaluation for hallucination, factual consistency, and retrieval quality

## Tech Stack

- Backend: FastAPI, Python
- Frontend: React, TypeScript, Vite
- Vector Search: Qdrant
- Database: PostgreSQL
- Graph Layer: Neo4j or Postgres-based graph tables
- Agent Layer: LangGraph
- Evaluation: RAGAS, DeepEval, custom eval scripts
- Deployment: Docker

## Architecture Decisions

DealGraph AI is designed as a relationship-intelligence retrieval system, not a simple chatbot over documents.

The system separates data into structured CRM records, unstructured interaction notes, relationship graph edges, and evaluation examples.

Key decisions:

1. Use metadata filtering before vector search to reduce irrelevant and unauthorized context.
2. Use hybrid retrieval because CRM search requires both semantic similarity and exact entity matching.
3. Use graph retrieval for warm introductions and relationship ownership questions.
4. Use reranking to improve precision after broad candidate retrieval.
5. Use contextual compression to reduce token usage and improve factual grounding.
6. Use citations and evaluation to make the system measurable and trustworthy.
7. Use confirmation and audit logs before CRM writeback.

## Data Access Design

The backend separates raw synthetic CRM records from RAG-ready documents.

Structured records such as companies, contacts, deals, and relationships are loaded from JSON files. RAG-ready interaction notes are loaded from JSONL because each line can be treated as an independent retrievable document.

This separation matters because production AI systems often need to combine structured lookup, metadata filtering, and semantic search. A user question may require exact company or deal lookup before vector retrieval begins.

The data preview API is intentionally filterable by fields like company_id, deal_id, visibility, doc_type, and source_type. These filters prepare the system for permission-aware retrieval, where the model only receives context the user is allowed to access.

## Current Retrieval Features

The project currently supports a baseline local retrieval endpoint:

```text
GET /api/search/documents?q=fundraising%20timeline&limit=5

DealGraph AI now includes a provider-neutral LLM layer.

Supported providers:

- `mock`
- `openai`
- `anthropic`

The RAG endpoint can use the default provider from environment variables or accept a per-request override.

Example request:

```json
{
  "question": "What did the team discuss about fundraising timeline?",
  "limit": 5,
  "llm_provider": "mock"
}
```

The provider abstraction keeps the RAG pipeline independent from a specific model vendor and makes it easier to test, evaluate, and compare model behavior.
