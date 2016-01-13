web: sh -c "cd HyberPayServer && gunicorn HyberPayServer.wsgi" --log-file -
worker: celery worker --app=tasks.app --loglevel=INFO