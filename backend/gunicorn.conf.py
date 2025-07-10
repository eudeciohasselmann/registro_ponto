import os

# Configurações do servidor
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv('WEB_CONCURRENCY', '1'))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de processo
preload_app = True
daemon = False
pidfile = None
tmp_upload_dir = None

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
