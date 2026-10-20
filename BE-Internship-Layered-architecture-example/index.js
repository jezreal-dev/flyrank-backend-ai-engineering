// Entry point. Its ONLY job is to start the server.
// Everything about *what* the app does lives in src/app.js and the layers below it.
const { createApp } = require('./src/app');

const app = createApp();
const port = process.env.PORT || 3000;

app.listen(port, () => {
  console.log(`CRUD API listening on port ${port}`);
});
