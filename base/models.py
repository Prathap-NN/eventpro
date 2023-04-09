from distutils.command.upload import upload
from tkinter.tix import Tree
from unittest.util import _MAX_LENGTH
from django.contrib.auth.models import User
from django.db import models
from ckeditor.fields import RichTextField



class Events(models.Model):
    title = models.CharField(max_length=200)
    # name = models.CharField(max_length=200)
    description = models.CharField(max_length=191, blank=True, null=True)
    email = models.CharField(max_length=191, blank=True, null=True, default='')
    about = RichTextField(blank=True, null=True)
    event_start_date = models.DateField(blank=True, null=True)
    event_end_date = models.DateField(blank=True, null=True)
    department = models.CharField(max_length=191, blank=True, null=True,default='')
    campus = models.CharField(max_length=191, blank=True, null=True)
    tags = models.CharField(max_length=191, blank=True, null=True)    
    event_start_time = models.TimeField(blank=True, null=True)
    event_end_time = models.TimeField(max_length=191,null=True,blank=True)
    contact = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_online_event = models.CharField(max_length=3, blank=True, null=True)
    website = models.CharField(max_length=191, blank=True, null=True)
    facebook = models.CharField(max_length=191, blank=True, null=True)
    youtube = models.CharField(max_length=191, blank=True, null=True)
    instagram = models.CharField(max_length=191, blank=True, null=True)
    twitter = models.CharField(max_length=191, blank=True, null=True)
    featured_img = models.ImageField(blank=True, null=True)
    attachment = models.CharField(max_length=200,blank=True,null=True)
    # Speakermail = models.CharField(max_length=191, blank=True, null=True)
    attachment = models.TextField(blank=True, null=True)
    view_count = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    external_link = models.TextField(blank=True, null=True)
    club_name = models.CharField(max_length=191, blank=True, null=True)
    button_name = models.CharField(max_length=20, blank=True, null=True)
    custom_text = models.CharField(max_length=100, blank=True, null=True)
    event_price = models.CharField(max_length=100, blank=True, null=True)
    event_attendees = models.CharField(max_length=10, blank=True, null=True)
    publish = models.CharField(max_length=20, blank=True, null=True)
    # google_map = models.CharField(max_length=15, blank=True, null=True)
    num_likes = models.IntegerField(blank=True,null=True,default=1)

    
       


    def __str__(self):
          return self.title
    
    def num_likse(self):
         return self.num_likes.all().count()

    class Meta:
        ordering = ['-updated_at', '-created_at']
    
   
        # managed = False
        # db_table = 'events'
       
class Campus(models.Model): 
    campuses = models.CharField(max_length=191, blank=True, null=True)
         

class Pictures(models.Model):
    event = models.ForeignKey(Events,on_delete=models.CASCADE,blank=True, null=True)
    event_images = models.ImageField(height_field=None, width_field=None, max_length=None)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

class Speakers(models.Model):
    event = models.ForeignKey(Events,on_delete=models.CASCADE,blank=True, null=True)
    name = models.CharField(max_length=191)
    profile_pic = models.ImageField(upload_to='speakers/',max_length=191)
    about = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)

class Brochures(models.Model):
    event =  models.ForeignKey(Events,on_delete=models.CASCADE,blank=True, null=True)
    document = models.FileField(upload_to="brochures/", max_length=100,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    

class Department(models.Model):
    name = models.CharField(max_length=255,blank=True, null=True)
    def __str__(self):
        return self.name

