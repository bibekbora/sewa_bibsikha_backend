# FastAPI Tooling — Reference

Use this reference when choosing FastAPI-adjacent tooling.

## CLI

FastAPI supports:

```bash
fastapi dev
fastapi run
```

Prefer a configured application entrypoint where the project supports one.

## Related libraries

The current FastAPI skill recommends considering:

- `uv` for Python package management;
- Ruff for linting and formatting;
- `ty` where static type checking is configured;
- Asyncer when mixing blocking and async code;
- SQLModel for SQL database work where appropriate;
- HTTPX for HTTP clients.

Do not change the repository's tooling merely to follow a generic recommendation. The project's existing `uv`/Ruff/SQLModel/HTTPX conventions remain authoritative.
