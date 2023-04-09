from django.forms import ModelForm
from .models import Events
from django import forms

class EventsForm(ModelForm):
    class Meta:
        model = Events
        fields = '__all__'
     

class EventAboutForm(ModelForm):

  class Meta:

    model = Events

   

    fields = '__all__'

    # exclude = ['posted_by','likes','view_count','published']

   

    widgets = {

      'about' : forms.Textarea(attrs={'width': 'auto;', 'height': '100%;' , 'float': 'left;', 'border': '1px solid #e5e7f2;', 'background': '#F5F7FB;',

                            'border-radius': '4px;', 'color': '#7d93b2;', 'font-size': '12px;', '-webkit-appearance': 'none;',

                            'outline': 'none;', 'overflow': 'hidden;', 'z-index': '1;', 'font-weight': '400;'}),

    }