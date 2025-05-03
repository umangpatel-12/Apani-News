"""
WSGI config for ApaniNews project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
<<<<<<< HEAD
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
=======
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
>>>>>>> b32e3409f2d87f193ea8976c0fd0ca6edf64df33
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ApaniNews.settings')

application = get_wsgi_application()
