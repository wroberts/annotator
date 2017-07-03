# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask, render_template
from flask_security import SQLAlchemyUserDatastore

from annotator import annotations, commands, public, user
from annotator.extensions import (babel, cache, compress, csrf_protect, db, debug_toolbar, mail, migrate, security,
                                  webpack)
from annotator.settings import ProdConfig
from annotator.user.forms import ExtendedConfirmRegisterForm, ExtendedRegisterForm
from annotator.user.models import Role, User


def create_app(config_object=ProdConfig):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    babel.init_app(app)
    cache.init_app(app)
    compress.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore,
                      confirm_register_form=ExtendedConfirmRegisterForm,
                      register_form=ExtendedRegisterForm)
    debug_toolbar.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    webpack.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    app.register_blueprint(annotations.rest.blueprint)
    app.register_blueprint(annotations.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)
    app.cli.add_command(commands.drop_db)
    app.cli.add_command(commands.create_corpus)
