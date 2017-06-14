# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required
from flask_restful import Api, Resource, url_for, fields, marshal_with, reqparse
from annotator.annotations.models import Annotation, Clause

blueprint = Blueprint('annotation', __name__, url_prefix='/api', static_folder='../static')
api = Api(blueprint)

comp_fields = {
    "type": fields.String(),
    "begin": fields.Integer(),
    "end": fields.Integer()
    }

anno_fields = {
    "invalid": fields.String(attribute=lambda annotation: annotation.invalid.name),
    "stative": fields.String(attribute=lambda annotation: annotation.stative.name),
    "bounded": fields.String(attribute=lambda annotation: annotation.bounded.name),
    "change": fields.String(attribute=lambda annotation: annotation.change.name),
}

clause_fields = {
    "id": fields.Integer(),
    "sentence": fields.List(fields.String, attribute=lambda clause: clause.text.split()),
    "verb-index": fields.Integer(attribute="verb_index"),
    "verb-comps": fields.List(fields.Nested(comp_fields), attribute="synargs"),
    "aspectual-indicators": fields.List(fields.Nested(comp_fields), attribute="synargs"),
    "last-annotation-date": fields.DateTime(
        dt_format='rfc822',
        attribute=lambda clause: clause.annotation.created_at if clause.annotation else None),
    "annotation": fields.Nested(anno_fields, allow_null=True),
}

class ClauseRsc(Resource):
    @marshal_with(clause_fields)
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
        clause.annotation = annotation
        return clause

    @marshal_with(clause_fields)
    def put(self, clause_id):
        # parse the PUT body
        parser = reqparse.RequestParser()
        parser.add_argument('invalid')
        parser.add_argument('stative', type=int, help='Rate cannot be converted')
        parser.add_argument('bounded')
        parser.add_argument('change')
        args = parser.parse_args()
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}

api.add_resource(ClauseRsc, '/clauses/<int:clause_id>')

# @blueprint.route('/')
# @login_required
# def members():
#     """List members."""
#     return render_template('users/members.html')
