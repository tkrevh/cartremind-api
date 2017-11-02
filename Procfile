web: newrelic-admin run-program gunicorn --pythonpath="$PWD/trackosaurus" wsgi:application
worker: python trackosaurus/manage.py rqworker default