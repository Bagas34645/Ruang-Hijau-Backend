# Gunicorn configuration file for Ruang Hijau Backend
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"

# Timeouts - CRITICAL for chatbot!
# First request may take 30-60 seconds while loading embedder model
timeout = 120  # 2 minutes for slow requests
keepalive = 2

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Process naming
proc_name = "ruang_hijau_backend"

# Server mechanics
daemon = False
pidfile = "gunicorn.pid"

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment
raw_env = [
    f"FLASK_ENV={os.environ.get('FLASK_ENV', 'production')}",
]

# Max requests before worker restart
max_requests = 1000
max_requests_jitter = 50

# Graceful timeout
graceful_timeout = 30

print("[gunicorn] Configuration loaded - timeout set to 120 seconds for chatbot support")
