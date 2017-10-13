# -*- coding: utf-8 -*-
"""User views."""
import sqlalchemy.orm
from flask import Blueprint, request
from flask_restful import Api, Resource, abort
from flask_security.core import current_user
from marshmallow import Schema, ValidationError, fields, post_load
from sqlalchemy.sql import func

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

    annotation_idx = fields.Int(default=0, missing=0)
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
    notes = fields.Str(allow_none=True)

    @post_load
    def convert_to_enums(self, data):
        """Convert strings into BooleanUnsure values."""
        retval = dict((key, BooleanUnsure.__members__[value])
                      for (key, value) in data.items() if key not in ['annotation_idx',
                                                                      'notes'])
        if 'annotation_idx' in data:
            retval['annotation_idx'] = data['annotation_idx']
        if 'notes' in data:
            retval['notes'] = data['notes']
        return retval


class ClauseSchema(Schema):
    """Marshmallow schema for Clause objects."""

    id = fields.Integer()
    sentence = fields.Function(lambda clause: clause.text.split())
    verb_index = fields.Int(load_from='verb-index', dump_to='verb-index')
    prefix_index = fields.Int(load_from='prefix-index', dump_to='prefix-index')
    synargs = fields.List(fields.Nested(CompSchema),
                          load_from='verb-comps', dump_to='verb-comps')
    aspinds = fields.List(fields.Nested(CompSchema),
                          load_from='aspectual-indicators', dump_to='aspectual-indicators')
    last_annotation_date = fields.DateTime(format='iso', missing=None,
                                           load_from='last-annotation-date',
                                           dump_to='last-annotation-date')
    annotations = fields.List(fields.Nested(AnnoSchema, missing=None))
    last = fields.Boolean()


def marshal(clause, max_id, annotations):
    """Generate JSON for a clause-annotation pair for a given user."""
    clause.last = (clause.id == max_id)
    clause.annotations = annotations
    clause.last_annotation_date = None
    if annotations is not None and len(annotations) > 0:
        clause.last_annotation_date = max(annotation.created_at
                                          for annotation in annotations)
    return ClauseSchema().dump(clause)


class ClauseRsc(Resource):
    """REST API for interacting with clauses and annotations."""

    def get(self, clause_id):
        """
        Returns the given Clause.

        This method ensures that the returned object contains the most
        recent Annotation that this user made on it.
        """
        if not current_user.is_authenticated:
            abort(401)
        # get the clause
        try:
            subq = (db.session.query(func.max(Annotation.id).label('max_id'))
                    .group_by(Annotation.clause_id, Annotation.user_id, Annotation.annotation_idx)
                    .subquery())
            clause = Clause.query.filter(Clause.id == clause_id).one()
            max_id = db.session.query(Clause.id).order_by(Clause.id.desc()).first()
            max_id = max_id[0] if max_id else -1
            annotations = (Annotation.query
                           .filter(Annotation.clause_id == clause_id)
                           .filter(Annotation.user_id == current_user.id)
                           .join(subq, Annotation.id == subq.c.max_id)
                           .order_by(Annotation.annotation_idx).all())
        except sqlalchemy.orm.exc.NoResultFound:
            abort(404, message='Clause {} not found'.format(clause_id))
        return marshal(clause, max_id, annotations)

    def put(self, clause_id):
        """
        Add a new annotation for the given clause.

        Parses the updated object out of the HTTP PUT request object.
        """
        if not current_user.is_authenticated:
            abort(401)
        # get the clause
        try:
            clause = Clause.query.filter(Clause.id == clause_id).one()
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
        return self.get(clause_id)


api.add_resource(ClauseRsc, '/clauses/<int:clause_id>')
