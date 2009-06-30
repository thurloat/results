#!/usr/bin/env python
# encoding: utf-8
"""
results.py

Created by Adam on 2009-06-15.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
from django.db.models import permalink, signals
from google.appengine.ext import db
from ragendja.dbutils import cleanup_relations

class Race(db.Model):
	raceNumber = db.StringProperty()
	roundNumber = db.StringProperty()
	heatNumber = db.StringProperty()
	description = db.StringProperty()
	windSpeed = db.StringProperty()
	weather = db.StringProperty()
	
	def __unicode__(self):
		return '%s - %s' % (self.raceNumber, self.description)
	
	def __json__(self):
		return self.description
	
	@permalink	
	def get_absolute_url(self):
		return ('results.views.show_race', (), {'key': self.key()})
	
	class Admin:
		list_display = ('raceNumber', 'roundNumber', 'heatNumber', 'description')
		list_filter = ('heatNumber', 'roundNumber')
		search_fields = ('description',)

class Results(db.Model):
	place = db.StringProperty()
	athleteNumber = db.StringProperty()
	laneNumber = db.StringProperty()
	lastName = db.StringProperty()
	firstName = db.StringProperty()
	countryCode = db.StringProperty()
	finalTime = db.StringProperty()
	deltaTime = db.StringProperty()
	splitDetails = db.StringProperty()
	race = db.ReferenceProperty(Race, required=True)
	
	def __unicode__(self):
		return 'p:%s. , n:%s , c:%s , t:%s' % (self.place, self.lastName, self.countryCode, self.finalTime)

	@permalink
	def get_absolute_url(self):
		return ('results.views.show_result', (), {'key': self.key()})

