# FastAPI Dependency Injection — Reference

Use this reference when a task involves advanced FastAPI dependencies.

## Use dependencies for

- shared endpoint concerns;
- request-scoped resources;
- authentication/authorization;
- external resources requiring setup/cleanup;
- runtime validation that cannot be expressed cleanly as Pydantic validation;
- reusable dependency logic.

Prefer `Annotated[..., Depends(...)]` and reusable dependency aliases.

Example shape:

```python
from typing import Annotated
from fastapi import Depends

CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("/items")
async def list_items(current_user: CurrentUserDep): ...
```

For cleanup/resource lifetime work, use dependencies with `yield` and choose the appropriate dependency scope.

For shared router concerns, prefer `APIRouter(..., dependencies=[...])`.

Repository rule: use `SessionDep`, `CurrentUser`, and `CurrentAdmin` rather than inventing equivalent dependencies.
