# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required
from flask_security.core import current_user

from annotator.annotations.models import Annotation, Clause
from annotator.extensions import db
from annotator.user.models import User

blueprint = Blueprint('annotations', __name__, url_prefix='/annotations', static_folder='../static')


@blueprint.route('/')
@login_required
def dashboard():
    """User dashboard."""
    # select user and the number of clauses they have annotated
    user_info = [{'user': user,
                  'last_annotation_date': (Annotation.query
                                           .filter(Annotation.user_id == user.id)
                                           .order_by(Annotation.created_at.desc())
                                           .first().created_at),
                  'num_annotated_clauses': (Clause.query
                                            .filter(Clause.annotations.any(
                                                Annotation.user_id == user.id))
                                            .count())}
                 for user in User.query.all() if
                 (Clause.query
                  .filter(Clause.annotations.any(Annotation.user_id == user.id))
                  .count())]
    context = {
        'number_total_clauses': Clause.query.count(),
        'number_annotated_clauses': (Clause.query
                                     .filter(Clause.annotations.any(Annotation.user_id == current_user.id))
                                     .count()),
        'first_unannotated_clause': (db.session.query(Clause.id)
                                     .filter(~Clause.annotations.any(Annotation.user_id == current_user.id))
                                     .order_by(Clause.id).first()),
        'last_annotated_clause': (db.session.query(Clause.id)
                                  .filter(Clause.annotations.any(Annotation.user_id == current_user.id))
                                  .order_by(Clause.id.desc()).first()),
        'user_info': sorted(user_info, key=lambda row: row['num_annotated_clauses'], reverse=True),
    }
    return render_template('users/dashboard.html', **context)


@blueprint.route('/interface/')
@login_required
def interface():
    """Annotation interface with Angular single-page app."""
    return render_template('users/annotation.html')
