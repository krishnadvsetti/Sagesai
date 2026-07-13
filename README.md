# sagesai
# Sagesai

## Enterprise AI Platform

Sagesai is an enterprise-oriented AI platform that combines generative AI, retrieval-augmented generation (RAG), multi-agent engineering workflows, machine learning, deep learning, cybersecurity analytics, enterprise governance, security controls, observability, and microservice architecture in a unified backend platform.

The project demonstrates how AI capabilities can be engineered as production-oriented services rather than isolated notebooks or model demos.

---

## Project Highlights

- Enterprise FastAPI platform API
- Retrieval-Augmented Generation (RAG)
- Document ingestion, chunking, embeddings, vector search, and reranking
- Multi-agent software engineering assistant
- AI gateway with provider abstraction and fallback handling
- Conversational memory
- Prompt-injection detection and AI guardrails
- Human-in-the-loop approval workflows
- JWT authentication and role-based access control
- SOC cybersecurity analysis
- PyTorch anomaly detection microservice
- TensorFlow document-quality computer vision
- NLP entity extraction
- RAG evaluation framework
- Prometheus metrics and structured application observability
- Grafana dashboard provisioning
- PostgreSQL persistence
- Dockerized service architecture
- Automated linting and testing with GitHub Actions

---

# Architecture

```text
                         ┌──────────────────────────┐
                         │      API Consumers       │
                         │ Web / Mobile / Services  │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │       Sagesai Platform API      │
                    │            FastAPI              │
                    ├─────────────────────────────────┤
                    │ Authentication / JWT / RBAC     │
                    │ Security Middleware             │
                    │ Rate Limiting                   │
                    │ Request Validation              │
                    │ Exception Handling              │
                    │ Structured Logging              │
                    │ Prometheus Metrics              │
                    └───────────────┬─────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌─────────────────┐        ┌─────────────────┐
│ AI & RAG      │          │ Enterprise      │        │ ML / AI         │
│ Services      │          │ Workflows       │        │ Services        │
├───────────────┤          ├─────────────────┤        ├─────────────────┤
│ AI Gateway    │          │ Approvals       │        │ Computer Vision │
│ Gemini        │          │ Memory          │        │ NLP             │
│ Embeddings    │          │ Company Sec.    │        │ SOC Analysis    │
│ Vector Search │          │ Engineering AI  │        │ Anomaly Client  │
│ Reranking     │          │ Guardrails      │        └────────┬────────┘
│ Evaluation    │          └─────────────────┘                 │
└───────────────┘                                              ▼
                                                    ┌─────────────────────┐
                                                    │ Anomaly Microservice│
                                                    │ PyTorch Autoencoder │
                                                    └─────────────────────┘

        ┌───────────────────────┐
        │      PostgreSQL       │
        │ Users / Memory /      │
        │ Approval Workflows    │
        └───────────────────────┘

        ┌───────────────────────┐
        │ Observability Stack   │
        │ Prometheus + Grafana  │
        └───────────────────────┘
