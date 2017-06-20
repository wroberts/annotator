# -*- coding: utf-8 -*-

"""Annotation models."""

import datetime

import enum

from annotator.database import Column, Model, SurrogatePK, backref, db, reference_col, relationship


class BooleanUnsure(enum.Enum):
    """Annotation decisions that can be taken by a user."""
    true = 1
    false = 2
    uncertain = 3


class Annotation(SurrogatePK, Model):
    """A snapshot of an annotation of a particular clause by a particular user."""
    __tablename__ = 'annotations'
    clause_id = reference_col('clauses', nullable=True)
    clause = relationship('Clause', backref=backref('annotations', order_by='Annotation.created_at.desc()'))
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref=backref('annotations', order_by='Annotation.created_at.desc()'))
    created_at = Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    invalid = Column(db.Enum(BooleanUnsure), nullable=True, default=BooleanUnsure.false)
    stative = Column(db.Enum(BooleanUnsure), nullable=True)
    bounded = Column(db.Enum(BooleanUnsure), nullable=True)
    extended = Column(db.Enum(BooleanUnsure), nullable=True)
    change = Column(db.Enum(BooleanUnsure), nullable=True)

    def __init__(self, clause, user, invalid, stative, bounded, extended, change, **kwargs):
        """Create instance."""
        db.Model.__init__(self,
                          clause_id=clause.id,
                          user_id=user.id,
                          invalid=invalid,
                          stative=stative,
                          bounded=bounded,
                          extended=extended,
                          change=change,
                          **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Annotation (sentence {clause_id}, user {user_id})>'.format(
            clause_id=self.clause_id,
            user_id=self.user_id)


class SynArg(SurrogatePK, Model):
    """A syntactic argument to a verb in a particular clause."""
    __tablename__ = 'synargs'
    type = Column(db.Unicode(30), nullable=True)
    begin = Column(db.Integer, nullable=True)  # index of first word in the argument
    end = Column(db.Integer, nullable=True)    # index of first word not in the argument
    clause_id = reference_col('clauses', nullable=True)
    clause = relationship('Clause', backref=backref('synargs', order_by='SynArg.begin'))

    def __init__(self, type, begin, end, clause, **kwargs):
        """Create instance."""
        db.Model.__init__(self, type=type, begin=begin, end=end, clause_id=clause.id, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<SynInd (type {type}, clause_id {clause_id})>'.format(
            type=self.type,
            clause_id=self.clause_id)


class AspInd(SurrogatePK, Model):
    """An aspectual indicator co-occurring with a verb in a particular clause."""
    __tablename__ = 'aspinds'
    type = Column(db.Unicode(30), nullable=True)
    begin = Column(db.Integer, nullable=True)  # index of first word in the argument
    end = Column(db.Integer, nullable=True)    # index of first word not in the argument
    clause_id = reference_col('clauses', nullable=True)
    clause = relationship('Clause', backref=backref('aspinds', order_by='AspInd.begin'))

    def __init__(self, type, begin, end, clause, **kwargs):
        """Create instance."""
        db.Model.__init__(self, type=type, begin=begin, end=end, clause_id=clause.id, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<AspInd (type {type}, clause_id {clause_id})>'.format(
            type=self.type,
            clause_id=self.clause_id)


class Clause(SurrogatePK, Model):
    """A clause to be annotated."""
    __tablename__ = 'clauses'
    text = Column(db.Unicode(1000), nullable=True)  # space-separated UTF-8
    verb_index = Column(db.Integer, nullable=True)  # index of verb in sentence

    def __init__(self, text, verb_index, **kwargs):
        """Create instance."""
        db.Model.__init__(self, text=text, verb_index=verb_index, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Clause (id {clause_id})>'.format(
            clause_id=self.id)
