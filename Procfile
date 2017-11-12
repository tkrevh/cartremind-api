web: bin/start-nginx bin/start-pgbouncer-stunnel newrelic-admin run-program gunicorn -c gunicorn.conf --pythonpath="$PWD/trackosaurus" wsgi:application --access-logfile=- --error-logfile=-
worker: bin/start-pgbouncer-stunnel celery -A trackosaurus.celeryapp worker -l info -c 4
# worker: bin/start-pgbouncer-stunnel python trackosaurus/manage.py rqworker default