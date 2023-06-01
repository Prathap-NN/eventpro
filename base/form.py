from django.forms import ModelForm
from .models import Events
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


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
class AuthUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=100,required=True)
    username = forms.EmailField(max_length=100,required=True)
    email = forms.EmailField(max_length=100,required=True)
    adminpic = forms.ImageField(max_length=100,required=False)
    is_superuser = forms.BooleanField(required=False)
    is_active = forms.BooleanField(required=False)


    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'is_superuser', 'is_active','email','adminpic')
        
        widgets = {

        'adminpic': forms.FileInput(attrs={'class': 'upload'}),

         }

class AuthUserEditForm(UserCreationForm):
    first_name = forms.CharField(max_length=100,required=True)
    username = forms.EmailField(max_length=100,required=True)
    email = forms.EmailField(max_length=100,required=True)
    adminpic = forms.ImageField(max_length=100,required=False)
    is_superuser = forms.BooleanField(required=False)
    is_active = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username','first_name', 'is_superuser', 'is_active','email','adminpic')
        widgets = {

        'adminpic': forms.FileInput(attrs={'class': 'upload'}),

        }

