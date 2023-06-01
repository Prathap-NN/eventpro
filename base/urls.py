from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.home, name="home"),


    path('like_event/<int:event_id>/<str:like_type>', views.like_event, name='like_event'),
    path('browse/<str:key>', views.browse, name='browse'),
    path('tags/<str:tag>/', views.browse_tags, name='browse_tags'),
    path('campus/<str:tag>', views.browse_campus, name='browse_campus'),
    path('department/<str:tag>', views.browse_department, name='browse_department'),
     path('browse/all/', views.browse_all, name='browse_all'),

    path('adduser/', views.add_user, name='add_user'),
    path('edituser/<str:pk>', views.edit_User, name='edit_user'),
    path('delete_user/<str:pk>/',views.delete_user, name='delete_user'),

    path('addplatform/', views.add_platform, name='add_platform'),
    path('editplatform/<str:pk>', views.edit_platform, name='edit_platform'),
     path('deleteplatform/<int:pk>', views.delete_platform, name='delete_platform'),

    path('addlocation/', views.add_location, name='add_location'),
    path('editlocation/<str:pk>', views.edit_location, name='edit_location'),
     path('deletelocation/<int:pk>', views.delete_location, name='delete_location'),


    path('archive-event/<int:event_id>/', views.archive_event, name='archive-event'), 
    path('draft-page/', views.draft_page, name='draft-page'),
    path('publish/<int:event_id>/',views.publish_event, name='publish_event'),

   
    path('dashboard/',views.dashboard, name="dashboard"),
    path('eventlisting/',views.myListing, name="event_listing"),

    path('addtags/',views.add_tag, name="add_tags"),
    path('edittags/<str:pk>', views.edit_tag, name='edit_tag'),
    path('deletetag/<int:pk>/', views.delete_tag, name='delete_tag'),

    path('addcampus/',views.add_campus, name="add_campus"),
    path('editcampus/<str:pk>', views.edit_campus, name='edit_campus'),
    path('deletecampus/<int:pk>/', views.delete_campus, name='delete_campus'),
    
    
    path('adddepartment/',views.add_department, name="add_department"),
    path('editdepartment/<str:pk>',views.edit_department, name="edit_department"),
    path('delete_department/<int:pk>/', views.delete_department, name='delete_department'),

    path('delete/<str:pk>',views.deleteEvent, name="delete"),
    path('deletepic/<str:pk>',views.deletePictures, name="deletepic"),
    path('delete_brochure/<int:pk>/', views.delete_brochure, name='delete_brochure'),
    path('create-event/',views.createEvent, name="create-event"),
    path('edit-event/<str:pk>',views.Edit_Event, name="edit-event"),
    path('singlevent/<str:pk>/',views.singlEvent, name="single-event"),
    path('update-event/<str:pk>/',views.updateEvent, name="update-event"),
    path('ribbon/<str:key>', views.ribbon, name='ribbon'),
    path('change_password/', views.change_password, name='change_password'),
    path('edit/<int:event_id>/<int:pk>/',views.edit_listing, name='edit-event'),

    path('createSpeaker/<str:pk>', views.createSpeaker, name='createSpeaker'),
    path('edit-speaker/<str:pk>/', views.editSpeaker, name='editSpeaker'),
    path('deletespeakerpic/<str:pk>/', views.deleteSpeakerPic, name='deletespeakerpic'),
    path('deleteSpeaker/<str:pk>/', views.deleteSpeaker, name='deleteSpeaker'),


    path('error/404/', views.error_404_view, name='404-error')
     

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

