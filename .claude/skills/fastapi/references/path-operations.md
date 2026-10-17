# FastAPI Path Operations — Reference

Use this reference when designing or reviewing routes.

## Router organization

Prefer `APIRouter` with domain-level:

- `prefix`
- `tags`
- shared dependencies

Keep one HTTP operation per function.

Declare the public contract explicitly:

```python
@router.get(
    "/items",
    response_model=ItemListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_items(...) -> ItemListResponse:
    ...
```

Use `Annotated` for path/query/header metadata.

Keep path operations thin: extract HTTP input, call the application/service layer, and return the public response.

Repository rule: this project uses `routes/v1/routes.py` as the central router registration point and follows Route → Service → CRUD → DB.
