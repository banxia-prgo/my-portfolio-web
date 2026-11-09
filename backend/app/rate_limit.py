from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from fastapi import HTTPException, Request

_attempts: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()

def limit_attempts(request: Request, *, key: str, maximum: int, window_seconds: int) -> None:
    client = request.client.host if request.client else "unknown"
    bucket = f"{key}:{client}"
    now = monotonic()
    with _lock:
        events = _attempts[bucket]
        while events and now - events[0] > window_seconds:
            events.popleft()
        if len(events) >= maximum:
            raise HTTPException(status_code=429, detail="操作过于频繁，请稍后再试")
        events.append(now)
