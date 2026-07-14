"""Lightweight Prometheus metrics for Flask (no extra dependency)."""
from functools import wraps
import time

from flask import request, g
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)


class PrometheusMetrics:
    """Auto-instrument Flask with request count and latency."""

    def __init__(self, app=None):
        self.request_count = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
        )
        self.request_latency = Histogram(
            "http_request_duration_seconds",
            "Request latency in seconds",
            ["method", "endpoint"],
        )
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self._before)
        app.after_request(self._after)

        @app.route("/metrics")
        def metrics():
            return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    @staticmethod
    def _before():
        g._start_time = time.time()

    def _after(self, response):
        latency = time.time() - getattr(g, "_start_time", time.time())
        endpoint = request.endpoint or "unknown"
        self.request_count.labels(request.method, endpoint, response.status_code).inc()
        self.request_latency.labels(request.method, endpoint).observe(latency)
        return response
