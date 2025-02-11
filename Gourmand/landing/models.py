from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models import CASCADE


class User(AbstractUser):
  ROLE_CHOICES = (
    ('gourmand', 'Гурман'),
    ('owner', 'Владелец заведения'),
  )
  role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='gourmand')

  def is_gourmand(self):
    return self.role == 'gourmand'

  def is_owner(self):
    return self.role == 'owner'


class GourmandProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gourmand_profile')
  first_name = models.CharField(max_length=100, null=False)  # ❌ Ошибка, если не передаем значение
  last_name = models.CharField(max_length=100, null=False)
  description = models.TextField()
  rating = models.DecimalField(max_digits=10, decimal_places=0)
  image = models.ImageField(
    validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
    verbose_name="Фото гурмана",
    upload_to="gourmands/",
    blank=True,
    null=True
  )

  def __str__(self):
    return f'{User.first_name} {User.last_name}, рейтинг гурмана {self.rating}'


class Place(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField()
  place_email = models.EmailField()
  location = models.TextField()
  rating = models.DecimalField(max_digits=10, decimal_places=0)
  image = models.ImageField(
    validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
    verbose_name="Фото заведения",
    upload_to="places/",
    blank=True,
    null=True
  )

  def __str__(self):
    return f'{self.name}, {self.description}, {self.place_email}, {self.location}, {self.rating}'

class OwnerProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
  first_name = models.CharField(max_length=100, null=False)  # ❌ Ошибка, если не передаем значение
  last_name = models.CharField(max_length=100, null=False)
  description = models.TextField()
  places = models.ForeignKey(Place, on_delete=models.CASCADE)
  image = models.ImageField(
    validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
    verbose_name="Фото гурмана",
    upload_to="gourmands/",
    blank=True,
    null=True
  )

  def __str__(self):
    return f'Профиль владельца {self.user.username}'


class Review(models.Model):
  name = models.CharField(max_length=50)
  review_date = models.DateTimeField(auto_now_add=True)
  description = models.TextField()
  positive_rating = models.DecimalField(max_digits=10, decimal_places=0)
  negative_rating = models.DecimalField(max_digits=10, decimal_places=0)
  gourmand =models.ForeignKey(User, on_delete=models.DO_NOTHING)
  place = models.ForeignKey(Place, on_delete=models.DO_NOTHING)
  image = models.ImageField(
    validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
    verbose_name="Фото отзыва",
    upload_to="reviews/",
    blank=True,
    null=True
  )

  def __str__(self):
    return (f'{self.name}, {self.gourmand} {self.description}, {self.review_date}, {self.positive_rating}, '
            f'{self.negative_rating}, '
            f'{self.place}')


class Event(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField()
  event_date = models.DateField()
  place = models.ManyToManyField(Place)
  image = models.ImageField(
    validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
    verbose_name="Изображение события",
    upload_to="events/",
    blank=True,
    null=True
  )

  def __str__(self):
    return f'{self.name}, {self.description}, {self.place}'




