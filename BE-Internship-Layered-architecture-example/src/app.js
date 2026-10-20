// The "wiring" layer: build the Express app and connect the pieces together.
// Notice it knows nothing about tasks, validation, or storage — it just plugs
// the routes and the error handler into Express.
const express = require('express');
const swaggerUi = require('swagger-ui-express');
const openapi = require('../openapi.json');

const metaRoutes = require('./routes/meta.routes');
const tasksRoutes = require('./routes/tasks.routes');
const { errorHandler } = require('./middleware/error-handler');

function createApp() {
  const app = express();

  // Parse JSON request bodies.
  app.use(express.json());

  // Stage 5 — Swagger UI at /docs
  app.use('/docs', swaggerUi.serve, swaggerUi.setup(openapi));

  // Feature routes (the HTTP layer). Each router is thin: it reads the request,
  // calls a service, and formats the response.
  app.use('/', metaRoutes);
  app.use('/', tasksRoutes);

  // One place that turns thrown errors into HTTP status codes. Must be last.
  app.use(errorHandler);

  return app;
}

module.exports = { createApp };
