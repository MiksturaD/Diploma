from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator

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




class Gourmand(models.Model):
  first_name = models.CharField(max_length=100)
  last_name = models.CharField(max_length=100)
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
    return f'{self.first_name} {self.last_name}, рейтинг гурмана {self.rating}'

class Review(models.Model):
  name = models.CharField(max_length=50)
  review_date = models.DateTimeField(auto_now_add=True)
  description = models.TextField()
  positive_rating = models.DecimalField(max_digits=10, decimal_places=0)
  negative_rating = models.DecimalField(max_digits=10, decimal_places=0)
  gourmand =models.ForeignKey(Gourmand, on_delete=models.DO_NOTHING)
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


class User(AbstractUser):
  first_name = models.CharField(max_length=100)
  last_name = models.CharField(max_length=100)

  def __str__(self):
    return self.username