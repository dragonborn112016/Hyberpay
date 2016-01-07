web: sh -c "cd HyberPayServer && gunicorn HyberPayServer.wsgi" --log-file -
worker: sh -c "cd HyberPayServer && python manage.py celeryd"