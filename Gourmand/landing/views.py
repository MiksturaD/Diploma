from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import first

from landing.forms import SignupForm, PlaceCreateForm, GourmandProfileForm, OwnerProfileForm
from landing.models import Review, Event, Place, User, GourmandProfile, OwnerProfile


def index(request):
  return render(request, 'landing/index.html')


def main(request):
  return None


def signup(request):
    if request.method == "POST":
        user_form = SignupForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            if user.role == "gourmand":
                gourmand_profile_form = GourmandProfileForm(request.POST, request.FILES)
                if gourmand_profile_form.is_valid():
                    gourmand_profile = gourmand_profile_form.save(commit=False)
                    gourmand_profile.user = user
                    gourmand_profile.save()
            elif user.role == "owner":
                owner_profile_form = OwnerProfileForm(request.POST, request.FILES)
                if owner_profile_form.is_valid():
                    owner_profile = owner_profile_form.save(commit=False)
                    owner_profile.user = user
                    owner_profile.save()
            login(request, user)
            return redirect("index")
        else:
            return render(request, "landing/index.html", {"user_form": user_form})
    else:
        user_form = SignupForm()
    return render(request, 'landing/index.html', {'user_form': user_form})


def signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "landing/index.html", {"login_error": "Введите email и пароль"})

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "landing/index.html", {"login_error": "Неверные учетные данные"})

    return redirect("index")


@login_required
def profile(request):
    user = request.user

    if user.is_gourmand():
        profile, _ = GourmandProfile.objects.get_or_create(user=user)
        return render(request, "gourmands/gourmand_profile.html", {"profile": profile})

    elif user.is_owner():
        profile, _ = OwnerProfile.objects.get_or_create(user=user)
        return render(request, "places/owner_profile.html", {"profile": profile})

    return redirect("index")


@login_required
def edit_profile(request):
    user = request.user
    if user.is_gourmand():
        profile = GourmandProfile.objects.get_or_create(user=user)[0]
        return render(request, "gourmands/edit_profile_gourmand.html", {"profile": profile})
    elif user.is_owner():
        profile = OwnerProfile.objects.get_or_create(user=user)[0]
        all_places = Place.objects.all()
        if request.method == "POST":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            description = request.POST.get("description")
            places_ids = request.POST.getlist("places")
            places = Place.objects.filter(id__in=places_ids)
            image = request.FILES.get("image")

            profile.first_name = first_name
            profile.last_name = last_name
            profile.description = description
            profile.places.set(places)
            if image:
                profile.image = image
            profile.save()

            user.first_name = first_name
            user.last_name = last_name
            user.save()

            return redirect("profile")
        return render(request, "places/edit_profile_owner.html", {"profile": profile, "all_places": all_places})
    return redirect("index")


def signout(request):
    logout(request)
    return redirect("index")

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

@login_required
def create_places(request):
    if not request.user.is_owner():
        print('не прошла проверка атата')
        return redirect("index")
    print('Прошла проверка на владельца')

    if request.method == "POST":
        print('запуск формы')
        form = PlaceCreateForm(request.POST, request.FILES)
        if form.is_valid():
            place = form.save()
            return redirect("place", place.id)
            print('не прошла проверка тут')
        else:
            print('не прошла проверка и тут')
            return render(request, "places/place_create.html", {"form": form})
    else:
        print('не прошла проверка совсем')
        form = PlaceCreateForm()
        return render(request, "places/place_create.html", {"form": form})


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
  gourmands_list = User.objects.all()
  return render(request, 'gourmands/gourmands.html', context={'gourmands': gourmands_list})


def gourmand(request, user_id):
    gourmand_obj = get_object_or_404(User, pk=user_id)
    context = {'gourmand': gourmand_obj}
    return render(request, 'gourmands/gourmand.html', context)

def gourmand_reviews(request, user_id):
    gourmand_obj = get_object_or_404(User, pk=user_id)
    reviews = Review.objects.filter(gourmand=gourmand_obj)
    context = {'gourmand': gourmand_obj, 'reviews': reviews}
    return render(request, 'gourmands/gourmand_reviews.html', context)


