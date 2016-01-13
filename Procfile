web: sh -c "cd HyberPayServer && gunicorn HyberPayServer.wsgi" --log-file -
worker: sh -c "cd HyberPayServer && celery -A HyberPayServer.celery worker" --loglevel=INFO