#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by Adam on 2009-07-02.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from django.db.models import permalink, signals
from google.appengine.ext import db
from ragendja.dbutils import cleanup_relations, KeyListProperty
from google.appengine.api import memcache
from norex.properties import ReferenceListProperty
from results.models import Event

class Country(db.Model):
	countryNumber = db.IntegerProperty()
	code = db.StringProperty()
	name = db.StringProperty()
	
	def __unicode__(self):
		return self.code
	
	@permalink
	def get_absolute_url(self):
		return ('bios.views.show_country', (), {'key': self.key})
	
	def put(self):
		memcache.delete("biosHtml")
		return super(Country,self).put()
	def delete(self):
		memcache.delete("biosHtml")
		return super(Country,self).delete()

class Athlete(db.Model):
	athleteNumber = db.IntegerProperty()
	firstName = db.StringProperty()
	lastName = db.StringProperty()
	birthDate = db.DateProperty()
	homeTown = db.StringProperty()
	coach = db.StringProperty()
	picture = db.BlobProperty()
	events = KeyListProperty(Event)
	country = db.ReferenceProperty(Country)
		
	def __unicode__(self):
		return '%s. %s %s, %s' % (self.athleteNumber, self.firstName, self.lastName, self.country)
	
	def __json__(self):
		return '%s %s' % (self.lastName, self.firstName)
	
	@permalink
	def get_absolute_url(self):
		return ('bios.views.show_athlete', (), {'key': self.key()})

########################################################
#Teams Are Deprecated
########################################################
"""
class Team(db.Model):
	teamNumber = db.IntegerProperty()
	country = db.ReferenceProperty(Country, required=True)
	event = db.ReferenceProperty(Event)
	members = KeyListProperty(Athlete)
	name = db.StringProperty()
	
	def __unicode__(self):
		return '%s. %s - %s' % (self.teamNumber, self.name, self.country)
			
	@permalink
	def get_absolute_url(self):
		return ('bios.views.show_team', (), {'key': self.key()})
	
	def put(self):
		memcache.delete("biosHtml")
		return super(Team,self).put()
	def delete(self):
		memcache.delete("biosHtml")
		return super(Team,self).delete()
	
class TeamMember(db.Model):
	team = db.ReferenceProperty(Team)
	athlete = db.ReferenceProperty(Athlete)
"""
