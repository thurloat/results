#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Adam on 2009-06-24.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, delete_object, \
    update_object
from google.appengine.ext import db
from mimetypes import guess_type
from ragendja.dbutils import get_object_or_404
from ragendja.template import render_to_response

from results.models import Race, Results

def show_races(request):
	return object_list(request,Race.all())
def show_race(request, key):
	return object_list(request,Race.all(),key)
def show_result(request, key):
	return object_detail(request,Results.all(),key)
def show_results(request, key):
	race = Race.get(key)
	return object_list(request,Results.gql("WHERE race = :1", race))
    
def upload(request):
    if request.method == 'POST':
        file_contents = request.FILES['lif'].read().strip()

        #file_contents = self.request.get('lif').strip()
        import csv
        imported = []
        importReader = csv.reader(file_contents.split('\n'))
        for row in importReader:
            imported += [row]
        existing = Race.all()
        #db.delete(existing)
        existing.filter("raceNumber =", imported[0][0])
        if existing.count(1) > 0:
            pass
        else:
            #validate data structure
            if len(imported[0]) >= 6:
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
                for r in imported:
                    if len(r[0]) > 0:
                        race = Race(raceNumber = r[0],
                                    roundNumber = r[1],
                                    heatNumber = r[2],
                                    description = r[3])
                        race.put()
            else:
                print("Race Data Structure Not Acceptable.")
                self.error(500)
        return render_to_response(request, 'results/upload.html');
    else:
        return render_to_response(request, 'results/upload.html');