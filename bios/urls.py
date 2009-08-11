#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Adam on 2009-07-02.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('bios.views',
	(r'^$', 'show_bios_overview_mobile'),
	(r'^img/(?P<id>.+)/$', 'image_view'),
	(r'^athletes/(?P<country>[A-Z]{3})/$', 'show_athletes_all_country'),
	(r'^athletes/(?P<country>[A-Z]{3})/(?P<crewNum>.+)/$', 'show_athletes_country_crew'),
	(r'^athlete/(?P<identifier>.+)/$', 'show_athlete'),
	(r'^upload/$', 'bio_upload'),
	(r'^crew/(?P<key>.+)/$', 'show_crew'),
)
