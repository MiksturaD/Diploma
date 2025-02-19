from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import first
import logging
from landing.forms import SignupForm, PlaceCreateForm, GourmandProfileForm, OwnerProfileForm, ReviewCreateForm, \
    EventCreateForm
from landing.models import Review, Event, Place, User, GourmandProfile, OwnerProfile


def index(request):
  return render(request, 'landing/index.html')


def main(request):
  return None

logger = logging.getLogger(__name__)
def signup(request): #TODO: СДЕЛАТЬ РЕДИРРЕКТ НА СТРАНИЦУ ПРОФИЛЯ ПОСЛЕ РЕГИСТРАЦИИ
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                if user.role == "gourmand":
                    GourmandProfile.objects.create(user=user)
                elif user.role == "owner":
                    OwnerProfile.objects.create(user=user)
            except Exception as e:
                logger.error(f"Error creating profile: {e}")
                return render(request, "auth/signup.html", {"form": form, "error": "Ошибка при создании профиля."})
            login(request, user)
            return redirect("profile")
        else:
            print(f"Form errors: {form.errors}")
            return render(request, "auth/signup.html", {"form": form})
    else:
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})


def signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "auth/signin.html", {"login_error": "Введите email и пароль"})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "auth/signin.html", {"login_error": "Пользователь не найден."})

        user = authenticate(request, username=user.email, password=password)  # Используем email
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "auth/signin.html", {"login_error": "Неверные учетные данные"})

    return render(request, "auth/signin.html")


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

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        description = request.POST.get("description")

        if user.is_gourmand():
            profile, _ = GourmandProfile.objects.get_or_create(user=user)
            profile.first_name = first_name
            profile.last_name = last_name
            profile.description = description
            if "image" in request.FILES:
                profile.image = request.FILES["image"]
            profile.save()

        elif user.is_owner():
            profile, _ = OwnerProfile.objects.get_or_create(user=user)
            places_ids = request.POST.getlist("places")
            places = Place.objects.filter(id__in=places_ids)
            profile.places.set(places)
            if "image" in request.FILES:
                profile.image = request.FILES["image"]
            profile.save()

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        return redirect("profile")

    if user.is_gourmand():
        profile = GourmandProfile.objects.filter(user=user).first()
        return render(request, "gourmands/edit_profile_gourmand.html", {"profile": profile})
    elif user.is_owner():
        profile = OwnerProfile.objects.filter(user=user).first()
        all_places = Place.objects.all()
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


@login_required
def create_event(request):
    if not request.user.is_owner():
        return redirect('index')  # Перенаправляем на главную страницу, если пользователь не является владельцем

    if request.method == "POST":
        form = EventCreateForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.save()
            form.save_m2m()  # Сохраняем связанные места
            return redirect("events")
    else:
        form = EventCreateForm()

    return render(request, 'events/create.html', {'form': form})


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

@login_required
def create_review(request):
    if request.user.is_owner():
        return redirect('index')  # Перенаправляем на главную страницу, если пользователь не является гурманом

    if request.method == "POST":
        form = ReviewCreateForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.gourmand = request.user
            review.save()
            return redirect("reviews")
    else:
        form = ReviewCreateForm()

    return render(request, 'review/create.html', {'form': form})

def about(request):
  return None


def contacts(request):
  return render(request, 'landing/contacts.html')


def gourmands(request):
    gourmands_list = GourmandProfile.objects.all()
    return render(request, 'gourmands/gourmands.html', {'gourmands': gourmands_list})

def gourmand(request, user_id):
    gourmand_obj = get_object_or_404(User, pk=user_id)
    return render(request, 'gourmands/gourmand.html', {'gourmand': gourmand_obj})

def gourmand_reviews(request, user_id):
    gourmand_obj = get_object_or_404(User, pk=user_id)
    reviews = Review.objects.filter(gourmand=gourmand_obj)
    return render(request, 'gourmands/gourmand_reviews.html', {'gourmand': gourmand_obj, 'reviews': reviews})


