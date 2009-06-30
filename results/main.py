#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.dist import use_library
use_library('django','1.0')

__author__ = 'Adam Thurlow, Norex'

import os, logging, datetime, re, csv
from results import *

import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from upload import UploadHandler



class MainHandler(webapp.RequestHandler):
  def get(self):
	template_values={}
	path = os.path.join(os.path.dirname(__file__), 'home.html')
	self.response.out.write(template.render(path, template_values))

class RPCHandler(webapp.RequestHandler):
	def __init__(self):
		webapp.RequestHandler.__init__(self)
		self.methods = RPCMethods()#keep callable methods in here, more secure.
	
	def get(self):
		#Process the url
		func = None
		action = self.request.get('action')
		if action:
			if action[0] == '_':
				#no private access for YOU!
				self.error(403)
				return
			if re.match("^put*",action[0]):
				self.error(403)
			else:
				#setting the valid RPC function call
				func = getattr(self.methods, action)
		if not func:
			#woops, no function with that name, sarry.
			self.error(404)
			return
		
		#build up the args list.
		args = []
		arg_counter = 0
		while True:
			arg = self.request.get('arg' + str(arg_counter))
			arg_counter +=1
			if arg:
				args += [arg]
			else:
				break
		#fetch the data to be JSON'd back to the browser.
		if args:
			result = func(*args)
		else:
			result = func()
		#dump the data!
		resultWrapper = {'result':result}
		self.response.out.write(JSONner().encode(resultWrapper))
	
	def post(self):
		"""
			Then pass the post to the correct put function
		"""
		#check RPC Key
		if self.request.get('rpckey') == 'abc':
			action = self.request.get('func')
			try:
				func = getattr(self.methods, action)
			except:
				print 'Error Code 0010'
				self.error(500)
			else:
				result = func()
				if result == False:
					self.error(500)
		else:
			print 'Error Code 0001'
			error(500)


class RPCMethods(object):
	"""Security, don't allow remote callers to access privae functions etc from the handler.
	"""
	def getRace(self, *args):
		#TODO: search by date
		query = Race.all()
		results = query.fetch(10)
		return self.returnDict(results)
	def getResults(self, *args):
		#get results for a race
		#TODO: sorting, etc.
		raceq = Race.gql("WHERE raceNumber= :raceNumber",raceNumber=args[0])
		race = raceq.get()
		query = Results.all()
		query.filter('race =', race)
		results = query.fetch(100)
		return self.returnDict(results)
	
	def returnDict(self, results):
		#translates a db.Model into a dict object in order to serialize as JSON
		return_dict = []
		for result in results:
			if isinstance(result, db.Model):
				properties = result.properties().items()
				output = {}
				for field, value in properties:
					output[field] = getattr(result,field)
				return_dict += [output]
		return return_dict
def main():
  application = webapp.WSGIApplication([('/', MainHandler),
										('/rpc', RPCHandler),
										('/upload',UploadHandler)
										],
										debug=True)
  wsgiref.handlers.CGIHandler().run(application)

class JSONner(simplejson.JSONEncoder):
	def default(self, obj):
		if hasattr(obj,'__json__'):
			func = getattr(obj,'__json__')
			return func()
		return simplejson.JSONEncoder.default(self,obj)
if __name__ == '__main__':
  main()
