#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    mail_helper.utils
    ~~~~~~~~~~~~~

    Utilities and shortcuts for mail functions by using EMAIL_BACKEND config

    :copyright: (c) 2016 by garfield_yang.
    :license: MIT, see LICENSE for more details.
"""

import contextlib

from django.conf import settings
from django.core import mail
from django.template import Context, Template, loader
from django.utils import six, translation

from django.contrib import auth


def build_mail_context_with_locale(content_dict, locale=settings.LANGUAGE_CODE):
    """Build context with given content dict and locale value

    :param content_dict: content dictionary
    :param locale: given locale or settings.LANGUAGE_CODE
    :returns: TODO

    """
    ctx = Context(content_dict)
    ctx['LANGUAGES'] = settings.LANGUAGES
    ctx['LANGUAGE_CODE'] = locale
    return ctx


def build_mail_context_with_request(content_dict, request):
    """build context with given content and request

    :param content_dict: content dictionary
    :param request: django request from client
    :returns: TODO

    """
    try:
        locale = getattr(auth.get_user(request), 'lang', None)
    except Exception:
        locale = None
    locale = locale or translation.get_language_from_request(request)
    return build_mail_context_with_locale(content_dict, locale=locale)


def resolve_template(template, using=None):
    """
    Borrow from django.template.response.SimpleTemplateResponse

    Accepts a template object, path-to-template or list of paths
    """
    if isinstance(template, (list, tuple)):
        return loader.select_template(template, using=using)
    elif isinstance(template, six.string_types):
        return loader.get_template(template, using=using)
    elif isinstance(template, Template):
        return template

    raise ValueError("template should be one of following type: (list, tuple, string, Template)")


def resolve_context(context):
    """
    convert context to proper instnace for processing

    :param context: Context isinstance or dict
    :returns: TODO

    """
    if isinstance(context, dict):
        return build_mail_context_with_locale(context, locale=context.get('LANGUAGE_CODE', settings.LANGUAGE_CODE))
    elif isinstance(context, Context):
        return context

    raise ValueError("conte should be one of following type: (dict, Context)")


def _check_lang_code(context):
    """Check LANGUAGES and LANGUAGE_CODE in context.
    If not, filled with default value

    :param context: TODO
    :returns: TODO

    """
    if 'LANGUAGES' not in context:
        context['LANGUAGES'] = settings.LANGUAGES

    if 'LANGUAGE_CODE' not in context:
        context['LANGUAGE_CODE'] = settings.LANGUAGE_CODE


@contextlib.contextmanager
def _dummy_translation_env(locale=settings.LANGUAGE_CODE):
    """While testing these is no specific locale settings.
    With this context manager, we can simulate real request and **HIDE** translate tag id when
    translation mechanism fail

    :param locale: temporarily activated locale
    :returns: TODO

    """
    old_lang = translation.get_language()
    translation.activate(locale)
    yield
    translation.activate(old_lang)


def send_with_template(subject, from_email, recipient_list, template, context):
    """Send mail by django template render engine

    :param request: django request which stores various info for rendering template
    :param template: use like the tempalte_name in TemplateResponse
    :param context: content dictionary or Context instance for template
    :returns: TODO

    """

    tpl = resolve_template(template)
    ctx = resolve_context(context)
    _check_lang_code(ctx)
    connection = mail.get_connection()
    with _dummy_translation_env(ctx['LANGUAGE_CODE']):
        subject = ''.join(subject() if callable(subject) else str(subject).splitlines())
        new_mail = mail.EmailMultiAlternatives(
            str(subject), '', from_email, recipient_list, connection=connection)
        new_mail.attach_alternative(tpl.render(ctx), 'text/html')
        new_mail.send()


def get_renderable_subject(subj_tpl, ctx):
    """TODO: Docstring for render_trans_subject.

    :param subj_tpl: subject template name
    :param ctx: context
    :returns: TODO

    """
    tpl = resolve_template(subj_tpl)
    _check_lang_code(ctx)
    sub = ''
    with _dummy_translation_env(ctx['LANGUAGE_CODE']):
        sub = tpl.render(ctx)
    return sub[:-1]


# vim:set et sw=4 ts=4 tw=99:
