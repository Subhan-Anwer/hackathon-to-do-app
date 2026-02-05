# Backend - FastAPI Application

## Current Structure

```
backend/
├── .venv/              # Virtual environment (managed by uv)
├── .python-version     # Python version (3.12)
├── main.py             # Application entry point
├── pyproject.toml      # Project configuration
├── uv.lock             # Dependency lock file
└── README.md
```

## Package Manager: uv

This project uses **uv** - a fast Python package manager and resolver written in Rust.

### Activate Virtual Environment

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Basic uv Commands

**Install Dependencies:**
```bash
# Install all dependencies from pyproject.toml
uv sync

# Install project in editable mode
uv pip install -e .
```

**Add New Packages:**
```bash
# Add a package and update pyproject.toml
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Examples:
uv add sqlmodel          # Add SQLModel for ORM
uv add pyjwt             # Add JWT support
uv add pytest --dev      # Add pytest as dev dependency
```

**Remove Packages:**
```bash
uv remove <package-name>
```

**Update Dependencies:**
```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add <package-name> --upgrade
```

**Run Python Scripts:**
```bash
# Run with uv (auto-activates venv)
uv run python main.py

# Or activate venv first, then run normally
source .venv/bin/activate
python main.py
```

## Working with requirements.txt

**Generate requirements.txt from pyproject.toml:**
```bash
uv pip freeze > requirements.txt
```

**Install from requirements.txt (if needed):**
```bash
uv pip install -r requirements.txt
```

**Note:** With uv, `pyproject.toml` and `uv.lock` are the source of truth. Only generate `requirements.txt` if needed for deployment or legacy compatibility.

## Current Dependencies

**Production:**
- `fastapi>=0.128.1` - Modern web framework

**Python Version:**
- Requires Python `>=3.12`

## Common Workflow

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Add a new dependency
uv add sqlmodel uvicorn

# 3. Run the application
python main.py
# or
uv run python main.py

# 4. Deactivate when done
deactivate
```

## Development Setup

```bash
# Initial setup (if .venv doesn't exist)
uv venv
source .venv/bin/activate
uv sync

# Start development
uv run uvicorn main:app --reload
```

## Notes

- No FastAPI app structure created yet (only basic main.py)
- No database models configured
- No authentication configured
- No API routes defined
- Ready for SQLModel ORM and JWT integration
