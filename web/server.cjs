/**
 * Foody web proxy (CommonJS). Serves /dist and proxies /api/v1/* to BACKEND_URL.
 */
const express = require('express');
const path = require('path');
const morgan = require('morgan');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 8080;
const BACKEND_URL = process.env.BACKEND_URL;

if (!BACKEND_URL) {
  console.warn('[web] BACKEND_URL is not set. API proxy will not work without it.');
}

app.set('trust proxy', 1);
app.use(morgan('combined'));

// Health endpoints
app.get('/health', (req, res) => res.json({ status: 'ok' }));
app.get('/ready', (req, res) => res.json({ status: 'ok' }));

// CORS for any static assets (fine) — API handled by backend CORS
app.use(cors());

// Proxy for /api and /api/v1 (no path rewrite)
if (BACKEND_URL) {
  const proxy = createProxyMiddleware({
    target: BACKEND_URL,
    changeOrigin: true,
    xfwd: true,
    logLevel: 'warn',
  });
  app.use('/api', proxy);
  app.use('/api/v1', proxy);
}

// Static files
const distDir = path.join(__dirname, 'dist');
app.use(express.static(distDir));

// Fallback to index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(distDir, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`[web] listening on ${PORT}, proxy → ${BACKEND_URL}`);
});
