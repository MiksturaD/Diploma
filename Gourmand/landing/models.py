from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin


from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models import DO_NOTHING


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
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="gourmand")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

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
    """Обновляет рейтинг гурмана на основе позитивных и негативных голосов его отзывов"""
    reviews = self.user.reviews.all()
    if reviews.exists():
      total_positive = sum(review.positive_rating for review in reviews)
      total_negative = sum(review.negative_rating for review in reviews)
      total_reactions = total_positive + total_negative
      self.rating = (total_positive / total_reactions) * 5 if total_reactions > 0 else 0.0
    else:
      self.rating = 0.0
    self.save()


class Place(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField()
  place_email = models.EmailField()
  location = models.TextField()
  rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
  phone = models.TextField(max_length=50)
  website = models.URLField(max_length=200, blank=True, null=True)
  owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_places')

  def __str__(self):
    return self.name

  def update_rating(self):
    """Обновляет рейтинг заведения на основе отзывов гурманов"""
    reviews = self.reviews.all()
    if reviews.exists():
      total_weighted_rating = sum(
        review.gourmand_rating * review.gourmand.gourmand_profile.rating
        for review in reviews
        if review.gourmand_rating is not None and hasattr(review.gourmand, 'gourmand_profile')
      )
      total_weight = sum(
        review.gourmand.gourmand_profile.rating
        for review in reviews
        if review.gourmand_rating is not None and hasattr(review.gourmand, 'gourmand_profile')
      )
      self.rating = total_weighted_rating / total_weight if total_weight > 0 else 0.0
    else:
      self.rating = 0.0
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
    description = models.TextField(blank=True)  # 🔥 Вернул поле description
    places = models.ManyToManyField(Place, blank=True)
    image = models.ImageField(upload_to="owners/", blank=True, null=True)

    def __str__(self):
        return f"Владелец {self.user}"


class Review(models.Model):
  name = models.CharField(max_length=50)
  review_date = models.DateTimeField(auto_now_add=True)
  description = models.TextField()
  gourmand_rating = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, default=None)
  positive_rating = models.IntegerField(default=0)
  negative_rating = models.IntegerField(default=0)
  gourmand = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='reviews')
  place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='reviews')

  def __str__(self):
    return f"{self.name} от {self.gourmand} о {self.place}"

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    self.place.update_rating()
    if hasattr(self.gourmand, 'gourmand_profile'):
      self.gourmand.gourmand_profile.update_rating()


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
    unique_together = ('review', 'user')  # Один пользователь — один голос за отзыв

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
  is_weekly = models.BooleanField(default=False)  # Еженедельное мероприятие
  day_of_week = models.IntegerField(choices=WEEKDAYS, null=True, blank=True)

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    # Если событие не еженедельное, очищаем day_of_week
    if not self.is_weekly:
      self.day_of_week = None
    super().save(*args, **kwargs)

  @property
  def is_recurring(self):
    """Просто для удобства, чтобы знать, повторяется ли событие."""
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
  score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)])  # 1-10
  tags = models.ManyToManyField('NPSTag', blank=True)  # Теги влияния
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"NPS {self.score} для {self.review.place}"


class NPSTag(models.Model):
  name = models.CharField(max_length=20, unique=True)
  label = models.CharField(max_length=50)

  def __str__(self):
    return self.label
