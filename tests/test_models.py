# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest
from flask_security.utils import verify_password

from annotator.user.models import Role, User

from .factories import UserFactory


@pytest.mark.usefixtures('db')
class TestUser:
    """User tests."""

    def test_get_by_id(self):
        """Get user by ID."""
        user = User('foo', 'foo@bar.com')
        user.save()

        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self):
        """Test creation date."""
        user = User(first_name='foo', last_name='bar', email='foo@bar.com')
        user.save()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self):
        """Test null password."""
        user = User(first_name='foo', last_name='bar', email='foo@bar.com')
        user.save()
        assert user.password is None

    def test_factory(self, db):
        """Test user factory."""
        user = UserFactory(password='myprecious')
        db.session.commit()
        assert bool(user.first_name)
        assert bool(user.last_name)
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.is_admin is False
        assert user.active is True
        assert verify_password('myprecious', user.password)

    def test_check_password(self):
        """Check password."""
        user = User.create(first_name='foo',
                           last_name='bar',
                           email='foo@bar.com',
                           password='foobarbaz123')
        assert verify_password('foobarbaz123', user.password) is True
        assert verify_password('barfoobaz', user.password) is False

    def test_full_name(self):
        """User full name."""
        user = UserFactory(first_name='Foo', last_name='Bar')
        assert user.full_name == 'Foo Bar'

    def test_roles(self):
        """Add a role to a user."""
        role = Role(name='admin')
        role.save()
        user = UserFactory()
        user.roles.append(role)
        user.save()
        assert role in user.roles
