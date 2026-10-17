# Pydantic v2 — Reference

Use this reference for Pydantic/FastAPI schema work.

## Required fields

Do not use `...` to mark a required field.

Prefer:

```python
class Item(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    price: Annotated[float, Field(gt=0)]
```

instead of the legacy `Field(...)` form.

## Metadata

Prefer `Annotated[T, Field(...metadata...)]` for field metadata.

Avoid redundant defaults.

Keep request and response schemas separate when their contracts differ.

For ORM-backed response schemas, use:

```python
model_config = ConfigDict(from_attributes=True)
```

Do not introduce `RootModel` when a normal annotated type plus Pydantic validation can express the API contract.

Repository rule: `models/` uses SQLModel's field/column declarations; the Pydantic `Annotated` rule applies to `schemas/`.
