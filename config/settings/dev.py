from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# On pourrait écraser la DB pour utiliser PostgreSQL en dev si besoin,
# mais SQLite3 suffit pour la maquette locale
