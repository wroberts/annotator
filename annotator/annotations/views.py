# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required
from flask_restful import Api, Resource
from marshmallow import Schema, fields
from annotator.annotations.models import Annotation, Clause

blueprint = Blueprint('annotation', __name__, url_prefix='/api', static_folder='../static')
api = Api(blueprint)

class CompSchema(Schema):
    """Marshmallow schema for SynArg and AspInd objects."""

    type = fields.Str()
    begin = fields.Int()
    end = fields.Int()


class AnnoSchema(Schema):
    """Marshmallow schema for Annotation objects."""

    invalid = fields.Function(lambda annotation: annotation.invalid.name)
    stative = fields.Function(lambda annotation: annotation.stative.name)
    bounded = fields.Function(lambda annotation: annotation.bounded.name)
    change = fields.Function(lambda annotation: annotation.change.name)


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
    Use Marshmallow to generate a JSON representation of a
    clause-annotation pair for a given user.
    """
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
        # get the clause
        clause = Clause.query.filter(Clause.id == clause_id).one()
        annotation = (Annotation.query
                      .filter(Annotation.clause_id == clause_id)
                      .filter(Annotation.user_id == 2)
                      .order_by(Annotation.created_at.desc())
                      .first())
        return marshal(clause, annotation)

    def put(self, clause_id):
        """
        Add a new annotation for the given clause, parsed out of the HTTP
        PUT request object.
        """
        # parse the PUT body
        #parser = reqparse.RequestParser()
        #parser.add_argument('invalid')
        #parser.add_argument('stative', type=int, help='Rate cannot be converted')
        #parser.add_argument('bounded')
        #parser.add_argument('change')
        #args = parser.parse_args()
        #todos[todo_id] = request.form['data']
        #return {todo_id: todos[todo_id]}
        pass

api.add_resource(ClauseRsc, '/clauses/<int:clause_id>')

# @blueprint.route('/')
# @login_required
# def members():
#     """List members."""
#     return render_template('users/members.html')
