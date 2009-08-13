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
#from results.models import Event

class Country(db.Model):
	countryNumber = db.IntegerProperty()
	code = db.StringProperty()
	name = db.StringProperty()
	flag = db.BlobProperty()
	
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
	bibNum = db.IntegerProperty()
	firstName = db.StringProperty()
	lastName = db.StringProperty()
	birthDate = db.StringProperty()
	homeTown = db.StringProperty()
	coach = db.StringProperty()
	picture = db.BlobProperty()
	country = db.ReferenceProperty(Country, collection_name = "athlete_country")
	gender = db.StringProperty(choices=('Male','Female'))
	accred = db.StringProperty()
	bio = db.TextProperty()
		
	def __unicode__(self):
		return '%s. %s %s, %s' % (self.bibNum, self.firstName, self.lastName, self.country)
	
	def __json__(self):
		return '%s %s' % (self.lastName, self.firstName)
	
	@permalink
	def get_absolute_url(self):
		return ('bios.views.show_athlete', (), {'key': self.key()})
	
	def get_crews(self):
		return Crew.gql('WHERE athletes = :ai', ai = self.key()).fetch(5)

class Crew(db.Model):
	#from results.models import Event as rEvent
	crewNum = db.IntegerProperty()
	athletes = ReferenceListProperty(Athlete, collection_name ="crew_athlete")
	crewString = db.StringProperty()
	
	def prefetch_athlete_data(self):
		print self.athletes
		athletes = [db.get(k) for k in self.athletes]
		print athletes
		self.athletes = athletes
		print self.athletes
	
	def __unicode__(self):
		return '%s, %s. %s' % (self.crewNum, self.athletes, self.crewString)
	
	
	
########################################################
#Teams Are Now Crews
########################################################

