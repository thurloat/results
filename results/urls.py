#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Adam on 2009-06-24.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('results.views',
	(r'^$', 'show_races'),
	(r'^detail/(?P<key>.+)$', 'show_result'),
	(r'^details/(?P<key>.+)$', 'show_results'),
	(r'^delete$', 'cleardata'),
	(r'^upload/$', 'upload'),
	(r'^cron/$', 'buildleaders'),
)
