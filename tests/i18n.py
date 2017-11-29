# -*- coding: utf-8 -*-
import unittest
from unittest import TestCase
from flask import request
from common import create_app
from jsonlint import StringField
from jsonlint.validators import DataRequired, Length

from flask_lint import FlaskLint


class NameLint(FlaskLint):
    name = StringField(validators=[DataRequired(), Length(min=8)])


class I18NTest(TestCase):
    def setUp(self):
        app = create_app()
        self.app = app
        self.client = app.test_client()

    def test_no_extension(self):
        @self.app.route('/', methods=['POST'])
        def index():
            lint = NameLint()
            lint.validate()
            self.assertEqual(lint.name.errors[0], 'This field is required.')

        self.client.post(
            '/', headers={'Accept-Language': 'zh-CN,zh;q=0.8'}
        )

    def test_i18n(self):
        try:
            from flask_babel import Babel
        except ImportError:
            try:
                from flask_babelex import Babel
            except ImportError:
                unittest.skip('Flask-Babel or Flask-BabelEx must be installed.')

        babel = Babel(self.app)

        @babel.localeselector
        def get_locale():
            return request.accept_languages.best_match(['en', 'zh'], 'en')

        @self.app.route('/', methods=['POST'])
        def index():
            lint = NameLint()
            lint.validate()

            if not self.app.config.get('WTF_I18N_ENABLED', True):
                self.assertEqual(lint.name.errors[0], 'This field is required.')
            elif not lint.name.data:
                self.assertEqual(lint.name.errors[0], u'该字段是必填字段。')
            else:
                self.assertEqual(lint.name.errors[0], u'字段长度必须至少 8 个字符。')

        self.client.post('/', headers={'Accept-Language': 'zh-CN,zh;q=0.8'})
        self.client.post(
            '/', headers={'Accept-Language': 'zh'}, data={'name': 'short'}
        )
        self.app.config['WTF_I18N_ENABLED'] = False
        self.client.post('/', headers={'Accept-Language': 'zh'})

    def test_outside_request(self):
        from flask_lint.i18n import translations

        s = 'This field is required.'

        self.assertEqual(translations.gettext(s), s)

        ss = 'Field must be at least %(min)d character long.'
        sp = 'Field must be at least %(min)d character long.'
        self.assertEqual(translations.ngettext(ss, sp, 1), ss)
        self.assertEqual(translations.ngettext(ss, sp, 2), sp)
