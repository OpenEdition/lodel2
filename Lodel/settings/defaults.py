DEBUG = True

TEMPLATE_DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(funcName)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'Lodel2.database': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'EditorialModel' : {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lodel2',
        'USER': 'lodel',
        'PASSWORD': 'bruno',
        'HOST': 'localhost',
    }
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

