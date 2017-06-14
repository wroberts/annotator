# -*- coding: utf-8 -*-
"""Model unit tests."""

import json
import pytest

from annotator.annotations.models import Annotation, AspInd, BooleanUnsure, Clause, SynArg
from annotator.user.models import User


class Bunch(object):
    """Empty object that can hold arbitrary other objects."""

    pass


@pytest.fixture()
def dummies(db):
    """Create some temporary dummy objects for testing."""
    bunch = Bunch()
    bunch.c1 = Clause(u'While the most common way is to use the flask command , '
                      u'you can also make your own " driver scripts " .', 5)
    bunch.c2 = Clause(u'While the most common way is to use the flask command , '
                      u'you can also make your own " driver scripts " .', 13)
    bunch.c3 = Clause(u'Since Flask uses click for the scripts there is no reason '
                      u'you cannot hook these scripts into any click application .', 2)
    bunch.c4 = Clause(u'Since Flask uses click for the scripts there is no reason '
                      u'you cannot hook these scripts into any click application .', 8)
    bunch.c5 = Clause(u'Since Flask uses click for the scripts there is no reason '
                      u'you cannot hook these scripts into any click application .', 12)
    for c in [bunch.c1, bunch.c2, bunch.c3, bunch.c4, bunch.c5]:
        c.save()

    # add some syntactic arguments
    bunch.s1 = SynArg(u'subj', 1, 5, bunch.c1)
    bunch.s2 = SynArg(u'subj', 12, 13, bunch.c2)
    bunch.s3 = SynArg(u'subj', 1, 2, bunch.c3)
    bunch.s4 = SynArg(u'obj', 3, 4, bunch.c3)
    bunch.s5 = SynArg(u'subj', 7, 8, bunch.c4)
    bunch.s6 = SynArg(u'subj', 11, 12, bunch.c5)

    for s in [bunch.s1, bunch.s2, bunch.s3, bunch.s4, bunch.s5, bunch.s6]:
        s.save()

    bunch.a1 = AspInd(u'advp_for', 4, 7, bunch.c3)
    bunch.a1.save()

    # we'll need a user to do this
    bunch.user = User('joe.blow', 'joe.blow@anywhere.com')
    bunch.user.save()

    # now let's create some Annotations on the first clause

    # start with a first annotation
    bunch.an1 = Annotation(bunch.c1, bunch.user,
                           BooleanUnsure.false,
                           BooleanUnsure.true,
                           BooleanUnsure.false,
                           BooleanUnsure.false)
    bunch.an1.save()

    # now create a new annotation to overwrite this; this contains an
    # annotation error
    bunch.an2 = Annotation(bunch.c1, bunch.user,
                           BooleanUnsure.false,
                           BooleanUnsure.false,
                           BooleanUnsure.false,
                           BooleanUnsure.false)
    bunch.an2.save()

    # now create a third annotation to fix the error
    bunch.an3 = Annotation(bunch.c1, bunch.user,
                           BooleanUnsure.false,
                           BooleanUnsure.true,
                           BooleanUnsure.false,
                           BooleanUnsure.false)
    bunch.an3.save()

    # finally, let's create an Annotation on the second clause
    bunch.an4 = Annotation(bunch.c2, bunch.user,
                           BooleanUnsure.false,
                           BooleanUnsure.false,
                           BooleanUnsure.false,
                           BooleanUnsure.false)
    bunch.an4.save()
    return bunch


def test_empty(db):
    """Test that the annotation model list is empty."""
    assert Clause.query.count() == 0
    assert SynArg.query.count() == 0
    assert AspInd.query.count() == 0
    assert Annotation.query.count() == 0


def test_relationship_1(dummies):
    """We should be able to access AspInd and SynArg objects from inside c3."""
    assert dummies.c3.aspinds[0].type == 'advp_for'
    assert dummies.c3.synargs[0].type == 'subj'
    assert dummies.c3.synargs[1].type == 'obj'


def test_relationship_2(dummies):
    """We should be able to access clauses from inside SynArg and AspInd."""
    assert dummies.a1.clause.verb_index == 2
    assert dummies.s3.clause.verb_index == 2
    assert dummies.s4.clause.verb_index == 2

# we should be able to query the database to ask questions


def test_clause_query_1(dummies):
    """Find out how many sentences do not have any aspectual indicators tagged on them."""
    assert Clause.query.filter(~Clause.aspinds.any()).count() == 4


def test_clause_query_2(dummies):
    """Find out how many clauses have been annotated now."""
    assert Clause.query.filter(Clause.annotations.any()).count() == 2


def test_clause_query_3(dummies):
    """Find out how many clauses has "user" annotated."""
    assert (Clause.query
            .filter(Clause.annotations.any(Annotation.user_id == dummies.user.id))
            .count()) == 2


def test_annotation_query_1(dummies):
    """Find out, given c1 and user, how many annotations there are."""
    assert (Annotation.query
            .filter(Annotation.clause_id == dummies.c1.id)
            .filter(Annotation.user_id == dummies.user.id)
            .count()) == 3


def test_annotation_query_2(dummies):
    """Given c1 and user, find the most recent annotation."""
    assert (Annotation.query
            .filter(Annotation.clause_id == dummies.c1.id)
            .filter(Annotation.user_id == dummies.user.id)
            .order_by(Annotation.created_at.desc())
            .first()) == dummies.an3

# test the REST backend


def test_rest_get_1(app, dummies):
    """Test the REST GET verb's ability to get a clause record."""
    with app.test_client() as client:
        rv = client.get('/api/clauses/2')
        response = json.loads(rv.data)
        # ignore 'last-annotation-date'
        if 'last-annotation-date' in response:
            del response['last-annotation-date']
        assert response == {
            u'verb-index': 13,
            u'verb-comps': [{u'type': u'subj',
                             u'begin': 12,
                             u'end': 13}],
            u'sentence': [u'While', u'the', u'most', u'common', u'way', u'is',
                          u'to', u'use', u'the', u'flask', u'command', u',',
                          u'you', u'can', u'also', u'make', u'your', u'own',
                          u'"', u'driver', u'scripts', u'"', u'.'],
            u'id': 2,
            u'aspectual-indicators': [],
            u'annotation': {u'bounded': u'false',
                            u'invalid': u'false',
                            u'change': u'false',
                            u'stative': u'false'}}


def test_rest_get_2(app, dummies):
    """Test the REST GET verb's ability to get a clause record."""
    with app.test_client() as client:
        rv = client.get('/api/clauses/3')
        response = json.loads(rv.data)
        assert response == {
            u'verb-index': 2,
            u'verb-comps': [{u'type': u'subj',
                             u'begin': 1,
                             u'end': 2},
                            {u'type': u'obj',
                             u'begin': 3,
                             u'end': 4}],
            u'sentence': [u'Since', u'Flask', u'uses', u'click', u'for', u'the',
                          u'scripts', u'there', u'is', u'no', u'reason', u'you',
                          u'cannot', u'hook', u'these', u'scripts', u'into',
                          u'any', u'click', u'application', u'.'],
            u'id': 3,
            u'aspectual-indicators': [{u"type": u"advp_for",
                                       u"begin": 4,
                                       u"end": 7}],
            u'last-annotation-date': None,
            u'annotation': None}
