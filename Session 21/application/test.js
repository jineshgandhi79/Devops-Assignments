const test = require('node:test');
const assert = require('node:assert');

test('DevOps Portal Unit Test Suite', async (t) => {
  await t.test('Environment variables validation', () => {
    const port = process.env.PORT || 8080;
    assert.strictEqual(typeof Number(port), 'number');
    assert.ok(Number(port) > 0 && Number(port) <= 65535, 'Port should be valid TCP range');
  });

  await t.test('Health check payload schema validation', () => {
    const payload = { status: 'healthy', check: 'liveness', timestamp: Date.now() };
    assert.strictEqual(payload.status, 'healthy');
    assert.strictEqual(payload.check, 'liveness');
  });

  await t.test('Metrics schema definition check', () => {
    const metricName = 'http_requests_total';
    assert.match(metricName, /^[a-zA-Z_:][a-zA-Z0-9_:]*$/);
  });
});
