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

from bios.models import Team, Country, Athlete

def show_athletes(request):
	return object_list(request,Athlete.all(),paginate_by = 10)
def show_athlete(request, key):
	return object_detail(request,Athlete.all(),key)
def show_teams(request):
	return object_list(request,Team.all())
def show_team(request, key):
	team = Team.get(key)
	return object_list(request,Athlete.gql("WHERE team = :1", team))
def show_countries(request):
	return object_list(request,Country.all(),paginate_by = 10)
def show_athletes_by_team(request,key):
	country = Country.all().filter("code = :1 LIMIT 1", key)
	return object_list(request,Team.gql("WHERE country = :1", country))
def show_athletes_by_country(request, key):
	country = Country.get(key)
	return object_list(request, Athlete.gql("WHERE country = :1", country))