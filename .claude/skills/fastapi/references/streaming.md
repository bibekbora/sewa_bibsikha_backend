# FastAPI Streaming — Reference

Read this reference only for streaming work.

## Server-Sent Events

Use FastAPI's SSE response support and yield events from an async iterable.

Typical shape:

```python
from collections.abc import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent

app = FastAPI()


@app.get("/events", response_class=EventSourceResponse)
async def stream_events() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(data={"status": "started"}, event="status", id="1")
```

Use `ServerSentEvent` when event metadata such as `event`, `id`, or `retry` matters.

For JSON Lines or arbitrary byte streaming, use the appropriate streaming response pattern instead.

Repository rule: this reference is not automatically relevant to ordinary CRUD/API work. Read it only when the task actually introduces streaming.
