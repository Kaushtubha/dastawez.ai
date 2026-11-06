# 🚀 DocuMind AI - Intelligent Document Analysis Platform

<div align="center">

![DocuMind AI](https://img.shields.io/badge/DocuMind-AI-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18.2.0-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)

**An Enterprise-Grade AI-Powered Document Analysis & Q&A System**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Deployment](#-deployment) • [Contributing](#-contributing)

</div>

## ✨ Features

### 📄 Document Processing
- ✅ **Multi-Format Support**: Upload PDF, DOCX, and TXT files
- ✅ **Smart Parsing**: Automatic document parsing and content extraction
- ✅ **Intelligent Chunking**: Advanced document segmentation for optimal analysis
- ✅ **Statistical Analysis**: Comprehensive document metrics and insights

### 📊 Analysis & Visualization
- ✅ **Element Distribution**: Interactive Bar and Pie charts showing document structure
- ✅ **Keyword Extraction**: AI-powered keyword identification and frequency analysis
- ✅ **Document Statistics**: Detailed metrics including word count, pages, and element types
- ✅ **Chart.js Integration**: Beautiful, responsive data visualizations

### 💬 Smart Q&A System
- ✅ **Natural Language Queries**: Ask questions in plain English
- ✅ **Context-Aware Responses**: AI-powered answers based on document content
- ✅ **Confidence Scoring**: Transparency with answer confidence levels
- ✅ **Source Attribution**: Direct references to source documents

### 🎨 Modern UI/UX
- ✅ **Dark Theme & Accent Switcher**: Cosmic Purple, Cyber Cyan, and Matrix Emerald themes
- ✅ **Global Keyboard Shortcuts**: Fast navigation with Ctrl+D, Ctrl+H, Ctrl+Q, and cheat-sheet modal (?)
- ✅ **Document & Chunk Inspector Modal**: Deep-dive into raw layout elements and chunk tokens
- ✅ **Interactive Confirmation Dialogs**: Custom glassmorphic confirmation modals replacing browser alerts
- ✅ **Multi-Stage Ingestion Telemetry**: Real-time pipeline progress (Verification, Layout OCR, Semantic Chunking, Vector Sync)
- ✅ **Smooth Animations**: Polished transitions and hover effects
- ✅ **Fully Responsive**: Optimized for desktop, tablet, and mobile devices
- ✅ **Modern Dashboard**: Intuitive navigation and professional layout

### 🔐 User Management
- ✅ **Authentication**: Secure login and registration system
- ✅ **Session Management**: Persistent user sessions
- ✅ **Protected Routes**: Role-based access control
- ✅ **User Profiles**: Personalized dashboard and settings

### 📚 Document History
- ✅ **Document Tracking**: Complete history of all uploads
- ✅ **Analysis Archive**: Access previous analysis results
- ✅ **Collection Management**: Organize and manage documents
- ✅ **Search & Filter**: Quick document discovery tools

## 🛠️ Tech Stack

### Backend
- **FastAPI** (v0.104+) - High-performance async Python web framework
- **SQLite** - Lightweight relational database for metadata
- **SQLAlchemy** - SQL toolkit and ORM
- **LangChain** - LLM orchestration framework
- **Unstructured** - Document parsing library (PDF, DOCX, TXT)
- **PyPDF** - PDF processing utilities
- **python-docx** - Microsoft Word document handling

### Frontend
- **React 18.2** - Modern UI library with hooks
- **Vite 4.4** - Lightning-fast build tool and dev server
- **React Router 7.11** - Declarative routing
- **Chart.js 4.4** - Responsive charting library
- **React-Chartjs-2** - Chart.js React wrapper
- **Axios** - HTTP client for API calls

### Infrastructure
- **Docker** - Containerization
- **docker-compose** - Multi-container orchestration
- **Qdrant** (optional) - Vector database for embeddings
- **OpenAI SDK** - LLM integration (optional)

### Development Tools
- **ESLint/Prettier** - Code linting and formatting
- **Python-dotenv** - Environment variable management
- **pytest** - Backend testing framework

## 🚀 Installation & Setup

### Prerequisites
- **Python** 3.8 or higher
- **Node.js** 16 or higher
- **npm** or **yarn** package manager
- **Git** for version control

### Quick Start (Development)

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/documind-ai.git
cd documind-ai
```

#### 2. Backend Setup

**Step 1:** Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Step 2:** Install Python dependencies
```bash
pip install -r requirements.txt
```

**Step 3:** Configure environment variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your settings
```

**Step 4:** Start the backend server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at: `http://localhost:8000`  
📚 API docs at: `http://localhost:8000/docs`

#### 3. Frontend Setup

**Step 1:** Navigate to frontend directory
```bash
cd frontend
```

**Step 2:** Install Node dependencies
```bash
npm install
```

**Step 3:** Start development server
```bash
npm run dev
```

✅ Frontend running at: `http://localhost:5173`

### Using Docker (Recommended for Production)

**Prerequisites:** Docker and Docker Compose installed

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

✅ Application accessible at: `http://localhost:3000`  
✅ Backend API at: `http://localhost:8000`

**Stop services:**
```bash
docker-compose down
```

## 📖 Usage Guide

### First-Time Setup

1. **Create Account**
   - Navigate to the registration page
   - Enter your credentials
   - Complete registration

2. **Login**
   - Use your registered credentials
   - Access the main dashboard

### Document Upload & Analysis

1. **Upload Documents**
   - Click "Upload" in the dashboard
   - Drag & drop or select files (PDF, DOCX, TXT)
   - Wait for processing completion
   - View real-time upload status

2. **View Analysis**
   - Automatic statistical analysis generation
   - Interactive charts (element distribution, keywords)
   - Detailed document metrics
   - Export analysis results

3. **Ask Questions**
   - Navigate to Chat section
   - Type natural language questions
   - Receive AI-powered responses with confidence scores
   - View source references

4. **Manage History**
   - Access document history anytime
   - Search and filter documents
   - Delete unwanted documents
   - Review past analyses

### Power User Tips

- 💡 Upload multiple documents for comparative analysis
- 💡 Use specific questions for better answers
- 💡 Check confidence scores for answer reliability
- 💡 Bookmark frequently accessed documents

## 🔌 API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register new user |
| `POST` | `/auth/login` | User login |
| `POST` | `/auth/logout` | User logout |

### Document Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload-docs` | Upload and analyze documents |
| `GET` | `/document-history` | Retrieve all user documents |
| `GET` | `/documents/{id}` | Get specific document details |
| `DELETE` | `/documents/{id}` | Delete a document |

### Analysis & Q&A
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ask` | Ask questions about documents |
| `GET` | `/analysis/{id}` | Get document analysis results |
| `GET` | `/stats/{id}` | Get document statistics |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Backend health check |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |

### Example API Usage

**Upload a Document:**
```bash
curl -X POST http://localhost:8000/api/v1/upload-docs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

**Ask a Question:**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question": "What is the main topic?", "document_id": 123}'
```

**Get Document History:**
```bash
curl http://localhost:8000/api/v1/document-history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📁 Project Structure

```
documind-ai/
├── 📂 app/                          # Backend Application
│   ├── 📂 api/                      # API Routes
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── upload.py                # Document upload endpoint
│   │   └── ask.py                   # Q&A endpoint
│   ├── 📂 core/                     # Core Logic
│   │   ├── __init__.py
│   │   ├── agent.py                 # AI Agent
│   │   ├── guardrails.py            # Safety filters
│   │   └── retriever.py             # Document retrieval
│   ├── 📂 db/                       # Database Layer
│   │   ├── __init__.py
│   │   ├── metadata.py              # SQLite metadata
│   │   └── vector_store.py          # Vector embeddings
│   ├── 📂 ingestion/                # Document Processing
│   │   ├── __init__.py
│   │   ├── parser.py                # File parsing
│   │   └── chunker.py               # Text chunking
│   ├── 📂 static/                   # Static Assets
│   │   └── index.html               # Built frontend
│   ├── 📂 templates/                # HTML Templates
│   ├── __init__.py
│   ├── config.py                    # Configuration
│   └── main.py                      # FastAPI Entry Point
│
├── 📂 frontend/                     # React Frontend
│   ├── 📂 src/
│   │   ├── 📂 components/           # Reusable Components
│   │   │   ├── UploadSection.jsx
│   │   │   ├── AnalysisSection.jsx
│   │   │   └── ChatSection.jsx
│   │   ├── 📂 pages/                # Page Components
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── HistoryPage.jsx
│   │   │   └── ProfilePage.jsx
│   │   ├── 📂 context/              # React Context
│   │   │   └── AuthContext.jsx
│   │   ├── 📂 services/             # API Services
│   │   │   ├── authService.js
│   │   │   └── historyService.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── public/
│
├── 📂 uploads/                      # Uploaded Documents
├── .env.example                     # Environment Template
├── .gitignore                       # Git Ignore Rules
├── docker-compose.yml               # Docker Orchestration
├── Dockerfile                       # Backend Docker Image
├── requirements.txt                 # Python Dependencies
├── README.md                        # Documentation
└── documind.db                      # SQLite Database
```

## 🎯 Key Features Demonstrated

### 📄 Document Analysis
- ✅ **Multi-Format Parsing**: PDF, DOCX, TXT content extraction
- ✅ **Statistical Analysis**: Word count, element distribution, metadata
- ✅ **Keyword Extraction**: TF-IDF and frequency-based analysis
- ✅ **Intelligent Chunking**: Semantic text segmentation

### 📊 Data Visualization
- ✅ **Chart.js Integration**: Bar, Pie, Line charts
- ✅ **Real-Time Updates**: Dynamic data rendering
- ✅ **Responsive Design**: Mobile-friendly charts
- ✅ **Interactive Elements**: Hover effects, tooltips

### 👤 User Experience
- ✅ **Dark Theme**: Professional gradient backgrounds
- ✅ **Smooth Animations**: CSS transitions and keyframes
- ✅ **Intuitive Navigation**: Clear user flows
- ✅ **Mobile-First**: Fully responsive across devices

### 🔧 Full-Stack Integration
- ✅ **RESTful API**: Clean endpoint design
- ✅ **CORS Configuration**: Cross-origin support
- ✅ **React Context**: Global state management
- ✅ **Async/Await**: Modern JavaScript patterns
- ✅ **Error Handling**: Graceful degradation

## 🚀 Future Enhancements

### Short-Term Roadmap
- [ ] **Vector Database Integration**: Qdrant, Pinecone, or Weaviate for semantic search
- [ ] **Advanced NLP Models**: BERT, RoBERTa for deeper text understanding
- [ ] **Multi-Language Support**: i18n for global accessibility
- [ ] **Export Functionality**: PDF/CSV export of analysis results
- [ ] **Batch Upload**: Multiple document processing

### Long-Term Vision
- [ ] **Collaborative Features**: Team workspaces and sharing
- [ ] **Advanced Search**: Full-text search with filters
- [ ] **API Rate Limiting**: Production-ready throttling
- [ ] **Analytics Dashboard**: Usage metrics and insights
- [ ] **Cloud Storage**: S3, Google Cloud Storage integration
- [ ] **Mobile App**: React Native mobile application
- [ ] **Browser Extension**: Quick document upload from web

## 👥 Author & Contributors

**Created by:** DocuMind AI Development Team  
**Project Type:** Full-Stack AI-Powered Document Analysis Platform  
**Technologies:** FastAPI, React, Docker, NLP

### Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow existing code style
- Write meaningful commit messages
- Add comments for complex logic
- Test thoroughly before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note:** This project was initially created as part of a Python internship project demonstrating full-stack development skills with modern web technologies.

## 🙏 Acknowledgments

- **FastAPI** team for the amazing framework
- **React** community for excellent documentation
- **Chart.js** for beautiful visualizations
- **LangChain** for LLM orchestration tools
- All contributors and supporters

## 📞 Support & Contact

- **Issues:** Open a GitHub issue for bugs or feature requests
- **Discussions:** Use GitHub Discussions for questions
- **Email:** support@documind.ai (if applicable)

## 🔗 Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Docker Documentation](https://docs.docker.com/)

---

<div align="center">

**Made with ❤️ by the DocuMind AI Team**

[Back to Top](#-documind-ai---intelligent-document-analysis-platform)

</div>