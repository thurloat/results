#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Adam on 2009-07-02.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from django.contrib import admin
from bios.models import Athlete, Country, Crew

class AthleteInline(admin.TabularInline):
	model = Athlete

class AthleteAdmin(admin.ModelAdmin):
	inlines = (AthleteInline,)

admin.site.register(Country, AthleteAdmin)
admin.site.register(Crew)
