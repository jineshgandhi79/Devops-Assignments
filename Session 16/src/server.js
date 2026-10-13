const app = require('./app');

const PORT = process.env.PORT || 3000;

const server = app.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(` Payment Service running on port ${PORT}`);
  console.log(` Author: Jinesh Gandhi`);
  console.log(` Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(` CI/CD Pipeline Demo Ready`);
  console.log(`====================================================`);
});

process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    console.log('HTTP server closed gracefully');
  });
});
