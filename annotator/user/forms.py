# -*- coding: utf-8 -*-
"""User forms."""
from flask_security.forms import RegisterForm
from wtforms import StringField
from wtforms.validators import DataRequired


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
