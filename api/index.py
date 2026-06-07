import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = os.path.join(BASE_DIR, "Site")

sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "Site.settings"
)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application