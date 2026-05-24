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