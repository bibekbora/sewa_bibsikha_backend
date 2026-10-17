---
name: database
description: Production SQLModel/SQLAlchemy database guidance for repositories, queries, relationships, transactions, loading strategies, and async persistence. Use when implementing or reviewing database access.
---

# Production Database Skill

This skill contains generic database engineering guidance. Repository-specific transaction ownership and naming conventions are defined in `CLAUDE.md`.

## Querying

- Prefer SQLModel/SQLAlchemy 2.0-style statement APIs.
- In this repository, the normal query idiom is `select()` from `sqlmodel` followed by `await session.exec(stmt)`.
- Keep result handling consistent with `session.exec()`; do not mix incompatible result assumptions from `session.execute()`.
- Avoid raw SQL unless the required operation cannot be expressed clearly and safely with the ORM/query builder.
- Parameterize all dynamic values.

## Repository Boundaries

- Repositories contain persistence logic, not business decisions.
- Keep query construction in repositories.
- Prefer reusable typed filters and list methods over a large collection of nearly identical lookup methods.
- Do not use `dict[str, Any]` as a generic escape hatch for repository APIs.
- Keep repository methods explicit about their inputs and return types.

## Transactions

- Transaction ownership must be clear.
- In this project, new business workflows own their transaction lifecycle in the service layer.
- Repositories should not commit by default.
- Do not introduce hidden commits inside a multi-step business workflow.
- Existing legacy repository commits are standing exceptions documented in `CLAUDE.md`.

## Relationships and Performance

- Avoid N+1 queries.
- Eager-load relationships that the caller will actually read using the appropriate loading strategy.
- Select only the columns/aggregates required when loading full ORM objects is unnecessary.
- Batch inserts/updates when doing repeated operations.
- Be deliberate about pagination and ordering for list endpoints.
- Avoid unbounded queries in API-facing repository methods.

## Async

- Do not block the event loop with synchronous database/network operations.
- Use the project's async session and driver consistently.
- Do not create ad-hoc sessions inside repositories when a managed session is already supplied by the service/dependency layer.

## Safety

- Never interpolate user input into SQL.
- Validate business constraints at the appropriate service/domain boundary.
- Do not leak database-driver exceptions to API clients.
- Preserve consistent error handling and logging conventions from `CLAUDE.md`.
