# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required
from annotator.annotations.models import Annotation

blueprint = Blueprint('annotation', __name__, url_prefix='/annotations', static_folder='../static')

# @blueprint.route('/')
# @login_required
# def members():
#     """List members."""
#     return render_template('users/members.html')
