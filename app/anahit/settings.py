"""
Django settings for anahit project.
Generated by 'django-admin startproject' using Django 3.2.6.
For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
import sys
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

from dotenv import load_dotenv 
load_dotenv(os.path.join(BASE_DIR, "anahit", ".env"))

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = int(os.environ.get("DEBUG", default=0))

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
ALLOWED_HOSTS = ['*']

SITE_ID=int(os.environ.get('SITE_ID',2))


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'django_summernote',
    'ckeditor',
    'ckeditor_uploader',
    'django_crontab',
     # custom apps 
    "apps.users.apps.UsersConfig",
    "apps.subscription.apps.SubscriptionConfig",
    "apps.blog.apps.BlogConfig",
    "apps.services.apps.ServicesConfig",
    "apps.price.apps.PriceConfig",
    "apps.notifications.apps.NotificationsConfig",

    # amazon s3 apps
    'storages',

    # RestAPI
    'rest_framework',
    
    # social share
    'django_social_share',

    # magic link
    'magiclink',

    # login attempts
    'axes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',

]

ROOT_URLCONF = 'anahit.urls'

AUTH_USER_MODEL = 'users.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = 'anahit.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE'),
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'magiclink.backends.MagicLinkBackend',
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
BASEDIRRR = os.path.join(BASE_DIR, "")

STATIC_ROOT = os.path.join(BASE_DIR, "static-temp")
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

CKEDITOR_UPLOAD_PATH = 'blog-uploads/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# All auth

ACCOUNT_FORMS = {'login': 'users.forms.UserLoginForm',
                 'signup': 'users.forms.UserSignupForm',
                }
ACCOUNT_USER_MODEL_USERNAME_FIELD=None
ACCOUNT_USERNAME_REQUIRED=False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
LOGIN_REDIRECT_URL='/'
SOCIALACCOUNT_EMAIL_VERIFICATION="none"
SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
    }
}


#dev 
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY',None)
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY',None)
STRIPE_WEBHOOK_ID = os.environ.get('STRIPE_WEBHOOK_ID',None)

from ckeditor.configs import DEFAULT_CONFIG  # noqa

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "ckeditor_uploader.backends.PillowBackend"
CKEDITOR_THUMBNAIL_SIZE = (300, 300)
CKEDITOR_IMAGE_QUALITY = 40
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_ALLOW_NONIMAGE_FILES = True

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
SUBSCRIPTION_SUBJECT = os.environ.get('SUBSCRIPTION_SUBJECT')
SUBSCRIPTION_MESSAGE = os.environ.get('SUBSCRIPTION_MESSAGE')
SUBSCRIPTION_PLAN_STATUS = os.environ.get('SUBSCRIPTION_PLAN_STATUS', 'active')
SUBSCRIPTION_PLAN_STATUS_CODE = os.environ.get('SUBSCRIPTION_PLAN_STATUS_CODE', 200)
FREE_PLAN_PRICE = os.environ.get("FREE_PLAN_PRICE", 0)
FREE_PLAN_NAME = os.environ.get("FREE_PLAN_NAME", 'Free')
UNLIMITED_PLAN_NAME = os.environ.get("UNLIMITED_PLAN_NAME", 'Unlimited')
EXCLUSIVE_PLAN_NAME = os.environ.get("EXCLUSIVE_PLAN_NAME", 'Exclusive')

#Facebook
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET') #app key
ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_USERNAME_REQURIED=True


# AWS S3

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
DEFAULT_FILE_STORAGE = os.environ.get('DEFAULT_FILE_STORAGE')
AWS_USER_AVATAR_MEDIA_LOCATION = os.environ.get('AWS_USER_AVATAR_MEDIA_LOCATION')
USER_AVATAR_FILE_STORAGE = os.environ.get('USER_AVATAR_FILE_STORAGE')
AWS_BLOG_MEDIA_LOCATION = os.environ.get('AWS_BLOG_MEDIA_LOCATION')
BLOG_FILE_STORAGE = os.environ.get('BLOG_FILE_STORAGE')
AWS_SERVICE_MEDIA_LOCATION = os.environ.get('AWS_SERVICE_MEDIA_LOCATION')
SERVICE_FILE_STORAGE = os.environ.get('SERVICE_FILE_STORAGE')

#customizing error messages in red box
MESSAGE_TAGS = {
    messages.ERROR:'danger'
    # messages.INFO: '',
    # 50: 'critical',
}

# Google Captcha keys

# ACCOUNT_SIGNUP_FORM_CLASS = 'users.forms.UserSignupForm'

GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')

# Telegram Token
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

CRONJOBS = [
    ('0 0 1 * *', 'cron.run', '>> /home/anahit_web/cron_logs/cron.log'),
    ('0 10 * * 1', 'cron.send_newsletter_notification', '>> /home/anahit_web/cron_logs/cron.log')
]

# LOGIN_URL = 'magiclink:login'

MAGICLINK_LOGIN_TEMPLATE_NAME = 'account/magic_link_login.html'
MAGICLINK_LOGIN_SENT_TEMPLATE_NAME = 'account/magic_link_login_sent.html'
MAGICLINK_LOGIN_FAILED_TEMPLATE_NAME = 'account/login_failed.html'


# If a login failed redirect is specified the user will be redirected to this
# URL instead of being shown the LOGIN_FAILED_TEMPLATE
MAGICLINK_LOGIN_FAILED_REDIRECT = '/link-expired'

# If this setting is set to False a user account will be created the first time
# a user requests a login link.
MAGICLINK_REQUIRE_SIGNUP = True

# Change the url a user is redirect to after requesting a magic link
MAGICLINK_LOGIN_SENT_REDIRECT = 'magiclink:login_sent'

# How long a magic link is valid for before returning an error
MAGICLINK_AUTH_TIMEOUT = 181  # In second - Default is 5 minutes

# Email address is not case sensitive. If this setting is set to True all
# emails addresses will be set to lowercase before any checks are run against it
MAGICLINK_IGNORE_EMAIL_CASE = True

# When creating a user assign their email as the username (if the User model
# has a username field)
MAGICLINK_EMAIL_AS_USERNAME = True

# Allow superusers to login via a magic link
MAGICLINK_ALLOW_SUPERUSER_LOGIN = True

# Allow staff users to login via a magic link
MAGICLINK_ALLOW_STAFF_LOGIN = True

# Ignore the Django user model's is_active flag for login requests
MAGICLINK_IGNORE_IS_ACTIVE_FLAG = True

# Override the default magic link length
# Warning: Overriding this setting has security implications, shorter tokens
# are much more susceptible to brute force attacks*
MAGICLINK_TOKEN_LENGTH = 50

# Require the user email to be included in the verification link
# Warning: If this is set to false tokens are more vulnerable to brute force
MAGICLINK_VERIFY_INCLUDE_EMAIL = False

# Ensure the user who clicked magic link used the same browser as the
# initial login request.
# Note: This can cause issues on devices where the default browser is
# different from the browser being used by the user such as on iOS)
MAGICLINK_REQUIRE_SAME_BROWSER = False

# Ensure the user who clicked magic link has the same IP address as the
# initial login request.
MAGICLINK_REQUIRE_SAME_IP = True

# Remove the last 8-bit octet of a clients IP address.
# Note: This has no effect if MAGICLINK_REQUIRE_SAME_IP as no IP address
# is stored
MAGICLINK_ANONYMIZE_IP = True
# The number of times a login token can be used before being disabled
MAGICLINK_TOKEN_USES = 1

# How often a user can request a new login token (basic rate limiting).
MAGICLINK_LOGIN_REQUEST_TIME_LIMIT = 30  # In seconds

# Disable all other tokens for a user when a new token is requested
MAGICLINK_ONE_TOKEN_PER_USER = True
MAGICLINK_ANTISPAM_FORMS = False
MAGICLINK_ANTISPAM_FIELD_TIME = 1
MAGICLINK_LOGIN_VERIFY_URL = 'magiclink:login_verify'

# If an email address has been added to the unsubscribe table but is also
# assocaited with a Django user, should a login email be sent
MAGICLINK_IGNORE_UNSUBSCRIBE_IF_USER = False
# axes 'login attempt counter'
AXES_FAILURE_LIMIT = 5
# AXES_ENABLED = True
AXES_COOLOFF_TIME = 0.5
# "python manage.py axes_reset" -----------------------command to reset login attempt
# SILENCED_SYSTEM_CHECKS = ['axes.W004']
AXES_LOCKOUT_TEMPLATE = f'{BASE_DIR}/templates/account/exceed_login_attempt.html'