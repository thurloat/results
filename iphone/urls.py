#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Adam on 2009-07-02.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('bios.views',
	(r'^athletes/(?P<team>\d{3})/$', 'show_athletes_by_team'),
	(r'^athletes/(?P<country>[A-Z]{3})/$', 'show_athletes_by_country'),
	(r'^athletes/(?P<country>[A-Z]{3})/(?P<identifier>.+)$', 'show_athlete'),
	(r'^teams$', 'show_teams'),
	(r'^team/(?P<key>.+)$', 'show_team'),
)
