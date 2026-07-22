from pathlib import Path
from decouple import config
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static


# Generic configs
# ----------------------------------------------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ROOT_URLCONF = 'config.urls_main'
WSGI_APPLICATION = 'config.wsgi.application'

# -------------- Subdomain routing (school.oiq.kz) --------------
BASE_DOMAIN = config('BASE_DOMAIN', default='oiq.lvh.me')   # prod: .env-те oiq.kz
SCHOOL_HOST = f'school.{BASE_DOMAIN}'

ALLOWED_HOSTS = [BASE_DOMAIN, SCHOOL_HOST]
SESSION_COOKIE_DOMAIN = f'.{BASE_DOMAIN}'
CSRF_COOKIE_DOMAIN = f'.{BASE_DOMAIN}'

_scheme = 'http' if DEBUG else 'https'
_port = ':8000' if DEBUG else ''
CSRF_TRUSTED_ORIGINS = [f'{_scheme}://{BASE_DOMAIN}{_port}', f'{_scheme}://{SCHOOL_HOST}{_port}']


# -------------- Application definition --------------
INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'unfold.contrib.import_export',
    'unfold.contrib.guardian',
    'unfold.contrib.simple_history',
    'unfold.contrib.location_field',
    'unfold.contrib.constance',

    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tailwind',
    'ui',
    'core.apps.CoreConfig',

    # apps...
    'apps.catalog.apps.CatalogConfig',
    'apps.accounts.apps.AccountsConfig',

    'apps.main.apps.MainConfig',
    'apps.teaching.apps.TeachingConfig',
    'apps.learning.apps.LearningConfig',
    'apps.school.apps.SchoolConfig',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'config.middleware.HostURLConfMiddleware',
    'core.utils.middleware.CookieLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.school.middleware.OrganizationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    INSTALLED_APPS += ['django_browser_reload']
    MIDDLEWARE += [
        'django_browser_reload.middleware.BrowserReloadMiddleware',
    ]


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


# -------------- Database --------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_USER_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


# -------------- Password validation --------------
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


# -------------- Internationalization --------------
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


# -------------- Static files (CSS, JavaScript, Images) --------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'ui/static'
]


# Logging settings
# ----------------------------------------------------------------------------------------------------------------------
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


# AI API Key settings
# ----------------------------------------------------------------------------------------------------------------------
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
QUESTION_IMPORT_MODEL = config('QUESTION_IMPORT_MODEL', default='claude-opus-4-8')
QUESTION_IMPORT_MAX_FILE_SIZE = 20 * 1024 * 1024


# Templates settings
# ----------------------------------------------------------------------------------------------------------------------

# -------------- UI tailwind design system --------------
TAILWIND_APP_NAME = 'ui'


# Authentification settings
# ----------------------------------------------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'apps.accounts.backends.EmailOrUsernameBackend'
]

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'main:login'


# Email settings
# ----------------------------------------------------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')


# Unfold settings
# ----------------------------------------------------------------------------------------------------------------------
UNFOLD = {
    'SITE_TITLE': config('SITE_NAME'),
    'SITE_HEADER': config('SITE_NAME'),
    'SITE_SUBHEADER': _('Administration'),

    'LOGIN': {
        'image': lambda request: static('images/oiq-banner.svg'),
        'title': _('Dashboard'),
    },

    'SITE_URL': '/',
    'SITE_ICON': lambda request: static('images/icon.png'),
    'SITE_SYMBOL': 'speed',
    'SITE_FAVICONS': [
        {
            'rel': 'icon',
            'sizes': '32x32',
            'type': 'image/svg+xml',
            'href': lambda request: static('images/icon.png'),
        },
    ],
    'SHOW_LANGUAGES': True,
    'SITE_DROPDOWN': [
        {
            'icon': 'dashboard',
            'title': _('Administration'),
            'link': config('ADMIN_URL'),
        },
        {
            'icon': 'arrow_outward',
            'title': _('Website'),
            'link': config('WEBSITE_URL'),
            'attrs': {
                'target': '_blank',
            },
        },
    ],
    'SIDEBAR': {
        'show_search': True,
        'command_search': True,
        'show_all_applications': True,

        'navigation': [
            {
                'items': [
                    {
                        'title': _('Dashboard'),
                        'icon': 'dashboard',
                        'link': reverse_lazy('admin:index'),
                        # 'badge': '3',
                        # 'badge_variant': 'info',
                        # 'badge_style': 'solid',
                        'permission': lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                'title': _('Account'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': _('Users'),
                        'icon': 'account_circle',
                        'link': reverse_lazy('admin:accounts_user_changelist'),
                    },
                    {
                        'title': _('User sessions'),
                        'icon': 'admin_panel_settings',
                        'link': reverse_lazy('admin:accounts_usersession_changelist'),
                    },
                    # ...
                ],
            },
            {
                'title': _('Catalog'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': _('Cities'),
                        'icon': 'apartment',
                        'link': reverse_lazy('admin:catalog_city_changelist'),
                    },
                    {
                        'title': _('Schools'),
                        'icon': 'school',
                        'link': reverse_lazy('admin:catalog_school_changelist'),
                    },
                    {
                        'title': _('Grades'),
                        'icon': 'cast_for_education',
                        'link': reverse_lazy('admin:catalog_grade_changelist'),
                    },
                    {
                        'title': _('Subjects'),
                        'icon': 'book_2',
                        'link': reverse_lazy('admin:catalog_subject_changelist'),
                    },
                    {
                        'title': _('Question formats'),
                        'icon': 'quiz',
                        'link': reverse_lazy('admin:catalog_questionformat_changelist'),
                    },
                    {
                        'title': _('Questions'),
                        'icon': 'live_help',
                        'link': reverse_lazy('admin:catalog_question_changelist'),
                    },
                    # ...
                ],
            },
            {
                'title': _('School system'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': _('Organizations'),
                        'icon': 'corporate_fare',
                        'link': reverse_lazy('admin:school_organization_changelist'),
                    },
                    {
                        'title': _('Memberships'),
                        'icon': 'group',
                        'link': reverse_lazy('admin:school_membership_changelist'),
                    },
                ],
            },
        ],
    },

    'BORDER_RADIUS': '12px',
    'COLORS': {
        'primary': {
            '50': '#eef2ff',
            '100': '#e0e7ff',
            '200': '#c7d2fe',
            '300': '#a5b4fc',
            '400': '#818cf8',
            '500': "#6366f1",
            '600': '#4f46e5',
            '700': '#4338ca',
            '800': '#3730a3',
            '900': '#312e81',
            '950': '#1e1b4b',
        },
    },
}
