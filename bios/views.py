#!/usr/bin/env python
# encoding: utf-8
"""
views.py

Created by Adam on 2009-07-02.
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
from ragendja.dbutils import get_object_or_404, prefetch_references
from ragendja.template import render_to_response
from google.appengine.api import memcache


from norex.generic import UA_object_list, UA_object_detail, UA_direct
from bios.models import Crew, Country, Athlete
from results.models import Event

def show_bios_overview_mobile(request):
    #memcache.delete("biosHtml")
    data = memcache.get('biosHtml')
    if data is not None:
        return data
    countryList = Country.all().order("name")
    data = UA_object_list(request,Event.all(), template_name="mobile-bioOverview.html", extra_context={'countries':countryList})
    memcache.add("biosHtml", data)
    return data

def show_athletes_all_country(request, country):
    countryQ = Country.gql("WHERE code = :cc", cc=country)
    selectedCountry = countryQ.get()
    data = UA_object_list(request,Athlete.all().filter("country =",selectedCountry), template_name="mobile-bioAthleteList.html", extra_context={'country':selectedCountry})
    return data

def show_athletes_country_crew(request, country, crewNum):
    selectedCountry = Country.gql("WHERE code = :cc", cc=country).get()
    return UA_object_detail(request,Crew.all(),slug_field="crewNum",slug=long(crewNum), template_name="mobile-bioCrew.html", template_object_name = "crew", extra_context={'country':selectedCountry})

def show_athlete(request, identifier):
    athlete = Athlete.all().filter("bibNum =",int(identifier)).get()
    crews = athlete.get_crews()
    return UA_object_detail(request,Athlete.all(),slug_field="bibNum",slug=long(identifier), template_name="mobile-bioAthleteDetail.html", template_object_name = "athlete", extra_context={'crews':crews})

def show_athletes(request):
	return UA_object_list(request,Athlete.all(),paginate_by = 10)

def show_crews(request):
	return UA_object_list(request,Crew.all())
    
def show_crew(request, key):
	crew = Crew.get(key)
	return UA_object_list(request,Athlete.gql("WHERE crew = :1", crew))
    
def image_view(request, id):
    athlete = Athlete.all().filter("bibNum =",int(id)).get()
    print ""
    print athlete.picture
    if athlete and athlete.picture: 
        response = HttpResponse()
        response['Content-Type'] = 'image/png'
        response.write(athlete.picture)
        return response
    else:
        raise Http404('Sorry, I couldnt find that image!')
    
def bio_upload(request):
    if request.method == 'POST':
        import re
        import os
        file = request.FILES['bios']
        uploadfile=file.name; 
        
        file_contents = request.FILES['bios'].read().strip()

        #file_contents = self.request.get('lif').strip()
        import csv
        imported = []
        importReader = csv.reader(file_contents.split('\n'))
        for row in importReader:
            imported += [row]
        #validate data structure
        
        ci = 0
        selectedCountry = None
        for r in imported:
            if len(r) is 2:
                name = [x.strip() for x in r[1].split('-')]
                #print name
                country = Country(name = name[0], code = name[1], countryNumber = ci)
                ci = ci + 1
                country.put()
                selectedCountry = country
            else:
                #print r
                athlete = Athlete()
                athlete.bibNum=int(r[0]) if r[0] is not '' else int(81)
                athlete.firstName=r[1]
                athlete.lastName=r[3]
                athlete.gender="Male" if r[4] is "M" else "Female"
                athlete.country = selectedCountry
                athlete.put()
                
    return UA_direct(request, 'bios/upload.html');
