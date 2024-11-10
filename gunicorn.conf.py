import os

# Gunicorn config
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
workers = 3
timeout = 120
capture_output = True
accesslog = '-'
errorlog = '-' 