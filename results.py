#!/usr/bin/env python
# encoding: utf-8
"""
results.py

Created by Adam on 2009-06-15.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
import simplejson
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

class Race(db.Model):
	raceNumber = db.StringProperty()
	roundNumber = db.StringProperty()
	heatNumber = db.StringProperty()
	description = db.StringProperty()
	windSpeed = db.StringProperty()
	weather = db.StringProperty()
	
	def __json__(self):
		return self.description
	

class RaceForm(djangoforms.ModelForm):
	class Meta:
		model = Race

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
	race = db.ReferenceProperty(Race)

class ResultsForm(djangoforms.ModelForm):
	class Meta:
		model = Results

class JSONner(simplejson.JSONEncoder):
	def default(self, obj):
		if hasattr(obj,'__json__'):
			func = getattr(obj,'__json__')
			return func()
		return simplejson.JSONEncoder.default(self,obj)