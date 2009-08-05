from django.db.models import permalink, signals
from google.appengine.ext import db
from ragendja.dbutils import cleanup_relations

class _ICHImages(object):
    def get_image_for_property(cls):
        pass

class Image(db.Model):
        
    @classmethod
    def image_find_gql(cls,model, id):
        print cls
        q = db.GqlQuery("SELECT * FROM  WHERE __key__ = 'agdjYW5vZTA5chILEgxldmVudHNfZXZlbnQYAQw'").fetch(1)
        return q  