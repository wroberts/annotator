# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint('annotations', __name__, url_prefix='/annotations', static_folder='../static')


@blueprint.route('/')
@login_required
def dashboard():
    """User dashboard."""
    return render_template('users/dashboard.html')
