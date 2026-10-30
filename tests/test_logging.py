import json
import logging

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.logging_config import JsonFormatter
from app.main import app

client = TestClient(app)

def setup_module():
    Base.metadata.create_all(bind=engine)

@app.get("/test-error")
def raise_error():
    raise RuntimeError("database is on fire")

def request_records(caplog):
    return [r for r in caplog.records if r.name == "task_tracker.request"]

def test_formatter_outputs_one_json_object():
    record = logging.LogRecord(
        "test", logging.INFO, __file__, 1, "hello %s", ("world",), None
    )
    record.route = "/tasks/{task_id}"

    line = JsonFormatter().format(record)
    data = json.loads(line)

    assert "\n" not in line
    assert data["route"] == "/tasks/{task_id}"
    assert data["level"] == "info"
    assert data["message"] == "hello world"

def test_request_is_logged_with_route(caplog):
    caplog.set_level(logging.INFO, logger="task_tracker.request")

    response = client.get("/tasks/")

    record = request_records(caplog)[-1]
    assert record.route == "/tasks/"
    assert record.status_code == 200
    assert record.request_id == response.headers["X-Request-Id"]

def test_health_is_not_logged_at_info(caplog):
    caplog.set_level(logging.INFO, logger="task_tracker.request")

    client.get("/health")

    assert request_records(caplog) == []

def test_unhandled_error_returns_500_and_is_logged(caplog):
    caplog.set_level(logging.INFO, logger="task_tracker.request")

    response = client.get("/test-error")

    assert response.status_code == 500
    record = request_records(caplog)[-1]
    assert record.levelname == "ERROR"
    assert record.route == "/test-error"
    assert "database is on fire" in JsonFormatter().format(record)