import os

BACKEND_URL = os.environ.get(
    "BACKEND_URL",
    f"http://localhost:{os.environ.get('BACKEND_PORT', 5000)}",
)
