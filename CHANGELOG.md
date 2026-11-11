# Changelog

All notable changes to Dastawez.ai (DocuMind) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.3] - 2026-11-10

### Added
- **AI Document Semantic Comparison Engine**: Implemented `POST /api/v1/documents/compare` endpoint calculating TF-IDF cosine similarity percentages, structural deltas (chunks, elements, file size), shared vocabulary, and distinct keyword divergence between any two catalog documents.
- **Side-by-Side Comparison Modal (`CompareModal.jsx`)**: Designed a glassmorphic modal with animated similarity progress meter, dual document metric cards with visual delta badges, and vocabulary divergence pills.
- **Batch Compare Toolbar Action**: Enhanced `HistoryPage.jsx` batch action toolbar with an instant "⚖️ Compare 2 Docs" trigger activated when two documents are selected.
- **Single-Document CSV Chunk Dataset Export**: Added `GET /api/v1/documents/{id}/export/csv` streaming all extracted text chunks, coordinates, section headings, and word counts as CSV.
- **Reconstructed Markdown Export**: Added `GET /api/v1/documents/{id}/export/markdown` reconstructing layout elements into formatted Markdown with YAML metadata frontmatter.
- **Modal Export Controls**: Integrated 1-click "Export MD" and "Export CSV" buttons into `DocumentModal.jsx`.
- **Test Suite Expansion**: Added `tests/test_document_exports.py` covering CSV export, Markdown reconstruction, and semantic document comparison.
- **Production Distribution Asset Compilation**: Built optimized production frontend bundle with Vite into `app/static/`.

---

## [1.3.2] - 2026-11-09

### Added
- **Cluster & Storage Telemetry Dashboard**: Enhanced `ProfilePage.jsx` with real-time server upload storage utilization, SQLite database footprint, active vector engine capabilities, DB ping latency metrics, and dynamic telemetry refresh.
- **Bulk ZIP Archive Export in Management Toolbar**: Added one-click "Export Selected ZIP" in the batch action toolbar and "Export Catalog ZIP" in `HistoryPage.jsx` with automatic download of structured archive packages.
- **Markdown & Syntax-Highlighted Code Blocks in AI Chat**: Integrated custom markdown formatting for assistant responses in `ChatSection.jsx`, including headers, bullet points, inline code badges, and copyable code blocks with 1-click clipboard button.
- **Hierarchical Heading Context Chunker**: Enhanced `DocumentChunker` in `app/ingestion/chunker.py` to capture section headers (`Title`, `Header`, `Subheader`), attach semantic section breadcrumbs to chunks, and compute statistical chunk metrics (`compute_chunk_metrics`).
- **Pipeline Benchmarking & Profiler Tool**: Added `scripts/benchmark.py` CLI utility for profiling document chunking throughput, cryptographic SHA-256 hashing speed, SQLite connection latency percentiles, and TF-IDF search ranking.
- **Comprehensive Test Suite Expansion**: Added `tests/test_chunker_benchmark.py` validating section heading propagation and statistical metrics (13/13 passing tests).
- **Production Asset Compilation**: Recompiled production distribution bundles with Vite into `app/static/`.

---

## [1.3.1] - 2026-11-09

### Added
- **Kubernetes-Ready Detailed Health Probes**: Added `GET /api/v1/system/health/detailed` featuring live database roundtrip latency measurement (`db.execute(SELECT 1)`), liveness/readiness probe states, runtime environment diagnostics (Python version, platform OS), and vector store connectivity.
- **Global Ctrl+K / Cmd+K Spotlight Command Palette**: Created `SpotlightModal.jsx` providing keyboard-first search launcher for instant document lookup, multi-page jumping, quick format filtering, and theme toggling.
- **Navbar Spotlight Launcher**: Integrated quick search pill in `Navbar.jsx` with keyboard badge and direct modal toggle.
- **Keyboard Shortcut Expansion**: Updated `useKeyboardShortcuts.js` and `ShortcutModal.jsx` with `Ctrl+K` / `Cmd+K` hotkey binding.
- **Frontend Distribution Build**: Compiled production assets with full Vite optimizations to `app/static/`.

---

## [1.3.0] - 2026-11-07

### Added
- **Native Markdown Parser**: Added full AST-aware Markdown (`.md`) ingestion parsing headers, tables, code blocks, and list items into structured layout elements.
- **Cryptographic SHA-256 Deduplication**: Added file hash calculation avoiding duplicate parsing and vector index bloating for previously ingested payloads.
- **Word-Overlap Sliding Chunker**: Enhanced chunker with token boundary sliding overlap (`overlap_words=25`) preserving semantic continuity.
- **Server-Side Full-Text & Format Search**: Added `GET /api/v1/documents/search` supporting keyword queries across documents and chunk datasets.
- **Bulk Document ZIP Archive Export**: Implemented `POST /api/v1/documents/export-archive` generating structured ZIP packages with JSON manifests, raw files, and CSV chunks.
- **Document Reprocessing & Re-indexing**: Added `POST /api/v1/documents/{id}/reindex` to purge chunks and re-parse documents with updated layout parameters.
- **Token Bucket Rate Limiting**: Injected in-memory sliding window rate limiter middleware with `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers.
- **Platform Capabilities Endpoint**: Added `GET /api/v1/system/capabilities` exposing vector engines, supported extensions, and feature flags.
- **Interactive Citation Excerpt Drawers**: Added expandable citation excerpt cards in chat displaying verified excerpts and similarity scores.
- **Search Highlighting in History**: Integrated real-time keyword highlight markers within the document archive view.
- **Multi-Select Checkboxes & Batch Deletion**: Added batch selection UI with instant multi-document deletion controls.
- **Executive AI Brief Modal**: Created `ExecutiveSummaryModal.jsx` for on-demand inspection of document executive briefs and insights.
- **Standalone CLI Ingestion Tool**: Created `scripts/ingest_cli.py` for headless single-file and directory document ingestion.
- **Database Maintenance & Vacuum Tool**: Created `scripts/db_maintenance.py` for SQLite PRAGMA checks, orphaned chunk purges, and disk vacuuming.
- **Automated Architecture Smoke Test**: Created `scripts/smoke_test.py` running automated 7-phase validation across all system modules.
- **Automatic SQLite Schema Migration**: Added non-destructive schema migrations on boot in `init_db()`.
- **Test Suite Expansion**: Added unit and integration test coverage (`16 passed`).

---

## [1.2.0] - 2026-11-06

### Added
- **Automated Document Executive Summaries**: Added `GET /api/v1/documents/{id}/summary` generating high-level briefs, structural composition summaries, and keyword highlights.
- **Batch Document Deletion**: Implemented `POST /api/v1/documents/batch-delete` for atomic multi-document purge of database records, vector partitions, and filesystem storage.
- **Storage Telemetry & Health Metrics**: Added `GET /api/v1/system/telemetry` tracking upload directory sizes, SQLite disk footprint, chunk counts, and system catalog statistics.
- **Performance Telemetry Middleware**: Injected `X-Process-Time` HTTP response header measuring microsecond request pipeline latency.
- **Global Standardized Exception Handlers**: Registered FastAPI error interceptors providing uniform error payloads with code, message, and diagnostic details.
- **Interactive Document Chunk Inspector Modal**: Created `DocumentModal.jsx` for deep inspection of individual text chunks, classifications, and page coordinates.
- **Glassmorphic Confirmation Modal**: Created `ConfirmModal.jsx` replacing native browser confirm prompts with styled glass dialogs.
- **Format Filter Pills & Sorting Controls**: Enriched `HistoryPage.jsx` with instant category pills (`ALL`, `PDF`, `DOCX`, `TXT`) and multi-factor sorting (date, name, size, element count).
- **Multi-Stage Ingestion Telemetry**: Enhanced `UploadSection.jsx` with active stage stepper (Verification, Layout Parsing, Semantic Chunking, Vector Sync).
- **Conversation JSON Export & Copy Controls**: Added instant thread export, clipboard copy with feedback toasts, and session reset controls in `ChatSection.jsx`.
- **Global Hotkey Navigation System**: Implemented `useKeyboardShortcuts.js` and `ShortcutModal.jsx` (`?`, `Ctrl+D`, `Ctrl+H`, `Ctrl+Q`, `Ctrl+P`, `Esc`).
- **Ambient Accent Theme Switcher**: Introduced `ThemeContext.jsx` with real-time accent color switches (`Cosmic Purple`, `Cyber Cyan`, `Matrix Emerald`).
- **Automated Test Suite Expansion**: Added `tests/test_advanced_api.py` validating executive brief synthesis and batch removal endpoints (11 passed).

---

## [1.1.0] - 2026-11-06

### Added
- **Multi-Format Document Ingestion Engine**: Support for unstructured PDF, Microsoft Word (`.docx`), and Plain Text (`.txt`).
- **Intelligent Spatial Element Extraction**: Extraction of paragraphs, section headings, tables, bullet lists, and spatial bounding boxes.
- **Vector Search Engine Integration**: Qdrant Vector Database integration with automatic fallback to Scikit-Learn TF-IDF vector retrieval.
- **OpenAI & Fallback Local Extractive Synthesis**: Grounded question answering pipeline with citation tracking and similarity confidence scoring.
- **Single Page Application Dashboard**: Interactive React frontend with statistics charts, document library, and AI chat room.
