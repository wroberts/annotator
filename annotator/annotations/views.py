# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from flask_restful import Api, Resource, abort
from marshmallow import Schema, ValidationError, fields, post_load
import sqlalchemy.orm

from annotator.annotations.models import Annotation, BooleanUnsure, Clause

blueprint = Blueprint('annotation', __name__, url_prefix='/api', static_folder='../static')
api = Api(blueprint)


class CompSchema(Schema):
    """Marshmallow schema for SynArg and AspInd objects."""

    type = fields.Str()
    begin = fields.Int()
    end = fields.Int()


def validate_booleanunsure(value):
    """Validate BooleanUnsure values."""
    if value not in set(x.name for x in BooleanUnsure):
        raise ValidationError('Value must be "true", "false", or "uncertain".')
    return True


class AnnoSchema(Schema):
    """Marshmallow schema for Annotation objects."""

    invalid = fields.Function(lambda annotation: annotation.invalid.name,
                              required=True, validate=validate_booleanunsure)
    stative = fields.Function(lambda annotation: annotation.stative.name,
                              required=True, validate=validate_booleanunsure)
    bounded = fields.Function(lambda annotation: annotation.bounded.name,
                              required=True, validate=validate_booleanunsure)
    change = fields.Function(lambda annotation: annotation.change.name,
                             required=True, validate=validate_booleanunsure)

    @post_load
    def convert_to_enums(self, data):
        """Convert strings into BooleanUnsure values."""
        return dict((key, BooleanUnsure.__members__[value])
                    for (key, value) in data.items())


class ClauseSchema(Schema):
    """Marshmallow schema for Clause objects."""

    id = fields.Integer()
    sentence = fields.Function(lambda clause: clause.text.split())
    verb_index = fields.Int(load_from='verb-index', dump_to='verb-index')
    synargs = fields.List(fields.Nested(CompSchema),
                          load_from='verb-comps', dump_to='verb-comps')
    aspinds = fields.List(fields.Nested(CompSchema),
                          load_from='aspectual-indicators', dump_to='aspectual-indicators')
    last_annotation_date = fields.DateTime(format='iso', missing=None,
                                           load_from='last-annotation-date',
                                           dump_to='last-annotation-date')
    annotation = fields.Nested(AnnoSchema, missing=None)


def marshal(clause, annotation):
    """
    Generate a JSON representation of a clause-annotation pair for a given user.
    """
    clause.annotation = annotation
    clause.last_annotation_date = None
    if annotation is not None:
        clause.last_annotation_date = annotation.created_at
    return ClauseSchema().dump(clause)


class ClauseRsc(Resource):
    """REST API for interacting with clauses and annotations."""

    @login_required
    def get(self, clause_id):
        """
        Returns the given Clause, with the most recent Annotation that
        this user made on it inserted.
        """
        # get the clause
        try:
            clause = Clause.query.filter(Clause.id == clause_id).one()
            annotation = (Annotation.query
                          .filter(Annotation.clause_id == clause_id)
                          .filter(Annotation.user_id == current_user.id)
                          .order_by(Annotation.created_at.desc())
                          .first())
        except sqlalchemy.orm.exc.NoResultFound:
            abort(404, message='Clause {} not found'.format(clause_id))
        return marshal(clause, annotation)

    @login_required
    def put(self, clause_id):
        """
        Add a new annotation for the given clause, parsed out of the HTTP
        PUT request object.
        """
        # get the clause
        try:
            clause = Clause.query.filter(Clause.id == clause_id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            abort(404, message='Clause {} not found'.format(clause_id))
        try:
            data, _ = AnnoSchema(strict=True).load(request.get_json())
        except ValidationError as e:
            abort(400, message=unicode(e))
        # create the new Annotation record
        new_record = Annotation(clause, current_user, **data)
        new_record.save()
        # return to user
        return marshal(clause, new_record)

api.add_resource(ClauseRsc, '/clauses/<int:clause_id>')

# @blueprint.route('/')
# @login_required
# def members():
#     """List members."""
#     return render_template('users/members.html')
