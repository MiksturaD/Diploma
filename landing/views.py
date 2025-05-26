from datetime import datetime # Импортируем класс datetime для работы с датами и временем
from django.core.cache import cache # Импортируем систему кэширования Django для временного хранения данных
from dateutil.relativedelta import relativedelta # Импортируем relativedelta для удобных манипуляций с датами (например, вычитание месяцев)
from django.conf import settings # Импортируем объект settings для доступа к настройкам проекта Django
from django.contrib.auth import authenticate, login, logout # Функции для аутентификации, входа и выхода пользователей
from django.contrib.auth.decorators import login_required # Декоратор для ограничения доступа к представлениям только для авторизованных пользователей
from django.db.models import Count, Avg # Функции агрегации Django ORM для подсчета и вычисления среднего значения
from django.http import HttpResponseBadRequest # Класс для ответа с HTTP статусом 400 (неверный запрос)
from django.shortcuts import render, get_object_or_404, redirect # Стандартные шорткаты Django: render для отображения шаблонов, get_object_or_404 для получения объекта или ошибки 404, redirect для перенаправления
import logging # Стандартная библиотека Python для логирования событий
from django.core.paginator import Paginator # Класс для разбиения длинных списков объектов на страницы (пагинация)
from django.views.decorators.http import require_POST # Декоратор для ограничения доступа к представлению только POST-запросами
from django.db.models import Q # Объект Q для создания сложных ORM-запросов с условиями ИЛИ/И
from django.urls import reverse # Функция для получения URL по имени маршрута (name в urls.py)
from django.contrib import messages # Функция для отправки сообщений

from django.utils import timezone # Утилиты Django для работы с часовыми поясами, предпочтительнее datetime.datetime
# from dateutil.relativedelta import relativedelta # Этот импорт уже был выше, дублируется

from landing.forms import SignupForm, PlaceCreateForm, ReviewCreateForm, \
    EventCreateForm # Импортируем кастомные формы из приложения 'landing'
from landing.models import Review, Event, Place, User, GourmandProfile, OwnerProfile, ReviewImage, PlaceImage, \
    ReviewVote, EventImage, NPSResponse # Импортируем модели из приложения 'landing'
from django.core.mail import send_mail # Функция для отправки электронной почты
from django.http import HttpResponse # Класс для простого HTTP-ответа (например, для тестовых сообщений)

from landing.utils import get_reviews_for_last_month, analyze_reviews_with_chatgpt, prepare_reviews_data, get_tag_stats # Импортируем вспомогательные функции из utils.py

# Представление для главной страницы (возможно, лендинга)
def index(request):
  return render(request, 'landing/index.html') # Отображает HTML-шаблон 'landing/index.html'

logger = logging.getLogger(__name__) # Инициализация логгера для текущего модуля (views.py)

# Представление для регистрации нового пользователя
def signup(request):
    if request.method == "POST": # Проверяет, был ли запрос отправлен методом POST (т.е. пользователь отправил форму)
        form = SignupForm(request.POST) # Создает экземпляр формы SignupForm с данными из POST-запроса
        if form.is_valid(): # Проверяет, прошли ли данные формы валидацию (например, корректность email, совпадение паролей)
            print("DEBUG: Form is valid") # Отладочное сообщение: форма валидна
            user = form.save() # Сохраняет данные пользователя в базу данных и возвращает созданный объект User
            print("DEBUG: User created:", user, "is_active:", user.is_active) # Отладочное сообщение: пользователь создан, его статус активности
            try: # Блок для обработки возможных ошибок при создании профиля (GourmandProfile или OwnerProfile)
                if user.role == "gourmand": # Если роль нового пользователя - "gourmand" (гурман)
                    print("DEBUG: Checking GourmandProfile for user", user) # Отладочное сообщение: проверка профиля гурмана
                    if not GourmandProfile.objects.filter(user=user).exists(): # Если профиль гурмана для этого пользователя еще не существует
                        print("DEBUG: Creating GourmandProfile") # Отладочное сообщение: создание профиля гурмана
                        GourmandProfile.objects.create(user=user) # Создает связанный объект GourmandProfile
                    else: # Если профиль гурмана уже существует (маловероятно при новой регистрации, но проверка на всякий случай)
                        print("DEBUG: GourmandProfile already exists") # Отладочное сообщение
                elif user.role == "owner": # Если роль нового пользователя - "owner" (владелец заведения)
                    print("DEBUG: Checking OwnerProfile for user", user) # Отладочное сообщение: проверка профиля владельца
                    if not OwnerProfile.objects.filter(user=user).exists(): # Если профиль владельца для этого пользователя еще не существует
                        print("DEBUG: Creating OwnerProfile") # Отладочное сообщение: создание профиля владельца
                        OwnerProfile.objects.create(user=user) # Создает связанный объект OwnerProfile
                    else: # Если профиль владельца уже существует
                        print("DEBUG: OwnerProfile already exists") # Отладочное сообщение
            except Exception as e: # Ловит любые исключения, возникшие при создании профиля
                print("DEBUG: Error creating profile:", str(e)) # Отладочное сообщение об ошибке
                logger.error(f"Error creating profile: {e}") # Записывает ошибку в лог
                return render( # Возвращает страницу регистрации с формой и сообщением об ошибке
                    request,
                    "auth/signup.html",
                    {"form": form, "error": f"Ошибка при создании профиля: {str(e)}", "settings": settings}
                )
            login(request, user) # Автоматически аутентифицирует и логинит пользователя после успешной регистрации
            print("DEBUG: User authenticated:", request.user.is_authenticated) # Отладочное сообщение: статус аутентификации
            print("DEBUG: Redirecting to profile") # Отладочное сообщение: перенаправление на профиль
            return redirect("profile") # Перенаправляет пользователя на страницу его профиля (URL с именем 'profile')
        else: # Если данные формы не прошли валидацию
            print("DEBUG: Form errors:", form.errors) # Отладочное сообщение: ошибки формы
            print("DEBUG: Form is NOT valid") # Отладочное сообщение: форма не валидна
            print(form.errors.as_data()) # Выводит детальную информацию об ошибках валидации формы (полезно для отладки)
            return render( # Возвращает страницу регистрации с той же формой, но теперь с сообщениями об ошибках
                request,
                "auth/signup.html",
                {"form": form, "errors": form.errors, "settings": settings}
            )
    else: # Если запрос был не POST (например, GET - первое открытие страницы регистрации)
        form = SignupForm() # Создает пустой экземпляр формы SignupForm
        print("DEBUG: Form created:", form) # Отладочное сообщение: форма создана
    return render(request, "auth/signup.html", {"form": form, "settings": settings}) # Отображает страницу регистрации с пустой (или ранее заполненной с ошибками) формой

# Представление для входа пользователя в систему
def signin(request):
    if request.method == "POST": # Если пользователь отправил форму входа
        email = request.POST.get("email") # Получает email из POST-данных
        password = request.POST.get("password") # Получает пароль из POST-данных

        if not email or not password: # Проверяет, что оба поля (email и пароль) были переданы
            return render(request, "auth/signin.html", {"login_error": "Введите email и пароль"}) # Возвращает ошибку, если что-то не введено

        user = authenticate(request, username=email, password=password) # Пытается аутентифицировать пользователя с предоставленными email и паролем
        if user: # Если аутентификация прошла успешно (пользователь найден и пароль верный)
            login(request, user) # Логинит пользователя в систему (создает сессию)
            return redirect("index") # Перенаправляет на главную страницу (URL с именем 'index')
        # Если аутентификация не удалась (неверный email или пароль)
        return render(request, "auth/signin.html", {"login_error": "Неверные email или пароль"}) # Возвращает страницу входа с сообщением об ошибке

    return render(request, "auth/signin.html") # Если метод GET, просто отображает страницу входа

# Представление для отображения профиля пользователя. Доступно только авторизованным пользователям.
@login_required # Декоратор, требующий аутентификации пользователя
def profile(request):
    user = request.user # Получает объект текущего авторизованного пользователя

    if user.is_gourmand(): # Проверяет, является ли пользователь гурманом (через метод модели User)
        gourmand_profile_obj, _ = GourmandProfile.objects.get_or_create(user=user) # Получает или создает профиль гурмана для пользователя
        return render(request, "gourmands/gourmand_profile.html", {"profile": gourmand_profile_obj}) # Отображает шаблон профиля гурмана

    elif user.is_owner(): # Проверяет, является ли пользователь владельцем заведения
        owner_profile_obj, _ = OwnerProfile.objects.get_or_create(user=user) # Получает или создает профиль владельца для пользователя

        period = request.GET.get('period', '1m') # Получает параметр 'period' из GET-запроса (по умолчанию '1m' - 1 месяц)
        sort_by = request.GET.get('sort_by', 'name') # Получает параметр сортировки 'sort_by' (по умолчанию 'name' - по названию)

        if period == '3m': # Если выбран период 3 месяца
            days = 90 # Устанавливаем количество дней для фильтрации
        elif period == '6m': # Если выбран период 6 месяцев
            days = 180 # Устанавливаем количество дней
        else: # '1m' или значение по умолчанию
            days = 30 # Устанавливаем 30 дней

        today = timezone.now() # Текущая дата и время с учетом часового пояса
        current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0) # Начало текущего месяца
        last_month_start = current_month_start - relativedelta(months=1) # Начало прошлого месяца
        # Корректное определение конца прошлого месяца (до начала текущего месяца, не включая его)
        last_month_end = current_month_start - timezone.timedelta(microseconds=1)

        places_query = Place.objects.filter(owner=user) # Изначальный queryset для заведений, принадлежащих текущему владельцу

        # Применение сортировки к списку заведений
        if sort_by == 'rating': # Если сортировка по рейтингу
            places_query = places_query.order_by('-rating') # Сортировка по убыванию рейтинга (от большего к меньшему)
        elif sort_by == 'reviews': # Если сортировка по количеству отзывов
            # Аннотируем (добавляем вычисляемое поле) количество отзывов для каждого заведения и сортируем по нему
            places_query = places_query.annotate(num_reviews_calculated=Count('review')).order_by('-num_reviews_calculated')
        else: # 'name' (по умолчанию) или любое другое значение
            places_query = places_query.order_by('name') # Сортировка по названию заведения (по алфавиту)

        place_stats_data = {} # Словарь для хранения статистики по каждому заведению владельца

        if places_query.exists(): # Если у владельца есть заведения
            for place in places_query: # Итерация по каждому заведению
                # Расчет общего NPS для заведения
                total_responses = NPSResponse.objects.filter(review__place=place).count() # Общее количество NPS ответов
                promoters = NPSResponse.objects.filter(review__place=place, score__gte=9).count() # Количество "промоутеров" (оценка 9-10)
                detractors = NPSResponse.objects.filter(review__place=place, score__lte=6).count() # Количество "детракторов" (оценка 0-6)
                nps = ( # Расчет NPS (Net Promoter Score)
                    (promoters / total_responses * 100) - (detractors / total_responses * 100)
                ) if total_responses > 0 else 0 # Расчет, если есть ответы, иначе NPS = 0

                # Расчет NPS за текущий месяц
                current_total = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=current_month_start # Ответы, созданные начиная с начала текущего месяца
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
                current_nps = ( # Расчет NPS за текущий месяц
                    (current_promoters / current_total * 100) - (current_detractors / current_total * 100)
                ) if current_total > 0 else None # None, если нет ответов в текущем месяце

                # Расчет NPS за прошлый месяц
                last_total = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=last_month_start, # Ответы, созданные начиная с начала прошлого месяца
                    created_at__lte=last_month_end    # и до конца прошлого месяца
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
                last_nps = ( # Расчет NPS за прошлый месяц
                    (last_promoters / last_total * 100) - (last_detractors / last_total * 100)
                ) if last_total > 0 else None # None, если нет ответов в прошлом месяце

                # Статистика по тегам (топ-3 за все время)
                tag_stats_list = NPSResponse.objects.filter(review__place=place).values('tags__label').annotate( # Группировка по меткам тегов
                    tag_count=Count('tags__label') # Подсчет количества каждого тега
                ).order_by('-tag_count')[:3] # Сортировка по убыванию количества и выбор первых трех

                # Статистика по тегам за текущий месяц
                current_month_tags_list = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=current_month_start
                ).values('tags__label').annotate(
                    tag_count=Count('tags__label')
                ).order_by('-tag_count')

                # Статистика по тегам за прошлый месяц
                last_month_tags_list = NPSResponse.objects.filter(
                    review__place=place,
                    created_at__gte=last_month_start,
                    created_at__lte=last_month_end
                ).values('tags__label').annotate(
                    tag_count=Count('tags__label')
                ).order_by('-tag_count')

                tag_dynamics_dict = {} # Словарь для хранения динамики тегов (изменение количества упоминаний)
                # Собираем все уникальные теги, которые встречались в текущем или прошлом месяце
                all_tags_for_dynamics = set( # Используем set для автоматического удаления дубликатов
                    [t['tags__label'] for t in current_month_tags_list if t['tags__label']] + # Теги текущего месяца (исключая None)
                    [t['tags__label'] for t in last_month_tags_list if t['tags__label']]      # Теги прошлого месяца (исключая None)
                )
                for tag_label in all_tags_for_dynamics: # Для каждого уникального тега
                    # Находим количество упоминаний в текущем месяце (0, если тег не найден)
                    current_count = next((t['tag_count'] for t in current_month_tags_list if t['tags__label'] == tag_label), 0)
                    # Находим количество упоминаний в прошлом месяце (0, если тег не найден)
                    last_count = next((t['tag_count'] for t in last_month_tags_list if t['tags__label'] == tag_label), 0)
                    tag_dynamics_dict[tag_label] = { # Сохраняем данные по тегу
                        'current': current_count, # Количество в текущем месяце
                        'last': last_count,       # Количество в прошлом месяце
                        'change': current_count - last_count # Изменение (динамика)
                    }

                # Получение отзывов за выбранный период (1, 3 или 6 месяцев)
                period_reviews_qs = get_reviews_for_last_month(place, days=days)
                # Получение статистики по тегам для этих отзывов
                period_tag_stats_dict = get_tag_stats(period_reviews_qs)

                # ---> НАЧАЛО: ИЗВЛЕЧЕНИЕ СВОДКИ ИЗ КЭША <---
                summary_cache_key = f"review_summary_{place.id}_{period}" # Формируем ключ для кэша (уникальный для заведения и периода)
                summary_from_cache = cache.get(summary_cache_key) # Пытаемся получить сводку из кэша
                logger.debug(f"PROFILE: For place {place.name} (ID: {place.id}), period {period}, trying cache key {summary_cache_key}. Found: {summary_from_cache is not None}") # Логируем попытку получения из кэша
                # ---> КОНЕЦ: ИЗВЛЕЧЕНИЕ СВОДКИ ИЗ КЭША <---

                place_stats_data[place.id] = { # Сохраняем всю собранную статистику для данного заведения
                    'place': place, # Объект заведения
                    'nps': nps, # Общий NPS
                    'total_responses': total_responses, # Общее количество NPS ответов
                    'current_nps': current_nps, # NPS за текущий месяц
                    'last_nps': last_nps, # NPS за прошлый месяц
                    'tag_stats': tag_stats_list, # Топ-3 тегов за все время
                    'tag_dynamics': tag_dynamics_dict, # Динамика тегов (текущий vs прошлый месяц)
                    'period_tag_stats': period_tag_stats_dict, # Статистика тегов за выбранный период (1/3/6 мес)
                    'summary': summary_from_cache,  # <--- ДОБАВЛЯЕМ СВОДКУ (полученную из кэша) В КОНТЕКСТ ЗАВЕДЕНИЯ
                }

        # Расчет среднего NPS по всем заведениям владельца
        avg_nps_total_responses = NPSResponse.objects.filter(review__place__owner=user).count() # Всего NPS ответов по всем заведениям владельца
        avg_nps_total_promoters = NPSResponse.objects.filter(review__place__owner=user, score__gte=9).count() # Всего промоутеров
        avg_nps_total_detractors = NPSResponse.objects.filter(review__place__owner=user, score__lte=6).count() # Всего детракторов
        average_nps_calculated = ( # Расчет среднего NPS
            (avg_nps_total_promoters / avg_nps_total_responses * 100) - (avg_nps_total_detractors / avg_nps_total_responses * 100)
        ) if avg_nps_total_responses > 0 else 0 # Расчет, если есть ответы, иначе 0

        context = { # Формируем контекст для передачи в шаблон
            'user': user, # Текущий пользователь
            'profile': owner_profile_obj, # Профиль владельца
            'place_stats': place_stats_data, # Статистика по каждому заведению
            'current_month': current_month_start.strftime('%B %Y'), # Текущий месяц и год в формате "Май 2025"
            'last_month': last_month_start.strftime('%B %Y'), # Прошлый месяц и год
            'average_nps': average_nps_calculated, # Средний NPS по всем заведениям
            'period': period, # Выбранный период для отображения (чтобы сохранить состояние фильтра)
            'sort_by': sort_by, # Выбранный параметр сортировки (для сохранения состояния)
        }
        return render(request, "places/owner_profile.html", context) # Отображаем шаблон профиля владельца с контекстом

    # Если пользователь не гурман и не владелец (например, администратор или другая роль, не предусмотренная здесь)
    return redirect("index") # Перенаправляем на главную страницу

# Представление для редактирования профиля пользователя. Доступно только авторизованным.
@login_required
def edit_profile(request):
    user = request.user # Текущий авторизованный пользователь

    if request.method == "POST": # Если пользователь отправил форму редактирования
        first_name = request.POST.get("first_name") # Получаем имя из формы
        last_name = request.POST.get("last_name") # Получаем фамилию из формы
        description = request.POST.get("description") # Получаем описание из формы

        if user.is_gourmand(): # Если пользователь - гурман
            profile, _ = GourmandProfile.objects.get_or_create(user=user) # Получаем или создаем профиль гурмана
            profile.first_name = first_name # Обновляем имя в профиле
            profile.last_name = last_name # Обновляем фамилию в профиле
            profile.description = description # Обновляем описание в профиле
            if "image" in request.FILES: # Если в запросе есть загруженный файл изображения
                profile.image = request.FILES["image"] # Сохраняем изображение в профиле
            profile.save() # Сохраняем изменения профиля гурмана

        elif user.is_owner(): # Если пользователь - владелец
            profile, _ = OwnerProfile.objects.get_or_create(user=user) # Получаем или создаем профиль владельца
            # places_ids = request.POST.getlist("places") # Получаем список ID заведений, связанных с владельцем (сейчас не используется, но может быть полезно)
            # places = Place.objects.filter(id__in=places_ids) # Получаем объекты заведений по их ID
            # profile.places.set(places) # Устанавливаем связь профиля с выбранными заведениями (если бы была такая связь ManyToMany в OwnerProfile)
            profile.description = description # Обновляем описание в профиле владельца
            if "image" in request.FILES: # Если загружено изображение
                profile.image = request.FILES["image"] # Сохраняем его
            profile.save() # Сохраняем изменения профиля владельца

        user.first_name = first_name # Обновляем имя в основной модели User
        user.last_name = last_name # Обновляем фамилию в основной модели User
        user.save() # Сохраняем изменения в User

        return redirect("profile") # Перенаправляем на страницу профиля

    # Если метод GET (первое открытие страницы редактирования)
    if user.is_gourmand(): # Если пользователь - гурман
        profile = GourmandProfile.objects.filter(user=user).first() # Получаем профиль гурмана (first(), чтобы избежать ошибки, если нет)
        return render(request, "gourmands/edit_profile_gourmand.html", {"profile": profile}) # Отображаем форму редактирования для гурмана
    elif user.is_owner(): # Если пользователь - владелец
        profile = OwnerProfile.objects.filter(user=user).first() # Получаем профиль владельца
        all_places = Place.objects.all() # Получаем все заведения (возможно, для выбора связанных заведений, но сейчас не используется в логике POST)
        return render(request, "places/edit_profile_owner.html", {"profile": profile, "all_places": all_places}) # Отображаем форму для владельца

    return redirect("index") # Если роль не определена, перенаправляем на главную

# Представление для выхода пользователя из системы
def signout(request):
    logout(request) # Выполняет выход пользователя (удаляет сессию)
    return redirect("index") # Перенаправляет на главную страницу

# Представление для отображения списка всех событий
def events(request):
    events_list = Event.objects.all() # Получает все объекты Event из базы данных

    # Фильтр по заведению (если параметр 'place' передан в GET-запросе)
    place_slug = request.GET.get('place')  # Получаем слаг заведения из GET-параметра
    if place_slug: # Если слаг заведения указан
        events_list = events_list.filter(place__slug=place_slug)  # Фильтруем события по слагу связанного заведения

    # Сортировка (если параметр 'sort' передан в GET-запросе)
    sort_by = request.GET.get('sort', 'id') # По умолчанию сортировка по 'id'
    if sort_by == 'date': # Если сортировка по дате
        events_list = events_list.order_by('event_date')  # Сортировка по полю 'event_date' (по возрастанию)
    elif sort_by == 'name': # Если сортировка по названию
        events_list = events_list.order_by('name') # Сортировка по полю 'name' (по алфавиту)

    paginator = Paginator(events_list, 12) # Создаем объект Paginator, отображая по 12 событий на странице
    page_number = request.GET.get('page') # Получаем номер текущей страницы из GET-запроса
    events_page = paginator.get_page(page_number) # Получаем объект страницы с нужными событиями

    places = Place.objects.all() # Получаем все заведения для использования в фильтре на странице
    return render(request, 'events/events.html', { # Отображаем шаблон списка событий
        'events': events_page, # События для текущей страницы
        'places': places, # Все заведения (для фильтра)
        'current_place': place_slug,  # Текущий выбранный слаг заведения (для сохранения состояния фильтра)
        'current_sort': sort_by, # Текущий параметр сортировки (для сохранения состояния)
    })

# Представление для отображения детальной информации о конкретном событии
def event(request, slug): # Принимает 'slug' события из URL
    event_obj = get_object_or_404(Event, slug=slug) # Получает объект Event по слагу или возвращает 404, если не найден
    return render(request, 'events/event.html', context={'event': event_obj}) # Отображает шаблон детальной страницы события

# Представление для создания нового события. Доступно только авторизованным владельцам.
@login_required
def create_event(request):
    if not request.user.is_owner(): # Проверяет, является ли пользователь владельцем
        return redirect("index") # Если нет, перенаправляет на главную

    if request.method == "POST": # Если пользователь отправил форму создания события
        form = EventCreateForm(request.POST) # Создает экземпляр формы с данными из POST
        if form.is_valid(): # Если форма валидна
            event = form.save(commit=False) # Сохраняет данные формы, но пока не коммитит в базу (commit=False)
            event.owner = request.user # Присваивает текущего пользователя как владельца события
            event.save() # Теперь сохраняет событие в базу данных
            if 'images' in request.FILES: # Если были загружены изображения для события
                for image in request.FILES.getlist('images'): # Для каждого загруженного файла изображения
                    EventImage.objects.create(event=event, image=image) # Создает объект EventImage и связывает его с событием
            return redirect("event", slug=event.slug) # Перенаправляет на страницу созданного события
        # Если форма не валидна, возвращаем ее с ошибками
        return render(request, "events/create.html", {"form": form})

    form = EventCreateForm() # Если метод GET, создаем пустую форму
    return render(request, "events/create.html", {"form": form}) # Отображаем страницу создания события с пустой формой


# Представление для отображения списка всех заведений
def places(request):
    query = request.GET.get('q', '').strip() # Получает поисковый запрос 'q' из GET-параметров, удаляет пробелы по краям, по умолчанию пустая строка
    sort_by = request.GET.get('sort', 'id') # Получает параметр сортировки, по умолчанию 'id'

    places_list = Place.objects.all() # Изначально получаем все заведения

    # Фильтрация по поисковому запросу
    if query: # Если поисковый запрос не пустой
        places_list = places_list.filter(Q(name__icontains=query)) # Фильтруем по названию (регистронезависимый поиск части строки)
                                                                  # Q-объект здесь избыточен для одного условия, но полезен для будущих ИЛИ

    # Сортировка
    if sort_by == 'name': # Если сортировка по названию
        places_list = places_list.order_by('name') # Сортируем по названию (алфавитный порядок)
    elif sort_by == 'rating': # Если сортировка по рейтингу
        places_list = places_list.order_by('-rating') # Сортируем по убыванию рейтинга
    else: # По умолчанию (или если sort_by == 'id')
        places_list = places_list.order_by('id') # Сортируем по ID

    # Пагинация
    paginator = Paginator(places_list, 12) # 12 заведений на страницу
    page_number = request.GET.get('page') # Номер текущей страницы
    places_page = paginator.get_page(page_number) # Объект страницы с заведениями

    return render(request, 'places/places.html', { # Отображаем шаблон списка заведений
        'places': places_page, # Заведения для текущей страницы
        'user': request.user, # Текущий пользователь (для отображения/скрытия элементов управления)
        'current_sort': sort_by, # Текущий параметр сортировки (для сохранения состояния)
        'query': query, # Текущий поисковый запрос (для сохранения в поле поиска)
    })

# Представление для отображения детальной информации о конкретном заведении
def place(request, slug): # Принимает 'slug' заведения из URL
    place_obj = get_object_or_404(Place, slug=slug) # Получает заведение по слагу или 404
    reviews = Review.objects.filter(place=place_obj) # Получает все отзывы, связанные с этим заведением

    context = { # Начальный контекст для шаблона
        'place': place_obj, # Объект заведения
        'reviews': reviews, # Список отзывов
    }

    # Если пользователь аутентифицирован и является владельцем этого заведения
    if request.user.is_authenticated and place_obj.owner == request.user:
        today = timezone.now() # Используем timezone.now() вместо datetime.today()
        current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0) # Начало текущего месяца
        last_month_start = current_month_start - relativedelta(months=1) # Начало прошлого месяца
        last_month_end = current_month_start - timezone.timedelta(microseconds=1) # Конец прошлого месяца (точно до начала текущего)

        # Расчет общего NPS для этого заведения (аналогично профилю владельца)
        total_responses = NPSResponse.objects.filter(review__place=place_obj).count()
        promoters = NPSResponse.objects.filter(review__place=place_obj, score__gte=9).count()
        detractors = NPSResponse.objects.filter(review__place=place_obj, score__lte=6).count()
        nps = (promoters / total_responses * 100 - detractors / total_responses * 100) if total_responses > 0 else 0

        # NPS за текущий месяц
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

        # NPS за прошлый месяц
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

        # Топ-3 тегов за все время для этого заведения
        tag_stats = NPSResponse.objects.filter(review__place=place_obj).values('tags__label').annotate(
            tag_count=Count('tags__label')
        ).order_by('-tag_count')[:3]

        # Теги за текущий месяц
        current_month_tags = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=current_month_start
        ).values('tags__label').annotate(
            tag_count=Count('tags__label')
        ).order_by('-tag_count')

        # Теги за прошлый месяц
        last_month_tags = NPSResponse.objects.filter(
            review__place=place_obj,
            created_at__gte=last_month_start,
            created_at__lte=last_month_end
        ).values('tags__label').annotate(
            tag_count=Count('tags__label')
        ).order_by('-tag_count')

        tag_dynamics = {} # Словарь для динамики тегов
        # Собираем все уникальные теги (которые были в текущем или прошлом месяце)
        all_tags_for_dynamics_place = set( # Используем set для уникальности, другое имя переменной чтобы не пересекалось с той что в profile
            [t['tags__label'] for t in current_month_tags if t['tags__label']] +
            [t['tags__label'] for t in last_month_tags if t['tags__label']]
        )
        for tag_label in all_tags_for_dynamics_place: # Для каждого уникального тега
            # Количество упоминаний в текущем месяце
            current_count_place = next((t['tag_count'] for t in current_month_tags if t['tags__label'] == tag_label), 0)
            # Количество упоминаний в прошлом месяце
            last_count_place = next((t['tag_count'] for t in last_month_tags if t['tags__label'] == tag_label), 0)
            tag_dynamics[tag_label] = { # Сохраняем данные
                'current': current_count_place,
                'last': last_count_place,
                'change': current_count_place - last_count_place
            }

        context.update({ # Добавляем статистику владельца в общий контекст
            'nps': nps,
            'total_responses': total_responses,
            'current_nps': current_nps,
            'last_nps': last_nps,
            'tag_stats': tag_stats,
            'tag_dynamics': tag_dynamics,
            'current_month': current_month_start.strftime('%Y-%m'), # Формат "Год-Месяц"
            'last_month': last_month_start.strftime('%Y-%m'),
        })

    return render(request, 'places/place.html', context) # Отображаем шаблон детальной страницы заведения

# Представление для отображения всех отзывов о конкретном заведении (отдельная страница)
def place_reviews(request, slug): # Принимает 'slug' заведения из URL
  place_obj = get_object_or_404(Place, slug=slug) # Получает заведение или 404
  reviews = Review.objects.filter(place=place_obj) # Получает все отзывы для этого заведения
  context = { # Контекст для шаблона
    'place': place_obj,
    'reviews': reviews,
  }
  return render(request, 'places/place_reviews.html', {'place': place_obj, 'reviews': reviews})

# Представление для создания нового заведения. Доступно только авторизованным владельцам.
@login_required
def create_places(request): # создание заведений
    if not request.user.is_owner(): # Проверка, является ли пользователь владельцем
        return redirect("index") # Если нет, на главную

    if request.method == "POST": # Если отправлена форма
        form = PlaceCreateForm(request.POST) # Создаем форму с POST-данными
        if form.is_valid(): # Если форма валидна
            place = form.save(commit=False) # Сохраняем, но не коммитим в базу
            place.owner = request.user  # Привязываем текущего пользователя как владельца заведения
            place.save() # Теперь сохраняем заведение в базу
            if 'images' in request.FILES: # Если загружены изображения
                for image in request.FILES.getlist('images'): # Для каждого изображения
                    PlaceImage.objects.create(place=place, image=image) # Создаем объект PlaceImage
            return redirect("place", slug=place.slug) # Перенаправляем на страницу созданного заведения
        return render(request, "places/place_create.html", {"form": form}) # Если форма не валидна, показываем ее с ошибками

    form = PlaceCreateForm() # Если GET-запрос, создаем пустую форму
    return render(request, "places/place_create.html", {"form": form}) # Отображаем страницу создания заведения

# Представление для редактирования существующего заведения. Доступно только владельцу заведения.
@login_required
def edit_place(request, slug): # Принимает 'slug' заведения из URL
    place = get_object_or_404(Place, slug=slug) # Получаем заведение или 404

    # Проверяем, что текущий пользователь — владелец заведения И является пользователем с ролью "owner"
    if not request.user.is_owner() or place.owner != request.user:
        return redirect("index") # Если нет, на главную

    if request.method == "POST": # Если отправлена форма редактирования
        form = PlaceCreateForm(request.POST, instance=place) # Создаем форму, передавая POST-данные и существующий объект 'place' для редактирования
        if form.is_valid(): # Если форма валидна
            form.save() # Сохраняем изменения
            # Обновляем изображения, если загружены новые
            if 'images' in request.FILES: # Если есть новые изображения
                # Удаляем старые изображения (опционально, если логика подразумевает полную замену)
                place.images.all().delete() # Удаляет все связанные объекты PlaceImage
                for image in request.FILES.getlist('images'): # Для каждого нового изображения
                    PlaceImage.objects.create(place=place, image=image) # Создаем новый объект PlaceImage
            return redirect("place", slug=place.slug) # Перенаправляем на страницу заведения (слаг мог измениться, если поле слаг редактируемое и изменилось)
        return render(request, "places/place_edit.html", {"form": form, "place": place}) # Если форма не валидна, показываем ее с ошибками

    form = PlaceCreateForm(instance=place) # Если GET-запрос, создаем форму, предзаполненную данными объекта 'place'
    return render(request, "places/place_edit.html", {"form": form, "place": place}) # Отображаем страницу редактирования

# Представление для отображения списка всех отзывов
def reviews(request):
    reviews_list = Review.objects.all() # Получаем все отзывы

    # Фильтр по заведению (если 'place' передан в GET)
    place_id = request.GET.get('place') # Получаем ID заведения из GET
    if place_id: # Если ID указан
        reviews_list = reviews_list.filter(place__id=place_id) # Фильтруем отзывы по ID заведения

    # Сортировка
    sort_by = request.GET.get('sort', 'id') # По умолчанию сортировка по ID
    if sort_by == 'date': # Если сортировка по дате
        reviews_list = reviews_list.order_by('-review_date') # Сортируем по дате отзыва (сначала новые)
    elif sort_by == 'name': # Если сортировка по имени (имени отзыва? или имени автора? поле 'name' в Review)
        reviews_list = reviews_list.order_by('name') # Сортируем по полю 'name'
    else: # По умолчанию (или sort_by == 'id')
        reviews_list = reviews_list.order_by('id') # Сортируем по ID

    paginator = Paginator(reviews_list, 12) # 12 отзывов на страницу
    page_number = request.GET.get('page') # Номер текущей страницы
    reviews_page = paginator.get_page(page_number) # Объект страницы с отзывами

    places = Place.objects.all() # Все заведения (для фильтра на странице)
    return render(request, 'review/reviews.html', { # Отображаем шаблон списка отзывов
        'reviews': reviews_page, # Отзывы для текущей страницы
        'places': places, # Все заведения
        'current_place': place_id, # Текущий ID выбранного заведения (для сохранения фильтра)
        'current_sort': sort_by, # Текущий параметр сортировки
    })

# Представление для отображения детальной информации о конкретном отзыве
def review(request, slug): # Принимает 'slug' отзыва из URL
    review = get_object_or_404(Review, slug=slug) # Получаем отзыв по слагу или 404
    user_vote = None # Инициализируем голос пользователя как None
    if request.user.is_authenticated: # Если пользователь авторизован
        # Пытаемся найти голос текущего пользователя для этого отзыва
        user_vote = ReviewVote.objects.filter(review=review, user=request.user).first()
    return render(request, 'review/review.html', { # Отображаем шаблон детальной страницы отзыва
        'review': review, # Объект отзыва
        'user': request.user, # Текущий пользователь
        'user_vote': user_vote, # Голос пользователя (объект ReviewVote или None)
    })

# Представление для создания нового отзыва. Доступно только авторизованным гурманам.
@login_required
def create_review(request):
    if not request.user.is_gourmand(): # Проверка, является ли пользователь гурманом
        return redirect('index') # Если нет, на главную

    place_id = request.GET.get('place') # Пытаемся получить ID заведения из GET-параметра (если отзыв создается со страницы заведения)
    initial_data = {} # Начальные данные для формы (для предзаполнения поля "заведение")
    if place_id: # Если ID заведения передан
        try:
            place = Place.objects.get(id=place_id) # Находим заведение по ID
            initial_data['place'] = place # Устанавливаем его как начальное значение для поля 'place' в форме
        except Place.DoesNotExist: # Если заведение с таким ID не найдено
            pass # Ничего не делаем, поле 'place' останется пустым или будет выбрано вручную

    if request.method == "POST": # Если отправлена форма создания отзыва
        form = ReviewCreateForm(request.POST, request.FILES) # Создаем форму с POST-данными и файлами (изображениями)
        if form.is_valid(): # Если форма валидна
            review = form.save(commit=False) # Сохраняем, но не коммитим
            review.gourmand = request.user # Привязываем текущего пользователя (гурмана) как автора отзыва
            review.save() # Теперь сохраняем отзыв в базу
            if 'images' in request.FILES: # Если загружены изображения
                for image in request.FILES.getlist('images'): # Для каждого изображения
                    ReviewImage.objects.create(review=review, image=image) # Создаем объект ReviewImage
            return redirect('review', slug=review.slug)  # Перенаправляем на страницу созданного отзыва
        else: # Если форма не валидна
            print(form.errors) # Выводим ошибки формы в консоль (для отладки)
            return render(request, "review/create.html", {"form": form}) # Показываем форму с ошибками

    form = ReviewCreateForm(initial=initial_data) # Если GET-запрос, создаем форму с начальными данными (если 'place_id' был)
    return render(request, "review/create.html", {"form": form}) # Отображаем страницу создания отзыва


def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"Новое сообщение с сайта от {name}"
        body = (
            f"Имя: {name}\n"
            f"Email: {email}\n\n"
            f"Сообщение:\n{message}"
        )

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['aagubanoff@yandex.ru'],
                fail_silently=False,
            )
            messages.success(request, 'Сообщение успешно отправлено!')
        except Exception as e:
            messages.error(request, f'Ошибка при отправке: {str(e)}')

    return render(request, 'landing/contacts.html', {
        'YANDEX_CAPTCHA_CLIENT_KEY': settings.YANDEX_CAPTCHA_CLIENT_KEY
    })

# Представление для отображения списка гурманов
def gourmands(request):
    # Фильтруем пользователей, чтобы получить только тех, у кого роль 'gourmand', и выбираем связанные профили GourmandProfile
    gourmands_list = GourmandProfile.objects.select_related('user').filter(user__role='gourmand')

    # Сортировка
    sort_by = request.GET.get('sort', 'id') # По умолчанию по ID
    if sort_by == 'rating': # Если сортировка по рейтингу гурмана (если есть такое поле в GourmandProfile)
        gourmands_list = gourmands_list.order_by('-rating')
    elif sort_by == 'experience': # Если сортировка по опыту (дате регистрации)
        gourmands_list = gourmands_list.order_by('user__date_joined') # Сортируем по дате регистрации пользователя (сначала старые)
    elif sort_by == 'reviews': # Если сортировка по количеству отзывов
        # Аннотируем количество отзывов для каждого пользователя и сортируем по убыванию
        gourmands_list = gourmands_list.annotate(review_count=Count('user__reviews')).order_by('-review_count')
    else: # По умолчанию (или sort_by == 'id')
        gourmands_list = gourmands_list.order_by('id') # Сортируем по ID профиля гурмана

    paginator = Paginator(gourmands_list, 12) # 12 гурманов на страницу
    page_number = request.GET.get('page') # Номер текущей страницы
    gourmands_page = paginator.get_page(page_number) # Объект страницы с гурманами

    return render(request, 'gourmands/gourmands.html', { # Отображаем шаблон списка гурманов
        'gourmands': gourmands_page, # Гурманы для текущей страницы
        'current_sort': sort_by, # Текущий параметр сортировки
    })

# Представление для отображения детальной информации о конкретном гурмане
def gourmand(request, slug): # Принимает 'slug' пользователя (гурмана) из URL
    # Предполагается, что у модели User есть поле slug
    gourmand_obj = get_object_or_404(User, slug=slug, role='gourmand') # Получаем пользователя по слагу и роли 'gourmand'
    # Если нужна информация из GourmandProfile, нужно будет сделать дополнительный запрос или изменить этот:
    # gourmand_profile = get_object_or_404(GourmandProfile, user__slug=slug, user__role='gourmand')
    return render(request, 'gourmands/gourmand.html', {'gourmand': gourmand_obj}) # Отображаем шаблон профиля гурмана

# Представление для отображения всех отзывов конкретного гурмана
def gourmand_reviews(request, slug): # Принимает 'slug' пользователя (гурмана)
    gourmand_obj = get_object_or_404(User, slug=slug, role='gourmand') # Получаем пользователя-гурмана
    reviews = Review.objects.filter(gourmand=gourmand_obj) # Получаем все отзывы, оставленные этим гурманом
    return render(request, 'gourmands/gourmand_reviews.html', {'gourmand': gourmand_obj, 'reviews': reviews}) # Отображаем шаблон

# Представление для голосования за отзыв (лайк/дизлайк). Доступно только авторизованным гурманам.
@login_required
def vote_review(request, slug, vote_type): # Принимает 'slug' отзыва и 'vote_type' (тип голоса) из URL
    if not request.user.is_gourmand(): # Проверка, является ли пользователь гурманом
        return redirect('index') # Если нет, на главную

    review = get_object_or_404(Review, slug=slug)  # Получаем отзыв по слагу
    if vote_type not in ['positive', 'negative']: # Проверяем, что тип голоса допустим
        return HttpResponseBadRequest("Недопустимый тип голоса") # Если нет, ошибка 400

    if review.gourmand == request.user: # Проверяем, не пытается ли автор проголосовать за свой же отзыв
        return redirect('review', slug=review.slug)  # Если да, просто перенаправляем обратно на страницу отзыва

    # Ищем существующий голос от этого пользователя для этого отзыва
    existing_vote = ReviewVote.objects.filter(review=review, user=request.user).first()

    if existing_vote: # Если пользователь уже голосовал
        if existing_vote.vote_type == vote_type: # Если новый голос совпадает со старым (например, дважды лайкнул)
            return redirect('review', slug=review.slug)  # Ничего не делаем, перенаправляем обратно
        # Если новый голос другой (например, был лайк, стал дизлайк), удаляем старый голос
        existing_vote.delete()
        if existing_vote.vote_type == 'positive': # Уменьшаем счетчик старого голоса в отзыве
            review.positive_rating = max(0, review.positive_rating - 1) # Убедимся, что рейтинг не станет отрицательным
        else:
            review.negative_rating = max(0, review.negative_rating - 1)

    # Создаем новый голос
    ReviewVote.objects.create(review=review, user=request.user, vote_type=vote_type)
    if vote_type == 'positive': # Увеличиваем соответствующий счетчик в отзыве
        review.positive_rating += 1
    else:
        review.negative_rating += 1
    review.save() # Сохраняем изменения в объекте отзыва (обновленные рейтинги)

    return redirect('review', slug=review.slug)  # Перенаправляем обратно на страницу отзыва


# Представление для анализа отзывов с помощью ChatGPT. Доступно только POST-запросами и авторизованным пользователям.
@require_POST # Декоратор, разрешающий только POST-запросы
@login_required # Декоратор, требующий аутентификации
def analyze_reviews(request, place_id): # Принимает 'place_id' из URL
    user = request.user # Текущий авторизованный пользователь
    period = request.GET.get('period', '1m') # Получает 'period' из GET-параметров запроса (хотя запрос POST, параметры могут быть в URL)
    days = {'1m': 30, '3m': 90, '6m': 180}.get(period, 30) # Определяем количество дней по периоду
    logger.info(f"ANALYZE_REVIEWS: Called for place_id: {place_id}, owner: {user.last_name}, period: {period}") # Логируем вызов функции

    try:
        # Получаем заведение по ID, убедившись, что оно принадлежит текущему пользователю (владельцу)
        place = Place.objects.get(id=place_id, owner=user)
    except Place.DoesNotExist: # Если заведение не найдено или не принадлежит пользователю
        logger.warning(f"ANALYZE_REVIEWS: Place with id {place_id} not found for owner {user.last_name}") # Логируем предупреждение
        # messages.error(request, "Заведение не найдено.") # Можно добавить сообщение для пользователя (требует импорта django.contrib.messages)
        return redirect('profile') # Перенаправляем на профиль владельца

    # Получаем queryset отзывов за указанный период для данного заведения
    reviews_qs = get_reviews_for_last_month(place, days=days)
    # Подготавливаем данные отзывов в строковом формате для передачи в ChatGPT
    reviews_data_str = prepare_reviews_data(reviews_qs)

    # ---> ЛОГИРОВАНИЕ ПОЛНЫХ ДАННЫХ ОТЗЫВОВ <---
    logger.info(f"ANALYZE_REVIEWS: Full reviews_data for {place.name} (ID: {place.id}):\n{reviews_data_str}") # Полные данные
    # Также можно оставить предыдущий debug-лог для краткой информации
    logger.debug(f"ANALYZE_REVIEWS: Prepared reviews data for {place.name} (length: {len(reviews_data_str)}): '{reviews_data_str[:200]}...'") # Краткая информация

    # Вызываем функцию анализа отзывов с помощью ChatGPT
    summary_text = analyze_reviews_with_chatgpt(reviews_data_str, place.name)
    logger.info(f"ANALYZE_REVIEWS: Received summary for {place.name}: '{summary_text[:100]}...'") # Логируем полученную сводку (начало)

    # Формируем ключ для кэша и сохраняем сводку в кэш на 24 часа
    cache_key = f"review_summary_{place.id}_{period}"
    cache.set(cache_key, summary_text, timeout=60 * 60 * 24) # timeout в секундах (24 часа)
    logger.info(f"ANALYZE_REVIEWS: Summary for {place.name} (key: {cache_key}) saved to cache.") # Логируем сохранение в кэш

    # Перенаправляем обратно на страницу профиля владельца, сохраняя выбранный период в URL
    return redirect(f"{reverse('profile')}?period={period}")