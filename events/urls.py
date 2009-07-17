#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by Adam on 2009-07-02.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('events.views',
	(r'^$', 'list_latest'),
)
