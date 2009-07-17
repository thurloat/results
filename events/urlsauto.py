#!/usr/bin/env python
# encoding: utf-8
"""
urlsauto.py

Created by Adam on 2009-07-02.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
from django.conf.urls.defaults import *

rootpatterns = patterns('',
    (r'^events/', include('events.urls')),
)
