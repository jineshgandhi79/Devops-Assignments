const request = require('supertest');
const app = require('../src/app');

describe('Payment Service Test Suite - CI/CD Automated Verification', () => {
  describe('GET /health', () => {
    it('should return 200 OK with healthy status and metadata', async () => {
      const res = await request(app).get('/health');
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('status', 'UP');
      expect(res.body).toHaveProperty('service', 'payment-gateway-service');
      expect(res.body).toHaveProperty('author', 'Jinesh Gandhi');
    });
  });

  describe('GET /api/v1/info', () => {
    it('should return system metadata and workflow details', async () => {
      const res = await request(app).get('/api/v1/info');
      expect(res.statusCode).toEqual(200);
      expect(res.body.message).toContain('Jinesh Gandhi');
      expect(res.body.pipeline).toEqual('GitHub Actions Multi-Stage Workflow');
    });
  });

  describe('POST /api/v1/payments/process', () => {
    it('should successfully process a valid transaction', async () => {
      const payload = {
        amount: 250.00,
        currency: 'USD',
        accountId: 'ACC-9821'
      };
      const res = await request(app)
        .post('/api/v1/payments/process')
        .send(payload);

      expect(res.statusCode).toEqual(201);
      expect(res.body.status).toEqual('SUCCESS');
      expect(res.body.transactionId).toMatch(/^TXN-[A-Z0-9]+$/);
      expect(res.body.fee).toEqual(3.75); // 1.5% fee
    });

    it('should reject payment when amount is missing or negative', async () => {
      const payload = {
        amount: -50,
        currency: 'USD',
        accountId: 'ACC-9821'
      };
      const res = await request(app)
        .post('/api/v1/payments/process')
        .send(payload);

      expect(res.statusCode).toEqual(400);
      expect(res.body).toHaveProperty('error', 'Invalid amount');
    });

    it('should reject payment when currency is invalid', async () => {
      const payload = {
        amount: 100,
        currency: 'US', // Less than 3 characters
        accountId: 'ACC-9821'
      };
      const res = await request(app)
        .post('/api/v1/payments/process')
        .send(payload);

      expect(res.statusCode).toEqual(400);
      expect(res.body).toHaveProperty('error', 'Invalid currency');
    });

    it('should reject payment when accountId is missing', async () => {
      const payload = {
        amount: 100,
        currency: 'USD'
      };
      const res = await request(app)
        .post('/api/v1/payments/process')
        .send(payload);

      expect(res.statusCode).toEqual(400);
      expect(res.body).toHaveProperty('error', 'Invalid account ID');
    });
  });

  describe('GET /api/v1/metrics', () => {
    it('should return operational telemetry', async () => {
      const res = await request(app).get('/api/v1/metrics');
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('memoryUsage');
      expect(res.body).toHaveProperty('cpuUsage');
    });
  });
});
