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

from gaepimage.models import Image

def inrto(request):
    return "Introduction Goes Here"
def render_image(request, model, property, id):
    print request
    print model
    print property
    print id
    
    q = db.GqlQuery("SELECT * FROM  WHERE __key__ = 'agdjYW5vZTA5chILEgxldmVudHNfZXZlbnQYAQw'").fetch(1)
    return q  
    event = Image.all()
    if event and event.image: 
        response = HttpResponse()
        response['Content-Type'] = 'image/png'
        response.write(event.image)
        return response
    else:
        raise Http404('Sorry, I couldnt find that image!')