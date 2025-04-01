from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models import Sum
from django.utils.text import slugify
from pytils.translit import slugify as pytils_slugify  # Для транслитерации кириллицы
from decimal import Decimal
from Gourmand import settings


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("gourmand", "Гурман"),
        ("owner", "Владелец заведения"),
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="gourmand", db_index=True)  # Индекс на role
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name="Слаг")
    date_joined = models.DateTimeField(auto_now_add=True, db_index=True)  # Индекс на date_joined

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = (
                f"{self.first_name}-{self.last_name}"
                if self.first_name and self.last_name
                else self.email.split('@')[0]
            )
            self.slug = pytils_slugify(base_slug)
            if not self.slug:
                self.slug = f"user-{self.id or 'new'}"
            original_slug = self.slug
            counter = 1
            while User.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def is_gourmand(self):
        return self.role == "gourmand"

    def is_owner(self):
        return self.role == "owner"

class GourmandProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gourmand_profile')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    image = models.ImageField(upload_to='gourmand_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def update_rating(self):
        # Используем агрегацию для подсчёта суммы positive_rating и negative_rating
        reviews_stats = self.user.reviews.aggregate(
            total_positive=Sum('positive_rating'),
            total_negative=Sum('negative_rating')
        )
        total_positive = reviews_stats['total_positive'] or 0
        total_negative = reviews_stats['total_negative'] or 0
        total_reactions = total_positive + total_negative

        # Вычисляем рейтинг
        if total_reactions > 0:
            self.rating = (total_positive / total_reactions) * 5
        else:
            self.rating = 0.0

        # Сохраняем без вызова save(), чтобы избежать рекурсии
        GourmandProfile.objects.filter(id=self.id).update(rating=self.rating)

class Place(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    place_email = models.EmailField()
    location = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    phone = models.TextField(max_length=50)
    website = models.URLField(max_length=200, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_places'
    )
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name="Слаг")

    def save(self, *args, **kwargs):
        if not self.slug:
            # Пробуем транслитерировать название с помощью pytils
            base_slug = pytils_slugify(self.name) if self.name else f"place-{self.id or 'new'}"
            if not base_slug:  # Если pytils тоже не справился (например, name пустое или содержит только спецсимволы)
                base_slug = f"place-{self.id or 'new'}"
            self.slug = base_slug
            original_slug = self.slug
            counter = 1
            while Place.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            # Учитываем только отзывы, у которых есть gourmand_rating и профиль GourmandProfile
            valid_reviews = [
                review for review in reviews
                if review.gourmand_rating is not None and hasattr(review.gourmand, 'gourmand_profile')
            ]
            if valid_reviews:
                # Вычисляем вес каждого отзыва: gourmand_profile.rating * (positive_rating - negative_rating + 1)
                # Минимальный модификатор веса 0.1, чтобы избежать отрицательного или нулевого веса
                total_weighted_rating = 0
                total_weight = 0
                for review in valid_reviews:
                    # Модификатор веса на основе лайков и дизлайков
                    modifier = review.positive_rating - review.negative_rating + 1
                    modifier = max(0.1, modifier)  # Минимальный модификатор 0.1
                    # Итоговый вес: рейтинг гурмана * модификатор
                    weight = float(review.gourmand.gourmand_profile.rating) * modifier
                    total_weighted_rating += review.gourmand_rating * weight
                    total_weight += weight

                # Считаем средневзвешенный рейтинг
                if total_weight > 0:
                    average_rating = total_weighted_rating / total_weight
                    self.rating = Decimal(str(average_rating)).quantize(Decimal('0.1'))
                else:
                    self.rating = Decimal('0.0')
            else:
                self.rating = Decimal('0.0')
        else:
            self.rating = Decimal('0.0')
        self.save()


class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
        verbose_name="Фото заведения",
        upload_to="places/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Фото для {self.place.name}"

class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    description = models.TextField(blank=True)
    places = models.ManyToManyField(Place, blank=True)
    image = models.ImageField(upload_to="owners/", blank=True, null=True)

    def __str__(self):
        return f"Владелец {self.user}"


class Review(models.Model):
    name = models.CharField(max_length=50)
    review_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    gourmand_rating = models.IntegerField(null=True, blank=True, default=None)
    positive_rating = models.IntegerField(default=0)
    negative_rating = models.IntegerField(default=0)
    gourmand = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='reviews'
    )
    place = models.ForeignKey('Place', on_delete=models.CASCADE, related_name='reviews')
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name="Слаг")

    def save(self, *args, **kwargs):
        # Сохраняем объект один раз
        super().save(*args, **kwargs)

        # Генерируем slug, если его нет
        if not self.slug:
            base_slug = f"{self.name}-{self.id}" if self.name else f"review-{self.id}"
            self.slug = pytils_slugify(base_slug)
            if not self.slug:
                self.slug = f"review-{self.id}"
            original_slug = self.slug
            counter = 1
            while Review.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
            # Сохраняем ещё раз только если изменился slug
            super().save(update_fields=['slug'])

        # Обновляем рейтинги
        self.place.update_rating()
        if hasattr(self.gourmand, 'gourmand_profile'):
            self.gourmand.gourmand_profile.update_rating()

    def __str__(self):
        return f"{self.name} от {self.gourmand} о {self.place}"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
        verbose_name="Фото отзыва",
        upload_to="reviews/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Фото для {self.review.name}"


class ReviewVote(models.Model):
    VOTE_CHOICES = (
        ('positive', 'Позитивный'),
        ('negative', 'Негативный'),
    )
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='review_votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return f"{self.user} проголосовал {self.vote_type} за {self.review}"


class Event(models.Model):
    WEEKDAYS = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    event_date = models.DateTimeField(null=True, blank=True)
    place = models.ForeignKey('Place', on_delete=models.CASCADE, related_name='events')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True
    )  # Добавляем поле owner
    is_weekly = models.BooleanField(default=False)
    day_of_week = models.IntegerField(choices=WEEKDAYS, null=True, blank=True)
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name="Слаг")

    def save(self, *args, **kwargs):
        if not self.slug:
            # Используем pytils для транслитерации кириллицы
            self.slug = pytils_slugify(self.name) if self.name else f"event-{self.id or 'new'}"
            if not self.slug:  # Если pytils не справился (например, name содержит только спецсимволы)
                self.slug = f"event-{self.id or 'new'}"
            original_slug = self.slug
            counter = 1
            while Event.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        if not self.is_weekly:
            self.day_of_week = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_recurring(self):
        return self.is_weekly


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
        verbose_name="Фото мероприятия",
        upload_to="events/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Фото для {self.event.name}"


class NPSResponse(models.Model):
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

    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='nps')
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)])
    tags = models.ManyToManyField('NPSTag', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"NPS {self.score} для {self.review.place}"


class NPSTag(models.Model):
  name = models.CharField(max_length=20, unique=True)
  label = models.CharField(max_length=50)

  def __str__(self):
    return self.label
