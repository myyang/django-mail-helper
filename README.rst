mail_helper
========

This Django app contains functions and shortcuts for mail service.

How to Install
--------------

1. add to `INSTALLED_APPS`

   .. code:: python
   
       INSTALLED_APPS = [
           ...,
           'mail_helper',
       ]

2. setup django mail backend configs in `settings.py`, example:

   .. code:: python
   
       EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
       # Host for sending email.
       EMAIL_HOST = 'smtp.office365.com'
       EMAIL_PORT = 587 
       # Optional SMTP authentication information for EMAIL_HOST.
       EMAIL_HOST_USER = 'mail-bot@email.com'
       EMAIL_HOST_PASSWORD = 'mail-bot_passowrd'
       # Optional for encryption
       EMAIL_USE_TLS = True
       EMAIL_USE_SSL = True
       EMAIL_SSL_CERTFILE = /etc/ssl/cert.pem
       EMAIL_SSL_KEYFILE = /etc/ssl/key.pem
       EMAIL_TIMEOUT = 30


3. (*OPTIONAL*) create mail templates' app for placing templates and locales file

How it works
------------

mail_helper take Django tempalte mechanism to render html mail content and locale system to translate mail content.
Web briefly describe the steps here:

1. Read template with django TemplateReponse Rule
2. Validate locales
3. Translate and render mail contet
4. Send mail through Django mail mechanism

Usage
-----

Example: 

.. code:: python

   from mail_helper import utils

   ctx = utils.build_mail_context_with_request(
       {"user": "Garfield", "click_url": "https://localhost/website/"}, request)
   utils.send_with_template(
       "Mail Subject", "from@email.com", ["to@email.com", "to2@email.com"],
       "mail_template/mail.html", ctx)


TODO
----

[ ] Flexibility: plugins, extensions

License
-------

MIT


.. vim:set et sw=4 ts=4:
