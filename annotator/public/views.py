# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request
from flask_security.core import current_user

blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route('/')
def home():
    """Home page."""
    if not current_user.is_authenticated:
        if 'logout' in request.args:
            flash('You are logged out.', 'info')
        return render_template('public/home.html')
    else:
        return redirect('/annotations/')


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')
