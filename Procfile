web: sh -c "cd HyberPayServer && gunicorn HyberPayServer.wsgi" --log-file -
worker: heroku run python HyberPayServer/manage.py celeryd --loglevel=INFO