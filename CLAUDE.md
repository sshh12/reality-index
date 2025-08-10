## Development Workflow

### General Preferences
- Do not hardcode fake test data. Instead prefer python script integration tests to figure out why things are failing.
- Do not use dummy data for fallbacks, instead hard fail when things do not work with detailed error messages.
- Prefer default constants only in the entrypoint but not in functions and classes within the package code.

### Entrypoint

- Use a `/main.py` as the main cli for running and integration testing the application.
- Put the majority of the application code within `/<module>/*.py`

### Deployment

- Setup a `railway.toml`, `Dockerfile`, and `entrypoint.sh`, `.dockerignore` for deploying the app to railway

### Virtual Environment

- Run python files with `source env.sh && PYTHONPATH=. python ...`
- If needed setup venv using `python -m venv .venv`
- Use existing venv and env.sh for API keys (OPENAI_API_KEY, POSTMARK_API_KEY, and POLYMARKET_SECRET_KEY already set)
- Create a `requirements.txt` if it doesn't exist and append as needed. Pin packages to major versions (pin to what pip install comes up with rather than your own guess).

### Formatting

- Run `black .` to format code (you may need to install in venv)

### Documentation

- `docs/openai-api.md`
- `docs/polymarket.md`

### README Guidelines

When creating or updating README files for projects:

- **Keep it high-level** - Focus on what the project does and how to run it, not implementation details
- **Avoid specific file references** - Don't mention specific filenames, modules, or code structure
- **Essential sections only**:
  - Project description and what it does
  - Quick start/setup instructions
  - Basic usage examples
  - Deployment instructions (Railway preferred)
- **Exclude these sections**:
  - Detailed feature lists
  - Cost estimates
  - Support/troubleshooting
  - "How it works" technical breakdowns
  - Specific configuration format details
- **Be concise** - READMEs should be scannable and focused on getting users started quickly