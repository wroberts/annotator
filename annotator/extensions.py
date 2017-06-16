# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security import Security
from flask_sqlalchemy import SQLAlchemy
from flask_webpack import Webpack
from flask_wtf.csrf import CSRFProtect

csrf_protect = CSRFProtect()
db = SQLAlchemy()
security = Security()
migrate = Migrate()
mail = Mail()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
webpack = Webpack()
