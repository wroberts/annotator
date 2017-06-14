# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask.helpers import get_debug_flag

from annotator.app import create_app
from annotator.settings import DevConfig, ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG)

# (setenv "FLASK_APP" "/Users/wroberts/dev/annotator/autoapp.py")
# (setenv "FLASK_DEBUG" "1")
# (setq python-shell-interpreter "flask")
# (setq python-shell-interpreter-args "shell")
