#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Adam on 2009-07-02.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from django.db.models import permalink, signals
from google.appengine.ext import db
from ragendja.dbutils import cleanup_relations

class Country(db.Model):
	countryNumber = db.StringProperty()
	code = db.StringProperty()
	name = db.StringProperty()
	
	def __unicode__(self):
		return self.code
	
	@permalink
	def get_absolute_url(self):
		return ('bios.views.show_country', (), {'key': self.key})

class Team(db.Model):
	teamNumber = db.StringProperty()
	country = db.ReferenceProperty(Country)
	name = db.StringProperty()
	
	def __unicode__(self):
		return '%s. %s - %s' % (self.teamNumber, self.name, self.country)
			
	@permalink
	def get_absolute_url(self):
		return ('bios.views.show_team', (), {'key': self.key()})



class Athlete(db.Model):
	athleteNumber = db.StringProperty()
	firstName = db.StringProperty()
	lastName = db.StringProperty()
	team = db.ReferenceProperty(Team)
	country = db.ReferenceProperty(Country)
	
	def __unicode__(self):
		return '%s. %s %s, %s' % (self.athleteNumber, self.firstName, self.lastName, self.country)
	
	def __json__(self):
		return '%s %s' % (self.lastName, self.firstName)
	
	@permalink
	def get_absolute_url(self):
		return ('bios.views.show_athlete', (), {'key': self.key()})

