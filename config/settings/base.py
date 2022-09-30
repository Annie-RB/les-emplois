"""
Base settings to build other settings files upon.
https://docs.djangoproject.com/en/dev/ref/settings
"""
import datetime
import json
import os

from dotenv import load_dotenv


load_dotenv()

from django.utils import timezone


# Django settings
# ---------------

_current_dir = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(_current_dir, "../.."))

APPS_DIR = os.path.abspath(os.path.join(ROOT_DIR, "itou"))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "inclusion.beta.gouv.fr,emplois.inclusion.beta.gouv.fr").split(",")

SITE_ID = 1

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.gis",
    "django.contrib.postgres",
    "django.forms",  # Required to override default Django widgets. See FORM_RENDERER
]

THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "anymail",
    "bootstrap4",
    "django_select2",
    "huey.contrib.djhuey",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "django_filters",
    "import_export",
    "hijack",
    "hijack.contrib.admin",
    "elasticapm.contrib.django",
]


LOCAL_APPS = [
    "itou.utils",
    "itou.cities",
    "itou.jobs",
    "itou.users",
    "itou.siaes",
    "itou.prescribers",
    "itou.institutions",
    "itou.job_applications",
    "itou.approvals",
    "itou.eligibility",
    "itou.openid_connect.france_connect",
    "itou.openid_connect.inclusion_connect",
    "itou.invitations",
    "itou.external_data",
    "itou.metabase",
    "itou.asp",
    "itou.employee_record",
    "itou.siae_evaluations",
    "itou.www.apply",
    "itou.www.approvals_views",
    "itou.www.autocomplete",
    "itou.www.dashboard",
    "itou.www.eligibility_views",
    "itou.www.home",
    "itou.www.prescribers_views",
    "itou.www.search",
    "itou.www.siaes_views",
    "itou.www.signup",
    "itou.www.invitations_views",
    "itou.www.stats",
    "itou.www.welcoming_tour",
    "itou.www.employee_record_views",
    "itou.www.siae_evaluations_views",
    "itou.api",
    "itou.status",
    "itou.scripts",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


DJANGO_MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "hijack.middleware.HijackUserMiddleware",
]

ITOU_MIDDLEWARE = [
    "itou.utils.new_dns.middleware.NewDnsRedirectMiddleware",
    "itou.utils.perms.middleware.ItouCurrentOrganizationMiddleware",
]

MIDDLEWARE = DJANGO_MIDDLEWARE + ITOU_MIDDLEWARE

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(APPS_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "itou.utils.perms.context_processors.get_current_organization_and_perms",
                "itou.utils.settings_context_processors.expose_settings",
            ]
        },
    }
]

# Override default Django forms widgets templates.
# Requires django.forms in INSTALLED_APPS
# https://timonweb.com/django/overriding-field-widgets-in-django-doesnt-work-template-not-found-the-solution/
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# Note how we use Clever Cloud environment variables here. No way for now to alias them :/
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("POSTGRESQL_ADDON_DB"),
        # FIXME(vperron): We should get rid of those Clever Cloud proprietary values in our code
        # and alias them as soon as we can in our pre-build and pre-run scripts. But those scripts
        # will be defined in a later PR.
        "HOST": os.getenv("POSTGRESQL_ADDON_DIRECT_HOST") or os.getenv("POSTGRESQL_ADDON_HOST"),
        "PORT": os.getenv("POSTGRESQL_ADDON_DIRECT_PORT") or os.getenv("POSTGRESQL_ADDON_PORT"),
        "USER": os.getenv("POSTGRESQL_ADDON_CUSTOM_USER") or os.getenv("POSTGRESQL_ADDON_USER"),
        "PASSWORD": os.getenv("POSTGRESQL_ADDON_CUSTOM_PASSWORD") or os.getenv("POSTGRESQL_ADDON_PASSWORD"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "itou.utils.password_validation.CnilCompositionPasswordValidator"},
]

LANGUAGE_CODE = "fr-FR"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True

DATE_INPUT_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", "%d %m %Y"]

STATIC_ROOT = os.path.join(APPS_DIR, "static_collected")

STATIC_URL = "/static/"

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATICFILES_DIRS = (os.path.join(APPS_DIR, "static"),)

CSRF_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SECURE = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SESSION_SERIALIZER = "itou.utils.session.JSONSerializer"

X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "null": {"class": "logging.NullHandler"},
        "api_console": {
            "class": "logging.StreamHandler",
            "formatter": "api_simple",
        },
    },
    "formatters": {
        "api_simple": {
            "format": "{levelname} {asctime} {pathname} : {message}",
            "style": "{",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
        # Silence `Invalid HTTP_HOST header` errors.
        # This should be done at the HTTP server level when possible.
        # https://docs.djangoproject.com/en/3.0/topics/logging/#django-security
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
        "itou": {
            "handlers": ["console"],
            "level": os.getenv("ITOU_LOG_LEVEL", "INFO"),
        },
        # Logger for DRF API application
        # Will be "log-drained": may need to adjust format
        "api_drf": {
            "handlers": ["api_console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
        # Huey; async tasks
        "huey": {
            "handlers": ["console"],
            "level": os.getenv("HUEY_LOG_LEVEL", "WARNING"),
        },
    },
}

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# User authentication callbacks such as redirections after login.
# Replaces LOGIN_REDIRECT_URL, which is static, by ACCOUNT_ADAPTER which is dynamic.
# https://django-allauth.readthedocs.io/en/latest/advanced.html#custom-redirects
ACCOUNT_ADAPTER = "itou.users.adapter.UserAdapter"

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5  # Protects only the allauth login view.
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 600  # Seconds.
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_DISPLAY = "itou.users.models.get_allauth_account_user_display"

BOOTSTRAP4 = {
    "required_css_class": "form-group-required",
    # Remove the default `.is-valid` class that Bootstrap will style in green
    # otherwise empty required fields will be marked as valid. This might be
    # a bug in django-bootstrap4, it should be investigated.
    "success_css_class": "",
}


# This trick
# https://github.com/pennersr/django-allauth/issues/749#issuecomment-70402595
# fixes the following issue
# https://github.com/pennersr/django-allauth/issues/749
# Without this trick, python manage.py makemigrations
# would want to create a migration in django-allauth dependency
# /usr/local/lib/python3.9/site-packages/allauth/socialaccount/migrations/0004_auto_20200415_1510.py
# - Alter field provider on socialaccount
# - Alter field provider on socialapp
#
# This setting redirects the migrations for socialaccount to our directory
MIGRATION_MODULES = {
    "socialaccount": "itou.allauth_adapters.migrations",
}


# ITOU settings
# -------------


# Environment, sets the type of env of the app (PROD, FAST-MACHINE, STAGING, DEMO, DEV…)
ITOU_ENVIRONMENT = os.getenv("ITOU_ENVIRONMENT", "PROD")
ITOU_PROTOCOL = "https"
ITOU_FQDN = os.getenv("ITOU_FQDN", "emplois.inclusion.beta.gouv.fr")
ITOU_EMAIL_CONTACT = os.getenv("ITOU_EMAIL_CONTACT", "assistance@inclusion.beta.gouv.fr")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@inclusion.beta.gouv.fr")


_sentry_dsn = os.getenv("SENTRY_DSN")
if _sentry_dsn:
    from ._sentry import sentry_init

    sentry_init(dsn=_sentry_dsn)

SHOW_TEST_ACCOUNTS_BANNER = ITOU_ENVIRONMENT in ("DEMO", "REVIEW-APP")

# On November 30th, 2021, we delivered approvals for AI structures.
# See itou.scripts.management.commands.import_ai_employees
AI_EMPLOYEES_STOCK_DEVELOPER_EMAIL = os.getenv("AI_EMPLOYEES_STOCK_DEVELOPER_EMAIL")
AI_EMPLOYEES_STOCK_IMPORT_DATE = datetime.datetime(2021, 11, 30, tzinfo=timezone.utc)

# https://adresse.data.gouv.fr/faq
API_BAN_BASE_URL = os.getenv("API_BAN_BASE_URL")

# https://api.gouv.fr/api/api-geo.html#doc_tech
API_GEO_BASE_URL = os.getenv("API_GEO_BASE_URL")

API_INSEE_BASE_URL = os.getenv("API_INSEE_BASE_URL")
API_INSEE_CONSUMER_KEY = os.getenv("API_INSEE_CONSUMER_KEY")
API_INSEE_CONSUMER_SECRET = os.getenv("API_INSEE_CONSUMER_SECRET")

# https://api.gouv.fr/documentation/sirene_v3
API_ENTREPRISE_BASE_URL = f"{API_INSEE_BASE_URL}/entreprises/sirene/V3"

# Pôle emploi's Emploi Store Dev aka ESD. There is a production AND a recette environment.
# Key and secrets are stored on pole-emploi.io (prod and recette) accounts, the values are not the
# same depending on the environment
# Please note that some of APIs have a dry run mode which is handled through (possibly undocumented) scopes
API_ESD = {
    "AUTH_BASE_URL": os.getenv("API_ESD_AUTH_BASE_URL"),
    "KEY": os.getenv("API_ESD_KEY"),
    "SECRET": os.getenv("API_ESD_SECRET"),
    "BASE_URL": os.getenv("API_ESD_BASE_URL"),
}

# PE Connect aka PEAMU - technically one of ESD's APIs.
# PEAM stands for Pôle emploi Access Management.
# Technically there are two PEAM distinct systems:
# - PEAM "Entreprise", PEAM-E or PEAME for short.
# - PEAM "Utilisateur", PEAM-U or PEAMU for short.
# To avoid confusion between the two when contacting ESD support,
# we get the habit to always explicitely state that we are using PEAM*U*.
PEAMU_AUTH_BASE_URL = os.getenv("PEAMU_AUTH_BASE_URL")
SOCIALACCOUNT_PROVIDERS = {
    "peamu": {
        "APP": {"key": "peamu", "client_id": API_ESD["KEY"], "secret": API_ESD["SECRET"]},
    },
}
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_ADAPTER = "itou.allauth_adapters.peamu.adapter.PEAMUSocialAccountAdapter"

# France Connect https://partenaires.franceconnect.gouv.fr/
FRANCE_CONNECT_BASE_URL = os.getenv("FRANCE_CONNECT_BASE_URL")
FRANCE_CONNECT_CLIENT_ID = os.getenv("FRANCE_CONNECT_CLIENT_ID")
FRANCE_CONNECT_CLIENT_SECRET = os.getenv("FRANCE_CONNECT_CLIENT_SECRET")

INCLUSION_CONNECT_BASE_URL = os.getenv("INCLUSION_CONNECT_BASE_URL")
INCLUSION_CONNECT_REALM = os.getenv("INCLUSION_CONNECT_REALM")
INCLUSION_CONNECT_CLIENT_ID = os.getenv("INCLUSION_CONNECT_CLIENT_ID")
INCLUSION_CONNECT_CLIENT_SECRET = os.getenv("INCLUSION_CONNECT_CLIENT_SECRET")

TALLY_URL = os.getenv("TALLY_URL")

# Metabase should only ever be populated:
# - from a fast machine (by clever cloud cronjob or manually by Supportix)
# - from local dev with latest production dataset (by experienced Metabase developers only)
# but not from prod, demo, staging or review apps.
ALLOW_POPULATING_METABASE = ITOU_ENVIRONMENT in ("FAST-MACHINE", "DEV")

METABASE_HOST = os.getenv("METABASE_HOST")
METABASE_PORT = os.getenv("METABASE_PORT")
METABASE_DATABASE = os.getenv("METABASE_DATABASE")
METABASE_USER = os.getenv("METABASE_USER")
METABASE_PASSWORD = os.getenv("METABASE_PASSWORD")

# Embedding signed Metabase dashboard
METABASE_SITE_URL = os.getenv("METABASE_SITE_URL")
METABASE_SECRET_KEY = os.getenv("METABASE_SECRET_KEY")

ASP_ITOU_PREFIX = "99999"

PILOTAGE_DASHBOARDS_WHITELIST = json.loads(
    os.environ.get("PILOTAGE_DASHBOARDS_WHITELIST", "[63, 90, 32, 52, 54, 116, 43, 136, 140, 129, 150]")
)

# Only ACIs given by Convergence France may access some contracts
ACI_CONVERGENCE_PK_WHITELIST = json.loads(os.environ.get("ACI_CONVERGENCE_PK_WHITELIST", "[]"))

# Specific stats are progressively being deployed to more and more departments and specific users.
# Kept as a setting to not let User PKs in clear in the code.
STATS_SIAE_USER_PK_WHITELIST = json.loads(os.getenv("STATS_SIAE_USER_PK_WHITELIST", "[]"))

# Slack notifications sent by Metabase cronjobs.
SLACK_CRON_WEBHOOK_URL = os.environ.get("SLACK_CRON_WEBHOOK_URL")

REDIS_URL = os.getenv("REDIS_URL")  # pay attention, prod & staging share the same redis but != DB
REDIS_DB = os.getenv("REDIS_DB")

HUEY = {
    "name": "ITOU",
    # Don't store task results (see our Redis Post-Morten in documentation for more information)
    "results": False,
    "url": f"{REDIS_URL}/?db={REDIS_DB}",
    "consumer": {
        "workers": 2,
        "worker_type": "thread",
    },
    "immediate": ITOU_ENVIRONMENT not in ("DEMO", "PROD", "STAGING"),
}

# Email https://anymail.readthedocs.io/en/stable/esps/mailjet/
ANYMAIL = {
    # it's the default but our probes need this at import time.
    "MAILJET_API_URL": "https://api.mailjet.com/v3.1/",
    "MAILJET_API_KEY": os.getenv("API_MAILJET_KEY"),
    "MAILJET_SECRET_KEY": os.getenv("API_MAILJET_SECRET"),
    "WEBHOOK_SECRET": os.getenv("MAILJET_WEBHOOK_SECRET"),
}

# EMAIL_BACKEND points to an async wrapper of a "real" email backend
# The real backend is hardcoded in the wrapper to avoid multiple and
# confusing parameters in Django settings.
# Switch to a "standard" Django backend to get the synchronous behaviour back.
EMAIL_BACKEND = "itou.utils.tasks.AsyncEmailBackend"


SEND_EMAIL_DELAY_BETWEEN_RETRIES_IN_SECONDS = 5 * 60
SEND_EMAIL_RETRY_TOTAL_TIME_IN_SECONDS = 24 * 3600

REST_FRAMEWORK = {
    # Namespace versioning e.g. `GET /api/v1/something/`.
    # https://www.django-rest-framework.org/api-guide/versioning/#namespaceversioning
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    # Pagination.
    # https://www.django-rest-framework.org/api-guide/pagination/#pagenumberpagination
    "DEFAULT_PAGINATION_CLASS": "itou.api.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # Response renderers
    # See DEV configuration for an additional rendeder for DRF browseable API
    # https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Default permissions for API views: user must be authenticated
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Throttling:
    # See: https://www.django-rest-framework.org/api-guide/throttling/
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    # Default values for throttling rates:
    # - overridden in custom throttling classes,
    # - arbitrary values, update should the need arise.
    "DEFAULT_THROTTLE_RATES": {
        "anon": "12/minute",
        "user": "12/minute",
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API - Les emplois de l'inclusion",
    "DESCRIPTION": "Documentation de l'API **emplois.inclusion.beta.gouv.fr**",
    "VERSION": "1.0.0",
}

ELASTIC_APM = {
    "ENABLED": bool(os.getenv("APM_SERVER_URL")),
    "SERVICE_NAME": "itou-django",
    "SERVICE_VERSION": os.getenv("COMMIT_ID"),
    "SERVER_URL": os.getenv("APM_SERVER_URL"),
    "SECRET_TOKEN": os.getenv("APM_AUTH_TOKEN"),
    "ENVIRONMENT": ITOU_ENVIRONMENT,
    "DJANGO_TRANSACTION_NAME_FROM_ROUTE": True,
    "TRANSACTION_SAMPLE_RATE": 0.1,
}

# Requests default timeout is None... See https://blog.mathieu-leplatre.info/handling-requests-timeout-in-python.html
# Use `httpx`, which has a default timeout of 5 seconds, when possible.
# Otherwise, set a timeout like this:
# requests.get(timeout=settings.REQUESTS_TIMEOUT)
REQUESTS_TIMEOUT = 5  # in seconds

# ASP SFTP connection
# ------------------------------------------------------------------------------
ASP_FS_SFTP_HOST = os.getenv("ASP_FS_SFTP_HOST")
ASP_FS_SFTP_PORT = os.getenv("ASP_FS_SFTP_PORT")
ASP_FS_SFTP_USER = os.getenv("ASP_FS_SFTP_USER")
# Path to SSH keypair for SFTP connection
ASP_FS_SFTP_PRIVATE_KEY_PATH = os.getenv("ASP_FS_SFTP_PRIVATE_KEY_PATH")
ASP_FS_KNOWN_HOSTS = os.getenv("ASP_FS_KNOWN_HOSTS")

# S3 uploads
# ------------------------------------------------------------------------------
S3_STORAGE_ACCESS_KEY_ID = os.getenv("CELLAR_ADDON_KEY_ID")
S3_STORAGE_SECRET_ACCESS_KEY = os.getenv("CELLAR_ADDON_KEY_SECRET")
S3_STORAGE_ENDPOINT_DOMAIN = os.getenv("CELLAR_ADDON_HOST")
S3_STORAGE_BUCKET_NAME = os.getenv("S3_STORAGE_BUCKET_NAME")
S3_STORAGE_BUCKET_REGION = "eu-west-3"

STORAGE_UPLOAD_KINDS = {
    "default": {
        "allowed_mime_types": ["application/pdf"],
        "upload_expiration": 90 * 60,  # in seconds
        "key_path": "",  # appended before the file key. No backslash!
        "max_files": 1,
        "max_file_size": 5,  # in mb
        "timeout": 20000,  # in ms
    },
    "resume": {
        "key_path": "resume",
    },
    "evaluations": {
        "key_path": "evaluations",
    },
}

# Employee records
# ------------------------------------------------------------------------------
# Employee record data archiving / pruning:
# "Proof of record" model field is erased after this delay (in days)
EMPLOYEE_RECORD_ARCHIVING_DELAY_IN_DAYS = int(os.environ.get("EMPLOYEE_RECORD_ARCHIVING_DELAY_IN_DAYS", 13 * 30))

# This is the official and final production phase date of the employee record feature.
# It is used as parameter to filter the eligible job applications for the feature.
# (no job application before this date can be used for this feature)
EMPLOYEE_RECORD_FEATURE_AVAILABILITY_DATE = timezone.datetime(2021, 9, 27, tzinfo=timezone.utc)

# Only PROD or temporary tests environments are able to transfer employee records data to ASP
# This is disabled by default, overidden in prod settings, and can be set
# via local dev settings or env vars for a temporary environment.
EMPLOYEE_RECORD_TRANSFER_ENABLED = bool(os.environ.get("EMPLOYEE_RECORD_TRANSFER_ENABLED", False))

HIJACK_PERMISSION_CHECK = "itou.utils.perms.user.has_hijack_perm"
HIJACK_ALLOWED_USER_EMAILS = [s.lower() for s in os.getenv("HIJACK_ALLOWED_USER_EMAILS", "").split(",") if s]

EXPORT_DIR = os.getenv("SCRIPT_EXPORT_PATH", f"{ROOT_DIR}/exports")
IMPORT_DIR = os.getenv("SCRIPT_IMPORT_PATH", f"{ROOT_DIR}/imports")
