#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Adam on 2009-06-24.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('results.views',
	(r'^$',                    'show_events'),
	(r'^races/(?P<event>.+)$', 'show_races_event'),
	(r'^detail/(?P<key>.+)$',  'show_result'),
	(r'^details/(?P<key>.+)$', 'show_results'),
	(r'^delete$',              'cleardata'),
	(r'^upload/$',             'upload'),
	(r'^evtupload/$',             'evt_upload'),
	(r'^cron/$',               'buildleaders'),
	(r'^raceupload/$',         'race_upload'),
	(r'^purgera$',              'purge_race'),
	(r'^purgere$',              'purge_results'),
	(r'^purgee$',              'purge_event'),
	(r'^lif$',                 'lif_upload'),
)
