from google.appengine.ext import db
from google.appengine.ext.db import DuplicatePropertyError
from django.utils.translation import ugettext_lazy as _
import pickle


################################################################
# Model Mix-ins
################################################################
# TODO (Wolfe):  _Auditable and _SaveHistory are NOT independent.
#    Restructure so you can include or the other or both.

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.db import djangoforms
from utils import *
import copy
from django import forms

last_model_saved = None
class _AssignKeyName(object):
  def __init__(self, *args, **kwds):
    if ('key_name' not in kwds) or (kwds['key_name'] is None):
      kwds['key_name'] = unique_key_name()
    super(_AssignKeyName, self).__init__(*args, **kwds)
  def put(self):
    global last_model_saved
    result = super(_AssignKeyName, self).put()
    if result: last_model_saved = self
  def __unicode__(self):
    return "PLEASE OVERRIDE __unicode__ METHOD"

class _Auditable(object):
  """ Every save, edit, or delete to an _Auditable model records an entry in model Audit """
  def info(self): return "None"
  def before_save_hook(self): pass
  @classmethod
  def get(cls, keys):
    if keys == 'None': keys = {}
    return super(_Auditable, cls).get(keys)
  @classmethod
  def form(cls, instance = None, data = None): return cls.Form(instance=instance, data=data)
  def put(self):
    self.log('put')
    self.search_string = str(self).upper()
    self.before_save_hook()
    return super(_Auditable, self).put()
  def delete(self):
    self.log('delete')
    return super(_Auditable,self).delete()
  def log(self, op):
    audit = Audit(
      user = users.get_current_user(),
      action = op,
      xml = self.to_xml())
    audit.put()
  def editable(self):
    return True
  def deletable(self):
    """Return true if this item has no ReferenceProperty or ReferenceListProperty links to it.
    (Currently tested by doing a fetch on all its Query properties.)
    """
    return not any ( [getattr(self,x).fetch(1) for x in dir(self) if isinstance(getattr(self,x), db.Query)] )
  @classmethod   # TODO: Not logically part of _Auditable. Rename _Auditable?
  def filter_prefix(cls, property_name, prefix):
    query = cls.all()
    query.filter("%s >= " % property_name, u"%s" % prefix)
    query.filter("%s < " % property_name, u"%s\xEF\xBF\xBD" % prefix)
    return query

class _SaveHistory(object):
  # These are defined in PictouModel to centralize the stuff that depends on inheritance from db.Model.  See TODO.
  # _active = db.BooleanProperty()
  # _timestamp = db.DateTimeProperty()
  # _current = db.SelfReferenceProperty()
  # search_string = db.StringProperty()
  
  """ One every edit and delete, this add-on saves previous states of
  the Model along with a timestamp.  The previous versions are saved
  as inactive records in the same table as the Model inself. """ 
  @classmethod
  def all(self):
    """New All!
    @summary:
        Doesn't really show all, since all is so commonly used, we don't want to show
        our "deleted" rows, only our active rows.
    @attention: 
        To really return ALL, including "deleted" records, use real_all()
    """
    return super(_SaveHistory,self).all().filter('_active =',True)
  @classmethod
  def real_all(self):
    return super(_SaveHistory,self).all()
  @classmethod
  def form(cls, instance = None, data = None):
    class ThisForm(Form):
      class Meta:
        model = cls
    return ThisForm(instance=instance, data=data)
  # _current = db.ReferenceProperty()
  def real_delete(self):
    return super(_SaveHistory, self).delete()

  def delete(self):
    """Maintain history
    @summary
      Disable rather than delete old items
    """
    self._active = False
    self._timestamp = dt.datetime.now()
    super(_SaveHistory,self).put()
  def put(self):
    """Maintain history
    
    @summary:
      Save a copy of the previous record on every put().
  
    @warning: 
     Alternative which uses the API is to property-copy as in appengine.ext.db.__init__.py, Model class init.
    """ 
    if self._entity is not None:
      oldme = db.get(self.key())
      oldme._entity = None
      oldme._key_name = None
      oldme._active = False
      oldme._current = self.key()
      oldme._timestamp = dt.datetime.now()
      super(_SaveHistory,oldme).put()
    self._timestamp = dt.datetime.now()
    self._active = True
    return super(_SaveHistory,self).put() 

from authorization.models import ModelWithPermissions
class PictouModel(db.Model):
  _active = db.BooleanProperty()
  _timestamp = db.DateTimeProperty()
  _current = db.SelfReferenceProperty()
  search_string = db.StringProperty()

  def info(self): return ""

class Expando(PictouModel, ModelWithPermissions, _SaveHistory, _Auditable, _AssignKeyName, db.Expando): pass
class PolyModel(PictouModel, ModelWithPermissions, _SaveHistory, _Auditable, _AssignKeyName, db.Model): pass
class Model(PictouModel, ModelWithPermissions, _SaveHistory, _Auditable, _AssignKeyName, db.Model): pass

class MergeMetaMetaclass(djangoforms.ModelFormMetaclass):
  def __new__(cls, class_name, bases, attrs):
    Meta = attrs.get('Meta', type('Meta', (), {}))
    if (not hasattr(Meta, 'exclude')): Meta.exclude = []
    Meta.exclude.extend(['search_string','_active','_timestamp','_current'])
    return super(MergeMetaMetaclass, cls).__new__(cls, class_name, bases, attrs)

from authorization.models import has_property_permission
class Form(djangoforms.ModelForm):
  def __init__(self, *args, **kwds):
    super(Form, self).__init__(*args, **kwds)
    instance = getattr(self, 'instance', None)
    model = self._meta.model.__name__
    for name in self.fields:
      if not has_property_permission (model, name, 'view'):
        del self.fields['name']
        continue
      if instance and not has_property_permission ('Policy', name, 'edit'):
        self.fields[name] = read_only_version_of(self.fields[name])
      if not instance and not has_property_permission ('Policy', name, 'create'):
        del self.fields[name]

  __metaclass__ = MergeMetaMetaclass
  class Meta:
    exclude = ['search_string','_active','_timestamp','_current']

class Audit(db.Expando):
  user = db.UserProperty()
  action = db.StringProperty()
  timestamp = db.DateTimeProperty(None,True)
  xml = db.TextProperty()
  @classmethod
  def display(cls):
    return cls.all().order('-timestamp').fetch(10)
  def __unicode__(self):
    return "%s: %s %s %s..." % (self.user, self.action, self.timestamp.strftime("%x %X"), self.xml[0:60])
  # audit_contents = db.ReferenceProperty(db.Model)

################################################################
# Widgets and Fields
################################################################

from django.forms.util import flatatt, smart_unicode
from itertools import chain
from django.forms.widgets import CheckboxInput
from django.utils.html import escape
from django.forms.util import flatatt, smart_unicode


class SelectMultiple(forms.SelectMultiple):
  def value_from_datadict (self, data, file, name): return data.getlist(name)

class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
  """This version pre-processes the value list to convert model instances to keys"""
  @classmethod
  def value_from_datadict (self, data, file, name):
    return data.getlist(name)
  def render (self, name, value, attrs=None, choices=()):
    if value is None: value = []
    value = [isinstance (v, Model) and v.key() or v for v in value]
    return super(CheckboxSelectMultiple, self).render(name, value, attrs, choices)

class ReadOnlyTextField(forms.Field):
  def __init__(self):
    super(ReadOnlyTextField,self).__init__(widget=ReadOnlyTextWidget())
  def clean(self, value):
    return self.initial
class ReadOnlyTextWidget(forms.Widget):
  def render(self, name, value, attrs=None):
    self.value = value
    if value is None: value = ''
    value = smart_unicode(value)
    final_attrs = self.build_attrs(attrs, name=name)
    return u'<b%s>%s</b>' % (flatatt(final_attrs), escape(value))

def read_only_version_of (field):
  return field if isinstance(field, ReadOnlyVersionOf) else ReadOnlyVersionOf(field)

class ReadOnlyVersionOf(forms.Field):
  def __init__(self, old_field):
    class Widget(forms.Widget):
      def render(self, name, value, attrs=None):
        self.value = value
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return u'<span%s><strong>%s</strong></span>' % (flatatt(final_attrs), smart_unicode(old_field.clean(value)))
    return super(ReadOnlyVersionOf,self).__init__(widget=Widget())
  def clean(self, value):
    return self.initial


integer_list_re = re.compile(r"^[0-9]+$")
class IntegerListField(forms.CharField):
  def __init__(self, max_length=None, min_length=None, *args, **kwargs):
    kwargs['widget'] = kwargs.get('widget', IntegerListTextarea(attrs={'cols': 10}))
    super(IntegerListField, self).__init__(integer_list_re, max_length, min_length, *args, **kwargs)
  default_error_messages = {
    'invalid': _(u'Enter a list of integers separated by commas, newlines, or whitespace.'),
    }
  def clean(self, value):
    return [int(i) for i in re.sub('\D+', " ", value).strip().split()]

class IntegerListTextarea(forms.Textarea):
  def render(self, name, value, attrs=None):
    if value is not None:
      value = "\n".join([str(i) for i in value])
    return super(IntegerListTextarea, self).render(name, value, attrs)

class IntegerListInput(forms.TextInput):
  def render(self, name, value, attrs=None):
    if value is not None:
      value = ", ".join([str(i) for i in value])
    return super(IntegerListInput, self).render(name, value, attrs)
