#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Adam on 2009-06-24.
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

from results.models import Race, Results

def show_races(request):
	return object_list(request,Race.all(),paginate_by = 2)
def show_race(request, key):
	return object_list(request,Race.all(),key)
def show_result(request, key):
	return object_detail(request,Results.all(),key)
def show_results(request, key):
	race = Race.get(key)
	return object_list(request,Results.gql("WHERE race = :1", race))