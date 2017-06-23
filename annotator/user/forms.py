# -*- coding: utf-8 -*-
"""User forms."""
from flask_security.forms import ConfirmRegisterForm, PasswordConfirmFormMixin, RegisterForm
from wtforms import StringField
from wtforms.validators import DataRequired


class ExtendedConfirmRegisterForm(ConfirmRegisterForm, PasswordConfirmFormMixin):
    """
    Add fields to Flask-Security's ConfirmRegisterForm.

    Adds ``first_name``, ``last_name`` and ``confirm_password`` to the
    form.  The form is used for user registration when "confirmable"
    is True.
    """

    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])


class ExtendedRegisterForm(RegisterForm):
    """
    Add fields to Flask-Security's RegisterForm.

    Adds ``first_name``, ``last_name`` to the form.  The form is used
    for user registration when "confirmable" is False.
    """

    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
