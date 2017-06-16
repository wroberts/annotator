# -*- coding: utf-8 -*-
"""Test forms."""

from annotator.user.forms import ExtendedRegisterForm


class TestRegisterForm:
    """Register form."""

    def test_validate_email_already_registered(self, user):
        """Enter email that is already registered."""
        form = ExtendedRegisterForm(first_name='unique',
                                    last_name='unique',
                                    email=user.email,
                                    password='example',
                                    password_confirm='example')

        assert form.validate() is False
        assert '{} is already associated with an account.'.format(user.email) in form.email.errors

    def test_validate_success(self, db):
        """Register with success."""
        form = ExtendedRegisterForm(first_name='newfirstname',
                                    last_name='newlastname',
                                    email='new@test.test',
                                    password='example',
                                    password_confirm='example')
        assert form.validate() is True
