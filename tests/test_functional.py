# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from flask_security import url_for_security

from annotator.user.models import User

from .factories import UserFactory


class TestLoggingIn:
    """Login."""

    def test_can_log_in_returns_200(self, user, testapp):
        """Login successful."""
        # Goes to homepage
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms['login_user_form']
        form['email'] = user.email
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200

    def test_sees_alert_on_log_out(self, user, testapp):
        """Show alert on logout."""
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms['login_user_form']
        form['email'] = user.email
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        res = testapp.get('/logout').follow()
        # sees alert
        assert 'You are logged out.' in res

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        """Show error if password is incorrect."""
        # Goes to homepage
        res = testapp.get('/login')
        # Fills out login form, password incorrect
        form = res.forms['login_user_form']
        form['email'] = user.email
        form['password'] = 'wrong'
        # Submits
        res = form.submit()
        # sees error
        assert 'Invalid password' in res

    def test_sees_error_message_if_username_doesnt_exist(self, user, testapp):
        """Show error if username doesn't exist."""
        # Goes to homepage
        res = testapp.get('/login')
        # Fills out login form, password incorrect
        form = res.forms['login_user_form']
        form['email'] = 'unknown@unknown.com'
        form['password'] = 'myprecious'
        # Submits
        res = form.submit()
        # sees error
        assert 'Specified user does not exist' in res


class TestRegistering:
    """Register a user."""

    def test_can_register(self, user, testapp):
        """Register a new user."""
        old_count = len(User.query.all())
        # Goes to homepage
        res = testapp.get('/')
        # Clicks Create Account button
        res = res.click('Create account')
        # Fills out the form
        form = res.forms['register_user_form']
        form['first_name'] = 'foo'
        form['last_name'] = 'bar'
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['password_confirm'] = 'secret'
        # Submits
        res = form.submit().follow()
        assert res.status_code in [200, 302]
        # A new user was created
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        """Show error if passwords don't match."""
        # Goes to registration page
        res = testapp.get(url_for_security('register'))
        # Fills out form, but passwords don't match
        form = res.forms['register_user_form']
        form['first_name'] = 'foo'
        form['last_name'] = 'bar'
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['password_confirm'] = 'secrets'
        # Submits
        res = form.submit()
        # sees error message
        assert 'Passwords do not match' in res

    def test_sees_error_message_if_user_already_registered(self, user, testapp):
        """Show error if user already registered."""
        user = UserFactory(active=True)  # A registered user
        user.save()
        # Goes to registration page
        res = testapp.get(url_for_security('register'))
        # Fills out form, but username is already registered
        form = res.forms['register_user_form']
        form['first_name'] = 'newfirstname'
        form['last_name'] = 'newlastname'
        form['email'] = user.email
        form['password'] = 'secret'
        form['password_confirm'] = 'secret'
        # Submits
        res = form.submit()
        # sees error
        assert '{} is already associated with an account'.format(user.email) in res
