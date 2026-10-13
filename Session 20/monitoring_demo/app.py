import time
import json
import logging
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import psutil
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "order-api", "message": "%(message)s"}'
)
logger = logging.getLogger("order-api")

# Prometheus Metrics Definitions
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency in seconds',
    ['endpoint']
)

SYSTEM_CPU_GAUGE = Gauge(
    'system_cpu_utilization_percent',
    'Current System CPU Utilization in percentage'
)

SYSTEM_MEMORY_GAUGE = Gauge(
    'system_memory_utilization_percent',
    'Current System Memory Utilization in percentage'
)

APP_HEALTH_STATUS = Gauge(
    'app_health_status',
    'Application health indicator (1 = healthy, 0 = degraded/unhealthy)'
)

# Simulated state
app_state = {
    "status": "UP",
    "database": "CONNECTED",
    "cache": "CONNECTED",
    "degraded_mode": False
}

class MetricsAndHealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        start_time = time.time()
        
        # Update system metrics on every request
        cpu_pct = psutil.cpu_percent(interval=None)
        mem_pct = psutil.virtual_memory().percent
        SYSTEM_CPU_GAUGE.set(cpu_pct)
        SYSTEM_MEMORY_GAUGE.set(mem_pct)

        if self.path == '/metrics':
            APP_HEALTH_STATUS.set(0 if app_state["degraded_mode"] else 1)
            output = generate_latest()
            self.send_response(200)
            self.send_header('Content-Type', CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(output)
            REQUEST_COUNT.labels(method='GET', endpoint='/metrics', http_status=200).inc()
            logger.info("Scraped /metrics endpoint successfully")

        elif self.path == '/health' or self.path == '/healthz':
            status_code = 503 if app_state["degraded_mode"] else 200
            resp = {
                "status": "DEGRADED" if app_state["degraded_mode"] else "HEALTHY",
                "uptime_seconds": round(time.time() - start_server_time, 2),
                "checks": {
                    "cpu_utilization_percent": cpu_pct,
                    "memory_utilization_percent": mem_pct,
                    "database": app_state["database"],
                    "redis_cache": app_state["cache"]
                }
            }
            body = json.dumps(resp, indent=2).encode('utf-8')
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            REQUEST_COUNT.labels(method='GET', endpoint='/health', http_status=status_code).inc()
            if app_state["degraded_mode"]:
                logger.warning(f"Health check warning: system running in degraded mode! CPU={cpu_pct}%, MEM={mem_pct}%")
            else:
                logger.info(f"Health check OK: CPU={cpu_pct}%, MEM={mem_pct}%")

        elif self.path.startswith('/api/orders'):
            # Simulate real endpoint
            latency = random.uniform(0.02, 0.15)
            time.sleep(latency)
            orders = [
                {"order_id": 1001, "customer": "Alice", "total": 249.99, "currency": "USD"},
                {"order_id": 1002, "customer": "Bob", "total": 89.50, "currency": "USD"},
                {"order_id": 1003, "customer": "Charlie", "total": 1220.00, "currency": "USD"}
            ]
            body = json.dumps({"orders": orders, "count": len(orders)}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            REQUEST_COUNT.labels(method='GET', endpoint='/api/orders', http_status=200).inc()
            REQUEST_LATENCY.labels(endpoint='/api/orders').observe(latency)
            logger.info(f"Order list fetched successfully (took {round(latency*1000, 1)}ms)")

        elif self.path == '/simulate/alert':
            # Trigger alert condition
            app_state["degraded_mode"] = True
            app_state["database"] = "HIGH_LATENCY_WARN"
            APP_HEALTH_STATUS.set(0)
            resp = {
                "alert": "TRIGGERED",
                "message": "High memory/CPU threshold crossed, app state set to DEGRADED",
                "alert_rule": "HighMemoryAndFailureRateThreshold"
            }
            body = json.dumps(resp).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            REQUEST_COUNT.labels(method='GET', endpoint='/simulate/alert', http_status=500).inc()
            logger.error("ALERT TRIGGERED: High error threshold reached in order processing pipeline!")

        elif self.path == '/simulate/recover':
            app_state["degraded_mode"] = False
            app_state["database"] = "CONNECTED"
            APP_HEALTH_STATUS.set(1)
            resp = {"status": "RESOLVED", "message": "Application health recovered to normal"}
            body = json.dumps(resp).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            logger.info("ALERT RESOLVED: System returned to nominal operating limits")

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')
            REQUEST_COUNT.labels(method='GET', endpoint='unknown', http_status=404).inc()

        duration = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint=self.path.split('?')[0]).observe(duration)

    def log_message(self, format, *args):
        # Suppress default BaseHTTPRequestHandler stdout noise to keep custom JSON logs clean
        pass

if __name__ == '__main__':
    start_server_time = time.time()
    server_address = ('127.0.0.1', 8000)
    httpd = HTTPServer(server_address, MetricsAndHealthHandler)
    logger.info("Starting Observability and Monitoring Demo Server on http://127.0.0.1:8000")
    print("Monitoring Demo Server running on http://127.0.0.1:8000")
    print("Endpoints:")
    print("  - http://127.0.0.1:8000/health (Application Health & System Utilization)")
    print("  - http://127.0.0.1:8000/metrics (Prometheus Exposition format)")
    print("  - http://127.0.0.1:8000/api/orders (Production Workload)")
    print("  - http://127.0.0.1:8000/simulate/alert (Trigger Alert threshold)")
    print("  - http://127.0.0.1:8000/simulate/recover (Recover Alert)")
    httpd.serve_forever()
