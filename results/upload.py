#!/usr/bin/env python
# encoding: utf-8
"""
upload.py

Created by Adam on 2009-06-17.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from google.appengine.ext import webapp
from results import *

class UploadHandler(webapp.RequestHandler):
	def __init__(self):
		pass
	def get(self):
		self.response.out.write("""
		<html>
			<body>
				<form method="POST" enctype="multipart/form-data" action="/upload">
					<h1> .lif uploader. </h1>
					<input type="file" name="lif" />
					<input type="submit" />
				</form>
			</body>
		</html>
		""")
	def post(self):
		file_contents = self.request.get('lif').strip()
		import csv
		imported = []
		importReader = csv.reader(file_contents.split('\n'))
		for row in importReader:
			imported += [row]
		print "a"
		print imported[1]
		print "b"
		existing = Race.all()
		existing.filter("raceNumber =", imported[0][0])
		if existing.count(1) > 0:
			print "Record Already Exists, Updating Race Info Instead of Inserting"
		else:
			#validate data structure
			print "sdfsdf"
			print len(imported[0])
			if len(imported[0]) == 6:
				#insert new records
				race = Race(raceNumber = imported[0][0],
						roundNumber = imported[0][1],
						heatNumber = imported[0][2],
						description = imported[0][3],
						windSpeed = imported[0][4],
						weather = imported[0][5])
				race.put()
				#remove the race from the list
				imported.pop(0)
				#loop through the rest of the records and insert them as results.
				for r in imported:
					result = Results(place=r[0],
									athleteNumber=r[1],
									laneNumber=r[2],
									lastName=r[3],
									firstName=r[4],
									countryCode=r[5],
									finalTime=r[6],
									deltaTime=r[8],
									splitDetails=r[10],
									race=race)
					result.put()
				print("Race %s imported." % race.description)
			elif len(imported[0]) == 5:
				pass
			else:
				print len(imported[0])
			
			#import the rest of the results.
	
