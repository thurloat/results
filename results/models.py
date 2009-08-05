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

class EventClass(db.Model):
	description = db.StringProperty()
	shortHand = db.StringProperty()
	
	def __unicode__(self): return self.shortHand

class EventDistance(db.Model):
	distance = db.StringProperty()
	
	def __unicode__(self): return self.distance
	
class EventGender(db.Model):
	gender = db.StringProperty()
	
	def __unicode__(self): return self.gender

class Event(db.Model):
	eventNumber = db.IntegerProperty()
	eventClass = db.ReferenceProperty(EventClass)
	distance = db.ReferenceProperty(EventDistance)
	gender = db.ReferenceProperty(EventGender)
	
	def __unicode__(self): return '%s - %s - %s' % (self.eventClass,self.distance,self.gender)

class Race(db.Model):
	raceNumber = db.IntegerProperty()
	roundNumber = db.StringProperty()
	heatNumber = db.StringProperty()
	description = db.StringProperty()
	windSpeed = db.StringProperty()
	weather = db.StringProperty()
	hasResults = db.BooleanProperty()
	
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
	place = db.IntegerProperty()
	athleteNum = db.StringProperty()
	laneNumber = db.StringProperty()
	lastName = db.StringProperty()
	firstName = db.StringProperty()
	countryCode = db.StringProperty()
	finalTime = db.StringProperty()
	deltaTime = db.StringProperty()
	splitDetails = db.StringProperty()
	time = db.TimeProperty()
	race = db.ReferenceProperty(Race, required=True)
	
	def put(self):
		db.Model.put(self)
		if self.finalTime is not None:
			from datetime import time
			str = self.finalTime.split(":")
	        if len(str) == 1:
	            s = str[0].split(".")
	            t = time(second=int(s[0]), microsecond=(int(s[1]) * 1000))
	            pass
	        elif len(str) == 2:
	            s = str[1].split(".")
	            t = time(minute=int(str[0]), second=int(s[0]), microsecond=(int(s[1]) * 1000))
	        elif len(str) == 3:
	            s = str[2].split(".")
	            t = time(hour=int(str[0]), minute=int(str[1]), second=int(s[0]), microsecond=(int(s[1]) * 1000))
	        
        	self.time = t
        	db.Model.put(self)
        
	
	def __unicode__(self):
		return 'p:%s. , n:%s , c:%s , t:%s' % (self.place, self.lastName, self.countryCode, self.finalTime)

	@permalink
	def get_absolute_url(self):
		return ('results.views.show_result', (), {'key': self.key()})

