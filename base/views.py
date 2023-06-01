from contextlib import redirect_stderr
from importlib.resources import contents
from multiprocessing import Event, context
from unicodedata import name
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse,HttpResponseRedirect
from .models import Events,Pictures,Speakers,Brochures,Department,Tag,Campus,Location,Platform,Contacts
from .form import EventsForm, EventAboutForm,AuthUserForm,AuthUserEditForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import CharField,TextField
from django.db.models import  Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from datetime import date
from datetime import datetime
from django.http import JsonResponse
from PIL import Image
from io import BytesIO
import os
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile





#Home----------
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    now = date.today()

    if q:
        ongoing_events = Events.objects.filter( Q(title__icontains=q) |
                                               Q(description__icontains=q) |
                                               Q(department__icontains=q) |
                                               Q(campus__icontains=q),event_start_date=now, is_archived=False).order_by('-event_start_date')
        upcoming_events = Events.objects.filter(Q(title__icontains=q) |
                                                Q(title__icontains=q) |
                                                Q(department__icontains=q) |
                                                Q(campus__icontains=q),event_start_date__gt=now, is_archived=False).order_by('-event_start_date')
        previous_events = Events.objects.filter(Q(title__icontains=q) |
                                                Q(description__icontains=q) |
                                                Q(department__icontains=q) |
                                                Q(campus__icontains=q),event_start_date__lt=now, is_archived=False).order_by('-event_start_date')
    else:
        ongoing_events = Events.objects.filter(event_start_date=now,is_archived=False).order_by('-event_start_date')
        upcoming_events = Events.objects.filter(event_start_date__gt=now,is_archived=False).order_by('-event_start_date')
        previous_events = Events.objects.filter(event_start_date__lt=now,is_archived=False).order_by('-event_start_date')
   # Limit previous_events queryset to 9 results
    previous_events = previous_events[:9]

    # Concatenate the queryset results to get the final sorted data
    on_up_events = ongoing_events | upcoming_events
    events = list(ongoing_events) + list(upcoming_events) + list(previous_events)  
    reversed_on_up_events = on_up_events.reverse()

    upcoming_count, ongoing_count, previous_count = get_event_count(events)

    # Pass the previous_events queryset with limited results to the context
    context = {'is_home': True, 'paginated_previous': previous_events, 'events': previous_events,'on_up_events': reversed_on_up_events, 'previous_events': previous_events[:9],'previous': previous_count, 'ongoing': ongoing_count, 'upcoming': upcoming_count,'total_count': len(events)}
    return render(request, 'base/home.html', context)

def get_event_count(events):
    upcoming_count=False
    ongoing_count=False
    previous_count=False
    todays_date = date.today()

    for event in events:
        if event.event_start_date:
            if not upcoming_count and event.event_start_date>todays_date:

                upcoming_count=True
            if not ongoing_count and event.event_start_date==todays_date:
                ongoing_count=True
            if not previous_count and event.event_start_date<todays_date:
                previous_count=True
    return upcoming_count,ongoing_count,previous_count

#Create-Event----------
def createEvent(request):
    current_date = date.today()
    EventsForms = EventsForm()
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()
    if request.method=="POST":
        for key, value in request.POST.items():
            print(key,value)
        
        form = Events()
        brouchers = Brochures()

        form.title = request.POST.get('title')
        form.is_online_event =  "Yes" if request.POST.get('is_online_event')=="Online" else "No"       
        form.event_price = request.POST.get('event_price')
        form.about = request.POST.get('about')
        form.Speakermail =request.POST.get('spkrgmail')
        form.event_start_date = request.POST.get('start_date')
        form.event_end_date = request.POST.get('end_date')
        department = request.POST.getlist('department[]')   
        form.department=",".join(department)
        campus = request.POST.getlist('campus[]')        
        form.campus=",".join(campus)
        tags = request.POST.getlist('tag[]')
        form.tags=",".join(tags)
        contact_names = request.POST.getlist('contact_name[]')       
        # Get the list of contacts
        contacts = request.POST.getlist('contact[]')
        # Get the list of contact emails
        contact_emails = request.POST.getlist('contact_email[]')
            
        for name, contact, email in zip(contact_names, contacts, contact_emails):
            form.event = Events(contact_name=name, contact=contact, email=email)
        if 'featured_img' in request.FILES:
            featured_img = request.FILES['featured_img']
            if featured_img.size > 300 * 1024:  
                # Open the image using PIL
                img = Image.open(featured_img)
                # Calculate the new width and height to maintain aspect ratio
                width, height = img.size
                aspect_ratio = width / height
                new_width = int((300 * 1024) ** 0.5 * aspect_ratio)
                new_height = int((300 * 1024) ** 0.5 / aspect_ratio)
                # Resize the image
                img = img.resize((new_width, new_height), Image.ANTIALIAS)
                # Save the compressed image to a BytesIO object
                output = BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                # Update the form with the compressed image
                form.featured_img = InMemoryUploadedFile(
                    output, 'ImageField', featured_img.name, 'image/jpeg', output.tell(), None
                )
            else:
                form.featured_img = featured_img
        form.event_start_time = request.POST.get('start_time')
        form.event_end_time = request.POST.get('end_time')
        if not form.event_start_date:
            form.event_start_date=current_date
        if not form.event_end_date:
            form.event_end_date=None
        if not form.event_start_time:
            form.event_start_time=None
        if not form.event_end_time:
            form.event_end_time=None
        
        form.description = request.POST.get('description')
        venue_name= request.POST.get('venue_name')
        default_venue = request.POST.get('default_venue')
        if venue_name == None or venue_name == '':
            default_venue = ''
        if default_venue == None:
            default_venue = ""
        if form.is_online_event == "No":
            form.address = venue_name + ' ' + default_venue
        else:
            form.address = venue_name + ',' + default_venue
        # form.is_online_event = request.POST.get('is_online_event')
        form.website = request.POST.get('website')
        form.facebook = request.POST.get('facebook')
        form.youtube = request.POST.get('youtube')
        form.instagram = request.POST.get('instagram')
        form.twitter = request.POST.get('twitter')
        if request.POST.getlist('button_name[]'):
            button_name=request.POST.getlist('button_name[]')[0]
            if button_name != "Custom Text":
                form.button_name = button_name
                form.external_link = request.POST.get('external_link')
            elif button_name == "Custom Text":
                form.button_name = button_name
                form.external_link = request.POST.get('custom_text')
        brouchers.document = request.FILES.get('event_broucher')
        form.view_count = 1
        form.publish = ('publish')
        form.google_map = ('google_map')
        form.attachment = request.POST.get('docs[]')
        form.save()
        brouchers.event_id = form.id
        brouchers.save()
        files = request.FILES.getlist('event_images')
        for f in files:
            if f.size > 300 * 1024:
                # Open the image using PIL
                img = Image.open(f)                
                # Save the compressed image to a BytesIO object
                output = BytesIO()
                img.save(output, format='JPEG', quality=60)
                output.seek(0)
                # Update the form with the compressed image
                Pictures.objects.create(
                    event_id=form.id,
                    event_images=InMemoryUploadedFile(
                        output, 'ImageField', f.name, 'image/jpeg', output.tell(), None
                    )
                )
            else:
                Pictures.objects.create(event_id=form.id, event_images=f)
        # for i in range(len(contact_names)):
        #     c=Contacts.objects.create(event_id=form.id,name=contact_names[i],phone=contacts[i],email=contact_emails[i])
        #     c.save()
        for i in range(len(contact_names)):
            if contact_names[i] or contacts[i] or contact_emails[i]:  # Check if any of the data fields are not empty
                c = Contacts.objects.create(event_id=form.id, name=contact_names[i], phone=contacts[i], email=contact_emails[i])
                c.save()

        singleEvent_redirection= '/singlevent/'+str(form.id)
        return redirect(singleEvent_redirection)
    departments = Department.objects.all()
    location = Location.objects.all()
    platform = Platform.objects.all()
    tags = Tag.objects.all()
    campuspes = Campus.objects.all()
        
    context = {'EventsForms':EventsForms,'departments':departments,'campuspes':campuspes,'tags':tags,'location':location,'platform':platform}
    return render(request, 'base/create-event.html', context)

#create event ends

#Edit event------------

def Edit_Event(request,pk):
    form = Events.objects.get(id=pk)
    location = Location.objects.all()
   
    location_list=[ i.name for i in location]
    print("location list is ",location_list)
    is_online=form.is_online_event
    address=form.address
    print("address is",address)
    if is_online == "Yes":
        
        if address:
            form.url, form.platform = address.split(",", maxsplit=1)
    else:
        for i in location_list:
            
            a=" ".join(address.split())
            
            b=" ".join(i.split())
            
            
            if b in a :
                
                index = a.find(b)
                # since variable url is used in template sending full_address as url
                form.url = address[:index]
                form.default_campus = address[index:]
               

    pictures = Pictures.objects.filter(event_id=pk)   
    speaker=0
    brouchers = Brochures.objects.filter(event_id=pk)
    contacts = Contacts.objects.filter(event_id=pk)
    campuspes = Campus.objects.all()
    departments = Department.objects.all()
    tags = Tag.objects.all()
    
    platform = Platform.objects.all()
    about_event = EventAboutForm(instance=form)
    EventsForms = EventsForm()
    if request.method=="POST":
        form.title = request.POST.get('title')
        form.is_online_event =  "Yes" if request.POST.get('is_online_event')=="Online" else "No"
        form.description = request.POST.get('description')
        form.about = request.POST.get('about')
        form.event_start_date = request.POST.get('start_date')
        form.event_end_date = request.POST.get('end_date')
        department = request.POST.getlist('department[]')
        form.department=",".join(department)
        campus = request.POST.getlist('campus[]')
        form.campus=",".join(campus)       
        tags = request.POST.getlist('tag[]')
        form.tags=",".join(tags)
        form.email = request.POST.get('email[]')
        contact_names = request.POST.getlist('contact_name[]')      
        contacts = request.POST.getlist('contact[]')
        contact_id = request.POST.getlist('contact_id[]')
        contact_emails = request.POST.getlist('contact_email[]')
        if 'featured_img' in request.FILES:
            featured_img = request.FILES['featured_img']
            if featured_img.size > 300 * 1024:  
                # Open the image using PIL
                img = Image.open(featured_img)
                # Calculate the new width and height to maintain aspect ratio
                width, height = img.size
                aspect_ratio = width / height
                new_width = int((300 * 1024) ** 0.5 * aspect_ratio)
                new_height = int((300 * 1024) ** 0.5 / aspect_ratio)
                # Resize the image
                img = img.resize((new_width, new_height), Image.ANTIALIAS)
                # Save the compressed image to a BytesIO object
                output = BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                # Update the form with the compressed image
                form.featured_img = InMemoryUploadedFile(
                    output, 'ImageField', featured_img.name, 'image/jpeg', output.tell(), None
                )
            else:
                form.featured_img = featured_img
        
        form.event_start_time = request.POST.get('start_time')
        form.event_end_time = request.POST.get('end_time')
        if not form.event_start_date:
            form.event_start_date=None
        if not form.event_end_date:
            form.event_end_date=None
        if not form.event_start_time or form.event_start_time == "null":
            form.event_start_time=None
        if not form.event_end_time or form.event_end_time == "null":
            form.event_end_time=None
        
        form.contact = request.POST.get('contact')

        venue_name= request.POST.get('venue_name')
        default_venue = request.POST.get('default_venue')
        if venue_name == None or venue_name == '':
            default_venue = ''
        if default_venue == None:
            default_venue = ""
        if form.is_online_event == "No":
            form.address = venue_name + ' ' + default_venue
        else:
            form.address = venue_name + ',' + default_venue
       
        
        form.website = request.POST.get('website')
        form.facebook = request.POST.get('facebook')
        form.youtube = request.POST.get('youtube')
        form.instagram = request.POST.get('instagram')
        form.twitter = request.POST.get('twitter')
        if request.POST.getlist('button_name[]'):
            button_name=request.POST.getlist('button_name[]')[0]
            if button_name != "Custom Text":
                form.button_name = button_name
                form.external_link = request.POST.get('external_link')
            elif button_name == "Custom Text":
                form.button_name = button_name
                form.external_link = request.POST.get('custom_text')
        
        form.custom_text = request.POST.get('custom_text')
        brouchers.document = request.FILES.get('event_broucher')
        form.publish = 'publish'
        form.google_map = request.POST.get('google_map')
        form.attachment = request.POST.get('docs[]')
        form.save()

        if speaker:
            speaker.name = request.POST.get('spkr_name')
            speaker.about = request.POST.get('spkr_about')
            speaker.profile_pic = request.FILES.get('spkr_profile_pic')
            speaker.contact = request.FILES.get('spkr_contact')
            speaker.designation = request.FILES.get('designation')
            print("speaker desgination",speaker.designation)
          
            speaker.save()
        # Update brochure document if it exists
        if request.FILES.get('event_broucher'):
            try:
                brochure = Brochures.objects.get(event_id=form.id)
                brochure.document = request.FILES.get('event_broucher')
                brochure.save()
            except Brochures.DoesNotExist:
                print("could not fetch broucher")
                brouchers = Brochures()
                brouchers.document = request.FILES.get('event_broucher')
                brouchers.event_id = form.id
                brouchers.save()
                print("print brochure",brouchers)
        # Remove any contacts that have been removed in the form submission
        Contacts.objects.filter(event_id=form.id).exclude(id__in=[id for id in contact_id if id not in ['', None]]).delete()

        # Loop through the contact data and update or create the contacts
        for i in range(len(contact_names)):
                try:
                    if contact_id[i] and (contact_names[i] or contacts[i] or contact_emails[i]) :
                        obj = Contacts.objects.get(id=contact_id[i])
                        obj.name = contact_names[i]
                        obj.phone = contacts[i]
                        obj.email = contact_emails[i]
                        obj.save()
                    elif contact_id[i] and (not contact_names[i] and not contacts[i] and not  contact_emails[i]):
                        obj = Contacts.objects.get(id=contact_id[i])
                        obj.delete()
                    else:
                        raise Contacts.DoesNotExist()
                except Contacts.DoesNotExist:
                      if contact_names[i] or contacts[i] or contact_emails[i]:  # Check if any of the data fields are not empty
                        obj = Contacts.objects.create(event_id=form.id, name=contact_names[i], phone=contacts[i], email=contact_emails[i])
                        obj.save()
        files = request.FILES.getlist('event_images')
        for f in files:
            
            Pictures.objects.create(event_id=form.id,event_images=f)
        
        return redirect('single-event',pk)
    
    context = {
        "form":form,
        'pictures':pictures,
        'contacts':contacts,
        'speaker':speaker,
        'brouchers': Brochures.objects.filter(event_id=form.id),
        'EventsForms':EventsForms,
        'about_events':about_event,
        'campuspes':campuspes,
        'tags':tags,
        'departments':departments,
        'location':location,
        'platform':platform,

    }
    return render(request, 'base/edit-event.html', context)
#edit function ends 

#Single-Event------------
def singlEvent(request, pk):
    event = get_object_or_404(Events, id=pk)
    try:
        pk=int(pk)
        event = get_object_or_404(Events, id=pk)
    except (ValueError, Events.DoesNotExist):
        return render(request,'base/404.html')
    speaker = Speakers.objects.filter(event_id=pk)   
    pictures = Pictures.objects.filter(event_id=pk)
    contacts = Contacts.objects.filter(event_id=pk)
    print("before sending........................................................",contacts)
    imagecount = pictures.count()
    try:
        brouchures = Brochures.objects.get(event_id=pk)
    except ObjectDoesNotExist:
        brouchures = None 
    recent_events = Events.objects.all().order_by('-created_at')[:6]
    platform = Platform.objects.all()

    add_count = event.view_count + 1
    Events.objects.filter(id=pk).update(view_count=add_count)

    try:
        start_time = event.event_start_time
        if "." in start_time:
            start_time = start_time[:-2]
        event.event_start_time = datetime.strptime(start_time, '%H:%M:%S').time()
    except:
        print("could not convert the start date")
    try:
        end_time = event.event_end_time

        if "." in end_time:
            end_time = end_time[:-2]
        event.event_end_time = datetime.strptime(end_time, '%H:%M:%S').time()
        

    except:
        print("could not convert the end date")
   

    selected_platform = request.GET.get('online_select') # get the selected platform from request.GET dictionary
    
    context = {
        'event': event,
        'speaker': speaker,
        'pictures': pictures,
        'brouchers': brouchures,
        'recent_events': recent_events,
        'imagecount': imagecount,
        'platform': platform,
        'contacts': contacts,
        'selected_platform': selected_platform, # add the selected platform to the context
    }

    return render(request, 'base/singlevent.html', context)

#Single-Event Ends

#Update and delete event-----------

@login_required(login_url='login')
def updateEvent(request, pk):
    edited = Events.objects.get(id=pk)
    form = EventsForm(instance=edited)

    if request.method == 'POST':
        form = Events(request.POST, instance=edited)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, "base/create-event.html", context)


@login_required(login_url='login')
def deleteEvent(request, pk):
    deleteEv = Events.objects.get(id=pk)
    deletePics = Pictures.objects.filter(event_id=pk)
    deletePics.delete()
    deleteEv.delete()
    return redirect('event_listing')


#View counts-----------
def eventsview(event):
    try:
        if event.event_end_time is not None:
            event.event_end_time = datetime.strptime(event.event_end_time , '%I:%M %p')
    except:
        print("Error while convertig time")
    event.view_count = event.view_count + 1
    event.save()
    return event
#view count ends

# Like Function ------------
def like_event(request, event_id,like_type):
    event = get_object_or_404(Events, id=event_id)
    if like_type=="like":
        event.num_likes += 1
    else:
        event.num_likes -= 1

    
    try:
        start_time = event.event_start_time
        print("start_time before conversion:", start_time)
        
        if "." in start_time:
            start_time = start_time[:-2]
            
        event.event_start_time = datetime.strptime(start_time, '%I:%M %p').time()
        print("start_time after conversion:", event.event_start_time)
        
    except:
        print("Could not convert the start time")
    
    try:
        end_time = event.event_end_time
        print("end_time before conversion:", end_time)
        
        if "." in end_time:
            end_time = end_time[:-1]
            
        event.event_end_time = datetime.strptime(end_time, '%I:%M %p').time()
        print("end_time after conversion:", event.event_end_time)
        
    except:
        print("Could not convert the end time")
        
    event.save()
    return JsonResponse({'success': True, 'new_like_count': event.num_likes})

def update_like_count(request):
    if request.method == 'POST' and request.is_ajax():
        event_id = request.POST.get('event_id')
        like_count = request.POST.get('like_count')

        # Update the like count in the database for the event with the given event ID
        # You can use the appropriate Django model and update the num_likes field
        event = Event.objects.get(id=event_id)
        event.num_likes = like_count
        event.save()

        # Return a JSON response with a success message
        data = {'message': 'Like count updated successfully'}
        return JsonResponse(data)
    else:
        # Return a JSON response with an error message
        data = {'message': 'Error updating like count'}
        return JsonResponse(data, status=400)

#Like Function Ends


#Browse all----------
def browse_all(request, queryset, tag, per_page=9):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page')
    events = paginator.get_page(page)

    total_count = queryset.count()      # Get the total count of events with the specified tag
    
    context = {
        'browse_all': events,
        'total_count': total_count, # Add the total count to the context
        'browse_by': tag, # Add the tag to the context for displaying in the template
    }
    return render(request, 'base/browse.html', context)

def browse_tags(request, tag):
    browse_all_queryset = Events.objects.filter(tags__icontains=tag)
    return browse_all(request, browse_all_queryset, tag)

def browse_department(request, tag):
    browse_department_queryset = Events.objects.filter(department__icontains=tag)
    return browse_all(request, browse_department_queryset, tag)

def browse_campus(request, tag):
    tags = tag.split(',')  # Split the tag values by comma to get separate tag values
    browse_campus_queryset = Events.objects.filter(campus__icontains=tags[0]) | Events.objects.filter(campus__icontains=tags[1])  # Use | (OR) operator to filter by either of the two tag values
    
    return browse_all(request, browse_campus_queryset, tag)

def browse(request):
    events = Events.objects.all()
    context = {'events':events}
    return render(request, 'base/browse.html', context)

#Browse all ends

#Ribbon-----------
def ribbon(request, key):
    print("key is",key)
    today = date.today()
    if key == "Previous":
        events = Events.objects.filter(event_start_date__lt=today,is_archived=False)
    elif key == "Upcoming":
        events = Events.objects.filter(event_start_date__gt=today,is_archived=False)
    else:
        events = Events.objects.filter(event_start_date__lte=today, event_end_date__gte=today,is_archived=False)
    
    page_number = request.GET.get('page')
    paginator = Paginator(events, 9)  # Change 10 to the desired number of objects per page
    events = paginator.get_page(page_number)

    context = {'events': events,'key':key}
    return render(request, "base/ribbon.html", context)

#Ribbon ends

#Event Listing ----------
def myListing(request):
    recent_events2 = Events.objects.all()
    p = Paginator(recent_events2, 16)   
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:       
        page_obj = p.page(1)
    except EmptyPage:        
        page_obj = p.page(p.num_pages)
    context = {'recent_events2': page_obj}   
    return render(request, 'base/eventlisting.html',context) 


def edit_listing(request, event_id,pk):    
    speaker = Speakers.objects.filter(event_id=pk)
    event = Events.objects.get(id=event_id)
    context = {'event': event,'speaker':speaker}
    return render(request, 'base/edit-event.html', context)

#Event Listing Ends

#Draft page----------
@login_required
def draft_page(request):
    draft_events = Events.objects.filter(status='draft').order_by('-created_at')
    published_events = Events.objects.filter(status='published').order_by('-created_at')
    archived_events = Events.objects.filter(status='archived').order_by('-created_at')

    p = Paginator(archived_events, 16)   
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
       
        page_obj = p.page(1)
    except EmptyPage:
        
        page_obj = p.page(p.num_pages)
    context = {
        'draft_events': draft_events,
        'published_events': published_events,
        'archived_events': page_obj,
    }
    return render(request, 'base/draft-page.html', context)

#Archieve event---------
def archive_event(request, event_id):
    event = get_object_or_404(Events, pk=event_id)
    event.status = 'archived'
    event.is_archived = True # add this line
    event.is_published=False
    event.save()
    messages.success(request, f'The event "{event.title}" has been archived.')
    return redirect('draft-page')

#Publish event----------
@login_required
def publish_event(request, event_id):
    event = get_object_or_404(Events, pk=event_id)
    event.status = 'published'
    event.is_published = True
    event.is_archived=False
    event.save()
    messages.success(request, f'The event "{event.title}" has been published.')
    return redirect('draft-page') 


#Dashboard---------

def dashboard(request):
    total_events = Events.objects.count()
    
    context = {'total_events': total_events}
    return render(request, 'base/dashboard.html',context)
#Dashboard Ends


#Add - Department---------
def add_department(request):
    
    if request.method == 'POST':
        name = request.POST.get('department_input')
        department = Department(name=name)
        department.save()
        return redirect('add_department')  # Redirect to the same page after submission
    else:
        departments = Department.objects.all()
        return render(request, 'base/adddepartment.html', {'departments': departments})

def edit_department(request,pk):
    if request.method == 'POST':
        department = Department.objects.get(id=pk)
        dname = request.POST.get('department_input')
        department.name =dname
        department.save()
        return redirect('add_department')

def delete_department(request,pk):
    Department.objects.get(id=pk).delete()
    return redirect('add_department')

#Add new tags--------
def add_tag(request):
    
    if request.method == 'POST':
        name = request.POST.get('tag_input')
        tag = Tag(name=name)
        tag.save()
        return redirect('add_tags')  # Redirect to the same page after submission
    else:
        tags = Tag.objects.all()
        return render(request, 'base/add-tags.html', {'tags': tags})

def edit_tag(request,pk):
    if request.method == 'POST':
        tag = Tag.objects.get(id=pk)        
        tname = request.POST.get('tag_input')
        tag.name =tname
        tag.save()
        return redirect('add_tags')

def delete_tag(request,pk):
    Tag.objects.get(id=pk).delete()
    return redirect('add_tags')
#Add new tags ends

#Add NEW CAMPUS---------
def add_campus(request):
    if request.method == 'POST':
        name = request.POST.get('campus_input')
        campus = Campus(name=name)
        campus.save()
        return redirect('add_campus')  # Redirect to the same page after submission
    else:
        campuspes = Campus.objects.all()
        return render(request, 'base/add-campus.html', {'campuspes': campuspes})

def edit_campus(request,pk):
    if request.method == 'POST':
        campus = Campus.objects.get(id=pk)        
        cname = request.POST.get('campus_input')
        campus.name =cname
        campus.save()
        return redirect('add_campus')

def delete_campus(request,pk):
    Campus.objects.get(id=pk).delete()
    return redirect('add_campus')


#Add Location------------
def add_location(request):
    
    if request.method == 'POST':
        name = request.POST.get('location_input')
        location = Location (name=name)
        location.save()
        return redirect('add_location')  # Redirect to the same page after submission
    else:
        location = Location.objects.all()
        return render(request, 'base/add-location.html', {'location': location})

def edit_location(request,pk):
    if request.method == 'POST':
        location = Location.objects.get(id=pk)        
        lname = request.POST.get('location_input')
        location.name =lname
        location.save()
        return redirect('add_location')

def delete_location(request,pk):
    Location.objects.get(id=pk).delete()
    return redirect('add_location')


#Add Platform--------

def add_platform(request):
    
    if request.method == 'POST':
        name = request.POST.get('platform_input')
        platform = Platform (name=name)
        platform.save()
        return redirect('add_platform')  # Redirect to the same page after submission
    else:
        platform = Platform.objects.all()
        return render(request, 'base/add-platform.html', {'platform': platform})

def edit_platform(request,pk):
    if request.method == 'POST':
        platform = Platform.objects.get(id=pk)        
        pname = request.POST.get('platform_input')
        platform.name =pname
        platform.save()
        return redirect('add_platform')

def delete_platform(request,pk):
    Platform.objects.get(id=pk).delete()
    return redirect('add_platform')

#Add Platform

#Create speaker-------
@login_required(login_url='login')
def createSpeaker(request, pk):
    speaker = Speakers()
    # event_id = Events.objects.get(id=pk)
    if request.method=='POST':
        speaker = Speakers()
        speaker.name = request.POST.get('spkr_name')
        speaker.speakermail = request.POST.get('Speakermail')
        speaker.about = request.POST.get('spkr_about')
        speaker.profile_pic = request.FILES.get('spkr_profile_pic')
        speaker.contact = request.POST.get('spkr_contact')
        speaker.designation = request.POST.get('designation')
        
        speaker.event_id = pk
        speaker.save()
        return redirect('single-event', pk)
    context = {}
    return render(request, "base/create-speaker.html", context)

def editSpeaker(request, pk):
    speaker = Speakers.objects.get(id=pk)
    if request.method == 'POST':       
        speaker.name = request.POST.get('spkr_name')
        speaker.speakermail = request.POST.get('Speakermail')
        speaker.about = request.POST.get('spkr_about')
        speaker.profile_pic = request.FILES.get('spkr_profile_pic')
        speaker.contact = request.POST.get('spkr_contact')
        speaker.designation = request.POST.get('designation')
        speaker.save()
      
        return redirect('editSpeaker', pk=speaker.id)
    context = {'speaker': speaker}
    return render(request, "base/create-speaker.html", context)

@login_required(login_url='login')    
def deleteSpeaker(request, pk):
    speaker = Speakers.objects.get(id=pk)
    event_id = speaker.event_id
    speaker.delete()
    return redirect('single-event', pk=event_id)

def deleteSpeakerPic(request, pk):
    speaker = Speakers.objects.get(id=pk)
    if speaker.profile_pic:        
        file_path = os.path.join(settings.MEDIA_ROOT, str(speaker.profile_pic))
        os.remove(file_path)        
        speaker.profile_pic = None
        speaker.save()
        return redirect('editSpeaker', pk)

#delete pictures-------
@login_required(login_url='login')
def deletePictures(request, pk):
    deletePics = Pictures.objects.get(id=pk)
    id = deletePics.event_id
    deletePics.delete()
    return redirect('edit-event', id)




#Delete brochure--------
@login_required(login_url='login')
def delete_brochure(request, pk):    
    delete_brochure = Brochures.objects.get(id=pk)
    id = delete_brochure.event_id
    delete_brochure.delete()
    return redirect('edit-event', id)



#Login Function----------
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            
        except:
            messages.error(request, 'User does not exist.')
            pass
        user = authenticate(request, username=username, password=password)

        if user is not None:    
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "The username and password you entered don't match. Please try again.")

    context = {}
    return render(request, 'base/login-form.html', context)

def logoutUser(request):
    logout(request)
    messages.error(request, "You have successfully logged out")  
    return redirect('login')

#Login Function Ends

#Change password------------

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been successfully updated')
            return redirect('change_password')
        else:
            messages.error(request, 'Your password should include a mix of uppercase and lowercase letters, numbers, and symbols.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'base/change_password.html', {'form': form})

#Add user----------

@login_required(login_url='login')
def add_user(request):
    user_check= User.objects.all()
    form = AuthUserForm()
    if request.method == 'POST':
        form = AuthUserForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
       
    context = { 'user_check':user_check,'form':form}
    return render(request, "base/add-user.html", context)

#Edit user-----------


def edit_User(request,pk):
    user_check= User.objects.all()
    user = User.objects.get(id=pk)
    form = AuthUserEditForm(instance=user)
    if request.method == 'POST':
        form = AuthUserEditForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
        
    context = { 'user_check':user_check,'form':form}
    return render(request, "base/add-user.html", context)




#Delete user---------
def delete_user(request, pk):
    user_check= User.objects.all()

    user = get_object_or_404(User, id=pk)
    user.delete()
    context={'user_check':user_check}
    return render(request, "base/add-user.html", context)

def error_404_view(request):
    return render(request, 'base/404.html')

