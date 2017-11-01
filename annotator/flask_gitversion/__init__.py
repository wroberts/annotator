#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Make the git hash available in a Flask application.

flask_gitversion/__init__.py
"""

import os
import subprocess

import wkr


# https://stackoverflow.com/a/40170206/1062499
# Return the git revision as a string
def get_git_version(basepath=None):
    """Get the git hash."""
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        if basepath is not None:
            with wkr.os.momentary_chdir(basepath):
                out = _minimal_ext_cmd(['git', 'rev-parse', '--short', 'HEAD'])
        else:
            out = _minimal_ext_cmd(['git', 'rev-parse', '--short', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = 'Unknown'

    return git_revision


class GitVersion(object):
    """Insert the git hash into the global context."""

    def __init__(self, app=None):
        """Constructor."""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialse extension on the given app."""
        git_version = get_git_version(app.root_path)

        @app.context_processor
        def gitversion_processor():
            return dict(git_version=git_version)
