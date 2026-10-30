import logging
import time
import uuid

from prometheus_client import Counter, Histogram
from starlette.responses import JSONResponse

logger = logging.getLogger("task_tracker.request")

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "route", "status_code"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "route"],
    buckets=[0.01, 0.05, 0.1, 0.3, 0.5, 1.0, 5.0]
)

NOISY_ROUTES = {"/health", "/metrics"}


def get_route_label(request):
    route = request.scope.get("route")
    if route is None:
        return "unmatched"
    return route.path


async def request_middleware(request, call_next):
    request_id = uuid.uuid4().hex
    start_time = time.perf_counter()
    error = None

    try:
        response = await call_next(request)
    except Exception as exc: # noqa: BLE001
        error = exc
        response = JSONResponse({"detail": "Internal Server Error"}, status_code=500)

    duration = time.perf_counter() - start_time
    route = get_route_label(request)
    status_code = response.status_code

    REQUEST_COUNT.labels(
        method=request.method,
        route=route,
        status_code=status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        route=route
    ).observe(duration)

    if error is not None or status_code >= 500:
        level = logging.ERROR
    elif status_code >= 400:
        level = logging.WARNING
    elif route in NOISY_ROUTES:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger.log(
        level,
        "%s %s %s",
        request.method,
        request.url.path,
        status_code,
        exc_info=error,
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "route": route,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )

    response.headers["X-Request-ID"] = request_id
    return response