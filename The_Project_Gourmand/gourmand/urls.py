from django.urls import path

from gourmand import views


urlpatterns = [
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
    path('events', views.events, name='events'),
    path('event/<int:event_id>/', views.event, name='event'),
    path('event/create/', views.create_event, name='create_event'),
    path('places', views.places, name='places'),
    path('place/<int:place_id>/', views.place, name='place'),
    path('places/create/', views.create_places, name='create_places'),
    path('reviews', views.reviews, name='reviews'),
    path('review/<int:review_id>/', views.review, name='review'),
    path('review/create/', views.create_review, name='create_review'),
]