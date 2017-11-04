web: bin/start-nginx bin/start-pgbouncer-stunnel newrelic-admin run-program gunicorn --pythonpath="$PWD/trackosaurus" wsgi:application
worker: bin/start-pgbouncer-stunnel python trackosaurus/manage.py rqworker default
