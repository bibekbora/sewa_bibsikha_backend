# FastAPI Responses — Reference

Use this reference when designing response contracts.

## Prefer typed return contracts

A return annotation can define the public response contract when the internal value already matches it.

Use `response_model` when the public schema differs from the internal return value.

Response models provide validation, serialization, documentation, and filtering of fields.

Do not assume returning a concrete `Response` object will still trigger normal response-model processing.

Example:

```python
@router.get("/items", response_model=ItemListResponse)
async def list_items() -> ItemListResponse:
    return result
```

## Security

Treat response schemas as a data-exposure boundary. Never accidentally return secrets, password hashes, tokens, or internal-only fields.

Repository rule: new/modified endpoints use the project's `ApiResponse[T]` envelope and must not return `JSONResponse` together with `response_model`.
