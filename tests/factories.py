# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory

from annotator.database import db
from annotator.user.models import User


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    first_name = Sequence(lambda n: 'first{0}'.format(n))
    last_name = Sequence(lambda n: 'last{0}'.format(n))
    email = Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = 'example'
    active = True

    class Meta:
        """Factory configuration."""

        model = User
