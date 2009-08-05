from django.conf.urls.defaults import *

rootpatterns = patterns('',
    (r'^gaepimage/', include('gaepimage.urls')),
)
