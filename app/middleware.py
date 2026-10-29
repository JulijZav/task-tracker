import time

from prometheus_client import Counter, Histogram

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

def get_route_label(request):
    route = request.scope.get("route")
    if route is None:
        return "unmatched"
    return route.path

async def metrics_middleware(request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        raise
    finally:
        duration = time.perf_counter() - start_time
        route = get_route_label(request)

        REQUEST_COUNT.labels(
            method=request.method,
            route=route,
            status_code=status_code
        ).inc()

        REQUEST_DURATION.labels(
            method=request.method,
            route=route
        ).observe(duration)

    return response