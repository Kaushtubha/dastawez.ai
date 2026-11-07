# Changelog

All notable changes to Dastawez.ai (DocuMind) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- **Document Export Utility**: Added `GET /api/v1/documents/{id}/export?format=json|csv` endpoint supporting structural chunk and metadata extraction.
- **Glassmorphic Toast Notifications**: Created `ToastContext` and `Toast.jsx` for non-intrusive feedback across upload, query, and authentication events.
- **Shimmer Skeleton Loaders**: Implemented `SkeletonLoader.jsx` with GPU-accelerated CSS shimmer animation for metric cards, charts, and table rows.
- **Enhanced OpenAPI Documentation**: Enriched Swagger specification with detailed tag taxonomy, contact information, and license metadata.
- **Automated Test Suite Expansion**: Added unit tests for document export, CSV formatting limits, and input validation guards (`8 passed`).

### Changed
- **Async Lifespan Architecture**: Migrated from deprecated `@app.on_event("startup")` to modern Starlette `@asynccontextmanager lifespan(app: FastAPI)` pattern.
- **Request Validation Constraints**: Enhanced `AskRequest` with string boundaries, non-empty whitespace validators, and structured example queries.

---

## [1.0.0] - 2024-03-03

### Added
- **Initial Release** - Complete full-stack document analysis platform
- FastAPI backend with RESTful API endpoints
- React frontend with modern dark theme UI
- Document upload and parsing (PDF, DOCX, TXT)
- Statistical analysis with Chart.js visualizations
- AI-powered Q&A system with confidence scoring
- User authentication and authorization
- Document history management
- Docker support with docker-compose
- Comprehensive documentation (README, DEPLOYMENT, CONTRIBUTING)
- Environment configuration templates
- Automated setup scripts for Windows and Unix
