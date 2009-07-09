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
	return object_list(request,Race.all().order("raceNumber"))
def show_race(request, key):
	return object_list(request,Race.all(),key)
def show_result(request, key):
	return object_detail(request,Results.all(),key)
def show_results(request, key):
    race = Race.get(key)
    return object_list(request,queryset=Results.all().filter("race =", race).order("place"), extra_context={'race':race})
    
def cleardata(request):
    messages = []
    if request.method == 'POST':
        existing = Race.all()
        db.delete(existing)
        messages.append("All races deleted")
        results = Results.all()
        db.delete(results)
        messages.append("All results deleted")
    return render_to_response(request, 'results/delete.html', {'messages':messages});

def upload(request):
    messages = []
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
        existing.filter("raceNumber =", int(imported[0][0]))
            #validate data structure
        if len(imported[0]) >= 6:
            #insert new records
            if existing.count(1) > 0:
                race = existing.get()
                if race.description != imported[0][3]:
                    messages.append("Updating race #" + imported[0][0] + ": " + imported[0][3])
                    
                race.description = imported[0][3]
                
            else:
                race = Race(raceNumber = int(imported[0][0]),
                    roundNumber = imported[0][1],
                    heatNumber = imported[0][2],
                    description = imported[0][3],
                    windSpeed = imported[0][4],
                    weather = imported[0][5])
                messages.append("Creating NEW race #" + imported[0][0] + ": " + imported[0][3])
                
            race.put()
            #remove the race from the list
            imported.pop(0)
            #loop through the rest of the records and insert them as results.
            for r in imported:
                existingresult = race.results_set.filter("place = ", int(r[0]))
                if existingresult.count(1) > 0:
                    result = existingresult.get()
                    if result.athleteNumber != r[1]:
                        result.athleteNumber=r[1]
                        result.laneNumber=r[2]
                        result.lastName=r[3]
                        result.firstName=r[4]
                        result.countryCode=r[5]
                        result.finalTime=r[6]
                        result.deltaTime=r[8]
                        result.splitDetails=r[10]
                        messages.append("Updating result:" + r[0] + " place")
                else:
                    result = Results(place=int(r[0]),
                                    athleteNumber=r[1],
                                    laneNumber=r[2],
                                    lastName=r[3],
                                    firstName=r[4],
                                    countryCode=r[5],
                                    finalTime=r[6],
                                    deltaTime=r[8],
                                    splitDetails=r[10],
                                    race=race)
                    messages.append("Creating NEW race result: " + r[4] + " " + r[3] + " came " +  r[0])
                result.put()
                
        elif len(imported[0]) == 5:
                for r in imported:
                    if len(r[0]) > 0:
                        existingrace = Race.all()
                        existingrace.filter("raceNumber =", int(r[0]))
                        if existingrace.count(1) > 0:
                            race = existingrace.get()
                            if race.description != r[3]:
                                messages.append("Updating race #" + r[0] + ": " + r[3])
                            race.description = r[3]
                            race.roundNumber = r[1]
                            race.heatNumber = r[2]
                        else:
                            race = Race(raceNumber = int(r[0]),
                                        roundNumber = r[1],
                                        heatNumber = r[2],
                                        description = r[3])
                            messages.append("Creating NEW race #" + r[0] + ": " + r[3])
                        race.put()
                messages.append("Everything seems to have worked!")
        else:
            messages.append("Race Data Structure Not Acceptable.")
    return render_to_response(request, 'results/upload.html', {'messages':messages});