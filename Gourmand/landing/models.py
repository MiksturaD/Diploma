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
    description = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to="gourmands/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - рейтинг {self.rating}"


class Place(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField()
  place_email = models.EmailField()
  location = models.TextField()
  rating = models.DecimalField(max_digits=10, decimal_places=0)
  phone = models.TextField(max_length=50)
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
    positive_rating = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, default=None)
    negative_rating = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, default=None)
    gourmand = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    place = models.ForeignKey(Place, on_delete=models.DO_NOTHING)

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


class Event(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField()
  event_date = models.DateField()
  places = models.ManyToManyField(Place)
  image = models.ImageField(
    validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "webp"])],
    verbose_name="Изображение события",
    upload_to="events/",
    blank=True,
    null=True
  )

  def __str__(self):
      return f'{self.name}, {self.description}, {", ".join(str(place) for place in self.places.all())}'



