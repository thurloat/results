from django.conf.urls.defaults import *

urlpatterns = patterns('gaepimage.views',
    (r'^$', 'intro'),
    (r'^(?P<model>.+)/(?P<property>.+)/(?P<id>.+)/$', 'render_image'),
)