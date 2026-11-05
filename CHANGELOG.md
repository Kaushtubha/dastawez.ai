# Changelog

All notable changes to Dastawez.ai (DocuMind) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Features
#### Backend
- FastAPI application with async support
- SQLite database for metadata storage
- Document parsing using Unstructured library
- Text chunking and processing
- Hybrid vector store implementation (TF-IDF + Qdrant)
- Authentication endpoints (login, register, logout)
- Document CRUD operations
- Q&A endpoint with context retrieval
- CORS configuration for frontend integration

#### Frontend
- React 18.2 with Vite build system
- Modern dark theme with gradient backgrounds
- Responsive design for all devices
- Authentication pages (Login, Register)
- Dashboard with document statistics
- Upload section with drag-and-drop
- Analysis section with interactive charts
- Chat interface for Q&A
- Document history management
- User profile page
- Protected routes with auth guards
- Context-based state management

#### Infrastructure
- Docker containerization
- Docker Compose orchestration
- Environment variable management
- Git ignore rules for clean repository
- Setup automation scripts
- Production deployment guides
