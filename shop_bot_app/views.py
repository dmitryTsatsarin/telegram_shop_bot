# -*- coding: utf-8 -*-
import logging

import sys
import traceback
import arrow
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render

from shop_bot_app.helpers import get_request_data
from shop_bot_app.tasks import CollectorTask


logger = logging.getLogger(__name__)


def webhooks(request, token):
    try:
        print 'Started %s ' % request.get_full_path()

        if 'CONTENT_LENGTH' in request.META and 'CONTENT_TYPE' in request.META and request.META['CONTENT_TYPE'] == 'application/json':
            json_string = get_request_data(request)
            message_created_at = arrow.now().datetime
            CollectorTask().apply_async(args=[token, json_string, message_created_at])
            return HttpResponse('')
        else:
            print 'Forbiden for %s' % request.body
            return HttpResponseForbidden()
    except Exception as e:
        t, v, tb = sys.exc_info()
        traceback.print_exc(tb, file=sys.stdout)
        raise


def main_page(request):
    return render(request, 'main.html', {})