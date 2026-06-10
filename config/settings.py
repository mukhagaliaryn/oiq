from pathlib import Path
from decouple import config, Csv
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static


# Generic configs
# ----------------------------------------------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


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
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tailwind',
    'ui',
    'core.apps.CoreConfig',

    # apps...
    'apps.dashboard.learner.apps.LearnerConfig',
    'apps.dashboard.teacher.apps.TeacherConfig',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
LANGUAGE_CODE = 'en-us'
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


# Templates settings
# ----------------------------------------------------------------------------------------------------------------------

# -------------- UI tailwind design system --------------
TAILWIND_APP_NAME = 'ui'


# Authentification settings
# ----------------------------------------------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'core.utils.backends.EmailOrUsernameBackend'
]

AUTH_USER_MODEL = 'core.User'


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
                        'badge': '3',
                        'badge_variant': 'info',
                        'badge_style': 'solid',
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
                        'link': reverse_lazy('admin:core_user_changelist'),
                    },
                    {
                        'title': _('User sessions'),
                        'icon': 'admin_panel_settings',
                        'link': reverse_lazy('admin:core_usersession_changelist'),
                    },
                    # ...
                ],
            },
            {
                'title': _('Education'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': _('Cities'),
                        'icon': 'apartment',
                        'link': reverse_lazy('admin:core_city_changelist'),
                    },
                    {
                        'title': _('Schools'),
                        'icon': 'school',
                        'link': reverse_lazy('admin:core_school_changelist'),
                    },
                    # ...
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
