import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(BASE_DIR, "Site"))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "Site.settings",
    "SmartBuy"
)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app=application