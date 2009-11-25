import os

# !!!!!!!!!!!!!!!!!!!!!!!
# DONT FORGET TO DOCUMENT ANY NEW SETTINGS IN /docs/settings.rst
# !!!!!!!!!!!!!!!!!!!!!!

GEOMETRY_DB_SRID = 3310

GEOMETRY_CLIENT_SRID = 4326

GOOGLE_API_KEY = 'ABQIAAAAu2dobIiH7nisivwmaz2gDhT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSLaQmJjJuOq03hTEjc-cNV8eegYg'

# Define the models which will represent the MPA and Array child classes
MPA_CLASS = None
ARRAY_CLASS = None
MPA_FORM = 'lingcod.mpa.forms.MpaForm'
ARRAY_FORM = 'lingcod.array.forms.ArrayForm'

from lingcod.common import assets

COMPRESS_CSS = {
    'application': {
        'source_filenames': assets.get_css_files(),
        'output_filename': 'marinemap.r?.css',
        'extra_context': {
            'media': 'all'
        }
    }
}

COMPRESS_JS = {
    'application': {
        'source_filenames': assets.get_js_files(),
        'output_filename': 'marinemap.r?.js'
    },
    'tests': {
        'source_filenames': assets.get_js_test_files(),
        'output_filename': 'marinemap_tests.r?.js'
    }
}

COMPRESS_VERSION = True
COMPRESS_AUTO = True

MIDDLEWARE_CLASSES = (
    # GZip speeds up downloads by compressing on the fly
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.gis',
    'compress',
    'lingcod.common',
    'lingcod.layers',
    'lingcod.studyregion',
    'lingcod.simplefaq',
    'lingcod.staticmap',
    'lingcod.manipulators',
    'lingcod.mpa',
    'lingcod.wave',
    'lingcod.mpa',
    'lingcod.kmlapp',
    'lingcod.array',
    'lingcod.rest',
)

MEDIA_ROOT = os.path.dirname(os.path.abspath(__file__)) + '/../../media/'

MEDIA_URL = '/media/'

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'