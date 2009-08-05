from google.appengine.ext import db
from django.http import HttpResponse

def image_find_gql(model, id):
        q = db.GqlQuery("SELECT * FROM  WHERE __key__ = 'agdjYW5vZTA5chILEgxldmVudHNfZXZlbnQYAQw'").fetch(1)
        return q  

class ImageProperty(db.Property):
    def __init__(self, the_class, the_property, verbose_name=None, default=None, **kwds):
        print ""
        print the_class
        super(ListProperty, self).__init__(verbose_name, **kwds)
    def url(self):
        return u"<img src='1' />"
    def make_value_from_datastore(self,value):
        return u"<img src='1' />"
    
class ICHImages(object):
    def __init__(self):
        pass