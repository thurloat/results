# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
from myapp.forms import UserRegistrationForm
from django.contrib import admin
from norex.generic import UA_direct

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

urlpatterns = auth_patterns + patterns('norex.generic',
    (r'^$',             'UA_direct', {'template': 'homepage.html'}),
    (r'^help/',         'UA_direct', {'template': 'help.html'}),
)   + patterns('',
    
    ('^admin/(.*)',     admin.site.root),
    (r'^simple/$',         'results.views.simple'),
    # Override the default registration form
    url(r'^account/register/$', 'registration.views.register',
        kwargs={'form_class': UserRegistrationForm},
        name='registration_register'),
) + urlpatterns