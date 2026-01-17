import os
import sys

# Tambahkan path project ke PYTHONPATH
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from app import app as application

# Gunakan konfigurasi production
os.environ['FLASK_ENV'] = 'production'
