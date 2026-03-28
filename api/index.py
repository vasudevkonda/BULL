"""
Vercel entrypoint.

Vercel's Python runtime cannot run Streamlit directly (Streamlit is a
long-running WebSocket server, not a WSGI/ASGI app). This handler
redirects visitors to your Streamlit Cloud deployment, which IS the
right platform for Streamlit apps.

Deployment options ranked by ease:
  1. Streamlit Community Cloud  — free, zero config, perfect for Streamlit
  2. Railway                    — free tier, one-click Docker deploy
  3. Render                     — free tier, similar to Railway
  4. Fly.io                     — great for production Docker workloads

See README.md for full deploy instructions for each platform.
"""

from http.server import BaseHTTPRequestHandler

# ── Update this URL after deploying to Streamlit Cloud / Railway ──────────
STREAMLIT_APP_URL = "https://your-app.streamlit.app"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", STREAMLIT_APP_URL)
        self.end_headers()

    def do_POST(self):
        self.do_GET()

    def log_message(self, format, *args):
        pass  # suppress default stderr logging
