from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import first
import logging
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from landing.forms import SignupForm, PlaceCreateForm, GourmandProfileForm, OwnerProfileForm, ReviewCreateForm, \
    EventCreateForm
from landing.models import Review, Event, Place, User, GourmandProfile, OwnerProfile, ReviewImage, PlaceImage, \
    ReviewVote, EventImage


def index(request):
  return render(request, 'landing/index.html')


def main(request):
  return None

logger = logging.getLogger(__name__)
def signup(request):
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
            return render(request, "auth/signup.html", {"form": form, "errors": form.errors})
    else:
        form = SignupForm()
    return render(request, "auth/signup.html", {"form": form})


def signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "auth/signin.html", {"login_error": "Введите email и пароль"})

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("index")
        return render(request, "auth/signin.html", {"login_error": "Неверные email или пароль"})

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
    events_list = Event.objects.all()

    # Фильтр по заведениям
    place_id = request.GET.get('place')
    if place_id:
        events_list = events_list.filter(places__id=place_id)

    # Сортировка
    sort_by = request.GET.get('sort', 'id')  # По умолчанию по ID
    if sort_by == 'date':
        events_list = events_list.order_by('event_date')
    elif sort_by == 'name':
        events_list = events_list.order_by('name')

    paginator = Paginator(events_list, 12)
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)

    places = Place.objects.all()  # Для выпадающего списка
    return render(request, 'events/events.html', {
        'events': events_page,
        'places': places,
        'current_place': place_id,
        'current_sort': sort_by,
    })


def event(request, event_id):
    event_obj= get_object_or_404(Event, pk=event_id)
    return render(request, 'events/event.html', context={'event': event_obj})


@login_required
def create_event(request):
    if not request.user.is_owner():
        return redirect('index')  # Ограничиваем доступ

    if request.method == "POST":
        print("POST DATA:", request.POST)  # 👀 Вывод данных в консоль
        form = EventCreateForm(request.POST, request.FILES)

        if form.is_valid():
            event = form.save(commit=False)
            event.save()
            form.save_m2m()  # Сохранение связей ManyToMany
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    EventImage.objects.create(event=event, image=image)

            print("Сохраненные места:", event.places.all())  # 👀 Проверяем сохраненные места
            return redirect("events")
        else:
            print("Ошибки формы:", form.errors)  # 👀 Проверяем ошибки формы

    else:
        form = EventCreateForm()

    return render(request, 'events/create.html', {'form': form})


def places(request):
    places_list = Place.objects.all()

    # Сортировка
    sort_by = request.GET.get('sort', 'id')
    if sort_by == 'name':
        places_list = places_list.order_by('name')
    elif sort_by == 'rating':
        places_list = places_list.order_by('-rating')  # По убыванию

    paginator = Paginator(places_list, 12)
    page_number = request.GET.get('page')
    places_page = paginator.get_page(page_number)

    return render(request, 'places/places.html', {
        'places': places_page,
        'user': request.user,
        'current_sort': sort_by,
    })


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
        return redirect("index")

    if request.method == "POST":
        form = PlaceCreateForm(request.POST)
        if form.is_valid():
            place = form.save(commit=False)
            place.owner = request.user  # Привязываем владельца
            place.save()
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    PlaceImage.objects.create(place=place, image=image)
            return redirect("place", place.id)
        return render(request, "places/place_create.html", {"form": form})

    form = PlaceCreateForm()
    return render(request, "places/place_create.html", {"form": form})


@login_required
def edit_place(request, place_id):
    place = get_object_or_404(Place, pk=place_id)

    # Проверяем, что текущий пользователь — владелец заведения
    if not request.user.is_owner() or place.owner != request.user:
        return redirect("index")

    if request.method == "POST":
        form = PlaceCreateForm(request.POST, instance=place)
        if form.is_valid():
            form.save()
            # Обновляем изображения, если загружены новые
            if 'images' in request.FILES:
                # Удаляем старые изображения (опционально, если хочешь заменять)
                place.images.all().delete()
                for image in request.FILES.getlist('images'):
                    PlaceImage.objects.create(place=place, image=image)
            return redirect("place", place.id)
        return render(request, "places/place_edit.html", {"form": form, "place": place})

    form = PlaceCreateForm(instance=place)
    return render(request, "places/place_edit.html", {"form": form, "place": place})


def reviews(request):
    reviews_list = Review.objects.all()

    # Фильтр по заведениям
    place_id = request.GET.get('place')
    if place_id:
        reviews_list = reviews_list.filter(place__id=place_id)

    # Сортировка
    sort_by = request.GET.get('sort', 'id')
    if sort_by == 'date':
        reviews_list = reviews_list.order_by('-review_date')
    elif sort_by == 'name':
        reviews_list = reviews_list.order_by('name')

    paginator = Paginator(reviews_list, 12)
    page_number = request.GET.get('page')
    reviews_page = paginator.get_page(page_number)

    places = Place.objects.all()
    return render(request, 'review/reviews.html', {
        'reviews': reviews_page,
        'places': places,
        'current_place': place_id,
        'current_sort': sort_by,
    })


def review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    user_vote = None
    if request.user.is_authenticated:
        user_vote = ReviewVote.objects.filter(review=review, user=request.user).first()
    return render(request, 'review/review.html', {
        'review': review,
        'user': request.user,
        'user_vote': user_vote,
    })


@login_required
def create_review(request):
    if not request.user.is_gourmand():
        return redirect('index')

    if request.method == "POST":
        form = ReviewCreateForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.gourmand = request.user
            review.save()
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    ReviewImage.objects.create(review=review, image=image)
            return redirect("place", place_id=review.place.id)  # Перенаправляем на страницу заведения
        return render(request, "review/create.html", {"form": form})

    form = ReviewCreateForm()
    return render(request, "review/create.html", {"form": form})

def about(request):
  return None


def contacts(request):
  return render(request, 'landing/contacts.html')


def gourmands(request):
    gourmands_list = GourmandProfile.objects.all()

    # Сортировка
    sort_by = request.GET.get('sort', 'id')
    if sort_by == 'rating':
        gourmands_list = gourmands_list.order_by('-rating')
    elif sort_by == 'experience':
        gourmands_list = gourmands_list.order_by('user__date_joined')
    elif sort_by == 'reviews':
        gourmands_list = gourmands_list.annotate(review_count=Count('user__reviews')).order_by('-review_count')

    paginator = Paginator(gourmands_list, 12)
    page_number = request.GET.get('page')
    gourmands_page = paginator.get_page(page_number)

    return render(request, 'gourmands/gourmands.html', {
        'gourmands': gourmands_page,
        'current_sort': sort_by,
    })

def gourmand(request, user_id):
    gourmand_obj = get_object_or_404(User, pk=user_id)
    return render(request, 'gourmands/gourmand.html', {'gourmand': gourmand_obj})

def gourmand_reviews(request, user_id):
    gourmand_obj = get_object_or_404(User, pk=user_id)
    reviews = Review.objects.filter(gourmand=gourmand_obj)
    return render(request, 'gourmands/gourmand_reviews.html', {'gourmand': gourmand_obj, 'reviews': reviews})


@login_required
def vote_review(request, review_id, vote_type):
    if not request.user.is_gourmand():
        return redirect('index')

    review = get_object_or_404(Review, pk=review_id)
    if vote_type not in ['positive', 'negative']:
        return HttpResponseBadRequest("Недопустимый тип голоса")

    existing_vote = ReviewVote.objects.filter(review=review, user=request.user).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            return redirect('place', place_id=review.place.id)  # Унифицируем с place
        existing_vote.delete()
        if existing_vote.vote_type == 'positive':
            review.positive_rating = max(0, review.positive_rating - 1)
        else:
            review.negative_rating = max(0, review.negative_rating - 1)

    ReviewVote.objects.create(review=review, user=request.user, vote_type=vote_type)
    if vote_type == 'positive':
        review.positive_rating += 1
    else:
        review.negative_rating += 1
    review.save()  # Сохраняем и запускаем пересчёт рейтингов

    return redirect('place', place_id=review.place.id)


