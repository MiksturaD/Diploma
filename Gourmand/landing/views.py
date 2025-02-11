from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import first

from landing.models import Review, Event, Place, User, GourmandProfile, OwnerProfile


def index(request):
  return render(request, 'landing/index.html')


def main(request):
  return None


@login_required
def profile(request):
    user = request.user

    if user.is_gourmand():
        profile = GourmandProfile.objects.filter(user=user).first()  # Без ошибки, если нет профиля
        if not profile:
            return redirect("index")  # Или можно создать профиль, если так задумано
        return render(request, "gourmands/gourmand_profile.html", {"profile": profile})

    elif user.is_owner():
        profile = OwnerProfile.objects.filter(user=user).first()
        if not profile:
            return redirect("index")
        return render(request, "places/owner_profile.html", {"profile": profile})

    return redirect("index")

@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        if user.is_gourmand():
            profile = GourmandProfile.objects.get(user=user)
            profile.first_name = first_name
            profile.last_name = last_name
            profile.description = request.POST["description"]
            if "image" in request.FILES:
                profile.image = request.FILES["image"]
            profile.save()
        elif user.is_owner():
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        return redirect("profile")

    if user.is_gourmand():
        profile = GourmandProfile.objects.get(user=user)
        return render(request, "gourmands/edit_profile_gourmand.html", {"profile": profile})
    elif user.is_owner():
        return render(request, "places/edit_profile_owner.html", {"user": user})
    return redirect("index")

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST.get("role", "gourmand")  # По умолчанию гурман

        if User.objects.filter(username=username).exists():
            return render(request, "landing/index.html", {"signup_error": "Этот никнэйм занят"})

        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password, role=role)

        # **Гарантированное создание профиля**
        if role == "gourmand":
            GourmandProfile.objects.get_or_create(user=user,
                first_name=first_name,
                last_name=last_name)
        elif role == "owner":
            OwnerProfile.objects.get_or_create(user=user,
                first_name=first_name,
                last_name=last_name)

        login(request, user)
        return redirect("index")
    return redirect("index")

def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "landing/index.html", {"login_error": "Неверные учетные данные"})
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


