from django.shortcuts import render, get_object_or_404

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


def event(request, event_id):
    event_obj= get_object_or_404(Event, pk=event_id)
    return render(request, 'events/event.html', context={'event': event_obj})


def create_event(request):
  return None


def places(request):
  places_list = Place.objects.all()
  return render(request, 'places/places.html', context={'places': places_list})


def place(request, place_id):
    place_obj = get_object_or_404(Place, pk=place_id)
    reviews = Review.objects.filter(place=place_obj)
    context = {
        'place': place_obj,
        'reviews': reviews,
    }
    return render(request, 'places/place.html', context)


def place_reviews(request, place_id):
  place_obj = get_object_or_404(Place, pk=place_id)
  reviews = Review.objects.filter(place=place_obj)
  context = {
    'place': place_obj,
    'reviews': reviews,
  }
  return render(request, 'places/place_reviews.html', context={'place': place_obj, 'reviews': reviews})

def create_places(request):
  return None


def reviews(request):
  review_list = Review.objects.all()
  return render(request, 'review/reviews.html', context={'reviews': review_list})


def review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'review/review.html', {'review': review})

def create_review(request):
  return None


def about(request):
  return None


def contacts(request):
  return render(request, 'landing/contacts.html')


def gourmands(request):
  gourmands_list = Gourmand.objects.all()
  return render(request, 'gourmands/gourmands.html', context={'gourmands': gourmands_list})


def gourmand(request, gourmand_id):
    gourmand_obj = get_object_or_404(Gourmand, pk=gourmand_id)
    context = {'gourmand': gourmand_obj}
    return render(request, 'gourmands/gourmand.html', context)

def gourmand_reviews(request, gourmand_id):
    gourmand_obj = get_object_or_404(Gourmand, pk=gourmand_id)
    reviews = Review.objects.filter(gourmand=gourmand_obj)
    context = {'gourmand': gourmand_obj, 'reviews': reviews}
    return render(request, 'gourmands/gourmand_reviews.html', context)