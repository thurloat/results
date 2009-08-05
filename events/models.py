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
from gaepimage.gaep import ImageProperty

class Event(db.Model):
	eventNumber = db.IntegerProperty()
	location = db.StringProperty()
	title = db.StringProperty()
	image = db.BlobProperty()
	price = db.StringProperty()
	description = db.TextProperty()
	date = db.DateProperty()
	time = db.TimeProperty()
	
	def __unicode__(self):
		return self.description
	
	@permalink
	def get_absolute_url(self):
		return ('events.views.show_event', (), {'key': self.key})