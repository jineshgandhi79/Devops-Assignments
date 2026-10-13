const express = require('express');
const client = require('prom-client');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;
const APP_ENV = process.env.APP_ENV || 'production';
const DATA_STORAGE_PATH = process.env.DATA_STORAGE_PATH || '/data/portal-data.log';

// Setup Prometheus metrics collection
const collectDefaultMetrics = client.collectDefaultMetrics;
collectDefaultMetrics({ timeout: 5000 });

const httpRequestCounter = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests processed by endpoint and status',
  labelNames: ['method', 'route', 'status_code']
});

const httpDurationSummary = new client.Summary({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route']
});

app.use(express.json());

// Request timing & metrics middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestCounter.inc({ method: req.method, route: req.path, status_code: res.statusCode });
    httpDurationSummary.observe({ method: req.method, route: req.path }, duration);
  });
  next();
});

// Root API Endpoint
app.get('/', (req, res) => {
  res.status(200).json({
    status: 'online',
    app: 'DevOps Enterprise Cloud Portal',
    version: '1.0.0',
    environment: APP_ENV,
    timestamp: new Date().toISOString()
  });
});

// Liveness Probe Endpoint (Checks if process is alive)
app.get('/healthz', (req, res) => {
  res.status(200).json({ status: 'healthy', check: 'liveness' });
});

// Readiness Probe Endpoint (Checks if application dependencies and storage are ready)
app.get('/ready', (req, res) => {
  try {
    // Verify storage directory/file access if mounted
    const dir = path.dirname(DATA_STORAGE_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.appendFileSync(DATA_STORAGE_PATH, `[${new Date().toISOString()}] Readiness check successful\n`);
    res.status(200).json({ status: 'ready', storage: 'connected', path: DATA_STORAGE_PATH });
  } catch (err) {
    res.status(503).json({ status: 'degraded', error: err.message });
  }
});

// Prometheus Metrics Scraping Endpoint
app.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', client.register.contentType);
    res.end(await client.register.metrics());
  } catch (ex) {
    res.status(500).end(ex);
  }
});

// DevOps status dashboard summary
app.get('/api/v1/system-status', (req, res) => {
  res.status(200).json({
    service: 'devops-portal-core',
    uptime_seconds: process.uptime(),
    memory_usage: process.memoryUsage(),
    cluster_node: process.env.NODE_NAME || 'k8s-worker-node-01',
    pod_name: process.env.POD_NAME || 'devops-portal-pod',
    region: process.env.AWS_REGION || 'us-east-1'
  });
});

// Start Server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`[DevOps Portal Service] Running on port ${PORT} in ${APP_ENV} mode`);
});

module.exports = app;
