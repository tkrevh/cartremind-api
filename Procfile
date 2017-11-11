web: bin/start-nginx bin/start-pgbouncer-stunnel newrelic-admin run-program gunicorn -c gunicorn.conf --pythonpath="$PWD/trackosaurus" wsgi:application
worker: bin/start-pgbouncer-stunnel newrelic-admin run-program celery -A trackosaurus worker -l info -c 4
# worker: bin/start-pgbouncer-stunnel python trackosaurus/manage.py rqworker default