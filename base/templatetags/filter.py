from operator import index
from django import template
import datetime,time
from django.utils import formats

register = template.Library()

@register.filter(name='split')
def split(value, key):
  """
    Returns the value turned into a list.
  """
  return value.split(key)

@register.filter(name='custom_format')
def custom_date(value, arg=None):
    if value in (None, ''):
        return ''

    if isinstance(value, str):
      
        api_date_format = '%H:%M:%S.%f%z'  # 2019-08-30T08:22:32.245-0700
        value = time.strptime(value)
        print("value is *****************",value)

    try:
        return formats.date_format(value, arg)
    except AttributeError:
        try:
            return format(value, arg)
        except AttributeError:
            return ''