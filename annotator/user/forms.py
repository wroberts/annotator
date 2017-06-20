# -*- coding: utf-8 -*-
"""User forms."""
from flask_security.forms import ConfirmRegisterForm, RegisterForm
from wtforms import StringField
from wtforms.validators import DataRequired


class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
