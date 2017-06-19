# -*- coding: utf-8 -*-
"""User views."""
import sqlalchemy.orm
from flask import Blueprint, request
from flask_restful import Api, Resource, abort
from flask_security.core import current_user
from marshmallow import Schema, ValidationError, fields, post_load

from annotator.annotations.models import Annotation, BooleanUnsure, Clause
from annotator.compat import text_type
from annotator.extensions import csrf_protect, db

blueprint = Blueprint('api', __name__, url_prefix='/api', static_folder='../static')
csrf_protect.exempt(blueprint)
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
    extended = fields.Function(lambda annotation: annotation.extended.name,
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
    last = fields.Boolean()


def marshal(clause, max_id, annotation):
    """
    Generate JSON for a clause-annotation pair for a given user.
    """
    clause.last = (clause.id == max_id)
    clause.annotation = annotation
    clause.last_annotation_date = None
    if annotation is not None:
        clause.last_annotation_date = annotation.created_at
    return ClauseSchema().dump(clause)


class ClauseRsc(Resource):
    """REST API for interacting with clauses and annotations."""

    def get(self, clause_id):
        """
        Returns the given Clause, with the most recent Annotation that
        this user made on it inserted.
        """
        if not current_user.is_authenticated:
            abort(401)
        # get the clause
        try:
            clause = Clause.query.filter(Clause.id == clause_id).one()
            max_id = db.session.query(Clause.id).order_by(Clause.id.desc()).first()
            max_id = max_id[0] if max_id else -1
            annotation = (Annotation.query
                          .filter(Annotation.clause_id == clause_id)
                          .filter(Annotation.user_id == current_user.id)
                          .order_by(Annotation.created_at.desc())
                          .first())
        except sqlalchemy.orm.exc.NoResultFound:
            abort(404, message='Clause {} not found'.format(clause_id))
        return marshal(clause, max_id, annotation)

    def put(self, clause_id):
        """
        Add a new annotation for the given clause, parsed out of the HTTP
        PUT request object.
        """
        if not current_user.is_authenticated:
            abort(401)
        # get the clause
        try:
            clause = Clause.query.filter(Clause.id == clause_id).one()
            max_id = db.session.query(Clause.id).order_by(Clause.id.desc()).first()
            max_id = max_id[0] if max_id else -1
        except sqlalchemy.orm.exc.NoResultFound:
            abort(404, message='Clause {} not found'.format(clause_id))
        try:
            data, _ = AnnoSchema(strict=True).load(request.get_json())
        except ValidationError as e:
            abort(400, message=text_type(e))
        # create the new Annotation record
        new_record = Annotation(clause, current_user, **data)
        new_record.save()
        # return to user
        return marshal(clause, max_id, new_record)

api.add_resource(ClauseRsc, '/clauses/<int:clause_id>')
