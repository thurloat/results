#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Adam on 2009-07-02.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, delete_object, \
    update_object
from google.appengine.ext import db
from mimetypes import guess_type
from ragendja.dbutils import get_object_or_404
from ragendja.template import render_to_response

from events.models import Event

def list_latest(request):
	return object_list(request,Event.all())
def event_detail(request, id):
    return object_detail(request,Event.all(),slug_field="eventNumber",slug=int(id), template_name="mobile-eventDetail.html", template_object_name = "event")
def image_view(request, id):
    event = Event.all().filter("eventNumber =",int(id)).get()
    if event and event.image: 
        response = HttpResponse()
        response['Content-Type'] = 'image/png'
        response.write(event.image)
        return response
    else:
        raise Http404('Sorry, I couldnt find that image!')