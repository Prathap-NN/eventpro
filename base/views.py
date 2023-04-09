from contextlib import redirect_stderr
from importlib.resources import contents
from multiprocessing import Event, context
from traceback import print_tb
from unicodedata import name
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse,HttpResponseRedirect
from .models import Events,Pictures,Speakers,Brochures,Department
# import datetime
from .form import EventsForm, EventAboutForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.db.models import CharField,TextField
from django.db.models import  Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
import time
from datetime import date
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404




# def like_event(request, event_id):
#   event = get_object_or_404(Events, id=event_id)
#   event.num_likes += 1
#   event.save()
#   return JsonResponse({'success': True, 'num_likes': event.num_likes})
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.likes += 1
    post.save()
    data = {'success': True, 'num_likes': post.likes}
    return JsonResponse(data)

def paginate(obj,page_number):
    p = Paginator(obj, 70)
    try:
        page_obj = p.get_page(page_number)  
    except PageNotAnInteger:
        
        page_obj = p.page(1)
    except EmptyPage:
        
        page_obj = p.page(p.num_pages)
    return page_obj


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    

    #PAGINATION start
    events = Events.objects.filter(
        Q(title__icontains=q) |
        Q(description__icontains=q) |
        Q(department__icontains=q) |
        Q(campus__icontains=q) 
        
    )
    p = Paginator(events, 20)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
       
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    todays_date = date.today()
    # previous = Events.objects.filter(event_start_date__lt=todays_date)
    # ongoing = Events.objects.filter(event_start_date = todays_date )
    # upcoming = Events.objects.filter(event_start_date__gt=todays_date)

    upcoming_count=False
    ongoing_count=False
    previous_count=False
    for event in events:
        if event.event_start_date:
            if not upcoming_count and event.event_start_date>todays_date:

                upcoming_count=True
            if not ongoing_count and event.event_start_date==todays_date:
                ongoing_count=True
            if not previous_count and event.event_start_date<todays_date:
                previous_count=True


    # for event in events.object_list: 
    #     if now "Y-m-d" as todays_date:
    #      if  todays_date >= event.event_start_date|date:"Y-m-d" and todays_date <= event.event_end_date|date:"Y-m-d":

    
    context = {'events': page_obj,'previous':previous_count,'ongoing':ongoing_count,'upcoming':upcoming_count}
    return render(request, 'base/home.html', context)
     #PAGINATION Ends


   
#like function
def like(request):
    if request.method == 'POST':
       
        id = request.POST.get('id', None)
       
        value = request.POST.get('key', None)
        
        event = Events.objects.filter(id=id)[0]
        # print(event)
        if event.num_likes==None or event.num_likes<1:
            event.num_likes=1

        if value=="like":

            event.num_likes=event.num_likes+1
        else:
            
            event.num_likes=event.num_likes-1
        event.save()
        ctx = {'num_likes_count':event.num_likes}
        return HttpResponse(json.dumps(ctx), content_type='application/json')
    
   
#browse by campus
def browse_campus(request,key):
   
    events = Events.objects.filter(campus__contains=key)
    print("event is ",events)
    page_number=request.GET.get('page')
    events=paginate(events,page_number)
    context = {'events': events}
    return render(request, 'base/home.html', context)



# browse by tags
def browse_tags(request,key):
    events = Events.objects.filter(tags__contains=key)
    page_number=request.GET.get('page')
    events=paginate(events,page_number)
    context = {'events': events}
    return render(request, 'base/home.html', context)

#browse by department
def browse_department(request,key):
    events = Events.objects.filter(department__contains=key)
    page_number=request.GET.get('page')
    events=paginate(events,page_number)
    context = {'events': events}
    return render(request, 'base/home.html', context)

# def ribbon(request,key):

#     today = date.today()
#     if key=="Previous":
        
#         events = Events.objects.filter(event_start_date__lt=today)
#     elif key=="Upcoming":
#         events = Events.objects.filter(event_start_date__gt=today)
#     else:
#         events = Events.objects.filter(event_start_date=today)
#     page_number=request.GET.get('page')
#     events=paginate(events,page_number)
#     context = {'events': events}
#     return render(request, "base/home.html", context)



def ribbon(request, key):
    today = date.today()
    if key == "Previous":
        events = Events.objects.filter(event_start_date__lt=today)
    elif key == "Upcoming":
        events = Events.objects.filter(event_start_date__gt=today)
    else:
        events = Events.objects.filter(event_start_date__lte=today, event_end_date__gte=today)
    page_number = request.GET.get('page')
    events = paginate(events, page_number)
    todays_date = date.today()
    upcoming_count=False
    ongoing_count=False
    previous_count=False
    for event in events:
        if event.event_start_date:
            if not upcoming_count and event.event_start_date>todays_date:
                upcoming_count=True
            if not ongoing_count and event.event_start_date==todays_date:
                ongoing_count=True
            if not previous_count and event.event_start_date<todays_date:
                previous_count=True

    context = {'events': events,'previous':previous_count,'ongoing':ongoing_count,'upcoming':upcoming_count}
    return render(request, "base/home.html", context)


def events(request):
    events = None

    return render(request, 'base/dashboard.html')

#edit page
def Edit_Event(request,pk):
    form = Events.objects.get(id=pk)
    pictures = Pictures.objects.filter(event_id=pk)
    speaker = Speakers.objects.filter(event_id=pk)
    brouchers = Brochures.objects.filter(event_id=pk)
    about_event = EventAboutForm(instance=form)
    EventsForms = EventsForm()
    if request.method=="POST":
        form.title = request.POST.get('title')
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
        if request.FILES.get('featured_img'):
            form.featured_img = request.FILES.get('featured_img')
        
        form.event_start_time = request.POST.get('start_time')
        form.event_end_time = request.POST.get('end_time')
        if not form.event_start_date:
            form.event_start_date=None
        if not form.event_end_date:
            form.event_end_date=None
        if not form.event_start_time:
            form.event_start_time=None
        if not form.event_end_time:
            form.event_end_time=None
        
        form.contact = request.POST.get('contact')
        venue_name= request.POST.get('venue_name')
        default_venue = request.POST.get('default_venue')
        if venue_name==None or venue_name=='':
            default_venue=''
        if default_venue==None:
            default_venue=""
        form.address = form.address = venue_name + ' ' + default_venue
        form.is_online_event = request.POST.get('is_online_event')
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


        

        files = request.FILES.getlist('event_images')
        for f in files:
            
            Pictures.objects.create(event_id=form.id,event_images=f)
        
        return redirect('single-event',pk)
   
    address =form.address
    
    address0="PES University, Ring Road Campus, Bangalore 560 085."
    address1="PES University, Electronic City Campus, Bangalore"
    address2="PES HN Campus,Hanumanthanagar, Bangalore 560050."
    found=0
    form.venue_name=""
    form.addr_num=-1
   
    if address!=None:
        for index,addr in enumerate([address0,address1,address2]):
            if addr in address:
                form.venue_name=address.replace(addr,"").rstrip()
                form.addr_num=index
                found=1
                break
        if not found:
            form.venue_name=address
            form.addr_num=-1

   
    
    context = {
        "form":form,
        'pictures':pictures,
        'speaker':speaker,
        'brouchers': Brochures.objects.filter(event_id=form.id),
        'EventsForms':EventsForms,
        'about_events':about_event,

    }
    return render(request, 'base/edit-event.html', context)
#edit page ends 

#create event
@login_required(login_url='login')
def createEvent(request):
    EventsForms = EventsForm()
    if request.method=="POST":
        print("getting created")
        form = Events()
        brouchers = Brochures()
        form.title = request.POST.get('title')
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
        form.email = request.POST.get('email')
        if len(request.FILES) != 0:
         form.featured_img = request.FILES.get('featured_img')
        form.event_start_time = request.POST.get('start_time')
        form.event_end_time = request.POST.get('end_time')
        if not form.event_start_date:
            form.event_start_date=None
        if not form.event_end_date:
            form.event_end_date=None
        if not form.event_start_time:
            form.event_start_time=None
        if not form.event_end_time:
            form.event_end_time=None
        form.contact = request.POST.get('contact')
        form.description = request.POST.get('description')
        venue_name= request.POST.get('venue_name')
        default_venue = request.POST.get('default_venue')
        if venue_name=='':
            default_venue=''
        if default_venue==None:
            default_venue=""
        form.address = venue_name + ' ' + default_venue
        form.is_online_event = request.POST.get('is_online_event')
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
            Pictures.objects.create(event_id=form.id,event_images=f)
        home(request)
    

    departments = Department.objects.all()
        
    context = {'EventsForms':EventsForms,'departments':departments}
    return render(request, 'base/create-event.html', context)

#create event ends

def myListing(request):
    recent_events2 = Events.objects.all()
    p = Paginator(recent_events2, 16)   
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
       
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    context = {'recent_events2': page_obj}   
    return render(request, 'base/dashboard.html',context)  

#adddepartment
def add_department(request):
    if request.method == 'POST':
        name = request.POST['department-input']
        department = Department(name=name)
        department.save()
        return redirect('add_department')  # Redirect to the same page after submission
    else:
        departments = Department.objects.all()
        return render(request, 'base/adddepartment.html', {'departments': departments})

         


#singleevent
def singlEvent(request,pk):
    
    event = Events.objects.get(id=pk)
    speaker =Speakers.objects.filter(event_id=pk)
    pictures = Pictures.objects.filter(event_id=pk)
    imagecount = pictures.count()
    brouchures = Brochures.objects.filter(event_id=pk)
    recent_events = Events.objects.all().order_by('-created_at')[:6]

    event= eventsview(event)
   
    try:
        start_time=event.event_start_time
        if "." in start_time:
            start_time=start_time[:-2]
        event.event_start_time = datetime.strptime(start_time, '%H:%M:%S').time()
        
        end_time=event.event_end_time
        if "." in end_time:
            end_time=end_time[:-2]
        event.event_end_time = datetime.strptime(end_time, '%H:%M:%S').time()

    except:
        print("could not convert the date")
    print("broucher is",brouchures)
    context={'event':event,'speaker':speaker,'pictures':pictures,'brouchers':brouchures,'recent_events':recent_events,'imagecount':imagecount}
    return render(request, 'base/singlevent.html',context)  

def eventsview(event):
    try:
        event.event_start_time = datetime.strptime(event.event_start_time, '%I:%M %p')
        if event.event_end_time is not None:
            event.event_end_time = datetime.strptime(event.event_end_time , '%I:%M %p')
    except:
        print("Error while convertig time")
    event.view_count = event.view_count + 1
    event.save()
    return event

   


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            # messages.error(request, 'User does not exist.')
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
    return redirect('login')

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
    return redirect('list')

#Delete method.
@login_required(login_url='login')
def createSpeaker(request, pk):
    speaker = Speakers()
    # event_id = Events.objects.get(id=pk)
    if request.method=='POST':
        speaker = Speakers()
        speaker.name = request.POST.get('spkr_name')
        speaker.about = request.POST.get('spkr_about')
        speaker.profile_pic = request.FILES.get('spkr_profile_pic')
        speaker.event_id = pk
        speaker.save()
    context = {}
    return render(request, "base/create-speaker.html", context)


@login_required(login_url='login')
def deletePictures(request, pk):
    deletePics = Pictures.objects.get(id=pk)
    id = deletePics.event_id
    deletePics.delete()
    return redirect('edit-event', id)

@login_required(login_url='login')
def delete_brochure(request, pk):    
    delete_brochure = Brochures.objects.get(id=pk)
    id = delete_brochure.event_id
    delete_brochure.delete()
    return redirect('edit-event', id)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'base/change_password.html', {'form': form})