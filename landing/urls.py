from django.urls import path
from landing import views

urlpatterns = [
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),
    path('profile/', views.profile, name='profile'),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('events/', views.events, name='events'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<slug:slug>/', views.event, name='event'),

    path('places/', views.places, name='places'),
    path('places/create/', views.create_places, name='create_places'),
    path('place/<slug:slug>/', views.place, name='place'),
    path('place/<slug:slug>/reviews/', views.place_reviews, name='place_reviews'),
    path('place/<slug:slug>/edit/', views.edit_place, name='edit_place'),

    path('reviews/', views.reviews, name='reviews'),
    path('reviews/create/', views.create_review, name='create_review'),
    path('reviews/<slug:slug>/vote/<str:vote_type>/', views.vote_review, name='vote_review'),
    path('reviews/<slug:slug>/', views.review, name='review'),
    path('contacts/', views.contacts, name='contacts'),
    path('gourmands/', views.gourmands, name='gourmands'),
    path('gourmands/<slug:slug>/', views.gourmand, name='gourmand'),
    path('gourmands/<slug:slug>/reviews/', views.gourmand_reviews, name='gourmand_reviews'),
    path('profile/<int:place_id>/', views.analyze_reviews, name='analyze_reviews'),
]