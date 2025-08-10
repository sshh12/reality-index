## Development Workflow

### General preferences
- Do not hardcode fake test data. Instead prefer python script integration tests to figure out why things are failing.
- Do not use dummy data for fallbacks, instead hard fail when things do not work with detailed error messages.

### Entrypoint

- Use a `/main.py` as the main cli for running and integration testing the application.
- Put the majority of the application code within `/<module>/*.py`

### Deployment

- Setup a `railway.toml`, `Dockerfile`, and `entrypoint.sh`, `.dockerignore` for deploying the app to railway

### Virtual Environment

- Run python files with `source env.sh && PYTHONPATH=. python ...`
- If needed setup venv using `python -m venv .venv`
- Use existing venv and env.sh for API keys (OPENAI_API_KEY and POLYMARKET_SECRET_KEY already set)
- Create a `requirements.txt` if it doesn't exist and append as needed. Pin packages to major versions (pin to what pip install comes up with rather than your own guess).

### Formatting

- Run `black .` to format code (you may need to install in venv)

### Useful Documentation

- `docs/openai-api.md`
- `docs/polymarket.md`