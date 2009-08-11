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
from bios.models import Athlete, Country, Crew


class Event(db.Model):
	
	eventClass = db.StringProperty(choices=("C1","C2","C3","C4","K1","K2","K3","K4","Men","Women",))
	distance = db.StringProperty(choices=("1000","500","200","Relay",))
	gender = db.StringProperty(choices=("Men","Women","LTATA","LTA","TAA",))
	eventString = db.StringProperty()
	
	def __unicode__(self): return '%s - %s - %s' % (self.eventClass,self.distance,self.gender)

	
class Race(db.Model):
	event = db.ReferenceProperty(Event)
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
	place = db.StringProperty()
	athlete = db.ReferenceProperty(Athlete, collection_name="result_athlete")
	crew = db.ReferenceProperty(Crew, collection_name="result_crew")
	laneNumber = db.StringProperty()
	country = db.ReferenceProperty(Country, collection_name="result_country")
	finalTime = db.StringProperty()
	deltaTime = db.StringProperty()
	splitDetails = db.StringProperty()
	time = db.TimeProperty()
	race = db.ReferenceProperty(Race, collection_name="results_race")
	
	def put(self):
		db.Model.put(self)
		"""	
		if self.finalTime is not None:
			from datetime import time
			sstr = self.finalTime.split(":")
	        if len(sstr) == 1:
	            s = sstr[0].split(".")
	            t = time(second=int(s[0]), microsecond=(int(s[1]) * 1000))
	            pass
	        elif len(sstr) == 2:
	            s = sstr[1].split(".")
	            t = time(minute=int(str[0]), second=int(s[0]), microsecond=(int(s[1]) * 1000))
	        elif len(sstr) == 3:
	            s = sstr[2].split(".")
	            t = time(hour=int(str[0]), minute=int(str[1]), second=int(s[0]), microsecond=(int(s[1]) * 1000))
	        
        	self.time = t
        	db.Model.put(self)
        """
	
	def __unicode__(self):
		return 'Lane:%s, Athlete%s,%s , t:%s' % (self.laneNumber, self.athlete.lastName if self.athlete is not None else "", self.country.code if self.country is not None else "", self.finalTime)

	@permalink
	def get_absolute_url(self):
		return ('results.views.show_result', (), {'key': self.key()})

