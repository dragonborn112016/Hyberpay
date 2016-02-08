web: sh -c "cd HyberPayServer && gunicorn HyberPayServer.wsgi" --log-file -
worker: python HyberPayServer/manage.py celeryd -l info 