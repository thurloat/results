# -*- coding: utf-8 -*-

# class DollarProperty(db.IntegerProperty):
# class DollarField(forms.fields.IntegerField):
# class RateProperty(db.FloatProperty): pass

# class ListProperty(db.ListProperty):
# class IntegerListProperty(ListProperty):
# class DollarListProperty(IntegerListProperty):

# class SerialProperty(db.Property):
# class CsvProperty(SerialProperty):
# class EnumProperty(db.Property):
# class JsonProperty(SerialProperty):
# class PickledProperty(SerialProperty):
# class TagListProperty(db.StringListProperty):

# class ReferenceListProperty(db.Property):


import csv, pickle
from django.utils import simplejson
from cStringIO import StringIO

from google.appengine.ext.db.djangoforms import monkey_patch
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from django import forms
from google.appengine.ext.db import _ReverseReferenceProperty
import re

def clean_dollar_value(x):
  """This rounds up floats to integer dollar ammounts; but 1.0000001
  should round to 1 since 4*.25 could yield 1.000000001 Also handles
  anything castable to a string such as '$35.25'."""
  if isinstance(x, int) or isinstance (x, long):
    return long(x)
  elif isinstance (x, float):
    return long (x+.9999) if x >= 0 else long (x-.9999)
  else:
    return clean_dollar_value(float(re.sub(',|\$', "", str(x).strip())))

class DollarProperty(db.IntegerProperty):
  """Dollar ammounts are rounded up to nearest integer"""
  def get_form_field(self, form_class=forms.CharField, **kwargs):
    return super(DollarProperty, self).get_form_field(form_class=DollarField, **kwargs)

  def get_value_for_form(self, instance):
    value = getattr(instance, self.name)
    return '$' + str(value) if not value is None else 0

  def make_value_from_form(self, value):
    return clean_dollar_value(value)

class DollarField(forms.fields.IntegerField):
  def clean(self, value):
    return value if value is None else clean_dollar_value(value)

################

class RateProperty(db.FloatProperty): pass


################################################################
# IntegerListProperty and DollarListProperty
################################################################
# class PropertiedClass(db.PropertiedClass):
#   def _require_parameter(self, kwds, parameter, value):
#     pass

# class ListProperty(db.ListProperty):
#   __metaclass__ = PropertiedClass

class ListProperty(db.ListProperty):
  __metaclass__ = monkey_patch
  def __init__(self, item_type, verbose_name=None, default=None, **kwds):
    """Construct ListProperty.

    Args:
      item_type: Type for the list items; must be one of the allowed property
        types.
      verbose_name: Optional verbose name.
      default: Optional default value; if omitted, an empty list is used.
      **kwds: Optional additional keyword arguments, passed to base class.

    Note that the only permissible value for 'required' is True.
    """
    if item_type is str:
      item_type = basestring
    if not isinstance(item_type, type):
      raise TypeError('Item type should be a type object')
    if item_type not in db._ALLOWED_PROPERTY_TYPES:
      raise ValueError('Item type %s is not acceptable' % item_type.__name__)
    if issubclass(item_type, (db.Blob, db.Text)):
      self._require_parameter(kwds, 'indexed', False)
      kwds['indexed'] = True
    # self._require_parameter(kwds, 'required', True)
    if default is None:
      default = []
    self.item_type = item_type
    super(ListProperty, self).__init__(verbose_name,
                                       default=default,
                                       **kwds)

class IntegerListProperty(ListProperty):
  def __init__(self, verbose_name=None, default=None, **kwds):
    super(IntegerListProperty, self).__init__(int,
                                              verbose_name=verbose_name,
                                              default=default,
                                              **kwds)

  def get_form_field(self, **kwargs):
    defaults = {'widget': forms.TextInput(attrs={'size': 50}), # Textarea,
                'initial': ''}
    defaults.update(kwargs)
    return super(IntegerListProperty, self).get_form_field(**defaults)

  def get_value_for_form(self, instance):
    value = super(IntegerListProperty, self).get_value_for_form(instance)
    if not value:
      return ""
    if isinstance(value, list):
      value = ', '.join([str(v) for v in value])
    return value

  def make_value_from_form(self, value):
    if not value:
      return []
    if isinstance(value, basestring):
      return [int(i) for i in re.sub('\D+', " ", value).strip().split()]
    return value


class DollarListProperty(IntegerListProperty):
  def get_value_for_form(self, instance):
    value = super(IntegerListProperty, self).get_value_for_form(instance)
    if not value:
      return ""
    if isinstance(value, list):
      value = ', '.join(['$'+str(v) for v in value])
    return value
  

################################################################
# SERIALIZING PROPERTIES
################################################################

"""
  gaefy.db.properties
  ~~~~~~~~~~~~~~~~~~~

  Extra properties for App Engine Models.

  :copyright: 2009 by tipfy.org.
  :license: BSD, see LICENSE.txt for more details.
"""

class SerialProperty(db.Property):
  def make_value_from_form (self, value):
    return value
  def get_value_for_form(self, instance):
    return getattr(instance, self.name)
    
class CsvProperty(SerialProperty):
  """A special property that accepts a list or tuple as value, and stores the
  data in CSV format using the db.Text data_type. Each item in the list must
  be a iterable representing fields in a CSV row. The value is converted back
  to a list of tuples when read.
  """
  data_type = db.Text

  def __init__(self, csv_params={}, field_count=None, default=None, **kwargs):
    """Constructs CsvProperty.

    Args:
      csv_params: CSV formatting parameters. See:
      http://docs.python.org/library/csv.html#csv-fmt-params
      field_count: If set, enforces all items to have this number of fields.
    """
    self._require_parameter(kwargs, 'indexed', False)
    kwargs['indexed'] = True
    if default is None:
      default = []
    self.field_count = field_count
    self.csv_params = csv_params
    super(CsvProperty, self).__init__(default=default, **kwargs)

  def get_value_for_datastore(self, model_instance):
    """Converts the list to CSV."""
    value = super(CsvProperty, self).get_value_for_datastore(model_instance)

    if value is not None:
      csvfile = StringIO()
      writer = csv.writer(csvfile, **self.csv_params)
      writer.writerows(value)
      value = csvfile.getvalue().strip()
      csvfile.close()
      return db.Text(value)

  def make_value_from_datastore(self, value):
    """Converts the CSV data back to a list."""
    values = []

    if value is not None:
      reader = csv.reader(StringIO(str(value)), **self.csv_params)
      for item in reader:
        values.append(item)

    return values

  def validate(self, value):
    """Validates the property on __set__."""
    value = super(CsvProperty, self).validate(value)
    if value is not None:
      if not isinstance(value, (list, tuple)):
        raise db.BadValueError('Property %s must be a list or tuple.' %
          (self.name))

      value = self.validate_list_contents(value)

    return value

  def validate_list_contents(self, value):
    """Validates that all rows are of the correct type and have a
    required number of fields.

    Returns:
      The validated list.

    Raises:
      BadValueError if the list has items that are not list or tuple
      instances or doesn't have the required length.
    """
    for item in value:
      if not isinstance(item, (list, tuple)):
        raise db.BadValueError(
          'Items in the %s list must be a list or tuple.' %
          (self.name))

      if self.field_count and len(item) != self.field_count:
        raise db.BadValueError(
          'Items in the %s list must have a length of %d.' %
          (self.name, self.length))

    return value

  def empty(self, value):
    return value is None


class EnumProperty(db.Property):
  """Maps a list of strings to be saved as int. The property is set or get
  using the string value, but it is stored using its index in the 'choices'
  list.
  """
  data_type = int

  def __init__(self, choices=None, **kwargs):
    if not isinstance(choices, list):
      raise TypeError('Choices must be a list.')
    super(EnumProperty, self).__init__(choices=choices, **kwargs)

  def get_value_for_datastore(self, model_instance):
    value = super(EnumProperty, self).get_value_for_datastore(model_instance)
    if value is not None:
      return int(self.choices.index(value))

  def make_value_from_datastore(self, value):
    if value is not None:
      return self.choices[int(value)]

  def empty(self, value):
    return value is None


class JsonProperty(SerialProperty):
  """Stores a dictionary automatically encoding to JSON on set and decoding
  on get.
  """
  data_type = db.Text

  def __init__(self, *args, **kwds):
    self._require_parameter(kwds, 'indexed', False)
    kwds['indexed'] = True
    super(JsonProperty, self).__init__(*args, **kwds)

  def get_value_for_datastore(self, model_instance):
    """Encodes the value to JSON."""
    value = super(JsonProperty, self).get_value_for_datastore(model_instance)
    if value is not None:
      value = simplejson.dumps(value)
      return db.Text(value)

  def make_value_from_datastore(self, value):
    """Decodes the value from JSON."""
    if value is not None:
      return simplejson.loads(value)

  def validate(self, value):
    if value is not None and not isinstance(value, (dict, list, tuple)):
      raise db.BadValueError('Property %s must be a dict, list or '
        'tuple.' % self.name)

    value = super(JsonProperty, self).validate(value)
    return value


class PickledProperty(SerialProperty):
  """Stores a native Python object, pickling automatically on set and
  unpickling on get.
  """
  data_type = db.Blob

  def __init__(self, force_type=None, **kwargs):
    """Constructs CsvProperty.

    Args:
      force_type: requires the property to be of this type.
    """
    self._require_parameter(kwargs, 'indexed', False)
    kwargs['indexed'] = True
    self.force_type = force_type
    super(PickledProperty, self).__init__(**kwargs)

  def get_value_for_datastore(self, model_instance):
    value = super(PickledProperty, self).get_value_for_datastore(model_instance)
    if value is not None:
      value = pickle.dumps(value)
      return db.Blob(value)

  def make_value_from_datastore(self, value):
    if value is not None:
      return pickle.loads(value)

  def validate(self, value):
    value = super(PickledProperty, self).validate(value)
    if value is not None and self.force_type and \
      not isinstance(value, self.force_type):
        raise datastore_errors.BadValueError(
          'Property %s must be of type "%s".' % (self.name,
            self.force_type))

    return value


class TagListProperty(db.StringListProperty):
  def validate(self, value):
    if isinstance(value, unicode):
      value = value.split(',')
      value = [v.strip().lower() for v in value]
      value = [v for v in value if v]

    value = super(TagListProperty, self).validate(value)
    return value

################################################################
# ReferenceListProperty
################################################################

class ReferenceListProperty(db.Property):
  """A property that stores a list of models.
  
  This is a parameterized property; the parameter must be a valid
  Model type, and all items must conform to this type.

  Obtained from: http://groups.google.com/group/google-appengine/msg/d203cc1b93ee22d7
  """
  def __init__(self,
               reference_class = None,
               verbose_name=None,
               collection_name=None,
               default=None,
               **kwds):
    """Construct ReferenceListProperty.

    Args:
      reference_class: Type for the list items; must be a subclass of Model.
      verbose_name: Optional verbose name.
      default: Optional default value; if omitted, an empty list is used.
      **kwds: Optional additional keyword arguments, passed to base class.
    """
    if not issubclass(reference_class, db.Model):
      raise TypeError('Item type should be a subclass of Model')
    if default is None:
      default = []
    self.reference_class = reference_class
    self.collection_name = collection_name
    super(ReferenceListProperty, self).__init__(verbose_name,
                                                default=default,
                                                **kwds)
  
  def validate(self, value):
    """Validate list.

    Note that validation here is just as broken as for ListProperty.
    The values in the list are only validated if the entire list is
    swapped out. If the list is directly modified, there is no attempt
    to validate the new items.

    Returns:
      A valid value.

    Raises:
      BadValueError if property is not a list whose items are
      instances of the reference_class given to the constructor.
    """
    value = super(ReferenceListProperty, self).validate(value)
    if value is not None:
      if not isinstance(value, list):
        raise db.BadValueError('Property %s must be a list' %
                               self.name)
      for item in value:
        if not isinstance(item, self.reference_class):
          raise db.BadValueError(
            'Items in the %s list must all be %s instances' %
            (self.name, self.reference_class.__name__))
    return value

  def empty(self, value):
    """Is list property empty.

    [] is not an empty value.
 
    Returns:
      True if value is None, else False.
    """ 
    return value is None

  data_type = list
 
  def default_value(self):
    """Default value for list.
 
    Because the property supplied to 'default' is a static value,
    that value must be shallow copied to prevent all fields with
    default values from sharing the same instance.
 
    Returns:
      Copy of the default value.
    """ 
    return list(super(ReferenceListProperty, self).default_value())
 
  def get_value_for_datastore(self, model_instance):
    """A list of key values is stored.

    Prior to storage, we validate the items in the list.
    This check seems to be missing from ListProperty.

    Args:
      model_instance: Instance to fetch datastore value from.
 
    Returns:
      A list of the keys for all Models in the value list.
    """
    value = self.__get__(model_instance, model_instance.__class__)
    self.validate(value)
    if value is None:
      return None
    else:
      return [v.key() for v in value]
 
  def make_value_from_datastore(self, value):
    """Recreates the list of Models from the list of keys.
 
    Args:
      value: value retrieved from the datastore entity.

    Returns:
      None or a list of Models.
    """ 
    if value is None:
      return None
    else:
      return [db.get(v) for v in value]

# DW added this code copied from /usr/local/google_appengine/google/appengine/ext/db/__init__.py
  def __property_config__(self, model_class, property_name):
    super(ReferenceListProperty, self).__property_config__(model_class,
                                                       property_name)

    if self.collection_name is None:
      self.collection_name = '%s_listref_set' % (model_class.__name__.lower())
    if hasattr(self.reference_class, self.collection_name):
      raise DuplicatePropertyError('Class %s already has property %s'
                                   % (self.reference_class.__name__,
                                      self.collection_name))
    setattr(self.reference_class,
            self.collection_name,
            _ReverseReferenceProperty(model_class, property_name))
    

  def get_form_field(self, **kwargs):
    from django import forms
    defaults = {'form_class': forms.ModelMultipleChoiceField,
            'queryset': self.reference_class.all(),
            'required': False}
    defaults.update(kwargs)
    return super(ReferenceListProperty, self).get_form_field(**defaults)
