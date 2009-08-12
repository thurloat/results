#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Adam on 2009-06-24.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from django.contrib import admin
from results.models import Race, Results, Event

class RaceInline(admin.TabularInline):
	model = Race

class EventAdmin(admin.ModelAdmin):
	inlines = (RaceInline,)
	
admin.site.register(Event,EventAdmin)
