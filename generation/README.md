# Generation Service - LAW-KBS Graph RAG

## Giới thiệu

Generation Service là thành phần cuối cùng trong hệ thống Graph RAG, chịu trách nhiệm tạo ra câu trả lời chất lượng cao từ các tài liệu và entities được truy xuất từ knowledge graph.

**Chức năng chính:**
- Xây dựng prompt từ câu hỏi và context
- Gọi LLM để sinh câu trả lời
- Xử lý và refine output
- Mapping citations từ tài liệu gốc
- Validate và format kết quả


---

## Kiến trúc

### Architecture Pattern

Service sử dụng kết hợp ba patterns:

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
│   ├── llm_caller.py             # LLM integration
│   ├── response_processor.py     # Response refinement
│   ├── citation_mapper.py        # Citation extraction & mapping
│   └── validator.py              # Response validation
├── strategies/
│   ├── __init__.py
│   ├── llm_strategy.py           # Base strategy interface
│   ├── openai_strategy.py        # OpenAI implementation
│   ├── claude_strategy.py        # Claude implementation
│   └── local_llm_strategy.py     # Local LLM implementation (optional)
├── models/
│   ├── __init__.py
│   ├── schemas.py                # Request/Response models
│   ├── domain.py                 # Domain models
│   └── enums.py                  # Enumerations
├── utils/
│   ├── __init__.py
│   ├── cache.py                  # Caching utilities
│   ├── logger.py                 # Logging configuration
│   ├── exceptions.py             # Custom exceptions
│   ├── retry.py                  # Retry logic
│   └── constants.py              # Constants
├── config/
│   ├── __init__.py
│   ├── settings.py               # Configuration management
│   └── prompts/                  # Prompt templates
│       ├── default.txt
│       ├── summary.txt
│       └── technical.txt
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── main.py                       # Application entry point
├── requirements.txt              # Dependencies
├── .env.example                  # Environment variables template
├── docker-compose.yml            # Docker configuration
├── Dockerfile                    # Docker image
└── README.md                     # This file
```