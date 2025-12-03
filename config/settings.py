from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG') == 'True'
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')


# Application definition
# ----------------------------------------------------------------------------------------------------------------------
INSTALLED_APPS = [
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tailwind',
    'ui',
    'ckeditor',

    # core apps...
    'core.apps.CoreConfig',

    # view apps...
    'apps.main.apps.MainConfig',
    'apps.learner.apps.LearnerConfig',
    'apps.teacher.apps.TeacherConfig',
]

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'config.middleware.ForceKazakhLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

if DEBUG:
    INSTALLED_APPS += ['django_browser_reload']
    MIDDLEWARE += [
        'django_browser_reload.middleware.BrowserReloadMiddleware',
    ]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'ui/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Database
# ----------------------------------------------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_USER_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# ----------------------------------------------------------------------------------------------------------------------
LANGUAGE_CODE = 'kk'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

LANGUAGES = (
    ('kk', _('Kazakh')),
    ('ru', _('Russian')),
    ('en', _('English')),
)

LOCALE_PATHS = [
    BASE_DIR / 'locales'
]

LANGUAGE_COOKIE_NAME = 'language'


# Static files (CSS, JavaScript, Images)
# ----------------------------------------------------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'ui/static'
]


# Templates settings
# ----------------------------------------------------------------------------------------------------------------------
# UI tailwind design system
TAILWIND_APP_NAME = 'ui'


# Default primary key field type
# ----------------------------------------------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS, API settings
# ----------------------------------------------------------------------------------------------------------------------
X_FRAME_OPTIONS = 'SAMEORIGIN'
SILENCED_SYSTEM_CHECKS = ['security.W019']



# Authentification settings
# ----------------------------------------------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'core.utils.db.backends.EmailOrUsernameModelBackend',
]

AUTH_USER_MODEL = 'core.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'post_login_redirect'
LOGOUT_REDIRECT_URL = 'login'


# CKEditor settings
# ----------------------------------------------------------------------------------------------------------------------
CKEDITOR_UPLOAD_PATH = 'uploads/'

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'defaultLanguage': 'ru',

        'toolbar': [
            {
                'name': 'styles',
                'items': ['Format']
            },
            {
                'name': 'basicstyles',
                'items': ['Bold', 'Italic', 'Underline', '-', 'RemoveFormat']
            },
            {
                'name': 'paragraph',
                'items': [
                    'NumberedList', 'BulletedList', '-',
                    'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock',
                ]
            },
            {
                'name': 'insert',
                'items': ['Image', 'Table', 'Mathjax', ]
            },
            {
                'name': 'document',
                'items': ['Source', '-', 'Preview', '-', 'Maximize']
            },
        ],
        'format_tags': 'p;h2;h3;h4',

        'mathJaxLib': 'https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,

        'extraPlugins': ','.join([
            'mathjax',
            'uploadimage',
            'autogrow',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath',
        ]),
    }
}