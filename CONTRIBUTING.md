# 🤝 Contributing to Toxic Language Detector

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and considerate
- Use welcoming and inclusive language
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory comments
- Trolling or insulting remarks
- Publishing others' private information
- Other unprofessional conduct

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PHP 8.1+ (for dashboard)
- Node.js 16+ (for dashboard assets)
- Git
- Redis (optional)
- PostgreSQL or MySQL (optional)

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/toxic-language-detector.git
cd toxic-language-detector

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/toxic-language-detector.git
```

---

## 💻 Development Setup

### Quick Setup

```bash
# Option 1: Using Makefile
make setup
make start

# Option 2: Using scripts
./scripts/start-all.sh    # Linux/Mac
.\scripts\start-all.ps1   # Windows
```

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with your settings

# 4. Run migrations
python -m backend.db.migrations.add_performance_indexes

# 5. Start backend
uvicorn app:app --reload --port 7860

# 6. Setup dashboard (separate terminal)
cd webdashboard
composer install
npm install
cp .env.example .env
php artisan key:generate
php artisan migrate
php artisan serve --port 8080
```

---

## 🤝 How to Contribute

### Types of Contributions

1. **Bug Fixes** - Fix reported issues
2. **Features** - Add new functionality
3. **Documentation** - Improve docs
4. **Tests** - Add or improve tests
5. **Performance** - Optimize code
6. **Refactoring** - Improve code quality

### Contribution Workflow

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description

# 2. Make your changes
# ... edit files ...

# 3. Format code
make format

# 4. Run linters
make lint

# 5. Run tests
make test

# 6. Commit changes
git add .
git commit -m "feat: add new feature"
# Use conventional commits (see below)

# 7. Push to your fork
git push origin feature/your-feature-name

# 8. Create Pull Request on GitHub
```

---

## 📝 Coding Standards

### Python (Backend)

#### Style Guide

Follow [PEP 8](https://peps.python.org/pep-0008/) and use these tools:

```bash
# Format code
black backend
isort backend

# Check style
flake8 backend
mypy backend
```

#### Naming Conventions

```python
# Classes: PascalCase
class UserService:
    pass

# Functions/methods: snake_case
def get_user_by_id(user_id: int):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private: prefix with _
def _internal_helper():
    pass
```

#### Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict

def process_texts(texts: List[str]) -> Dict[str, float]:
    """Process multiple texts and return scores."""
    pass

async def get_user(user_id: int) -> Optional[User]:
    """Get user by ID, return None if not found."""
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def predict_toxicity(text: str) -> Dict[str, Any]:
    """Predict toxicity of text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary with prediction results:
            - is_toxic: bool
            - confidence: float
            - categories: List[str]
            
    Raises:
        ValueError: If text is empty
        ModelNotLoadedError: If model not initialized
    """
    pass
```

### PHP (Dashboard)

Follow [PSR-12](https://www.php-fig.org/psr/psr-12/) standards.

### JavaScript (Extension)

- Use ES6+ features
- Use `const`/`let`, not `var`
- Use arrow functions where appropriate
- Add JSDoc comments for functions

```javascript
/**
 * Detect toxicity in text
 * @param {string} text - Text to analyze
 * @returns {Promise<Object>} Prediction result
 */
async function detectToxicity(text) {
    // implementation
}
```

---

## 🧪 Testing Guidelines

### Writing Tests

#### Unit Tests

```python
# tests/unit/test_feature.py
import pytest
from backend.services.feature import FeatureService

class TestFeatureService:
    def test_basic_operation(self):
        """Test basic operation works correctly."""
        service = FeatureService()
        result = service.process("input")
        assert result == "expected"
    
    @pytest.mark.parametrize("input,expected", [
        ("hello", "HELLO"),
        ("world", "WORLD"),
    ])
    def test_multiple_cases(self, input, expected):
        """Test multiple input cases."""
        service = FeatureService()
        assert service.upper(input) == expected
```

#### Integration Tests

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient

def test_predict_endpoint(client: TestClient, auth_headers):
    """Test prediction endpoint."""
    response = client.post(
        "/api/v1/predict",
        json={"text": "test"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "is_toxic" in response.json()
```

### Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/unit/test_cache.py -v

# With coverage
make test-coverage

# Watch mode (re-run on changes)
ptw tests/
```

### Coverage Requirements

- **Minimum**: 80% overall coverage
- **Target**: 90%+ for new features
- Check coverage: `pytest --cov=backend --cov-report=html`

---

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code is formatted (`make format`)
- [ ] Linters pass (`make lint`)
- [ ] All tests pass (`make test`)
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts with main

### PR Title

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user profile page
fix: resolve caching bug in Redis service
docs: update API documentation
test: add tests for rate limiter
refactor: improve model loading logic
perf: optimize database queries
chore: update dependencies
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issue
Fixes #123

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass locally
```

### Review Process

1. **Automated Checks** - CI/CD runs automatically
2. **Code Review** - Maintainers review your code
3. **Requested Changes** - Address feedback
4. **Approval** - Get approval from maintainers
5. **Merge** - Maintainer merges your PR

---

## 🐛 Issue Guidelines

### Before Creating an Issue

- Search existing issues to avoid duplicates
- Check if it's already fixed in main branch
- Collect relevant information

### Bug Report Template

```markdown
**Describe the Bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Windows 10]
- Python version: [e.g., 3.10]
- Browser: [e.g., Chrome 120]
- Extension version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information
```

### Feature Request Template

```markdown
**Is your feature related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
What you want to happen

**Describe alternatives you've considered**
Other solutions you've thought about

**Additional context**
Any other relevant information
```

---

## 🏷️ Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Formatting, missing semicolons, etc.
- **refactor**: Code restructuring
- **perf**: Performance improvement
- **test**: Adding tests
- **chore**: Maintenance tasks

### Examples

```bash
feat(api): add batch prediction endpoint

Implement endpoint for batch text predictions to improve
extension performance.

Closes #123

fix(cache): resolve Redis connection timeout

Add connection pooling and retry logic to handle
Redis connection issues gracefully.

Fixes #456

docs(readme): update installation instructions

Update setup guide with new Redis configuration steps.
```

---

## 📚 Resources

### Documentation

- [Project README](README.md)
- [Setup Guide](SETUP_AND_RUN_GUIDE.md)
- [API Documentation](http://localhost:7860/docs)
- [Architecture Overview](SYSTEM_ARCHITECTURE.md)

### Technologies

- [FastAPI](https://fastapi.tiangolo.com/)
- [Laravel](https://laravel.com/docs)
- [Chrome Extensions](https://developer.chrome.com/docs/extensions/)
- [Pytest](https://docs.pytest.org/)
- [Redis](https://redis.io/documentation)
- [Prometheus](https://prometheus.io/docs/)

### Style Guides

- [PEP 8](https://peps.python.org/pep-0008/) - Python
- [PSR-12](https://www.php-fig.org/psr/psr-12/) - PHP
- [Airbnb JavaScript](https://github.com/airbnb/javascript) - JavaScript

---

## 🎯 Development Tips

### VS Code Setup

```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true
}
```

### Git Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# This will run linters before each commit
```

### Debugging

```python
# Use logging instead of print
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

---

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and features
- **GitHub Discussions**: Q&A and ideas
- **Email**: support@yourdomain.com

### Response Time

- Issues: Within 48 hours
- Pull Requests: Within 1 week
- Security Issues: Within 24 hours

---

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing! 🎉

*Last Updated: 2025-10-19*

