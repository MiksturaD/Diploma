# Импорт базового класса пользователя и менеджера из Django для кастомной аутентификации.
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
# Импорт миксина PermissionsMixin для работы с правами доступа.
from django.contrib.auth.models import PermissionsMixin
# Импорт базовых моделей и полей из Django для создания структуры базы данных.
from django.db import models
# Импорт валидатора для проверки расширений файлов.
from django.core.validators import FileExtensionValidator
# Импорт функции Sum для агрегации данных (например, подсчёт рейтингов).
from django.db.models import Sum
# Импорт утилиты slugify для генерации slug на основе текста.
from django.utils.text import slugify
# Импорт pytils_slugify для транслитерации кириллических символов в slug.
from pytils.translit import slugify as pytils_slugify  # Для транслитерации кириллицы
# Импорт Decimal для работы с десятичными числами (например, рейтингами).
from decimal import Decimal
# Импорт настроек Django для доступа к модели пользователя.
from django.conf import settings


# Класс UserManager — кастомный менеджер для модели User, управляет созданием пользователей.
class UserManager(BaseUserManager):
    # Метод create_user создаёт обычного пользователя с указанным email и паролем.
    def create_user(self, email, password=None, **extra_fields):
        # Проверяем, что email обязателен, иначе выбрасываем исключение.
        if not email:
            raise ValueError("Email обязателен")
        # Нормализуем email (приводим к нижнему регистру).
        email = self.normalize_email(email)
        # Создаём новый объект пользователя с указанным email и дополнительными полями.
        user = self.model(email=email, **extra_fields)
        # Устанавливаем пароль (хешируем его).
        user.set_password(password)
        # Сохраняем пользователя в базе с использованием текущей базы данных.
        user.save(using=self._db)
        return user

    # Метод create_superuser создаёт суперпользователя с правами администратора.
    def create_superuser(self, email, password=None, **extra_fields):
        # Устанавливаем значения по умолчанию для is_staff и is_superuser, если они не указаны.
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # Вызываем create_user с заданными параметрами.
        return self.create_user(email, password, **extra_fields)


# Класс User — кастомная модель пользователя, наследуется от AbstractBaseUser и PermissionsMixin.
class User(AbstractBaseUser, PermissionsMixin):
    # Константа ROLE_CHOICES — варианты ролей пользователя (гурман или владелец).
    ROLE_CHOICES = (
        ("gourmand", "Гурман"),
        ("owner", "Владелец заведения"),
    )
    # Поле email — уникальный адрес пользователя, используется как идентификатор.
    email = models.EmailField(unique=True)
    # Поле first_name — имя пользователя, может быть пустым.
    first_name = models.CharField(max_length=30, blank=True)
    # Поле last_name — фамилия пользователя, может быть пустым.
    last_name = models.CharField(max_length=30, blank=True)
    # Поле role — роль пользователя, выбирается из ROLE_CHOICES, по умолчанию "gourmand".
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="gourmand", db_index=True)
    # Поле is_active — флаг активности пользователя, по умолчанию True.
    is_active = models.BooleanField(default=True)
    # Поле is_staff — флаг, обозначающий, является ли пользователь персоналом, по умолчанию False.
    is_staff = models.BooleanField(default=False)
    # Поле slug — уникальный URL-дружественный идентификатор, генерируется автоматически.
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name="Слаг")
    # Поле date_joined — дата регистрации пользователя, устанавливается автоматически.
    date_joined = models.DateTimeField(auto_now_add=True, db_index=True)

    # Указываем менеджер для модели.
    objects = UserManager()

    # Указываем, что email используется как поле для входа вместо username.
    USERNAME_FIELD = "email"
    # Указываем обязательные поля при создании пользователя (кроме email).
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # Метод save переопределяет сохранение объекта для генерации slug.
    def save(self, *args, **kwargs):
        # Проверяем, что slug ещё не сгенерирован.
        if not self.slug:
            # Формируем базовый slug из имени и фамилии или email, если имя/фамилия пусты.
            base_slug = (
                f"{self.first_name}-{self.last_name}"
                if self.first_name and self.last_name
                else self.email.split('@')[0]
            )
            # Транслитерируем базовый slug для поддержки кириллицы.
            self.slug = pytils_slugify(base_slug)
            # Если транслитерация не удалась, используем дефолтный формат.
            if not self.slug:
                self.slug = f"user-{self.id or 'new'}"
            original_slug = self.slug
            counter = 1
            # Проверяем уникальность slug и добавляем суффикс, если он уже существует.
            while User.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        # Вызываем родительский метод save для сохранения объекта.
        super().save(*args, **kwargs)

    # Метод __str__ возвращает строковое представление объекта (email).
    def __str__(self):
        return self.email

    # Метод is_gourmand проверяет, является ли пользователь гурманом.
    def is_gourmand(self):
        return self.role == "gourmand"

    # Метод is_owner проверяет, является ли пользователь владельцем заведения.
    def is_owner(self):
        return self.role == "owner"


# Класс GourmandProfile — профиль гурмана, связан с User один-к-одному.
class GourmandProfile(models.Model):
    # Связь один-к-одному с пользователем, удаление пользователя удаляет профиль.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gourmand_profile')
    # Рейтинг гурмана, десятичное число с 1 знаком после запятой, по умолчанию 0.0.
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    # Поле для изображения профиля, сохраняется в 'gourmand_images/', может быть пустым.
    image = models.ImageField(upload_to='gourmand_images/', blank=True, null=True)
    # Описание профиля, текстовое поле, может быть пустым.
    description = models.TextField(blank=True, null=True)

    # Метод __str__ возвращает строковое представление профиля (имя и фамилия пользователя).
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    # Метод update_rating обновляет рейтинг профиля на основе отзывов.
    def update_rating(self):
        # Используем агрегацию для подсчёта суммы positive_rating и negative_rating из отзывов пользователя.
        reviews_stats = self.user.reviews.aggregate(
            total_positive=Sum('positive_rating'),
            total_negative=Sum('negative_rating')
        )
        # Получаем значения или 0, если агрегация вернула None.
        total_positive = reviews_stats['total_positive'] or 0
        total_negative = reviews_stats['total_negative'] or 0
        # Общее количество реакций.
        total_reactions = total_positive + total_negative

        # Вычисляем рейтинг: доля положительных реакций умножается на 5.
        if total_reactions > 0:
            self.rating = (total_positive / total_reactions) * 5
        else:
            self.rating = 0.0

        # Обновляем рейтинг напрямую в базе, чтобы избежать рекурсии при вызове save().
        GourmandProfile.objects.filter(id=self.id).update(rating=self.rating)


# Класс Place — модель заведения с информацией и рейтингом.
class Place(models.Model):
    # Название заведения, строка до 100 символов.
    name = models.CharField(max_length=100)
    # Описание заведения, текстовое поле.
    description = models.TextField()
    # Email заведения.
    place_email = models.EmailField()
    # Местоположение заведения, текстовое поле.
    location = models.TextField()
    # Рейтинг заведения, десятичное число с 1 знаком после запятой, по умолчанию 0.0.
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    # Номер телефона, текстовое поле до 50 символов.
    phone = models.TextField(max_length=50)
    # Сайт заведения, URL, может быть пустым.
    website = models.URLField(max_length=200, blank=True, null=True)
    # Владелец заведения, связь с моделью User, при удалении устанавливается NULL.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_places'
    )
    # Уникальный URL-дружественный идентификатор, генерируется автоматически.
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name="Слаг")

    # Метод save переопределяет сохранение объекта для генерации slug.
    def save(self, *args, **kwargs):
        # Проверяем, что slug ещё не сгенерирован.
        if not self.slug:
            # Пробуем транслитерировать название с помощью pytils.
            base_slug = pytils_slugify(self.name) if self.name else f"place-{self.id or 'new'}"
            # Если транслитерация не удалась, используем дефолтный формат.
            if not base_slug:  # Если name пустое или содержит только спецсимволы
                base_slug = f"place-{self.id or 'new'}"
            self.slug = base_slug
            original_slug = self.slug
            counter = 1
            # Проверяем уникальность slug и добавляем суффикс, если он уже существует.
            while Place.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        # Вызываем родительский метод save для сохранения объекта.
        super().save(*args, **kwargs)

    # Метод __str__ возвращает строковое представление объекта (название).
    def __str__(self):
        return self.name

    # Метод update_rating обновляет рейтинг заведения на основе отзывов.
    def update_rating(self):
        # Получаем все отзывы для этого места.
        reviews = self.reviews.all()
        if reviews.exists():
            # Фильтруем отзывы с валидным gourmand_rating и профилем.
            valid_reviews = [
                review for review in reviews
                if review.gourmand_rating is not None and hasattr(review.gourmand, 'gourmand_profile')
            ]
            if valid_reviews:
                # Вычисляем вес каждого отзыва: рейтинг гурмана * (positive - negative + 1).
                total_weighted_rating = 0
                total_weight = 0
                for review in valid_reviews:
                    # Модификатор веса на основе лайков и дизлайков, минимум 0.1.
                    modifier = review.positive_rating - review.negative_rating + 1
                    modifier = max(0.1, modifier)  # Минимальный модификатор 0.1
                    # Итоговый вес: рейтинг гурмана * модификатор.
                    weight = float(review.gourmand.gourmand_profile.rating) * modifier
                    total_weighted_rating += review.gourmand_rating * weight
                    total_weight += weight

                # Считаем средневзвешенный рейтинг.
                if total_weight > 0:
                    average_rating = total_weighted_rating / total_weight
                    self.rating = Decimal(str(average_rating)).quantize(Decimal('0.1'))
                else:
                    self.rating = Decimal('0.0')
            else:
                self.rating = Decimal('0.0')
        else:
            self.rating = Decimal('0.0')
        # Сохраняем обновлённый рейтинг.
        self.save()


# Класс PlaceImage — модель для хранения изображений заведения.
class PlaceImage(models.Model):
    # Связь с местом, удаление места удаляет изображение.
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    # Поле для изображения, проверяет расширения (jpg, png, webp), может быть пустым.
    image = models.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
        verbose_name="Фото заведения",
        upload_to="places/",
        blank=True,
        null=True
    )

    # Метод __str__ возвращает строковое представление объекта (название места).
    def __str__(self):
        return f"Фото для {self.place.name}"


# Класс OwnerProfile — профиль владельца заведения, связан с User один-к-одному.
class OwnerProfile(models.Model):
    # Связь один-к-одному с пользователем, удаление пользователя удаляет профиль.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    # Описание профиля, текстовое поле, может быть пустым.
    description = models.TextField(blank=True)
    # Связь многие-ко-многим с местами, может быть пустым.
    places = models.ManyToManyField(Place, blank=True)
    # Поле для изображения профиля, сохраняется в 'owners/', может быть пустым.
    image = models.ImageField(upload_to="owners/", blank=True, null=True)

    # Метод __str__ возвращает строковое представление профиля (статус владельца).
    def __str__(self):
        return f"Владелец {self.user}"


# Класс Review — модель отзыва о месте.
class Review(models.Model):
    # Название отзыва, строка до 50 символов.
    name = models.CharField(max_length=50)
    # Дата создания отзыва, устанавливается автоматически.
    review_date = models.DateTimeField(auto_now_add=True)
    # Текст отзыва.
    description = models.TextField()
    # Рейтинг от гурмана, может быть пустым.
    gourmand_rating = models.IntegerField(null=True, blank=True, default=None)
    # Количество положительных оценок.
    positive_rating = models.IntegerField(default=0)
    # Количество отрицательных оценок.
    negative_rating = models.IntegerField(default=0)
    # Связь с автором отзыва (гурманом), не удаляется при удалении пользователя.
    gourmand = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='reviews'
    )
    # Связь с местом, удаление места удаляет отзыв.
    place = models.ForeignKey('Place', on_delete=models.CASCADE, related_name='reviews')
    # Уникальный URL-дружественный идентификатор, генерируется автоматически.
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name="Слаг")

    # Метод save переопределяет сохранение объекта для генерации slug и обновления рейтингов.
    def save(self, *args, **kwargs):
        # Сохраняем объект один раз для получения id.
        super().save(*args, **kwargs)

        # Генерируем slug, если его нет.
        if not self.slug:
            # Формируем базовый slug из названия и id.
            base_slug = f"{self.name}-{self.id}" if self.name else f"review-{self.id}"
            self.slug = pytils_slugify(base_slug)
            if not self.slug:
                self.slug = f"review-{self.id}"
            original_slug = self.slug
            counter = 1
            # Проверяем уникальность slug и добавляем суффикс, если он уже существует.
            while Review.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
            # Сохраняем ещё раз только если изменился slug.
            super().save(update_fields=['slug'])

        # Обновляем рейтинги места и профиля гурмана после сохранения.
        self.place.update_rating()
        if hasattr(self.gourmand, 'gourmand_profile'):
            self.gourmand.gourmand_profile.update_rating()

    # Метод __str__ возвращает строковое представление отзыва.
    def __str__(self):
        return f"{self.name} от {self.gourmand} о {self.place}"


# Класс ReviewImage — модель для хранения изображений отзывов.
class ReviewImage(models.Model):
    # Связь с отзывом, удаление отзыва удаляет изображение.
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    # Поле для изображения, проверяет расширения (jpg, png, webp), может быть пустым.
    image = models.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
        verbose_name="Фото отзыва",
        upload_to="reviews/",
        blank=True,
        null=True
    )

    # Метод __str__ возвращает строковое представление объекта (название отзыва).
    def __str__(self):
        return f"Фото для {self.review.name}"


# Класс ReviewVote — модель для хранения голосов за отзывы.
class ReviewVote(models.Model):
    # Константа VOTE_CHOICES — варианты голосов (позитивный или негативный).
    VOTE_CHOICES = (
        ('positive', 'Позитивный'),
        ('negative', 'Негативный'),
    )
    # Связь с отзывом, удаление отзыва удаляет голос.
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    # Связь с пользователем, оставившим голос.
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='review_votes')
    # Тип голоса, выбирается из VOTE_CHOICES.
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)

    # Метакласс Meta задаёт ограничения уникальности для комбинации review и user.
    class Meta:
        unique_together = ('review', 'user')

    # Метод __str__ возвращает строковое представление голоса.
    def __str__(self):
        return f"{self.user} проголосовал {self.vote_type} за {self.review}"


# Класс Event — модель мероприятия.
class Event(models.Model):
    # Константа WEEKDAYS — список дней недели для выбора.
    WEEKDAYS = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]
    # Название мероприятия, строка до 100 символов.
    name = models.CharField(max_length=100)
    # Описание мероприятия, текстовое поле.
    description = models.TextField()
    # Дата и время проведения, может быть пустым.
    event_date = models.DateTimeField(null=True, blank=True)
    # Связь с местом проведения, удаление места удаляет мероприятие.
    place = models.ForeignKey('Place', on_delete=models.CASCADE, related_name='events')
    # Связь с владельцем (пользователем), удаление владельца удаляет мероприятие.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True
    )  # Добавляем поле owner
    # Флаг, указывающий, является ли мероприятие еженедельным.
    is_weekly = models.BooleanField(default=False)
    # День недели для еженедельных мероприятий, может быть пустым.
    day_of_week = models.IntegerField(choices=WEEKDAYS, null=True, blank=True)
    # Уникальный URL-дружественный идентификатор, генерируется автоматически.
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name="Слаг")

    # Метод save переопределяет сохранение объекта для генерации slug.
    def save(self, *args, **kwargs):
        # Сначала сохраняем объект, чтобы получить id.
        if not self.slug:
            super().save(*args, **kwargs)  # Первое сохранение
            self.slug = pytils_slugify(self.name) if self.name else f"event-{self.id}"
            if not self.slug:
                self.slug = f"event-{self.id}"
            original_slug = self.slug
            counter = 1
            # Проверяем уникальность slug и добавляем суффикс, если он уже существует.
            while Event.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
            # Сохраняем ещё раз с обновлённым slug.
            super().save(*args, **kwargs)
        else:
            # Если мероприятие не еженедельное, сбрасываем день недели.
            if not self.is_weekly:
                self.day_of_week = None
            super().save(*args, **kwargs)

    # Метод __str__ возвращает строковое представление объекта (название).
    def __str__(self):
        return self.name

    # Свойство is_recurring проверяет, является ли мероприятие повторяющимся.
    @property
    def is_recurring(self):
        return self.is_weekly


# Класс EventImage — модель для хранения изображений мероприятий.
class EventImage(models.Model):
    # Связь с мероприятием, удаление мероприятия удаляет изображение.
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    # Поле для изображения, проверяет расширения (jpg, png, webp), может быть пустым.
    image = models.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
        verbose_name="Фото мероприятия",
        upload_to="events/",
        blank=True,
        null=True
    )

    # Метод __str__ возвращает строковое представление объекта (название мероприятия).
    def __str__(self):
        return f"Фото для {self.event.name}"


# Класс NPSResponse — модель для ответов NPS (оценок удовлетворённости).
class NPSResponse(models.Model):
    # Константа TAGS — список тегов для классификации отзывов.
    TAGS = [
        ('kitchen', 'Кухня'),
        ('service', 'Обслуживание'),
        ('atmosphere', 'Атмосфера'),
        ('cozy', 'Уют'),
        ('comfort', 'Комфорт'),
        ('dishes', 'Блюда'),
        ('music', 'Музыка'),
        ('price', 'Цена'),
        ('cleanliness', 'Чистота'),
    ]

    # Связь один-к-одному с отзывом, удаление отзыва удаляет ответ NPS.
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='nps')
    # Оценка от 1 до 10, выбирается из списка.
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)])
    # Связь многие-ко-многим с тегами, может быть пустым.
    tags = models.ManyToManyField('NPSTag', blank=True)
    # Дата создания ответа, устанавливается автоматически.
    created_at = models.DateTimeField(auto_now_add=True)

    # Метод __str__ возвращает строковое представление объекта (оценка и место).
    def __str__(self):
        return f"NPS {self.score} для {self.review.place}"


# Класс NPSTag — модель для тегов NPS.
class NPSTag(models.Model):
    # Уникальное имя тега, строка до 20 символов.
    name = models.CharField(max_length=20, unique=True)
    # Метка тега, строка до 50 символов (для отображения).
    label = models.CharField(max_length=50)

    # Метод __str__ возвращает строковое представление объекта (метка).
    def __str__(self):
        return self.label