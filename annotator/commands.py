# -*- coding: utf-8 -*-
"""Click commands."""
import csv
import json
import os
from glob import glob
from subprocess import call

import click
import tqdm
import wkr
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy.sql import func
from werkzeug.exceptions import MethodNotAllowed, NotFound

from annotator.annotations.models import Annotation, AspInd, Clause, SynArg
from annotator.user.models import User

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """Run the tests."""
    import pytest
    rv = pytest.main([TEST_PATH, '--verbose'])
    exit(rv)


@click.command()
@click.option('-f', '--fix-imports', default=False, is_flag=True,
              help='Fix imports using isort, before linting')
def lint(fix_imports):
    """Lint and check code style with flake8 and isort."""
    skip = ['migrations', 'node_modules', 'requirements']
    root_files = glob('*.py')
    root_directories = [
        name for name in next(os.walk('.'))[1] if not name.startswith('.')]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo('{}: {}'.format(description, ' '.join(command_line)))
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    if fix_imports:
        execute_tool('Fixing import order', 'isort', '-rc')
    execute_tool('Checking code style', 'flake8')


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.

    Borrowed from Flask-Script, converted to use Click.
    """
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dirpath, filename)
                click.echo('Removing {}'.format(full_pathname))
                os.remove(full_pathname)


@click.command()
@click.option('--url', default=None,
              help='Url to test (ex. /static/image.png)')
@click.option('--order', default='rule',
              help='Property on Rule to order by (default: rule)')
@with_appcontext
def urls(url, order):
    """Display all of the url matching routes for the project.

    Borrowed from Flask-Script, converted to use Click.
    """
    rows = []
    column_length = 0
    column_headers = ('Rule', 'Endpoint', 'Arguments')

    if url:
        try:
            rule, arguments = (
                current_app.url_map
                           .bind('localhost')
                           .match(url, return_rule=True))
            rows.append((rule.rule, rule.endpoint, arguments))
            column_length = 3
        except (NotFound, MethodNotAllowed) as e:
            rows.append(('<{}>'.format(e), None, None))
            column_length = 1
    else:
        rules = sorted(
            current_app.url_map.iter_rules(),
            key=lambda rule: getattr(rule, order))
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, None))
        column_length = 2

    str_template = ''
    table_width = 0

    if column_length >= 1:
        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4
        str_template += '{:' + str(max_rule_length) + '}'
        table_width += max_rule_length

    if column_length >= 2:
        max_endpoint_length = max(len(str(r[1])) for r in rows)
        # max_endpoint_length = max(rows, key=len)
        max_endpoint_length = (
            max_endpoint_length if max_endpoint_length > 8 else 8)
        str_template += '  {:' + str(max_endpoint_length) + '}'
        table_width += 2 + max_endpoint_length

    if column_length >= 3:
        max_arguments_length = max(len(str(r[2])) for r in rows)
        max_arguments_length = (
            max_arguments_length if max_arguments_length > 9 else 9)
        str_template += '  {:' + str(max_arguments_length) + '}'
        table_width += 2 + max_arguments_length

    click.echo(str_template.format(*column_headers[:column_length]))
    click.echo('-' * table_width)

    for row in rows:
        click.echo(str_template.format(*row[:column_length]))


@click.command()
@with_appcontext
def drop_db():
    """Drop all databases, except for user information."""
    if click.confirm('Are you sure you want to continue?', abort=True):
        AspInd.query.delete()
        SynArg.query.delete()
        Annotation.query.delete()
        Clause.query.delete()
        current_app.extensions['sqlalchemy'].db.session.commit()


@click.command()
@click.argument('jsonfile', type=click.Path(exists=True))
@with_appcontext
def create_corpus(jsonfile):
    """
    Write a description of a corpus from file to the DB.

    :param str jsonfile: the path to the JSON-formatted corpus
        description
    """
    iterator = tqdm.tqdm(wkr.lines(jsonfile),
                         unit='clause',
                         total=wkr.io.count_lines(jsonfile))
    for line in iterator:
        # recover the object dump from the line
        item = json.loads(line.strip())
        # create a Clause object from the item
        text = u' '.join(item['words'])
        verb_index = item['windex']
        prefix_index = item['pwindex']
        # can also pass additional kwargs, e.g. "id"
        clause = Clause(text, verb_index, prefix_index)
        clause.save()
        postfix = {'Cl.:': clause.id}
        # create AspInds
        for aitem in item['aspinds']:
            atype, begin, end = aitem
            aspind = AspInd(atype, begin, end, clause)
            aspind.save()
        # create SynArgs
        for sitem in item['synargs']:
            stype, begin, end = sitem
            synarg = SynArg(stype, begin, end, clause)
            synarg.save()
        iterator.set_postfix(**postfix)


@click.command()
@click.argument('jsonfile', type=click.Path(exists=True))
@with_appcontext
def upgrade_corpus_v2(jsonfile):
    """
    Upgrade a corpus created with create_corpus to DB v2.

    v2 adds the sindex, windex, and verb fields.
    """
    iterator = tqdm.tqdm(wkr.lines(jsonfile),
                         unit='clause',
                         total=wkr.io.count_lines(jsonfile))
    for idx, line in enumerate(iterator, 1):
        # recover the object dump from the line
        item = json.loads(line.strip())
        # get the clause from the DB
        clause = Clause.query.filter(Clause.id == idx).first()
        # double-check that we have the right one
        assert clause.verb_index == item['windex']
        assert clause.prefix_index == item['pwindex']
        assert clause.text == u' '.join(item['words'])
        u' '.join(item['words'])
        # add .sindex and .windex fields
        clause.sindex = item['sindex']
        clause.windex = item['orig_windex']
        clause.verb = item['verb']
        # save
        clause.save()
        postfix = {'Cl.:': clause.id}
        iterator.set_postfix(**postfix)


@click.command()
@with_appcontext
def export():
    """
    Export the annotations currently stored in the database to CSV format.

    Writes the CSV data out on standard output.
    """
    session = current_app.extensions['sqlalchemy'].db.session
    with wkr.open('-', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL)
        # header
        csvwriter.writerow(['id',
                            'clause_sindex',
                            'clause_windex',
                            'user_email',
                            'invalid',
                            'stative',
                            'bounded',
                            'extended',
                            'change'])
        # https://stackoverflow.com/a/1313140/1062499
        #
        # subquery: find the largest (most recent) annotations for each clause
        # and user combination
        subq = (session.query(func.max(Annotation.id).label('max_id'))
                .group_by(Annotation.clause_id, Annotation.user_id)
                .subquery())
        # inner join Annotation on these id values
        for annotation, clause, user in (session.query(Annotation, Clause, User)
                                         .join(subq, Annotation.id == subq.c.max_id)
                                         .join(Clause)
                                         .join(User)
                                         .order_by(Annotation.clause_id).all()):
            csvwriter.writerow([annotation.id,
                                clause.sindex,
                                clause.windex,
                                user.email,
                                annotation.invalid.name,
                                annotation.stative.name,
                                annotation.bounded.name,
                                annotation.extended.name,
                                annotation.change.name])
