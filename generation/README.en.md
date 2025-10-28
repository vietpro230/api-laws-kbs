# Generation Service - LAW-KBS Graph RAG

## Introduction

The Generation Service is the final component in the Graph RAG system, responsible for generating high-quality answers from documents and entities retrieved from the knowledge graph.

**Main Functions:**
- Builds prompts from questions and context
- Calls the LLM to generate an answer
- Processes and refines the output
- Maps citations from original documents
- Validates and formats the result

---

## Architecture

### Architecture Pattern

The service uses a combination of three patterns:

```
┌─────────────────────────────────────────────┐
│         API Layer (FastAPI)                 │
│    POST /api/v1/generation/generate         │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│      Service Layer (Business Logic)         │
│  - Generation Pipeline                      │
│  - Orchestration & Error Handling           │
├─────────────────────────────────────────────┤
│      Pipeline Steps (Sequential)            │
│  1. Prompt Builder (Strategy Pattern)       │
│  2. LLM Caller (Strategy Pattern)           │
│  3. Response Processor                      │
│  4. Citation Mapper                         │
│  5. Validator                               │
├─────────────────────────────────────────────┤
│      LLM Integration Layer                  │
│  - OpenAI Strategy                          │
│  - Claude Strategy                          │
│  - Local LLM Strategy                       │
├─────────────────────────────────────────────┤
│      Support Layers                         │
│  - Cache (Redis)                            │
│  - Logging                                  │
│  - Error Handling & Retry                   │
└─────────────────────────────────────────────┘
```

---

### Folder Structure

```
generation_service/
├── api/
│   ├── __init__.py
│   ├── routes.py                 # API endpoints
│   └── dependencies.py           # Dependency injection
├── services/
│   ├── __init__.py
│   ├── generation_pipeline.py    # Main pipeline orchestration
│   ├── prompt_builder.py         # Prompt construction
│   ├── llm_cal_
