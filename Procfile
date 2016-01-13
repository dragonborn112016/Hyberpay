web: sh -c "cd HyberPayServer && gunicorn HyberPayServer.wsgi" --log-file -
worker: python HyberPayServer/manage.py celery worker -l info 