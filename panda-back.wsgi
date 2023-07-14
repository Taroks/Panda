#!/usr/bin/python3
import sys, os


# Add <path> to PYTHONPATH to let python find packages
def application(wsgi_env, start_response):
    sys.path.insert(0, '/var/www/panda-back')

    from Internal.API.ParserAPI import app as application

    if wsgi_env.get('KRB5CCNAME'):
        os.environ['KRB5CCNAME'] = wsgi_env['KRB5CCNAME']
    return application(wsgi_env, start_response)
# This import is for Apache2 which search object 'application' in *.wsgi file to run server.

