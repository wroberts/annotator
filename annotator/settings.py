# -*- coding: utf-8 -*-
"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('ANNOTATOR_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', b'password-salt')  # TODO
    SECURITY_REGISTERABLE = True,
    SECURITY_RECOVERABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORDLESS = False
    SECURITY_CHANGEABLE = True
    SECURITY_REGISTER_USER_TEMPLATE = 'public/register.html'
    SECURITY_LOGIN_USER_TEMPLATE = 'public/login.html'
    SECURITY_FORGOT_PASSWORD_TEMPLATE = 'public/forgot_password.html'
    SECURITY_RESET_PASSWORD_TEMPLATE = 'public/reset_password.html'
    SECURITY_CHANGE_PASSWORD_TEMPLATE = 'users/change_password.html'
    SECURITY_SEND_CONFIRMATION_TEMPLATE = 'users/send_confirmation.html'
    SECURITY_POST_LOGIN_VIEW = '/annotations/'
    SECURITY_POST_LOGOUT_VIEW = '/?logout'
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)
    MAIL_SUPPRESS_SEND = True  # TODO
    WEBPACK_MANIFEST_PATH = 'static/build/manifest.json'


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI',  # TODO: Change me
                                             'postgresql://localhost/example')
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)
    DEBUG_TB_ENABLED = True
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False  # Allows form testing
