# This settings file is intended to be used as the second-half of a 
# SplitSetting as described on the django wiki. See:
# http://code.djangoproject.com/wiki/SplitSettings#Multiplesettingfilesimportingfromeachother
# It will be imported at the end of settings.py
# Here you should define your database and email connection settings, as well
# as any GeoDjango settings. You can also specify where media is located on
# your filesystem. Settings defined here will override those in settings.py.

# At the very least, ensure that production setups have their own SECRET_KEY
# that is kept hidden from public repositories.
# SECRET_KEY = '6c(kr8r%aqf#r8%arr=0py_7t9m)wgocwyp5g@!j7eb0erm(2+sdklj23'

# The following Google key is for localhost:
# GOOGLE_API_KEY = 'ABQIAAAAu2dobIiH7nisivwmaz2gDhT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSLaQmJjJuOq03hTEjc-cNV8eegYg' 

# You'll want to specify any database connection info here:
DATABASE_NAME = 'simple_example'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'my-secret-password'

# Uncomment this line to cause MarineMap to go into maintenance mode
# It will not be accessible without logging in as staff
# See http://pypi.python.org/pypi/django-maintenancemode
# MAINTENANCE_MODE = True

# And to run tests correctly, tell Django what your spatial database template is...
#POSTGIS_TEMPLATE='template_postgis'
# ...and uncomment TEST_RUNNER
#TEST_RUNNER='django.contrib.gis.tests.run_tests'

# ID of Wave to be used in demo of the conversation tab
WAVE_ID = 'wavesandbox.com!w+W0aM2epE%A'