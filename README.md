# Sarathi AI — Full AI Intelligence Architecture
### PCMC WhatsApp AI Chatbot & Civic Intelligence Platform
> **Enterprise-Grade AI/NLP/ML/Voice/Vision/GIS/Governance Platform**  
> Aligned with PCMC RFP Scope of Work (*Sections 1.2.2, 1.2.4–1.2.15, 2.1–2.4*)

---

## 🏛️ Executive Architecture Overview

**Sarathi AI** is an omnichannel, citizen-centric AI intelligence suite engineered specifically for the **Pimpri Chinchwad Municipal Corporation (PCMC)**. Designed to serve millions of citizens round-the-clock via WhatsApp and municipal portals, it unifies Generative AI, Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP) integrations, Multilingual Indic Voice/NLP, Computer Vision, and Geospatial Intelligence into a resilient, DPDP-compliant municipal service engine.

```
Citizen (WhatsApp / Web)
         │
         ▼
[ voice/audio_preprocessing ] ──► [ voice/stt ] 
         │ (Audio to Text)
         ▼
[ nlp/transliteration ] ─────────► [ nlp/language_detection ]
         │ (Roman Marathi -> Devanagari)
         ▼
[ moderation/pii_masking ] ──────► [ moderation/profanity_filter ]
         │ (DPDP Act Compliance: Redact Aadhaar/Phone/Bank)
         ▼
[ orchestration/workflows ] ◄───► [ orchestration/agents ]
         │                                │
         │                                ├──► [ orchestration/human_handoff ]
         │                                │    (Routes to PCMC Call Center if
         │                                │     triggered by governance/escalation)
         │
 ┌───────┴─────────────────────────────────────────────┐
 │                                                     │
 ▼                                                     ▼
[ rag/hybrid_search + reranking ]             [ mcp/servers/* ]
 (Knowledge Base, Policies, Schemes)           (Live ERP, Water, Tax, Grievance, GIS)
 │                                                     │
 └───────────────────────┬─────────────────────────────┘
                         │
                         ▼
           [ llm/response_generation ]
           (OpenAI / Azure / Gemini)
                         │
                         ▼
           [ governance/hallucination_control ]
           (Fact-check vs context & confidence score)
                         │
                         ▼
           [ voice/tts ] (Optional Voice Note)
                         │
                         ▼
        Citizen Response Delivered (WhatsApp)
                         │
                         ▼
           [ analytics/ai_usage_tracking ] 
           + [ governance/audit_logs ]
```

---

## 📂 Detailed Folder Structure & Module Catalog

### 1. `shared/` — Common Cross-Cutting Concerns
*Enterprise foundational utilities shared across all sub-services to prevent circular dependencies.*
- **`config/`**: Central environment settings, YAML/Pydantic configurations, and feature flags.
- **`logging/`**: Structured JSON logging, correlation IDs, and distributed tracing across microservices.
- **`auth/`**: Token verification, API key rotation, PCMC service account authentication.
- **`utils/`**: Standard string sanitizers, Marathi text formatters, phone/ID validators, datetime utilities.
- **`exceptions/`**: Domain-specific error types (e.g., `RateLimitException`, `HallucinationThresholdExceeded`, `MCPConnectionError`).

### 2. `orchestration/` — Agent & Conversation Orchestration
*Aligned with RFP Sec 1.2.2 & 1.2.3-C (Agent framework, Prompt orchestration, Human handoff)*
- **`agents/`**: Autonomous sub-agents (Grievance Agent, Tax & Billing Agent, Scheme Discovery Agent, General Q&A Agent).
- **`workflows/`**: Deterministic state-machine workflows for structured municipal processes (e.g., Birth Certificate application, RTS/RTI flows).
- **`human_handoff/`**: **Runtime Handoff & Session Transfer Layer** (RFP 1.2.3-C). Locks bot interactions, packages multi-turn dialogue history with an AI-generated summary, routes session to the PCMC Sarathi Call Center / Live Operator portal, and handles operator release back to bot.
- **`session_context/`**: Multi-turn conversation history, slot filling, and cross-session citizen state persistence.
- **`prompts/`**: Base system prompts, persona guidelines (official PCMC tone in Marathi/English), and role definitions.
- **`config/`**: Orchestration rules, agent routing logic, and timeout thresholds.

### 3. `nlp/` — Indic & Multilingual Natural Language Processing
*Aligned with RFP Sec 1.2.2 & 1.2.9 (Multilingual: Marathi, English, Hindi; Intent & Entity Extraction)*
- **`transliteration/`**: Converts Romanized Marathi (Hinglish/Minglish like *"pani bill kiti baki ahe"*) into standard Marathi Devanagari text for accurate parsing.
- **`intent_detection/`**: Zero-shot and fine-tuned classifiers identifying civic intents (grievance lodging, bill enquiry, ward office details, etc.).
- **`entity_extraction/`**: Named Entity Recognition (NER) for Consumer IDs, Property IDs, Ward Numbers, Application Numbers, Dates, and Pincodes.
- **`language_detection/`**: Real-time language identification across Marathi, Hindi, English, and regional dialects.
- **`translation/`**: Bidirectional translation layer between Indian regional languages and English.
- **`sentiment_analysis/`**: Citizen sentiment detector for identifying distressed, urgent, or dissatisfied inquiries.
- **`service_discovery/`**: Semantic intent-to-service mapper connecting vague citizen questions to exact municipal departments and RTS schemes.

### 4. `voice/` — WhatsApp Audio & Speech Intelligence
*Aligned with RFP Sec 1.2.9 (Voice Services: STT, TTS, Voice Note Understanding)*
- **`audio_preprocessing/`**: WhatsApp voice note converter (`.ogg`/Opus to `.wav`), Voice Activity Detection (VAD), and background noise reduction for outdoor street recordings.
- **`stt/`**: Speech-to-Text pipelines utilizing Indic-specialized models (Bhashini, Whisper, Azure Speech) optimized for Marathi accents.
- **`tts/`**: Text-to-Speech synthesis generating natural, pleasant Marathi and English voice notes for citizen audio replies.
- **`audio_understanding/`**: End-to-end audio emotion and tone classifier.

### 5. `document_ai/` — Vision, OCR & Document Verification
*Aligned with RFP Sec 1.2.10 (OCR, Document Reading, Image Understanding, Verification)*
- **`ocr/`**: High-accuracy OCR engine for scanned PDF forms, handwritten Marathi/English documents, and utility bills.
- **`document_reading/`**: Structured key-value pair and table extraction from uploaded proofs (Electricity bill, Index-II, Aadhaar, PAN).
- **`image_understanding/`**: Vision models for analyzing civic grievance photos (potholes, garbage dumps, broken streetlights, water leakages).
- **`verification/`**: Document completeness and validity verification to prevent invalid application submissions.

### 6. `rag/` & `vector_db/` — Hybrid Knowledge Retrieval Engine
*Aligned with RFP Sec 1.2.2 & 1.2.8 (RAG Framework, Vector Database, AI Searchable Repository)*
- **`rag/ingestion/`**: Automated data loaders for PCMC government resolutions (GRs), gazettes, citizen charters, and FAQs.
- **`rag/chunking/`**: Context-preserving semantic chunking tuned for municipal legal clauses and procedural documents.
- **`rag/embeddings/`**: Multilingual dense embedding generators (e.g., text-embedding-3, Indic-BERT).
- **`rag/hybrid_search/`**: Reciprocal Rank Fusion (RRF) blending lexical keyword search (BM25) with vector similarity search for exact circular number lookups.
- **`rag/reranking/`**: Cross-encoder re-ranking layer ensuring only the most relevant, legally binding municipal information reaches the LLM.
- **`rag/retrieval/`**: Context retrieval orchestration with metadata filtering (by Department, Ward, or Date).
- **`vector_db/`**: Connection management, indexing strategies (HNSW/IVF), schemas, and database migrations for Qdrant / PgVector / Milvus.

### 7. `mcp/` — Model Context Protocol (PCMC Core Integrations)
*Aligned with RFP Sec 1.2.2 & 1.2.13 (Integration with ERP, Property Tax, Water Billing, Grievance, GIS, Payments)*
- **`servers/property_tax/`**: Real-time property tax dues enquiry, receipt download, and assessment tracking.
- **`servers/water_billing/`**: Water meter consumption, outstanding bill fetch, and billing complaint logging.
- **`servers/grievance_system/`**: Direct bi-directional integration with PCMC's central grievance ticketing system.
- **`servers/gis_platform/`**: Integration with PCMC's GIS server for spatial boundary and asset queries.
- **`servers/payment_gateway/`**: Generation of secure payment links, status callbacks, and reconciliation verification.
- **`servers/document_repository/`**: Secure document archival and retrieval bridge.
- **`tools/` & `config/`**: MCP tool definitions, JSON-RPC protocol interfaces, and authentication handlers.

### 8. `llm/` — Foundation Models & Prompt Engineering
*Aligned with RFP Sec 1.2.2 (OpenAI, Azure OpenAI, Gemini enterprise models)*
- **`providers/`**: Pluggable adapters for Azure OpenAI, Google Cloud Gemini, and OpenAI with automatic fallback and load balancing.
- **`prompt_templates/`**: Dynamic Few-Shot prompt templates with context injection and safety guardrails.
- **`response_generation/`**: Streaming response generator formatted for WhatsApp constraints (bolding, lists, emojis, character limits).
- **`summarization/`**: Multi-turn dialogue summarization for operator handoff and ticket logging.
- **`evaluation/`**: **Offline Prompt & Model Benchmark Lab** (A/B testing prompt versions, comparing LLM provider latencies vs quality, token efficiency tests *prior to deployment*).

### 9. `ml_services/` — Applied Civic Machine Learning Models
*Aligned with RFP Sec 1.2.2 & 1.2.5 (Complaint Categorization, Prioritization, Duplicate Detection)*
- **`complaint_categorization/`**: Multi-class text/image classifier mapping complaints to 30+ municipal categories.
- **`complaint_prioritization/`**: Urgency scoring based on safety hazards, weather conditions, or public health emergencies.
- **`department_mapping/`**: Accurate routing to appropriate Ward Executive Engineers and Department Heads.
- **`duplicate_detection/`**: Spatial + semantic deduplication preventing repeated complaint tickets for the same civic issue.
- **`model_registry/`**: Model versioning, weights storage, and artifact tracking.
- **`training_pipeline/`**: Continuous re-training pipelines using citizen feedback and resolved complaints data.

### 10. `geo_intelligence/` — GIS & Spatial AI
*Aligned with RFP Sec 1.2.12 (Location capture, Geo-tagged complaints, Ward mapping, Heat maps, Routing)*
- **`location_capture/`**: Parsing WhatsApp GPS pins and reverse geocoding to PCMC landmark names.
- **`ward_zone_mapping/`**: Polygon point-in-polygon verification mapping GPS coordinates to PCMC's 8 administrative zones and 32 election wards.
- **`asset_mapping/`**: Nearest civic asset identification (Gardens, Hospitals, Dispensaries, BRT stops, Schools).
- **`heat_maps/`**: Density clustering of grievances to highlight infrastructure degradation hotspots.
- **`routing/`**: Location-aware complaint routing to the beat officer or field technician.

### 11. `moderation/` — Runtime In-Flight Guardrails & Safety Filters
*Aligned with RFP Sec 1.2.11 & 1.2.15 (In-line content safety, PII protection, DPDP Act)*  
> **Scope**: Executes synchronously on every incoming user query and outgoing model response before transmission.
- **`pii_masking/`**: Client/edge sanitization of citizen Aadhaar, PAN, phone numbers, and bank details before passing data to external LLMs (Mandatory under India's Digital Personal Data Protection Act - DPDP).
- **`profanity_filter/`**: Marathi, Hindi, and English abusive language detection and respectful boundary enforcement.
- **`content_moderation/`**: Filtering political, religious hate speech, defamatory content, or off-topic dialogue.
- **`safety_controls/`**: Defense against Prompt Injections, Jailbreaking, and system prompt leakage.

### 12. `governance/` — Policy, Compliance, Audit & Post-Inference Controls
*Aligned with RFP Sec 1.2.11 & 1.2.15 (Hallucination Control, Audit Trail, Human Escalation Rules)*  
> **Scope**: Enforces municipal oversight, truthfulness verification, escalation detection, and compliance auditing.
- **`hallucination_control/`**: Real-time context grounding verification (RAG-Triad check) preventing generation of fake circulars or wrong contact numbers.
- **`escalation/`**: **Trigger Detection & Rule Engine**. Analyzes sentiment decay, repeated unanswered questions (e.g., >2 failures), or high-severity citizen distress to issue an escalation event to `orchestration/human_handoff/`.
- **`prompt_logging/`**: Immutable logging of prompts, system contexts, token consumption, and response metadata.
- **`audit_logs/`**: Cryptographically verifiable audit trail for CERT-In, legal RTI compliance, and government scrutiny.
- **`evaluations/`**: **Production Quality & Compliance Benchmark Suite**. Continuous evaluation of live RAG faithfulness, answer relevancy, toxicity regression, and DPDP compliance auditing.

### 13. `knowledge_base/` — Municipal Repository & Ownership
*Aligned with RFP Sec 1.2.8 (FAQ, Service KB, Circulars, Ownership Docs)*
- **`faq/`**: Frequently Asked Questions across all 32 PCMC departments.
- **`service_kb/`**: RTS (Right to Services) application eligibility, fees, deadlines, and step-by-step procedures.
- **`policies/`**: Standing committee resolutions, municipal by-laws, and development control regulations.
- **`circulars/`**: Official municipal notices, tender updates, and public safety announcements.
- **`ownership_docs/`**: Intellectual property and data ownership artifacts (Prompt library ownership, Embeddings ownership, Vector DB schema ownership, Training dataset ownership).

### 14. `analytics/` — Civic Insights & Cost Intelligence
*Aligned with RFP Sec 1.2.7 & 1.2.14 (Dashboards, NPS, AI Usage Tracking, Predictive Analytics)*
- **`ai_usage_tracking/`**: Fine-grained token consumption, model latencies, and API cost analytics per department.
- **`sentiment_nps_analysis/`**: Citizen satisfaction index (CSAT), Net Promoter Score (NPS), and post-resolution grievance feedback analytics.
- **`predictive_insights/`**: Seasonal grievance forecasting (e.g., water contamination before monsoon, dengue hotspots).
- **`recommendation_engine/`**: Proactive citizen notification recommendations (e.g., tax discount early-bird reminders).

### 15. `tests/` — Verification & Quality Assurance
- **`unit/`**: Unit tests for NLP tokenizers, PII maskers, and utility functions.
- **`integration/`**: End-to-end integration tests for MCP servers, RAG pipelines, and WhatsApp webhook handlers.
- **`evals/`**: Golden test sets evaluating hallucination rates, translation quality, and intent classification accuracy.

---

## 🧭 Architectural Boundary Clarifications

| Module Pair | Distinct Responsibilities & Boundary |
|---|---|
| **`llm/evaluation/`**<br>vs<br>**`governance/evaluations/`** | **`llm/evaluation/`**: Developer & engineering lab for **offline model/prompt experimentation** (testing Prompt v1 vs Prompt v2, comparing GPT-4o vs Gemini 1.5 vs Claude on benchmark test cases before deployment).<br>**`governance/evaluations/`**: Government compliance & **production monitoring** suite (measuring live RAG Faithfulness, Hallucination rates on real citizen queries, toxicity detection, and DPDP Act compliance audit). |
| **`moderation/`**<br>vs<br>**`governance/`** | **`moderation/`**: **Synchronous Runtime Guardrails** (Active packet inspection: PII masking, profanity filtering, jailbreak defense on user input & bot output).<br>**`governance/`**: **Asynchronous & Policy Controls** (Escalation decision logic, hallucination detection, prompt & audit logging, legal compliance). |
| **`governance/escalation/`**<br>vs<br>**`orchestration/human_handoff/`** | **`governance/escalation/`**: The **Brain / Detector** (Decides *WHY* & *WHEN* to escalate based on rules, negative sentiment, repetitive confusion).<br>**`orchestration/human_handoff/`**: The **Action / Bridge** (Executes *HOW* the session is frozen, packages the context/summary, routes to the PCMC Live Operator CRM, and resumes when the human exits). |
#   S a r a t h i - A I - I n t e l l i g e n c e  
 