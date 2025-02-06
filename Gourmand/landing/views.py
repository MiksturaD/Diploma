from django.shortcuts import render

from landing.models import Review, Event, Place, Gourmand


def index(request):
  return render(request, 'landing/index.html')


def main(request):
  return None


def edit_profile(request):
  return None


def signup(request):
  return None


def signin(request):
  return None


def signout(request):
  return None


def profile(request):
  return None


def events(request):
  event_list = Event.objects.all()
  return render(request, 'events/events.html', context={'events': event_list})


def event(request):
  return None


def create_event(request):
  return None


def places(request):
  places_list = Place.objects.all()
  return render(request, 'places/places.html', context={'places': places_list})


def place(request):
  return None


def create_places(request):
  return None


def reviews(request):
  review_list = Review.objects.all()
  return render(request, 'landing/index.html', context={'reviews': review_list})


def review(request):
  return None


def create_review(request):
  return None


def about(request):
  return None


def contacts(request):
  return None


def gourmands(request):
  gourmands_list = Gourmand.objects.all()
  return render(request, 'gourmands/gourmands.html', context={'gourmands': gourmands_list})


def gourmand(request):
  return None