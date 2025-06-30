from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production!
SECRET_KEY = 'django-insecure-#fs5^#gsc+tuvh+pty=$p^0wq+*ip3*o0ojno&$a&l^pbfoeh%'

DEBUG = True

# Allow any IP for development and image distribution — fine for local use
ALLOWED_HOSTS = ['*']

# CSRF settings — safe default for local-only access
CSRF_TRUSTED_ORIGINS = []  # Empty is fine for HTTP usage only

# Only needed if you use HTTPS behind a proxy (not needed now)
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'kSipP',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

CACHE_MIDDLEWARE_SECONDS = 0
CACHE_MIDDLEWARE_KEY_PREFIX = None

ROOT_URLCONF = 'EasySipP.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI_APPLICATION = 'EasySipP.wsgi.application'
ASGI_APPLICATION = 'EasySipP.asgi.application'

# Localization
LANGUAGE_CODE = 'en-us'

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'collectstatic/'

# Databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {filename}:{lineno} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG' if DEBUG else 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG' if DEBUG else 'WARNING',
        },
        'django.server': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
