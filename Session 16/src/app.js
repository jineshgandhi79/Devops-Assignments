const express = require('express');
const app = express();

app.use(express.json());

// System health and readiness endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'UP',
    timestamp: new Date().toISOString(),
    service: 'payment-gateway-service',
    version: '1.0.0',
    uptime: process.uptime(),
    author: 'Jinesh Gandhi'
  });
});

// Root API Welcome endpoint
app.get('/api/v1/info', (req, res) => {
  res.status(200).json({
    message: 'CI/CD Pipeline Demo API by Jinesh Gandhi',
    environment: process.env.NODE_ENV || 'development',
    pipeline: 'GitHub Actions Multi-Stage Workflow',
    features: ['Build', 'Unit & Integration Testing', 'Dockerization', 'Staging Deploy', 'Production Rollout']
  });
});

// Core business logic: Process payment transaction
app.post('/api/v1/payments/process', (req, res) => {
  const { amount, currency, accountId } = req.body;

  if (!amount || typeof amount !== 'number' || amount <= 0) {
    return res.status(400).json({
      error: 'Invalid amount',
      message: 'Amount must be a positive numeric value'
    });
  }

  if (!currency || typeof currency !== 'string' || currency.length !== 3) {
    return res.status(400).json({
      error: 'Invalid currency',
      message: 'Currency must be a 3-letter ISO code (e.g., USD, EUR, INR)'
    });
  }

  if (!accountId) {
    return res.status(400).json({
      error: 'Invalid account ID',
      message: 'accountId is mandatory for transaction routing'
    });
  }

  const transactionId = 'TXN-' + Math.random().toString(36).substring(2, 10).toUpperCase();

  return res.status(201).json({
    status: 'SUCCESS',
    transactionId,
    accountId,
    amount,
    currency: currency.toUpperCase(),
    fee: parseFloat((amount * 0.015).toFixed(2)),
    processedAt: new Date().toISOString()
  });
});

// Metric telemetry endpoint
app.get('/api/v1/metrics', (req, res) => {
  res.status(200).json({
    memoryUsage: process.memoryUsage(),
    cpuUsage: process.cpuUsage(),
    nodeVersion: process.version
  });
});

module.exports = app;
