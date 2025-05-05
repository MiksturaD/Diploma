from datetime import datetime
from django.core.cache import cache
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import first
import logging
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db.models.functions import Lower

from landing.forms import SignupForm, PlaceCreateForm, ReviewCreateForm, \
    EventCreateForm
from landing.models import Review, Event, Place, User, GourmandProfile, OwnerProfile, ReviewImage, PlaceImage, \
    ReviewVote, EventImage, NPSResponse
from django.core.mail import send_mail
from django.http import HttpResponse

from landing.utils import get_reviews_for_last_month, analyze_reviews_with_chatgpt, prepare_reviews_data, get_tag_stats


def index(request):
  return render(request, 'landing/index.html')


def main(request):
  return None

logger = logging.getLogger(__name__)

from django.conf import settings

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
                return render(
                    request,
                    "auth/signup.html",
                    {"form": form, "error": "Ошибка при создании профиля.", "settings": settings}
                )
            login(request, user)
            return redirect("index")
        else:
            print("Form errors:", form.errors)
            print("Form is NOT valid")
            print(form.errors.as_data())
            return render(
                request,
                "auth/signup.html",
                {"form": form, "errors": form.errors, "settings": settings}
            )
    else:
        form = SignupForm()
        print("Form created:", form)
    return render(request, "auth/signup.html", {"form": form, "settings": settings})



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

        # Получаем период из GET-параметра (по умолчанию 1 месяц)
        period = request.GET.get('period', '1m')
        if period == '3m':
            days = 90
        elif period == '6m':
            days = 180
        else:
            days = 30

        today = datetime.today()
        current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = current_month_start - relativedelta(months=1)
        last_month_end = current_month_start - relativedelta(seconds=1)

        # Получаем заведения владельца
        places = Place.objects.filter(owner=user)
        place_stats = {}

        if places.exists():
            for place in places:
                # Общее количество ответов
                total_responses = NPSResponse.objects.filter(review__place=place).count()
                promoters = NPSResponse.objects.filter(review__place=place, score__gte=9).count()
                detractors = NPSResponse.objects.filter(review__place=place, score__lte=6).count()
                nps = (
                    promoters / total_responses * 100 - detractors / total_responses * 100
                ) if total_responses > 0 else 0

                # NPS за текущий месяц
                current_total = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=current_month_start
                ).count()
                current_promoters = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=current_month_start,
                    score__gte=9
                ).count()
                current_detractors = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=current_month_start,
                    score__lte=6
                ).count()
                current_nps = (
                    current_promoters / current_total * 100 - current_detractors / current_total * 100
                ) if current_total > 0 else None

                # NPS за прошлый месяц
                last_total = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=last_month_start,
                    created_at__lte=last_month_end
                ).count()
                last_promoters = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=last_month_start,
                    created_at__lte=last_month_end,
                    score__gte=9
                ).count()
                last_detractors = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=last_month_start,
                    created_at__lte=last_month_end,
                    score__lte=6
                ).count()
                last_nps = (
                    last_promoters / last_total * 100 - last_detractors / last_total * 100
                ) if last_total > 0 else None

                # Топ-теги за всё время
                tag_stats = NPSResponse.objects.filter(review__place=place).values('tags__label').annotate(
                    tag_count=Count('tags__label')
                ).order_by('-tag_count')[:3]
                # Теги за текущий месяц
                current_month_tags = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=current_month_start
                ).values('tags__label').annotate(
                    tag_count=Count('tags__label')
                ).order_by('-tag_count')
                # Теги за прошлый месяц
                last_month_tags = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=last_month_start,
                    created_at__lte=last_month_end
                ).values('tags__label').annotate(
                    tag_count=Count('tags__label')
                ).order_by('-tag_count')

                # Динамика тегов
                tag_dynamics = {}
                for tag in set(
                        [t['tags__label'] for t in current_month_tags] + [t['tags__label'] for t in last_month_tags]):
                    current_count = next((t['tag_count'] for t in current_month_tags if t['tags__label'] == tag), 0)
                    last_count = next((t['tag_count'] for t in last_month_tags if t['tags__label'] == tag), 0)
                    tag_dynamics[tag] = {
                        'current': current_count,
                        'last': last_count,
                        'change': current_count - last_count
                    }

                # Анализ отзывов через ChatGPT
                cache_key = f"review_summary_{place.id}_{period}"
                cached_summary = cache.get(cache_key)

                if cached_summary:
                    summary = cached_summary
                else:
                    reviews = get_reviews_for_last_month(place, days=days)
                    reviews_data = prepare_reviews_data(reviews)
                    summary = analyze_reviews_with_chatgpt(reviews_data, place.name)
                    cache.set(cache_key, summary, timeout=60*60*24)

                # Статистика по тегам за выбранный период
                period_reviews = get_reviews_for_last_month(place, days=days)
                period_tag_stats = get_tag_stats(period_reviews)

                place_stats[place.id] = {
                    'place': place,
                    'nps': nps,
                    'total_responses': total_responses,
                    'current_nps': current_nps,
                    'last_nps': last_nps,
                    'tag_stats': tag_stats,
                    'tag_dynamics': tag_dynamics,
                    'summary': summary,  # Добавляем сводку от ChatGPT
                    'period_tag_stats': period_tag_stats,  # Статистика тегов за выбранный период
                }

        # Средний NPS по всем заведениям
        total_responses = NPSResponse.objects.filter(review__place__owner=user).count()
        total_promoters = NPSResponse.objects.filter(review__place__owner=user, score__gte=9).count()
        total_detractors = NPSResponse.objects.filter(review__place__owner=user, score__lte=6).count()
        average_nps = (
            total_promoters / total_responses * 100 - total_detractors / total_responses * 100
        ) if total_responses > 0 else 0

        context = {
            'user': user,
            'profile': profile,
            'place_stats': place_stats,
            'current_month': current_month_start.strftime('%Y-%m'),
            'last_month': last_month_start.strftime('%Y-%m'),
            'average_nps': average_nps,
            'period': period,  # Передаём период для шаблона
        }
        return render(request, "places/owner_profile.html", context)

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
            profile.description = description
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
    place_slug = request.GET.get('place')  # Обновляем
    if place_slug:
        events_list = events_list.filter(place__slug=place_slug)  # Обновляем

    # Сортировка
    sort_by = request.GET.get('sort', 'id')
    if sort_by == 'date':
        events_list = events_list.order_by('event_date')  # Исправляем event_datetime на event_date
    elif sort_by == 'name':
        events_list = events_list.order_by('name')

    paginator = Paginator(events_list, 12)
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)

    places = Place.objects.all()
    return render(request, 'events/events.html', {
        'events': events_page,
        'places': places,
        'current_place': place_slug,  # Обновляем
        'current_sort': sort_by,
    })


def event(request, slug):
    event_obj= get_object_or_404(Event, slug=slug)
    return render(request, 'events/event.html', context={'event': event_obj})


@login_required
def create_event(request):
    if not request.user.is_owner():
        return redirect("index")

    if request.method == "POST":
        form = EventCreateForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.owner = request.user
            event.save()
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    EventImage.objects.create(event=event, image=image)
            return redirect("event", slug=event.slug)
        return render(request, "events/create.html", {"form": form})

    form = EventCreateForm()
    return render(request, "events/create.html", {"form": form})


from django.db.models import Q
from django.core.paginator import Paginator

def places(request):
    query = request.GET.get('q', '').strip() # Поисковый запрос
    sort_by = request.GET.get('sort', 'id')

    places_list = Place.objects.all()

    # Фильтрация по поисковому запросу
    if query:
        places_list = places_list.filter(Q(name__icontains=query))


    # Сортировка
    if sort_by == 'name':
        places_list = places_list.order_by('name')
    elif sort_by == 'rating':
        places_list = places_list.order_by('-rating')
    else:
        places_list = places_list.order_by('id')

    # Пагинация
    paginator = Paginator(places_list, 12)
    page_number = request.GET.get('page')
    places_page = paginator.get_page(page_number)

    return render(request, 'places/places.html', {
        'places': places_page,
        'user': request.user,
        'current_sort': sort_by,
        'query': query,
    })


def place(request, slug):
    place_obj = get_object_or_404(Place, slug=slug)
    reviews = Review.objects.filter(place=place_obj)

    context = {
        'place': place_obj,
        'reviews': reviews,
    }

    if request.user.is_authenticated and place_obj.owner == request.user:
        today = datetime.today()
        current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = current_month_start - relativedelta(months=1)
        last_month_end = current_month_start - relativedelta(seconds=1)

        total_responses = NPSResponse.objects.filter(review__place=place_obj).count()
        promoters = NPSResponse.objects.filter(review__place=place_obj, score__gte=9).count()
        detractors = NPSResponse.objects.filter(review__place=place_obj, score__lte=6).count()
        nps = (promoters / total_responses * 100 - detractors / total_responses * 100) if total_responses > 0 else 0

        current_total = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=current_month_start
        ).count()
        current_promoters = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=current_month_start,
            score__gte=9
        ).count()
        current_detractors = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=current_month_start,
            score__lte=6
        ).count()
        current_nps = (
                    current_promoters / current_total * 100 - current_detractors / current_total * 100) if current_total > 0 else None

        last_total = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=last_month_start,
            created_at__lte=last_month_end
        ).count()
        last_promoters = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=last_month_start,
            created_at__lte=last_month_end,
            score__gte=9
        ).count()
        last_detractors = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=last_month_start,
            created_at__lte=last_month_end,
            score__lte=6
        ).count()
        last_nps = (last_promoters / last_total * 100 - last_detractors / last_total * 100) if last_total > 0 else None

        tag_stats = NPSResponse.objects.filter(review__place=place_obj).values('tags__label').annotate(
            tag_count=Count('tags__label')
        ).order_by('-tag_count')[:3]
        current_month_tags = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=current_month_start
        ).values('tags__label').annotate(
            tag_count=Count('tags__label')
        ).order_by('-tag_count')
        last_month_tags = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=last_month_start,
            created_at__lte=last_month_end
        ).values('tags__label').annotate(
            tag_count=Count('tags__label')
        ).order_by('-tag_count')

        tag_dynamics = {}
        for tag in set([t['tags__label'] for t in current_month_tags] + [t['tags__label'] for t in last_month_tags]):
            current_count = next((t['tag_count'] for t in current_month_tags if t['tags__label'] == tag), 0)
            last_count = next((t['tag_count'] for t in last_month_tags if t['tags__label'] == tag), 0)
            tag_dynamics[tag] = {
                'current': current_count,
                'last': last_count,
                'change': current_count - last_count
            }

        context.update({
            'nps': nps,
            'total_responses': total_responses,
            'current_nps': current_nps,
            'last_nps': last_nps,
            'tag_stats': tag_stats,
            'tag_dynamics': tag_dynamics,
            'current_month': current_month_start.strftime('%Y-%m'),
            'last_month': last_month_start.strftime('%Y-%m'),
        })

    return render(request, 'places/place.html', context)



def place_reviews(request, slug):
  place_obj = get_object_or_404(Place, slug=slug)
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
            return redirect("place", slug=place.slug)
        return render(request, "places/place_create.html", {"form": form})

    form = PlaceCreateForm()
    return render(request, "places/place_create.html", {"form": form})


@login_required
def edit_place(request, slug):
    place = get_object_or_404(Place, slug=slug)

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
            return redirect("place", slug)
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
    else:
        reviews_list = reviews_list.order_by('id')


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


def review(request, slug):
    review = get_object_or_404(Review, slug=slug)
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

    place_id = request.GET.get('place')
    initial_data = {}
    if place_id:
        try:
            place = Place.objects.get(id=place_id)
            initial_data['place'] = place
        except Place.DoesNotExist:
            pass

    if request.method == "POST":
        form = ReviewCreateForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.gourmand = request.user
            review.save()
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    ReviewImage.objects.create(review=review, image=image)
            return redirect('review', slug=review.slug)  # Обновляем
        else:
            print(form.errors)
            return render(request, "review/create.html", {"form": form})

    form = ReviewCreateForm(initial=initial_data)
    return render(request, "review/create.html", {"form": form})

def about(request):
  return None


def contacts(request):
  return render(request, 'landing/contacts.html')


def gourmands(request):
    # Фильтруем только гурманов
    gourmands_list = GourmandProfile.objects.select_related('user').filter(user__role='gourmand')

    # Сортировка
    sort_by = request.GET.get('sort', 'id')
    if sort_by == 'rating':
        gourmands_list = gourmands_list.order_by('-rating')
    elif sort_by == 'experience':
        gourmands_list = gourmands_list.order_by('user__date_joined')
    elif sort_by == 'reviews':
        gourmands_list = gourmands_list.annotate(review_count=Count('user__reviews')).order_by('-review_count')
    else:
        gourmands_list = gourmands_list.order_by('id')

    paginator = Paginator(gourmands_list, 12)
    page_number = request.GET.get('page')
    gourmands_page = paginator.get_page(page_number)

    return render(request, 'gourmands/gourmands.html', {
        'gourmands': gourmands_page,
        'current_sort': sort_by,
    })

def gourmand(request, slug):
    gourmand_obj = get_object_or_404(User, slug=slug)
    return render(request, 'gourmands/gourmand.html', {'gourmand': gourmand_obj})

def gourmand_reviews(request, slug):
    gourmand_obj = get_object_or_404(User, slug=slug)
    reviews = Review.objects.filter(gourmand=gourmand_obj)
    return render(request, 'gourmands/gourmand_reviews.html', {'gourmand': gourmand_obj, 'reviews': reviews})


@login_required
def vote_review(request, slug, vote_type):
    if not request.user.is_gourmand():
        return redirect('index')

    review = get_object_or_404(Review, slug=slug)  # Обновляем
    if vote_type not in ['positive', 'negative']:
        return HttpResponseBadRequest("Недопустимый тип голоса")

    if review.gourmand == request.user:
        return redirect('review', slug=review.slug)  # Обновляем

    existing_vote = ReviewVote.objects.filter(review=review, user=request.user).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            return redirect('review', slug=review.slug)  # Обновляем
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
    review.save()

    return redirect('review', slug=review.slug)  # Обновляем


def test_email(request):
    try:
        send_mail(
            subject='Тестовое письмо от Проекта Гурман',
            message='Это тестовое письмо. Если ты его получил, значит всё работает!',
            from_email=None,  # Используется DEFAULT_FROM_EMAIL из settings.py
            recipient_list=['thereal@mail.ru'],  # Укажи свой тестовый email
        )
        return HttpResponse("Письмо успешно отправлено!")
    except Exception as e:
        return HttpResponse(f"Ошибка при отправке письма: {str(e)}")