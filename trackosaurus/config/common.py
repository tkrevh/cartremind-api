import os

try:
    # Python 2.x
    import urlparse
except ImportError:
    # Python 3.x
    from urllib import parse as urlparse

from os.path import join

from configurations import Configuration, values

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Common(Configuration):

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',


        # Third party apps
        'rest_framework',            # utilities for rest apis
        'rest_framework.authtoken',  # token authentication
        # 'django_rq',                 # asynchronous queuing
        'versatileimagefield',       # image manipulation
        'corsheaders',               # Cross Origin Resource Sharing Headers

        # Your apps
        'authentication',
        'users',
        'core'

    )

    # https://docs.djangoproject.com/en/1.10/topics/http/middleware/
    MIDDLEWARE = (
        'corsheaders.middleware.CorsMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'qinspect.middleware.QueryInspectMiddleware',
    )

    ROOT_URLCONF = 'trackosaurus.urls'

    SECRET_KEY = 'Not a secret'
    WSGI_APPLICATION = 'wsgi.application'

    # Email
    EMAIL_BACKEND = values.Value('django.core.mail.backends.smtp.EmailBackend')

    ADMINS = (
        ('Author', 'tadej.krevh@gmail.com'),
    )

    # Postgres
    DATABASES = values.DatabaseURLValue('postgres://postgres:postgres@localhost:5433/trackosaurus')

    # General
    APPEND_SLASH = values.BooleanValue(False)
    TIME_ZONE = 'UTC'
    LANGUAGE_CODE = 'en-us'
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = '/'

    # Static Files
    STATIC_ROOT = join(os.path.dirname(BASE_DIR), 'staticfiles')
    STATICFILES_DIRS = [join(os.path.dirname(BASE_DIR), 'static'), ]
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), 'media')
    MEDIA_URL = '/media/'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': STATICFILES_DIRS,
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages'
                ],
                'loaders':[
                    ('django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ]),
                ],
            },
        },
    ]

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = values.BooleanValue(False)
    for config in TEMPLATES:
        config['OPTIONS']['debug'] = DEBUG

    # Password Validation
    # https://docs.djangoproject.com/en/1.10/topics/auth/passwords/#module-django.contrib.auth.password_validation
    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 9,
            }
        },
    ]

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'django.server': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(server_time)s] %(message)s',
            },
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
            'rq_console': {
                'format': '%(asctime)s %(message)s',
                'datefmt': '%H:%M:%S',
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'django.server': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'django.server',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'rq_console': {
                'level': 'DEBUG',
                'class': 'rq.utils.ColorizingStreamHandler',
                'formatter': 'rq_console',
                'exclude': ['%(asctime)s'],
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'propagate': True,
            },
            'django.server': {
                'handlers': ['django.server'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': False,
            },
            'rq.worker': {
                'handlers': ['rq_console'],
                'level': 'DEBUG'
            },
            'qinspect': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'trackosaurus.core': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'trackosaurus': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }

    # Custom user app
    AUTH_USER_MODEL = 'users.User'

    # Django Rest Framework
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': int(os.getenv('DJANGO_PAGINATION_LIMIT', 10)),
        'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
            'users.permissions.HasAPIAccess',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
            'users.authentication.ApiKeyAuthentication'
        )
    }

    # Versatile Image Field
    VERSATILEIMAGEFIELD_SETTINGS = {
        # The amount of time, in seconds, that references to created images
        # should be stored in the cache. Defaults to `2592000` (30 days)
        'cache_length': 2592000,
        'cache_name': 'versatileimagefield_cache',
        'jpeg_resize_quality': 70,
        'sized_directory_name': '__sized__',
        'filtered_directory_name': '__filtered__',
        'placeholder_directory_name': '__placeholder__',
        'create_images_on_demand': False
    }

    # django-rq
    # Adds dashboard link for queues in /admin, This will override the default
    # admin template so it may interfere with other apps that modify the
    # default admin template. If you're using such an app, simply remove this.
    RQ_SHOW_ADMIN_LINK = True

    # Whether the Query Inspector should do anything (default: False)
    QUERY_INSPECT_ENABLED = True
    # Whether to log the stats via Django logging (default: True)
    QUERY_INSPECT_LOG_STATS = True
    # Whether to add stats headers (default: True)
    QUERY_INSPECT_HEADER_STATS = True
    # Whether to log duplicate queries (default: False)
    QUERY_INSPECT_LOG_QUERIES = True
    # Whether to log queries that are above an absolute limit (default: None - disabled)
    QUERY_INSPECT_ABSOLUTE_LIMIT = 100  # in milliseconds
    # Whether to log queries that are more than X standard deviations above the mean query time
    # (default: None - disabled)
    QUERY_INSPECT_STANDARD_DEVIATION_LIMIT = 2
    # Whether to include tracebacks in the logs (default: False)
    QUERY_INSPECT_LOG_TRACEBACKS = True
    # Project root (a list of directories, see below - default empty)
    QUERY_INSPECT_TRACEBACK_ROOTS = [BASE_DIR]

    # CORS SETTINGS
    CORS_ORIGIN_ALLOW_ALL = True

    # SITE SETTINGS
    HOMEPAGE_URL = 'https://trackosaurus.io'

    # Caching
    REDIS_URL = os.environ.get('REDISCLOUD_URL', 'redis://127.0.0.1:6379/1')
    parsed_redis_url = urlparse.urlparse(os.environ.get('REDISCLOUD_URL', 'redis://127.0.0.1:6379/1'))
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '{}:{}'.format(parsed_redis_url.hostname, parsed_redis_url.port),
            'OPTIONS': {
                'DB': 0,
                'PASSWORD': parsed_redis_url.password,
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
                'CONNECTION_POOL_CLASS_KWARGS': {
                    'max_connections': 50,
                    'timeout': 20,
                }
            }
        }
    }

    BROKER_URL=REDIS_URL