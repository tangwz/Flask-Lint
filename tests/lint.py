# -*- coding: utf-8 -*-
from common import create_app
from unittest import TestCase
from flask import json, request
from jsonlint import StringField
from jsonlint.validators import DataRequired

from flask_lint import FlaskLint


class BasicLint(FlaskLint):
    name = StringField(validators=[DataRequired()])


class LintTest(TestCase):
    def setUp(self):
        app = create_app()
        self.app = app
        self.client = app.test_client()

    def test_populate_from_form(self):
        @self.app.route('/', methods=['POST'])
        def index():
            lint = BasicLint()
            self.assertEqual(lint.name.data, 'lint')

        self.client.post('/', data={'name': 'lint'})

    def test_populate_from_json(self):
        @self.app.route('/', methods=['POST'])
        def index():
            lint = BasicLint()
            self.assertEqual(lint.name.data, 'json')

        self.client.post(
            '/', data=json.dumps({'name': 'json'}),
            content_type='application/json'
        )

    def test_populate_from_args(self):
        @self.app.route('/', methods=['GET'])
        def index():
            lint = BasicLint()
            self.assertEqual(lint.name.data, 'args')

        self.client.get(
            '/', query_string={'name': 'args'},
        )

    def test_populate_manually(self):
        @self.app.route('/', methods=['POST'])
        def index():
            lint = BasicLint(request.args)
            self.assertEqual(lint.name.data, 'args')

        self.client.post('/', query_string={'name': 'args'})

    def test_populate_none(self):
        @self.app.route('/', methods=['POST'])
        def index():
            lint = BasicLint(None)
            self.assertTrue(lint.name.data is None)

        self.client.post('/', data={'name': 'ignore'})

    def test_validate_on_submit(self):
        @self.app.route('/', methods=['POST'])
        def index():
            lint = BasicLint()
            self.assertTrue(lint.is_submitted())
            self.assertTrue(not lint.validate_on_submit())
            self.assertTrue('name' in lint.errors)

        self.client.post('/')
