# Contributing to DocuMind AI

Thank you for your interest in contributing to DocuMind AI! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone. We welcome contributors of all backgrounds and experience levels.

### Our Standards

Examples of behavior that contributes to creating a positive environment:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

Examples of unacceptable behavior:
- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments
- Personal or political attacks
- Publishing others' private information

---

## Getting Started

### 1. Fork the Repository

Click the "Fork" button at the top right of the repository page.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/documind-ai.git
cd documind-ai
```

### 3. Set Up Development Environment

Follow the setup instructions in README.md to configure your local environment.

---

## Development Setup

### Backend Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start development server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

---

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Screenshots or logs** if applicable

**Example:**
```markdown
**Bug Description**
The upload fails when file size exceeds 10MB.

**Steps to Reproduce**
1. Go to upload page
2. Select a file larger than 10MB
3. Click upload

**Expected Behavior**
File should upload successfully.

**Actual Behavior**
Upload fails with timeout error.

**Environment**
- OS: Windows 11
- Python: 3.9.7
- Browser: Chrome 120
```

### Suggesting Features

Feature suggestions are welcome! Please provide:
- Use case for the feature
- Expected behavior
- Examples or mockups if possible

### Your First Code Contribution

1. Look for issues labeled "good first issue" or "help wanted"
2. Comment on the issue to claim it
3. Create a branch and make your changes
4. Test thoroughly
5. Submit a pull request

---

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions small and focused
- Use meaningful variable names

**Example:**
```python
def calculate_document_stats(documents: List[Dict]) -> Dict[str, Any]:
    """
    Calculate statistics for a list of documents.
    
    Args:
        documents: List of document dictionaries
        
    Returns:
        Dictionary containing calculated statistics
    """
    total_docs = len(documents)
    # ... implementation
    return stats
```

### JavaScript/React Style Guide

- Use ES6+ features
- Use functional components with hooks
- Follow consistent naming conventions
- Add PropTypes or TypeScript types
- Comment complex logic

**Example:**
```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const DocumentCard = ({ document, onDelete }) => {
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Fetch document data
  }, [document.id]);
  
  const handleDelete = async () => {
    setLoading(true);
    await onDelete(document.id);
    setLoading(false);
  };
  
  return (
    <div className="document-card">
      {/* Component content */}
    </div>
  );
};

DocumentCard.propTypes = {
  document: PropTypes.object.isRequired,
  onDelete: PropTypes.func.isRequired
};

export default DocumentCard;
```

### File Naming Conventions

- **Python**: snake_case (e.g., `document_parser.py`)
- **JavaScript/React**: PascalCase for components, camelCase for utilities
- **CSS**: kebab-case (e.g., `dashboard-styles.css`)

---

## Commit Guidelines

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(upload): add support for batch file uploads

Implemented multi-file selection and parallel upload processing.

Closes #123

---

fix(api): resolve timeout issue in document parsing

Fixed connection pool exhaustion during large file processing.

Fixes #456

---

docs(readme): update installation instructions

Added detailed steps for Docker setup and troubleshooting section.
```

### Before Committing

```bash
# Run linters
flake8 .
eslint frontend/src

# Run tests
pytest
npm test

# Format code
black .
prettier --write frontend/src
```

---

## Pull Request Process

### Creating a Pull Request

1. **Create a branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them following commit guidelines

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** on GitHub

5. **Fill out the PR template** completely

### PR Template

When opening a PR, please include:

- **Description**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Testing**: How was it tested?
- **Screenshots**: If UI changes (before/after)
- **Checklist**:
  - [ ] Tests added/updated
  - [ ] Documentation updated
  - [ ] No breaking changes
  - [ ] Code follows style guidelines

### Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Celebrate! 🎉

---

## Testing

### Writing Tests

**Backend (pytest):**
```python
def test_document_upload():
    """Test document upload endpoint."""
    response = client.post(
        "/api/v1/upload-docs",
        files={"file": ("test.pdf", test_data)}
    )
    assert response.status_code == 200
    assert "document_id" in response.json()
```

**Frontend (Jest + React Testing Library):**
```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import UploadSection from './UploadSection';

test('uploads file successfully', async () => {
  render(<UploadSection />);
  
  const fileInput = screen.getByTestId('file-input');
  const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
  
  fireEvent.change(fileInput, { target: { files: [file] } });
  
  expect(await screen.findByText('Upload successful')).toBeInTheDocument();
});
```

### Running Tests

```bash
# Backend
pytest
pytest --cov=app  # With coverage

# Frontend
npm test
npm test -- --coverage
```

---

## Documentation

### Code Comments

- Explain **why**, not just **what**
- Keep comments up-to-date
- Document complex algorithms
- Add TODO comments for future improvements

### API Documentation

Update API documentation when changing endpoints:

```python
@app.post("/api/v1/documents", tags=["Documents"])
async def create_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_user)
) -> DocumentResponse:
    """
    Create a new document.
    
    - **name**: Document name
    - **content**: Document content
    - **tags**: Optional tags for categorization
    
    Returns the created document with metadata.
    """
    # Implementation
```

---

## Questions?

If you have questions or need help:
- Check existing issues and discussions
- Join our community chat (if available)
- Ask in GitHub Discussions
- Contact maintainers

---

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Annual contributor highlights

---

**Thank you for contributing to DocuMind AI!** 🚀

Together we're building better software.
