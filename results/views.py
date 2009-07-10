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
from google.appengine.api import memcache

messages = []

from results.models import Race, Results

def show_races(request):
    return object_list(request,Race.all().order("raceNumber"))

def ajax(request):
    data = memcache.get('raceshtml');
    if data is not None:
        return data
    
    data = object_list(request,Race.all().order("raceNumber"), template_name="list.html")
    memcache.add("raceshtml", data)
    return data
    
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

def getrace(field):
    existing = Race.all()
    existing.filter("raceNumber =", int(field[0]))
    if existing.count(1) > 0:
        race = existing.get()
        messages.append("Updating race #" + field[0] + ": " + field[3])
    else:
        race = Race(raceNumber = int(field[0]))
        messages.append("Creating NEW race #" + field[0] + ": " + field[3])
    
    race.roundNumber = field[1]
    race.heatNumber = field[2]
    
    if len(field[3]) == 0 or field[3] == "":
        race.description = "Event # " + field[0]
    else:
        race.description = field[3]
        
    if len(field) >= 5:
        race.windSpeed = field[4]
    
    if len(field) >= 6:
        race.weather = field[5]
    
    return race

def getresult(field, race):
    existingresult = race.results_set.filter("place = ", int(field[0]))
    if existingresult.count(1) > 0:
        result = existingresult.get()
        messages.append("Updating result:" + field[0] + " place")
    else:
        result = Results(place=int(field[0]), race=race)
        messages.append("Creating NEW race result: " + field[4] + " " + field[3] + " came " +  field[0])
        
    if len(field[1]) > 0:
        result.athleteNumber = field[1]
    result.laneNumber = field[2]
    result.lastName = field[3]
    result.firstName = field[4]
    result.countryCode = field[5]
    result.finalTime = field[6]
    result.deltaTime = field[8]
    result.splitDetails = field[10]

    return result

def upload(request):
    if request.method == 'POST':
        import re
        import os
        file = request.FILES['lif']
        uploadfile=file.name; 
        evt=".evt"
        lif=".lif"
        reneedle=re.compile(evt, re.IGNORECASE)
        reneedlelif=re.compile(lif)
        
        file_contents = request.FILES['lif'].read().strip()

        #file_contents = self.request.get('lif').strip()
        import csv
        imported = []
        importReader = csv.reader(file_contents.split('\n'))
        for row in importReader:
            imported += [row]
        existing = Race.all()
        existing.filter("raceNumber =", int(imported[0][0]))
            #validate data structure
        if lif in uploadfile:
            race = getrace(imported[0])
            race.hasResults = True
            race.put()
            #remove the race from the list
            imported.pop(0)
            #loop through the rest of the records and insert them as results.
            for r in imported:
                if len(r[0]) > 0:
                    result = getresult(r, race)
                    result.put()
                
        elif evt in uploadfile:
                for r in imported:
                    if len(r[0]) > 0:
                        race = getrace(r)
                        race.put()
                messages.append("Everything seems to have worked!")
        else:
            messages.append("Race Data Structure Not Acceptable.")
        memcache.delete("raceshtml")
    return render_to_response(request, 'results/upload.html', {'messages':messages});