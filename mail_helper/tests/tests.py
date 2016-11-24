#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

from django.test import TestCase

from django.http import request
from django.template import Context
from django.conf import settings
from django.core import mail
from django.utils.translation import gettext_lazy as _

from mail_helper import utils


class TestUtils(TestCase):

    """Testcase for utils functions"""

    def test_build_mail_context_with_locale(self):
        raw_content_dict = {"var1": 'vvv1', 'var2': 'vvv2'}

        en_ctx = Context(raw_content_dict)
        en_ctx['LANGUAGE_CODE'] = 'en'
        en_ctx['LANGUAGES'] = settings.LANGUAGES
        zh_ctx = Context(raw_content_dict)
        zh_ctx['LANGUAGE_CODE'] = 'zh-Hant'
        zh_ctx['LANGUAGES'] = settings.LANGUAGES

        test_cases = [
            ('en', en_ctx),
            ('zh-Hant', zh_ctx),
            ('wrong', en_ctx),  # default language is en
        ]

        for l, exp in test_cases:
            got = utils.build_mail_context_with_locale(raw_content_dict, locale=l)
            self.assertEqual(
                exp, got, "\n\nParam: {}\n\nExp: {}\n\nGot: {}\n\n".format((raw_content_dict, l), exp, got))

    def test_build_mail_context_with_request(self):
        raw_content_dict = {"var1": 'vvv1', 'var2': 'vvv2'}

        en_ctx = Context(raw_content_dict)
        en_ctx['LANGUAGE_CODE'] = 'en'
        en_ctx['LANGUAGES'] = settings.LANGUAGES
        zh_ctx = Context(raw_content_dict)
        zh_ctx['LANGUAGE_CODE'] = 'zh-Hant'
        zh_ctx['LANGUAGES'] = settings.LANGUAGES

        en_request = request.HttpRequest()
        en_request.META['HTTP_ACCEPT_LANGUAGE'] = 'en'
        zh_request = request.HttpRequest()
        zh_request.META['HTTP_ACCEPT_LANGUAGE'] = 'zh-Hant'
        w_request = request.HttpRequest()
        w_request.META['HTTP_ACCEPT_LANGUAGE'] = 'wrong'

        test_cases = [
            (en_request, en_ctx),
            (zh_request, zh_ctx),
            (w_request, en_ctx),
        ]

        for r, exp in test_cases:
            got = utils.build_mail_context_with_request(raw_content_dict, r)
            self.assertEqual(
                exp, got, "\n\nParam: {}\n\nExp: {}\n\nGot: {}\n\n".format((raw_content_dict, r), exp, got))

    def test_resolve_template(self):
        # copy from django source, skip testing
        pass

    def test_resolve_content(self):
        raw_content_dict = {"var1": 'vvv1', 'var2': 'vvv2'}

        en_ctx = Context(raw_content_dict)
        en_ctx['LANGUAGE_CODE'] = 'en'
        en_ctx['LANGUAGES'] = settings.LANGUAGES
        en_dict = copy.deepcopy(raw_content_dict)
        en_dict.update({'LANGUAGE_CODE': 'en'})

        exp, got = en_ctx, utils.resolve_context(en_dict)
        self.assertEqual(exp, got, "\n\nparam: {}\n\nExp: {}\n\nGot: {}\n\n".format(en_dict, exp, got))

        zh_ctx = Context(raw_content_dict)
        zh_ctx['LANGUAGE_CODE'] = 'zh-Hant'
        zh_ctx['LANGUAGES'] = settings.LANGUAGES
        zh_dict = copy.deepcopy(raw_content_dict)
        zh_dict.update({'LANGUAGE_CODE': 'zh-Hant'})

        exp, got = en_ctx, utils.resolve_context(zh_dict)
        self.assertEqual(exp, got, "\n\nparam: {}\n\nExp: {}\n\nGot: {}\n\n".format(zh_dict, exp, got))

        test_exceptions = [
            (1, ValueError),
            ([1, 1, ], TypeError),
            ((1, 1, ), TypeError),
        ]

        for c, err in test_exceptions:
            self.assertRaises(err, utils.resolve_template, c)

    def test_send_with_template(self):
        raw_content_dict = {"var1": 'vvv1', 'var2': 'vvv2'}
        zh_dict = {"var1": 'vvv1', 'var2': 'vvv2', 'LANGUAGE_CODE': 'zh-Hant'}

        sender, reciever, subject = 'from@email.com', ['to@email.com'], _("tMSG001")

        for _dict in [raw_content_dict, zh_dict]:
            utils.send_with_template(subject, sender, reciever, 'mail_helper/test_mail.html', _dict)

        test_cases = [
            ("Test mail title", "Test mail content with vars: vvv1, vvv2"),
            ("測試郵件標題", "測試郵件內容與變數: vvv1, vvv2"),
        ]

        for m, c in zip(mail.outbox, test_cases):
            msg = m.message().as_bytes()
            for _c in c:
                self.assertIn(_c.encode(), msg)
