# Agentic Hive: Technology Stack Reference

## Core Execution Engine
*   **[Just](https://github.com/casey/just)**: The primary task runner.
    *   **Role:** Executes project-local tasks defined in `justfiles`. Acts as the "Worker" that translates human-readable commands into environment-specific scripts (Python, Node.js, Rust, etc.).
    *   **Rationale:** Lightweight, single-binary, cross-platform, and avoids vendor lock-in.

## Multi-Agent Orchestration Framework
*   **Orchestration Logic (Custom Python):** A bespoke state machine/message bus built in Python to handle agent delegation and hand-offs.
*   **LLM Integration:** 
    *   **Planner (8B Model):** High-level architectural reasoning and plan generation.
    *   **Watcher/Architect (3B Models):** Tactical execution monitoring, alignment, and initial discovery.
*   **Integration Interface:** `litellm` or direct `ollama` API calls (local model management).

## Knowledge & Data Layer
*   **RAG Database:** [ChromaDB](https://www.trychroma.com/) or [FAISS](https://github.com/facebookresearch/faiss).
    *   **Role:** Stores verified fixes, architectural specs, and tribal knowledge.
    *   **Rationale:** Local-first, high performance, and handles document embeddings for RAG retrieval.
*   **Researcher Tooling:** `googlesearch-python` (or similar API) for live web-based data retrieval when local RAG yields no results.

## Monitoring & Alignment
*   **Judge Agent:** A deterministic logic gate combined with an LLM-as-a-Judge prompt to verify the "Proof-of-Fix" protocol.
*   **Interceptor Pattern:** Log aggregation via standard `stdout/stderr` streams, structured into JSON logs in `.harness/logs/`.

## Lifecycle Management
*   **Justfile Templates:** Standardized command patterns stored in `~/.harness/registry/prompts/`.
*   **State Management:** Local JSON files (`pipeline_config.json`, `master_spec.json`) stored in project-local `.harness/` directories.
