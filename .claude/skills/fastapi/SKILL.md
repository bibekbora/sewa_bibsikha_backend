---
name: fastapi
description: Production FastAPI guidance for APIs, dependencies, Pydantic v2, routing, response contracts, async/sync behavior, and FastAPI tooling. Use whenever implementing or reviewing FastAPI code.
---

# FastAPI

Use the official FastAPI conventions for framework behavior, while following the repository `CLAUDE.md` for all project-specific architecture and conventions.

## Reference Routing

Read only the relevant reference when the task needs deeper framework guidance:

- `references/dependencies.md` — dependency injection, `yield`, dependency scopes, and class dependencies.
- `references/path-operations.md` — path-operation and router patterns.
- `references/pydantic.md` — Pydantic v2 field/model patterns and validation.
- `references/responses.md` — response typing, response models, serialization, and filtering.
- `references/other-tools.md` — FastAPI CLI and related tooling/libraries.
- `references/streaming.md` — SSE, JSON Lines, and byte streaming. Read only for streaming work.

## Core Rules

- Prefer `Annotated` for FastAPI parameters and dependencies.
- Prefer typed return annotations when they represent the public response contract.
- Use `response_model` when the public schema differs from the internal return value.
- Do not use `...` as the required-field/default marker.
- Do not use Pydantic `RootModel` when an annotated type can express the desired API shape.
- Keep routers focused on HTTP concerns.
- Put router-level prefix, tags, and genuinely shared dependencies on `APIRouter`.
- Do not block the event loop. Use `async def` only with async-compatible, non-blocking work; use `def`/threadpool or explicit offloading for blocking work.
- Use one HTTP operation per path-operation function.
- Avoid deprecated response optimizations such as `ORJSONResponse`/`UJSONResponse`.
- Use FastAPI's current CLI (`fastapi dev` / `fastapi run`) where it fits the repository.
- For SSE/streaming, read `references/streaming.md` before implementing.
- No need to create migrations for new models or any changes to existing models , i will handle that, just make sure to add the new models to the `models` folder and import them in `models/__init__.py` and `migrations/env.py`.
- No need to create Test Cases for anything, i will handle that.

## Authority

When this skill conflicts with the project's `CLAUDE.md`, the project rules win. The references are framework guidance, not permission to change the project's architecture.
